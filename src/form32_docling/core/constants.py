"""Constants for Form32 processing."""

from enum import StrEnum
from typing import Any

# Regex patterns for field extraction
EXTRACTION_PATTERNS: dict[str, list[str]] = {
    "patient_name": [
        r"Injured\s*employee:\s*([^\n]+)",
        r"1\.\s*Employee's\s*name.*?\n.*?([^\n]+?)(?=\s*2\.)",
        r"Employee's\s*name\s*:\s*([^\n]+)",
    ],
    "exam_date": [
        r"Date:\s*\|\s*(\d{2}/\d{2}/\d{4})",
        r"Your\s*exam\s*is\s*on:.*?(\d{2}/\d{2}/\d{4})",
        r"exam\s*is\s*on:\s*(\d{2}/\d{2}/\d{4})",
    ],
    "exam_time": [
        r"Time:\s*\|\s*((?:1[0-2]|0?[1-9]):[0-5][0-9]\s*(?:AM|PM))",
    ],
    "exam_location": [
        r"Location:\s*\|\s*([^,\n]+?)(?=\s*,|\s*\d{3}-|\s*$)",
    ],
    "dwc_number": [
        r"DWC\s*#:\s*(\d+(?:-[A-Z]+)?)",
        r"DWC\s*claim\s*number.*?:\s*(\d+(?:-[A-Z]+)?)",
    ],
    "employee_ssn": [
        r"Social\s*Security\s*number.*?XXX\D*XX\D*(\d{4})",
        r"SSN.*?:\s*XXX\D*XX\D*(\d{4})",
    ],
    "date_of_injury": [
        r"8\.\s*Date\s*of\s*injury.*?\n\s*(\d{1,2}[./]\d{1,2}[./]\d{4})",
    ],
    "employee_address": [
        r"3\.\s*Employee's\s*address.*?\n((?:\d+[^,\n]+,\s*[^,\n]+,\s*(?:Texas|TX)\s+\d{5}))",
    ],
    "employee_county": [
        r"4\.\s*Employee(?:'s)?\s*county.*?\n.*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+County)",
    ],
    "employee_primary_phone": [
        r"5\.\s*Employee(?:'s)?\s*primary\s*phone.*\n\s*(\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4})",
    ],
    "employer_name": [
        r"13\.\s*Employer(?:'s)?\s*name.*?14\.\s*Employer(?:'s)?\s*phone.*?\n\s*([^\d\n]+)",
        r"Employer:\s*([^\n]+?)(?=\s+Insurance)",
    ],
    "insurance_carrier": [
        r"16\.\s*Insurance\s*carrier(?:'s)?\s*name.*?\n(.+?)(?=\s*17\.)",
    ],
    "carrier_address": [
         r"17\.\s*Insurance\s*carrier(?:'s)?\s*address.*?\n((?:\d+[^,\n]+,\s*[^,\n]+,\s*(?:Texas|TX|[A-Z]{2})\s+\d{5}))",
    ],
    "adjuster_name": [
        r"18\.\s*Adjuster(?:'s)?\s*name.*?(.+?)(?=\s*19\.)",
    ],
    "adjuster_email": [
        r"Adjuster(?:'s)?\s*email.*?\n\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
    ],
    "treating_doctor_name": [
        r"24\.\s*Treating\s*doctor(?:'s)?\s*name.*?\n\s*([A-Za-z.\-\s]+?)(?=,\s*MD\b)",
    ],
    "treating_doctor_phone": [
        r"25\.\s*Phone\s*number.*?\n\s*(\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4})",
    ],
    "treating_doctor_license_number": [
        r"28\.\s*License\s*number\s*([A-Z0-9]+)",
    ],
    "claim_number": [
        r"Insurance\s+carrier\s+claim\s+#[\s:]*([A-Z0-9]+)",
        r"claim\s+#\s*([A-Z0-9]+)",
    ],
    "doctor_name": [
        r"Name:\s*\|\s*([^\n|]+)",
    ],
    "doctor_phone": [
        r"Phone:\s*\|\s*(\d{3}[\.-]\d{3}[\.-]\d{4})",
    ],
    "doctor_address": [
        r"(?<=\n)(\d+[^,\n]+(?:,\s*[^,\n]+)*,\s*TX\s+\d{5}(?:-\d{4})?)",
    ],
}

class FormPages(StrEnum):
    """Form page type identifiers."""

    NETWORK = "network"
    BODY_AREA = "body_area"
    PURPOSE = "purpose"


# ROI definitions for checkbox regions
CHECKBOX_PARAMS: dict[str, dict[str, Any]] = {
    "network": {
        "x": 377,
        "w": 22,
        "h": 22,
        "threshold": 0.3,
        "checkboxes": {
            "q22_yes": 1778,
            "q22_no": 1778,
            "q23_yes": 1908,
            "q23_no": 1908,
        },
        "x_offsets": {
            "q22_no": 114,
            "q23_no": 117,
        },
    },
    "body_area": {
        "x": 83,
        "w": 30,
        "h": 30,
        "threshold": 0.3,
        "checkboxes": {
            "spine": 704,
            "upper_extremities": 790,
            "lower_extremities": 877,
            "feet": 964,
            "teeth_jaw": 1055,
            "eyes": 1116,
            "other_systems": 1170,
            "brain_injury": 1342,
            "spinal_cord": 1390,
            "burns": 1481,
            "fractures": 1530,
            "infectious": 1580,
            "regional_pain": 1630,
            "chemical_exposure": 1680,
            "cardiovascular": 1730,
            "mental_disorders": 1780,
        },
    },
    "purpose": {
        "x": 87,
        "w": 22,
        "h": 22,
        "threshold": 0.15,
        "checkboxes": {
            "box_a": 361,
            "box_b": 501,
            "box_c": 712,
            "box_d": 1144,
            "box_e": 1370,
            "box_f": 1555,
            "box_g": 1782,
            "dwc024_yes": 1914,
            "dwc024_no": 1958,
        },
    },
}
