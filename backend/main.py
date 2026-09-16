from __future__ import annotations

import os
import random

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

load_dotenv()

SUPPORTED_VIBES = [
    "Afro-fusion",
    "Afrobeats",
    "Highlife",
    "Gospel",
    "House",
]

app = FastAPI(title="Bean-sounds API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SongRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Theme or idea for the song")
    vibe: Literal["Afro-fusion", "Afrobeats", "Highlife", "Gospel", "House"] = Field(
        default="Afro-fusion", description="One of the supported musical vibes"
    )
    duration: int = Field(default=90, ge=30, le=240)


class SongResponse(BaseModel):
    title: str
    lyrics: str
    mood: str
    bpm: int
    duration: int
    key: str
    energy: Literal["Low", "Medium", "High", "Peak"]
    generated_by: str
    sections: list[str]


def get_song_key(vibe: str) -> str:
    vibe_map = {
        "Afro-fusion": "A",
        "Afrobeats": "D",
        "Highlife": "G",
        "Gospel": "F",
        "House": "E",
    }
    return vibe_map.get(vibe, "A")


def get_song_energy(vibe: str, duration: int) -> str:
    if vibe in {"House", "Afrobeats"}:
        return "Peak" if duration >= 120 else "High"
    if vibe in {"Gospel", "Highlife"}:
        return "Medium" if duration < 120 else "High"
    return "Low" if duration < 60 else "Medium"


def make_mock_lyrics(prompt: str, vibe: str) -> tuple[str, list[str]]:
    seed_lines = [
        "Sunrise on the coast, the rhythm starts to rise",
        "We carry the heartbeat of the night into the dawn",
        "Every step is a drumline, every note a prayer",
        "From the city lights to the river road, we sing louder",
        f"{prompt} runs through my blood like a festival groove",
        "My soul keeps time with the pulse of the people",
    ]

    chorus = [
        "Hold the rhythm, let it move through us",
        "Feel the fire, feel the love, feel the joy",
        "We rise together, we glow together",
        "From the first beat to the last, we stay in motion",
    ]

    selected = random.sample(seed_lines, 3)
    chorus_line = random.choice(chorus)
    verse = "\n".join(
        [
            selected[0],
            selected[1],
            f"{vibe} in the air, we are living the dream",
            selected[2],
        ]
    )
    bridge = f"{prompt} keeps calling me home, and the night feels alive"
    sections = [
        f"Verse:\n{verse}",
        f"Chorus:\n{chorus_line}",
        f"Bridge:\n{bridge}",
        f"Final Chorus:\n{chorus_line}",
    ]
    return "\n\n".join(sections), sections


@app.get("/")
def root() -> dict:
    return {"service": "bean-sounds", "status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "bean-sounds"}


@app.get("/api/vibes")
def get_vibes() -> dict:
    return {"vibes": SUPPORTED_VIBES}


@app.post("/api/generate", response_model=SongResponse)
def generate_song(request: SongRequest) -> SongResponse:
    gemini_key = os.getenv("GEMINI_API_KEY")
    key = get_song_key(request.vibe)
    energy = get_song_energy(request.vibe, request.duration)
    bpm = max(80, min(150, request.duration // 2))

    if gemini_key and genai is not None:
        try:
            genai.configure(api_key=gemini_key)
            for model_name in ("gemini-2.0-flash", "gemini-1.5-flash"):
                try:
                    model = genai.GenerativeModel(model_name)
                    prompt = (
                        f"Create an original song in a {request.vibe} style inspired by {request.prompt}. "
                        "Write vivid, catchy lyrics with a clear verse, chorus, bridge, and final chorus. "
                        "Keep it around 12-18 lines and make it musical and emotionally expressive."
                    )
                    result = model.generate_content(prompt)
                    generated_text = getattr(result, "text", "").strip()
                    if generated_text:
                        lines = [line.strip() for line in generated_text.splitlines() if line.strip()]
                        sections = [
                            "Verse:\n" + lines[0] if lines else generated_text,
                            "Chorus:\n" + lines[1] if len(lines) > 1 else generated_text,
                            "Bridge:\n" + lines[-1] if lines else generated_text,
                            "Final Chorus:\n" + (lines[1] if len(lines) > 1 else generated_text),
                        ]
                        return SongResponse(
                            title=f"{request.prompt.title()} Pulse",
                            lyrics=generated_text,
                            mood=request.vibe,
                            bpm=bpm,
                            duration=request.duration,
                            key=key,
                            energy=energy,
                            generated_by="gemini",
                            sections=sections,
                        )
                except Exception:
                    continue
        except Exception:
            pass

    lyrics, sections = make_mock_lyrics(request.prompt, request.vibe)
    return SongResponse(
        title=f"{request.prompt.title()} Reverb",
        lyrics=lyrics,
        mood=request.vibe,
        bpm=bpm,
        duration=request.duration,
        key=key,
        energy=energy,
        generated_by="fallback",
        sections=sections,
    )
