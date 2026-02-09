"""DWC Form-069 generator (Report of Medical Evaluation)."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter

from form32_docling.config import Config
from form32_docling.models import PatientInfo

logger = logging.getLogger(__name__)


def _format_ssn_masked(ssn: str | None) -> str:
    """Format SSN to show only last 4 digits."""
    if not ssn:
        return ""
    digits = "".join(c for c in str(ssn) if c.isdigit())
    if len(digits) == 9:
        return f"XXX-XX-{digits[-4:]}"
    if len(digits) == 4:
        return f"XXX-XX-{digits}"
    return ssn


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

    def _split_date(self, date_str: str | None) -> tuple[str, str, str]:
        """Split date string into (month, day, year)."""
        if not date_str:
            return "", "", ""

        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return f"{dt.month:02d}", f"{dt.day:02d}", f"{dt.year}"
            except ValueError:
                continue
        return "", "", ""

    def _map_patient_info_to_fields(self, info: PatientInfo) -> dict[str, Any]:
        """Map PatientInfo attributes to Form 69 field names.

        Args:
            info: Patient information.

        Returns:
            Dictionary mapping field names to values.
        """
        month, day, year = self._split_date(info.exam_date)

        # Aggregate diagnosis codes from evaluations
        diag_codes = []
        for eval in info.injury_evaluations:
            diag_codes.extend([c for c in eval.diagnosis_codes if c])
        diag_codes_str = ", ".join(diag_codes[:10]) # Limit to 10 for display

        fields: dict[str, Any] = {
            "1 Workers Compensation Insurance Carrier": info.insurance_carrier,
            "2 Employers Name": info.employer_name,
            "3 Employers Address  Street or PO Box City State Zip": info.employer_address,
            "4 Injured Employees Name First Middle Last": info.patient_name,
            "5 Date of Injury": info.date_of_injury,
            "6 Social Security Number": _format_ssn_masked(info.ssn),
            "7 Employees Phone Number": info.employee_primary_phone,
            "8 Employees Address  Street or PO Box City State Zip": info.employee_address,
            "9 Certifying Doctors Name and License Type": f"{info.doctor_name}, {info.doctor_license_type}" if info.doctor_name else "",
            "10 Certifying Doctors License Number and Jurisdiction": f"{info.doctor_license_number} {info.doctor_license_jurisdiction}" if info.doctor_license_number else "",
            "11 Doctors Phone": info.doctor_phone,
            "11 Doctors Fax": info.doctor_fax,
            "12 Certifying Doctors Address Street or PO Box City State Zip": info.doctor_address,
            "13. Designated Doctor selected by DWC": "/Yes",  # Explicitly Designated Doctor
            "14. Month - Date of Exam": month,
            "14. Day - Date of Exam": day,
            "14. Year - Date of Exam": year,
            "15 Diagnosis Codes": diag_codes_str,
            "DWC Claim": info.dwc_number,
            "Carrier Claim": info.claim_number,
            # Placeholder for Certification - usually filled manually or via GUI in future phases
            # For now we pre-fill the doctor info
            "18. Date of Certification": info.exam_date or "",
        }

        return fields

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
        writer = PdfWriter()

        # Clone entire document structure (including AcroForm)
        writer.clone_document_from_reader(reader)

        field_values = self._map_patient_info_to_fields(patient_info)
        writer.update_page_form_field_values(writer.pages[0], field_values)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"Form69 generated: {output_path}")
        return output_path
