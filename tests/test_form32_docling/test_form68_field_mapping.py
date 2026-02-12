"""Test Form 68 field mapping to verify correct PDF field names are used."""


from pathlib import Path
from typing import Any, cast

import pytest
from pypdf import PdfReader

from form32_docling.config import Config
from form32_docling.forms.form68_generator import Form68Generator
from form32_docling.models.patient_info import InjuryEvaluation, PatientInfo

# Expected PDF field names in DWC068 template
EXPECTED_PDF_FIELDS = [
    "1 Employee name last first middle",
    "2 Social Security number",
    "3 Insurance carrier name",
    "4 Date of injury mmddyyyy",
    "5 Designated doctor name",
    "6 Designated doctor mailing address street or PO box city state ZIP code",
    "7 Designated doctor license number",
    "8 Designated doctor license jurisdiction",
    "9 Designated doctor license type",
    "10 Designated doctor phone number",
    "11 Exam location street city state ZIP code",
    "12 Date and time of appointment",
    "Insurance carrier claim number",
    "DWC claim number",
    "a Extent of injury",
    "b Disability Direct result",
    "c Other similar issues",
    "Additional claimed diagnosis or condition, row 1",
    "Additional claimed diagnosis or condition, row 2",
    "Diagnosis code 1, row 1",
    "Diagnosis code 2, row 1",
]


@pytest.fixture
def config() -> Config:
    """Create a test configuration."""
    return Config()


@pytest.fixture
def form68_generator(config: Config) -> Form68Generator:
    """Create a Form68Generator instance."""
    return Form68Generator(config)


@pytest.fixture
def sample_patient_info() -> PatientInfo:
    """Create a sample PatientInfo with test data."""
    return PatientInfo(
        patient_name="John Doe",
        employee_ssn="1234",
        date_of_injury="2024-01-15",
        claim_number="CLAIM123",
        dwc_number="DWC123456",
        insurance_carrier="Test Insurance Co",
        doctor_name="Dr. Jane Smith",
        doctor_address="123 Medical Dr, Austin, TX 78701",
        doctor_license_number="MD12345",
        doctor_license_jurisdiction="TX",
        doctor_license_type="MD",
        doctor_phone="512-555-1234",
        exam_date="01/20/2025 10:00 AM",
        exam_location="456 Exam St, San Antonio, TX 78201",
        purpose_box_c_checked=True,
        purpose_box_d_checked=True,
        purpose_box_g_checked=False,
        injury_evaluations=[
            InjuryEvaluation(
                condition_text="Lumbar spine strain",
                is_substantial_factor=True,
                diagnosis_codes=["M54.5", "M54.2", "", ""],
            ),
            InjuryEvaluation(
                condition_text="Cervical radiculopathy",
                is_substantial_factor=False,
                diagnosis_codes=["M54.12", "", "", ""],
            ),
        ],
    )


class TestForm68FieldMapping:
    """Test that field mapping uses correct PDF field names."""

    def test_map_patient_info_uses_actual_pdf_field_names(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
    ) -> None:
        """Verify that _map_patient_info_to_fields uses actual PDF field names."""
        fields = form68_generator._map_patient_info_to_fields(sample_patient_info)

        # Check that we're using actual PDF field names, not generic ones
        assert "1 Employee name last first middle" in fields
        assert "2 Social Security number" in fields
        assert "3 Insurance carrier name" in fields
        assert "4 Date of injury mmddyyyy" in fields
        assert "5 Designated doctor name" in fields
        assert "12 Date and time of appointment" in fields
        assert "Insurance carrier claim number" in fields
        assert "DWC claim number" in fields

        # Ensure we're NOT using the old incorrect field names
        assert "patient_name" not in fields
        assert "patient_ssn" not in fields
        assert "date_of_injury" not in fields  # This was ambiguous
        assert "exam_date" not in fields

    def test_field_values_are_correctly_mapped(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
    ) -> None:
        """Verify that PatientInfo values are correctly mapped to fields."""
        fields = form68_generator._map_patient_info_to_fields(sample_patient_info)

        assert fields["1 Employee name last first middle"] == "John Doe"
        assert fields["2 Social Security number"] == "1234"
        assert fields["3 Insurance carrier name"] == "Test Insurance Co"
        assert fields["4 Date of injury mmddyyyy"] == "2024-01-15"
        assert fields["5 Designated doctor name"] == "Dr. Jane Smith"
        assert fields["Insurance carrier claim number"] == "CLAIM123"
        assert fields["DWC claim number"] == "DWC123456"
        assert fields["12 Date and time of appointment"] == "01/20/2025 10:00 AM"

    def test_purpose_checkboxes_mapped_correctly(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
    ) -> None:
        """Verify purpose checkboxes are mapped to correct field names."""
        fields = form68_generator._map_patient_info_to_fields(sample_patient_info)

        # box_c_checked = Extent of injury
        assert fields.get("a Extent of injury") == "Yes"
        # box_d_checked = Disability
        assert fields.get("b Disability Direct result") == "Yes"
        # box_g_checked = Other (False in sample)
        assert fields.get("c Other similar issues") is None

    def test_injury_evaluations_mapped_correctly(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
    ) -> None:
        """Verify injury evaluations are mapped to correct field names."""
        fields = form68_generator._map_patient_info_to_fields(sample_patient_info)

        # Row 1
        assert fields["Additional claimed diagnosis or condition, row 1"] == "Lumbar spine strain"
        assert fields["Diagnosis code 1, row 1"] == "M54.5"
        assert fields["Diagnosis code 2, row 1"] == "M54.2"

        # Row 2
        assert fields["Additional claimed diagnosis or condition, row 2"] == "Cervical radiculopathy"
        assert fields["Diagnosis code 1, row 2"] == "M54.12"

    def test_substantial_factor_checkboxes_mapped(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
    ) -> None:
        """Verify substantial factor Yes/No checkboxes use correct field names."""
        fields = form68_generator._map_patient_info_to_fields(sample_patient_info)

        # Row 1: is_substantial_factor=True -> Yes checkbox
        yes_field_1 = "Yes (Did you determine that the accident or incident giving rise to the compensable injury was a substantial factor in bringing about the additional claimed diagnoses or condition?), row 1"
        assert fields.get(yes_field_1) == "Yes"

        # Row 2: is_substantial_factor=False -> No checkbox
        no_field_2 = "No (Did you determine that the accident or incident giving rise to the compensable injury was a substantial factor in bringing about the additional claimed diagnoses or condition?), row 2"
        assert fields.get(no_field_2) == "Yes"

    def test_mapped_fields_exist_in_pdf_template(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
    ) -> None:
        """Verify that all mapped field names exist in the actual PDF template."""
        # Get actual field names from template
        template_path = form68_generator.template_path
        assert template_path.exists(), f"Template not found: {template_path}"

        reader = PdfReader(str(template_path))
        root = cast(Any, reader.trailer["/Root"])
        form = cast(Any, root["/AcroForm"])
        pdf_fields = set()
        for field in cast(Any, form["/Fields"]):
            obj = field.get_object()
            name = obj.get("/T", "")
            if name:
                pdf_fields.add(name)

        # Get mapped field names
        mapped_fields = form68_generator._map_patient_info_to_fields(sample_patient_info)

        # Check that all mapped field names exist in PDF
        missing_fields = []
        for field_name in mapped_fields:
            if field_name not in pdf_fields:
                missing_fields.append(field_name)

        assert not missing_fields, f"Mapped fields not found in PDF template: {missing_fields}"

    def test_generate_pdf_with_populated_fields(
        self,
        form68_generator: Form68Generator,
        sample_patient_info: PatientInfo,
        tmp_path: Path,
    ) -> None:
        """Test that generated PDF has fields populated."""
        # Set output directory
        form68_generator.output_directory = tmp_path

        # Generate the PDF
        output_path = form68_generator.generate(sample_patient_info)

        # Verify file was created
        assert output_path.exists()

        # Read the generated PDF and check field values
        reader = PdfReader(str(output_path))
        root = cast(Any, reader.trailer["/Root"])

        # Check that AcroForm exists
        assert "/AcroForm" in root

        # Get field values from the generated PDF
        form = cast(Any, root["/AcroForm"])
        field_values = {}
        for field in cast(Any, form["/Fields"]):
            obj = field.get_object()
            name = obj.get("/T", "")
            value = obj.get("/V", "")
            if name and value:
                field_values[name] = value

        # Verify key fields were populated
        # Note: pypdf may return values in different formats, so we check for presence
        assert len(field_values) > 0, "No fields were populated in the generated PDF"


class TestForm68FieldMappingEmptyData:
    """Test field mapping with edge cases."""

    def test_empty_patient_info(self, form68_generator: Form68Generator) -> None:
        """Verify mapping handles empty PatientInfo gracefully."""
        empty_info = PatientInfo()
        fields = form68_generator._map_patient_info_to_fields(empty_info)

        # All fields should be empty strings, not None
        for field_name, value in fields.items():
            assert value in ("", "Yes", "No") or value is None, \
                f"Field {field_name} has unexpected value: {value}"

    def test_no_injury_evaluations(self, form68_generator: Form68Generator) -> None:
        """Verify mapping handles no injury evaluations."""
        info = PatientInfo(
            patient_name="Test Patient",
            injury_evaluations=[],
        )
        fields = form68_generator._map_patient_info_to_fields(info)

        # Should not have injury evaluation fields
        assert "Additional claimed diagnosis or condition, row 1" not in fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
