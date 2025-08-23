"""Tests for validation functions."""

import pytest

from pricetag.validators import (
    is_above_maximum,
    is_below_minimum,
    is_reasonable_salary,
    is_valid_hourly_rate,
    is_valid_monthly_salary,
    validate_consistency,
    validate_price_value,
    validate_single_value,
)


class TestBasicValidations:
    """Tests for basic validation functions."""
    
    def test_is_below_minimum(self):
        assert is_below_minimum(5000, 10000) is True
        assert is_below_minimum(15000, 10000) is False
        assert is_below_minimum(10000, 10000) is False
    
    def test_is_above_maximum(self):
        assert is_above_maximum(150000, 100000) is True
        assert is_above_maximum(50000, 100000) is False
        assert is_above_maximum(100000, 100000) is False
    
    def test_is_reasonable_salary(self):
        assert is_reasonable_salary(50000) is True
        assert is_reasonable_salary(500000) is True
        assert is_reasonable_salary(5000) is False
        assert is_reasonable_salary(50000000) is False
    
    def test_is_valid_hourly_rate(self):
        assert is_valid_hourly_rate(25) is True
        assert is_valid_hourly_rate(200) is True
        assert is_valid_hourly_rate(5) is False
        assert is_valid_hourly_rate(1000) is False
    
    def test_is_valid_monthly_salary(self):
        assert is_valid_monthly_salary(5000) is True
        assert is_valid_monthly_salary(50000) is True
        assert is_valid_monthly_salary(300) is False
        assert is_valid_monthly_salary(200000) is False


class TestValidateSingleValue:
    """Tests for validate_single_value function."""
    
    def test_below_minimum(self):
        flags = validate_single_value(5000, 10000, 100000, "annual")
        assert "below_minimum" in flags
    
    def test_above_maximum(self):
        flags = validate_single_value(200000, 10000, 100000, "annual")
        assert "above_maximum" in flags
    
    def test_unreasonable_hourly(self):
        flags = validate_single_value(5, 0, 1000, "hourly")
        assert "unreasonable_hourly_rate" in flags
    
    def test_unreasonable_monthly(self):
        flags = validate_single_value(300, 0, 1000000, "monthly")
        assert "unreasonable_monthly_salary" in flags
    
    def test_unreasonable_annual(self):
        flags = validate_single_value(5000, 0, 10000000, "annual")
        assert "unreasonable_annual_salary" in flags
    
    def test_valid_value(self):
        flags = validate_single_value(50000, 10000, 100000, "annual")
        assert len(flags) == 0
    
    @pytest.mark.parametrize("value,min_t,max_t,type_,expected_flags", [
        (5000, 10000, 100000, "annual", ["below_minimum", "unreasonable_annual_salary"]),
        (150000, 10000, 100000, "annual", ["above_maximum"]),
        (3, 0, 1000, "hourly", ["unreasonable_hourly_rate"]),
        (100, 0, 1000000, "monthly", ["unreasonable_monthly_salary"]),
    ])
    def test_various_validations(self, value, min_t, max_t, type_, expected_flags):
        flags = validate_single_value(value, min_t, max_t, type_)
        for flag in expected_flags:
            assert flag in flags


class TestValidatePriceValue:
    """Tests for validate_price_value function."""
    
    def test_single_value(self):
        flags = validate_price_value(50000, 10000, 100000, "annual")
        assert len(flags) == 0
    
    def test_valid_range(self):
        flags = validate_price_value((40000, 60000), 10000, 100000, "annual")
        assert len(flags) == 0
    
    def test_invalid_range(self):
        flags = validate_price_value((60000, 40000), 10000, 100000, "annual")
        assert "invalid_range" in flags
    
    def test_range_below_minimum(self):
        flags = validate_price_value((5000, 8000), 10000, 100000, "annual")
        assert "below_minimum" in flags
    
    def test_range_above_maximum(self):
        flags = validate_price_value((150000, 200000), 10000, 100000, "annual")
        assert "above_maximum" in flags
    
    def test_range_with_none_min(self):
        flags = validate_price_value((None, 50000), 10000, 100000, "annual")
        assert len(flags) == 0
    
    def test_range_with_none_max(self):
        flags = validate_price_value((50000, None), 10000, 100000, "annual")
        assert len(flags) == 0
    
    def test_mixed_range_issues(self):
        # Range where min is below threshold and max is above
        flags = validate_price_value((5000, 150000), 10000, 100000, "annual")
        assert "below_minimum" in flags
        assert "above_maximum" in flags


class TestValidateConsistency:
    """Tests for validate_consistency function."""
    
    def test_empty_results(self):
        results = validate_consistency([])
        assert results == []
    
    def test_single_result(self):
        results = [{
            'normalized_annual': 50000,
            'flags': []
        }]
        validated = validate_consistency(results)
        assert len(validated) == 1
        assert 'potential_inconsistency' not in validated[0]['flags']
    
    def test_consistent_results(self):
        results = [
            {'normalized_annual': 50000, 'flags': []},
            {'normalized_annual': 55000, 'flags': []},
            {'normalized_annual': 60000, 'flags': []},
        ]
        validated = validate_consistency(results)
        for result in validated:
            assert 'potential_inconsistency' not in result['flags']
    
    def test_inconsistent_results(self):
        results = [
            {'normalized_annual': 50000, 'flags': []},
            {'normalized_annual': 600000, 'flags': []},  # 12x difference
        ]
        validated = validate_consistency(results)
        # Both should be flagged as outliers
        assert any('potential_inconsistency' in r['flags'] for r in validated)
    
    def test_range_consistency(self):
        results = [
            {'normalized_annual': (50000, 70000), 'flags': []},
            {'normalized_annual': (55000, 65000), 'flags': []},
        ]
        validated = validate_consistency(results)
        for result in validated:
            assert 'potential_inconsistency' not in result.get('flags', [])
    
    def test_mixed_single_and_range(self):
        results = [
            {'normalized_annual': 60000, 'flags': []},
            {'normalized_annual': (55000, 65000), 'flags': []},
        ]
        validated = validate_consistency(results)
        for result in validated:
            assert 'potential_inconsistency' not in result.get('flags', [])
    
    def test_none_values_ignored(self):
        results = [
            {'normalized_annual': None, 'flags': []},
            {'normalized_annual': 50000, 'flags': []},
            {'normalized_annual': 55000, 'flags': []},
        ]
        validated = validate_consistency(results)
        for result in validated:
            assert 'potential_inconsistency' not in result.get('flags', [])
    
    def test_partial_range_values(self):
        results = [
            {'normalized_annual': (None, 100000), 'flags': []},
            {'normalized_annual': (50000, None), 'flags': []},
            {'normalized_annual': 75000, 'flags': []},
        ]
        validated = validate_consistency(results)
        for result in validated:
            assert 'potential_inconsistency' not in result.get('flags', [])