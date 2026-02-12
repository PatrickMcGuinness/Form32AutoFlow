"""Shared field mapping functions for DWC form generators."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from form32_docling.models import PatientInfo


def _split_date(date_str: str | None) -> tuple[str, str, str]:
    """Split date string into (month, day, year)."""
    if not date_str:
        return "", "", ""

    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return f"{dt.month:02d}", f"{dt.day:02d}", f"{dt.year}"
        except ValueError:
            continue
    return "", "", ""


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
        return ""


def _format_phone_fax(phone: str | None, fax: str | None) -> str:
    """Format phone and fax values for a single form field."""
    if phone and fax:
        return f"{phone} / {fax}"
    return phone or fax or ""


def map_form68_fields(info: PatientInfo) -> dict[str, Any]:
    """Map PatientInfo attributes to Form 68 field names."""
    fields: dict[str, Any] = {
        "1 Employee name last first middle": info.patient_name or "",
        "2 Social Security number": info.employee_ssn or "",
        "3 Insurance carrier name": info.insurance_carrier or "",
        "4 Date of injury mmddyyyy": info.date_of_injury or "",
        "Insurance carrier claim number": info.claim_number or "",
        "DWC claim number": info.dwc_number or "",
        "5 Designated doctor name": info.doctor_name or "",
        "6 Designated doctor mailing address street or PO box city state ZIP code":
            info.doctor_address or "",
        "7 Designated doctor license number": info.doctor_license_number or "",
        "8 Designated doctor license jurisdiction":
            info.doctor_license_jurisdiction or "",
        "9 Designated doctor license type": info.doctor_license_type or "",
        "10 Designated doctor phone number": info.doctor_phone or "",
        "11 Exam location street city state ZIP code": info.exam_location or "",
        "12 Date and time of appointment": info.exam_date or "",
    }

    if info.purpose_box_c_checked:
        fields["a Extent of injury"] = "Yes"
    if info.purpose_box_d_checked:
        fields["b Disability Direct result"] = "Yes"
    if info.purpose_box_g_checked:
        fields["c Other similar issues"] = "Yes"

    for i, evaluation in enumerate(info.injury_evaluations[:6]):
        row_num = i + 1
        fields[f"Additional claimed diagnosis or condition, row {row_num}"] = (
            evaluation.condition_text or ""
        )
        if evaluation.is_substantial_factor is True:
            fields[
                "Yes (Did you determine that the accident or incident giving rise to the compensable injury was a substantial factor in bringing about the additional claimed diagnoses or condition?), row "
                f"{row_num}"
            ] = "Yes"
        elif evaluation.is_substantial_factor is False:
            fields[
                "No (Did you determine that the accident or incident giving rise to the compensable injury was a substantial factor in bringing about the additional claimed diagnoses or condition?), row "
                f"{row_num}"
            ] = "Yes"

        for c_idx, code in enumerate(evaluation.diagnosis_codes[:4]):
            fields[f"Diagnosis code {c_idx + 1}, row {row_num}"] = code or ""

    return fields


def map_form69_fields(info: PatientInfo) -> dict[str, Any]:
    """Map PatientInfo attributes to Form 69 field names."""
    month, day, year = _split_date(info.exam_date)
    diag_codes: list[str] = []
    for evaluation in info.injury_evaluations:
        diag_codes.extend([code for code in evaluation.diagnosis_codes if code])

    return {
        "1 Workers Compensation Insurance Carrier": info.insurance_carrier or "",
        "2 Employers Name": info.employer_name or "",
        "3 Employers Address  Street or PO Box City State Zip": info.employer_address or "",
        "4 Injured Employees Name First Middle Last": info.patient_name or "",
        "5 Date of Injury": info.date_of_injury or "",
        "6 Social Security Number": _format_ssn_masked(info.employee_ssn),
        "7 Employees Phone Number": info.employee_primary_phone or "",
        "8 Employees Address  Street or PO Box City State Zip": info.employee_address or "",
        "9 Certifying Doctors Name and License Type": (
            f"{info.doctor_name}, {info.doctor_license_type}" if info.doctor_name else ""
        ),
        "10 Certifying Doctors License Number and Jurisdiction": (
            f"{info.doctor_license_number} {info.doctor_license_jurisdiction}"
            if info.doctor_license_number
            else ""
        ),
        "11 Doctors Phone": info.doctor_phone or "",
        "11 Doctors Fax": info.doctor_fax or "",
        "12 Certifying Doctors Address Street or PO Box City State Zip": info.doctor_address or "",
        "13. Designated Doctor selected by DWC": "/Yes",
        "14. Month - Date of Exam": month,
        "14. Day - Date of Exam": day,
        "14. Year - Date of Exam": year,
        "15 Diagnosis Codes": ", ".join(diag_codes[:10]),
        "DWC Claim": info.dwc_number or "",
        "Carrier Claim": info.claim_number or "",
        "18. Date of Certification": info.exam_date or "",
    }


def map_form73_section_i_fields(info: PatientInfo) -> dict[str, Any]:
    """Map Section I (General Information) fields for Form 73."""
    ssn_last4 = info.employee_ssn.split("-")[-1] if info.employee_ssn else ""
    carrier_contact = (
        info.adjuster_fax
        or info.adjuster_email
        or info.insurance_billing_fax
        or info.insurance_billing_email
        or ""
    )

    return {
        "1.  Injured Employee's Name": info.patient_name or "",
        "2.  Date of Injury": info.date_of_injury or "",
        "3.  Social Security Number": ssn_last4,
        "4.  Employee's Description of Injury/Accident": info.extent_of_injury or "",
        "5a.  Doctor's/Delegating Doctor's Name and Degree": (
            f"{info.doctor_name}, {info.doctor_license_type}" if info.doctor_name else ""
        ),
        "5b.  PA/APRN Name": "",
        "6.  Clinic/Facility Name": _clean_facility_name(info.exam_location),
        "7.  Clinic/Facility/Doctor Phone & Fax": _format_phone_fax(
            info.doctor_phone, info.doctor_fax
        ),
        "8.  Clinic/Facility/Doctor Address (street address)": info.doctor_address or "",
        "9.  Employer's Name": info.employer_name or "",
        "10.  Employer's Fax Number or E-mail Address": info.employer_phone or "",
        "11.  Insurance Carrier": info.insurance_carrier or "",
        "12.  Carrier's Fax Number or E-mail Address": carrier_contact,
    }


def map_form73_fields(info: PatientInfo) -> dict[str, Any]:
    """Map PatientInfo attributes to Form 73 field names."""
    month, day, year = _split_date(info.exam_date)

    hour, minute = "", ""
    if info.exam_time:
        try:
            dt_time = datetime.strptime(info.exam_time, "%I:%M %p")
            hour = f"{dt_time.hour % 12 or 12}"
            minute = f"{dt_time.minute:02d}"
        except ValueError:
            pass

    fields = map_form73_section_i_fields(info)
    fields.update(
        {
            "Role: Designated doctor": "/Yes",
            "date of TD evaluation month (mm)": month,
            "date of TD evaluation day (dd)": day,
            "date of TD evaluation year (yyyy)": year,
            "Time of TD evaluation HOUR": hour,
            "Time of TD evaluation MINUTES": minute,
            "Discharge time": _calculate_discharge_time(info.exam_time),
            "Date Being Sent": datetime.now().strftime("%m/%d/%Y"),
        }
    )
    return fields
