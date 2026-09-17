from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .config import Settings, get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> str | None:
    if not settings.api_key:
        return None
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")
    return x_api_key
