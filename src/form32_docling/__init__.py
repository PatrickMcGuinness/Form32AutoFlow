"""Form32 Docling - Medical form processor using the docling library.

This package provides Form 32 PDF processing and DWC form generation
using IBM's docling library for document extraction.
"""

__version__ = "0.1.0"

from form32_docling.config import Config
from form32_docling.core import CheckboxAnalyzer, Form32Processor, FormPages
from form32_docling.forms import (
    Form68Generator,
    Form69Generator,
    Form73Generator,
    FormGenerationController,
)
from form32_docling.models import Form32Data, PatientInfo

__all__ = [
    "CheckboxAnalyzer",
    "Config",
    "Form32Data",
    "Form32Processor",
    "Form68Generator",
    "Form69Generator",
    "Form73Generator",
    "FormGenerationController",
    "FormPages",
    "PatientInfo",
]
