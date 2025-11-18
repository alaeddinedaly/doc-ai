"""High level extraction orchestrator."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Document, Extraction
from .gemini import GeminiService
from .text_extraction import TextExtractionService

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Represents aggregated extraction output."""

    document: Document
    extraction: Extraction


class ExtractionPipeline:
    """Coordinates text extraction and Gemini structuring."""

    def __init__(
        self,
        session: AsyncSession,
        text_reader: TextExtractionService | None = None,
        gemini: GeminiService | None = None,
    ) -> None:
        self.session = session
        self.text_reader = text_reader or TextExtractionService()
        self.gemini = gemini or GeminiService()

    async def run(self, document_id: str) -> ExtractionResult:
        """Execute the extraction pipeline for a document."""

        document = await self.session.scalar(select(Document).where(Document.id == document_id))
        if not document:
            raise ValueError("Document not found")

        start_time = time.perf_counter()
        extracted_text = await asyncio.to_thread(
            self.text_reader.extract_text, document.file_path, document.mime_type
        )
        gemini_payload = self.gemini.extract(extracted_text)
        doc_type, confidence = self._enhance_metadata(
            gemini_payload.get("document_type", "other"),
            gemini_payload.get("confidence_score"),
            extracted_text,
            gemini_payload,
        )
        gemini_payload["document_type"] = doc_type
        gemini_payload["confidence_score"] = confidence
        processing_time = time.perf_counter() - start_time

        extraction = await self._persist_extraction(
            document=document,
            gemini_payload=gemini_payload,
            ocr_text=extracted_text,
            processing_time=processing_time,
        )
        return ExtractionResult(document=document, extraction=extraction)

    def _enhance_metadata(
        self,
        doc_type: str,
        confidence: float | None,
        full_text: str,
        payload: dict[str, Any],
    ) -> tuple[str, float]:
        """Improve document type and confidence when Gemini is unsure."""

        normalized_text = full_text.lower()
        candidates = {
            "invoice": ["facture", "invoice", "montant", "tva", "numéro de facture"],
            "contract": ["contrat", "agreement", "signature", "clause"],
            "receipt": ["receipt", "reçu", "cash", "payment"],
        }
        detected_type = doc_type or "other"
        for dtype, keywords in candidates.items():
            if any(keyword in normalized_text for keyword in keywords):
                detected_type = dtype
                break

        base_confidence = confidence if isinstance(confidence, (int, float)) else 0.0
        filled_fields = sum(1 for key, value in payload.items() if key != "confidence_score" and value not in (None, "", []))
        if filled_fields >= 3 and base_confidence < 0.7:
            base_confidence = 0.7
        elif filled_fields >= 1 and base_confidence < 0.4:
            base_confidence = 0.4

        if detected_type != (doc_type or "other") and base_confidence < 0.6:
            base_confidence = 0.65

        return detected_type, min(base_confidence, 0.99)

    async def _persist_extraction(
        self,
        document: Document,
        gemini_payload: dict[str, Any],
        ocr_text: str,
        processing_time: float,
    ) -> Extraction:
        extraction = Extraction(
            document=document,
            document_type=gemini_payload.get("document_type", "other"),
            extracted_data=gemini_payload,
            confidence_scores={
                key: gemini_payload.get("confidence_score", 0.0)
                for key in gemini_payload.keys()
            },
            ocr_text=ocr_text,
            processing_time=processing_time,
        )
        document.status = "completed"
        document.processed_at = document.processed_at or document.uploaded_at
        self.session.add(extraction)
        await self.session.commit()
        await self.session.refresh(extraction)
        return extraction

