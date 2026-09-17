from __future__ import annotations

from fastapi import APIRouter

from ..schemas import SUPPORTED_VIBES, VibesResponse

router = APIRouter()


@router.get("/")
def root() -> dict:
    return {"service": "bean-sounds", "status": "ok"}


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "bean-sounds"}


@router.get("/api/vibes", response_model=VibesResponse)
def vibes() -> VibesResponse:
    return VibesResponse(vibes=SUPPORTED_VIBES)
