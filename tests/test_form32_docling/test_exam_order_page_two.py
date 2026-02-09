"""Unit tests for Exam Order Page Two extraction."""


from form32_docling.config.form32_templates import (
    FIELD_TO_ATTRIBUTE_MAP,
    exam_order_page_two_template,
)
from form32_docling.models.patient_info import (
    Form32Data,
    InsuranceBillingContact,
    PatientInfo,
)


class TestExamOrderPageTwoTemplate:
    """Tests for the exam_order_page_two_template."""

    def test_template_exists(self) -> None:
        """Verify template is defined."""
        assert exam_order_page_two_template is not None
        assert isinstance(exam_order_page_two_template, dict)

    def test_template_contains_exam_fields(self) -> None:
        """Verify template contains exam scheduling fields."""
        assert "Exam date" in exam_order_page_two_template
        assert "Exam time" in exam_order_page_two_template
        assert "Exam location" in exam_order_page_two_template
        assert "Exam location address" in exam_order_page_two_template

    def test_template_contains_doctor_fields(self) -> None:
        """Verify template contains designated doctor fields."""
        assert "Designated doctor name" in exam_order_page_two_template
        assert "Designated doctor license" in exam_order_page_two_template
        assert "Designated doctor phone" in exam_order_page_two_template
        assert "Designated doctor fax" in exam_order_page_two_template

    def test_template_contains_insurance_billing_fields(self) -> None:
        """Verify template contains insurance billing contact fields."""
        assert "DD assignment number" in exam_order_page_two_template
        assert "Insurance business name" in exam_order_page_two_template
        assert "Insurance mailing address" in exam_order_page_two_template
        assert "Insurance phone number" in exam_order_page_two_template
        assert "Insurance fax number" in exam_order_page_two_template
        assert "Insurance email address" in exam_order_page_two_template

    def test_template_contains_recipients_field(self) -> None:
        """Verify template contains order recipients field."""
        assert "Sent to names" in exam_order_page_two_template


class TestExamOrderPageTwoFieldMappings:
    """Tests for field mappings in FIELD_TO_ATTRIBUTE_MAP."""

    def test_exam_field_mappings_exist(self) -> None:
        """Verify exam field mappings exist."""
        assert FIELD_TO_ATTRIBUTE_MAP.get("Exam date") == "exam_date"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Exam time") == "exam_time"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Exam location") == "exam_location"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Exam location address") == "exam_location_full"

    def test_doctor_field_mappings_exist(self) -> None:
        """Verify designated doctor field mappings exist."""
        assert FIELD_TO_ATTRIBUTE_MAP.get("Designated doctor name") == "doctor_name"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Designated doctor license") == "doctor_license_number"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Designated doctor phone") == "doctor_phone"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Designated doctor fax") == "doctor_fax"

    def test_insurance_billing_field_mappings_exist(self) -> None:
        """Verify insurance billing field mappings exist."""
        assert FIELD_TO_ATTRIBUTE_MAP.get("DD assignment number") == "dd_assignment_number"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Insurance business name") == "insurance_billing_name"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Insurance mailing address") == "insurance_billing_address"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Insurance phone number") == "insurance_billing_phone"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Insurance fax number") == "insurance_billing_fax"
        assert FIELD_TO_ATTRIBUTE_MAP.get("Insurance email address") == "insurance_billing_email"

    def test_recipients_field_mapping_exists(self) -> None:
        """Verify order recipients field mapping exists."""
        assert FIELD_TO_ATTRIBUTE_MAP.get("Sent to names") == "order_recipients"


class TestInsuranceBillingContactModel:
    """Tests for the InsuranceBillingContact Pydantic model."""

    def test_model_creation_with_defaults(self) -> None:
        """Verify model can be created with default values."""
        contact = InsuranceBillingContact()
        assert contact.business_name is None
        assert contact.mailing_address is None
        assert contact.phone is None
        assert contact.fax is None
        assert contact.email is None
        assert contact.dd_assignment_number is None

    def test_model_creation_with_values(self) -> None:
        """Verify model can be created with specific values."""
        contact = InsuranceBillingContact(
            business_name="A.I.U. Insurance Company",
            mailing_address="1271 Avenue of the Americas, New York, NY 10020-1300",
            phone="1.619.688.3701",
            fax=None,
            email="robert.kinsman@aig.com",
            dd_assignment_number="24242689DD02",
        )
        assert contact.business_name == "A.I.U. Insurance Company"
        assert contact.mailing_address == "1271 Avenue of the Americas, New York, NY 10020-1300"
        assert contact.phone == "1.619.688.3701"
        assert contact.fax is None
        assert contact.email == "robert.kinsman@aig.com"
        assert contact.dd_assignment_number == "24242689DD02"

    def test_model_serialization(self) -> None:
        """Verify model can be serialized to dict."""
        contact = InsuranceBillingContact(
            business_name="Test Insurance",
            dd_assignment_number="12345DD01",
        )
        data = contact.model_dump()
        assert data["business_name"] == "Test Insurance"
        assert data["dd_assignment_number"] == "12345DD01"


class TestForm32DataWithBillingContact:
    """Tests for Form32Data with insurance_billing field."""

    def test_form32data_has_insurance_billing(self) -> None:
        """Verify Form32Data has insurance_billing field."""
        data = Form32Data()
        assert hasattr(data, "insurance_billing")
        assert isinstance(data.insurance_billing, InsuranceBillingContact)

    def test_form32data_has_order_recipients(self) -> None:
        """Verify Form32Data has order_recipients field."""
        data = Form32Data()
        assert hasattr(data, "order_recipients")
        assert data.order_recipients is None

    def test_form32data_with_billing_values(self) -> None:
        """Verify Form32Data can be created with billing values."""
        data = Form32Data(
            insurance_billing=InsuranceBillingContact(
                business_name="Test Carrier",
                dd_assignment_number="99999DD99",
            ),
            order_recipients="John Doe Jane Smith",
        )
        assert data.insurance_billing.business_name == "Test Carrier"
        assert data.insurance_billing.dd_assignment_number == "99999DD99"
        assert data.order_recipients == "John Doe Jane Smith"


class TestPatientInfoWithBillingContact:
    """Tests for PatientInfo with billing contact fields."""

    def test_patient_info_has_billing_fields(self) -> None:
        """Verify PatientInfo has billing contact fields."""
        info = PatientInfo()
        assert hasattr(info, "dd_assignment_number")
        assert hasattr(info, "insurance_billing_name")
        assert hasattr(info, "insurance_billing_address")
        assert hasattr(info, "insurance_billing_phone")
        assert hasattr(info, "insurance_billing_fax")
        assert hasattr(info, "insurance_billing_email")
        assert hasattr(info, "order_recipients")

    def test_patient_info_billing_fields_defaults(self) -> None:
        """Verify PatientInfo billing fields default to None."""
        info = PatientInfo()
        assert info.dd_assignment_number is None
        assert info.insurance_billing_name is None
        assert info.insurance_billing_address is None
        assert info.insurance_billing_phone is None
        assert info.insurance_billing_fax is None
        assert info.insurance_billing_email is None
        assert info.order_recipients is None

    def test_patient_info_with_billing_values(self) -> None:
        """Verify PatientInfo can be created with billing values."""
        info = PatientInfo(
            patient_name="Leroy Myers, Jr.",
            dd_assignment_number="24242689DD02",
            insurance_billing_name="A.I.U. Insurance Company",
            insurance_billing_address="1271 Avenue of the Americas, New York, NY 10020-1300",
            insurance_billing_phone="1.619.688.3701",
            insurance_billing_email="robert.kinsman@aig.com",
            order_recipients="MELISSA M KEMPF LEROY MYERS JOHN AUBRY DAVIS AIU Insurance Co",
        )
        assert info.patient_name == "Leroy Myers, Jr."
        assert info.dd_assignment_number == "24242689DD02"
        assert info.insurance_billing_name == "A.I.U. Insurance Company"
        assert info.order_recipients == "MELISSA M KEMPF LEROY MYERS JOHN AUBRY DAVIS AIU Insurance Co"


class TestModelConversions:
    """Tests for conversions between Form32Data and PatientInfo."""

    def test_form32data_from_patient_info_with_billing(self) -> None:
        """Verify Form32Data.from_patient_info includes billing fields."""
        info = PatientInfo(
            patient_name="Test Patient",
            dd_assignment_number="12345DD01",
            insurance_billing_name="Test Insurance",
            insurance_billing_address="123 Test St",
            insurance_billing_phone="555-1234",
            insurance_billing_fax="555-5678",
            insurance_billing_email="test@insurance.com",
            order_recipients="Recipient1 Recipient2",
        )

        data = Form32Data.from_patient_info(info)

        assert data.insurance_billing.dd_assignment_number == "12345DD01"
        assert data.insurance_billing.business_name == "Test Insurance"
        assert data.insurance_billing.mailing_address == "123 Test St"
        assert data.insurance_billing.phone == "555-1234"
        assert data.insurance_billing.fax == "555-5678"
        assert data.insurance_billing.email == "test@insurance.com"
        assert data.order_recipients == "Recipient1 Recipient2"

    def test_patient_info_from_form32data_with_billing(self) -> None:
        """Verify PatientInfo.from_form32_data includes billing fields."""
        data = Form32Data(
            insurance_billing=InsuranceBillingContact(
                dd_assignment_number="67890DD02",
                business_name="Another Insurance",
                mailing_address="456 Another Ave",
                phone="555-9876",
                email="another@insurance.com",
            ),
            order_recipients="Recipient3 Recipient4",
        )

        info = PatientInfo.from_form32_data(data)

        assert info.dd_assignment_number == "67890DD02"
        assert info.insurance_billing_name == "Another Insurance"
        assert info.insurance_billing_address == "456 Another Ave"
        assert info.insurance_billing_phone == "555-9876"
        assert info.insurance_billing_email == "another@insurance.com"
        assert info.order_recipients == "Recipient3 Recipient4"

    def test_roundtrip_conversion(self) -> None:
        """Verify roundtrip conversion preserves billing data."""
        original = PatientInfo(
            patient_name="Roundtrip Test",
            dd_assignment_number="11111DD11",
            insurance_billing_name="Roundtrip Insurance",
            insurance_billing_address="111 Roundtrip Way",
            insurance_billing_phone="555-1111",
            insurance_billing_fax="555-2222",
            insurance_billing_email="roundtrip@insurance.com",
            order_recipients="R1 R2 R3",
        )

        # Convert to Form32Data and back
        data = Form32Data.from_patient_info(original)
        result = PatientInfo.from_form32_data(data)

        assert result.dd_assignment_number == original.dd_assignment_number
        assert result.insurance_billing_name == original.insurance_billing_name
        assert result.insurance_billing_address == original.insurance_billing_address
        assert result.insurance_billing_phone == original.insurance_billing_phone
        assert result.insurance_billing_fax == original.insurance_billing_fax
        assert result.insurance_billing_email == original.insurance_billing_email
        assert result.order_recipients == original.order_recipients
