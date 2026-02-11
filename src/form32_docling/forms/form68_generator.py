"""Form 68 (DWC-068) generation from patient information."""

import logging
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from form32_docling.config import Config
from form32_docling.models import PatientInfo

from .form_mappings import map_form68_fields
from .pdf_form_utils import (
    apply_field_values,
    clone_template_to_writer,
    extract_encryption_profile,
    normalize_for_acrobat,
    reencrypt_writer_if_needed,
)

logger = logging.getLogger(__name__)


class Form68Generator:
    """Generates DWC-068 PDF from processed PatientInfo."""

    def __init__(self, config: Config, *, verbose: bool = False) -> None:
        """Initialize generator.

        Args:
            config: Application configuration.
            verbose: Enable verbose logging.
        """
        self.config = config
        self.verbose = verbose
        self.template_path = self.config.form68_template
        self.output_directory: Path | None = None
        self.font_name = "Helvetica-Bold"
        self.font_size = 12

    def _map_patient_info_to_fields(self, patient_info: PatientInfo) -> dict[str, Any]:
        """Map PatientInfo attributes to Form 68 field names.

        Args:
            patient_info: Source patient data.

        Returns:
            Dictionary mapping PDF field names to values.
        """
        return map_form68_fields(patient_info)

    def generate(self, patient_info: PatientInfo) -> Path:
        """Generate Form 68 PDF.

        Args:
            patient_info: Patient data for the form.

        Returns:
            Path to the generated PDF.
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        if not self.output_directory:
            patient_dir = self.config.get_patient_dir(
                patient_info.exam_date or "",
                patient_info.patient_name or "",
                patient_info.exam_location_city,
            )
        else:
            patient_dir = self.output_directory

        patient_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.config.get_form_path(
            patient_dir, "DWC068", patient_info.patient_name or "UNKNOWN"
        )

        reader = PdfReader(str(self.template_path))
        encryption_profile = extract_encryption_profile(reader)
        writer = clone_template_to_writer(reader)

        # Fill fields
        field_values = self._map_patient_info_to_fields(patient_info)
        apply_field_values(writer, field_values, page_spec=None, auto_regenerate=None)
        normalize_for_acrobat(writer)
        reencrypt_writer_if_needed(writer, encryption_profile)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"Form68 generated: {output_path}")
        return output_path
