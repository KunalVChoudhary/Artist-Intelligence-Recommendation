import json
import re
from pathlib import Path

import ollama


class OllamaClient:

    def __init__(self, model: str, host: str = "http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=host)

    def check_connection(self) -> bool:
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        images: list[str] | None = None,
        audio: list[str] | None = None,
        videos: list[str] | None = None,
    ) -> str:
        del videos
        message: dict[str, object] = {"role": "user", "content": prompt}
        if images:
            message["images"] = [Path(path) for path in images]
        if audio:
            message["audio"] = [Path(path) for path in audio]
        try:
            response = self.client.chat(
                model=self.model,
                messages=[message],
                options={"temperature": 0},
                format="json",
            )
            return response.message.content
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed for '{self.model}': {exc}") from exc


def parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.S)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise ValueError(f"Model response did not contain a JSON object:\n{text}")
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("Model response must be a JSON object.")
    return value
