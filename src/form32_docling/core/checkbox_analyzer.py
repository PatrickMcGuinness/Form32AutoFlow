"""Checkbox analyzer module for Form 32 processing.

This module provides ROI-based checkbox detection using OpenCV.
Docling handles text extraction; this module handles checkbox states.
"""

import logging
from pathlib import Path

import cv2
import numpy as np
from pdf2image import convert_from_path

from form32_docling.core.constants import CHECKBOX_PARAMS, FormPages

logger = logging.getLogger(__name__)





class CheckboxAnalyzer:
    """Analyzes checkbox states in Form 32 using OpenCV.

    Uses ROI-based binary threshold analysis to detect filled checkboxes.
    """

    def __init__(self, pdf_path: str | Path) -> None:
        """Initialize analyzer with PDF path.

        Args:
            pdf_path: Path to the Form 32 PDF file.
        """
        self.pdf_path = Path(pdf_path)
        self._images: list[np.ndarray] | None = None
        self._page_types: dict[FormPages, int] = {}

    @property
    def images(self) -> list[np.ndarray]:
        """Lazy-load PDF page images."""
        if self._images is None:
            pages = convert_from_path(str(self.pdf_path))
            self._images = [np.array(page) for page in pages]
        return self._images

    def identify_page_type(self, page_text: str) -> FormPages | None:
        """Identify page type from extracted text.

        Args:
            page_text: Text content of the page (from docling).

        Returns:
            FormPages enum value or None if not a key page.
        """
        text_lower = page_text.lower()

        if "22. does the claim have medical benefits" in text_lower:
            return FormPages.NETWORK

        if any(
            phrase in text_lower
            for phrase in [
                "30. check all body areas",
                "part 4. designated doctor selection",
                "body areas and diagnoses",
            ]
        ):
            return FormPages.BODY_AREA

        if any(
            phrase in text_lower
            for phrase in ["purpose of examination", "check boxes a through g"]
        ):
            return FormPages.PURPOSE

        return None

    def set_page_mapping(self, page_texts: list[str]) -> None:
        """Map page types to their indices using docling text.

        Args:
            page_texts: List of text content for each page.
        """
        self._page_types.clear()
        for idx, text in enumerate(page_texts):
            page_type = self.identify_page_type(text)
            if page_type:
                self._page_types[page_type] = idx
                logger.debug(f"Found {page_type.value} page at index {idx}")

    def _analyze_roi(
        self,
        img: np.ndarray,
        y: int,
        x: int,
        w: int,
        h: int,
        threshold: float,
    ) -> bool:
        """Analyze a region of interest for checkbox detection.

        Args:
            img: Page image as numpy array.
            y: Y-coordinate of ROI.
            x: X-coordinate of ROI.
            w: Width of ROI.
            h: Height of ROI.
            threshold: Fill ratio threshold for detection.

        Returns:
            True if checkbox appears filled.
        """
        # Bounds checking
        max_y = min(y + h, img.shape[0])
        max_x = min(x + w, img.shape[1])

        if y >= img.shape[0] or x >= img.shape[1]:
            logger.warning(f"ROI out of bounds: x={x}, y={y}")
            return False

        roi = img[y:max_y, x:max_x]

        # Convert to grayscale and threshold
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

        # Calculate fill ratio
        total_pixels = binary.size
        filled_pixels = np.sum(binary == 255)
        fill_ratio = filled_pixels / total_pixels

        return bool(fill_ratio > threshold)

    def analyze_network_checkboxes(self) -> dict[str, bool]:
        """Analyze Q22/Q23 network checkboxes.

        Returns:
            Dictionary with network checkbox results.
        """
        results = {"has_certified_network": False, "has_political_subdivision": False}

        if FormPages.NETWORK not in self._page_types:
            logger.warning("Network page not found")
            return results

        page_idx = self._page_types[FormPages.NETWORK]
        img = self.images[page_idx]
        params = CHECKBOX_PARAMS["network"]

        for box_name, y_coord in params["checkboxes"].items():
            x_coord = params["x"]
            if box_name.endswith("_no"):
                x_coord += params["x_offsets"].get(box_name, 0)

            is_checked = self._analyze_roi(
                img, y_coord, x_coord, params["w"], params["h"], params["threshold"]
            )

            if is_checked:
                if box_name == "q22_yes":
                    results["has_certified_network"] = True
                elif box_name == "q23_yes":
                    results["has_political_subdivision"] = True

        return results

    def analyze_body_area_checkboxes(self) -> dict[str, bool]:
        """Analyze body area checkboxes on Part 4 page.

        Returns:
            Dictionary with body area flags.
        """
        results = dict.fromkeys(CHECKBOX_PARAMS["body_area"]["checkboxes"], False)

        if FormPages.BODY_AREA not in self._page_types:
            logger.warning("Body area page not found")
            return results

        page_idx = self._page_types[FormPages.BODY_AREA]
        img = self.images[page_idx]
        params = CHECKBOX_PARAMS["body_area"]

        for field, y_coord in params["checkboxes"].items():
            results[field] = self._analyze_roi(
                img, y_coord, params["x"], params["w"], params["h"], params["threshold"]
            )

        return results

    def analyze_purpose_checkboxes(self) -> dict[str, bool]:
        """Analyze purpose checkboxes (A-G) and DWC-024.

        Returns:
            Dictionary with purpose flags.
        """
        results = dict.fromkeys(CHECKBOX_PARAMS["purpose"]["checkboxes"], False)

        if FormPages.PURPOSE not in self._page_types:
            logger.warning("Purpose page not found")
            return results

        page_idx = self._page_types[FormPages.PURPOSE]
        img = self.images[page_idx]
        params = CHECKBOX_PARAMS["purpose"]

        for field, y_coord in params["checkboxes"].items():
            results[field] = self._analyze_roi(
                img, y_coord, params["x"], params["w"], params["h"], params["threshold"]
            )

        return results

    def analyze_all(self) -> dict[str, dict[str, bool]]:
        """Analyze all checkbox types.

        Returns:
            Dictionary with all checkbox results organized by type.
        """
        return {
            "network": self.analyze_network_checkboxes(),
            "body_areas": self.analyze_body_area_checkboxes(),
            "purpose": self.analyze_purpose_checkboxes(),
        }
