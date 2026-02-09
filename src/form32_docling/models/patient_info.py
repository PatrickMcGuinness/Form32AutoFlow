"""Pydantic data models for Form 32 extraction.

These models leverage Pydantic's Field descriptions for schema-based
extraction with docling, providing type validation and documentation.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class InjuryEvaluation(BaseModel):
    """Evaluation of an identified injury or condition."""

    condition_text: str | None = Field(default=None, description="The injury or condition text")
    is_substantial_factor: bool | None = Field(
        default=None,
        description="Whether the incident was a substantial factor for this condition",
    )
    diagnosis_codes: list[str] = Field(
        default_factory=lambda: ["", "", "", ""],
        description="Up to 4 diagnosis codes for this condition",
    )


class EmployeeInfo(BaseModel):
    """Schema for injured employee information (Part 1)."""

    patient_name: str | None = Field(
        default=None, description="Employee's full name"
    )
    ssn: str | None = Field(
        default=None, description="Employee's Social Security Number"
    )
    date_of_birth: str | None = Field(
        default=None, description="Employee's date of birth"
    )
    address: str | None = Field(
        default=None, description="Employee's street address"
    )
    county: str | None = Field(default=None, description="Employee's county")
    phone_primary: str | None = Field(
        default=None, description="Employee's primary phone number"
    )
    phone_alternate: str | None = Field(
        default=None, description="Employee's alternate phone number"
    )
    date_of_injury: str | None = Field(
        default=None, description="Date of injury"
    )


class RepresentativeInfo(BaseModel):
    """Schema for employee representative information."""

    name: str | None = Field(default=None, description="Representative's name")
    phone: str | None = Field(
        default=None, description="Representative's phone number"
    )
    email: str | None = Field(
        default=None, description="Representative's email address"
    )
    fax: str | None = Field(
        default=None, description="Representative's fax number"
    )


class EmployerInfo(BaseModel):
    """Schema for employer information."""

    name: str | None = Field(default=None, description="Employer's name")
    phone: str | None = Field(
        default=None, description="Employer's phone number"
    )
    address: str | None = Field(
        default=None, description="Employer's address"
    )


class InsuranceInfo(BaseModel):
    """Schema for insurance carrier information (Part 2)."""

    carrier_name: str | None = Field(
        default=None, description="Insurance carrier name"
    )
    carrier_address: str | None = Field(
        default=None, description="Insurance carrier address"
    )
    adjuster_name: str | None = Field(
        default=None, description="Adjuster's name"
    )
    adjuster_phone: str | None = Field(
        default=None, description="Adjuster's phone number"
    )
    adjuster_email: str | None = Field(
        default=None, description="Adjuster's email address"
    )
    adjuster_fax: str | None = Field(
        default=None, description="Adjuster's fax number"
    )
    claim_number: str | None = Field(
        default=None, description="Insurance carrier claim number"
    )
    dwc_number: str | None = Field(
        default=None, description="DWC claim number"
    )
    has_certified_network: bool = Field(
        default=False, description="Certified network coverage (Q22)"
    )
    has_political_subdivision: bool = Field(
        default=False, description="Political subdivision coverage (Q23)"
    )
    health_plan_name: str | None = Field(
        default=None, description="Health plan name if applicable"
    )


class InsuranceBillingContact(BaseModel):
    """Schema for insurance carrier billing contact from exam order page two."""

    business_name: str | None = Field(
        default=None, description="Insurance carrier business name for billing"
    )
    mailing_address: str | None = Field(
        default=None, description="Insurance carrier mailing address"
    )
    phone: str | None = Field(
        default=None, description="Insurance carrier billing phone"
    )
    fax: str | None = Field(
        default=None, description="Insurance carrier billing fax"
    )
    email: str | None = Field(
        default=None, description="Insurance carrier billing email"
    )
    dd_assignment_number: str | None = Field(
        default=None, description="DD assignment number"
    )


class TreatingDoctorInfo(BaseModel):
    """Schema for treating doctor information (Part 3)."""

    name: str | None = Field(default=None, description="Treating doctor's name")
    phone: str | None = Field(
        default=None, description="Treating doctor's phone number"
    )
    fax: str | None = Field(
        default=None, description="Treating doctor's fax number"
    )
    address: str | None = Field(
        default=None, description="Treating doctor's address"
    )
    license_number: str | None = Field(
        default=None, description="Treating doctor's license number"
    )
    license_type: str | None = Field(
        default=None, description="Treating doctor's license type (MD, DC, DO)"
    )
    license_jurisdiction: str | None = Field(
        default=None, description="Treating doctor's license jurisdiction"
    )


class DesignatedDoctorInfo(BaseModel):
    """Schema for designated doctor / examiner information."""

    name: str | None = Field(
        default=None, description="Designated doctor's name"
    )
    phone: str | None = Field(
        default=None, description="Designated doctor's phone number"
    )
    fax: str | None = Field(
        default=None, description="Designated doctor's fax number"
    )
    address: str | None = Field(
        default=None, description="Designated doctor's address"
    )
    license_number: str | None = Field(
        default=None, description="Designated doctor's license number"
    )
    license_type: str | None = Field(
        default=None, description="Designated doctor's license type"
    )
    license_jurisdiction: str | None = Field(
        default=None, description="Designated doctor's license jurisdiction"
    )


class ExamInfo(BaseModel):
    """Schema for examination information."""

    date: str | None = Field(default=None, description="Date of examination")
    time: str | None = Field(default=None, description="Time of examination")
    location: str | None = Field(
        default=None, description="Examination location/facility"
    )
    location_full: str | None = Field(
        default=None, description="Full examination address"
    )
    location_city: str | None = Field(
        default=None, description="Examination city"
    )


class BodyAreaFlags(BaseModel):
    """Schema for body area checkboxes (Part 4)."""

    spine: bool = Field(default=False, description="Spine affected")
    upper_extremities: bool = Field(
        default=False, description="Upper extremities affected"
    )
    lower_extremities: bool = Field(
        default=False, description="Lower extremities affected"
    )
    teeth_jaw: bool = Field(default=False, description="Teeth/jaw affected")
    eyes: bool = Field(default=False, description="Eyes affected")
    other_systems: bool = Field(
        default=False, description="Other systems affected"
    )
    brain_injury: bool = Field(
        default=False, description="Traumatic brain injury"
    )
    spinal_cord: bool = Field(
        default=False, description="Spinal cord injury"
    )
    burns: bool = Field(default=False, description="Burns")
    fractures: bool = Field(default=False, description="Fractures/dislocations")
    infectious: bool = Field(default=False, description="Infectious disease")
    regional_pain: bool = Field(
        default=False, description="Complex regional pain syndrome"
    )
    chemical_exposure: bool = Field(
        default=False, description="Chemical exposure"
    )
    cardiovascular: bool = Field(
        default=False, description="Cardiovascular conditions"
    )
    mental_disorders: bool = Field(default=False, description="Mental disorders")


class PurposeFlags(BaseModel):
    """Schema for purpose of examination checkboxes (Field 31)."""

    box_a_checked: bool = Field(
        default=False, description="Box A: Maximum medical improvement"
    )
    mmi_date: str | None = Field(default=None, description="MMI date for Box A")
    box_b_checked: bool = Field(
        default=False, description="Box B: Impairment rating"
    )
    ir_mmi_date: str | None = Field(
        default=None, description="MMI date for impairment rating"
    )
    box_c_checked: bool = Field(
        default=False, description="Box C: Extent of injury"
    )
    box_d_checked: bool = Field(
        default=False, description="Box D: Ability to work"
    )
    disability_from_date: str | None = Field(
        default=None, description="Disability period start date"
    )
    disability_to_date: str | None = Field(
        default=None, description="Disability period end date"
    )
    box_e_checked: bool = Field(
        default=False, description="Box E: Return to work"
    )
    rtw_from_date: str | None = Field(
        default=None, description="Return to work period start date"
    )
    rtw_to_date: str | None = Field(
        default=None, description="Return to work period end date"
    )
    box_f_checked: bool = Field(
        default=False, description="Box F: Supplemental income benefits"
    )
    sib_from_date: str | None = Field(
        default=None, description="SIB period start date"
    )
    sib_to_date: str | None = Field(
        default=None, description="SIB period end date"
    )
    box_g_checked: bool = Field(
        default=False, description="Box G: Other examination"
    )


class NetworkFlags(BaseModel):
    """Schema for network-related checkboxes (Field 32)."""

    dwc024_yes_checked: bool = Field(
        default=False, description="DWC-024 form received - Yes"
    )
    dwc024_no_checked: bool = Field(
        default=False, description="DWC-024 form received - No"
    )


class Form32Data(BaseModel):
    """Complete Form 32 extracted data model.

    This is the main model aggregating all sub-models for structured
    extraction from Form 32 PDFs using docling.
    """

    employee: EmployeeInfo = Field(default_factory=EmployeeInfo)
    representative: RepresentativeInfo = Field(default_factory=RepresentativeInfo)
    employer: EmployerInfo = Field(default_factory=EmployerInfo)
    insurance: InsuranceInfo = Field(default_factory=InsuranceInfo)
    treating_doctor: TreatingDoctorInfo = Field(default_factory=TreatingDoctorInfo)
    designated_doctor: DesignatedDoctorInfo = Field(
        default_factory=DesignatedDoctorInfo
    )
    exam: ExamInfo = Field(default_factory=ExamInfo)
    body_areas: BodyAreaFlags = Field(default_factory=BodyAreaFlags)
    purpose: PurposeFlags = Field(default_factory=PurposeFlags)
    network: NetworkFlags = Field(default_factory=NetworkFlags)
    extent_of_injury: str | None = Field(
        default=None, description="Extent of injury description"
    )
    injury_evaluations: list[InjuryEvaluation] = Field(
        default_factory=list, description="Doctor's evaluation of identified injuries"
    )
    # Insurance Billing Contact (from Exam Order Page Two)
    insurance_billing: InsuranceBillingContact = Field(
        default_factory=InsuranceBillingContact,
        description="Insurance billing contact from exam order page two"
    )
    order_recipients: str | None = Field(
        default=None, description="List of recipients who received the order"
    )

    @classmethod
    def from_patient_info(cls, info: PatientInfo) -> Form32Data:
        """Convert flat PatientInfo back to structured Form32Data."""
        return cls(
            employee=EmployeeInfo(
                patient_name=info.patient_name,
                ssn=info.ssn,
                date_of_birth=info.employee_date_of_birth,
                address=info.employee_address,
                county=info.employee_county,
                phone_primary=info.employee_primary_phone,
                phone_alternate=info.employee_alternate_phone,
                date_of_injury=info.date_of_injury,
            ),
            representative=RepresentativeInfo(
                name=info.representative_name,
                phone=info.representative_phone,
                email=info.representative_email,
                fax=info.representative_fax,
            ),
            employer=EmployerInfo(
                name=info.employer_name,
                phone=info.employer_phone,
                address=info.employer_address,
            ),
            insurance=InsuranceInfo(
                carrier_name=info.insurance_carrier,
                carrier_address=info.carrier_address,
                adjuster_name=info.adjuster_name,
                adjuster_phone=info.adjuster_phone,
                adjuster_email=info.adjuster_email,
                adjuster_fax=info.adjuster_fax,
                claim_number=info.claim_number,
                dwc_number=info.dwc_number,
                has_certified_network=info.has_certified_network,
                has_political_subdivision=info.has_political_subdivision,
                health_plan_name=info.health_plan_name,
            ),
            treating_doctor=TreatingDoctorInfo(
                name=info.treating_doctor_name,
                phone=info.treating_doctor_phone,
                fax=info.treating_doctor_fax,
                address=info.treating_doctor_address,
                license_number=info.treating_doctor_license_number,
                license_type=info.treating_doctor_license_type,
                license_jurisdiction=info.treating_doctor_license_jurisdiction,
            ),
            designated_doctor=DesignatedDoctorInfo(
                name=info.doctor_name,
                phone=info.doctor_phone,
                fax=info.doctor_fax,
                address=info.doctor_address,
                license_number=info.doctor_license_number,
                license_type=info.doctor_license_type,
                license_jurisdiction=info.doctor_license_jurisdiction,
            ),
            exam=ExamInfo(
                date=info.exam_date,
                time=info.exam_time,
                location=info.exam_location,
                location_full=info.exam_location_full,
                location_city=info.exam_location_city,
            ),
            body_areas=BodyAreaFlags(
                spine=info.body_area_spine,
                upper_extremities=info.body_area_upper_extremities,
                lower_extremities=info.body_area_lower_extremities,
                teeth_jaw=info.body_area_teeth_jaw,
                eyes=info.body_area_eyes,
                other_systems=info.body_area_other_systems,
                brain_injury=info.body_area_brain_injury,
                spinal_cord=info.body_area_spinal_cord,
                burns=info.body_area_burns,
                fractures=info.body_area_fractures,
                infectious=info.body_area_infectious,
                regional_pain=info.body_area_regional_pain,
                chemical_exposure=info.body_area_chemical_exposure,
                cardiovascular=info.body_area_cardiovascular,
                mental_disorders=info.body_area_mental_disorders,
            ),
            purpose=PurposeFlags(
                box_a_checked=info.purpose_box_a_checked,
                mmi_date=info.purpose_mmi_date,
                box_b_checked=info.purpose_box_b_checked,
                ir_mmi_date=info.purpose_ir_mmi_date,
                box_c_checked=info.purpose_box_c_checked,
                box_d_checked=info.purpose_box_d_checked,
                disability_from_date=info.purpose_disability_from_date,
                disability_to_date=info.purpose_disability_to_date,
                box_e_checked=info.purpose_box_e_checked,
                rtw_from_date=info.purpose_rtw_from_date,
                rtw_to_date=info.purpose_rtw_to_date,
                box_f_checked=info.purpose_box_f_checked,
                sib_from_date=info.purpose_sib_from_date,
                sib_to_date=info.purpose_sib_to_date,
                box_g_checked=info.purpose_box_g_checked,
            ),
            network=NetworkFlags(
                dwc024_yes_checked=info.dwc024_yes_checked,
                dwc024_no_checked=info.dwc024_no_checked,
            ),
            extent_of_injury=info.extent_of_injury,
            injury_evaluations=info.injury_evaluations,
            insurance_billing=InsuranceBillingContact(
                business_name=info.insurance_billing_name,
                mailing_address=info.insurance_billing_address,
                phone=info.insurance_billing_phone,
                fax=info.insurance_billing_fax,
                email=info.insurance_billing_email,
                dd_assignment_number=info.dd_assignment_number,
            ),
            order_recipients=info.order_recipients,
        )


    def is_valid(self) -> bool:
        """Check if required fields are present for form generation."""
        missing = []
        if not self.employee.patient_name:
            missing.append("patient_name")
        if not self.exam.date:
            missing.append("exam_date")
        if not self.exam.location:
            missing.append("exam_location")

        if missing:
            import logging
            logging.getLogger(__name__).warning(f"Patient record is incomplete: Missing {', '.join(missing)}")
            return False

        return True

    def get_formatted_exam_date(self) -> str:
        """Return exam date in YYYY-MM-DD format."""
        if not self.exam.date:
            return ""

        date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(self.exam.date, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return self.exam.date


class PatientInfo(BaseModel):
    """Flat model compatible with legacy form generators.

    This model provides backward compatibility with the existing form
    generator interfaces while leveraging Pydantic validation.
    """

    # Part 1. Injured employee information
    patient_name: str | None = None
    ssn: str | None = None
    employee_address: str | None = None
    employee_county: str | None = None
    employee_primary_phone: str | None = None
    employee_alternate_phone: str | None = None
    employee_date_of_birth: str | None = None
    date_of_injury: str | None = None
    representative_name: str | None = None
    representative_phone: str | None = None
    representative_email: str | None = None
    representative_fax: str | None = None
    employer_name: str | None = None
    employer_phone: str | None = None
    employer_address: str | None = None

    # Part 2. Insurance carrier information
    insurance_carrier: str | None = None
    carrier_address: str | None = None
    adjuster_name: str | None = None
    adjuster_email: str | None = None
    adjuster_phone: str | None = None
    adjuster_fax: str | None = None
    has_certified_network: bool = False
    has_political_subdivision: bool = False
    health_plan_name: str | None = None

    # Part 3. Treating doctor information
    treating_doctor_name: str | None = None
    treating_doctor_phone: str | None = None
    treating_doctor_address: str | None = None
    treating_doctor_fax: str | None = None
    treating_doctor_license_number: str | None = None
    treating_doctor_license_type: str | None = None
    treating_doctor_license_jurisdiction: str | None = None

    # Part 4. Body Areas
    body_area_spine: bool = False
    body_area_upper_extremities: bool = False
    body_area_lower_extremities: bool = False
    body_area_teeth_jaw: bool = False
    body_area_eyes: bool = False
    body_area_other_systems: bool = False
    body_area_brain_injury: bool = False
    body_area_spinal_cord: bool = False
    body_area_burns: bool = False
    body_area_fractures: bool = False
    body_area_infectious: bool = False
    body_area_regional_pain: bool = False
    body_area_chemical_exposure: bool = False
    body_area_cardiovascular: bool = False
    body_area_mental_disorders: bool = False

    # Part 5. Purpose of examination (Field 31)
    purpose_box_a_checked: bool = False
    purpose_mmi_date: str | None = None
    purpose_box_b_checked: bool = False
    purpose_ir_mmi_date: str | None = None
    purpose_box_c_checked: bool = False
    purpose_box_d_checked: bool = False
    purpose_disability_from_date: str | None = None
    purpose_disability_to_date: str | None = None
    purpose_box_e_checked: bool = False
    purpose_rtw_from_date: str | None = None
    purpose_rtw_to_date: str | None = None
    purpose_box_f_checked: bool = False
    purpose_sib_from_date: str | None = None
    purpose_sib_to_date: str | None = None
    purpose_box_g_checked: bool = False

    # Field 32
    dwc024_yes_checked: bool = False
    dwc024_no_checked: bool = False

    # Additional required fields
    dwc_number: str | None = None
    claim_number: str | None = None
    exam_date: str | None = None
    exam_time: str | None = None
    exam_location: str | None = None
    exam_location_full: str | None = None
    exam_location_city: str | None = None
    extent_of_injury: str | None = None
    doctor_name: str | None = None
    doctor_address: str | None = None
    doctor_license_number: str | None = None
    doctor_license_jurisdiction: str | None = None
    doctor_license_type: str | None = None
    doctor_phone: str | None = None
    doctor_fax: str | None = None

    # Insurance Billing Contact (from Exam Order Page Two)
    dd_assignment_number: str | None = None
    insurance_billing_name: str | None = None
    insurance_billing_address: str | None = None
    insurance_billing_phone: str | None = None
    insurance_billing_fax: str | None = None
    insurance_billing_email: str | None = None
    order_recipients: str | None = None

    # Doctor Edits / Clinical Data
    injury_evaluations: list[InjuryEvaluation] = []

    def is_valid(self) -> bool:
        """Check if required fields are present.

        Note: Relaxed to warning to allow GUI-based correction.
        """
        missing = []
        if not self.patient_name:
            missing.append("patient_name")
        if not self.exam_date:
            missing.append("exam_date")
        if not self.exam_location:
            missing.append("exam_location")

        if missing:
            import logging
            logging.getLogger(__name__).warning(f"PatientInfo is incomplete: Missing {', '.join(missing)}")

        return True

    def get_formatted_exam_date(self) -> str:
        """Return exam date in YYYY-MM-DD format."""
        if not self.exam_date:
            return ""

        date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(self.exam_date, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return self.exam_date

    @field_validator("ssn", mode="before")
    @classmethod
    def normalize_ssn(cls, v: str | None) -> str | None:
        """Normalize SSN format to XXX-XX-XXXX."""
        if not v:
            return None
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) == 9:
            return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
        return v

    @classmethod
    def from_form32_data(cls, data: Form32Data) -> PatientInfo:
        """Convert structured Form32Data to flat PatientInfo."""
        return cls(
            patient_name=data.employee.patient_name,
            ssn=data.employee.ssn,
            employee_address=data.employee.address,
            employee_county=data.employee.county,
            employee_primary_phone=data.employee.phone_primary,
            employee_alternate_phone=data.employee.phone_alternate,
            employee_date_of_birth=data.employee.date_of_birth,
            date_of_injury=data.employee.date_of_injury,
            representative_name=data.representative.name,
            representative_phone=data.representative.phone,
            representative_email=data.representative.email,
            representative_fax=data.representative.fax,
            employer_name=data.employer.name,
            employer_phone=data.employer.phone,
            employer_address=data.employer.address,
            insurance_carrier=data.insurance.carrier_name,
            carrier_address=data.insurance.carrier_address,
            adjuster_name=data.insurance.adjuster_name,
            adjuster_email=data.insurance.adjuster_email,
            adjuster_phone=data.insurance.adjuster_phone,
            adjuster_fax=data.insurance.adjuster_fax,
            has_certified_network=data.insurance.has_certified_network,
            has_political_subdivision=data.insurance.has_political_subdivision,
            health_plan_name=data.insurance.health_plan_name,
            treating_doctor_name=data.treating_doctor.name,
            treating_doctor_phone=data.treating_doctor.phone,
            treating_doctor_address=data.treating_doctor.address,
            treating_doctor_fax=data.treating_doctor.fax,
            treating_doctor_license_number=data.treating_doctor.license_number,
            treating_doctor_license_type=data.treating_doctor.license_type,
            treating_doctor_license_jurisdiction=data.treating_doctor.license_jurisdiction,
            body_area_spine=data.body_areas.spine,
            body_area_upper_extremities=data.body_areas.upper_extremities,
            body_area_lower_extremities=data.body_areas.lower_extremities,
            body_area_teeth_jaw=data.body_areas.teeth_jaw,
            body_area_eyes=data.body_areas.eyes,
            body_area_other_systems=data.body_areas.other_systems,
            body_area_brain_injury=data.body_areas.brain_injury,
            body_area_spinal_cord=data.body_areas.spinal_cord,
            body_area_burns=data.body_areas.burns,
            body_area_fractures=data.body_areas.fractures,
            body_area_infectious=data.body_areas.infectious,
            body_area_regional_pain=data.body_areas.regional_pain,
            body_area_chemical_exposure=data.body_areas.chemical_exposure,
            body_area_cardiovascular=data.body_areas.cardiovascular,
            body_area_mental_disorders=data.body_areas.mental_disorders,
            purpose_box_a_checked=data.purpose.box_a_checked,
            purpose_mmi_date=data.purpose.mmi_date,
            purpose_box_b_checked=data.purpose.box_b_checked,
            purpose_ir_mmi_date=data.purpose.ir_mmi_date,
            purpose_box_c_checked=data.purpose.box_c_checked,
            purpose_box_d_checked=data.purpose.box_d_checked,
            purpose_disability_from_date=data.purpose.disability_from_date,
            purpose_disability_to_date=data.purpose.disability_to_date,
            purpose_box_e_checked=data.purpose.box_e_checked,
            purpose_rtw_from_date=data.purpose.rtw_from_date,
            purpose_rtw_to_date=data.purpose.rtw_to_date,
            purpose_box_f_checked=data.purpose.box_f_checked,
            purpose_sib_from_date=data.purpose.sib_from_date,
            purpose_sib_to_date=data.purpose.sib_to_date,
            purpose_box_g_checked=data.purpose.box_g_checked,
            dwc024_yes_checked=data.network.dwc024_yes_checked,
            dwc024_no_checked=data.network.dwc024_no_checked,
            dwc_number=data.insurance.dwc_number,
            claim_number=data.insurance.claim_number,
            exam_date=data.exam.date,
            exam_time=data.exam.time,
            exam_location=data.exam.location,
            exam_location_full=data.exam.location_full,
            exam_location_city=data.exam.location_city,
            extent_of_injury=data.extent_of_injury,
            doctor_name=data.designated_doctor.name,
            doctor_address=data.designated_doctor.address,
            doctor_license_number=data.designated_doctor.license_number,
            doctor_license_jurisdiction=data.designated_doctor.license_jurisdiction,
            doctor_license_type=data.designated_doctor.license_type,
            doctor_phone=data.designated_doctor.phone,
            doctor_fax=data.designated_doctor.fax,
            injury_evaluations=data.injury_evaluations,
            dd_assignment_number=data.insurance_billing.dd_assignment_number,
            insurance_billing_name=data.insurance_billing.business_name,
            insurance_billing_address=data.insurance_billing.mailing_address,
            insurance_billing_phone=data.insurance_billing.phone,
            insurance_billing_fax=data.insurance_billing.fax,
            insurance_billing_email=data.insurance_billing.email,
            order_recipients=data.order_recipients,
        )
