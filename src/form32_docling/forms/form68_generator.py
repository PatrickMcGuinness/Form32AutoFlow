"""Form 68 (DWC-068) generation from patient information."""

import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from form32_docling.config import Config
from form32_docling.models import PatientInfo

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

    def _map_patient_info_to_fields(self, patient_info: PatientInfo) -> dict[str, str]:
        """Map PatientInfo attributes to Form 68 field names.

        Args:
            patient_info: Source patient data.

        Returns:
            Dictionary mapping PDF field names to values.
        """
        fields = {
            # Patient Info
            "patient_name": patient_info.patient_name or "",
            "patient_ssn": patient_info.ssn or "",
            "date_of_injury": patient_info.date_of_injury or "",
            "claim_number": patient_info.claim_number or "",

            # Exam info
            "exam_date": patient_info.exam_date or "",
            "exam_location": patient_info.exam_location or "",

            # Carrier info
            "insurance_carrier": patient_info.insurance_carrier or "",

            # Treating doctor info
            "treating_doctor_name": patient_info.treating_doctor_name or "",
            "treating_doctor_addr": patient_info.treating_doctor_address or "",
            "treating_doctor_phone": patient_info.treating_doctor_phone or "",
        }

        # Handle injury evaluations (Page 2)
        # We handle up to 4 evaluations as per form structure
        for i, evaluation in enumerate(patient_info.injury_evaluations[:4]):
            idx = i + 1
            fields[f"condition_{idx}"] = evaluation.condition_text or ""

            # Radio buttons / checkboxes for substantial factor
            if evaluation.is_substantial_factor is True:
                fields[f"factor_yes_{idx}"] = "/Yes"
            elif evaluation.is_substantial_factor is False:
                fields[f"factor_no_{idx}"] = "/Yes"

            # Diagnosis codes
            for c_idx, code in enumerate(evaluation.diagnosis_codes[:4]):
                fields[f"icd_{idx}_{c_idx+1}"] = code or ""

        return fields

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
        writer = PdfWriter()

        # Clone entire document structure (including AcroForm)
        writer.clone_document_from_reader(reader)

        # Fill fields
        field_values = self._map_patient_info_to_fields(patient_info)

        # update_page_form_field_values works on the writer's internal AcroForm
        writer.update_page_form_field_values(writer.pages[0], field_values)
        if len(writer.pages) > 1:
            writer.update_page_form_field_values(writer.pages[1], field_values)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"Form68 generated: {output_path}")
        return output_path
