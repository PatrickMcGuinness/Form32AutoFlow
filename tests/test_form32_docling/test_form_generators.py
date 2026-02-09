"""Tests for form32_docling form generators."""


import pytest

from form32_docling.forms import (
    Form68Generator,
    Form69Generator,
    Form73Generator,
    FormGenerationController,
)
from form32_docling.models import PatientInfo


@pytest.fixture
def sample_patient_info() -> PatientInfo:
    """Create sample patient info for testing."""
    return PatientInfo(
        patient_name="John Doe",
        ssn="123-45-6789",
        exam_date="01/15/2024",
        exam_time="10:00 AM",
        exam_location="Test Clinic",
        exam_location_city="Austin",
        date_of_injury="06/15/2023",
        insurance_carrier="ABC Insurance",
        claim_number="CLM12345",
        dwc_number="123456",
        employer_name="Test Employer",
        employer_address="123 Main St, Austin, TX 78701",
        doctor_name="Dr. Smith",
        doctor_phone="512.555.1234",
        doctor_address="456 Oak Ave, Austin, TX 78702",
        doctor_license_number="12345",
        doctor_license_type="D.C.",
        doctor_license_jurisdiction="TX",
        treating_doctor_name="Dr. Jones",
        treating_doctor_phone="512.555.5678",
        treating_doctor_license_number="67890",
        treating_doctor_license_type="MD",
        treating_doctor_license_jurisdiction="TX",
        has_certified_network=True,
        health_plan_name="Test Network",
        purpose_box_c_checked=True,
        purpose_box_e_checked=True,
    )


class TestForm68Generator:
    """Tests for Form68Generator."""

    def test_initialization(self) -> None:
        """Test generator initialization."""
        from form32_docling.config import Config
        generator = Form68Generator(Config())
        assert generator.font_name == "Helvetica-Bold"
        assert generator.font_size == 12
        assert generator.output_directory is None

    def test_mapping(self, sample_patient_info: PatientInfo) -> None:
        """Test patient info mapping to fields."""
        from form32_docling.config import Config
        generator = Form68Generator(Config())
        fields = generator._map_patient_info_to_fields(sample_patient_info)

        assert fields["patient_name"] == "John Doe"
        assert fields["patient_ssn"] == "123-45-6789"
        assert fields["claim_number"] == "CLM12345"
        assert fields["exam_date"] == "01/15/2024"


class TestForm69Generator:
    """Tests for Form69Generator."""

    def test_initialization(self) -> None:
        """Test generator initialization."""
        from form32_docling.config import Config
        generator = Form69Generator(Config())
        assert generator.font_name == "Helvetica-Bold"
        assert generator.font_size == 8

    def test_mapping(self, sample_patient_info: PatientInfo) -> None:
        """Test patient info mapping to fields."""
        from form32_docling.config import Config
        generator = Form69Generator(Config())
        fields = generator._map_patient_info_to_fields(sample_patient_info)

        assert fields["4 Injured Employees Name First Middle Last"] == "John Doe"
        assert fields["6 Social Security Number"] == "XXX-XX-6789"
        # Form 69 has more specific fields like doctor names
        assert fields["9 Certifying Doctors Name and License Type"] == "Dr. Smith, D.C."
        assert fields["2 Employers Name"] == "Test Employer"


class TestForm73Generator:
    """Tests for Form73Generator."""

    def test_initialization(self) -> None:
        """Test generator initialization."""
        from form32_docling.config import Config
        generator = Form73Generator(Config())
        assert generator.font_name == "Helvetica-Bold"
        assert generator.font_size == 8

    def test_clean_facility_name(self) -> None:
        """Test facility name extraction."""
        from form32_docling.forms.form73_generator import _clean_facility_name

        result = _clean_facility_name("Test Clinic, 123 Main St, Austin, TX")
        assert result == "Test Clinic"

    def test_clean_facility_name_none(self) -> None:
        """Test facility name extraction with None."""
        from form32_docling.forms.form73_generator import _clean_facility_name

        result = _clean_facility_name(None)
        assert result == ""

    def test_calculate_discharge_time(self) -> None:
        """Test discharge time calculation."""
        from form32_docling.forms.form73_generator import _calculate_discharge_time

        result = _calculate_discharge_time("10:00 AM")
        assert result == "10:30 AM"

    def test_calculate_discharge_time_pm(self) -> None:
        """Test discharge time calculation with PM."""
        from form32_docling.forms.form73_generator import _calculate_discharge_time

        result = _calculate_discharge_time("11:30 AM")
        assert result == "12:00 PM"

    def test_calculate_discharge_time_none(self) -> None:
        """Test discharge time calculation with None."""
        from form32_docling.forms.form73_generator import _calculate_discharge_time

        result = _calculate_discharge_time(None)
        assert result == ""


class TestFormGenerationController:
    """Tests for FormGenerationController."""

    def test_initialization(self, sample_patient_info: PatientInfo) -> None:
        """Test controller initialization."""
        controller = FormGenerationController(sample_patient_info)
        assert controller.patient_info == sample_patient_info
        assert len(controller.generated_forms) == 0

    def test_determine_required_forms_with_c(
        self, sample_patient_info: PatientInfo
    ) -> None:
        """Test form determination with box C checked."""
        controller = FormGenerationController(sample_patient_info)
        required = controller._determine_required_forms()

        assert "Form68" in required
        assert "Form69" in required
        assert "Form73" in required  # box E is also checked

    def test_determine_required_forms_only_69(self) -> None:
        """Test form determination with no boxes checked."""
        info = PatientInfo(
            patient_name="Test",
            exam_date="01/01/2024",
            exam_location="Test",
        )
        controller = FormGenerationController(info)
        required = controller._determine_required_forms()

        assert "Form68" not in required
        assert "Form69" in required
        assert "Form73" not in required

