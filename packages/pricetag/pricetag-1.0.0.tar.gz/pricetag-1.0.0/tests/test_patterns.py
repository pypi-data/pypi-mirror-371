"""Tests for pattern matching functions."""

import pytest

from pricetag.patterns import (
    detect_price_type,
    extract_range_values,
    find_contextual_prices,
    find_numeric_prices,
    has_price_indicators,
    infer_range_from_context,
    parse_number,
)


class TestParseNumber:
    """Tests for parse_number function."""
    
    @pytest.mark.parametrize("input_text,expected", [
        ("50000", 50000.0),
        ("50,000", 50000.0),
        ("50k", 50000.0),
        ("50K", 50000.0),
        ("1.5k", 1500.0),
        ("2.5m", 2500000.0),
        ("2M", 2000000.0),
        ("100", 100.0),
        ("1,234,567", 1234567.0),
    ])
    def test_parse_number_various_formats(self, input_text, expected):
        assert parse_number(input_text) == expected
    
    def test_parse_number_with_whitespace(self):
        assert parse_number("  50k  ") == 50000.0
    
    def test_parse_number_caching(self):
        # First call should cache
        result1 = parse_number("75k")
        # Second call should use cache
        result2 = parse_number("75k")
        assert result1 == result2 == 75000.0


class TestHasPriceIndicators:
    """Tests for has_price_indicators function."""
    
    def test_dollar_sign(self):
        assert has_price_indicators("The price is $50")
    
    def test_abbreviated_number(self):
        assert has_price_indicators("Salary: 50k annually")
    
    def test_comma_separated(self):
        assert has_price_indicators("Earning 50,000 per year")
    
    def test_salary_keywords(self):
        assert has_price_indicators("competitive salary offered")
    
    def test_no_indicators(self):
        assert not has_price_indicators("This is just regular text")


class TestFindNumericPrices:
    """Tests for find_numeric_prices function."""
    
    def test_single_amount_with_dollar(self):
        results = find_numeric_prices("Salary is $50,000 per year")
        assert len(results) == 1
        assert results[0]['value'] == 50000.0
        assert results[0]['is_range'] is False
    
    def test_range_with_dash(self):
        results = find_numeric_prices("$50k-$75k annually")
        assert len(results) == 1
        assert results[0]['value'] == (50000.0, 75000.0)
        assert results[0]['is_range'] is True
    
    def test_range_with_to(self):
        results = find_numeric_prices("50,000 to 75,000")
        assert len(results) == 1
        assert results[0]['value'] == (50000.0, 75000.0)
    
    def test_up_to_pattern(self):
        results = find_numeric_prices("up to $100k")
        assert len(results) == 1
        assert results[0]['value'] == (None, 100000.0)
        assert results[0]['pattern_type'] == 'up_to'
    
    def test_starting_at_pattern(self):
        results = find_numeric_prices("starting at $60,000")
        assert len(results) == 1
        assert results[0]['value'] == (60000.0, None)
        assert results[0]['pattern_type'] == 'starting_at'
    
    def test_plus_pattern(self):
        results = find_numeric_prices("$150k+")
        assert len(results) == 1
        assert results[0]['value'] == (150000.0, None)
        assert results[0]['pattern_type'] == 'plus'
    
    def test_between_pattern(self):
        results = find_numeric_prices("between $40k and $60k")
        assert len(results) == 1
        assert results[0]['value'] == (40000.0, 60000.0)
        assert results[0]['pattern_type'] == 'between'
    
    def test_approximate_pattern(self):
        results = find_numeric_prices("approximately $50,000")
        assert len(results) == 1
        assert results[0]['value'][0] == pytest.approx(45000.0)  # 50k * 0.9
        assert results[0]['value'][1] == pytest.approx(55000.0)  # 50k * 1.1
        assert 'approximate' in results[0].get('flags', [])
    
    def test_multiple_prices(self):
        text = "Base salary $80k, bonus up to $20k"
        results = find_numeric_prices(text)
        assert len(results) == 2
        assert results[0]['value'] == 80000.0
        assert results[1]['value'] == (None, 20000.0)
    
    def test_max_results_limit(self):
        text = "$50k $60k $70k $80k $90k"
        results = find_numeric_prices(text, max_results=3)
        assert len(results) <= 3


class TestDetectPriceType:
    """Tests for detect_price_type function."""
    
    @pytest.mark.parametrize("text,context,expected", [
        ("$50/hour", "", "hourly"),
        ("$50k/year", "", "annual"),
        ("$4000/month", "", "monthly"),
        ("$1000/week", "", "weekly"),
        ("$50,000", "annual salary", "annual"),
        ("$25", "hourly rate", "hourly"),
        ("$50k", "", "unknown"),
    ])
    def test_detect_price_type(self, text, context, expected):
        assert detect_price_type(text, context) == expected


class TestExtractRangeValues:
    """Tests for extract_range_values function."""
    
    def test_two_numbers(self):
        result = extract_range_values("$50k-$75k")
        assert result == (50000.0, 75000.0)
    
    def test_up_to_single_number(self):
        result = extract_range_values("up to $100,000")
        assert result == (None, 100000.0)
    
    def test_starting_at_single_number(self):
        result = extract_range_values("starting at $60k")
        assert result == (60000.0, None)
    
    def test_plus_notation(self):
        result = extract_range_values("$80k+")
        assert result == (80000.0, None)
    
    def test_no_numbers(self):
        result = extract_range_values("no numbers here")
        assert result is None


class TestInferRangeFromContext:
    """Tests for infer_range_from_context function."""
    
    def test_up_to_context(self):
        result = infer_range_from_context("up to", 100000)
        assert result == (None, 100000)
    
    def test_starting_at_context(self):
        result = infer_range_from_context("starting at", 50000)
        assert result == (50000, None)
    
    def test_approximately_context(self):
        result = infer_range_from_context("approximately", 60000)
        assert result == (54000, 66000)  # ±10%
    
    def test_no_context(self):
        result = infer_range_from_context("regular text", 50000)
        assert result is None


class TestFindContextualPrices:
    """Tests for find_contextual_prices function."""
    
    def test_six_figures(self):
        results = find_contextual_prices("Looking for six figures")
        assert len(results) == 1
        assert results[0]['value'] == (100000, 999999)
        assert results[0]['pattern_type'] == 'six_figures'
    
    def test_low_six_figures(self):
        results = find_contextual_prices("Offering low six figures")
        assert len(results) == 1
        assert results[0]['value'] == (100000, 300000)
    
    def test_mid_five_figures(self):
        results = find_contextual_prices("mid five figures expected")
        assert len(results) == 1
        assert results[0]['value'] == (30000, 70000)
    
    def test_competitive_salary(self):
        results = find_contextual_prices("competitive salary")
        assert len(results) == 1
        assert results[0]['value'] is None
        assert 'requires_market_data' in results[0]['flags']
    
    def test_doe(self):
        results = find_contextual_prices("Salary DOE")
        assert len(results) == 1
        assert results[0]['value'] is None
        assert 'experience_dependent' in results[0]['flags']
    
    def test_tbd(self):
        results = find_contextual_prices("Compensation TBD")
        assert len(results) == 1
        assert results[0]['value'] is None
        assert 'unspecified' in results[0]['flags']
    
    def test_multiple_contextual(self):
        text = "six figures, competitive, DOE"
        results = find_contextual_prices(text)
        assert len(results) == 3