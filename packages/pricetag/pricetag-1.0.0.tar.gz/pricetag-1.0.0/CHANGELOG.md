# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-08-21

### Added
- Initial release of pricetag library
- Core price extraction functionality for unstructured text
- Support for various price formats:
  - Currency symbols ($)
  - Abbreviated numbers (50k, 1.5m)
  - Ranges ($50k-$75k)
  - Hourly/annual/monthly rates
  - Contextual terms (six figures, competitive, DOE)
- Automatic normalization to annual USD amounts
- Confidence scoring for each extraction
- Comprehensive validation and sanity checks
- Batch processing support for high-volume operations
- Pure Python implementation with zero dependencies
- Type hints throughout the codebase
- Comprehensive test suite with 140+ tests

### Features
- High performance: processes 1000+ documents per second
- Smart pattern recognition with pre-compiled regex
- Number parsing cache for efficiency
- Fast mode for bulk processing
- Configurable extraction parameters
- Result deduplication and consistency validation

### Technical
- Python 3.13+ support
- Full type annotations
- 100% pure Python - no external dependencies
- Thread-safe implementation