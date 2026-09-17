from __future__ import annotations

import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")
os.environ.setdefault("AUDIO_STORAGE_DIR", tempfile.mkdtemp())
os.environ.setdefault("RATE_LIMIT_GENERATE", "1000/minute")
os.environ.setdefault("RATE_LIMIT_AUDIO", "1000/minute")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402

init_db()
client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "bean-sounds"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vibes_endpoint():
    response = client.get("/api/vibes")
    assert response.status_code == 200
    payload = response.json()
    assert "Afro-fusion" in payload["vibes"]
    assert "Afrobeats" in payload["vibes"]


def test_generate_song_valid_prompt():
    response = client.post(
        "/api/generate",
        json={"prompt": "Sunset on the coast", "vibe": "Afro-fusion", "duration": 90},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mood"] == "Afro-fusion"
    assert len(payload["lyrics"]) > 20
    assert payload["generated_by"].startswith(("gemini", "fallback"))
    assert isinstance(payload["sections"], list)
    assert payload["id"]


def test_generate_song_rejects_empty_prompt():
    response = client.post("/api/generate", json={"prompt": "", "vibe": "Afro-fusion", "duration": 60})
    assert response.status_code == 422


def test_generate_song_rejects_unsupported_vibe():
    response = client.post("/api/generate", json={"prompt": "hello", "vibe": "Jazz", "duration": 60})
    assert response.status_code == 422


def test_generate_song_metadata():
    response = client.post(
        "/api/generate",
        json={"prompt": "Night drive neon", "vibe": "House", "duration": 120},
    )
    payload = response.json()
    assert payload["duration"] == 120
    assert payload["key"] in {"A", "D", "G", "F", "E"}
    assert payload["energy"] in {"Low", "Medium", "High", "Peak"}


def test_generate_with_audio_and_serve():
    response = client.post(
        "/api/generate",
        json={"prompt": "Coastal breeze", "vibe": "Highlife", "duration": 30, "with_audio": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["audio_url"]
    assert payload["audio_provider"] in {"lyria", "mock"}

    audio_resp = client.get(payload["audio_url"])
    assert audio_resp.status_code == 200
    assert audio_resp.headers["content-type"].startswith("audio/")


def test_generate_audio_for_existing_song():
    created = client.post(
        "/api/generate",
        json={"prompt": "River road", "vibe": "Gospel", "duration": 30},
    ).json()
    assert created["audio_url"] is None
    response = client.post("/api/generate-audio", json={"song_id": created["id"]})
    assert response.status_code == 200
    payload = response.json()
    assert payload["audio_url"]


def test_generate_audio_for_missing_song():
    response = client.post("/api/generate-audio", json={"song_id": "does-not-exist"})
    assert response.status_code == 404


def test_list_and_get_songs():
    client.post("/api/generate", json={"prompt": "Listing test", "vibe": "Afrobeats", "duration": 30})
    response = client.get("/api/songs?limit=5")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    detail = client.get(f"/api/songs/{items[0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == items[0]["id"]


def test_get_song_not_found():
    response = client.get("/api/songs/missing")
    assert response.status_code == 404


def test_audio_rejects_path_traversal():
    response = client.get("/audio/..%2Fetc%2Fpasswd")
    assert response.status_code in (400, 404)
