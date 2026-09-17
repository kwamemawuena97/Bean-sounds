import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import require_api_key
from ..models import Song
from ..schemas import AudioRequest, SongListItem, SongRequest, SongResponse
from ..services import audio as audio_service
from ..services import lyrics as lyrics_service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["songs"])
limiter = Limiter(key_func=get_remote_address)

_settings = get_settings()


def _to_response(song: Song) -> SongResponse:
    return SongResponse(
        id=song.id,
        title=song.title,
        lyrics=song.lyrics,
        sections=json.loads(song.sections_json or "[]"),
        mood=song.mood,
        bpm=song.bpm,
        duration=song.duration,
        key=song.song_key,
        energy=song.energy,  # type: ignore[arg-type]
        generated_by=song.generated_by,
        audio_url=song.audio_url,
        audio_provider=song.audio_provider,
        prompt=song.prompt,
        vibe=song.vibe,  # type: ignore[arg-type]
        created_at=song.created_at,
    )


@router.post("/generate", response_model=SongResponse)
@limiter.limit(_settings.rate_limit_generate)
def generate_song(
    request: Request,
    payload: SongRequest,
    db: Session = Depends(get_db),
    _: str | None = Depends(require_api_key),
) -> SongResponse:
    lyr = lyrics_service.generate_lyrics(payload.prompt, payload.vibe)
    key = lyrics_service.song_key(payload.vibe)
    energy = lyrics_service.song_energy(payload.vibe, payload.duration)
    bpm = lyrics_service.song_bpm(payload.duration)

    song = Song(
        prompt=payload.prompt,
        vibe=payload.vibe,
        title=lyr.title,
        lyrics=lyr.lyrics,
        sections_json=json.dumps(lyr.sections),
        mood=payload.vibe,
        bpm=bpm,
        duration=payload.duration,
        song_key=key,
        energy=energy,
        generated_by=lyr.generated_by,
    )

    if payload.with_audio:
        audio = audio_service.generate_audio(payload.prompt, payload.vibe, payload.duration, bpm)
        song.audio_url = audio_service.audio_url_for(audio.filename)
        song.audio_provider = audio.provider

    db.add(song)
    db.commit()
    db.refresh(song)
    log.info(
        "song_generated",
        extra={"song_id": song.id, "vibe": song.vibe, "generated_by": song.generated_by, "with_audio": payload.with_audio},
    )
    return _to_response(song)


@router.post("/generate-audio", response_model=SongResponse)
@limiter.limit(_settings.rate_limit_audio)
def generate_audio_for_song(
    request: Request,
    payload: AudioRequest,
    db: Session = Depends(get_db),
    _: str | None = Depends(require_api_key),
) -> SongResponse:
    song = db.get(Song, payload.song_id)
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="song not found")
    audio = audio_service.generate_audio(song.prompt, song.vibe, song.duration, song.bpm)
    song.audio_url = audio_service.audio_url_for(audio.filename)
    song.audio_provider = audio.provider
    db.commit()
    db.refresh(song)
    log.info("audio_generated", extra={"song_id": song.id, "provider": audio.provider})
    return _to_response(song)


@router.get("/songs", response_model=list[SongListItem])
def list_songs(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> list[Song]:
    limit = max(1, min(100, limit))
    offset = max(0, offset)
    stmt = select(Song).order_by(Song.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars())


@router.get("/songs/{song_id}", response_model=SongResponse)
def get_song(song_id: str, db: Session = Depends(get_db)) -> SongResponse:
    song = db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="song not found")
    return _to_response(song)


audio_router = APIRouter(tags=["audio"])


@audio_router.get("/audio/{filename}")
def serve_audio(filename: str):
    if not audio_service.is_safe_filename(filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid filename")
    path = audio_service.audio_path_for(filename)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="audio not found")
    return FileResponse(path, media_type="audio/wav", filename=filename)
