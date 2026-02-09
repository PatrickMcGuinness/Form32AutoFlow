"""Tests for form32_docling configuration module."""

import os
from pathlib import Path
from unittest.mock import patch

from form32_docling.config import Config
from form32_docling.utils.date_utils import format_date


class TestConfig:
    """Tests for Config class."""

    def test_default_initialization(self) -> None:
        """Test Config initializes with defaults."""
        config = Config()
        assert isinstance(config.base_directory, Path)
        assert isinstance(config.pdf_path, Path)

    def test_format_date_valid(self) -> None:
        """Test date formatting with valid input."""
        result = format_date("01/15/2024")
        assert result == "1.15.24"

    def test_format_date_none(self) -> None:
        """Test date formatting with None input."""
        result = format_date(None)
        assert result == "NO_DATE"

    def test_format_date_empty(self) -> None:
        """Test date formatting with empty string."""
        result = format_date("")
        assert result == "NO_DATE"

    def test_format_date_invalid(self) -> None:
        """Test date formatting with invalid format."""
        result = format_date("not-a-date")
        assert result == "NO_DATE"

    def test_format_date_iso_format(self) -> None:
        """Test date formatting with ISO format input."""
        result = format_date("2024-01-15")
        assert result == "1.15.24"

    def test_get_patient_dir_without_city(self) -> None:
        """Test patient directory path without city."""
        config = Config()
        path = config.get_patient_dir("01/15/2024", "John Doe")
        assert "John_Doe_1.15.24" in str(path)

    def test_get_patient_dir_with_city(self) -> None:
        """Test patient directory path with city."""
        config = Config()
        path = config.get_patient_dir("01/15/2024", "John Doe", "Austin")
        assert "John_Doe_Austin_1.15.24" in str(path)

    def test_get_form_path(self) -> None:
        """Test form file path generation."""
        directory = Path("/tmp/test")
        path = Config.get_form_path(directory, "DWC068", "John Doe")
        assert path == directory / "DWC068 JOHN DOE.pdf"

    def test_get_form_path_none_patient(self) -> None:
        """Test form path with None patient name."""
        directory = Path("/tmp/test")
        path = Config.get_form_path(directory, "DWC068", None)
        assert "UNKNOWN_PATIENT" in str(path)

    def test_get_templates_dir(self) -> None:
        """Test templates directory path."""
        templates_dir = Config.get_templates_dir()
        assert templates_dir.name == "templates"
        assert "forms" in str(templates_dir)

    def test_to_dict(self) -> None:
        """Test config serialization to dict."""
        config = Config()
        result = config.to_dict()
        assert "base_directory" in result
        assert "pdf_path" in result
        assert "use_vlm" in result

    @patch.dict(os.environ, {"FORM32_OUTPUT_DIR": "/custom/output"})
    def test_env_override_output_dir(self) -> None:
        """Test environment variable override for output directory."""
        from form32_docling.config import custom_config
        path = custom_config.get_base_output_dir()
        assert str(path) == "/custom/output"

    @patch.dict(os.environ, {"FORM32_PDF_PATH": "/custom/pdf"})
    def test_env_override_pdf_path(self) -> None:
        """Test environment variable override for PDF path."""
        from form32_docling.config import custom_config
        path = custom_config.get_pdf_source_dir()
        assert str(path) == "/custom/pdf"
