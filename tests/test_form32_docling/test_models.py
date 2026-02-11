"""Tests for form32_docling data models."""


from form32_docling.models import (
    BodyAreaFlags,
    EmployeeInfo,
    ExamInfo,
    Form32Data,
    InsuranceInfo,
    PatientInfo,
    PurposeFlags,
)


class TestEmployeeInfo:
    """Tests for EmployeeInfo model."""

    def test_default_values(self) -> None:
        """Test that all fields have None defaults."""
        info = EmployeeInfo()
        assert info.patient_name is None
        assert info.ssn is None
        assert info.address is None

    def test_with_values(self) -> None:
        """Test setting field values."""
        info = EmployeeInfo(
            patient_name="John Doe",
            ssn="123-45-6789",
            date_of_birth="01/15/1980",
        )
        assert info.patient_name == "John Doe"
        assert info.ssn == "123-45-6789"
        assert info.date_of_birth == "01/15/1980"


class TestInsuranceInfo:
    """Tests for InsuranceInfo model."""

    def test_boolean_defaults(self) -> None:
        """Test boolean fields default to False."""
        info = InsuranceInfo()
        assert info.has_certified_network is False
        assert info.has_political_subdivision is False

    def test_set_network_flags(self) -> None:
        """Test setting network flags."""
        info = InsuranceInfo(
            carrier_name="ABC Insurance",
            has_certified_network=True,
            health_plan_name="Test Network",
        )
        assert info.has_certified_network is True
        assert info.health_plan_name == "Test Network"


class TestBodyAreaFlags:
    """Tests for BodyAreaFlags model."""

    def test_all_defaults_false(self) -> None:
        """Test all body area flags default to False."""
        flags = BodyAreaFlags()
        assert flags.spine is False
        assert flags.upper_extremities is False
        assert flags.burns is False
        assert flags.mental_disorders is False

    def test_set_multiple_flags(self) -> None:
        """Test setting multiple body area flags."""
        flags = BodyAreaFlags(
            spine=True,
            upper_extremities=True,
            burns=False,
        )
        assert flags.spine is True
        assert flags.upper_extremities is True
        assert flags.burns is False


class TestPurposeFlags:
    """Tests for PurposeFlags model."""

    def test_default_checkboxes(self) -> None:
        """Test purpose checkbox defaults."""
        flags = PurposeFlags()
        assert flags.box_a_checked is False
        assert flags.box_b_checked is False
        assert flags.box_c_checked is False

    def test_with_dates(self) -> None:
        """Test purpose flags with associated dates."""
        flags = PurposeFlags(
            box_a_checked=True,
            mmi_date="01/15/2024",
            box_e_checked=True,
            rtw_from_date="01/01/2024",
            rtw_to_date="01/31/2024",
        )
        assert flags.box_a_checked is True
        assert flags.mmi_date == "01/15/2024"
        assert flags.box_e_checked is True


class TestForm32Data:
    """Tests for Form32Data composite model."""

    def test_default_structure(self) -> None:
        """Test Form32Data has proper default sub-models."""
        data = Form32Data()
        assert isinstance(data.employee, EmployeeInfo)
        assert isinstance(data.insurance, InsuranceInfo)
        assert isinstance(data.body_areas, BodyAreaFlags)
        assert isinstance(data.purpose, PurposeFlags)

    def test_is_valid_missing_fields(self) -> None:
        """Test is_valid returns False when required fields missing."""
        data = Form32Data()
        assert data.is_valid() is False

    def test_is_valid_with_required_fields(self) -> None:
        """Test is_valid returns True when required fields present."""
        data = Form32Data(
            employee=EmployeeInfo(patient_name="John Doe"),
            exam=ExamInfo(date="01/15/2024", location="Test Clinic"),
        )
        assert data.is_valid() is True

    def test_get_formatted_exam_date(self) -> None:
        """Test exam date formatting."""
        data = Form32Data(
            exam=ExamInfo(date="01/15/2024"),
        )
        formatted = data.get_formatted_exam_date()
        assert formatted == "2024-01-15"

    def test_get_formatted_exam_date_empty(self) -> None:
        """Test exam date formatting when date is None."""
        data = Form32Data()
        assert data.get_formatted_exam_date() == ""


    def test_from_patient_info(self) -> None:
        """Test conversion from PatientInfo to Form32Data."""
        info = PatientInfo(
            patient_name="John Doe",
            employee_ssn="123-45-6789",
            exam_date="01/15/2024",
            exam_location="Test Clinic",
            has_certified_network=True,
            body_area_spine=True,
            purpose_box_c_checked=True,
        )

        data = Form32Data.from_patient_info(info)

        assert data.employee.patient_name == "John Doe"
        assert data.employee.ssn == "123-45-6789"
        assert data.exam.date == "01/15/2024"
        assert data.exam.location == "Test Clinic"
        assert data.insurance.has_certified_network is True
        assert data.body_areas.spine is True
        assert data.purpose.box_c_checked is True


class TestPatientInfo:
    """Tests for PatientInfo flat model."""

    def test_default_values(self) -> None:
        """Test PatientInfo defaults."""
        info = PatientInfo()
        assert info.patient_name is None
        assert info.exam_date is None
        assert info.has_certified_network is False

    def test_ssn_normalization(self) -> None:
        """Test SSN gets normalized on input."""
        info = PatientInfo(employee_ssn="123456789")
        assert info.employee_ssn == "123-45-6789"

    def test_ssn_already_formatted(self) -> None:
        """Test SSN that's already formatted stays the same."""
        info = PatientInfo(employee_ssn="123-45-6789")
        assert info.employee_ssn == "123-45-6789"

    def test_is_valid(self) -> None:
        """Test is_valid method."""
        info = PatientInfo(
            patient_name="John Doe",
            exam_date="01/15/2024",
            exam_location="Test Clinic",
        )
        assert info.is_valid() is True

    def test_from_form32_data(self) -> None:
        """Test conversion from Form32Data to PatientInfo."""
        data = Form32Data(
            employee=EmployeeInfo(
                patient_name="John Doe",
                ssn="123-45-6789",
            ),
            insurance=InsuranceInfo(
                carrier_name="ABC Insurance",
                has_certified_network=True,
            ),
            exam=ExamInfo(
                date="01/15/2024",
                location="Test Clinic",
            ),
            body_areas=BodyAreaFlags(spine=True),
            purpose=PurposeFlags(box_c_checked=True),
        )

        info = PatientInfo.from_form32_data(data)

        assert info.patient_name == "John Doe"
        assert info.employee_ssn == "123-45-6789"
        assert info.insurance_carrier == "ABC Insurance"
        assert info.has_certified_network is True
        assert info.exam_date == "01/15/2024"
        assert info.body_area_spine is True
        assert info.purpose_box_c_checked is True
