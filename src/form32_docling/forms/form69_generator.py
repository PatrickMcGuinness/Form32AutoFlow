"""DWC Form-069 generator (Report of Medical Evaluation)."""

import logging
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from form32_docling.config import Config
from form32_docling.models import PatientInfo

from .form_mappings import map_form69_fields
from .pdf_form_utils import (
    apply_field_values,
    clone_template_to_writer,
    extract_encryption_profile,
    normalize_for_acrobat,
    reencrypt_writer_if_needed,
)

logger = logging.getLogger(__name__)


class Form69Generator:
    """Generates DWC Form-069 by filling interactive form fields."""

    def __init__(
        self,
        config: Config | None = None,
        *,
        verbose: bool = False,
    ) -> None:
        """Initialize generator.

        Args:
            config: Configuration instance.
            verbose: Enable verbose logging.
        """
        self.config = config or Config()
        self.verbose = verbose
        self.template_path = self.config.form69_template
        self.output_directory: Path | None = None
        self.font_name = "Helvetica-Bold"
        self.font_size = 8

    def _map_patient_info_to_fields(self, info: PatientInfo) -> dict[str, Any]:
        """Map PatientInfo attributes to Form 69 field names.

        Args:
            info: Patient information.

        Returns:
            Dictionary mapping field names to values.
        """
        return map_form69_fields(info)

    def generate(self, patient_info: PatientInfo) -> Path:
        """Generate Form-069 PDF by filling form fields.

        Args:
            patient_info: Patient data for the form.

        Returns:
            Path to generated PDF file.

        Raises:
            FileNotFoundError: If template is not found.
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        if self.output_directory:
            patient_dir = Path(self.output_directory)
        else:
            patient_dir = self.config.get_patient_dir(
                patient_info.exam_date or "",
                patient_info.patient_name or "",
                patient_info.exam_location_city,
            )

        patient_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.config.get_form_path(
            patient_dir, "DWC069", patient_info.patient_name or "UNKNOWN"
        )

        reader = PdfReader(str(self.template_path))
        encryption_profile = extract_encryption_profile(reader)
        writer = clone_template_to_writer(reader)

        field_values = self._map_patient_info_to_fields(patient_info)
        apply_field_values(writer, field_values, page_spec=0, auto_regenerate=None)
        normalize_for_acrobat(writer)
        reencrypt_writer_if_needed(writer, encryption_profile)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"Form69 generated: {output_path}")
        return output_path
