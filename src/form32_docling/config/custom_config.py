"""Private configuration defaults for form32_docling.

This module provides defaults for hardcoded paths and doctor information,
supporting environment variable overrides.
"""

import os
import platform
from pathlib import Path

# --- Output and Data Paths ---

def get_base_output_dir() -> Path:
    """Get the default base output directory."""
    env_val = os.environ.get("FORM32_OUTPUT_DIR")
    if env_val:
        return Path(env_val)

    # Platform defaults
    if platform.system() == "Windows":
        return Path(r"D:\AIDev\Pending Exams")

    # Linux/WSL2 default
    return Path.home() / "AIDev/Form32_output"


def get_pdf_source_dir() -> Path:
    """Get the default PDF source directory."""
    env_val = os.environ.get("FORM32_PDF_PATH")
    if env_val:
        return Path(env_val)

    # Platform defaults
    if platform.system() == "Windows":
        return Path(r"D:\AIDev\Form32_pdf")

    # Linux/WSL2 default
    return Path.home() / "AIDev/Form32_pdf"


# --- Designated Doctor Defaults ---

DEFAULT_DOCTOR_PHONE = os.environ.get("FORM32_DOCTOR_PHONE", "512-903-5083")
DEFAULT_DOCTOR_LICENSE_TYPE = os.environ.get("FORM32_DOCTOR_LICENSE_TYPE", "D.C.")
DEFAULT_DOCTOR_LICENSE_JURISDICTION = os.environ.get("FORM32_DOCTOR_LICENSE_JURISDICTION", "TX")

# --- Docling Model Defaults ---

def get_default_docling_model() -> str | None:
    """Get the default docling model name."""
    return os.environ.get("DOCLING_MODEL")
