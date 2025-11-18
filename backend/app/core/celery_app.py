"""Celery application factory."""

from __future__ import annotations

from celery import Celery

from .config import settings

celery_app = Celery(
    "docia",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

