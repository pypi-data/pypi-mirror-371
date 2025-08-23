"""Tests for normalization functions."""

import pytest

from pricetag.normalizer import (
    estimate_from_type,
    is_valid_range,
    normalize_range,
    normalize_to_annual,
)


class TestNormalizeToAnnual:
    """Tests for normalize_to_annual function."""
    
    def test_hourly_to_annual_default(self):
        result = normalize_to_annual(50.0, "hourly")
        assert result == 50.0 * 2080  # 104,000
    
    def test_hourly_to_annual_custom_hours(self):
        result = normalize_to_annual(50.0, "hourly", hours_per_year=2000)
        assert result == 50.0 * 2000  # 100,000
    
    def test_monthly_to_annual(self):
        result = normalize_to_annual(5000.0, "monthly")
        assert result == 5000.0 * 12  # 60,000
    
    def test_weekly_to_annual(self):
        result = normalize_to_annual(1000.0, "weekly")
        assert result == 1000.0 * 52  # 52,000
    
    def test_annual_unchanged(self):
        result = normalize_to_annual(75000.0, "annual")
        assert result == 75000.0
    
    def test_unknown_unchanged(self):
        result = normalize_to_annual(50000.0, "unknown")
        assert result == 50000.0
    
    def test_base_unchanged(self):
        result = normalize_to_annual(80000.0, "base")
        assert result == 80000.0
    
    def test_bonus_unchanged(self):
        result = normalize_to_annual(15000.0, "bonus")
        assert result == 15000.0
    
    @pytest.mark.parametrize("value,price_type,expected", [
        (25.0, "hourly", 52000.0),
        (4166.67, "monthly", 50000.04),
        (961.54, "weekly", 50000.08),
        (100000.0, "annual", 100000.0),
    ])
    def test_various_conversions(self, value, price_type, expected):
        result = normalize_to_annual(value, price_type)
        assert result == pytest.approx(expected, rel=0.01)


class TestNormalizeRange:
    """Tests for normalize_range function."""
    
    def test_hourly_range_to_annual(self):
        result = normalize_range((25.0, 35.0), "hourly")
        assert result == (52000.0, 72800.0)
    
    def test_monthly_range_to_annual(self):
        result = normalize_range((4000.0, 5000.0), "monthly")
        assert result == (48000.0, 60000.0)
    
    def test_range_with_none_min(self):
        result = normalize_range((None, 50.0), "hourly")
        assert result == (None, 104000.0)
    
    def test_range_with_none_max(self):
        result = normalize_range((30.0, None), "hourly")
        assert result == (62400.0, None)
    
    def test_both_none(self):
        result = normalize_range((None, None), "annual")
        assert result == (None, None)
    
    def test_custom_hours_per_year(self):
        result = normalize_range((40.0, 50.0), "hourly", hours_per_year=2000)
        assert result == (80000.0, 100000.0)


class TestIsValidRange:
    """Tests for is_valid_range function."""
    
    def test_valid_range(self):
        assert is_valid_range((50000.0, 75000.0)) is True
    
    def test_equal_values(self):
        assert is_valid_range((50000.0, 50000.0)) is True
    
    def test_invalid_range(self):
        assert is_valid_range((75000.0, 50000.0)) is False
    
    def test_none_min(self):
        assert is_valid_range((None, 75000.0)) is True
    
    def test_none_max(self):
        assert is_valid_range((50000.0, None)) is True
    
    def test_both_none(self):
        assert is_valid_range((None, None)) is True


class TestEstimateFromType:
    """Tests for estimate_from_type function."""
    
    def test_hourly_estimate(self):
        result = estimate_from_type("hourly")
        assert result == 30 * 2080  # 62,400
    
    def test_hourly_estimate_custom_hours(self):
        result = estimate_from_type("hourly", hours_per_year=2000)
        assert result == 30 * 2000  # 60,000
    
    def test_monthly_estimate(self):
        result = estimate_from_type("monthly")
        assert result == 5000 * 12  # 60,000
    
    def test_annual_estimate(self):
        result = estimate_from_type("annual")
        assert result == 60000
    
    def test_unknown_type(self):
        result = estimate_from_type("unknown")
        assert result is None
    
    def test_invalid_type(self):
        result = estimate_from_type("invalid")
        assert result is None