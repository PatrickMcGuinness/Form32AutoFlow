from pathlib import Path

from form32_docling.core.form32_processor import Form32Processor


def test_form32(verbose: bool = True) -> None:
    # File path
    pdf_path = r"data/LEROY.pdf"
    #pdf_path = r"c:\Users\billy_knott\Form32pdf\Merissa Stein 32.pdf"

    try:
        # Verify file exists
        if not Path(pdf_path).exists():
            print(f"Error: File not found: {pdf_path}")
            return

        print(f"\nProcessing file: {pdf_path}")
        print(f"Mode: {'Verbose' if verbose else 'Normal'}")
        print("-" * 50)

        # Initialize processor with verbose flag
        processor = Form32Processor(pdf_path, verbose=verbose)

        # Process the form
        result = processor.process()

        if result["success"]:
            print("\nSuccess: Form32 processed successfully")

            # In verbose mode, show patient info
            if verbose and result.get("patient_info"):
                patient_info = result["patient_info"]
                print("\nExtracted Information:")
                print("-" * 50)
                for field, value in vars(patient_info).items():
                    if value not in (None, "", False):
                        print(f"{field}: {value}")

            # Show output paths in both modes

            if result.get("generated_forms"):
                print("\nGenerated Forms:")
                for form in result["generated_forms"]:
                    print(f"- {form}")

        else:
            print(f"\nError: Processing failed: {result.get('errors', ['Unknown error'])}")

    except Exception as e:
        print(f"\nError: Exception during processing: {str(e)}")


if __name__ == "__main__":
    # Run tests
    #print("\n=== Testing in Normal Mode ===")
    #test_form32(verbose=False)

    print("\n\n=== Testing in Verbose Mode ===\n")
    test_form32(verbose=True)
