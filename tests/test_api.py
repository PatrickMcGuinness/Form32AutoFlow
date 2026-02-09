from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from form32_docling.api.db import SessionLocal, init_db
from form32_docling.api.main import app, get_db

# Setup Test Database
TEST_DB_PATH = Path("test_form32_gui.db")


def override_get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db() -> Generator[None]:
    # Initialize DB for tests
    init_db()
    yield
    # Clean up after tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_health_check() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_process_partial_data() -> None:
    # Test Upload with a file that might be missing data (simulated by a "wrong" file or partial content)
    # Here we just want to ensure it doesn't return 500
    test_pdf = Path("/home/patrickm/AIDev/OCRtools/Form32reader/WorkersCompData/LEROY-3pager.pdf")
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

def test_process_and_flow() -> None:
    # 1. Test Upload & Process
    test_pdf = Path("/home/patrickm/AIDev/OCRtools/Form32reader/WorkersCompData/LEROY-3pager.pdf")
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
