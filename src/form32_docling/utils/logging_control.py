"""Logging configuration utilities for form32_docling."""

import logging
from pathlib import Path


class LoggingControl:
    """Centralized logging configuration management.

    Provides methods to configure logging levels, handlers, and output
    destinations for the form32_docling application.
    """

    def __init__(self) -> None:
        """Initialize with default logging levels."""
        self.default_level = logging.DEBUG
        self.minimal_level = logging.ERROR
        self._configured = False

    def setup_logging(
        self,
        *,
        enable_debug: bool = True,
        log_to_file: bool = False,
        log_file: str | Path = "form32_processing.log",
        minimal_console: bool = True,
    ) -> None:
        """Configure application logging.

        Args:
            enable_debug: Enable DEBUG level logging.
            log_to_file: Write logs to file.
            log_file: Path to log file.
            minimal_console: Show only ERROR/CRITICAL on console.
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG if enable_debug else self.default_level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_level = self.minimal_level if minimal_console else self.default_level
        console_handler.setLevel(console_level)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        root_logger.addHandler(console_handler)

        # File handler (optional)
        if log_to_file:
            file_handler = logging.FileHandler(str(log_file))
            file_level = logging.DEBUG if enable_debug else self.default_level
            file_handler.setLevel(file_level)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            root_logger.addHandler(file_handler)

        self._configured = True


    @staticmethod
    def enable_debug() -> None:
        """Enable DEBUG level for all handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        for handler in root_logger.handlers:
            handler.setLevel(logging.DEBUG)

