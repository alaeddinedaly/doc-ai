"""FastAPI application entrypoint."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.api import api_router
from .core.config import settings
from .core.database import init_models
from .core.logging_config import setup_logging

setup_logging()

app = FastAPI(title=settings.app_name, version="1.0.0")
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthcheck() -> dict:
    """Simple health endpoint for Docker."""

    return {"status": "ok"}


@app.on_event("startup")
async def init_database() -> None:
    """Ensure database schema exists."""

    await init_models()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
