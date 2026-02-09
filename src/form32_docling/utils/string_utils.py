"""String manipulation utilities for form32_docling."""

import re


def clean_location(location: str | None) -> str:
    """Clean and standardize location strings.

    Args:
        location: Raw location string from form.

    Returns:
        Cleaned and formatted location string.
    """
    if not location:
        return ""

    # Remove leading/trailing spaces and 'Fax:' artifacts
    result = location.strip().replace("Fax:", "").strip()

    # Add comma before city/state based on ZIP code pattern
    result = re.sub(r"(\d{5}-\d{4}|\d{5})", r", \1", result)

    # Normalize whitespace
    result = re.sub(r"\s+", " ", result)

    return result


def normalize_phone(phone: str | None) -> str:
    """Normalize phone number to XXX.XXX.XXXX format.

    Args:
        phone: Raw phone number string.

    Returns:
        Formatted phone number or original string if invalid.
    """
    if not phone:
        return ""

    # Extract digits only
    digits = "".join(c for c in phone if c.isdigit())

    # Handle 10-digit US phone numbers
    if len(digits) == 10:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"

    # Handle 11-digit with leading 1
    if len(digits) == 11 and digits[0] == "1":
        return f"{digits[1:4]}.{digits[4:7]}.{digits[7:]}"

    return phone.strip()


def clean_ssn(ssn: str | None, mask_full: bool = False) -> str:
    """Clean and format Social Security Number.

    Args:
        ssn: Raw SSN string.
        mask_full: If True, return XXX-XX-LAST4 format.

    Returns:
        Formatted SSN string.
    """
    if not ssn:
        return ""

    # Extract digits only
    digits = "".join(c for c in ssn if c.isdigit())

    if len(digits) == 9:
        if mask_full:
            return f"XXX-XX-{digits[5:]}"
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"

    # Return last 4 if available
    if len(digits) >= 4 and mask_full:
        return f"XXX-XX-{digits[-4:]}"

    return ssn.strip()


def extract_city(location: str | None) -> str:
    """Extract city name from a full address/location string.

    Args:
        location: Full location/address string.

    Returns:
        City name or empty string.
    """
    if not location:
        return ""

    # Common patterns for city extraction
    # Look for "City, State ZIP" pattern
    match = re.search(r"([A-Za-z\s]+),\s*[A-Z]{2}\s*\d{5}", location)
    if match:
        return match.group(1).strip()

    # Look for text before first comma
    if "," in location:
        return location.split(",")[0].strip()

    return ""


def clean_name(name: str | None) -> str:
    """Clean and standardize a person's name.

    Args:
        name: Raw name string.

    Returns:
        Cleaned name with proper capitalization.
    """
    if not name:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r"\s+", " ", name.strip())

    # Remove common artifacts
    cleaned = re.sub(r"[^\w\s,.-]", "", cleaned)

    return cleaned


def extract_license_parts(license_str: str | None) -> tuple[str, str, str]:
    """Extract license number, type, and jurisdiction from combined string.

    Args:
        license_str: Combined license string like "12345 MD TX".

    Returns:
        Tuple of (number, type, jurisdiction).
    """
    if not license_str:
        return ("", "", "")

    parts = license_str.strip().split()

    number = ""
    license_type = ""
    jurisdiction = ""

    for part in parts:
        if part.isdigit() or (part[0].isdigit() if part else False):
            number = part
        elif part.upper() in ("MD", "DC", "DO", "DPM", "PA", "NP"):
            license_type = part.upper()
        elif len(part) == 2 and part.isalpha():
            jurisdiction = part.upper()

    return (number, license_type, jurisdiction)
