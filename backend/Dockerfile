FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --uid 1001 --create-home appuser && \
    mkdir -p /app/audio_storage /app/data && \
    chown -R appuser:appuser /app
USER appuser

ENV DATABASE_URL=sqlite:////app/data/bean_sounds.db \
    AUDIO_STORAGE_DIR=/app/audio_storage

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
