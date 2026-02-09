"""Custom exceptions for Form32 processing."""

class Form32Error(Exception):
    """Base exception for Form32 processing errors."""
    pass

class ExtractionError(Form32Error):
    """Error during text extraction."""
    pass

class ValidationError(Form32Error):
    """Error during form validation."""
    pass

class CheckboxAnalysisError(Form32Error):
    """Error during checkbox analysis."""
    pass
