"""Gemini extraction service."""

from __future__ import annotations

import json
import logging

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..core.config import settings

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are an expert at extracting structured data from OCR text of French business documents.

TASK: Extract key information from this invoice text and return ONLY valid JSON.

RULES:
1. Dates must be ISO format (YYYY-MM-DD)
2. Numbers must be float (no currency symbols)
3. If field not found, use null
4. Include confidence: 0.0-1.0 based on clarity
5. Detect document_type: "invoice" | "contract" | "receipt" | "other"

OCR TEXT:
{ocr_text}

JSON OUTPUT:
"""


class GeminiService:
    """Wrapper for Gemini generative extraction."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def extract(self, ocr_text: str) -> dict:
        """Extract structured fields from OCR text."""

        prompt = PROMPT_TEMPLATE.format(ocr_text=ocr_text)
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.BLOCK_NONE,
                },
            )
            text = response.text or "{}"
            return self._safe_json_loads(text)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Gemini extraction failed: %s", exc)
            return {"document_type": "other", "confidence_score": 0.0}

    def _safe_json_loads(self, raw: str) -> dict:
        """Attempt to parse JSON output and recover if needed."""

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.split("{", 1)[-1]
            cleaned = "{" + cleaned
            cleaned = cleaned.rsplit("}", 1)[0] + "}"
            try:
                return json.loads(cleaned)
            except Exception:  # noqa: BLE001
                logger.error("Unable to parse Gemini output: %s", raw)
                return {"document_type": "other", "confidence_score": 0.0}

