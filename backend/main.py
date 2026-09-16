from __future__ import annotations

import os
import random
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

load_dotenv()

app = FastAPI(title="Bean-sounds API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SongRequest(BaseModel):
    prompt: str
    vibe: str = "Afro-fusion"
    duration: int = 90


class SongResponse(BaseModel):
    title: str
    lyrics: str
    mood: str
    bpm: int


def make_mock_lyrics(prompt: str, vibe: str) -> str:
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
    return "\n\n".join(
        [
            selected[0],
            chorus_line,
            selected[1],
            f"{vibe} in the air, we are living the dream",
            selected[2],
            "Keep the tempo high, keep the spirit alive",
        ]
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "bean-sounds"}


@app.post("/api/generate", response_model=SongResponse)
def generate_song(request: SongRequest) -> SongResponse:
    gemini_key = os.getenv("GEMINI_API_KEY")

    if gemini_key and genai is not None:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"Create an original song in a {request.vibe} style inspired by {request.prompt}. "
                "Make it vivid, catchy, and musical with a clear verse and chorus. Keep it around 12-16 lines."
            )
            result = model.generate_content(prompt)
            generated_text = getattr(result, "text", "").strip()
            if generated_text:
                return SongResponse(
                    title=f"{request.prompt.title()} Pulse",
                    lyrics=generated_text,
                    mood=request.vibe,
                    bpm=max(80, min(150, request.duration // 2)),
                )
        except Exception:
            pass

    return SongResponse(
        title=f"{request.prompt.title()} Reverb",
        lyrics=make_mock_lyrics(request.prompt, request.vibe),
        mood=request.vibe,
        bpm=max(82, min(140, request.duration // 2)),
    )
