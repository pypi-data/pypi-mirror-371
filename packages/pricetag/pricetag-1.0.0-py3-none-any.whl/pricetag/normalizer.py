"""Functions for normalizing prices to annual USD amounts."""

from typing import Optional

# Conversion constants
HOURS_PER_YEAR = 2080  # Standard full-time hours (40 hours/week * 52 weeks)
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52


def normalize_to_annual(
    value: float | tuple[float, float] | tuple[float | None, float | None],
    price_type: str,
    hours_per_year: int = HOURS_PER_YEAR,
) -> float | tuple[float, float] | tuple[float | None, float | None]:
    """
    Convert a price value to annual USD amount.

    Args:
        value: Single value or (min, max) range tuple
        price_type: Type of price (hourly, monthly, weekly, annual, unknown)
        hours_per_year: Hours per year for hourly conversion (default 2080)

    Returns:
        Normalized annual value(s)
    """
    if isinstance(value, tuple):
        return normalize_range(value, price_type, hours_per_year)  # type: ignore

    # Single value normalization
    if price_type == "hourly":
        return value * hours_per_year
    elif price_type == "monthly":
        return value * MONTHS_PER_YEAR
    elif price_type == "weekly":
        return value * WEEKS_PER_YEAR
    elif price_type in ("annual", "unknown", "base", "bonus"):
        # Already annual or unknown, return as-is
        return value
    else:
        # Unrecognized type, return as-is
        return value


def normalize_range(
    value_range: tuple[float | None, float | None],
    price_type: str,
    hours_per_year: int = HOURS_PER_YEAR,
) -> tuple[float | None, float | None]:
    """
    Normalize a range of values to annual amounts.

    Args:
        value_range: (min, max) tuple, either can be None
        price_type: Type of price
        hours_per_year: Hours per year for hourly conversion

    Returns:
        Normalized (min, max) tuple
    """
    min_val, max_val = value_range

    # Normalize each component if present
    normalized_min: float | None = None
    normalized_max: float | None = None
    
    if min_val is not None:
        result = normalize_to_annual(min_val, price_type, hours_per_year)
        if isinstance(result, (int, float)):
            normalized_min = float(result)

    if max_val is not None:
        result = normalize_to_annual(max_val, price_type, hours_per_year)
        if isinstance(result, (int, float)):
            normalized_max = float(result)

    return (normalized_min, normalized_max)


def is_valid_range(value_range: tuple[float | None, float | None]) -> bool:
    """
    Check if a range has valid ordering (max >= min).

    Args:
        value_range: (min, max) tuple

    Returns:
        True if range is valid or has None values, False if inverted
    """
    min_val, max_val = value_range

    # If either is None, consider it valid
    if min_val is None or max_val is None:
        return True

    # Both values present, check ordering
    return max_val >= min_val


def estimate_from_type(
    price_type: str, hours_per_year: int = HOURS_PER_YEAR
) -> Optional[float]:
    """
    Estimate a reasonable default annual value for a given price type.

    This is used when we need to provide some value but don't have
    a specific number (e.g., for "competitive" salaries).

    Args:
        price_type: Type of price
        hours_per_year: Hours per year for calculations

    Returns:
        Estimated annual value or None
    """
    # These are rough US market estimates
    if price_type == "hourly":
        # Assume median hourly rate ~$30
        return 30 * hours_per_year
    elif price_type == "monthly":
        # Assume median monthly ~$5000
        return 5000 * MONTHS_PER_YEAR
    elif price_type == "annual":
        # Assume median annual ~$60000
        return 60000
    else:
        return None
