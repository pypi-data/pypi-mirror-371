"""Type definitions for the pricetag library."""

from typing import Literal, TypedDict

PriceType = Literal["hourly", "annual", "monthly", "base", "bonus", "unknown"]
"""Valid price type classifications."""


class PriceResult(TypedDict):
    """
    Represents an extracted price from text.

    Attributes:
        value: Single float value or tuple of (min, max) for ranges
        raw_text: Original matched text from the source
        position: Start and end character positions in source text
        type: Classification of the price (hourly, annual, etc.)
        confidence: Confidence score from 0.0 to 1.0
        normalized_annual: Value normalized to annual USD amount
        currency: Currency code (always "USD" in v1)
        is_range: Whether the value represents a range
        flags: List of validation/warning flags
    """

    value: float | tuple[float, float]
    raw_text: str
    position: tuple[int, int]
    type: PriceType
    confidence: float
    normalized_annual: float | tuple[float, float] | None
    currency: str
    is_range: bool
    flags: list[str]


class Config(TypedDict):
    """
    Configuration options for PriceExtractor.

    Attributes:
        min_confidence: Minimum confidence score to include results (0.0-1.0)
        include_contextual: Whether to extract contextual terms like "six figures"
        normalize_to_annual: Whether to convert all values to annual amounts
        min_salary: Minimum reasonable salary for validation
        max_salary: Maximum reasonable salary for validation
        assume_hours_per_year: Hours per year for hourly→annual conversion
    """

    min_confidence: float
    include_contextual: bool
    normalize_to_annual: bool
    min_salary: float
    max_salary: float
    assume_hours_per_year: int
