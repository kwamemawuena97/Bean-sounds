from __future__ import annotations

import logging
import math
import os
import struct
import uuid
import wave
from dataclasses import dataclass
from pathlib import Path

from ..config import get_settings

log = logging.getLogger(__name__)


@dataclass
class GeneratedAudio:
    filename: str
    path: str
    provider: str


_VIBE_PROFILE = {
    "Afro-fusion": {"root": 220.0, "bpm": 105},
    "Afrobeats": {"root": 246.94, "bpm": 110},
    "Highlife": {"root": 261.63, "bpm": 118},
    "Gospel": {"root": 196.0, "bpm": 92},
    "House": {"root": 293.66, "bpm": 124},
}


def _mock_wav(path: Path, vibe: str, duration: int, bpm: int) -> None:
    """Generate a simple layered sine-wave preview so the UI has playable audio."""
    sample_rate = 22050
    n_frames = sample_rate * duration
    profile = _VIBE_PROFILE.get(vibe, _VIBE_PROFILE["Afro-fusion"])
    root = float(profile["root"])
    beat_hz = bpm / 60.0

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        chunk = 2048
        buf = bytearray()
        for i in range(n_frames):
            t = i / sample_rate
            # Chord: root + fifth + octave, subtle detune
            note = (
                math.sin(2 * math.pi * root * t)
                + 0.6 * math.sin(2 * math.pi * root * 1.5 * t)
                + 0.4 * math.sin(2 * math.pi * root * 2.0 * t)
            ) / 2.0
            # Kick-drum pulse on the beat
            beat_phase = (t * beat_hz) % 1.0
            kick = math.exp(-beat_phase * 25.0) * math.sin(2 * math.pi * 55.0 * t)
            # Fade in/out to avoid clicks
            envelope = min(1.0, t * 4.0, (duration - t) * 4.0)
            sample = max(-1.0, min(1.0, 0.5 * note + 0.6 * kick)) * envelope
            buf.extend(struct.pack("<h", int(sample * 32767 * 0.7)))
            if len(buf) >= chunk * 2:
                wav.writeframes(bytes(buf))
                buf.clear()
        if buf:
            wav.writeframes(bytes(buf))


def _try_lyria(prompt: str, vibe: str, duration: int, out_path: Path) -> bool:
    """Attempt Lyria via Vertex AI. Returns True if audio was written to out_path."""
    settings = get_settings()
    if not settings.vertex_project_id:
        return False
    try:
        # Import lazily so environments without google-cloud-aiplatform still work.
        from google.cloud import aiplatform_v1  # type: ignore
        from google.protobuf import json_format  # type: ignore
        from google.protobuf.struct_pb2 import Value  # type: ignore
    except ImportError:
        log.info("lyria_sdk_not_installed")
        return False

    try:
        endpoint = (
            f"projects/{settings.vertex_project_id}/locations/{settings.vertex_location}"
            f"/publishers/google/models/{settings.lyria_model}"
        )
        client = aiplatform_v1.PredictionServiceClient(
            client_options={"api_endpoint": f"{settings.vertex_location}-aiplatform.googleapis.com"}
        )
        instance = json_format.ParseDict(
            {
                "prompt": f"{vibe} instrumental. {prompt}",
                "sample_count": 1,
                "seconds_total": duration,
            },
            Value(),
        )
        response = client.predict(endpoint=endpoint, instances=[instance])
        for pred in response.predictions:
            data = json_format.MessageToDict(pred)
            b64 = data.get("bytesBase64Encoded") or data.get("audio")
            if b64:
                import base64

                out_path.write_bytes(base64.b64decode(b64))
                return True
        log.warning("lyria_no_audio_in_response")
    except Exception:
        log.exception("lyria_generate_failed")
    return False


def generate_audio(prompt: str, vibe: str, duration: int, bpm: int) -> GeneratedAudio:
    settings = get_settings()
    storage_dir = Path(settings.audio_storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4()}.wav"
    path = storage_dir / filename

    if _try_lyria(prompt, vibe, duration, path) and path.exists() and path.stat().st_size > 0:
        return GeneratedAudio(filename=filename, path=str(path), provider="lyria")

    _mock_wav(path, vibe, duration, bpm)
    return GeneratedAudio(filename=filename, path=str(path), provider="mock")


def audio_url_for(filename: str) -> str:
    prefix = get_settings().audio_public_prefix.rstrip("/")
    return f"{prefix}/{filename}"


def audio_path_for(filename: str) -> Path:
    return Path(get_settings().audio_storage_dir) / filename


def is_safe_filename(name: str) -> bool:
    return bool(name) and "/" not in name and "\\" not in name and ".." not in name and os.path.basename(name) == name
