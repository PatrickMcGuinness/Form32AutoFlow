"""Tests for form32_docling checkbox analyzer."""

import numpy as np

from form32_docling.core import CHECKBOX_PARAMS, CheckboxAnalyzer, FormPages


class TestFormPages:
    """Tests for FormPages enum."""

    def test_enum_values(self) -> None:
        """Test FormPages enum string values."""
        assert FormPages.NETWORK == "network"
        assert FormPages.BODY_AREA == "body_area"
        assert FormPages.PURPOSE == "purpose"


class TestCheckboxParams:
    """Tests for CHECKBOX_PARAMS configuration."""

    def test_network_params_exist(self) -> None:
        """Test network checkbox parameters are defined."""
        assert "network" in CHECKBOX_PARAMS
        assert "checkboxes" in CHECKBOX_PARAMS["network"]
        assert "q22_yes" in CHECKBOX_PARAMS["network"]["checkboxes"]

    def test_body_area_params_exist(self) -> None:
        """Test body area checkbox parameters are defined."""
        assert "body_area" in CHECKBOX_PARAMS
        assert "checkboxes" in CHECKBOX_PARAMS["body_area"]
        assert "spine" in CHECKBOX_PARAMS["body_area"]["checkboxes"]

    def test_purpose_params_exist(self) -> None:
        """Test purpose checkbox parameters are defined."""
        assert "purpose" in CHECKBOX_PARAMS
        assert "checkboxes" in CHECKBOX_PARAMS["purpose"]
        assert "box_a" in CHECKBOX_PARAMS["purpose"]["checkboxes"]

    def test_all_params_have_threshold(self) -> None:
        """Test all param sets have a threshold value."""
        for key in CHECKBOX_PARAMS:
            assert "threshold" in CHECKBOX_PARAMS[key]
            assert 0 < CHECKBOX_PARAMS[key]["threshold"] < 1


class TestCheckboxAnalyzerPageIdentification:
    """Tests for CheckboxAnalyzer page identification."""

    def test_identify_network_page(self) -> None:
        """Test identification of network page from text."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)
        analyzer._page_types = {}

        text = "22. Does the claim have medical benefits provided through..."
        result = analyzer.identify_page_type(text)
        assert result == FormPages.NETWORK

    def test_identify_body_area_page(self) -> None:
        """Test identification of body area page from text."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)
        analyzer._page_types = {}

        text = "30. Check all body areas that apply"
        result = analyzer.identify_page_type(text)
        assert result == FormPages.BODY_AREA

    def test_identify_purpose_page(self) -> None:
        """Test identification of purpose page from text."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)
        analyzer._page_types = {}

        text = "31. Requester: Check boxes A through G as applicable"
        result = analyzer.identify_page_type(text)
        assert result == FormPages.PURPOSE

    def test_identify_unknown_page(self) -> None:
        """Test identification returns None for unknown page."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)
        analyzer._page_types = {}

        text = "Some random text that doesn't match any page type"
        result = analyzer.identify_page_type(text)
        assert result is None


class TestCheckboxAnalyzerROI:
    """Tests for CheckboxAnalyzer ROI analysis."""

    def test_analyze_roi_empty_checkbox(self) -> None:
        """Test ROI analysis on empty (unchecked) checkbox."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)

        # Create a white (empty) image
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = analyzer._analyze_roi(img, 10, 10, 20, 20, threshold=0.3)
        assert result is False

    def test_analyze_roi_filled_checkbox(self) -> None:
        """Test ROI analysis on filled (checked) checkbox."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)

        # Create an image with a dark region
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img[10:30, 10:30] = 0  # Dark square (filled checkbox)

        result = analyzer._analyze_roi(img, 10, 10, 20, 20, threshold=0.3)
        assert result is True

    def test_analyze_roi_out_of_bounds(self) -> None:
        """Test ROI analysis with out-of-bounds coordinates."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)

        img = np.ones((50, 50, 3), dtype=np.uint8) * 255
        result = analyzer._analyze_roi(img, 100, 100, 20, 20, threshold=0.3)
        assert result is False

    def test_analyze_roi_partial_fill(self) -> None:
        """Test ROI analysis with partially filled region."""
        analyzer = CheckboxAnalyzer.__new__(CheckboxAnalyzer)

        # Create an image with about 20% fill (below threshold)
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img[10:14, 10:30] = 0  # Only partial fill

        result = analyzer._analyze_roi(img, 10, 10, 20, 20, threshold=0.3)
        assert result is False
