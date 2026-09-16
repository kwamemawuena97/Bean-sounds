# Bean-sounds

Bean-sounds is an AI-powered song generator for Afro-inspired music ideas, built with a FastAPI backend and a Next.js frontend.

## Features
- Prompt-based song generation
- Afro-fusion, Afrobeats, Highlife, Gospel, and House-inspired vibes
- FastAPI API for generation requests
- Next.js UI for prompt input and song preview
- Gemini-ready backend with a mock fallback when no API key is configured

## Project structure
- backend/ - FastAPI service
- frontend/ - Next.js app
- .env.example - sample environment variable template

## Local setup

### 1) Backend
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

### 3) Environment
Create a local `.env` file in the backend folder with:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

## App URLs
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- Health check: http://localhost:8000/health

## Notes
The backend will use Gemini when a valid API key is available. If not, it falls back to a generated mock lyric response so the app remains usable locally.
