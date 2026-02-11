"""Form generation controller for orchestrating DWC form creation."""

import logging

from form32_docling.config import Config
from form32_docling.models import PatientInfo

from .form68_generator import Form68Generator
from .form69_generator import Form69Generator
from .form73_generator import Form73Generator

logger = logging.getLogger(__name__)


class FormGenerationController:
    """Orchestrates generation of DWC Forms 68, 69, and 73.

    Form generation rules:
    - Form68: Generated when purpose_box_c, purpose_box_d, or purpose_box_g is checked
    - Form69: Always generated
    - Form73: Always generated (with Form69) but only needed when purpose_box_e is checked
    """

    def __init__(
        self,
        patient_info: PatientInfo,
        *,
        verbose: bool = False,
    ) -> None:
        """Initialize controller.

        Args:
            patient_info: Patient data for form generation.
            verbose: Enable verbose logging.
        """
        self.patient_info = patient_info
        self.verbose = verbose
        self.generated_forms: list[str] = []
        self.config = Config()

        self.output_directory = self.config.get_patient_dir(
            patient_info.exam_date or "",
            patient_info.patient_name or "",
            patient_info.exam_location_city,
        )

        self._generators: dict[str, type] = {
            "Form68": Form68Generator,
            "Form69": Form69Generator,
            "Form73": Form73Generator,
        }

    def _determine_required_forms(self) -> list[str]:
        """Determine which forms to generate based on purpose checkboxes.

        Returns:
            List of form type names to generate.
        """
        required: list[str] = []

        # Form68 triggers: boxes C, D, or G
        form68_triggers = [
            self.patient_info.purpose_box_c_checked,
            self.patient_info.purpose_box_d_checked,
            self.patient_info.purpose_box_g_checked,
        ]
        if any(form68_triggers):
            required.append("Form68")

        # Form69 is always required
        required.append("Form69")

        # Form73 is always generated together with Form69.
        required.append("Form73")

        return required

    def generate_forms(self) -> list[str]:
        """Generate all required forms.

        Returns:
            List of paths to generated form PDFs.
        """
        required_forms = self._determine_required_forms()
        output_paths: list[str] = []

        if not required_forms:
            logger.info("No forms required for generation")
            return output_paths

        for form_type in required_forms:
            if form_type not in self._generators:
                logger.warning(f"Unknown form type: {form_type}")
                continue

            try:
                generator_class = self._generators[form_type]
                generator = generator_class(self.config, verbose=self.verbose)
                generator.output_directory = self.output_directory

                output_path = generator.generate(self.patient_info)
                output_paths.append(str(output_path))

                if self.verbose:
                    logger.info(f"Generated {form_type}: {output_path}")

            except FileNotFoundError as e:
                logger.error(f"Template not found for {form_type}: {e}")
            except Exception as e:
                logger.error(f"Error generating {form_type}: {e}")

        self.generated_forms = output_paths
        return output_paths
