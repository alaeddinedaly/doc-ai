"""Celery task definitions."""

from __future__ import annotations

import asyncio
import logging
import time

from sqlalchemy import select

from ..core.celery_app import celery_app
from ..core.config import settings
from ..core.database import SessionLocal, init_models
from ..models import Document
from ..services.extraction import ExtractionPipeline
from ..services.tasks import TaskTracker

logger = logging.getLogger(__name__)
tracker = TaskTracker()
_db_initialized = False
_db_init_lock = asyncio.Lock()
worker_loop = asyncio.new_event_loop()
asyncio.set_event_loop(worker_loop)


async def ensure_db_initialized() -> None:
    """Run database migrations once per worker process."""

    global _db_initialized
    if _db_initialized:
        return
    async with _db_init_lock:
        if not _db_initialized:
            await init_models()
            _db_initialized = True


@celery_app.task(bind=True, max_retries=3, name="process_document")
def process_document(self, document_id: str) -> str:
    """Background document processing pipeline."""

    task_id = self.request.id or document_id
    tracker.set_progress(
        task_id,
        status="processing",
        current_step=0,
        total_steps=5,
        message="Starting processing",
    )

    async def _run() -> str:
        await ensure_db_initialized()
        async with SessionLocal() as session:
            pipeline = ExtractionPipeline(session=session)

            tracker.set_progress(
                task_id,
                status="processing",
                current_step=1,
                total_steps=5,
                message="Fetching document",
            )

            document = await session.scalar(select(Document).where(Document.id == document_id))
            if not document:
                raise ValueError("Document not found")
            document.status = "processing"
            await session.commit()

            tracker.set_progress(
                task_id,
                status="processing",
                current_step=2,
                total_steps=5,
                message="Running pipeline",
            )

            extraction_result = await pipeline.run(document_id)

            tracker.set_progress(
                task_id,
                status="completed",
                current_step=5,
                total_steps=5,
                message="Completed",
                result_id=extraction_result.document.id,
            )
            return extraction_result.document.id

    try:
        return worker_loop.run_until_complete(_run())
    except Exception as exc:  # noqa: BLE001
        logger.exception("Processing failed for %s: %s", document_id, exc)
        tracker.set_progress(
            task_id,
            status="failed",
            current_step=5,
            total_steps=5,
            message=str(exc),
        )
        raise self.retry(exc=exc, countdown=60)

