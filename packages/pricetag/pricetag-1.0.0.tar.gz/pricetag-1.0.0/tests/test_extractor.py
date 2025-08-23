"""Integration tests for the PriceExtractor class."""

import time
from typing import List

import pytest

from pricetag import PriceExtractor, PriceResult


class TestBasicExtraction:
    """Tests for basic price extraction functionality."""
    
    def test_simple_annual_salary(self):
        extractor = PriceExtractor()
        text = "The position offers $50,000 per year"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == 50000.0
        assert results[0]['type'] == 'annual'
        assert results[0]['confidence'] >= 0.8
        assert results[0]['normalized_annual'] == 50000.0
    
    def test_hourly_rate(self):
        extractor = PriceExtractor()
        text = "Paying $25/hour for this role"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == 25.0
        assert results[0]['type'] == 'hourly'
        assert results[0]['normalized_annual'] == 52000.0  # 25 * 2080
    
    def test_salary_range(self):
        extractor = PriceExtractor()
        text = "Salary range: $50k-$75k annually"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == (50000.0, 75000.0)
        assert results[0]['is_range'] is True
        assert results[0]['type'] == 'annual'
        assert results[0]['normalized_annual'] == (50000.0, 75000.0)
    
    def test_no_currency_symbol(self):
        extractor = PriceExtractor()
        text = "Compensation: 50k annually"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == 50000.0
        assert results[0]['type'] == 'annual'
    
    def test_monthly_salary(self):
        extractor = PriceExtractor()
        text = "Monthly salary of $5,000"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == 5000.0
        assert results[0]['type'] == 'monthly'
        assert results[0]['normalized_annual'] == 60000.0  # 5000 * 12


class TestRealJobPostings:
    """Tests with realistic job posting text."""
    
    @pytest.fixture
    def job_postings(self):
        return [
            {
                'text': """
                Senior Software Engineer
                San Francisco, CA
                
                We're looking for an experienced engineer to join our team.
                Base salary: $150,000 - $200,000 annually
                Equity: 0.1% - 0.5%
                Benefits: Health, dental, vision, 401k
                """,
                'expected_count': 1,
                'expected_value': (150000.0, 200000.0),
                'expected_type': 'annual'
            },
            {
                'text': """
                Data Scientist Position
                
                Competitive compensation package:
                - Base: $120k-$140k
                - Annual bonus: up to $30k
                - Sign-on bonus: $10,000
                
                Requirements: PhD preferred, 5+ years experience
                """,
                'expected_count': 3,
                'expected_base': (120000.0, 140000.0)
            },
            {
                'text': """
                Part-time Developer Needed
                
                $50-75/hour depending on experience
                Approximately 20 hours per week
                Remote work available
                """,
                'expected_count': 1,
                'expected_value': (50.0, 75.0),
                'expected_type': 'hourly'
            },
            {
                'text': """
                Marketing Manager
                
                Offering six figures plus benefits
                Performance bonuses available
                Relocation assistance provided
                """,
                'expected_count': 1,
                'expected_value': (100000, 999999),
                'expected_contextual': True
            },
            {
                'text': """
                Entry Level Analyst
                
                Starting at $45,000 with regular reviews
                Quick progression to $55k+ within first year
                Great learning opportunity
                """,
                'expected_count': 2,
                'expected_first_value': (45000.0, None)
            }
        ]
    
    def test_job_posting_extraction(self, job_postings):
        extractor = PriceExtractor()
        
        for posting in job_postings:
            results = extractor.extract(posting['text'])
            
            # Check expected count
            assert len(results) >= posting['expected_count']
            
            # Check specific expectations
            if 'expected_value' in posting:
                assert results[0]['value'] == posting['expected_value']
            
            if 'expected_type' in posting:
                assert results[0]['type'] == posting['expected_type']
            
            if 'expected_base' in posting:
                # Check if the first result matches the expected base salary
                # (assuming base salary is typically mentioned first)
                assert results[0]['value'] == posting['expected_base']
            
            if 'expected_contextual' in posting:
                # Contextual terms should have lower confidence
                assert results[0]['confidence'] < 0.95
            
            if 'expected_first_value' in posting:
                assert results[0]['value'] == posting['expected_first_value']


class TestConfigurationOptions:
    """Tests for various configuration options."""
    
    def test_min_confidence_filter(self):
        extractor_high = PriceExtractor(min_confidence=0.9)
        extractor_low = PriceExtractor(min_confidence=0.3)
        
        text = "Salary is competitive"  # Low confidence contextual term
        
        results_high = extractor_high.extract(text)
        results_low = extractor_low.extract(text)
        
        assert len(results_high) == 0  # Filtered out
        assert len(results_low) > 0    # Included
    
    def test_include_contextual_toggle(self):
        extractor_with = PriceExtractor(include_contextual=True)
        extractor_without = PriceExtractor(include_contextual=False)
        
        text = "Looking for six figures, ideally $120k"
        
        results_with = extractor_with.extract(text)
        results_without = extractor_without.extract(text)
        
        assert len(results_with) == 2  # Both contextual and numeric
        assert len(results_without) == 1  # Only numeric
        assert results_without[0]['value'] == 120000.0
    
    def test_normalize_to_annual_toggle(self):
        extractor_norm = PriceExtractor(normalize_to_annual=True)
        extractor_no_norm = PriceExtractor(normalize_to_annual=False)
        
        text = "$30/hour"
        
        results_norm = extractor_norm.extract(text)
        results_no_norm = extractor_no_norm.extract(text)
        
        assert results_norm[0]['normalized_annual'] == 62400.0
        assert results_no_norm[0]['normalized_annual'] is None
    
    def test_custom_thresholds(self):
        extractor = PriceExtractor(min_salary=50000, max_salary=200000)
        
        text = "Salaries: $30,000, $100,000, $500,000"
        results = extractor.extract(text)
        
        # Check flags
        assert 'below_minimum' in results[0]['flags']
        assert len(results[1]['flags']) == 0  # Within range
        assert 'above_maximum' in results[2]['flags']
    
    def test_custom_hours_per_year(self):
        extractor = PriceExtractor(assume_hours_per_year=2000)
        
        text = "$50/hour"
        results = extractor.extract(text)
        
        assert results[0]['normalized_annual'] == 100000.0  # 50 * 2000
    
    def test_fast_mode(self):
        extractor_fast = PriceExtractor(fast_mode=True)
        extractor_normal = PriceExtractor(fast_mode=False)
        
        # Text without price indicators
        text = "This is just regular text with no prices"
        
        results_fast = extractor_fast.extract(text)
        results_normal = extractor_normal.extract(text)
        
        assert len(results_fast) == 0
        assert len(results_normal) == 0
    
    def test_max_results_limit(self):
        extractor = PriceExtractor(max_results_per_text=2)
        
        text = "$50k $60k $70k $80k $90k"
        results = extractor.extract(text)
        
        assert len(results) <= 2


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_input(self):
        extractor = PriceExtractor()
        assert extractor.extract("") == []
        assert extractor.extract("   ") == []
    
    def test_none_input(self):
        extractor = PriceExtractor()
        assert extractor.extract(None) == []
    
    def test_non_string_input(self):
        extractor = PriceExtractor()
        assert extractor.extract(123) == []
        assert extractor.extract([]) == []
        assert extractor.extract({}) == []
    
    def test_very_long_text(self):
        extractor = PriceExtractor()
        # Create text longer than 1MB
        long_text = "Salary $50,000 " * 100000
        results = extractor.extract(long_text)
        assert len(results) > 0  # Should still work
    
    def test_malformed_prices(self):
        extractor = PriceExtractor()
        
        test_cases = [
            ("Salary is $", []),  # Incomplete
            ("Pay: $$$", []),  # Multiple dollar signs
            ("Amount: $50k*", 1),  # With asterisk (should clean)
            ("($75,000)", 1),  # In parentheses (should clean)
            ("$50k¹", 1),  # With superscript (should clean)
        ]
        
        for text, expected in test_cases:
            results = extractor.extract(text)
            if isinstance(expected, int):
                assert len(results) == expected
            else:
                assert results == expected
    
    def test_overlapping_matches(self):
        extractor = PriceExtractor()
        text = "Salary $50,000 to $75,000 per year"
        results = extractor.extract(text)
        
        # Should detect range, not individual amounts
        assert len(results) == 1
        assert results[0]['is_range'] is True
    
    def test_invalid_range(self):
        extractor = PriceExtractor()
        text = "Range: $75k-$50k"  # Backwards range
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert 'invalid_range' in results[0]['flags']
    
    def test_ambiguous_amounts(self):
        extractor = PriceExtractor()
        text = "Paying $50 for this project"
        results = extractor.extract(text)
        
        if len(results) > 0:
            # Should flag as potentially ambiguous
            assert results[0]['type'] == 'unknown' or \
                   'ambiguous_type' in results[0].get('flags', [])
    
    def test_hint_type(self):
        extractor = PriceExtractor()
        text = "Compensation: 75"  # Ambiguous number
        
        results_no_hint = extractor.extract(text)
        results_annual = extractor.extract(text, hint_type='annual')
        results_hourly = extractor.extract(text, hint_type='hourly')
        
        if len(results_annual) > 0:
            assert results_annual[0]['type'] == 'annual'
        if len(results_hourly) > 0:
            assert results_hourly[0]['type'] == 'hourly'


class TestBatchProcessing:
    """Tests for batch processing functionality."""
    
    def test_extract_batch(self):
        extractor = PriceExtractor()
        texts = [
            "Salary: $50,000",
            "Hourly rate: $25/hr",
            "No prices here",
            "Range: $60k-$80k"
        ]
        
        results_batch = extractor.extract_batch(texts)
        
        assert len(results_batch) == 4
        assert len(results_batch[0]) == 1
        assert results_batch[0][0]['value'] == 50000.0
        assert len(results_batch[1]) == 1
        assert results_batch[1][0]['value'] == 25.0
        assert len(results_batch[2]) == 0
        assert len(results_batch[3]) == 1
        assert results_batch[3][0]['is_range'] is True
    
    def test_batch_with_hint(self):
        extractor = PriceExtractor()
        texts = ["75", "100", "125"]
        
        results = extractor.extract_batch(texts, hint_type='hourly')
        
        for result_list in results:
            if len(result_list) > 0:
                assert result_list[0]['type'] == 'hourly'
    
    def test_batch_performance(self):
        extractor = PriceExtractor(fast_mode=True)
        
        # Create 1000 sample texts
        texts = []
        for i in range(1000):
            if i % 3 == 0:
                texts.append(f"Salary: ${50000 + i * 100}")
            elif i % 3 == 1:
                texts.append(f"Rate: ${25 + i}/hour")
            else:
                texts.append("No salary information provided")
        
        start_time = time.time()
        results = extractor.extract_batch(texts)
        elapsed_time = time.time() - start_time
        
        # Should process 1000 texts in under 1 second
        assert elapsed_time < 1.0
        assert len(results) == 1000
        
        # Verify some results
        assert results[0][0]['value'] == 50000.0
        assert results[1][0]['value'] == 26.0


class TestConsistencyValidation:
    """Tests for consistency validation across multiple results."""
    
    def test_consistent_prices(self):
        extractor = PriceExtractor()
        text = "Base salary: $80,000, with bonus up to $20,000"
        results = extractor.extract(text)
        
        # Should not flag as inconsistent
        for result in results:
            assert 'potential_inconsistency' not in result.get('flags', [])
    
    def test_inconsistent_prices(self):
        extractor = PriceExtractor()
        text = "Salary: $50,000 or $500,000 depending on role"
        results = extractor.extract(text)
        
        # Should flag large discrepancy
        if len(results) == 2:
            flags_combined = results[0].get('flags', []) + results[1].get('flags', [])
            assert 'potential_inconsistency' in flags_combined


class TestComplexPatterns:
    """Tests for complex price patterns."""
    
    def test_approximate_values(self):
        extractor = PriceExtractor()
        text = "Approximately $100,000 per year"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['is_range'] is True
        assert 'approximate' in results[0].get('flags', [])
        # Should be ±10% range
        assert results[0]['value'][0] == pytest.approx(90000, rel=0.01)
        assert results[0]['value'][1] == pytest.approx(110000, rel=0.01)
    
    def test_up_to_pattern(self):
        extractor = PriceExtractor()
        text = "Bonus up to $50,000"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == (None, 50000.0)
    
    def test_starting_at_pattern(self):
        extractor = PriceExtractor()
        text = "Starting at $60k with growth potential"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == (60000.0, None)
    
    def test_plus_notation(self):
        extractor = PriceExtractor()
        text = "Earning potential: $100k+"
        results = extractor.extract(text)
        
        assert len(results) == 1
        assert results[0]['value'] == (100000.0, None)