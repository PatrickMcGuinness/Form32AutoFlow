import argparse
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any

import pypdf
from faker import Faker
from pypdf.generic import NameObject

from form32_docling.config.form32_templates import (
    DWC032_part1_template,
    DWC032_part3_template,
    DWC032_part5_template,
    DWC032_part6_template,
)

logger = logging.getLogger(__name__)
fake = Faker()

# Default input PDF location
DEFAULT_INPUT_PDF = Path(__file__).resolve().parents[2] / "WorkersCompData" / "dwc032desdoc-fillable.pdf"

# Mapping from Template field labels to PDF form field names
FIELD_MAPPING = {
    # Part 1
    "1. Employee's name": "1 Employees name first middle last",
    "2. Social Security number": "2 Social Security number",
    "3. Employee's address": "3 Employees address street or PO box city state ZIP code",
    "4. Employee's county": "4 Employees county",
    "5. Employee's primary phone number": "5 Employees primary phone number",
    "6. Employee's alternate phone number": "6 Employees alternate phone number",
    "7. Employee's date of birth (mm/dd/yyyy)": "7 Employees date of birth mmddyyyy",
    "8. Date of injury (mm/dd/yyyy)": "8 Date of injury mmddyyyy",
    "9. Representative's name": "9 Representatives name first middle last",
    "10. Representative's phone number": "10 Representatives phone number",
    "11. Representative's email address": "11 Representatives email address",
    "12. Representative's fax number": "12 Representatives fax number",
    "13. Employer's name": "13 Employers name",
    "14. Employer's phone number": "14 Employers phone number",
    "15. Employer's address": "15 Employers address street or PO box city state ZIP code",
    "16. Insurance carrier's name": "16 Insurance carriers name",
    "17. Insurance carrier's address": "17 Insurance carriers address street or PO box city state ZIP code",
    "18. Adjuster's name": "18 Adjusters name first middle last",
    "19. Adjuster's email": "19 Adjusters email address",
    "20. Adjuster's phone number": "20 Adjusters phone number",
    "21. Adjuster's fax number": "21 Adjusters fax number",
    "22. Certified network": {
        "Yes": "22. YES - Does the claim have medical benefits provided through a certified workers compensation health care network",
        "No": "22. NO - Does the claim have medical benefits provided through a certified workers compensation health care network"
    },
    "If yes, name of the network": "22. Name of network",
    "23. Political subdivision": {
        "Yes": "23. YES - Does the claim have medical benefits provided through a political subdivision according to Texas Labor Code Section 504",
        "No": "23. NO - Does the claim have medical benefits provided through a political subdivision according to Texas Labor Code Section 504"
    },
    "If yes, name of the health care plan": "23. Name of health care plan",

    # Part 3
    "24. Treating doctor name": "24 Treating doctors name",
    "25. Phone number": "25 Phone number",
    "26. Address": "26 Address street or PO box city state ZIP code",
    "27. Fax number": "27 Fax number",
    "28. License number": "28 License number",
    "29. License type": "29 License type",

    # Part 4 (Checkboxes - in Part 3 template)
    "Spine and musculoskeletal structures of torso": "Spine and musculoskeletal structures of torso",
    "Upper extremities": "Upper extremities See below for a fracture with",
    "Lower extremities (excluding feet)": "Lower extremities excluding feet",
    "Feet": "Feet",
    "Teeth and jaw": "Teeth and jaw",
    "Eyes": "Eyes",
    "Other body areas or systems": "Other body areas or systems",
    "Traumatic brain injury": "Traumatic brain injury",
    "Spinal cord injury": "Spinal cord injury",
    "Severe burns (including chemical burns)": "Severe burns including chemical burns",
    "Joint dislocation, fractures with vascular injury": "Fractures with vascular injury, joint dislocation and pelvis, or multiple rib fractures",
    "Infectious diseases (complicated)": "Infectious diseases (complicated)",
    "Complex regional pain syndrome": "Complex regional pain syndrome",
    "Chemical exposure": "Chemical exposure",
    "Heart or cardiovascular condition": "Heart or cardiovascular condition",
    "Mental and behavioral disorders": "Mental and behavioral disorders",

    # Part 5
    "A. MMI": "A",
    "Statutory MMI date": "A: Statutory MMI date if any (mm/dd/yyyy)",
    "B. Impairment rating": "B",
    "MMI Date (if Box A not checked)": "B. MMI date (mm/dd/yyyy)",
    "C. Extent of injury": "C",
    "C. Description of accident or incident": "List all injuries (diagnoses, body parts, or conditions) in question, claimed to be caused by, or naturally resulting from the accident or incident and describe the accident or incident that caused the claimed injury",
    "D. Disability - direct result": "D",
    "D. From": "D: Claimed period of disability start date (mm/dd/yyyy)",
    "D. to": "D: Claimed period of disability end date (mm/dd/yyyy)",
    "E. Return to work": "E",
    "E. From": "E Period to be assessed start date (mm/dd/yyyy)",
    "E. to": "E Period to be assessed end date (mm/dd/yyyy)",
    "F. Return to work (SIBs)": "F",
    "F. From": "F: Period to be assessed start date (mm/dd/yyyy)",
    "F. to": "F: Period to be assessed end date (mm/dd/yyyy)",
    "G. Other issues": "G. Other similar issues",
    "G. Description of issues": "G. Identify the issues for the designated doctor to address, including whether a first responder is still eligible to receive lifetime income benefits under Labor Code 408.1615",

    # Part 6
    "Requester type": {
        "Injured employee": "Injured employee",
        "Injured employee representative": "Injured employee representative",
        "Insurance carrier": "Insurance carrier"
    },
    "Requester name": "35 Printed name of requester",
    "Requester date": "36 Date of signature mmddyyyy",
}

def generate_realistic_data(field_label: str, field_type: Any, count: int = 10) -> list[Any]:
    """Generate realistic random data based on field label."""
    entries = []
    for _ in range(count):
        if isinstance(field_type, list):
            entries.append(random.choice(field_type))
            continue

        label_lower = field_label.lower()
        if "name" in label_lower:
            entries.append(fake.name())
        elif "address" in label_lower:
            entries.append(fake.address().replace("\n", ", "))
        elif "phone" in label_lower or "fax" in label_lower:
            entries.append(fake.phone_number())
        elif "date" in label_lower or "birth" in label_lower or "injury" in label_lower:
            entries.append(fake.date(pattern="%m/%d/%Y"))
        elif "email" in label_lower:
            entries.append(fake.email())
        elif "social security" in label_lower or "ssn" in label_lower:
            entries.append(fake.ssn())
        elif "county" in label_lower:
            entries.append(fake.city() + " County")
        elif "description" in label_lower or "list all" in label_lower or "identify" in label_lower:
            entries.append(fake.text(max_nb_chars=100))
        elif "checked" in label_lower or "selected" in label_lower:
             entries.append(random.choice(["Checked", "Unchecked"]))
        else:
            entries.append(fake.word())
    return entries

def construct_randomized_json() -> dict[str, Any]:
    """Construct a JSON structure with randomized data picked from 10 generated entries."""
    all_templates = {
        **DWC032_part1_template,
        **DWC032_part3_template,
        **DWC032_part5_template,
        **DWC032_part6_template,
    }

    field_pool = {}
    for label, field_type in all_templates.items():
        field_pool[label] = generate_realistic_data(label, field_type, 10)

    result = {}
    for label in all_templates:
        result[label] = random.choice(field_pool[label])

    return result

def fill_pdf(input_pdf: Path, output_pdf: Path, data: dict[str, Any]) -> None:
    """Fill the PDF form fields with data."""
    reader = pypdf.PdfReader(input_pdf)
    writer = pypdf.PdfWriter()

    # Copy all pages and AcroForm data
    writer.append_pages_from_reader(reader)

    # Explicitly ensure AcroForm is copied if pypdf missed it
    if "/AcroForm" not in writer.root_object and "/AcroForm" in reader.root_object:
        writer.root_object.update({
            NameObject("/AcroForm"): reader.root_object["/AcroForm"]
        })

    # Construct field updates
    field_values = {}
    for template_label, value in data.items():
        pdf_field = FIELD_MAPPING.get(template_label)
        if not pdf_field:
            continue

        if isinstance(pdf_field, dict):
            # Checkbox/Radio logic
            if value in pdf_field:
                field_values[pdf_field[value]] = "/Yes"
        elif isinstance(value, str):
            if value == "Selected" or value == "Checked":
                field_values[pdf_field] = "/Yes"
            elif value == "Not Selected" or value == "Unchecked":
                field_values[pdf_field] = "/Off"
            else:
                field_values[pdf_field] = value

    # Update all pages
    for i in range(len(writer.pages)):
        writer.update_page_form_field_values(writer.pages[i], field_values)

    with open(output_pdf, "wb") as f:
        writer.write(f)

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Populate Form32 PDF with randomized data."
    )
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=DEFAULT_INPUT_PDF,
        help=f"Input fillable PDF path (default: {DEFAULT_INPUT_PDF})"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("."),
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout
    )

    if not args.input.exists():
        logger.error(f"Input PDF {args.input} not found.")
        sys.exit(1)

    if not args.output_dir.exists():
        logger.info(f"Creating output directory: {args.output_dir}")
        args.output_dir.mkdir(parents=True, exist_ok=True)

    random_num = random.randint(1000, 9999)
    output_filename = f"DWC032_randomized_{random_num}.pdf"
    output_pdf = args.output_dir / output_filename

    data = construct_randomized_json()
    logger.debug("Constructed randomized JSON data:")
    logger.debug(json.dumps(data, indent=2))

    try:
        fill_pdf(args.input, output_pdf, data)
        logger.info(f"Generated populated PDF: {output_pdf}")
    except Exception as e:
        logger.error(f"Failed to fill PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
