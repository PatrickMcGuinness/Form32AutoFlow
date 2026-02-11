"""Docling DocumentExtractor-based extraction for Form32.

This module uses Docling's VLM-powered DocumentExtractor to extract
structured data from DWC-032 forms into Pydantic models.

Note: The DocumentExtractor API is currently in beta and may change.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from docling.datamodel.base_models import InputFormat
from docling.document_extractor import DocumentExtractor
from pydantic import BaseModel, Field

from form32_docling.config.form32_templates import (
    DWC032_part1_template,
    DWC032_part3_template,
    DWC032_part5_checkbox_assist_template,
    DWC032_part5_template,
    DWC032_part6_template,
    exam_order_page_two_template,
    front_page_template,
)

logger = logging.getLogger(__name__)

# Map page types from _identify_dwc032_pages() to extraction templates
TEMPLATE_MAP: dict[str, dict[str, Any]] = {
    "front_page": front_page_template,
    "DWC032_part1": DWC032_part1_template,
    "DWC032_part3": DWC032_part3_template,
    "DWC032_part5": DWC032_part5_template,
    "DWC032_part6": DWC032_part6_template,
    "exam_order_page_two": exam_order_page_two_template,
}


class Form32TextFields(BaseModel):
    """Text-only fields for VLM extraction from DWC-032 forms.

    This model is used as the template for DocumentExtractor.
    Boolean checkbox fields are handled separately via OpenCV.

    Fields are organized by DWC-032 form sections with descriptive
    examples to guide the VLM extraction process.
    """

    # Part 1: Injured Employee Information (Fields 1-15)
    employee_name: str | None = Field(
        default=None,
        description="Injured employee's full name from Field 1",
        examples=["John Smith", "Maria Garcia", "James O'Brien"],
    )
    employee_ssn_last4: str | None = Field(
        default=None,
        description="Last 4 digits of SSN shown after XXX-XX- in Field 2",
        examples=["1234", "5678", "9012"],
    )
    employee_dob: str | None = Field(
        default=None,
        description="Employee's date of birth from Field 2 in MM/DD/YYYY format",
        examples=["01/15/1985", "12/03/1972", "06/22/1990"],
    )
    employee_address: str | None = Field(
        default=None,
        description="Employee's complete street address from Field 3",
        examples=["123 Main St, Dallas, TX 75201", "456 Oak Ave, Austin, TX 78701"],
    )
    employee_county: str | None = Field(
        default=None,
        description="Employee's county from Field 4",
        examples=["Dallas County", "Travis County", "Harris County"],
    )
    employee_primary_phone: str | None = Field(
        default=None,
        description="Employee's primary phone number from Field 5",
        examples=["(214) 555-1234", "512-555-6789", "713.555.4321"],
    )
    employee_alternate_phone: str | None = Field(
        default=None,
        description="Employee's alternate phone number from Field 6",
        examples=["(214) 555-9876", "512-555-1111"],
    )
    date_of_injury: str | None = Field(
        default=None,
        description="Date of injury from Field 8 in MM/DD/YYYY format",
        examples=["03/15/2024", "11/22/2023", "07/04/2024"],
    )
    representative_name: str | None = Field(
        default=None,
        description="Employee representative's name from Field 9",
        examples=["Jane Attorney", "Smith & Associates"],
    )
    representative_phone: str | None = Field(
        default=None,
        description="Representative's phone number from Field 10",
        examples=["(214) 555-0000", "512-555-1111"],
    )
    representative_email: str | None = Field(
        default=None,
        description="Representative's email address from Field 11",
        examples=["attorney@lawfirm.com", "rep@legal.com"],
    )
    representative_fax: str | None = Field(
        default=None,
        description="Representative's fax number from Field 12",
        examples=["(214) 555-0001", "512-555-1112"],
    )
    employer_name: str | None = Field(
        default=None,
        description="Employer's name from Field 13",
        examples=["ABC Construction LLC", "City of Dallas", "Texas Health Resources"],
    )
    employer_phone: str | None = Field(
        default=None,
        description="Employer's phone number from Field 14",
        examples=["(214) 555-2222", "512-555-3333"],
    )
    employer_address: str | None = Field(
        default=None,
        description="Employer's address from Field 15",
        examples=["789 Business Pkwy, Dallas, TX 75201"],
    )

    # Part 2: Insurance Carrier Information (Fields 16-23)
    insurance_carrier: str | None = Field(
        default=None,
        description="Insurance carrier name from Field 16",
        examples=["Texas Mutual Insurance", "CompSource Mutual", "Hartford"],
    )
    carrier_address: str | None = Field(
        default=None,
        description="Insurance carrier address from Field 17",
        examples=["P.O. Box 12345, Austin, TX 78701"],
    )
    adjuster_name: str | None = Field(
        default=None,
        description="Claims adjuster's name from Field 18",
        examples=["Bob Johnson", "Sarah Williams"],
    )
    adjuster_phone: str | None = Field(
        default=None,
        description="Adjuster's phone number from Field 19",
        examples=["(800) 555-1234", "512-555-4444"],
    )
    adjuster_email: str | None = Field(
        default=None,
        description="Adjuster's email address from Field 20",
        examples=["bjohnson@insurance.com", "claims@carrier.com"],
    )
    adjuster_fax: str | None = Field(
        default=None,
        description="Adjuster's fax number from Field 21",
        examples=["(800) 555-1235", "512-555-4445"],
    )
    claim_number: str | None = Field(
        default=None,
        description="Insurance carrier claim number",
        examples=["CLM-2024-123456", "WC123456789", "2024-001234"],
    )
    dwc_number: str | None = Field(
        default=None,
        description="DWC claim number",
        examples=["123456789-TDI", "987654321"],
    )
    health_plan_name: str | None = Field(
        default=None,
        description="Health plan name if applicable from Field 23",
        examples=["BCBS Texas", "Aetna PPO"],
    )

    # Part 3: Treating Doctor Information (Fields 24-28)
    treating_doctor_name: str | None = Field(
        default=None,
        description="Treating doctor's full name from Field 24",
        examples=["Dr. Robert Smith, MD", "Jane Doe, D.O.", "Michael Brown, DC"],
    )
    treating_doctor_phone: str | None = Field(
        default=None,
        description="Treating doctor's phone number from Field 25",
        examples=["(214) 555-7777", "512-555-8888"],
    )
    treating_doctor_fax: str | None = Field(
        default=None,
        description="Treating doctor's fax number from Field 26",
        examples=["(214) 555-7778", "512-555-8889"],
    )
    treating_doctor_address: str | None = Field(
        default=None,
        description="Treating doctor's address from Field 27",
        examples=["100 Medical Plaza, Dallas, TX 75201"],
    )
    treating_doctor_license: str | None = Field(
        default=None,
        description="Treating doctor's license number from Field 28",
        examples=["MD12345", "DC54321", "DO98765"],
    )

    # Examination Information (From scheduling section)
    exam_date: str | None = Field(
        default=None,
        description="Scheduled examination date in MM/DD/YYYY format",
        examples=["02/15/2024", "03/22/2024", "04/10/2024"],
    )
    exam_time: str | None = Field(
        default=None,
        description="Scheduled examination time",
        examples=["10:00 AM", "2:30 PM", "9:00 AM"],
    )
    exam_location: str | None = Field(
        default=None,
        description="Examination facility or clinic name",
        examples=["Dallas Medical Center", "Austin Health Clinic", "Houston Spine Institute"],
    )
    exam_location_address: str | None = Field(
        default=None,
        description="Full address of examination location",
        examples=["1234 Healthcare Blvd, Dallas, TX 75201"],
    )
    exam_location_city: str | None = Field(
        default=None,
        description="City where examination will be held",
        examples=["Dallas", "Austin", "Houston", "San Antonio"],
    )

    # Designated Doctor Information
    designated_doctor_name: str | None = Field(
        default=None,
        description="Designated doctor's full name",
        examples=["Dr. Michael Lee, DC", "William Chen, MD"],
    )
    designated_doctor_phone: str | None = Field(
        default=None,
        description="Designated doctor's phone number",
        examples=["(512) 555-9999", "214-555-0000"],
    )
    designated_doctor_fax: str | None = Field(
        default=None,
        description="Designated doctor's fax number",
        examples=["(512) 555-9998"],
    )
    designated_doctor_address: str | None = Field(
        default=None,
        description="Designated doctor's address",
        examples=["200 Doctor Way, Austin, TX 78701"],
    )
    designated_doctor_license: str | None = Field(
        default=None,
        description="Designated doctor's license number",
        examples=["DC12345", "MD67890"],
    )

    # Extent of Injury
    extent_of_injury: str | None = Field(
        default=None,
        description="Description of the extent of injury from Field 30",
        examples=["Low back pain, lumbar strain", "Cervical disc herniation C5-C6"],
    )


class Form32Extractor:
    """Extract Form32 data using Docling's DocumentExtractor.

    Uses VLM-based extraction to populate Form32TextFields from DWC-032 PDFs.
    This extractor handles text fields only; checkbox/boolean fields are
    handled separately via OpenCV analysis.
    """

    def __init__(
        self,
        *,
        verbose: bool = False,
        use_gpu: bool = True,
        use_part5_checkbox_assist: bool = False,
    ) -> None:
        """Initialize the extractor.

        Args:
            verbose: Enable verbose logging.
            use_gpu: Enable GPU acceleration (default: True).
            use_part5_checkbox_assist: Use enhanced Part 5 checkbox template.
        """
        logger.debug(
            f"[{datetime.now().isoformat()}] ENTER Form32Extractor.__init__(verbose={verbose}, use_gpu={use_gpu}, use_part5_checkbox_assist={use_part5_checkbox_assist})"
        )
        import os

        self.verbose = verbose
        self.use_gpu = use_gpu
        self.use_part5_checkbox_assist = use_part5_checkbox_assist
        self._extractor: DocumentExtractor | None = None

        # Set environment variable for GPU acceleration
        # This is the recommended way to configure Docling device
        if use_gpu:
            os.environ.setdefault("DOCLING_DEVICE", "cuda")
            os.environ.setdefault("DOCLING_NUM_THREADS", "8")
            logger.info("Set DOCLING_DEVICE=cuda for GPU acceleration")

    @property
    def extractor(self) -> DocumentExtractor:
        """Lazy-load the DocumentExtractor."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Extractor.extractor property")
        if self._extractor is None:
            logger.info("Initializing Docling DocumentExtractor")
            self._extractor = DocumentExtractor(
                allowed_formats=[InputFormat.PDF, InputFormat.IMAGE]
            )
        return self._extractor

    def extract(
        self, pdf_path: str | Path, *, page_numbers: list[int] | None = None
    ) -> Form32TextFields:
        """Extract text fields from a DWC-032 form.

        Args:
            pdf_path: Path to the PDF file.
            page_numbers: Optional list of specific page numbers to extract.
                         If provided, only those pages are processed.
                         If None or empty, all pages are processed.

        Returns:
            Form32TextFields with extracted data (text fields only).

        Raises:
            Exception: If extraction fails.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Extractor.extract(pdf_path={pdf_path}, page_numbers={page_numbers})")
        # Log extraction scope
        if page_numbers:
            logger.info(f"Extracting pages {page_numbers} with VLM: {pdf_path}")
        else:
            logger.info(f"Extracting all pages with VLM: {pdf_path}")

        # Build extraction kwargs
        extract_kwargs: dict[str, Any] = {
            "source": str(pdf_path),
            "template": Form32TextFields,
        }

        # Add page_range if specific pages requested
        # Docling page_range is [start, end] inclusive
        if page_numbers:
            page_range = (min(page_numbers), max(page_numbers))
            extract_kwargs["page_range"] = page_range
            logger.info(f"Using page_range: {page_range}")

        # Time the VLM extraction (typically the slowest step)
        extract_start = datetime.now()
        logger.debug(f"[{extract_start.isoformat()}] DOCLING_VLM_EXTRACT_START")

        result = self.extractor.extract(**extract_kwargs)

        extract_end = datetime.now()
        extract_elapsed = (extract_end - extract_start).total_seconds()
        logger.info(f"[{extract_end.isoformat()}] DOCLING_VLM_EXTRACT_END - elapsed: {extract_elapsed:.2f}s")

        # Time the aggregation step
        agg_start = datetime.now()
        aggregated = self._aggregate_page_results(result.pages)
        agg_elapsed = (datetime.now() - agg_start).total_seconds()
        logger.debug(f"DOCLING_VLM_AGGREGATE - elapsed: {agg_elapsed:.2f}s")

        if self.verbose:
            logger.debug(f"Aggregated extraction result: {aggregated}")

        return Form32TextFields.model_validate(aggregated)

    def _aggregate_page_results(self, pages: list[Any]) -> dict[str, Any]:
        """Aggregate extracted data from multiple pages.

        DWC-032 is typically 3 pages. Each page may contain different
        sections of the form. This method merges non-null values from
        all pages into a single result.

        Args:
            pages: List of ExtractedPageData from DocumentExtractor.

        Returns:
            Merged dictionary of extracted fields.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Extractor._aggregate_page_results(pages_count={len(pages)})")
        merged: dict[str, Any] = {}

        for page in pages:
            page_data = page.extracted_data if hasattr(page, "extracted_data") else {}
            if page_data:
                logger.debug(f"Page {page.page_no}: extracted {len(page_data)} fields")
                for key, value in page_data.items():
                    # Prefer non-null, non-empty values; first valid wins
                    if value is not None and value != "":
                        if merged.get(key) is None or merged.get(key) == "":
                            merged[key] = value
                        # For nested dicts, merge recursively
                        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                            merged[key] = self._merge_dicts(merged[key], value)

        logger.info(f"Aggregated {len(merged)} fields from {len(pages)} pages")
        return merged

    def _merge_dicts(
        self, base: dict[str, Any], update: dict[str, Any]
    ) -> dict[str, Any]:
        """Recursively merge dictionaries, preferring non-null values."""
        logger.debug(f"[{datetime.now().isoformat()}] ENTER Form32Extractor._merge_dicts()")
        result = base.copy()
        for key, value in update.items():
            if value is not None and value != "":
                if key not in result or result[key] is None or result[key] == "":
                    result[key] = value
                elif isinstance(value, dict) and isinstance(result.get(key), dict):
                    result[key] = self._merge_dicts(result[key], value)
        return result

    def extract_with_templates(
        self,
        pdf_path: str | Path,
        page_type_map: dict[int, str],
    ) -> dict[str, Any]:
        """Extract using page-specific templates.

        For each page identified in page_type_map, uses the corresponding
        template from TEMPLATE_MAP to extract structured data.

        Args:
            pdf_path: Path to the PDF file.
            page_type_map: Dict from _identify_dwc032_pages() mapping
                          page numbers to page types, e.g.
                          {8: 'DWC032_part1', 9: 'DWC032_part3'}

        Returns:
            Merged dict of all extracted fields from all pages.
        """
        logger.debug(f"[{datetime.now().isoformat()}] ENTER extract_with_templates()")
        logger.info(f"Extracting with templates from {len(page_type_map)} pages: {page_type_map}")

        merged_results: dict[str, Any] = {}

        for page_num, page_type in page_type_map.items():
            # Skip page types without templates
            if page_type not in TEMPLATE_MAP:
                logger.debug(f"Page {page_num} ({page_type}): No template, skipping")
                continue

            template = TEMPLATE_MAP[page_type]
            if page_type == "DWC032_part5" and self.use_part5_checkbox_assist:
                template = DWC032_part5_checkbox_assist_template
            logger.info(f"Page {page_num} ({page_type}): Using template with {len(template.get('Parts', {}))} parts")

            try:
                extract_start = datetime.now()
                result = self.extractor.extract(
                    source=str(pdf_path),
                    template=template,
                    page_range=(page_num, page_num),  # Single page
                )
                extract_elapsed = (datetime.now() - extract_start).total_seconds()
                logger.debug(f"Page {page_num}: Extraction took {extract_elapsed:.2f}s")

                # Process extracted data from this page
                for page in result.pages:
                    page_data = page.extracted_data if hasattr(page, "extracted_data") else {}
                    if page_data:
                        logger.info(f"Page {page_num} ({page_type}): Extracted {len(page_data)} fields")
                        # Log each extracted field for debugging
                        for key, value in page_data.items():
                            if value is not None and value != "":
                                logger.debug(f"  {key}: {value}")
                        # Merge into results
                        merged_results = self._merge_dicts(merged_results, page_data)
                    else:
                        logger.warning(f"Page {page_num} ({page_type}): No data extracted")

            except (RuntimeError, OSError, ValueError, TypeError) as e:
                logger.error(f"Page {page_num} ({page_type}): Extraction failed: {e}")
                continue

        logger.info(f"Template extraction complete: {len(merged_results)} total fields")
        return merged_results
