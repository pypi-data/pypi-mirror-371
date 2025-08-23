"""Regular expression patterns for price extraction."""

import re
from typing import Any, Optional

# Performance optimization: Pre-compile common sub-patterns
_DIGIT = r"\d"
_DIGITS = r"\d+"

# Cache for parsed numbers to avoid re-parsing
_number_cache: dict[str, float] = {}

# Currency patterns
CURRENCY_SYMBOL = r"\$"
CURRENCY_TEXT = r"(?:USD|usd|dollars?)"
OPTIONAL_CURRENCY = rf"(?:{CURRENCY_SYMBOL}|{CURRENCY_TEXT}\s*)?"

# Number format patterns
NUMBER_WITH_COMMAS = r"\d{1,3}(?:,\d{3})+"
NUMBER_NO_COMMAS = r"\d+"
DECIMAL_NUMBER = r"\d+\.?\d*"

# Abbreviated number patterns (50k, 50K, 1.5m)
ABBREVIATED_NUMBER = rf"{DECIMAL_NUMBER}[kKmM]"

# Combined number pattern - Order matters! Most specific first
NUMBER = rf"(?:{NUMBER_WITH_COMMAS}|{ABBREVIATED_NUMBER}|{NUMBER_NO_COMMAS})"

# Time period patterns
HOURLY_INDICATORS = r"(?:/hour|/hr|per\s+hour|hourly|p/h)"
ANNUAL_INDICATORS = r"(?:/year|/yr|per\s+year|annually|per\s+annum|p/a)"
MONTHLY_INDICATORS = r"(?:/month|/mo|per\s+month|monthly|p/m)"
WEEKLY_INDICATORS = r"(?:/week|/wk|per\s+week|weekly|p/w)"

TIME_PERIOD = rf"(?:{HOURLY_INDICATORS}|{ANNUAL_INDICATORS}|{MONTHLY_INDICATORS}|{WEEKLY_INDICATORS})"

# Single amount patterns
AMOUNT_WITH_SYMBOL = rf"{CURRENCY_SYMBOL}\s*{NUMBER}"
AMOUNT_WITH_TEXT_CURRENCY = rf"{NUMBER}\s*{CURRENCY_TEXT}"
AMOUNT_NO_CURRENCY = rf"{NUMBER}"

# Single amount with optional time period
SINGLE_AMOUNT = rf"(?:{AMOUNT_WITH_SYMBOL}|{AMOUNT_WITH_TEXT_CURRENCY}|{AMOUNT_NO_CURRENCY})(?:\s*{TIME_PERIOD})?"

# Range separators - expanded set
RANGE_SEPARATOR = r"(?:\s*[-–—]\s*|\s+to\s+|\s*-\s*)"
RANGE_SEPARATOR_EXTENDED = r"(?:\s*[-–—]\s*|\s+to\s+|\s+through\s+|\s*-\s*|\s+and\s+)"

# Range patterns
RANGE_WITH_SYMBOL = (
    rf"{CURRENCY_SYMBOL}\s*{NUMBER}{RANGE_SEPARATOR}{CURRENCY_SYMBOL}?\s*{NUMBER}"
)
RANGE_WITH_TEXT_CURRENCY = rf"{NUMBER}{RANGE_SEPARATOR}{NUMBER}\s*{CURRENCY_TEXT}"
RANGE_NO_CURRENCY = rf"{NUMBER}{RANGE_SEPARATOR}{NUMBER}"

# Range with optional time period
RANGE_AMOUNT = rf"(?:{RANGE_WITH_SYMBOL}|{RANGE_WITH_TEXT_CURRENCY}|{RANGE_NO_CURRENCY})(?:\s*{TIME_PERIOD})?"

# Contextual term patterns
SIX_FIGURES_PATTERN = r"(?:low|mid|high)?\s*six[\s-]?figures?"
FIVE_FIGURES_PATTERN = r"(?:low|mid|high)?\s*five[\s-]?figures?"
SEVEN_FIGURES_PATTERN = r"seven[\s-]?figures?"

COMPETITIVE_TERMS = r"(?:competitive|market\s+rate|negotiable|commensurate)"
EXPERIENCE_TERMS = r"(?:DOE|depending\s+on\s+experience|based\s+on\s+experience)"
UNSPECIFIED_TERMS = r"(?:TBD|to\s+be\s+determined|open|flexible)"

# Special range patterns - expanded
UP_TO_PATTERN = rf"(?:up\s+to|maximum\s+of|max|no\s+more\s+than)\s+{SINGLE_AMOUNT}"
STARTING_AT_PATTERN = rf"(?:starting\s+at|from|minimum\s+of|min|at\s+least|no\s+less\s+than)\s+{SINGLE_AMOUNT}"
PLUS_PATTERN = rf"{SINGLE_AMOUNT}\++"
APPROXIMATELY_PATTERN = rf"(?:approximately|about|around|circa|~)\s*{SINGLE_AMOUNT}"

# Between X and Y pattern - expanded
BETWEEN_PATTERN = (
    rf"(?:between|from)\s+{SINGLE_AMOUNT}\s+(?:and|to|through)\s+{SINGLE_AMOUNT}"
)

# New patterns for complex ranges
RANGE_WITH_WORDS = rf"(?:from\s+)?{SINGLE_AMOUNT}\s+(?:up\s+)?to\s+{SINGLE_AMOUNT}"

# Compile all patterns
SINGLE_AMOUNT_RE = re.compile(SINGLE_AMOUNT, re.IGNORECASE)
RANGE_AMOUNT_RE = re.compile(RANGE_AMOUNT, re.IGNORECASE)
UP_TO_RE = re.compile(UP_TO_PATTERN, re.IGNORECASE)
STARTING_AT_RE = re.compile(STARTING_AT_PATTERN, re.IGNORECASE)
PLUS_RE = re.compile(PLUS_PATTERN, re.IGNORECASE)
BETWEEN_RE = re.compile(BETWEEN_PATTERN, re.IGNORECASE)
APPROXIMATELY_RE = re.compile(APPROXIMATELY_PATTERN, re.IGNORECASE)
RANGE_WITH_WORDS_RE = re.compile(RANGE_WITH_WORDS, re.IGNORECASE)

# Contextual patterns compiled
SIX_FIGURES_RE = re.compile(SIX_FIGURES_PATTERN, re.IGNORECASE)
FIVE_FIGURES_RE = re.compile(FIVE_FIGURES_PATTERN, re.IGNORECASE)
SEVEN_FIGURES_RE = re.compile(SEVEN_FIGURES_PATTERN, re.IGNORECASE)
COMPETITIVE_RE = re.compile(COMPETITIVE_TERMS, re.IGNORECASE)
EXPERIENCE_RE = re.compile(EXPERIENCE_TERMS, re.IGNORECASE)
UNSPECIFIED_RE = re.compile(UNSPECIFIED_TERMS, re.IGNORECASE)

# Time period detection patterns (for classification)
HOURLY_RE = re.compile(HOURLY_INDICATORS, re.IGNORECASE)
ANNUAL_RE = re.compile(ANNUAL_INDICATORS, re.IGNORECASE)
MONTHLY_RE = re.compile(MONTHLY_INDICATORS, re.IGNORECASE)
WEEKLY_RE = re.compile(WEEKLY_INDICATORS, re.IGNORECASE)

# Contextual term value mappings
FIGURE_MAPPINGS = {
    "five_figures": {
        "base": (10000, 99999),
        "low": (10000, 30000),
        "mid": (30000, 70000),
        "high": (70000, 99999),
    },
    "six_figures": {
        "base": (100000, 999999),
        "low": (100000, 300000),
        "mid": (300000, 700000),
        "high": (700000, 999999),
    },
    "seven_figures": {
        "base": (1000000, 9999999),
        "low": (1000000, 3000000),
        "mid": (3000000, 7000000),
        "high": (7000000, 9999999),
    },
}

# Relative term flag mappings
RELATIVE_TERM_FLAGS = {
    "competitive": ["requires_market_data", "competitive"],
    "market_rate": ["requires_market_data", "market_rate"],
    "negotiable": ["negotiable"],
    "commensurate": ["experience_dependent", "commensurate"],
    "doe": ["experience_dependent"],
    "depending_on_experience": ["experience_dependent"],
    "tbd": ["unspecified"],
    "open": ["unspecified", "open"],
    "flexible": ["unspecified", "flexible"],
}


def estimate_from_contextual(
    term: str, modifier: str | None = None
) -> tuple[float, float] | None:
    """
    Estimate a value range from contextual terms like "six figures".

    Args:
        term: The contextual term (e.g., "six_figures")
        modifier: Optional modifier (e.g., "low", "mid", "high")

    Returns:
        Estimated (min, max) range or None
    """
    if term in FIGURE_MAPPINGS:
        mapping = FIGURE_MAPPINGS[term]
        if modifier and modifier in mapping:
            return mapping[modifier]
        return mapping["base"]

    # Industry-specific estimates could be added here
    # For example, "competitive" might map to industry averages

    return None


def extract_range_values(
    match_text: str, separator_pattern: str | None = None
) -> tuple[float | None, float | None] | None:
    """
    Extract min and max values from a range match.

    Args:
        match_text: The matched range text
        separator_pattern: Optional specific separator pattern to use

    Returns:
        (min, max) tuple or None if extraction fails
    """
    # Find all numbers in the text
    numbers = re.findall(NUMBER, match_text)

    if len(numbers) < 1:
        return None
    elif len(numbers) == 1:
        # Single number - determine if it's min or max based on context
        value = parse_number(numbers[0])

        # Check for "up to", "maximum" patterns
        if re.search(
            r"(?:up\s+to|maximum|max|no\s+more\s+than)", match_text, re.IGNORECASE
        ):
            return (None, value)
        # Check for "starting at", "minimum" patterns
        elif re.search(
            r"(?:starting|from|minimum|min|at\s+least|no\s+less\s+than)",
            match_text,
            re.IGNORECASE,
        ):
            return (value, None)
        # Check for "plus" pattern
        elif re.search(r"\++$", match_text):
            return (value, None)
        else:
            # Default to single value, not a range
            return None
    else:
        # Multiple numbers - take first and last as range
        min_val = parse_number(numbers[0])
        max_val = parse_number(numbers[-1])

        # Validate the range
        if max_val < min_val:
            # Might be reversed, but we'll flag it
            pass

        return (min_val, max_val)


def infer_range_from_context(
    text: str, value: float
) -> tuple[float | None, float | None] | None:
    """
    Infer a range from contextual clues around a single value.

    Args:
        text: The text containing the value
        value: The numeric value found

    Returns:
        Inferred (min, max) range or None
    """
    text_lower = text.lower()

    # "up to X" patterns
    if any(
        phrase in text_lower
        for phrase in ["up to", "maximum", "max of", "no more than"]
    ):
        return (None, value)

    # "starting at X" patterns
    if any(
        phrase in text_lower
        for phrase in [
            "starting at",
            "from",
            "minimum",
            "min of",
            "at least",
            "no less than",
        ]
    ):
        return (value, None)

    # "X+" patterns
    if re.search(rf"{re.escape(str(value))}\++", text):
        return (value, None)

    # "approximately X" patterns - add ±10% range
    if any(
        phrase in text_lower for phrase in ["approximately", "about", "around", "circa"]
    ):
        return (value * 0.9, value * 1.1)

    return None


def parse_number(text: str) -> float:
    """
    Parse a number string into a float value.

    Handles:
    - Numbers with commas: "50,000" -> 50000.0
    - Abbreviated numbers: "50k" -> 50000.0, "1.5m" -> 1500000.0
    - Regular numbers: "50000" -> 50000.0

    Args:
        text: Number string to parse

    Returns:
        Float value of the number
    """
    # Check cache first
    if text in _number_cache:
        return _number_cache[text]

    # Remove any whitespace
    text = text.strip()

    result = None
    # Check for abbreviated format
    if text and text[-1].lower() == "k":
        # Remove 'k' and multiply by 1000
        base = text[:-1].replace(",", "")
        result = float(base) * 1000
    elif text and text[-1].lower() == "m":
        # Remove 'm' and multiply by 1,000,000
        base = text[:-1].replace(",", "")
        result = float(base) * 1000000
    else:
        # Regular number, just remove commas
        result = float(text.replace(",", ""))

    # Cache the result (limit cache size for memory)
    if len(_number_cache) < 1000:
        _number_cache[text] = result

    return result


def has_price_indicators(text: str) -> bool:
    """
    Quick check to see if text likely contains prices.

    Args:
        text: Text to check

    Returns:
        True if text likely contains prices
    """
    # Quick checks for common price indicators
    if "$" in text:
        return True
    if re.search(r"\d+[kKmM](?:\s|$)", text):
        return True
    if re.search(r"\d{1,3},\d{3}", text):
        return True
    if re.search(
        r"(?:salary|compensation|pay|wage|hour|annual|month)", text, re.IGNORECASE
    ):
        return True
    return False


def find_numeric_prices(text: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """
    Find all numeric price patterns in text.

    Args:
        text: Input text to search
        max_results: Optional limit on number of results

    Returns:
        List of dictionaries containing match information
    """
    # Quick pre-check
    if not has_price_indicators(text):
        return []

    results: list[dict[str, Any]] = []

    # Check for "between X and Y" patterns first (most specific)
    for match in BETWEEN_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break

        match_text = match.group(0)
        range_values = extract_range_values(match_text)
        if range_values:
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": range_values,
                    "pattern_type": "between",
                }
            )

    # Check for range patterns
    for match in RANGE_AMOUNT_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        # Skip if this was already captured by between pattern
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        numbers = re.findall(NUMBER, match_text)
        if len(numbers) >= 2:
            min_val = parse_number(numbers[0])
            max_val = parse_number(numbers[1])
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": (min_val, max_val),
                    "pattern_type": "range",
                }
            )

    # Check for word-based ranges (e.g., "$50k to $75k")
    for match in RANGE_WITH_WORDS_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        range_values = extract_range_values(match_text)
        if range_values:
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": range_values,
                    "pattern_type": "range_words",
                }
            )

    # Check for "up to" patterns
    for match in UP_TO_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        range_values = extract_range_values(match_text)
        if range_values:
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": range_values,
                    "pattern_type": "up_to",
                }
            )

    # Check for "starting at" patterns
    for match in STARTING_AT_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        range_values = extract_range_values(match_text)
        if range_values:
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": range_values,
                    "pattern_type": "starting_at",
                }
            )

    # Check for "plus" patterns (e.g., "$100k+")
    for match in PLUS_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        range_values = extract_range_values(match_text)
        if range_values:
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": range_values,
                    "pattern_type": "plus",
                }
            )

    # Check for "approximately" patterns
    for match in APPROXIMATELY_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        numbers = re.findall(NUMBER, match_text)
        if numbers:
            value = parse_number(numbers[0])
            # Create a ±10% range for approximate values
            range_values = (value * 0.9, value * 1.1)
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": True,
                    "value": range_values,
                    "pattern_type": "approximate",
                    "flags": ["approximate"],
                }
            )

    # Check for single amounts
    for match in SINGLE_AMOUNT_RE.finditer(text):
        if max_results and len(results) >= max_results:
            break
        # Skip if this position was already captured
        if any(r["position"][0] <= match.start() < r["position"][1] for r in results):
            continue

        match_text = match.group(0)
        numbers = re.findall(NUMBER, match_text)
        if numbers:
            value = parse_number(numbers[0])
            results.append(
                {
                    "raw_text": match_text,
                    "position": (match.start(), match.end()),
                    "is_range": False,
                    "value": value,
                    "pattern_type": "single",
                }
            )
    
    # Sort results by position for consistent ordering
    results.sort(key=lambda r: r["position"][0])
    return results


def detect_price_type(text: str, context: str = "") -> str:
    """
    Detect the type of price based on text and surrounding context.

    Args:
        text: The matched price text
        context: Surrounding context (optional)

    Returns:
        Price type: "hourly", "annual", "monthly", "weekly", or "unknown"
    """
    combined = text + " " + context

    if HOURLY_RE.search(combined):
        return "hourly"
    elif ANNUAL_RE.search(combined):
        return "annual"
    elif MONTHLY_RE.search(combined):
        return "monthly"
    elif WEEKLY_RE.search(combined):
        return "weekly"

    # Check for contextual clues in the wider context
    context_lower = context.lower()
    if any(word in context_lower for word in ["salary", "annual", "year", "yearly"]):
        return "annual"
    elif any(word in context_lower for word in ["hourly", "hour", "hr"]):
        return "hourly"
    elif any(word in context_lower for word in ["monthly", "month"]):
        return "monthly"

    return "unknown"


def find_contextual_prices(text: str) -> list[dict[str, Any]]:
    """
    Find contextual (non-numeric) price indicators in text.

    Args:
        text: Input text to search

    Returns:
        List of dictionaries containing match information
    """
    results: list[dict[str, Any]] = []

    # Check for figure-based descriptions
    for match in SIX_FIGURES_RE.finditer(text):
        match_text = match.group(0).lower()

        # Determine modifier
        modifier = None
        if "low" in match_text:
            modifier = "low"
        elif "mid" in match_text:
            modifier = "mid"
        elif "high" in match_text:
            modifier = "high"

        value_range = estimate_from_contextual("six_figures", modifier)

        results.append(
            {
                "raw_text": match.group(0),
                "position": (match.start(), match.end()),
                "is_range": True,
                "value": value_range,
                "pattern_type": "six_figures",
                "is_contextual": True,
                "confidence_modifier": 0.7,  # Contextual terms have lower base confidence
            }
        )

    for match in FIVE_FIGURES_RE.finditer(text):
        match_text = match.group(0).lower()

        # Determine modifier
        modifier = None
        if "low" in match_text:
            modifier = "low"
        elif "mid" in match_text:
            modifier = "mid"
        elif "high" in match_text:
            modifier = "high"

        value_range = estimate_from_contextual("five_figures", modifier)

        results.append(
            {
                "raw_text": match.group(0),
                "position": (match.start(), match.end()),
                "is_range": True,
                "value": value_range,
                "pattern_type": "five_figures",
                "is_contextual": True,
                "confidence_modifier": 0.7,
            }
        )

    for match in SEVEN_FIGURES_RE.finditer(text):
        value_range = estimate_from_contextual("seven_figures")

        results.append(
            {
                "raw_text": match.group(0),
                "position": (match.start(), match.end()),
                "is_range": True,
                "value": value_range,
                "pattern_type": "seven_figures",
                "is_contextual": True,
                "confidence_modifier": 0.7,
            }
        )

    # Check for relative terms (these don't have numeric values but get flags)
    for match in COMPETITIVE_RE.finditer(text):
        match_text = match.group(0).lower()

        # Determine which specific term was matched
        term_type = "competitive"  # default
        if "market" in match_text:
            term_type = "market_rate"
        elif "negotiable" in match_text:
            term_type = "negotiable"
        elif "commensurate" in match_text:
            term_type = "commensurate"

        flags = RELATIVE_TERM_FLAGS.get(term_type, ["competitive"])

        results.append(
            {
                "raw_text": match.group(0),
                "position": (match.start(), match.end()),
                "is_range": False,
                "value": None,
                "pattern_type": term_type,
                "is_contextual": True,
                "flags": flags,
                "confidence_modifier": 0.3,  # Very low confidence for non-numeric terms
            }
        )

    for match in EXPERIENCE_RE.finditer(text):
        match_text = match.group(0).lower()

        # Determine specific type
        if "doe" in match_text:
            flags = RELATIVE_TERM_FLAGS["doe"]
        else:
            flags = RELATIVE_TERM_FLAGS["depending_on_experience"]

        results.append(
            {
                "raw_text": match.group(0),
                "position": (match.start(), match.end()),
                "is_range": False,
                "value": None,
                "pattern_type": "experience_dependent",
                "is_contextual": True,
                "flags": flags,
                "confidence_modifier": 0.3,
            }
        )

    for match in UNSPECIFIED_RE.finditer(text):
        match_text = match.group(0).lower()

        # Determine specific type
        term_type = "unspecified"
        if "tbd" in match_text:
            term_type = "tbd"
        elif "open" in match_text:
            term_type = "open"
        elif "flexible" in match_text:
            term_type = "flexible"

        flags = RELATIVE_TERM_FLAGS.get(term_type, ["unspecified"])

        results.append(
            {
                "raw_text": match.group(0),
                "position": (match.start(), match.end()),
                "is_range": False,
                "value": None,
                "pattern_type": term_type,
                "is_contextual": True,
                "flags": flags,
                "confidence_modifier": 0.3,
            }
        )

    return results
