"""Form32 processor using docling for document extraction.

This module provides the main processor for Form 32 PDFs using IBM's
docling library for text extraction and layout analysis.
"""

import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, cast

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    RapidOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

# Optional: docling.datamodel.settings may not exist in all versions
docling_settings: Any | None
try:
    from docling.datamodel.settings import settings as _docling_settings
    HAS_DOCLING_SETTINGS = True
    docling_settings = _docling_settings
except ImportError:
    HAS_DOCLING_SETTINGS = False
    docling_settings = None


from form32_docling.config import Config  # noqa: E402
from form32_docling.config.form32_templates import FIELD_TO_ATTRIBUTE_MAP  # noqa: E402
from form32_docling.core.checkbox_analyzer import CheckboxAnalyzer  # noqa: E402
from form32_docling.core.constants import EXTRACTION_PATTERNS  # noqa: E402
from form32_docling.core.docling_extractor import Form32Extractor  # noqa: E402
from form32_docling.forms import FormGenerationController  # noqa: E402
from form32_docling.models import Form32Data, PatientInfo  # noqa: E402

logger = logging.getLogger(__name__)



class Form32Processor:
    """Process Form 32 PDFs using docling for extraction.

    Uses docling DocumentConverter for text extraction with built-in OCR,
    and OpenCV (via CheckboxAnalyzer) for checkbox state detection.
    """

    def __init__(
        self,
        pdf_path: str | Path,
        config: Config | None = None,
        *,
        verbose: bool = True,
    ) -> None:
        """Initialize processor.

        Args:
            pdf_path: Path to the Form 32 PDF file.
            config: Configuration instance.
            verbose: Enable verbose logging.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.__init__(pdf_path={pdf_path}, verbose={verbose})")
        self.pdf_path = Path(pdf_path)
        self.config = config or Config()
        self.verbose = verbose
        self.validation_errors: list[str] = []

        # Initialize data model
        self.patient_info = PatientInfo()

        # Lazy-loaded components
        self._converter: DocumentConverter | None = None
        self._document: Any = None
        self._full_text: str = ""
        self._page_texts: list[str] = []
        self._checkbox_analyzer: CheckboxAnalyzer | None = None
        self._vlm_set_fields: set[str] = set()
        self._field_sources: dict[str, str] = {}
        self._extracted_fields_trace: dict[str, Any] = {
            "vlm_raw": {},
            "vlm_mapped": [],
            "regex_fallback": [],
            "location_fallback": [],
            "opencv_fallback": [],
            "final_sources": {},
        }

        if verbose:
            logger.setLevel(logging.DEBUG)
            # Enable docling's built-in pipeline profiler for detailed timing (if available)
            if HAS_DOCLING_SETTINGS and docling_settings is not None:
                try:
                    docling_settings.debug.profile_pipeline_timings = True
                    logger.debug("Enabled docling pipeline timing profiler")
                except AttributeError:
                    logger.debug("docling.settings.debug.profile_pipeline_timings not available")
        self._try_enable_docling_offline_cache()

    # Not using VLM in converter, just PDF layout analysis to get text for classification.
    @property
    def converter(self) -> DocumentConverter:
        """Lazy-load docling DocumentConverter."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.converter property")
        if self._converter is None:
            pdf_pipeline_options = PdfPipelineOptions()
            pdf_pipeline_options.images_scale = 1.0  # 2.0+ scale helps with small fonts
            pdf_pipeline_options.generate_page_images = self.config.docling_generate_page_images
            pdf_pipeline_options.enable_remote_services = False
            # Force RapidOCR (torch backend) to skip auto-probing unavailable OCR engines.
            pdf_pipeline_options.ocr_options = RapidOcrOptions(backend="torch")
            self._converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=pdf_pipeline_options
                    )
            }
        )
        return self._converter

    def _try_enable_docling_offline_cache(self) -> None:
        """Enable HF/Transformers offline mode when required docling models are cached."""
        if not self.config.docling_prefer_offline_cache:
            return
        if os.environ.get("HF_HUB_OFFLINE") == "1":
            return

        hub_root = Path.home() / ".cache" / "huggingface" / "hub"
        required_models = (
            hub_root / "models--docling-project--docling-layout-heron",
            hub_root / "models--docling-project--docling-models",
        )
        if all(model_path.exists() for model_path in required_models):
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            logger.info("Enabled offline Hugging Face/Transformers mode from local cache")
        else:
            missing = [str(path) for path in required_models if not path.exists()]
            logger.debug(f"Offline cache mode not enabled; missing cached models: {missing}")

    def _log_phase_timing(self, phase: str, elapsed_seconds: float, budget_seconds: float | None) -> None:
        """Log phase timing and warn when budget is exceeded."""
        logger.info(f"PHASE_{phase.upper()} elapsed: {elapsed_seconds:.2f}s")
        if budget_seconds is not None and elapsed_seconds > budget_seconds:
            logger.warning(
                f"PHASE_{phase.upper()} exceeded budget: {elapsed_seconds:.2f}s > {budget_seconds:.2f}s"
            )


    def _extract_page_texts(self, document: Any) -> list[str]:
        """Extract text for each page from a DoclingDocument.

        Uses the Docling iterate_items(page_no=N) API to collect text items
        per page.

        Args:
            document: A DoclingDocument instance from docling conversion.

        Returns:
            List of text strings, one per page (0-indexed list for 1-indexed pages).
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER _extract_page_texts()")
        page_texts: list[str] = []

        try:
            num_pages = cast(int, document.num_pages()) if callable(document.num_pages) else 0
            logger.debug(f"Document has {num_pages} pages")

            for page_num in range(1, num_pages + 1):
                page_text_parts: list[str] = []

                # iterate_items with page_no filters to items on that page
                for item, _level in document.iterate_items(page_no=page_num):
                    # TextItem, SectionHeaderItem, etc. have .text attribute
                    if hasattr(item, "text") and item.text:
                        page_text_parts.append(item.text)

                page_text = "\n".join(page_text_parts)
                page_texts.append(page_text)
                logger.debug(f"Page {page_num}: extracted {len(page_text)} chars from {len(page_text_parts)} items")

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning(f"Failed to extract page texts via iterate_items: {e}")

        return page_texts

    @property
    def full_text(self) -> str:
        """Get full extracted text."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.full_text property")
        if not self._full_text:
            self._convert_with_docling()
        return self._full_text

    def _convert_with_docling(self) -> bool:
        """Extract text from PDF using docling.

        Returns:
            True if extraction succeeded.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._convert_with_docling()")
        try:
            logger.info(f"Extracting text with docling: {self.pdf_path}")

            # Time the document conversion (typically the slowest step)
            convert_start = datetime.now()
            logger.debug(f"[{convert_start.isoformat()}] DOCLING_CONVERT_START")

            result = self.converter.convert(str(self.pdf_path))

            convert_end = datetime.now()
            convert_elapsed = (convert_end - convert_start).total_seconds()
            logger.info(f"[{convert_end.isoformat()}] DOCLING_CONVERT_END - elapsed: {convert_elapsed:.2f}s")

            self._document = result.document

            # Time the markdown export
            export_start = datetime.now()
            self._full_text = self._document.export_to_markdown()
            export_elapsed = (datetime.now() - export_start).total_seconds()
            logger.debug(f"DOCLING_EXPORT_MARKDOWN - elapsed: {export_elapsed:.2f}s")

            # Extract per-page text using iterate_items API
            self._page_texts = self._extract_page_texts(self._document)

            extracted_via_obj = any(t.strip() for t in self._page_texts)

            # Fallback if object extraction failed but we have full text
            if (not extracted_via_obj or all(not t.strip() for t in self._page_texts)) and self._full_text:
                logger.info("Using markdown splitting for page text extraction")
                # Docling markdown typically separates pages with "PAGE <n>" or similar
                # We'll rely on our specific docling version's output format
                # The preview showed "PAGE 1", "PAGE 2" etc.

                # Simple split by "PAGE <n>"
                # Note: This might be fragile if "PAGE <n>" appears in content,
                # but docling usually makes it a distinct block.

                parts = re.split(r"\nPAGE \d+\n", self._full_text)

                if len(parts) > 1:
                    # parts[0] is usually empty or content before PAGE 1
                    # If it's just metadata, ignore it or check.
                    # Based on preview: "<!-- image -->\n\nPAGE 1..."
                    # So split gives: ["<!-- image -->\n\n", "Injured..."]

                    # We need to map to physical pages 1..N
                    # If the first part is empty/junk, skip it.
                    candidates = [p for p in parts if p.strip()]

                    # If we have matches comparable to page count
                    if candidates:
                        self._page_texts = candidates
                else:
                    # If regex didn't match, just use full text as single page (better than nothing)
                    self._page_texts = [self._full_text]

            if not self._page_texts:
                 self._page_texts = [self._full_text]


            logger.debug(f"Extracted {len(self._full_text)} characters")
            return bool(self._full_text)

        except (RuntimeError, OSError, ValueError, TypeError) as e:
            logger.error(f"Docling extraction failed: {e}")
            self.validation_errors.append(f"Text extraction failed: {e}")
            return False

    def validate_form(self) -> bool:
        """Validate that this is a valid DWC Form 32.

        Returns:
            True if form appears valid.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.validate_form()")
        validation_markers = self.config.form32_validation_markers

        text_lower = self.full_text.lower()
        missing = []

        for marker, description in validation_markers.items():
            if marker not in text_lower:
                missing.append(description)

        if missing:
            for item in missing:
                self.validation_errors.append(f"Missing required element: {item}")
            return False

        return True

    def _extract_with_patterns(self) -> None:
        """Extract fields using regex patterns on full text."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._extract_with_patterns()")
        text = self.full_text
        for field_name, pattern_list in EXTRACTION_PATTERNS.items():
            if field_name in self._vlm_set_fields:
                self._extracted_fields_trace["regex_fallback"].append(
                    {"field": field_name, "status": "skipped", "reason": "vlm_owned"}
                )
                continue
            current_value = getattr(self.patient_info, field_name, None)
            if not self._is_missing_or_invalid(field_name, current_value):
                self._extracted_fields_trace["regex_fallback"].append(
                    {"field": field_name, "status": "skipped", "reason": "already_set"}
                )
                continue
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = self._clean_value(field_name, match.group(1).strip())
                    if value and self._set_patient_field(
                        field_name,
                        value,
                        source="regex_fallback",
                    ):
                        self._extracted_fields_trace["regex_fallback"].append(
                            {
                                "field": field_name,
                                "pattern": pattern,
                                "value": value,
                                "status": "applied",
                            }
                        )
                        logger.debug(f"Extracted {field_name}: {value}")
                        break
                    self._extracted_fields_trace["regex_fallback"].append(
                        {
                            "field": field_name,
                            "pattern": pattern,
                            "value": value,
                            "status": "skipped",
                            "reason": "invalid_or_not_needed",
                        }
                    )

    def _clean_value(self, field_name: str, value: str) -> str | None:
        """Clean and normalize extracted field values.

        Args:
            field_name: Name of the field being cleaned.
            value: Raw extracted value.

        Returns:
            Cleaned value or None if invalid.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._clean_value(field_name={field_name})")
        if not value:
            return None

        value = value.strip()

        # Date fields
        if field_name in ("exam_date", "date_of_injury", "employee_date_of_birth"):
            match = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", value)
            if match:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

        # Time fields
        if field_name == "exam_time":
            match = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", value, re.IGNORECASE)
            if match:
                return f"{match.group(1)}:{match.group(2)} {match.group(3).upper()}"

        # Phone fields
        if "phone" in field_name or "fax" in field_name:
            digits = "".join(c for c in value if c.isdigit())
            if len(digits) == 10:
                return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"

        # SSN - return last 4 only
        if field_name == "employee_ssn":
            digits = "".join(c for c in value if c.isdigit())
            if len(digits) >= 4:
                return digits[-4:]

        # Clean address
        if "address" in field_name:
            value = re.sub(r"\bTexas\b", "TX", value, flags=re.IGNORECASE)

        # Clean name
        if "name" in field_name:
            value = re.sub(r"\d+\.\s*$", "", value)
            value = re.sub(r"\s+", " ", value)

        # DWC number
        if field_name == "dwc_number":
            value = re.sub(r"\s+", "", value)
            value = re.sub(r"-HW$", "", value)

        return value.strip() if value else None

    def _extract_location(self) -> None:
        """Extract exam location details."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._extract_location()")
        location_fields = ("exam_location", "exam_location_city", "exam_location_full")
        if all(field in self._vlm_set_fields for field in location_fields):
            self._extracted_fields_trace["location_fallback"].append(
                {"status": "skipped", "reason": "vlm_owned"}
            )
            return

        match = re.search(
            r"Location:\s*\|\s*(.+?)(?=Fax:)",
            self.full_text,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            location_str = match.group(1).strip().replace("\n", " ")

            # Facility name
            facility_match = re.match(r"([^,]+)", location_str)
            if facility_match:
                value = facility_match.group(1).strip()
                applied = self._set_patient_field("exam_location", value, source="regex_fallback")
                self._extracted_fields_trace["location_fallback"].append(
                    {
                        "field": "exam_location",
                        "value": value,
                        "status": "applied" if applied else "skipped",
                    }
                )

            # City
            city_match = re.search(
                r"\b([A-Za-z]+)\b(?=,\s*TX\s+\d{5})",
                location_str,
                re.IGNORECASE,
            )
            if city_match:
                value = city_match.group(1).strip().upper()
                applied = self._set_patient_field("exam_location_city", value, source="regex_fallback")
                self._extracted_fields_trace["location_fallback"].append(
                    {
                        "field": "exam_location_city",
                        "value": value,
                        "status": "applied" if applied else "skipped",
                    }
                )

            applied = self._set_patient_field("exam_location_full", location_str, source="regex_fallback")
            self._extracted_fields_trace["location_fallback"].append(
                {
                    "field": "exam_location_full",
                    "value": location_str,
                    "status": "applied" if applied else "skipped",
                }
            )

    def _analyze_checkboxes(self) -> None:
        """Analyze checkbox states using OpenCV."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._analyze_checkboxes()")
        if self._checkbox_analyzer is None:
            self._checkbox_analyzer = CheckboxAnalyzer(self.pdf_path)

        # Set page mappings using docling-extracted text
        self._checkbox_analyzer.set_page_mapping(self._page_texts)

        # Analyze all checkbox types
        results = self._checkbox_analyzer.analyze_all()

        # Update patient_info with network flags
        network = results.get("network", {})
        self._set_checkbox_fallback(
            "has_certified_network",
            network.get("has_certified_network", False),
            source="opencv_fallback",
        )
        self._set_checkbox_fallback(
            "has_political_subdivision",
            network.get("has_political_subdivision", False),
            source="opencv_fallback",
        )

        # Update body area flags
        body_areas = results.get("body_areas", {})
        for field, checked in body_areas.items():
            attr_name = f"body_area_{field}"
            if hasattr(self.patient_info, attr_name):
                self._set_checkbox_fallback(attr_name, checked, source="opencv_fallback")

        # Update purpose flags
        purpose = results.get("purpose", {})
        purpose_mapping = {
            "box_a": "purpose_box_a_checked",
            "box_b": "purpose_box_b_checked",
            "box_c": "purpose_box_c_checked",
            "box_d": "purpose_box_d_checked",
            "box_e": "purpose_box_e_checked",
            "box_f": "purpose_box_f_checked",
            "box_g": "purpose_box_g_checked",
            "dwc024_yes": "dwc024_yes_checked",
            "dwc024_no": "dwc024_no_checked",
        }
        for key, attr_name in purpose_mapping.items():
            if key in purpose:
                if (
                    self.config.part5_checkbox_assist
                    and (attr_name.startswith("purpose_box_") or attr_name.startswith("dwc024_"))
                    and attr_name in self._vlm_set_fields
                ):
                    current_value = bool(getattr(self.patient_info, attr_name, False))
                    opencv_value = bool(purpose[key])
                    if (not current_value) and opencv_value:
                        self._set_patient_field(
                            attr_name,
                            True,
                            source="opencv_override_part5",
                            force=True,
                        )
                        self._extracted_fields_trace["opencv_fallback"].append(
                            {
                                "field": attr_name,
                                "value": opencv_value,
                                "status": "applied",
                                "reason": "part5_assist_override",
                            }
                        )
                        continue
                self._set_checkbox_fallback(attr_name, purpose[key], source="opencv_fallback")

    def _set_hardcoded_values(self) -> None:
        """Set hardcoded values for designated doctor info."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._set_hardcoded_values()")
        # These are now filled from config
        if not self.patient_info.doctor_phone:
            self.patient_info.doctor_phone = self.config.doctor_phone
        if not self.patient_info.doctor_license_type:
            self.patient_info.doctor_license_type = self.config.doctor_license_type
        if not self.patient_info.doctor_license_jurisdiction:
            self.patient_info.doctor_license_jurisdiction = self.config.doctor_license_jurisdiction

    def _identify_dwc032_pages(self) -> dict[int, str]:
        """Identify DWC-032 pages and their types from already-extracted document.

        Uses the document extracted by _convert_with_docling() to find
        pages containing DWC-032 content and classify them by part.

        Page type classification:
        - "front_page": Contains validation markers (TDI header, DWC reference)
        - "DWC032_part1": Part 1. Injured employee information
        - "DWC032_part3": Part 3. Treating doctor information
        - "DWC032_part5": Part 5. Purpose of examination
        - "DWC032_part6": Part 6. Requester information

        Returns:
            Dict mapping 1-indexed page numbers to their DWC032 page type.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._identify_dwc032_pages()")
        if self._document is None:
            logger.warning("Document not extracted yet, cannot identify pages")
            return {}

        # Ensure _page_texts is populated
        if not self._page_texts:
            logger.debug("_page_texts is empty, extracting page texts now")
            self._page_texts = self._extract_page_texts(self._document)

        dwc032_pages: dict[int, str] = {}

        # Page type markers - order matters for matching
        page_type_markers = self.config.form32_page_type_markers

        # Front page and page two validation markers (tuples for immutability and slight performance gain)
        FRONT_PAGE_MARKERS = self.config.form32_front_page_markers
        EXAM_ORDER_PAGE_TWO_MARKERS = self.config.form32_exam_order_page_two_markers

        def _matches_all_markers(text: str, markers: tuple[str, ...]) -> bool:
            """Check if all markers are present in text.

            Uses early termination for better performance on non-matches.
            """
            return all(marker in text for marker in markers)

        logger.debug(f"Checking {len(self._page_texts)} pages for DWC-032 markers")
        for idx, page_text in enumerate(self._page_texts):
            page_num = idx + 1  # Convert to 1-indexed page number

            # Guard against empty page text
            if not page_text or not page_text.strip():
                logger.debug(f"Page {page_num}: Skipping empty page")
                continue

            text_lower = page_text.lower()
            text_upper = page_text.upper()

            # Check if this is a DWC-032 form page
            is_dwc032 = "DWC032" in text_upper or "DWC 032" in text_upper

            if is_dwc032:
                # Classify DWC-032 page by specific part markers
                logger.debug(f"Page {page_num}: Classifying DWC-032 page type ({len(page_text)} chars)")
                page_type = "dwc032"  # Default to generic DWC032 page
                for ptype, marker in page_type_markers.items():
                    if marker in text_lower:
                        page_type = ptype
                        logger.debug(f"Page {page_num}: Classified as {ptype}")
                        break
                dwc032_pages[page_num] = page_type

            elif _matches_all_markers(text_lower, EXAM_ORDER_PAGE_TWO_MARKERS):
                # Check for exam order page two (higher priority than front_page)
                page_type = "exam_order_page_two"
                logger.debug(f"Page {page_num}: Classified as {page_type}")
                dwc032_pages[page_num] = page_type

            elif _matches_all_markers(text_lower, FRONT_PAGE_MARKERS):
                # Check for front page (commissioner's order cover letter)
                page_type = "front_page"
                logger.debug(f"Page {page_num}: Classified as {page_type}")
                dwc032_pages[page_num] = page_type
            else:
                logger.debug(f"Page {page_num} not classified.")

            # else: Not a DWC-032 page, front page, or exam order page - skip

        logger.info(f"Identified {len(dwc032_pages)} DWC-032 pages: {dwc032_pages}")
        return dwc032_pages

    def _extract_with_vlm(self) -> bool:
        """Extract fields using VLM-based DocumentExtractor with page-specific templates.

        Uses templates from form32_templates matching each identified page type
        for more accurate extraction.

        Returns:
            True if extraction succeeded.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor._extract_with_vlm()")
        try:
            # First, identify which pages are DWC-032 and their types
            dwc032_pages = self._identify_dwc032_pages()
            if dwc032_pages:
                logger.info(f"Will extract VLM from DWC-032 pages: {dwc032_pages}")
            else:
                logger.info("No DWC-032 pages identified, cannot extract with VLM")
                return False

            logger.info("Using VLM-based DocumentExtractor with page-specific templates")
            extractor = Form32Extractor(
                verbose=self.verbose,
                use_part5_checkbox_assist=self.config.part5_checkbox_assist,
            )

            # Use template-based extraction for each page type
            template_fields = extractor.extract_with_templates(self.pdf_path, dwc032_pages)
            self._extracted_fields_trace["vlm_raw"] = dict(template_fields)

            # Map template-extracted fields to PatientInfo using FIELD_TO_ATTRIBUTE_MAP
            self._map_template_fields_to_patient_info(template_fields)

            return True
        except (RuntimeError, OSError, ValueError, TypeError) as e:
            logger.error(f"VLM extraction failed: {e}")
            self.validation_errors.append(f"VLM extraction failed: {e}")
            return False

    def _map_template_fields_to_patient_info(self, fields: dict[str, Any]) -> None:
        """Map template-extracted fields to PatientInfo using FIELD_TO_ATTRIBUTE_MAP.

        Args:
            fields: Dict of extracted fields from template-based extraction.
                   Keys are template field labels (e.g. "1. Employee's name").
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER _map_template_fields_to_patient_info()")
        logger.info(f"Mapping {len(fields)} template fields to PatientInfo")

        mapped_count = 0
        for field_label, value in fields.items():
            if value is None or value == "":
                continue

            # Look up the PatientInfo attribute name
            attr_name = FIELD_TO_ATTRIBUTE_MAP.get(field_label)
            if not attr_name:
                logger.debug(f"No mapping for field: {field_label}")
                continue

            # Special handling for boolean-like fields from VLM checkbox enums.
            bool_like_fields = (
                attr_name.endswith("_checked")
                or attr_name.startswith("body_area_")
                or attr_name in {"has_certified_network", "has_political_subdivision"}
            )
            if bool_like_fields:
                if isinstance(value, str):
                    value = value.lower() in {
                        "selected",
                        "checked",
                        "yes",
                        "true",
                        "checkbox filled",
                        "filled",
                    }
                elif isinstance(value, list):
                    normalized = [v.lower() for v in value if isinstance(v, str)]
                    value = any(
                        v in {"selected", "checked", "yes", "true", "checkbox filled", "filled"}
                        for v in normalized
                    )

            # Set the attribute if it exists on PatientInfo
            if hasattr(self.patient_info, attr_name):
                self._set_patient_field(attr_name, value, source="vlm", force=True)
                self._vlm_set_fields.add(attr_name)
                self._extracted_fields_trace["vlm_mapped"].append(
                    {"label": field_label, "attribute": attr_name, "value": value}
                )
                logger.debug(f"Mapped: {field_label} -> {attr_name} = {value}")
                mapped_count += 1
            else:
                logger.warning(f"PatientInfo has no attribute: {attr_name}")

        logger.info(f"Mapped {mapped_count} fields to PatientInfo")

    def _is_missing_or_invalid(self, field_name: str, value: Any) -> bool:
        """Check if a field value is effectively missing or invalid."""
        if value is None:
            return True
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return True
            if stripped in {"|", "||", "|||"}:
                return True
            if field_name.endswith("_name") and stripped.replace("|", "").strip() == "":
                return True
        return False

    def _set_patient_field(
        self,
        field_name: str,
        value: Any,
        *,
        source: str,
        force: bool = False,
    ) -> bool:
        """Set a PatientInfo field with source tracking and fallback guards."""
        if not hasattr(self.patient_info, field_name):
            return False
        current = getattr(self.patient_info, field_name)
        if not force and not self._is_missing_or_invalid(field_name, current):
            return False
        setattr(self.patient_info, field_name, value)
        self._field_sources[field_name] = source
        return True

    def _set_checkbox_fallback(self, field_name: str, value: bool, *, source: str) -> bool:
        """Set checkbox field only if VLM did not already set it."""
        if field_name in self._vlm_set_fields:
            self._extracted_fields_trace["opencv_fallback"].append(
                {"field": field_name, "value": value, "status": "skipped", "reason": "vlm_owned"}
            )
            return False
        applied = self._set_patient_field(field_name, value, source=source, force=True)
        self._extracted_fields_trace["opencv_fallback"].append(
            {"field": field_name, "value": value, "status": "applied" if applied else "skipped"}
        )
        return applied

    def create_patient_directory(self) -> Path:
        """Create output directory for patient files.

        Returns:
            Path to created directory.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.create_patient_directory()")
        patient_dir = self.config.get_patient_dir(
            self.patient_info.exam_date or "Date",
            self.patient_info.patient_name or "Patient",
            self.patient_info.exam_location_city or "City",
        )
        patient_dir.mkdir(parents=True, exist_ok=True)
        return patient_dir

    def copy_form32(self, patient_dir: Path) -> Path:
        """Copy Form32 PDF to patient directory.

        Args:
            patient_dir: Destination directory.

        Returns:
            Path to copied file.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.copy_form32(patient_dir={patient_dir})")
        safe_name = (self.patient_info.patient_name or "UNKNOWN").replace("/", "_")
        new_filename = f"FORM32 {safe_name}.pdf"
        dest_path = patient_dir / new_filename
        shutil.copy2(self.pdf_path, dest_path)
        return dest_path

    def save_docling_document(self, patient_dir: Path) -> Path | None:
        """Save the raw docling document as JSON for debugging/analysis.

        Only called when config.output_docling_document is True.

        Args:
            patient_dir: Destination directory for the JSON file.

        Returns:
            Path to the saved JSON file, or None if document not available.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.save_docling_document(patient_dir={patient_dir})")
        if self._document is None:
            logger.warning("No docling document available to save")
            return None

        output_path = patient_dir / "docling_document.json"
        try:
            self._document.save_as_json(output_path)
            logger.info(f"Saved docling document to: {output_path}")
            return output_path
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            logger.error(f"Failed to save docling document: {e}")
            return None

    def save_docling_markdown(self, patient_dir: Path) -> Path | None:
        """Save the docling document as Markdown for review.

        Only called when config.output_docling_markdown is True.

        Args:
            patient_dir: Destination directory for the Markdown file.

        Returns:
            Path to the saved Markdown file, or None if document not available.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.save_docling_markdown(patient_dir={patient_dir})")
        if self._document is None:
            logger.warning("No docling document available to save as markdown")
            return None

        output_path = patient_dir / "docling_document.md"
        try:
            markdown_content = self._document.export_to_markdown()
            output_path.write_text(markdown_content, encoding="utf-8")
            logger.info(f"Saved docling markdown to: {output_path}")
            return output_path
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            logger.error(f"Failed to save docling markdown: {e}")
            return None

    def save_form32_json(self, patient_dir: Path) -> Path | None:
        """Save the structured Form32Data as JSON.

        Only called when config.output_form32_json is True.

        Args:
            patient_dir: Destination directory for the JSON file.

        Returns:
            Path to the saved JSON file, or None if saving failed.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.save_form32_json(patient_dir={patient_dir})")
        try:
            form32_data = Form32Data.from_patient_info(self.patient_info)
            output_path = patient_dir / "form32_data.json"

            # Use pydantic's model_dump_json for pretty printing
            json_content = form32_data.model_dump_json(indent=4)
            output_path.write_text(json_content, encoding="utf-8")

            logger.info(f"Saved Form32 structured data to: {output_path}")
            return output_path
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            logger.error(f"Failed to save Form32 JSON: {e}")
            return None

    def save_extracted_fields_json(self, patient_dir: Path) -> Path | None:
        """Save extraction provenance for VLM/regex/OpenCV field sourcing."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.save_extracted_fields_json(patient_dir={patient_dir})")
        try:
            final_sources: dict[str, str] = {}
            for field_name, value in self.patient_info.model_dump().items():
                if field_name in self._field_sources:
                    final_sources[field_name] = self._field_sources[field_name]
                elif self._is_missing_or_invalid(field_name, value):
                    final_sources[field_name] = "default"
                else:
                    final_sources[field_name] = "default"

            payload = dict(self._extracted_fields_trace)
            payload["final_sources"] = final_sources

            output_path = patient_dir / "extracted_fields.json"
            output_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
            logger.info(f"Saved extraction provenance to: {output_path}")
            return output_path
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            logger.error(f"Failed to save extracted fields JSON: {e}")
            return None

    def process(self) -> dict[str, Any]:
        """Process Form 32 and generate output forms.

        Returns:
            Dictionary with processing results including success flag,
            patient_info, generated forms, and output directory.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Processor.process()")
        process_start = perf_counter()
        try:
            # Extract text with docling (needed for validation and fallback)
            convert_start = perf_counter()
            if not self._convert_with_docling():
                self._log_phase_timing(
                    "convert",
                    perf_counter() - convert_start,
                    self.config.phase_budget_convert_seconds,
                )
                return {"success": False, "errors": self.validation_errors}
            self._log_phase_timing(
                "convert",
                perf_counter() - convert_start,
                self.config.phase_budget_convert_seconds,
            )

            # Validate and classify form
            if not self.validate_form():
                return {"success": False, "errors": self.validation_errors}

            # Extract patient information. Always use VLM extraction model.
            extraction_start = perf_counter()
            logger.info("Using VLM-based extraction")
            if not self._extract_with_vlm():
                logger.warning("VLM extraction failed")
            # Run regex and location extraction as fallback-only completion.
            self._extract_with_patterns()
            self._extract_location()
            self._log_phase_timing(
                "extraction",
                perf_counter() - extraction_start,
                self.config.phase_budget_extraction_seconds,
            )

            # Analyze checkboxes (OpenCV fallback for fields VLM did not set)
            checkbox_start = perf_counter()
            self._analyze_checkboxes()
            self._log_phase_timing(
                "checkbox",
                perf_counter() - checkbox_start,
                self.config.phase_budget_checkbox_seconds,
            )

            # Set hardcoded values
            self._set_hardcoded_values()

            # Validate required fields
            if not self.patient_info.is_valid():
                logger.warning("Missing required patient information (Record will still be created)")
                self.validation_errors.append("Missing required patient information (Saved for manual correction)")
                # No longer returning early here

            # Create output directory and copy Form32
            patient_dir = self.create_patient_directory()
            form32_path = self.copy_form32(patient_dir)

            # Generate additional forms
            generated_forms: list[str] = []
            try:
                controller = FormGenerationController(
                    self.patient_info,
                    verbose=self.verbose,
                )
                controller.output_directory = patient_dir
                generated_forms = controller.generate_forms()
            except (RuntimeError, OSError, ValueError, TypeError) as e:
                logger.error(f"Error generating forms: {e}")

            # Save docling document if verbose output is enabled
            docling_document_path: str | None = None
            docling_markdown_path: str | None = None

            if self.config.output_docling_document:
                saved_path = self.save_docling_document(patient_dir)
                if saved_path:
                    docling_document_path = str(saved_path)

            if self.config.output_docling_markdown:
                saved_md_path = self.save_docling_markdown(patient_dir)
                if saved_md_path:
                    docling_markdown_path = str(saved_md_path)

            # Save Form32 JSON if enabled
            form32_json_path: str | None = None
            if self.config.output_form32_json:
                saved_json_path = self.save_form32_json(patient_dir)
                if saved_json_path:
                    form32_json_path = str(saved_json_path)

            extracted_fields_path: str | None = None
            if self.verbose:
                saved_extracted_path = self.save_extracted_fields_json(patient_dir)
                if saved_extracted_path:
                    extracted_fields_path = str(saved_extracted_path)

            return {
                "success": True,
                "patient_info": self.patient_info,
                "output_directory": str(patient_dir),
                "form32_path": str(form32_path),
                "generated_forms": generated_forms,
                "docling_document_path": docling_document_path,
                "docling_markdown_path": docling_markdown_path,
                "form32_json_path": form32_json_path,
                "extracted_fields_path": extracted_fields_path,
            }

        except Exception as e:
            logger.exception(f"Processing failed: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            self._log_phase_timing(
                "total",
                perf_counter() - process_start,
                self.config.phase_budget_total_seconds,
            )
