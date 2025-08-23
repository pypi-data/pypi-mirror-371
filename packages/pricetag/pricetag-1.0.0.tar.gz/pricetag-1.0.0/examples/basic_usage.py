#!/usr/bin/env python3
"""
Basic usage examples for the pricetag library.

This script demonstrates common use cases for extracting price
information from text.
"""

from pricetag import PriceExtractor


def basic_extraction():
    """Basic price extraction examples."""
    print("=" * 50)
    print("BASIC EXTRACTION")
    print("=" * 50)
    
    extractor = PriceExtractor()
    
    # Simple annual salary
    text = "The position offers $75,000 per year with excellent benefits"
    results = extractor.extract(text)
    print(f"\nText: {text}")
    print(f"Results: {results[0]['value']} ({results[0]['type']})")
    print(f"Confidence: {results[0]['confidence']:.2f}")
    
    # Hourly rate
    text = "Paying $45/hour for experienced developers"
    results = extractor.extract(text)
    print(f"\nText: {text}")
    print(f"Results: ${results[0]['value']}/hour")
    print(f"Annual equivalent: ${results[0]['normalized_annual']:,.0f}")
    
    # Salary range
    text = "Salary range: $60k-$80k depending on experience"
    results = extractor.extract(text)
    print(f"\nText: {text}")
    print(f"Results: ${results[0]['value'][0]:,.0f} - ${results[0]['value'][1]:,.0f}")


def contextual_extraction():
    """Extract contextual salary terms."""
    print("\n" + "=" * 50)
    print("CONTEXTUAL EXTRACTION")
    print("=" * 50)
    
    extractor = PriceExtractor(include_contextual=True)
    
    # Six figures
    text = "Looking for senior engineers, offering low six figures"
    results = extractor.extract(text)
    print(f"\nText: {text}")
    if results:
        print(f"Results: ${results[0]['value'][0]:,.0f} - ${results[0]['value'][1]:,.0f}")
        print(f"Confidence: {results[0]['confidence']:.2f}")
    
    # Competitive salary
    text = "Competitive salary with great benefits and equity"
    results = extractor.extract(text)
    print(f"\nText: {text}")
    if results:
        print(f"Flags: {results[0].get('flags', [])}")


def real_job_posting():
    """Process a realistic job posting."""
    print("\n" + "=" * 50)
    print("REAL JOB POSTING")
    print("=" * 50)
    
    job_posting = """
    Senior Data Scientist - San Francisco
    
    We're seeking an experienced data scientist to join our growing team.
    
    Compensation:
    - Base salary: $140,000 - $180,000
    - Annual bonus: up to 20% of base
    - Equity: 0.05% - 0.15%
    - Sign-on bonus: $25,000
    
    Requirements:
    - MS/PhD in Computer Science, Statistics, or related field
    - 5+ years of industry experience
    - Strong Python and SQL skills
    """
    
    extractor = PriceExtractor()
    results = extractor.extract(job_posting)
    
    print("\nFound prices in job posting:")
    for i, result in enumerate(results, 1):
        if result.get('is_range'):
            if isinstance(result['value'], tuple):
                if result['value'][0] is not None and result['value'][1] is not None:
                    print(f"{i}. {result['raw_text']}: ${result['value'][0]:,.0f} - ${result['value'][1]:,.0f}")
                elif result['value'][1] is not None:
                    print(f"{i}. {result['raw_text']}: up to ${result['value'][1]:,.0f}")
                elif result['value'][0] is not None:
                    print(f"{i}. {result['raw_text']}: starting at ${result['value'][0]:,.0f}")
        else:
            print(f"{i}. {result['raw_text']}: ${result['value']:,.0f}")


def configuration_examples():
    """Demonstrate different configuration options."""
    print("\n" + "=" * 50)
    print("CONFIGURATION OPTIONS")
    print("=" * 50)
    
    text = "The role pays $35/hour, approximately 30 hours per week"
    
    # Default configuration
    extractor_default = PriceExtractor()
    results = extractor_default.extract(text)
    print(f"\nDefault extraction:")
    print(f"  Hourly: ${results[0]['value']}")
    print(f"  Annual (2080 hours): ${results[0]['normalized_annual']:,.0f}")
    
    # Custom hours per year
    extractor_custom = PriceExtractor(assume_hours_per_year=1560)  # 30 hrs/week
    results = extractor_custom.extract(text)
    print(f"\nCustom hours (1560/year):")
    print(f"  Hourly: ${results[0]['value']}")
    print(f"  Annual (1560 hours): ${results[0]['normalized_annual']:,.0f}")
    
    # Fast mode for performance
    extractor_fast = PriceExtractor(fast_mode=True, max_results_per_text=3)
    results = extractor_fast.extract(text)
    print(f"\nFast mode extraction:")
    print(f"  Results found: {len(results)}")


def batch_processing():
    """Process multiple texts efficiently."""
    print("\n" + "=" * 50)
    print("BATCH PROCESSING")
    print("=" * 50)
    
    job_texts = [
        "Software Engineer: $90,000 - $120,000",
        "Data Analyst: $60k-$75k plus bonus",
        "Product Manager: six figures",
        "Intern: $20/hour, summer position",
        "No salary information available"
    ]
    
    extractor = PriceExtractor()
    batch_results = extractor.extract_batch(job_texts)
    
    print("\nBatch processing results:")
    for i, (text, results) in enumerate(zip(job_texts, batch_results), 1):
        if results:
            print(f"{i}. {text[:30]}... → {len(results)} price(s) found")
        else:
            print(f"{i}. {text[:30]}... → No prices found")


def validation_examples():
    """Show validation and flag examples."""
    print("\n" + "=" * 50)
    print("VALIDATION AND FLAGS")
    print("=" * 50)
    
    extractor = PriceExtractor(min_salary=30000, max_salary=500000)
    
    test_cases = [
        "$15,000 per year",  # Below minimum
        "$1,000,000 annually",  # Above maximum
        "$75k-$50k",  # Invalid range
        "approximately $100,000",  # Approximate value
    ]
    
    for text in test_cases:
        results = extractor.extract(text)
        if results:
            print(f"\nText: {text}")
            print(f"  Value: {results[0]['value']}")
            print(f"  Flags: {results[0].get('flags', [])}")


def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("PRICETAG LIBRARY EXAMPLES")
    print("=" * 50)
    
    basic_extraction()
    contextual_extraction()
    real_job_posting()
    configuration_examples()
    batch_processing()
    validation_examples()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()