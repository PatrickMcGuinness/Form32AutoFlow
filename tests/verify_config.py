import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "Form32reader" / "src"
sys.path.append(str(src_path))

from form32_docling.config import Config  # noqa: E402
from form32_docling.core.form32_processor import Form32Processor  # noqa: E402


def test_config_defaults() -> None:
    print("Testing Config defaults...")
    config = Config()
    assert config.doctor_phone == "512-903-5083"
    assert config.doctor_license_type == "D.C."
    assert config.doctor_license_jurisdiction == "TX"
    print("Config defaults OK")

def test_config_to_dict() -> None:
    print("Testing Config.to_dict()...")
    config = Config()
    d = config.to_dict()
    assert d["doctor_phone"] == "512-903-5083"
    assert d["doctor_license_type"] == "D.C."
    assert d["doctor_license_jurisdiction"] == "TX"
    print("Config.to_dict() OK")

def test_processor_uses_config() -> None:
    print("Testing Form32Processor usage of config...")
    # Mocking pdf_path
    pdf_path = Path("test.pdf")
    config = Config(doctor_phone="123-456-7890")

    # We don't want to actually process a PDF, just check _set_hardcoded_values
    processor = Form32Processor(pdf_path, config=config)
    processor._set_hardcoded_values()

    assert processor.patient_info.doctor_phone == "123-456-7890"
    assert processor.patient_info.doctor_license_type == "D.C."
    assert processor.patient_info.doctor_license_jurisdiction == "TX"
    print("Form32Processor usage of config OK")

if __name__ == "__main__":
    try:
        test_config_defaults()
        test_config_to_dict()
        test_processor_uses_config()
        print("\nAll verifications passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)
