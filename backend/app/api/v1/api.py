"""Versioned API router."""

from __future__ import annotations

from fastapi import APIRouter

from .endpoints import documents, export, tasks, upload

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(upload.router)
api_router.include_router(documents.router)
api_router.include_router(tasks.router)
api_router.include_router(export.router)

