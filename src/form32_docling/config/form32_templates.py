
"""DWC-032 Form Templates for DocumentExtractor.

These templates define the structure of each DWC-032 form page
for use with Docling's DocumentExtractor.
"""

# Map template field labels to PatientInfo attribute names
FIELD_TO_ATTRIBUTE_MAP: dict[str, str] = {
    # Part 1 - Employee Information
    "1. Employee's name": "patient_name",
    "2. Social Security number": "employee_ssn",
    "3. Employee's address": "employee_address",
    "4. Employee's county": "employee_county",
    "5. Employee's primary phone number": "employee_primary_phone",
    "6. Employee's alternate phone number": "employee_alternate_phone",
    "7. Employee's date of birth (mm/dd/yyyy)": "employee_date_of_birth",
    "8. Date of injury (mm/dd/yyyy)": "date_of_injury",
    "9. Representative's name": "representative_name",
    "10. Representative's phone number": "representative_phone",
    "11. Representative's email address": "representative_email",
    "12. Representative's fax number": "representative_fax",
    "13. Employer's name": "employer_name",
    "14. Employer's phone number": "employer_phone",
    "15. Employer's address": "employer_address",
    # Part 2 - Insurance Information
    "16. Insurance carrier's name": "insurance_carrier",
    "17. Insurance carrier's address": "carrier_address",
    "18. Adjuster's name": "adjuster_name",
    "19. Adjuster's email": "adjuster_email",
    "20. Adjuster's phone number": "adjuster_phone",
    "21. Adjuster's fax number": "adjuster_fax",
    "If yes, name of the network": "network_name",
    "If yes, name of the health care plan": "health_plan_name",
    # Part 3 - Treating Doctor Information
    "24. Treating doctor name": "treating_doctor_name",
    "25. Phone number": "treating_doctor_phone",
    "26. Address": "treating_doctor_address",
    "27. Fax number": "treating_doctor_fax",
    "28. License number": "treating_doctor_license_number",
    "29. License type": "treating_doctor_license_type",
    # Part 4 - Body Areas
    "Spine and musculoskeletal structures of torso": "body_area_spine",
    "Upper extremities": "body_area_upper_extremities",
    "Lower extremities (excluding feet)": "body_area_lower_extremities",
    "Feet": "body_area_lower_extremities",
    "Teeth and jaw": "body_area_teeth_jaw",
    "Eyes": "body_area_eyes",
    "Other body areas or systems": "body_area_other_systems",
    "Traumatic brain injury": "body_area_brain_injury",
    "Spinal cord injury": "body_area_spinal_cord",
    "Severe burns (including chemical burns)": "body_area_burns",
    "Joint dislocation, fractures with vascular injury": "body_area_fractures",
    "Infectious diseases (complicated)": "body_area_infectious",
    "Complex regional pain syndrome": "body_area_regional_pain",
    "Chemical exposure": "body_area_chemical_exposure",
    "Heart or cardiovascular condition": "body_area_cardiovascular",
    "Mental and behavioral disorders": "body_area_mental_disorders",
    # Part 5 - Purpose Checkboxes (simplified names)
    "A. Maximum medical improvement (MMI)": "purpose_box_a_checked",
    "A. Maximum medical improvement (MMI) checkbox": "purpose_box_a_checked",
    "B. Impairment rating (IR)": "purpose_box_b_checked",
    "B. Impairment rating (IR) checkbox": "purpose_box_b_checked",
    "C. Extent of injury": "purpose_box_c_checked",
    "C. Extent of injury checkbox": "purpose_box_c_checked",
    "C. Description of accident or incident": "extent_of_injury",
    "D. Disability - direct result": "purpose_box_d_checked",
    "D. Disability - direct result checkbox": "purpose_box_d_checked",
    "E. Return to work": "purpose_box_e_checked",
    "E. Return to work checkbox": "purpose_box_e_checked",
    "F. Return to work (supplemental income benefits)": "purpose_box_f_checked",
    "F. Return to work (supplemental income benefits) checkbox": "purpose_box_f_checked",
    "G. Other similar issues": "purpose_box_g_checked",
    "G. Other similar issues checkbox": "purpose_box_g_checked",
    "G. Description of issues": "purpose_box_g_description",
    "32. Has there been an approved DWC Form-024, final decision, or final court order to determine the compensable injury? Yes": "dwc024_yes_checked",
    "32. Has there been an approved DWC Form-024, final decision, or final court order to determine the compensable injury? No": "dwc024_no_checked",
    # Part 6 - Requester Information
    "Requester type": "requester_type",
    "Requester name": "requester_name",
    "Requester date": "requester_date",
    # Front Page Fields
    "Injured employee": "patient_name",
    "DWC#": "dwc_number",
    "Date of injury": "date_of_injury",
    "Employer": "employer_name",
    "Insurance carrier": "insurance_carrier",
    "Insurance carrier claim#": "claim_number",
    "DD assignment #": "dd_assignment_number",
    "Date": "exam_date",
    # Exam Order Page Two Fields
    "Exam date": "exam_date",
    "Exam time": "exam_time",
    "Exam location": "exam_location",
    "Exam location address": "exam_location_full",
    "Designated doctor name": "doctor_name",
    "Designated doctor license": "doctor_license_number",
    "Designated doctor phone": "doctor_phone",
    "Designated doctor fax": "doctor_fax",
    "DD assignment number": "dd_assignment_number",
    "Insurance business name": "insurance_billing_name",
    "Insurance mailing address": "insurance_billing_address",
    "Insurance phone number": "insurance_billing_phone",
    "Insurance fax number": "insurance_billing_fax",
    "Insurance email address": "insurance_billing_email",
    "Sent to names": "order_recipients",
}

# Front page template (scheduling/assignment info)
front_page_template = {
    "Injured employee": "string",
    "DWC#": "string",
    "Date of injury": "date-time",
    "Employer": "string",
    "Insurance carrier": "string",
    "Insurance carrier claim#": "string",
    "DD assignment #": "string",
    "Date": "date-time",
}

# Field names and labels (text in the form itself)
# NOTE: Templates must be FLAT dicts for DocumentExtractor
# Format: {"field_label": "type"} where type is "string", "float", "int", or a list of enum values

DWC032_part1_template = {
    # Part 1 - Employee Information
    "1. Employee's name": "string",
    "2. Social Security number": "string",
    "3. Employee's address": "string",
    "4. Employee's county": "string",
    "5. Employee's primary phone number": "string",
    "6. Employee's alternate phone number": "string",
    "7. Employee's date of birth (mm/dd/yyyy)": "date-time",
    "8. Date of injury (mm/dd/yyyy)": "date-time",
    "9. Representative's name": "string",
    "10. Representative's phone number": "string",
    "11. Representative's email address": "string",
    "12. Representative's fax number": "string",
    "13. Employer's name": "string",
    "14. Employer's phone number": "string",
    "15. Employer's address": "string",
    # Part 2 - Insurance Information
    "16. Insurance carrier's name": "string",
    "17. Insurance carrier's address": "string",
    "18. Adjuster's name": "string",
    "19. Adjuster's email": "string",
    "20. Adjuster's phone number": "string",
    "21. Adjuster's fax number": "string",
    "22. Certified network": ["Yes", "No"],
    "If yes, name of the network": "string",
    "23. Political subdivision": ["Yes", "No"],
    "If yes, name of the health care plan": "string",
}

DWC032_part3_template = {
    # Part 3 - Treating Doctor Information
    "24. Treating doctor name": "string",
    "25. Phone number": "string",
    "26. Address": "string",
    "27. Fax number": "string",
    "28. License number": "string",
    "29. License type": "string",
    # Part 4 - Body Areas (simplified to checkbox-like)
    "Spine and musculoskeletal structures of torso": ["Checked", "Unchecked"],
    "Upper extremities": ["Checked", "Unchecked"],
    "Lower extremities (excluding feet)": ["Checked", "Unchecked"],
    "Feet": ["Checked", "Unchecked"],
    "Teeth and jaw": ["Checked", "Unchecked"],
    "Eyes": ["Checked", "Unchecked"],
    "Other body areas or systems": ["Checked", "Unchecked"],
    "Traumatic brain injury": ["Checked", "Unchecked"],
    "Spinal cord injury": ["Checked", "Unchecked"],
    "Severe burns (including chemical burns)": ["Checked", "Unchecked"],
    "Joint dislocation, fractures with vascular injury": ["Checked", "Unchecked"],
    "Infectious diseases (complicated)": ["Checked", "Unchecked"],
    "Complex regional pain syndrome": ["Checked", "Unchecked"],
    "Chemical exposure": ["Checked", "Unchecked"],
    "Heart or cardiovascular condition": ["Checked", "Unchecked"],
    "Mental and behavioral disorders": ["Checked", "Unchecked"],
}

DWC032_part5_template = {
    # Part 5 - Purpose of Examination
    "A. Maximum medical improvement (MMI)": ["Checked", "Unchecked"],
    "Statutory MMI date (if any)": "date-time",
    "B. Impairment rating (IR)": ["Checked", "Unchecked"],
    "MMI date* (required only if Box A is not checked)": "date-time",
    "C. Extent of injury": ["Checked", "Unchecked"],
    "C. Description of accident or incident": "string",
    "D. Disability - direct result": ["Checked", "Unchecked"],
    "D. From": "date-time",
    "D. To": "date-time",
    "E. Return to work": ["Checked", "Unchecked"],
    "E. From": "date-time",
    "E. To": "date-time",
    "F. Return to work (supplemental income benefits)": ["Checked", "Unchecked"],
    "F. From": "date-time",
    "F. To": "date-time",
    "G. Other similar issues": ["Checked", "Unchecked"],
    "G. Description of issues": "string",
    "32. Has there been an approved DWC Form-024, final decision, or final court order to determine the compensable injury? Yes": ["Checked", "Unchecked"],
    "32. Has there been an approved DWC Form-024, final decision, or final court order to determine the compensable injury? No": ["Checked", "Unchecked"],
}

# Optional Part 5 template variant to improve checkbox extraction.
DWC032_part5_checkbox_assist_template = {
    # Part 5 - Purpose of Examination
    "A. Maximum medical improvement (MMI) checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "Statutory MMI date (if any)": "date-time",
    "B. Impairment rating (IR) checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "MMI date* (required only if Box A is not checked)": "date-time",
    "C. Extent of injury checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "C. Description of accident or incident": "string",
    "D. Disability - direct result checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "D. From": "date-time",
    "D. To": "date-time",
    "E. Return to work checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "E. From": "date-time",
    "E. To": "date-time",
    "F. Return to work (supplemental income benefits) checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "F. From": "date-time",
    "F. To": "date-time",
    "G. Other similar issues checkbox": ["Checkbox filled", "Checkbox unfilled"],
    "G. Description of issues": "string",
    "32. Has there been an approved DWC Form-024, final decision, or final court order to determine the compensable injury? Yes": ["Checkbox filled", "Checkbox unfilled"],
    "32. Has there been an approved DWC Form-024, final decision, or final court order to determine the compensable injury? No": ["Checkbox filled", "Checkbox unfilled"],
}

DWC032_part6_template = {
    # Part 6 - Requester Information
    "Requester type": ["Injured employee", "Injured employee representative", "Insurance carrier"],
    "Requester name": "string",
    "Requester date": "date-time",
}

# Exam Order Letter Page Two Template (Commissioner's Order)
exam_order_page_two_template = {
    # Exam Scheduling Information
    "Exam date": "date-time",
    "Exam time": "string",
    "Exam location": "string",
    "Exam location address": "string",
    # Designated Doctor Information
    "Designated doctor name": "string",
    "Designated doctor license": "string",
    "Designated doctor phone": "string",
    "Designated doctor fax": "string",
    # Insurance Carrier Billing Contact
    "DD assignment number": "string",
    "Insurance business name": "string",
    "Insurance mailing address": "string",
    "Insurance phone number": "string",
    "Insurance fax number": "string",
    "Insurance email address": "string",
    # Recipients
    "Sent to names": "string",
}
