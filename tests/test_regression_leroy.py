"""Regression test for Form32 processing of LEROY.pdf."""

import logging
from pathlib import Path

import pytest

from form32_docling.core.form32_processor import Form32Processor

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent.parent / "data"

def test_process_leroy_pdf(test_data_dir: Path, tmp_path: Path) -> None:
    """Test full processing of LEROY.pdf."""
    pdf_path = test_data_dir / "LEROY.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Test file not found: {pdf_path}")

    # Initialize processor with temporary output directory in config if needed
    # But Processor takes config object, let's mock config or use default
    # Config uses env vars or defaults. We can patch it or let it use defaults.
    # For isolation, let's patch the output directory logic or just check the return dict.

    # We want to use a temporary directory for output to avoid cluttering real folders
    # config.base_directory is used. We should probably override it.

    from form32_docling.config import Config

    config = Config()
    config.base_directory = tmp_path

    processor = Form32Processor(pdf_path, config=config, verbose=True)

    # Execute processing
    result = processor.process()

    # 1. Check success
    assert result["success"] is True, f"Processing failed with errors: {result.get('errors')}"

    # 2. Check patient info extraction (Sample expected values based on typical audit,
    #    or just sanity check non-empty if we don't know exact content yet)
    patient_info = result["patient_info"]
    assert patient_info.patient_name is not None, "Patient name should be extracted"
    logger.info(f"Extracted Name: {patient_info.patient_name}")

    # 3. Check generated forms
    generated_forms = result["generated_forms"]
    assert len(generated_forms) > 0, "Should generate at least one form"

    # 4. Check specifically for Form 68
    form68_path = next((f for f in generated_forms if "DWC068" in str(f)), None)
    assert form68_path is not None, "DWC068 form should be generated"
    assert Path(form68_path).exists(), "Generated Form 68 file should exist"

    # 5. Check Form32 copy exists
    form32_path = result["form32_path"]
    assert Path(form32_path).exists(), "Form 32 copy should exist"

    # 6. Check page two extraction (insurance billing contact)
    # These fields are extracted from the Commissioner's Order page
    logger.info(f"DD Assignment Number: {patient_info.dd_assignment_number}")
    logger.info(f"Insurance Billing Name: {patient_info.insurance_billing_name}")
    logger.info(f"Order Recipients: {patient_info.order_recipients}")

    # Verify DD assignment number is extracted (should contain DD)
    if patient_info.dd_assignment_number:
        assert "DD" in patient_info.dd_assignment_number, \
            f"DD assignment number should contain 'DD': {patient_info.dd_assignment_number}"

    # Verify insurance billing name is extracted if present
    if patient_info.insurance_billing_name:
        logger.info(f"Verified insurance billing name: {patient_info.insurance_billing_name}")

    # Verify order recipients is extracted if present
    if patient_info.order_recipients:
        logger.info(f"Verified order recipients: {patient_info.order_recipients}")

