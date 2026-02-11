from pathlib import Path

from docling.document_converter import DocumentConverter

from form32_docling.core import Form32Processor


class TestModelConfig:
    def test_processor_default_converter(self, tmp_path: Path) -> None:
        """Test that Form32Processor uses default converter when no model is specified."""
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_text("dummy")

        processor = Form32Processor(dummy_pdf)
        converter = processor.converter

        assert isinstance(converter, DocumentConverter)
        from docling.datamodel.base_models import InputFormat
        pdf_options = converter.format_to_options[InputFormat.PDF]

        # Should be StandardPdfPipeline by default
        from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
        assert pdf_options.pipeline_cls == StandardPdfPipeline
