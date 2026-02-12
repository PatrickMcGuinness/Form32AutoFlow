"""Tests for DWC-073 Section I field mapping."""

from form32_docling.config import Config
from form32_docling.forms.form73_generator import Form73Generator
from form32_docling.models import PatientInfo


def test_section_i_general_info_maps_12_fields() -> None:
    """Verify Section I mapping includes all general information fields."""
    generator = Form73Generator(Config())
    info = PatientInfo(
        patient_name="John Doe",
        date_of_injury="06/15/2023",
        employee_ssn="123-45-6789",
        extent_of_injury="Low back strain after lifting",
        doctor_name="Dr. Smith",
        doctor_license_type="D.C.",
        exam_location="Test Clinic, 123 Main St, Austin, TX 78701",
        doctor_phone="512.555.1234",
        doctor_fax="512.555.5678",
        doctor_address="456 Oak Ave, Austin, TX 78702",
        employer_name="Test Employer",
        employer_phone="512.555.2222",
        insurance_carrier="ABC Insurance",
        adjuster_fax="512.555.9999",
        adjuster_email="adjuster@example.com",
    )

    fields = generator._map_section_i_general_info_fields(info)

    assert len(fields) == 13  # 1-12 plus 5a/5b split
    assert fields["1.  Injured Employee's Name"] == "John Doe"
    assert fields["2.  Date of Injury"] == "06/15/2023"
    assert fields["3.  Social Security Number"] == "6789"
    assert fields["4.  Employee's Description of Injury/Accident"] == "Low back strain after lifting"
    assert fields["5a.  Doctor's/Delegating Doctor's Name and Degree"] == "Dr. Smith, D.C."
    assert fields["5b.  PA/APRN Name"] == ""
    assert fields["6.  Clinic/Facility Name"] == "Test Clinic"
    assert fields["7.  Clinic/Facility/Doctor Phone & Fax"] == "512.555.1234 / 512.555.5678"
    assert fields["8.  Clinic/Facility/Doctor Address (street address)"] == "456 Oak Ave, Austin, TX 78702"
    assert fields["9.  Employer's Name"] == "Test Employer"
    assert fields["10.  Employer's Fax Number or E-mail Address"] == "512.555.2222"
    assert fields["11.  Insurance Carrier"] == "ABC Insurance"
    assert fields["12.  Carrier's Fax Number or E-mail Address"] == "512.555.9999"
