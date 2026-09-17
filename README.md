# Bean-sounds

AI-powered Afro-inspired song generator: lyrics via Gemini, optional audio via Lyria (Vertex AI) with a mock WAV fallback so the app is fully usable offline. FastAPI backend, Next.js frontend, SQLite persistence.

## Features
- Prompt-based lyric generation (verse / chorus / bridge / final chorus) via Gemini
- Audio preview generation via Lyria on Vertex AI, with a local sine-wave fallback
- Song history — every generation is persisted and playable
- Vibes: Afro-fusion, Afrobeats, Highlife, Gospel, House
- Locked CORS, per-IP rate limiting, optional API-key auth, structured JSON logs

## Project structure
```
backend/
  app/
    main.py           FastAPI factory, middleware, lifespan
    config.py         pydantic-settings config
    db.py             SQLAlchemy engine/session
    models.py         Song ORM model
    schemas.py        Pydantic request/response
    deps.py           API-key dependency
    logging_conf.py   JSON logging
    routers/          meta, songs, audio
    services/         lyrics (Gemini), audio (Lyria + mock)
  test_main.py
  Dockerfile
frontend/
  app/                Next.js app router
  Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

## Local setup

### 1) Backend
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev -- --port 3000
```

### 3) Environment
Copy `.env.example` to `backend/.env` and set what you need. All keys are optional — the app runs end-to-end without any (mock lyrics + mock audio).

## API
- `GET /health`
- `GET /api/vibes`
- `POST /api/generate` — body: `{ prompt, vibe, duration, with_audio? }`
- `POST /api/generate-audio` — body: `{ song_id }`
- `GET /api/songs?limit=`
- `GET /api/songs/{id}`
- `GET /audio/{filename}`

## Docker
```bash
docker compose up --build
```
Frontend: http://localhost:3000  ·  Backend: http://localhost:8000

## Tests
```bash
cd backend && pytest
```
CI runs backend tests and a frontend build on every push.
