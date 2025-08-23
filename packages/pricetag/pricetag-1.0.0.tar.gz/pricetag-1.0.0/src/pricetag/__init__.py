"""
pricetag - A pure-Python library for extracting price and currency information
from text.

Pure Python library for extracting price and currency information from
unstructured text, with a focus on salary data in job postings.

Example:
    >>> from pricetag import PriceExtractor
    >>> extractor = PriceExtractor()
    >>> results = extractor.extract("Salary: $50,000 - $75,000 per year")
    >>> print(results[0]['value'])
    (50000.0, 75000.0)
"""

from .extractor import PriceExtractor
from .types import Config, PriceResult, PriceType

__version__ = "1.0.0"
__author__ = "Michelle Pellon"
__email__ = "mgracepellon@gmail.com"
__license__ = "MIT"

__all__ = [
    "PriceExtractor",
    "PriceResult",
    "PriceType",
    "Config",
]
