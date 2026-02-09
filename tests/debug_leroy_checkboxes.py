"""Debug script for LEROY.pdf checkbox analysis."""

import logging
from pathlib import Path

from form32_docling.core.checkbox_analyzer import CheckboxAnalyzer
from form32_docling.core.form32_processor import Form32Processor

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def debug_leroy() -> None:
    pdf_path = Path("data/LEROY.pdf")
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return

    print(f"Analyzing {pdf_path}...")

    # Run full processor logic to seeing page mapping
    processor = Form32Processor(pdf_path, verbose=True)
    # This triggers docling extraction
    processor._convert_with_docling()

    analyzer = processor._checkbox_analyzer
    if analyzer is None:
        analyzer = CheckboxAnalyzer(pdf_path)
        processor._checkbox_analyzer = analyzer

    print(f"Full text length: {len(processor._full_text)}")
    print("Full text preview:")
    print(processor._full_text[:500])

    print(f"Document type: {type(processor._document)}")
    if hasattr(processor._document, "pages"):
        print(f"Pages type: {type(processor._document.pages)}")
        # Check if it behaves like a dict
        if isinstance(processor._document.pages, dict):
            print("Pages is a dictionary. Keys:", list(processor._document.pages.keys())[:5])
            first_page = list(processor._document.pages.values())[0]
        else:
            # Assume iterable
            first_page = list(processor._document.pages)[0]

        print(f"First item in pages: {first_page}, type: {type(first_page)}")

        if isinstance(first_page, int) and isinstance(processor._document.pages, dict):
             # It was just keys
             first_page = processor._document.pages[first_page]
             print(f"Resolved page type: {type(first_page)}")

    print("\n--- PAGE TEXT DUMP ---")
    for i, text in enumerate(processor._page_texts):
        print(f"\nPage {i+1} Content Preview:")
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 40)

    analyzer.set_page_mapping(processor._page_texts)

    print("\nPage Mapping:")
    for page_type, idx in analyzer._page_types.items():
        print(f"  {page_type}: Page {idx + 1}")

    results = analyzer.analyze_all()
    print("\nCheckbox Results:")
    import json
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    debug_leroy()
