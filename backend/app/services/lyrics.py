from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass
from typing import Any

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None  # type: ignore[assignment]

from ..config import get_settings

log = logging.getLogger(__name__)

_KEY_MAP = {
    "Afro-fusion": "A",
    "Afrobeats": "D",
    "Highlife": "G",
    "Gospel": "F",
    "House": "E",
}


@dataclass
class GeneratedLyrics:
    title: str
    lyrics: str
    sections: list[str]
    generated_by: str


def song_key(vibe: str) -> str:
    return _KEY_MAP.get(vibe, "A")


def song_energy(vibe: str, duration: int) -> str:
    if vibe in {"House", "Afrobeats"}:
        return "Peak" if duration >= 120 else "High"
    if vibe in {"Gospel", "Highlife"}:
        return "Medium" if duration < 120 else "High"
    return "Low" if duration < 60 else "Medium"


def song_bpm(duration: int) -> int:
    return max(80, min(150, duration // 2))


_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _parse_gemini_json(text: str) -> dict[str, Any] | None:
    match = _JSON_BLOCK.search(text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _mock(prompt: str, vibe: str) -> GeneratedLyrics:
    seeds = [
        "Sunrise on the coast, the rhythm starts to rise",
        "We carry the heartbeat of the night into the dawn",
        "Every step is a drumline, every note a prayer",
        "From the city lights to the river road, we sing louder",
        f"{prompt} runs through my blood like a festival groove",
        "My soul keeps time with the pulse of the people",
    ]
    chorus_pool = [
        "Hold the rhythm, let it move through us",
        "Feel the fire, feel the love, feel the joy",
        "We rise together, we glow together",
        "From the first beat to the last, we stay in motion",
    ]
    picks = random.sample(seeds, 3)
    chorus = random.choice(chorus_pool)
    verse = "\n".join([picks[0], picks[1], f"{vibe} in the air, we live the dream", picks[2]])
    bridge = f"{prompt} keeps calling me home, and the night feels alive"
    sections = [
        f"Verse:\n{verse}",
        f"Chorus:\n{chorus}",
        f"Bridge:\n{bridge}",
        f"Final Chorus:\n{chorus}",
    ]
    title = f"{prompt.title()} Reverb"
    return GeneratedLyrics(title=title, lyrics="\n\n".join(sections), sections=sections, generated_by="fallback")


def _build_prompt(prompt: str, vibe: str) -> str:
    return (
        f"Write an original song in a {vibe} style inspired by: {prompt!r}.\n"
        "Return STRICT JSON with keys: title (short catchy name), verse, chorus, bridge, final_chorus.\n"
        "Each section should be 3-5 lines separated by \\n. Do not include any prose outside the JSON.\n"
    )


def generate_lyrics(prompt: str, vibe: str) -> GeneratedLyrics:
    settings = get_settings()
    key = settings.gemini_api_key
    if not key or genai is None:
        return _mock(prompt, vibe)

    try:
        genai.configure(api_key=key)
    except Exception:
        log.exception("gemini_configure_failed")
        return _mock(prompt, vibe)

    for model_name in (settings.gemini_model_primary, settings.gemini_model_fallback):
        try:
            model = genai.GenerativeModel(model_name)
            result = model.generate_content(_build_prompt(prompt, vibe))
            text = getattr(result, "text", "").strip()
            if not text:
                continue
            data = _parse_gemini_json(text)
            if data and all(k in data for k in ("verse", "chorus", "bridge", "final_chorus")):
                title = str(data.get("title") or f"{prompt.title()} Pulse")[:120]
                sections = [
                    f"Verse:\n{data['verse']}",
                    f"Chorus:\n{data['chorus']}",
                    f"Bridge:\n{data['bridge']}",
                    f"Final Chorus:\n{data['final_chorus']}",
                ]
                return GeneratedLyrics(
                    title=title,
                    lyrics="\n\n".join(sections),
                    sections=sections,
                    generated_by=f"gemini:{model_name}",
                )
            log.warning("gemini_json_parse_failed", extra={"model": model_name})
        except Exception:
            log.exception("gemini_generate_failed", extra={"model": model_name})
            continue

    return _mock(prompt, vibe)
