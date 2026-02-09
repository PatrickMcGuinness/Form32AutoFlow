"""DWC Form-073 generator (Work Status Report)."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter

from form32_docling.config import Config
from form32_docling.models import PatientInfo

logger = logging.getLogger(__name__)


def _clean_facility_name(location: str | None) -> str:
    """Extract facility name from full location string."""
    if not location:
        return ""
    return location.split(",")[0].strip()


def _calculate_discharge_time(exam_time: str | None) -> str:
    """Calculate discharge time 30 minutes after exam time."""
    if not exam_time:
        return ""
    try:
        time_obj = datetime.strptime(exam_time, "%I:%M %p")
        discharge = time_obj + timedelta(minutes=30)
        return discharge.strftime("%I:%M %p")
    except ValueError:
        logger.warning(f"Unable to parse exam time: {exam_time}")
        return ""


class Form73Generator:
    """Generates DWC Form-073 by filling interactive form fields."""

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
        self.template_path = self.config.form73_template
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
        """Map PatientInfo attributes to Form 73 field name.

        Args:
            info: Patient information.

        Returns:
            Dictionary mapping field names to values.
        """
        ssn_last4 = info.ssn.split("-")[-1] if info.ssn else ""
        month, day, year = self._split_date(info.exam_date)

        # Split time into hour and minutes
        hour, minute = "", ""
        if info.exam_time:
            try:
                dt_time = datetime.strptime(info.exam_time, "%I:%M %p")
                hour = f"{dt_time.hour % 12 or 12}"
                minute = f"{dt_time.minute:02d}"
            except ValueError:
                pass

        fields: dict[str, Any] = {
            "1.  Injured Employee's Name": info.patient_name,
            "2.  Date of Injury": info.date_of_injury,
            "3.  Social Security Number": ssn_last4,
            "5a.  Doctor's/Delegating Doctor's Name and Degree": f"{info.doctor_name}, {info.doctor_license_type}" if info.doctor_name else "",
            "6.  Clinic/Facility Name": _clean_facility_name(info.exam_location),
            "7.  Clinic/Facility/Doctor Phone & Fax": f"{info.doctor_phone} / {info.doctor_fax}" if info.doctor_phone else "",
            "8.  Clinic/Facility/Doctor Address (street address)": info.doctor_address,
            "9.  Employer's Name": info.employer_name,
            "11.  Insurance Carrier": info.insurance_carrier,
            "Role: Designated doctor": "/Yes",  # Explicitly Designated Doctor
            "date of TD evaluation month (mm)": month,
            "date of TD evaluation day (dd)": day,
            "date of TD evaluation year (yyyy)": year,
            "Time of TD evaluation HOUR": hour,
            "Time of TD evaluation MINUTES": minute,
            "Discharge time": _calculate_discharge_time(info.exam_time),
            "Date Being Sent": datetime.now().strftime("%m/%d/%Y"),
        }

        return fields

    def generate(self, patient_info: PatientInfo) -> Path:
        """Generate Form-073 PDF by filling form fields.

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
            patient_dir, "DWC073", patient_info.patient_name or "UNKNOWN"
        )

        reader = PdfReader(str(self.template_path))
        writer = PdfWriter()

        # Clone entire document structure (including AcroForm)
        writer.clone_document_from_reader(reader)

        field_values = self._map_patient_info_to_fields(patient_info)
        writer.update_page_form_field_values(writer.pages[0], field_values)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"Form73 generated: {output_path}")
        return output_path
