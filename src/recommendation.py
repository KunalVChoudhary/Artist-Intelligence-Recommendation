import json
from pathlib import Path

from .ollama_client import OllamaClient, parse_json_response


HIRER_DIR = Path("dataset/hirer_conversations")
ARTIST_INTELLIGENCE_FILE = Path(
    "outputs/artist_intelligence.jsonl"
)

RECOMMENDATIONS_FILE = Path(
    "outputs/recommendations.json"
)

UPDATED_RECOMMENDATION_FILE = Path(
    "outputs/updated_recommendation.json"
)

MODEL_NAME = "gemma4:e2b"

# File reading

def read_text_file(file_path: Path) -> str:

    return file_path.read_text(
        encoding="utf-8"
    )


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


def compact_artist_records(requirement: dict, artists: list[dict]) -> list[dict]:
    """Keep ranking prompts inside the local model's small context window."""
    category = requirement.get("category")
    candidates = [artist for artist in artists if artist.get("category") == category]
    candidates = candidates or artists
    compact = []
    for artist in candidates:
        dimensions = artist.get("capability_dimensions", {})
        if not isinstance(dimensions, dict):
            dimensions = {}
        compact_dimensions = {
            name: value.get("status")
            for name, value in dimensions.items()
            if isinstance(value, dict) and value.get("status") != "unknown"
        }
        evidence = []
        for value in dimensions.values():
            if not isinstance(value, dict) or value.get("status") != "demonstrated":
                continue
            for item in value.get("evidence", [])[:1]:
                if isinstance(item, dict):
                    evidence.append({
                        "source_file": item.get("source_file"),
                        "timestamp_seconds": item.get("timestamp_seconds"),
                        "observation": str(item.get("observation", ""))[:140],
                    })
                if len(evidence) == 3:
                    break
            if len(evidence) == 3:
                break
        compact.append({
            "artist_folder": artist.get("artist_folder"),
            "category": artist.get("category"),
            "profile_claims": artist.get("profile_claims", [])[:2],
            "capability_dimensions": compact_dimensions,
            "demonstrated_capabilities": artist.get("demonstrated_capabilities", [])[:2],
            "evidence": evidence,
            "unknowns": artist.get("unknowns", [])[:2],
            "confidence": artist.get("confidence"),
            "processing_error": artist.get("processing_error"),
        })
    return compact


# Hirer requirement analysis

def build_hirer_analysis_prompt(
    conversation: str,
) -> str:

    return f"""
You are analysing a short hirer conversation for an evidence-led
creative marketplace.

The conversation may be incomplete.

Your task is to extract the actual hiring requirement without inventing
information that the hirer did not provide.

HIRER CONVERSATION:
{conversation}

Analyse the conversation and return a structured requirement containing:

1. category
   - photographer
   - musician
   - video_editor
   - unknown

2. explicit_constraints
   Requirements directly stated by the hirer.

3. priorities
   The requirements that appear most important to the hirer.
   Order them from highest to lowest priority.

4. reasonable_assumptions
   Reasonable interpretations that can be made from the conversation.
   Clearly distinguish these from explicit requirements.

5. contradictions
   Any requirements or statements that conflict with each other.

6. unknowns
   Important information that is missing but could affect the choice.

7. matching_signals
   The artist capabilities that should matter most when ranking artists.

8. irrelevant_signals
   Artist information that should not materially affect this particular
   recommendation.

IMPORTANT RULES:

- Do not invent requirements.
- Do not turn assumptions into explicit constraints.
- Do not reject artists merely because the brief is incomplete.
- Identify unknowns rather than pretending they do not exist.
- Priorities must be based on the actual conversation.
- The goal is to produce useful initial recommendations despite
  incomplete information.

Return valid JSON only.
""".strip()


def analyze_hirer_requirement(
    client: OllamaClient,
    conversation: str,
) -> dict:
    prompt = build_hirer_analysis_prompt(
        conversation
    )

    response = client.generate(
        prompt=prompt
    )

    try:
        return parse_json_response(response)

    except ValueError as exc:
        raise ValueError(
            "Ollama returned invalid JSON while analysing "
            "the hirer requirement:\n"
            f"{response}"
        ) from exc


# Artist matching

def build_matching_prompt(
    requirement: dict,
    artists: list[dict],
) -> str:

    artist_data = json.dumps(
        compact_artist_records(requirement, artists),
        indent=2,
        ensure_ascii=False,
    )

    requirement_data = json.dumps(
        requirement,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are recommending artists for an evidence-led creative marketplace.

You have:

1. A structured interpretation of a hirer's requirement.
2. Evidence-backed capability records for the available artists.

Your task is to return the TWO strongest initial artist matches whenever
plausible matches exist.

HIRER REQUIREMENT:
{requirement_data}

AVAILABLE ARTISTS:
{artist_data}

RANKING RULES:

1. Match artists against the hirer's actual priorities.

2. Prefer demonstrated capabilities over profile claims.

3. A profile claim that has not been supported by supplied work must not
   be treated as equivalent to demonstrated capability.

4. Do not penalize an artist for information that is simply unknown unless
   that unknown is important to the hirer's requirement.

5. Do not use reliability, punctuality, professionalism, popularity,
   appearance, character or other unsupported trust signals.

6. Category-specific capability matters more than generic similarity.

7. Explain why each recommended artist matches the requirement.

8. Explain important trade-offs.

9. State relevant uncertainty.

10. If an important capability is only claimed rather than demonstrated,
    explicitly say so.

11. Do not wait for a perfect brief. Recommend the strongest plausible
    matches from the available evidence.

12. Return at most two artists. Return two whenever two plausible matches
    exist.

For each recommendation include:

- rank
- artist_folder
- reasons
- matching_capabilities
- trade_offs
- evidence_strength
- uncertainty

Also include:

- assumptions_used
- important_unknowns
- why_other_candidates_were_not_ranked_higher
- improve_your_matches: at most two objects with question and ranking_impact.
  Put this after the shortlist. Each question must explain how either answer
  could materially change the ranking.

Return valid JSON only.
Use exactly this top-level structure:
{{
  "recommendations": [{{"rank": 1, "artist_folder": "...", "reasons": [], "matching_capabilities": [], "trade_offs": [], "evidence_strength": "...", "uncertainty": []}}],
  "assumptions_used": [],
  "important_unknowns": [],
  "why_other_candidates_were_not_ranked_higher": [],
  "improve_your_matches": [{{"question": "...", "ranking_impact": "..."}}]
}}
""".strip()


def recommend_artists(
    client: OllamaClient,
    requirement: dict,
    artists: list[dict],
) -> dict:

    prompt = build_matching_prompt(
        requirement,
        artists,
    )

    response = client.generate(
        prompt=prompt
    )

    try:
        return parse_json_response(response)

    except ValueError as exc:
        raise ValueError(
            "Ollama returned invalid JSON while ranking artists:\n"
            f"{response}"
        ) from exc

# Initial recommendation pipeline

def process_all_briefs(
    client: OllamaClient,
    artists: list[dict],
) -> list[dict]:

    if not HIRER_DIR.exists():
        raise FileNotFoundError(
            f"Hirer conversation directory not found: "
            f"{HIRER_DIR}"
        )

    results = []

    hirer_files = sorted(
        file
        for file in HIRER_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in {
            ".txt",
            ".md",
            ".docx",
        }
    )

    for hirer_file in hirer_files:

        print(
            f"Processing hirer brief: "
            f"{hirer_file.name}"
        )

        if hirer_file.suffix.lower() == ".docx":
            raise ValueError(
                "DOCX hirer conversations are not supported by "
                "read_text_file(). Convert them to text or add DOCX "
                "reading here."
            )

        conversation = read_text_file(
            hirer_file
        )

        requirement = analyze_hirer_requirement(
            client,
            conversation,
        )

        recommendation = recommend_artists(
            client,
            requirement,
            artists,
        )

        results.append(
            {
                "brief_id": hirer_file.stem,
                "source_file": str(hirer_file),
                "requirement": requirement,
                "recommendation": recommendation,
            }
        )

    return results

# Main pipeline

def run_recommendations() -> None:

    RECOMMENDATIONS_FILE.parent.mkdir(
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

    artists = load_artist_intelligence()

    print(
        f"Loaded {len(artists)} artist intelligence records."
    )

    results = process_all_briefs(
        client,
        artists,
    )

    with RECOMMENDATIONS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Recommendations written to: "
        f"{RECOMMENDATIONS_FILE}"
    )

# Entry point

if __name__ == "__main__":
    run_recommendations()
