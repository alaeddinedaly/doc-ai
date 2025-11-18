"""Image preprocessing pipeline."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image


@dataclass
class PreprocessResult:
    """Container for preprocessing output."""

    image: np.ndarray
    steps: list[str]


class PreprocessingService:
    """Pipeline responsible for preparing documents for OCR."""

    def __init__(self) -> None:
        self.steps_log: list[str] = []

    def _log(self, message: str) -> None:
        self.steps_log.append(message)

    def load_bytes(self, file_bytes: bytes, mime_type: str) -> np.ndarray:
        """Convert file bytes to an OpenCV image."""

        if mime_type == "application/pdf":
            images = convert_from_bytes(file_bytes)
            with io.BytesIO() as buffer:
                images[0].save(buffer, format="PNG")
                buffer.seek(0)
                return self.load_bytes(buffer.read(), "image/png")
        pil_image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def preprocess(self, file_bytes: bytes, mime_type: str) -> PreprocessResult:
        """Execute the full preprocessing pipeline."""

        image = self.load_bytes(file_bytes, mime_type)
        self._log("Loaded image")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self._log("Grayscale conversion")

        gray = self._correct_rotation(gray)
        self._log("Rotation correction")

        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        self._log("Denoising")

        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35,
            11,
        )
        self._log("Adaptive threshold")

        deskewed = self._deskew(thresh)
        self._log("Deskew")

        cropped = self._crop_borders(deskewed)
        self._log("Border removal")

        return PreprocessResult(image=cropped, steps=self.steps_log.copy())

    def _correct_rotation(self, gray: np.ndarray) -> np.ndarray:
        coords = np.column_stack(np.where(gray > 0))
        angle = 0.0
        if len(coords):
            rect = cv2.minAreaRect(coords)
            angle = rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(gray, matrix, (w, h), flags=cv2.INTER_CUBIC)

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        edges = cv2.Canny(image, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi / 180.0, 200)
        angle = 0.0
        if lines is not None:
            angles = [(theta - np.pi / 2) for rho, theta in lines[:, 0]]
            angle = np.mean(angles)
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle * 180 / np.pi, 1.0)
        return cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_LINEAR)

    def _crop_borders(self, image: np.ndarray) -> np.ndarray:
        coords = cv2.findNonZero(image)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            return image[y : y + h, x : x + w]
        return image

