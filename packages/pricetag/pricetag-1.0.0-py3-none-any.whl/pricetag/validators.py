"""Validation functions for price values."""


def is_below_minimum(value: float, threshold: float) -> bool:
    """
    Check if a value is below the minimum threshold.

    Args:
        value: Value to check
        threshold: Minimum threshold

    Returns:
        True if value is below threshold
    """
    return value < threshold


def is_above_maximum(value: float, threshold: float) -> bool:
    """
    Check if a value is above the maximum threshold.

    Args:
        value: Value to check
        threshold: Maximum threshold

    Returns:
        True if value is above threshold
    """
    return value > threshold


def is_reasonable_salary(value: float) -> bool:
    """
    Common sense check for salary values.

    Args:
        value: Annual salary value

    Returns:
        True if value seems reasonable for an annual salary
    """
    # Reasonable annual salary range: $10K - $10M
    return 10000 <= value <= 10000000


def is_valid_hourly_rate(value: float) -> bool:
    """
    Check if an hourly rate is within reasonable bounds.

    Args:
        value: Hourly rate

    Returns:
        True if rate is reasonable
    """
    # Reasonable hourly rate: $7 (near minimum wage) to $500
    return 7 <= value <= 500


def is_valid_monthly_salary(value: float) -> bool:
    """
    Check if a monthly salary is within reasonable bounds.

    Args:
        value: Monthly salary

    Returns:
        True if salary is reasonable
    """
    # Reasonable monthly salary: $500 to $100K
    return 500 <= value <= 100000


def validate_price_value(
    value: float | tuple[float, float],
    min_threshold: float,
    max_threshold: float,
    price_type: str,
) -> list[str]:
    """
    Validate a price value and return flags for any issues.

    Args:
        value: Single value or (min, max) range
        min_threshold: Minimum acceptable value
        max_threshold: Maximum acceptable value
        price_type: Type of price (hourly, annual, etc.)

    Returns:
        List of validation flags
    """
    flags = []

    # Handle ranges
    if isinstance(value, tuple):
        min_val, max_val = value
        values_to_check = []

        if min_val is not None:
            values_to_check.append(min_val)
        if max_val is not None:
            values_to_check.append(max_val)

        # Check each value in the range
        for val in values_to_check:
            val_flags = validate_single_value(
                val, min_threshold, max_threshold, price_type
            )
            flags.extend(val_flags)

        # Check range consistency
        if min_val is not None and max_val is not None:
            if max_val < min_val:
                if "invalid_range" not in flags:
                    flags.append("invalid_range")

    else:
        # Single value
        flags = validate_single_value(value, min_threshold, max_threshold, price_type)

    return flags


def validate_single_value(
    value: float, min_threshold: float, max_threshold: float, price_type: str
) -> list[str]:
    """
    Validate a single price value.

    Args:
        value: Value to validate
        min_threshold: Minimum acceptable value
        max_threshold: Maximum acceptable value
        price_type: Type of price

    Returns:
        List of validation flags
    """
    flags = []

    # Check against configured thresholds
    if is_below_minimum(value, min_threshold):
        flags.append("below_minimum")

    if is_above_maximum(value, max_threshold):
        flags.append("above_maximum")

    # Type-specific validation
    if price_type == "hourly":
        if not is_valid_hourly_rate(value):
            if "unreasonable_hourly_rate" not in flags:
                flags.append("unreasonable_hourly_rate")

    elif price_type == "monthly":
        if not is_valid_monthly_salary(value):
            if "unreasonable_monthly_salary" not in flags:
                flags.append("unreasonable_monthly_salary")

    elif price_type == "annual":
        if not is_reasonable_salary(value):
            if "unreasonable_annual_salary" not in flags:
                flags.append("unreasonable_annual_salary")

    return flags


def validate_consistency(results: list[dict]) -> list[dict]:
    """
    Check consistency across multiple price extractions from the same text.

    This function looks for large discrepancies between prices that might
    indicate extraction errors.

    Args:
        results: List of price results

    Returns:
        Updated results with consistency flags
    """
    if len(results) < 2:
        return results

    # Get all normalized annual values
    annual_values = []
    for result in results:
        if result.get("normalized_annual") is not None:
            val = result["normalized_annual"]
            if isinstance(val, tuple):
                # For ranges, use the average
                min_val, max_val = val
                if min_val is not None and max_val is not None:
                    annual_values.append((min_val + max_val) / 2)
                elif max_val is not None:
                    annual_values.append(max_val)
                elif min_val is not None:
                    annual_values.append(min_val)
            else:
                annual_values.append(val)

    if len(annual_values) < 2:
        return results

    # Check for large discrepancies (more than 10x difference)
    min_annual = min(annual_values)
    max_annual = max(annual_values)

    if min_annual > 0 and max_annual / min_annual >= 10:
        # Flag results with extreme values
        for i, result in enumerate(results):
            if result.get("normalized_annual") is not None:
                val = result["normalized_annual"]
                check_val = val

                if isinstance(val, tuple):
                    min_val, max_val = val
                    if min_val is not None and max_val is not None:
                        check_val = (min_val + max_val) / 2
                    elif max_val is not None:
                        check_val = max_val
                    elif min_val is not None:
                        check_val = min_val

                # Flag if this value is an outlier
                if check_val == min_annual or check_val == max_annual:
                    if "potential_inconsistency" not in result.get("flags", []):
                        if "flags" not in result:
                            result["flags"] = []
                        result["flags"].append("potential_inconsistency")

    return results
