from collections.abc import Generator
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from form32_docling.api.db import SessionLocal, init_db
from form32_docling.api.main import app, get_db
from form32_docling.models.patient_info import PatientInfo

# API integration tests are opt-in because local runtime can hang on ASGI client calls.
if os.getenv("RUN_API_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "Skipping API integration tests. Set RUN_API_INTEGRATION_TESTS=1 to run.",
        allow_module_level=True,
    )

# Setup Test Database
TEST_DB_PATH = Path("test_form32_gui.db")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PDF_PATH = PROJECT_ROOT / "WorkersCompData" / "LEROY-3pager.pdf"


def override_get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db() -> Generator[None]:
    # Initialize DB for tests
    init_db()
    yield
    # Clean up after tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_heavy_processing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Mock slow PDF extraction/form generation for API flow tests."""
    sample_patient = PatientInfo(
        patient_name="LEROY SAMPLE",
        employee_ssn="1234",
        exam_date="01/15/2026",
        exam_location="Austin Clinic",
        exam_location_city="AUSTIN",
    )

    def fake_process(self: object) -> dict[str, object]:  # noqa: ARG001
        return {
            "success": True,
            "patient_info": sample_patient,
            "output_directory": str(tmp_path),
            "form32_path": str(tmp_path / "FORM32 LEROY SAMPLE.pdf"),
            "generated_forms": [],
            "docling_document_path": None,
            "docling_markdown_path": None,
            "form32_json_path": None,
            "extracted_fields_path": None,
        }

    generated_pdf = tmp_path / "DWC069 LEROY SAMPLE.pdf"
    generated_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    def fake_generate_forms(self: object) -> list[str]:  # noqa: ARG001
        return [str(generated_pdf)]

    monkeypatch.setattr("form32_docling.api.main.Form32Processor.process", fake_process)
    monkeypatch.setattr(
        "form32_docling.api.main.FormGenerationController.generate_forms",
        fake_generate_forms,
    )


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_process_partial_data(client: TestClient) -> None:
    # Test Upload with a file that might be missing data (simulated by a "wrong" file or partial content)
    # Here we just want to ensure it doesn't return 500
    test_pdf = TEST_PDF_PATH
    if not test_pdf.exists():
        pytest.skip("Test PDF not found")

    with open(test_pdf, "rb") as f:
        # We use a dummy filename to see if that triggers any issues,
        # but the content is the same. The key is that is_valid() now returns True even if
        # extraction missed something.
        response = client.post(
            "/api/process",
            files={"file": ("partial_data_test.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "patient_info" in data

def test_process_and_flow(client: TestClient) -> None:
    # 1. Test Upload & Process
    test_pdf = TEST_PDF_PATH
    if not test_pdf.exists():
        pytest.skip("Test PDF not found")

    with open(test_pdf, "rb") as f:
        response = client.post(
            "/api/process",
            files={"file": ("LEROY-3pager.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "patient_info" in data
    patient_id = data["id"]

    # 2. Test Fetch Patients List
    response = client.get("/api/patients")
    assert response.status_code == 200
    patients = response.json()
    assert len(patients) > 0
    assert any(p["id"] == patient_id for p in patients)

    # 3. Test Fetch Specific Patient
    response = client.get(f"/api/patients/{patient_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == patient_id
    assert "patient_info" in detail

    # 4. Test Update (PATCH) - Simulating Doctor's Workbench edits
    edit_payload = {
        "patient_info": {
            **detail["patient_info"],
            "patient_name": "LEROY TEST EDIT",
            "purpose_box_a_checked": True,
            "purpose_mmi_date": "2026-02-11",
            "purpose_box_b_checked": True,
            "purpose_ir_mmi_date": "2026-02-10",
            "purpose_box_c_checked": True,
            "extent_of_injury": "Slip and fall while lifting equipment",
            "purpose_box_d_checked": True,
            "purpose_disability_from_date": "2026-01-15",
            "purpose_disability_to_date": "2026-01-29",
            "purpose_box_e_checked": True,
            "purpose_rtw_from_date": "2026-02-01",
            "purpose_rtw_to_date": "2026-02-14",
            "purpose_box_f_checked": True,
            "purpose_sib_from_date": "2026-02-15",
            "purpose_sib_to_date": "2026-03-01",
            "purpose_box_g_checked": True,
            "purpose_box_g_description": "Clarify additional work restrictions",
            "injury_evaluations": [
                {
                    "condition_text": "Lumbar Discopathy",
                    "is_substantial_factor": True,
                    "diagnosis_codes": ["M51.26", "M54.5", "", ""]
                }
            ]
        }
    }

    response = client.patch(f"/api/patients/{patient_id}", json=edit_payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Updated successfully"}

    # Verify update persisted
    response = client.get(f"/api/patients/{patient_id}")
    updated_detail = response.json()
    assert updated_detail["patient_info"]["patient_name"] == "LEROY TEST EDIT"
    assert updated_detail["patient_info"]["purpose_box_a_checked"] is True
    assert updated_detail["patient_info"]["purpose_mmi_date"] == "2026-02-11"
    assert updated_detail["patient_info"]["purpose_box_b_checked"] is True
    assert updated_detail["patient_info"]["purpose_ir_mmi_date"] == "2026-02-10"
    assert updated_detail["patient_info"]["purpose_box_c_checked"] is True
    assert updated_detail["patient_info"]["extent_of_injury"] == "Slip and fall while lifting equipment"
    assert updated_detail["patient_info"]["purpose_box_d_checked"] is True
    assert updated_detail["patient_info"]["purpose_disability_from_date"] == "2026-01-15"
    assert updated_detail["patient_info"]["purpose_disability_to_date"] == "2026-01-29"
    assert updated_detail["patient_info"]["purpose_box_e_checked"] is True
    assert updated_detail["patient_info"]["purpose_rtw_from_date"] == "2026-02-01"
    assert updated_detail["patient_info"]["purpose_rtw_to_date"] == "2026-02-14"
    assert updated_detail["patient_info"]["purpose_box_f_checked"] is True
    assert updated_detail["patient_info"]["purpose_sib_from_date"] == "2026-02-15"
    assert updated_detail["patient_info"]["purpose_sib_to_date"] == "2026-03-01"
    assert updated_detail["patient_info"]["purpose_box_g_checked"] is True
    assert updated_detail["patient_info"]["purpose_box_g_description"] == "Clarify additional work restrictions"
    assert len(updated_detail["patient_info"]["injury_evaluations"]) == 1
    assert updated_detail["patient_info"]["injury_evaluations"][0]["is_substantial_factor"] is True

    # 5. Test Generate Forms
    # This might take a moment due to PDF generation
    response = client.post(f"/api/generate/{patient_id}")
    assert response.status_code == 200
    gen_data = response.json()
    assert gen_data["success"] is True
    assert "files" in gen_data
    assert len(gen_data["files"]) > 0

    # 6. Test Download
    for file_info in gen_data["files"]:
        path = file_info["path"]
        response = client.get("/api/download", params={"path": path})
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
