"""Document retrieval endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....core.database import get_session
from ....models import Document, Extraction

router = APIRouter()


@router.get("/documents")
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type: str | None = Query(default=None, alias="type"),
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = "uploaded_at",
    order: str = Query("desc", pattern="^(asc|desc)$"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> dict:
    """Return paginated documents with filters."""

    query = select(Document).options(selectinload(Document.extraction))
    if type:
        query = query.join(Document.extraction, isouter=True).where(
            Extraction.document_type == type
        )
    if date_from:
        query = query.where(Document.uploaded_at >= date_from)
    if date_to:
        query = query.where(Document.uploaded_at <= date_to)

    sort_column = getattr(Document, sort_by, Document.uploaded_at)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column).offset((page - 1) * limit).limit(limit)
    result = await session.scalars(query)
    count_query = select(func.count()).select_from(Document)
    if type:
        count_query = count_query.join(Document.extraction, isouter=True).where(
            Extraction.document_type == type
        )
    if date_from:
        count_query = count_query.where(Document.uploaded_at >= date_from)
    if date_to:
        count_query = count_query.where(Document.uploaded_at <= date_to)
    total = await session.scalar(count_query)

    data = []
    for doc in result:
        extraction = doc.extraction
        data.append(
            {
                "id": doc.id,
                "filename": doc.filename,
                "mime_type": doc.mime_type,
                "file_size": doc.file_size,
                "status": doc.status,
                "uploaded_at": doc.uploaded_at,
                "processed_at": doc.processed_at,
                "document_type": extraction.document_type if extraction else None,
                "extracted_data": extraction.extracted_data if extraction else None,
                "confidence_scores": extraction.confidence_scores if extraction else None,
            }
        )
    return {"data": data, "total": total or 0, "page": page, "limit": limit}


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> dict:
    """Fetch a single document with extraction data."""

    document = await session.get(
        Document,
        document_id,
        options=(selectinload(Document.extraction),),
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    extraction = document.extraction
    return {
        "id": document.id,
        "filename": document.filename,
        "mime_type": document.mime_type,
        "file_size": document.file_size,
        "status": document.status,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at,
        "error_message": document.error_message,
        "download_url": f"/api/v1/files/{document.id}",
        "extracted_data": extraction.extracted_data if extraction else None,
        "confidence_scores": extraction.confidence_scores if extraction else None,
        "document_type": extraction.document_type if extraction else None,
        "ocr_text": extraction.ocr_text if extraction else None,
        "processing_time": extraction.processing_time if extraction else None,
    }


@router.patch("/documents/{document_id}/extracted-data")
async def update_extracted_data(
    document_id: str,
    payload: dict,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> dict:
    """Allow manual correction of extracted fields."""

    document = await session.get(
        Document,
        document_id,
        options=(selectinload(Document.extraction),),
    )
    if not document or not document.extraction:
        raise HTTPException(status_code=404, detail="Document not found")
    extraction = document.extraction
    extraction.extracted_data.update(payload.get("extracted_data", {}))
    scores = payload.get("confidence_scores") or {}
    for key in payload.get("extracted_data", {}):
        scores[key] = 1.0
    extraction.confidence_scores.update(scores)
    extraction.manually_corrected = True
    await session.commit()
    await session.refresh(extraction)
    return {"status": "ok", "extracted_data": extraction.extracted_data}

