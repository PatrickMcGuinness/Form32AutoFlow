"""Command-line interface for form32_docling."""

import argparse
import sys
import warnings
from pathlib import Path

from form32_docling import __version__
from form32_docling.config import Config
from form32_docling.core import Form32Processor
from form32_docling.utils import LoggingControl

# Suppress pypdfium2 cleanup warning (cosmetic issue during process exit)
warnings.filterwarnings("ignore", message="Cannot close object; pdfium library is destroyed")


def main() -> int:
    """Main entry point for form32-docling CLI.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        prog="form32-docling",
        description="Process Form 32 PDFs using docling library",
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the Form 32 PDF file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (overrides default)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Docling model to use (e.g., granite-docling-258M)",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output structured Form32Data as JSON",
    )

    # VLM extraction flags (mutually exclusive)
    vlm_group = parser.add_mutually_exclusive_group()
    vlm_group.add_argument(
        "--use-vlm",
        action="store_true",
        dest="use_vlm",
        default=None,
        help="Use VLM-based DocumentExtractor for field extraction (default)",
    )
    vlm_group.add_argument(
        "--no-vlm",
        action="store_false",
        dest="use_vlm",
        help="Use regex-based extraction instead of VLM",
    )

    args = parser.parse_args()

    # Setup logging
    # Priority: -v flag (DEBUG) > FORM32_LOG_LEVEL env var > default (INFO)
    import logging
    import os

    if args.verbose:
        log_level = logging.DEBUG
    else:
        env_level = os.environ.get("FORM32_LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, env_level, logging.INFO)

    logging_control = LoggingControl()
    logging_control.setup_logging(
        enable_debug=(log_level == logging.DEBUG),
        log_to_file=True,
        minimal_console=(log_level > logging.DEBUG),
    )

    # Validate input file
    if not args.pdf_path.exists():
        print(f"Error: File not found: {args.pdf_path}", file=sys.stderr)
        return 1

    if args.pdf_path.suffix.lower() != ".pdf":
        print(f"Error: File must be a PDF: {args.pdf_path}", file=sys.stderr)
        return 1

    # Setup config
    config = Config()
    if args.output_dir:
        config.base_directory = args.output_dir
    if args.verbose:
        config.output_docling_document = True
        config.output_docling_markdown = True
        config.output_form32_json = True
    if args.output_json:
        config.output_form32_json = True
    if args.model:
        config.docling_model = args.model
    if args.use_vlm is not None:
        config.use_vlm = args.use_vlm

    # Log extraction mode
    extraction_mode = "VLM" if config.use_vlm else "regex"
    print(f"Processing: {args.pdf_path} (extraction mode: {extraction_mode})")

    processor = Form32Processor(
        args.pdf_path,
        config=config,
        verbose=args.verbose,
    )

    result = processor.process()

    if result["success"]:
        print(f"Success! Output directory: {result['output_directory']}")
        print(f"Form32 copied to: {result['form32_path']}")

        if result.get("generated_forms"):
            print("Generated forms:")
            for form_path in result["generated_forms"]:
                print(f"  - {form_path}")

        if result.get("docling_document_path"):
            print(f"Docling document saved to: {result['docling_document_path']}")

        if result.get("docling_markdown_path"):
            print(f"Docling markdown saved to: {result['docling_markdown_path']}")

        if result.get("form32_json_path"):
            print(f"Form32 structured data saved to: {result['form32_json_path']}")

        return 0

    print("Processing failed:", file=sys.stderr)
    for error in result.get("errors", []):
        print(f"  - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
