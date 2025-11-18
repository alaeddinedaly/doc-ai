"""Export endpoint."""

from __future__ import annotations

import csv
import io
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_session
from ....models import Document
from ....schemas.document import ExportRequest

router = APIRouter()


@router.post("/export")
async def export_documents(
    payload: ExportRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> Response:
    """Export selected documents as JSON/CSV/Excel."""

    query = select(Document).where(Document.id.in_(payload.document_ids))
    result = await session.scalars(query)
    documents = list(result)
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")

    rows = [
        {
            "id": doc.id,
            "filename": doc.filename,
            "document_type": doc.extraction.document_type if doc.extraction else None,
            "invoice_number": doc.extraction.extracted_data.get("invoice_number")
            if doc.extraction
            else None,
            "amount_ttc": doc.extraction.extracted_data.get("amount_ttc")
            if doc.extraction
            else None,
        }
        for doc in documents
    ]

    if payload.format == "json":
        return Response(
            content=json.dumps(rows),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=export.json"},
        )

    if payload.format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return Response(
            content=buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )

    # Excel fallback via CSV with .xls extension for simplicity
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=rows[0].keys(), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": "attachment; filename=export.xls"},
    )

