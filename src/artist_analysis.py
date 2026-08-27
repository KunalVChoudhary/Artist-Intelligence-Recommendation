import json
from pathlib import Path

from docx import Document

from .ollama_client import OllamaClient, parse_json_response
from .schemas import CATEGORY_SCHEMAS

ARTISTS_DIR = Path("dataset/artist_profiles")
OUTPUT_FILE = Path("outputs/artist_intelligence.jsonl")
MODEL_NAME = "gemma4:e2b"

CATEGORY_NAMES = {
    "photographers": "photographer",
    "musicians": "musician",
    "video_editors": "video_editor",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


def read_profile(profile_path: Path) -> str:
    document = Document(profile_path)
    return "\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip())


def find_media_directory(artist_dir: Path) -> Path | None:
    for name in ("media", "Work"):
        candidate = artist_dir / name
        if candidate.is_dir():
            return candidate
    return None


def discover_media(artist_dir: Path) -> dict[str, list[Path]]:
    media_dir = find_media_directory(artist_dir)
    files = sorted(path for path in media_dir.iterdir() if path.is_file()) if media_dir else []
    return {
        "images": [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS],
        "audio": [path for path in files if path.suffix.lower() in AUDIO_EXTENSIONS],
        "videos": [path for path in files if path.suffix.lower() in VIDEO_EXTENSIONS],
        "unsupported_images": [path for path in files if path.suffix.lower() == ".webp"],
    }


def select_evenly(files: list[Path], limit: int = 3) -> tuple[list[Path], list[Path]]:
    if len(files) <= limit:
        return files, []
    indexes = sorted({round(index * (len(files) - 1) / (limit - 1)) for index in range(limit)})
    selected = [files[index] for index in indexes]
    return selected, [path for path in files if path not in selected]


def prepare_media(category_folder: str, media: dict[str, list[Path]]) -> tuple[list[str], list[str], list[str], dict]:
    images: list[Path] = []
    audio: list[Path] = []
    videos: list[Path] = []
    selected, skipped = [], []

    if category_folder == "photographers":
        images, skipped_paths = select_evenly(media["images"])
        selected = [{"source_file": str(path), "input_type": "image"} for path in images]
        skipped = [{"source_file": str(path), "reason": "coverage limit; evenly distributed sample retained"} for path in skipped_paths]
    elif category_folder == "musicians":
        audio, skipped_paths = select_evenly(media["audio"])
        selected = [{"source_file": str(path), "input_type": "audio"} for path in audio]
        skipped = [{"source_file": str(path), "reason": "coverage limit; evenly distributed sample retained"} for path in skipped_paths]
    else:  # video editors: record media, but analyse the profile only.
        videos = media["videos"]

    unassessed = media["videos"] if category_folder != "video_editors" else [
        path for paths in media.values() for path in paths
    ]
    return [str(path) for path in images], [str(path) for path in audio], [str(path) for path in videos], {
        "method": "At most three evenly distributed category-relevant files are supplied to the model.",
        "selected": selected,
        "skipped": skipped,
        "unassessed_media": [
            {"source_file": str(path), "reason": "intentionally unassessed and not supplied to the model"}
            for path in unassessed
        ] + [{"source_file": str(path), "reason": "unsupported image format for this local model input"} for path in media["unsupported_images"]],
    }


def build_artist_prompt(category: str, profile_text: str, profile_source: Path, selection: dict) -> str:
    dimension_names = list(CATEGORY_SCHEMAS[CATEGORY_NAMES[category]]["capability_dimensions"])
    return f"""You are analysing a {CATEGORY_NAMES[category]} for an evidence-led creative marketplace.

PROFILE SOURCE: {profile_source}
PROFILE TEXT: claims in this text are not proof.\n{profile_text}

CATEGORY-SPECIFIC DIMENSIONS: {json.dumps(dimension_names, ensure_ascii=False)}

MEDIA SELECTION:\n{json.dumps(selection, ensure_ascii=False)}

Return valid JSON with: artist_name, category, profile_claims, capability_dimensions, demonstrated_capabilities, unknowns, confidence, media_selection.
For each relevant dimension, use status demonstrated, claimed_only, conflicting, or unknown; include assessment and evidence. Cite every profile claim with the profile source and every media-derived observation with its source filename (and timestamp if one is actually available). Treat a profile statement as claimed_only unless supplied media supports it. Media listed as unassessed_media was not analysed and cannot support a demonstrated capability. Keep arrays to at most four concise items and do not infer reliability, punctuality, professionalism, character, popularity or personality."""


def analyze_artist(client: OllamaClient, category_folder: str, artist_dir: Path) -> dict:
    profiles = sorted(artist_dir.glob("*.docx"))
    if not profiles:
        raise FileNotFoundError(f"No DOCX profile found in {artist_dir}")
    media = discover_media(artist_dir)
    images, audio, videos, selection = prepare_media(category_folder, media)
    result = parse_json_response(client.generate(
        prompt=build_artist_prompt(category_folder, read_profile(profiles[0]), profiles[0], selection),
        images=images,
        audio=audio,
        videos=videos,
    ))
    result.setdefault("artist_name", artist_dir.name)
    result.setdefault("profile_claims", [])
    result.setdefault("capability_dimensions", {})
    result.setdefault("demonstrated_capabilities", [])
    result.setdefault("unknowns", [])
    result.setdefault("confidence", {"level": "low", "rationale": "Model did not provide confidence."})
    result.update({
        "artist_folder": artist_dir.name,
        "category": CATEGORY_NAMES[category_folder],
        "profile_source": str(profiles[0]),
        "media_sources": [str(path) for paths in media.values() for path in paths],
        "media_selection": selection,
    })
    return result


def failed_record(category_folder: str, artist_dir: Path, error: Exception) -> dict:
    profiles = sorted(artist_dir.glob("*.docx"))
    media = discover_media(artist_dir)
    _, _, _, selection = prepare_media(category_folder, media)
    return {
        "artist_name": artist_dir.name,
        "artist_folder": artist_dir.name,
        "category": CATEGORY_NAMES[category_folder],
        "profile_source": str(profiles[0]) if profiles else None,
        "media_sources": [str(path) for paths in media.values() for path in paths],
        "profile_claims": [],
        "capability_dimensions": {},
        "demonstrated_capabilities": [],
        "unknowns": ["Capability assessment unavailable because this supplied case could not be processed."],
        "media_selection": selection,
        "processing_error": str(error),
        "confidence": {"level": "low", "rationale": "Processing failed; no capability claim is inferred."},
    }


def run_artist_analysis() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    client = OllamaClient(model=MODEL_NAME)
    if not client.check_connection():
        raise RuntimeError("Could not connect to Ollama. Start Ollama and ensure the configured model is installed.")

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for category_folder in CATEGORY_NAMES:
            category_dir = ARTISTS_DIR / category_folder
            if not category_dir.is_dir():
                raise FileNotFoundError(f"Artist category directory not found: {category_dir}")
            for artist_dir in sorted(path for path in category_dir.iterdir() if path.is_dir()):
                try:
                    print(f"Analysing {artist_dir.name}...")
                    record = analyze_artist(client, category_folder, artist_dir)
                except Exception as exc:
                    record = failed_record(category_folder, artist_dir, exc)
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()
    print(f"Artist intelligence written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_artist_analysis()
