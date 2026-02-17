"""Regression tests for config-driven marker usage in Form32Processor."""

from pathlib import Path

from form32_docling.config import Config
from form32_docling.core.form32_processor import Form32Processor


def _make_dummy_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_text("dummy")
    return pdf_path


def test_validate_form_uses_config_markers(tmp_path: Path) -> None:
    pdf_path = _make_dummy_pdf(tmp_path)
    config = Config(
        form32_validation_markers={
            "custom required marker": "Custom marker",
        }
    )
    processor = Form32Processor(pdf_path, config=config, verbose=False)

    processor._full_text = "this text does not include it"
    assert processor.validate_form() is False
    assert "Missing required element: Custom marker" in processor.validation_errors

    processor.validation_errors.clear()
    processor._full_text = "this text includes CUSTOM REQUIRED MARKER"
    assert processor.validate_form() is True


def test_identify_pages_uses_config_markers(tmp_path: Path) -> None:
    pdf_path = _make_dummy_pdf(tmp_path)
    config = Config(
        form32_page_type_markers={"CUSTOM_PART": "my custom part marker"},
        form32_exam_order_page_two_markers=("unique page two marker",),
        form32_front_page_markers=("front page marker one", "front page marker two"),
    )
    processor = Form32Processor(pdf_path, config=config, verbose=False)

    processor._document = object()
    processor._page_texts = [
        "DWC 032 header and my custom part marker",
        "this includes unique page two marker only",
        "this includes front page marker one and front page marker two",
    ]

    page_map = processor._identify_dwc032_pages()
    assert page_map == {
        1: "CUSTOM_PART",
        2: "exam_order_page_two",
        3: "front_page",
    }
