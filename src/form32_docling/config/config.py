"""Configuration module for form32_docling.

Platform-aware configuration with environment variable support.
Docling handles OCR internally.
"""

from dataclasses import dataclass, field
from pathlib import Path

from form32_docling.config import custom_config
from form32_docling.utils.date_utils import format_date


@dataclass
class Config:
    """Configuration settings for form32_docling processing.

    Attributes:
        base_directory: Base output directory for processed forms.
        pdf_path: Default source directory for Form 32 PDFs.
    """

    base_directory: Path = field(default_factory=custom_config.get_base_output_dir)
    pdf_path: Path = field(default_factory=custom_config.get_pdf_source_dir)
    use_vlm: bool = False
    output_docling_document: bool = False  # Output docling document JSON when -v flag set
    output_docling_markdown: bool = False  # Output docling document as Markdown when -v flag set
    output_form32_json: bool = False       # Output structured Form32Data as JSON
    docling_model: str | None = field(default_factory=custom_config.get_default_docling_model)  # Custom docling model

    # Designated Doctor Defaults
    doctor_phone: str = custom_config.DEFAULT_DOCTOR_PHONE
    doctor_license_type: str = custom_config.DEFAULT_DOCTOR_LICENSE_TYPE
    doctor_license_jurisdiction: str = custom_config.DEFAULT_DOCTOR_LICENSE_JURISDICTION

    def __post_init__(self) -> None:
        """Ensure directories exist after initialization."""
        self.base_directory.mkdir(parents=True, exist_ok=True)


    def get_patient_dir(
        self,
        exam_date: str,
        patient_name: str,
        exam_location_city: str | None = None,
    ) -> Path:
        """Get standardized patient directory path.

        Directory format: "PATIENT_CITY_M.D.YY"

        Args:
            exam_date: Exam date string.
            patient_name: Patient's full name.
            exam_location_city: Optional city name for the directory.

        Returns:
            Path object for the patient directory.
        """
        formatted_date = format_date(exam_date)
        name_upper = patient_name.replace(" ", "_") if patient_name else "Patient"

        if exam_location_city:
            dir_name = f"{name_upper}_{exam_location_city}_{formatted_date}"
        else:
            dir_name = f"{name_upper}_{formatted_date}"

        return self.base_directory / dir_name

    @staticmethod
    def get_project_root() -> Path:
        """Get the root directory of the Form32reader project."""
        return Path(__file__).parent.parent.parent.parent

    @property
    def form68_template(self) -> Path:
        """Get path to Form 68 template."""
        # Prioritize the fillable version in WorkersCompData if it exists
        path = self.get_project_root() / "WorkersCompData" / "dwc068drrpt-fillable.pdf"
        if not path.exists():
            path = self.get_templates_dir() / "DWC068.pdf"
        return path

    @property
    def form69_template(self) -> Path:
        """Get path to Form 69 template."""
        # Prioritize the fillable version in WorkersCompData if it exists
        path = self.get_project_root() / "WorkersCompData" / "dwc069medrpt-fillable.pdf"
        if not path.exists():
            path = self.get_templates_dir() / "DWC069.pdf"
        return path

    @property
    def form73_template(self) -> Path:
        """Get path to Form 73 template."""
        # Prioritize the fillable version in WorkersCompData if it exists
        path = self.get_project_root() / "WorkersCompData" / "dwc073wkstat-fillable.pdf"
        if not path.exists():
            path = self.get_templates_dir() / "DWC073.pdf"
        return path

    @staticmethod
    def get_form_path(directory: Path, form_type: str | None, patient_name: str | None) -> Path:
        """Get path for a specific form within patient directory.

        Args:
            directory: Patient directory path.
            form_type: Form type (e.g., "DWC068", "DWC069").
            patient_name: Patient's name for filename.

        Returns:
            Path object for the form PDF.
        """
        safe_name = (patient_name or "UNKNOWN_PATIENT").strip().upper()
        safe_type = (form_type or "UNKNOWN_FORM").strip().upper()
        return directory / f"{safe_type} {safe_name}.pdf"

    @staticmethod
    def get_templates_dir() -> Path:
        """Get path to form templates directory."""
        return Path(__file__).parent.parent / "forms" / "templates"

    def to_dict(self) -> dict:
        """Convert config to dictionary for serialization."""
        return {
            "base_directory": str(self.base_directory),
            "pdf_path": str(self.pdf_path),
            "use_vlm": self.use_vlm,
            "output_docling_document": self.output_docling_document,
            "output_docling_markdown": self.output_docling_markdown,
            "output_form32_json": self.output_form32_json,
            "docling_model": self.docling_model,
            "doctor_phone": self.doctor_phone,
            "doctor_license_type": self.doctor_license_type,
            "doctor_license_jurisdiction": self.doctor_license_jurisdiction,
        }
