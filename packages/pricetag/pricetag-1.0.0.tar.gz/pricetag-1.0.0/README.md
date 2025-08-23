# Pricetag

A pure-Python library for extracting price and currency information from unstructured text, with a primary focus on salary data in job postings.

## Features

- **Zero Dependencies**: Uses only Python standard library
- **High Performance**: Processes 1000+ documents per second
- **Comprehensive Pattern Support**: 
  - Individual amounts: `$50,000`, `$50k`, `50k USD`
  - Ranges: `$50k-$75k`, `$50,000 to $75,000`
  - Hourly/Annual/Monthly rates: `$25/hour`, `$50k/year`, `$4k/month`
  - Contextual terms: `six figures`, `competitive`, `DOE`
- **Smart Normalization**: Converts all amounts to annual USD for easy comparison
- **Confidence Scoring**: Each extraction includes a confidence score
- **Validation & Sanity Checks**: Flags unusual or problematic values

## Installation

```bash
pip install pricetag
```

## Quick Start

```python
from pricetag import PriceExtractor

# Initialize the extractor
extractor = PriceExtractor()

# Extract prices from text
text = "Senior Engineer position paying $120,000 - $150,000 annually"
results = extractor.extract(text)

# Access the results
for result in results:
    print(f"Value: {result['value']}")
    print(f"Type: {result['type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Annual value: {result['normalized_annual']}")
```

## Configuration Options

```python
extractor = PriceExtractor(
    min_confidence=0.5,        # Minimum confidence score to include
    include_contextual=True,   # Extract terms like "six figures"
    normalize_to_annual=True,  # Convert to annual amounts
    min_salary=10000,          # Minimum reasonable salary
    max_salary=10000000,       # Maximum reasonable salary
    assume_hours_per_year=2080,# For hourly→annual conversion
    fast_mode=False,           # Enable for better performance
    max_results_per_text=None  # Limit number of results
)
```

## Examples

### Basic Salary Extraction
```python
text = "The position offers $75,000 per year with benefits"
results = extractor.extract(text)
# Returns: [{'value': 75000.0, 'type': 'annual', ...}]
```

### Hourly Rate with Normalization
```python
text = "Paying $45/hour for senior developers"
results = extractor.extract(text)
# Returns: [{'value': 45.0, 'type': 'hourly', 'normalized_annual': 93600.0, ...}]
```

### Salary Range
```python
text = "Salary range: $60k-$80k depending on experience"
results = extractor.extract(text)
# Returns: [{'value': (60000.0, 80000.0), 'is_range': True, ...}]
```

### Contextual Terms
```python
text = "Looking for someone with 5+ years experience, six figures"
results = extractor.extract(text)
# Returns: [{'value': (100000, 999999), 'type': 'unknown', 'confidence': 0.7, ...}]
```

### Multiple Prices
```python
text = "Base: $100k, Bonus: up to $30k, Equity: 0.5%"
results = extractor.extract(text)
# Returns multiple results with appropriate flags
```

### Batch Processing
```python
texts = [
    "Salary: $50,000",
    "Rate: $30/hour", 
    "Competitive pay"
]
results_batch = extractor.extract_batch(texts)
```

## Output Format

Each extraction returns a `PriceResult` dictionary:

```python
{
    'value': float | tuple[float, float],  # Single value or (min, max)
    'raw_text': str,                       # Original matched text
    'position': tuple[int, int],           # Character positions
    'type': str,                           # 'hourly', 'annual', 'monthly', etc.
    'confidence': float,                   # 0.0 to 1.0
    'normalized_annual': float | tuple,    # Annual USD amount
    'currency': str,                       # Always 'USD' in v1
    'is_range': bool,                      # True for ranges
    'flags': list[str]                     # Validation flags
}
```

### Validation Flags

- `invalid_range`: Max less than min
- `below_minimum`: Below configured threshold
- `above_maximum`: Above configured threshold
- `unreasonable_hourly_rate`: Outside $7-$500/hour
- `potential_inconsistency`: Large discrepancy with other prices
- `ambiguous_type`: Unclear if hourly/annual
- `approximate`: Estimated from "approximately"
- `requires_market_data`: Needs external data (e.g., "competitive")
- `experience_dependent`: Depends on experience (e.g., "DOE")

## Performance

The library is optimized for high-volume processing:

- Pre-compiled regex patterns
- Number parsing cache
- Quick pre-filtering
- Fast mode for bulk processing
- Batch processing support

```python
# Fast mode for high-volume processing
extractor = PriceExtractor(fast_mode=True, max_results_per_text=5)

# Process 1000 documents
texts = ["..." for _ in range(1000)]
results = extractor.extract_batch(texts)  # < 1 second
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=pricetag
```

## Limitations

- Currently supports USD only
- Optimized for US salary formats
- Context window limited to surrounding text
- Does not handle equity/stock compensation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Michelle Pellon - mgracepellon@gmail.com

## Acknowledgments

Built with pure Python for maximum compatibility and zero dependencies.