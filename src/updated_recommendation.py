import json
from pathlib import Path

from .ollama_client import OllamaClient, parse_json_response
from .recommendation import compact_artist_records

# Configuration

RECOMMENDATIONS_FILE = Path(
    "outputs/recommendations.json"
)

ARTIST_INTELLIGENCE_FILE = Path(
    "outputs/artist_intelligence.jsonl"
)

FOLLOWUP_DIR = Path(
    "dataset/follow_up_update"
)

OUTPUT_FILE = Path(
    "outputs/updated_recommendation.json"
)

MODEL_NAME = "gemma4:e2b"


def compact_requirement(requirement: dict) -> dict:
    """Retain decision signals while fitting the local model context window."""
    return {
        "category": requirement.get("category"),
        "explicit_constraints": requirement.get("explicit_constraints", [])[:6],
        "priorities": requirement.get("priorities", [])[:4],
        "reasonable_assumptions": requirement.get("reasonable_assumptions", [])[:3],
        "contradictions": requirement.get("contradictions", [])[:3],
        "unknowns": requirement.get("unknowns", [])[:4],
        "matching_signals": requirement.get("matching_signals", [])[:5],
    }


def compact_recommendation(recommendation: dict) -> dict:
    rankings = recommendation.get("recommendations", [])
    return {
        "recommendations": [
            {
                "rank": item.get("rank"),
                "artist_folder": item.get("artist_folder"),
                "matching_capabilities": item.get("matching_capabilities", [])[:3],
                "trade_offs": item.get("trade_offs", [])[:2],
                "uncertainty": item.get("uncertainty", [])[:2],
            }
            for item in rankings[:2]
            if isinstance(item, dict)
        ],
        "assumptions_used": recommendation.get("assumptions_used", [])[:3],
        "important_unknowns": recommendation.get("important_unknowns", [])[:3],
    }

# File reading

def read_text_file(file_path: Path) -> str:
    return file_path.read_text(
        encoding="utf-8"
    )


def load_recommendations() -> list[dict]:

    if not RECOMMENDATIONS_FILE.exists():
        raise FileNotFoundError(
            f"Recommendations file not found: "
            f"{RECOMMENDATIONS_FILE}"
        )

    with RECOMMENDATIONS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_artist_intelligence() -> list[dict]:
    if not ARTIST_INTELLIGENCE_FILE.exists():
        raise FileNotFoundError(
            f"Artist intelligence file not found: "
            f"{ARTIST_INTELLIGENCE_FILE}"
        )

    artists = []

    with ARTIST_INTELLIGENCE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            artists.append(
                json.loads(line)
            )

    return artists


# Follow-up discovery

def find_followup_file() -> Path:
    
    if not FOLLOWUP_DIR.exists():
        raise FileNotFoundError(
            f"Follow-up directory not found: "
            f"{FOLLOWUP_DIR}"
        )

    followup_files = sorted(
        file
        for file in FOLLOWUP_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in {
            ".txt",
            ".md",
        }
    )

    if not followup_files:
        raise FileNotFoundError(
            "Could not find a follow-up file in "
            f"{FOLLOWUP_DIR}"
        )

    if len(followup_files) > 1:
        raise ValueError(
            "Multiple follow-up files found: "
            + ", ".join(
                file.name
                for file in followup_files
            )
        )

    return followup_files[0]


# ---------------------------------------------------------------------------
# Follow-up re-ranking
# ---------------------------------------------------------------------------

def build_reranking_prompt(
    original_requirement: dict,
    original_recommendation: dict,
    followup: str,
    artists: list[dict],
) -> str:
    """
    Build the prompt used to re-rank artists after new hirer information.
    """

    return f"""
You are updating an artist recommendation after receiving new information
from a hirer.

The original requirement may have been incomplete. The new follow-up
information can change the importance of different capabilities.

ORIGINAL HIRER REQUIREMENT:
{json.dumps(
    compact_requirement(original_requirement),
    indent=2,
    ensure_ascii=False,
)}

ORIGINAL RECOMMENDATION:
{json.dumps(
    compact_recommendation(original_recommendation),
    indent=2,
    ensure_ascii=False,
)}

NEW HIRER FOLLOW-UP:
{followup}

AVAILABLE ARTIST INTELLIGENCE:
{json.dumps(
    compact_artist_records(original_requirement, artists),
    indent=2,
    ensure_ascii=False,
)}

Your task is to update the recommendation using the new information.

IMPORTANT RULES:

1. Identify what the follow-up adds, removes, clarifies, or changes.

2. Do not reinterpret information that has not changed.

3. Re-rank artists according to the updated requirement.

4. Prefer demonstrated capabilities over profile claims.

5. A profile claim that has not been supported by supplied work must not
   be treated as equivalent to demonstrated capability.

6. Do not invent capabilities or evidence.

7. Do not use reliability, punctuality, professionalism, popularity,
   appearance, character, or other unsupported trust signals.

8. Keep unknown information as unknown.

9. Return the strongest two plausible matches whenever two plausible
   matches exist.

10. The ranking does not have to change. If the new information does not
    materially affect the ranking, keep the original ranking and explain
    why.

11. If the ranking changes, explain exactly which new requirement or
    priority caused the change.

12. Distinguish between:
    - information that was already known
    - information introduced by the follow-up
    - consequences for the ranking

Return valid JSON only with this structure:

{{
    "updated_ranking": [
        {{
            "rank": 1,
            "artist_folder": "...",
            "reasons": [],
            "matching_capabilities": [],
            "trade_offs": [],
            "evidence_strength": "...",
            "uncertainty": []
        }},
        {{
            "rank": 2,
            "artist_folder": "...",
            "reasons": [],
            "matching_capabilities": [],
            "trade_offs": [],
            "evidence_strength": "...",
            "uncertainty": []
        }}
    ],
    "what_changed": [],
    "why_it_changed": [],
    "unchanged_factors": [],
    "trade_offs": [],
    "uncertainty": []
}}
""".strip()


def rerank_after_followup(
    client: OllamaClient,
    original_requirement: dict,
    original_recommendation: dict,
    followup: str,
    artists: list[dict],
) -> dict:
    """
    Re-rank artists after receiving the hirer's follow-up information.
    """

    prompt = build_reranking_prompt(
        original_requirement=original_requirement,
        original_recommendation=original_recommendation,
        followup=followup,
        artists=artists,
    )

    response = client.generate(
        prompt=prompt
    )

    try:
        return parse_json_response(response)

    except ValueError as exc:
        raise ValueError(
            "Ollama returned invalid JSON while re-ranking artists:\n"
            f"{response}"
        ) from exc


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_updated_recommendation() -> None:
    """
    Run the follow-up recommendation pipeline.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = OllamaClient(
        model=MODEL_NAME,
    )

    if not client.check_connection():
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running and the model is available."
        )

    # -----------------------------------------------------------------------
    # Load the outputs from the previous pipelines.
    # -----------------------------------------------------------------------

    recommendations = load_recommendations()

    artists = load_artist_intelligence()

    # -----------------------------------------------------------------------
    # Find and read the supplied follow-up.
    # -----------------------------------------------------------------------

    followup_file = find_followup_file()

    followup = read_text_file(
        followup_file
    )

    print(
        f"Using follow-up: {followup_file.name}"
    )

    # -----------------------------------------------------------------------
    # The assessment supplies one follow-up for one hirer request.
    #
    # We therefore need to identify which original recommendation it
    # belongs to. The model is given all original briefs and asked to
    # identify the matching one.
    # -----------------------------------------------------------------------

    # The full four recommendation objects exceed the local model's context.
    # These requirement signals are sufficient to attach the supplied update.
    brief_data = [
        {
            "brief_id": result["brief_id"],
            "category": result["requirement"].get("category"),
            "explicit_constraints": result["requirement"].get("explicit_constraints", [])[:6],
            "priorities": result["requirement"].get("priorities", [])[:4],
        }
        for result in recommendations
    ]

    identification_prompt = f"""
You are matching a hirer's follow-up message to one of the original
hirer briefs.

ORIGINAL BRIEFS:
{json.dumps(
    brief_data,
    indent=2,
    ensure_ascii=False,
)}

FOLLOW-UP MESSAGE:
{followup}

Identify which original brief this follow-up belongs to.

Return valid JSON only:

{{
    "brief_id": "...",
    "reason": "..."
}}

Do not invent a brief.
""".strip()

    identification_response = client.generate(
        prompt=identification_prompt
    )

    try:
        identification = parse_json_response(identification_response)

    except ValueError as exc:
        raise ValueError(
            "Ollama returned invalid JSON while identifying the "
            "follow-up brief:\n"
            f"{identification_response}"
        ) from exc

    brief_id = identification.get(
        "brief_id"
    )

    if not brief_id:
        raise ValueError(
            "Ollama did not identify a brief for the follow-up."
        )

    # -----------------------------------------------------------------------
    # Find the original recommendation that the follow-up belongs to.
    # -----------------------------------------------------------------------

    matching_results = [
        result
        for result in recommendations
        if result["brief_id"] == brief_id
    ]

    if len(matching_results) != 1:
        raise ValueError(
            f"Could not uniquely identify brief '{brief_id}'."
        )

    original_result = matching_results[0]

    # -----------------------------------------------------------------------
    # Re-rank using the original requirement, original recommendation,
    # follow-up information and complete artist intelligence.
    # -----------------------------------------------------------------------

    updated = rerank_after_followup(
        client=client,
        original_requirement=original_result["requirement"],
        original_recommendation=original_result["recommendation"],
        followup=followup,
        artists=artists,
    )

    # -----------------------------------------------------------------------
    # Store both the original context and the updated result so that the
    # output is self-explanatory and easy to inspect during the demo.
    # -----------------------------------------------------------------------

    final_result = {
        "brief_id": brief_id,
        "followup_source": str(followup_file),
        "followup": followup,
        "original_requirement": original_result[
            "requirement"
        ],
        "original_recommendation": original_result[
            "recommendation"
        ],
        "updated_recommendation": updated,
        "followup_matching_reason": identification.get(
            "reason",
            "",
        ),
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Updated recommendation written to: "
        f"{OUTPUT_FILE}"
    )

# Entry point

if __name__ == "__main__":
    run_updated_recommendation()
