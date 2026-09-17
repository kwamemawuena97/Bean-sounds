from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Vibe = Literal["Afro-fusion", "Afrobeats", "Highlife", "Gospel", "House"]
Energy = Literal["Low", "Medium", "High", "Peak"]

SUPPORTED_VIBES: list[str] = ["Afro-fusion", "Afrobeats", "Highlife", "Gospel", "House"]


class SongRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    vibe: Vibe = "Afro-fusion"
    duration: int = Field(default=90, ge=30, le=240)
    with_audio: bool = False


class AudioRequest(BaseModel):
    song_id: str


class SongResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    lyrics: str
    sections: list[str]
    mood: str
    bpm: int
    duration: int
    key: str
    energy: Energy
    generated_by: str
    audio_url: str | None = None
    audio_provider: str | None = None
    prompt: str
    vibe: Vibe
    created_at: datetime


class SongListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    vibe: Vibe
    created_at: datetime
    audio_url: str | None = None


class VibesResponse(BaseModel):
    vibes: list[str]
