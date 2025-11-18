"""Upload endpoint."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_session
from ....core.security import validate_magic_bytes, validate_mime_type
from ....models import Document
from ....services.storage import StorageService
from ....workers.tasks import process_document

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=202)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> dict:
    """Upload document(s) and trigger background processing."""

    if len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one file required.")

    storage = StorageService()
    created = []
    for file in files:
        content = await file.read()
        validate_mime_type(file.content_type or "")
        validate_magic_bytes(content[:8])
        file.file.seek(0)
        path = storage.save_upload(file)
        document = Document(
            filename=file.filename or "document",
            file_path=str(path),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            status="pending",
        )
        session.add(document)
        created.append(document)
    await session.commit()
    for document in created:
        background_tasks.add_task(process_document.delay, document.id)
    return {"documents": [doc.id for doc in created]}

