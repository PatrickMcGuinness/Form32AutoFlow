"""Tests for form32_docling string utilities."""


from form32_docling.utils import (
    clean_location,
    clean_name,
    clean_ssn,
    extract_city,
    extract_license_parts,
    normalize_phone,
)


class TestCleanLocation:
    """Tests for clean_location function."""

    def test_none_input(self) -> None:
        """Test with None input."""
        assert clean_location(None) == ""

    def test_empty_string(self) -> None:
        """Test with empty string."""
        assert clean_location("") == ""

    def test_removes_fax_artifact(self) -> None:
        """Test removal of 'Fax:' from location."""
        result = clean_location("123 Main St Fax: 555-1234")
        assert "Fax:" not in result

    def test_adds_comma_before_zip(self) -> None:
        """Test comma insertion before ZIP code."""
        result = clean_location("123 Main St Austin TX 78701")
        assert ", 78701" in result

    def test_normalizes_whitespace(self) -> None:
        """Test whitespace normalization."""
        result = clean_location("123   Main    St")
        assert "  " not in result


class TestNormalizePhone:
    """Tests for normalize_phone function."""

    def test_none_input(self) -> None:
        """Test with None input."""
        assert normalize_phone(None) == ""

    def test_ten_digit_phone(self) -> None:
        """Test 10-digit phone formatting."""
        assert normalize_phone("5125551234") == "512.555.1234"

    def test_phone_with_dashes(self) -> None:
        """Test phone with existing dashes."""
        assert normalize_phone("512-555-1234") == "512.555.1234"

    def test_phone_with_parens(self) -> None:
        """Test phone with parentheses."""
        assert normalize_phone("(512) 555-1234") == "512.555.1234"

    def test_eleven_digit_with_country_code(self) -> None:
        """Test 11-digit phone with leading 1."""
        assert normalize_phone("15125551234") == "512.555.1234"

    def test_invalid_length(self) -> None:
        """Test phone with invalid length returns original."""
        assert normalize_phone("555-1234") == "555-1234"


class TestCleanSsn:
    """Tests for clean_ssn function."""

    def test_none_input(self) -> None:
        """Test with None input."""
        assert clean_ssn(None) == ""

    def test_full_ssn_formatted(self) -> None:
        """Test full SSN formatting."""
        assert clean_ssn("123456789") == "123-45-6789"

    def test_full_ssn_masked(self) -> None:
        """Test full SSN with masking."""
        assert clean_ssn("123456789", mask_full=True) == "XXX-XX-6789"

    def test_already_formatted_ssn(self) -> None:
        """Test SSN that's already formatted."""
        result = clean_ssn("123-45-6789")
        assert result == "123-45-6789"

    def test_partial_ssn_masked(self) -> None:
        """Test partial SSN with masking."""
        assert clean_ssn("6789", mask_full=True) == "XXX-XX-6789"


class TestExtractCity:
    """Tests for extract_city function."""

    def test_none_input(self) -> None:
        """Test with None input."""
        assert extract_city(None) == ""

    def test_city_state_zip_pattern(self) -> None:
        """Test extraction from 'City, ST ZIP' pattern."""
        result = extract_city("123 Main St, Austin, TX 78701")
        assert result == "Austin"

    def test_comma_separated(self) -> None:
        """Test extraction from comma-separated address."""
        result = extract_city("Some Clinic, 123 Main St")
        assert result == "Some Clinic"

    def test_no_comma(self) -> None:
        """Test with no comma in string."""
        assert extract_city("Austin") == ""


class TestCleanName:
    """Tests for clean_name function."""

    def test_none_input(self) -> None:
        """Test with None input."""
        assert clean_name(None) == ""

    def test_extra_whitespace(self) -> None:
        """Test removal of extra whitespace."""
        result = clean_name("John   Doe")
        assert result == "John Doe"

    def test_leading_trailing_space(self) -> None:
        """Test removal of leading/trailing space."""
        result = clean_name("  John Doe  ")
        assert result == "John Doe"


class TestExtractLicenseParts:
    """Tests for extract_license_parts function."""

    def test_none_input(self) -> None:
        """Test with None input."""
        result = extract_license_parts(None)
        assert result == ("", "", "")

    def test_full_license_string(self) -> None:
        """Test extraction from full license string."""
        result = extract_license_parts("12345 MD TX")
        number, license_type, jurisdiction = result
        assert number == "12345"
        assert license_type == "MD"
        assert jurisdiction == "TX"

    def test_partial_license(self) -> None:
        """Test extraction from partial license."""
        result = extract_license_parts("12345 DC")
        number, license_type, jurisdiction = result
        assert number == "12345"
        assert license_type == "DC"
        assert jurisdiction == ""
