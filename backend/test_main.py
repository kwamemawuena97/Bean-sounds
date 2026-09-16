from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_endpoint_returns_service_info():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "bean-sounds"


def test_health_endpoint_is_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_song_accepts_valid_prompt():
    response = client.post(
        "/api/generate",
        json={"prompt": "Sunset on the coast and a deep African heartbeat", "vibe": "Afro-fusion", "duration": 90},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mood"] == "Afro-fusion"
    assert len(payload["lyrics"]) > 50
    assert payload["generated_by"] in {"gemini", "fallback"}
    assert isinstance(payload["sections"], list)
    assert len(payload["sections"]) >= 3


def test_generate_song_rejects_empty_prompt():
    response = client.post(
        "/api/generate",
        json={"prompt": "", "vibe": "Afro-fusion", "duration": 60},
    )
    assert response.status_code == 422


def test_vibes_endpoint_lists_supported_styles():
    response = client.get("/api/vibes")
    assert response.status_code == 200
    payload = response.json()
    assert "vibes" in payload
    assert "Afro-fusion" in payload["vibes"]
    assert "Afrobeats" in payload["vibes"]


def test_generate_song_includes_rich_metadata():
    response = client.post(
        "/api/generate",
        json={"prompt": "Night drive and neon reflections", "vibe": "House", "duration": 120},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["duration"] == 120
    assert payload["key"] in {"A", "B", "C", "D", "E", "F", "G", "G#m", "Bm", "Am"}
    assert payload["energy"] in {"Low", "Medium", "High", "Peak"}
    assert payload["generated_by"] in {"gemini", "fallback"}


def test_generate_song_rejects_unsupported_vibe():
    response = client.post(
        "/api/generate",
        json={"prompt": "Night drive and neon reflections", "vibe": "Jazz", "duration": 60},
    )
    assert response.status_code == 422
