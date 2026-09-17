from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    vibe: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    lyrics: Mapped[str] = mapped_column(Text, nullable=False)
    sections_json: Mapped[str] = mapped_column(Text, default="[]")
    mood: Mapped[str] = mapped_column(String(64), default="")
    bpm: Mapped[int] = mapped_column(Integer, default=110)
    duration: Mapped[int] = mapped_column(Integer, default=90)
    song_key: Mapped[str] = mapped_column(String(8), default="A")
    energy: Mapped[str] = mapped_column(String(16), default="Medium")
    generated_by: Mapped[str] = mapped_column(String(32), default="fallback")
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    audio_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
