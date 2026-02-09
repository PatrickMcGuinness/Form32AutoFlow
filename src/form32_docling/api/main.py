"""FastAPI application for Form32 GUI."""

import shutil
import uuid
from collections.abc import Generator
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from form32_docling.api.db import InjuryEvaluation, Patient, SessionLocal, init_db
from form32_docling.config import Config
from form32_docling.core.form32_processor import Form32Processor
from form32_docling.forms.form_generation_controller import FormGenerationController
from form32_docling.models.patient_info import InjuryEvaluation as ModelInjuryEvaluation
from form32_docling.models.patient_info import PatientInfo

app = FastAPI(title="Form32_docling GUI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

@app.post("/api/process")
async def process_form(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, Any]:
    """Upload and process a Form 32 PDF."""
    filename = file.filename or "unknown.pdf"
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file to temp location
    temp_dir = Path("/tmp/form32_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Run Processor for extraction with VLM enabled
        config = Config(use_vlm=True)
        processor = Form32Processor(temp_path, config=config, verbose=True)

        # Use the unified process method which handles extraction, validation, and directory setup
        result = processor.process()

        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Processing failed: {', '.join(result.get('errors', []))}")

        patient_info = result["patient_info"]

        # Save to SQLite
        db_patient = Patient(
            patient_name=patient_info.patient_name or "Unknown",
            ssn=patient_info.ssn,
            exam_date=patient_info.exam_date,
            exam_location=patient_info.exam_location,
            patient_info_json=patient_info.model_dump_json(),
            status="pending"
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        return {
            "id": db_patient.id,
            "patient_info": patient_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        # We might want to keep the Form 32 for later generation if needed
        pass

@app.get("/api/patients", response_model=list[dict])
def list_patients(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return [{"id": p.id, "name": p.patient_name, "date": p.exam_date, "location": p.exam_location, "status": p.status} for p in patients]

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_info = PatientInfo.model_validate_json(db_patient.patient_info_json)

    # Merge evaluations from DB
    evals = [
        ModelInjuryEvaluation(
            condition_text=e.condition_text,
            is_substantial_factor=e.is_substantial_factor,
            diagnosis_codes=eval(e.diagnosis_codes_json) if isinstance(e.diagnosis_codes_json, str) else e.diagnosis_codes_json
        )
        for e in db_patient.injury_evaluations
    ]
    patient_info.injury_evaluations = evals

    return {
        "id": db_patient.id,
        "patient_info": patient_info,
        "status": db_patient.status
    }

@app.patch("/api/patients/{patient_id}")
async def update_patient(patient_id: int, data: dict[str, Any], db: Session = Depends(get_db)) -> dict[str, str]:
    """Update patient info and injury evaluations."""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if "patient_info" in data:
        updated_info = PatientInfo.model_validate(data["patient_info"])
        db_patient.patient_info_json = updated_info.model_dump_json()
        db_patient.patient_name = updated_info.patient_name or "Unknown"
        db_patient.exam_date = updated_info.exam_date

        # Sync evaluations
        db.query(InjuryEvaluation).filter(InjuryEvaluation.patient_id == patient_id).delete()
        for eval_data in updated_info.injury_evaluations:
            db_eval = InjuryEvaluation(
                patient_id=patient_id,
                condition_text=eval_data.condition_text,
                is_substantial_factor=eval_data.is_substantial_factor,
                diagnosis_codes_json=str(eval_data.diagnosis_codes)
            )
            db.add(db_eval)

    db.commit()
    return {"message": "Updated successfully"}

@app.post("/api/generate/{patient_id}")
def generate_forms(patient_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Generate final PDFs for a patient."""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Load patient info and evaluations
    response = get_patient(patient_id, db)
    patient_info = response["patient_info"]

    try:
        controller = FormGenerationController(patient_info, verbose=True)
        generated_paths = controller.generate_forms()

        db_patient.status = "generated"
        db.commit()

        # Map filenames to relative paths/IDs for download
        results = []
        for path in generated_paths:
            p = Path(path)
            results.append({
                "type": p.name.split("_")[0], # e.g. DWC068
                "filename": p.name,
                "path": str(p)
            })

        return {"success": True, "files": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/api/download")
def download_file(path: str) -> FileResponse:
    """Download a specific generated PDF by its absolute path."""
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p, filename=p.name, media_type="application/pdf")

@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a patient record and its associated data."""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(db_patient)
    db.commit()
    return {"message": f"Patient {patient_id} deleted successfully"}

@app.delete("/api/patients")
def delete_all_patients(db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete all patient records (database cleanup)."""
    try:
        # Delete all evaluations first (cascaded if supported, but explicit for safety)
        db.query(InjuryEvaluation).delete()
        db.query(Patient).delete()
        db.commit()
        return {"message": "All database records cleaned successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database cleanup failed: {e!s}") from e

# --- Static File Serving (for Unified Deployment) ---

# Resolve the static files directory (gui/out)
# In production, this can be controlled via environment variable
STATIC_DIR = Path(__file__).parent.parent / "gui" / "out"

if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    # If static dir doesn't exist, we provide a minimal landing page or info
    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "message": "Form32 API is running. Static UI files not found at /gui/out. "
                       "Run 'npm run build' in the gui directory to generate them."
        }

def main() -> None:
    """Entry point for the form32-server command."""
    import uvicorn
    uvicorn.run("form32_docling.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
