"""Main PriceExtractor class for extracting prices from text."""

import re
from typing import Optional, Any

from .normalizer import is_valid_range, normalize_to_annual
from .patterns import (
    detect_price_type,
    find_contextual_prices,
    find_numeric_prices,
    has_price_indicators,
)
from .types import PriceResult, PriceType
from .validators import validate_consistency, validate_price_value


class PriceExtractor:
    """
    Extracts price information from unstructured text.

    Example:
        >>> extractor = PriceExtractor()
        >>> results = extractor.extract("The salary is $50,000 per year")
        >>> print(results[0]['value'])
        50000.0
    """

    def __init__(
        self,
        min_confidence: float = 0.5,
        include_contextual: bool = True,
        normalize_to_annual: bool = True,
        min_salary: float = 10000,
        max_salary: float = 10000000,
        assume_hours_per_year: int = 2080,
        fast_mode: bool = False,
        max_results_per_text: int | None = None,
    ):
        """
        Initialize the PriceExtractor with configuration options.

        Args:
            min_confidence: Minimum confidence score to include results (0.0-1.0)
            include_contextual: Whether to extract contextual terms like "six figures"
            normalize_to_annual: Whether to convert all values to annual amounts
            min_salary: Minimum reasonable salary for validation
            max_salary: Maximum reasonable salary for validation
            assume_hours_per_year: Hours per year for hourly→annual conversion
            fast_mode: Skip some validation for better performance
            max_results_per_text: Limit number of results per text for performance
        """
        self.min_confidence = min_confidence
        self.include_contextual = include_contextual
        self.normalize_to_annual = normalize_to_annual
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.assume_hours_per_year = assume_hours_per_year
        self.fast_mode = fast_mode
        self.max_results_per_text = max_results_per_text

    def _get_surrounding_context(
        self, text: str, position: tuple[int, int], window: int = 50
    ) -> str:
        """
        Extract surrounding context from a match position.

        Args:
            text: Full text
            position: (start, end) position of match
            window: Number of characters before/after to include

        Returns:
            Context string
        """
        start = max(0, position[0] - window)
        end = min(len(text), position[1] + window)
        return text[start:end]

    def _has_salary_context(self, text: str) -> bool:
        """Check if text contains salary-related keywords."""
        salary_keywords = [
            "salary",
            "compensation",
            "pay",
            "wage",
            "earning",
            "income",
            "remuneration",
            "package",
            "base",
            "bonus",
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in salary_keywords)

    def _has_currency_indicator(self, text: str) -> bool:
        """Check if text contains currency symbols or text."""
        return bool(re.search(r"[$]|USD|usd|dollars?", text))

    def _has_time_indicator(self, text: str) -> bool:
        """Check if text contains time period markers."""
        time_patterns = [
            r"/(?:hour|hr|year|yr|month|mo|week|wk)",
            r"per\s+(?:hour|year|month|week)",
            r"(?:hourly|annually|monthly|weekly)",
            r"p/[hywm]",
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in time_patterns)

    def _is_reasonable_value(
        self, value: float | tuple[float, float], price_type: str
    ) -> bool:
        """
        Check if a value is within reasonable bounds for its type.

        Args:
            value: Single value or range tuple
            price_type: Type of price (hourly, annual, etc.)

        Returns:
            True if value seems reasonable
        """
        # Extract single value or max of range for checking
        if isinstance(value, tuple):
            # For ranges, check if either endpoint is reasonable
            check_values = [v for v in value if v is not None]
            if not check_values:
                return False
            check_value = max(check_values)
        else:
            check_value = value

        # Type-specific bounds
        if price_type == "hourly":
            return 7 <= check_value <= 500
        elif price_type == "monthly":
            return 500 <= check_value <= 100000
        elif price_type == "annual":
            return self.min_salary <= check_value <= self.max_salary
        else:
            # For unknown type, use annual bounds as default
            return self.min_salary <= check_value <= self.max_salary

    def _calculate_confidence(
        self, match_data: dict, text: str, hint_type: Optional[str] = None
    ) -> float:
        """
        Calculate confidence score for a price extraction.

        Args:
            match_data: Raw match data from patterns
            text: Full input text
            hint_type: Optional type hint

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        if match_data.get("confidence_modifier"):
            # Use the confidence modifier from contextual terms
            confidence = match_data["confidence_modifier"]
        elif match_data.get("is_contextual"):
            confidence = 0.7
        else:
            confidence = 1.0

        # Get context around the match
        context = self._get_surrounding_context(text, match_data["position"])

        # Boost for currency indicator
        if self._has_currency_indicator(match_data["raw_text"]):
            confidence = min(1.0, confidence + 0.1)

        # Boost for explicit time period
        if self._has_time_indicator(match_data["raw_text"]):
            confidence = min(1.0, confidence + 0.1)

        # Boost for salary context
        if self._has_salary_context(context):
            confidence = min(1.0, confidence + 0.1)

        # Check if value is reasonable
        if match_data.get("value") is not None:
            price_type = detect_price_type(match_data["raw_text"], context)
            if hint_type and price_type == "unknown":
                price_type = hint_type

            if self._is_reasonable_value(match_data["value"], price_type):
                confidence = min(1.0, confidence + 0.1)
            else:
                # Penalize unreasonable values
                confidence = max(0.3, confidence - 0.2)

        # Boost if hint_type matches detected type
        if hint_type:
            detected_type = detect_price_type(match_data["raw_text"], context)
            if detected_type == hint_type:
                confidence = min(1.0, confidence + 0.1)
            elif detected_type != "unknown":
                # Penalize if hint conflicts with clear type indicator
                confidence = max(0.4, confidence - 0.1)

        # Special handling for non-value results
        if match_data.get("value") is None:
            # These are things like "competitive", "DOE"
            confidence = 0.3

        return float(confidence)

    def _create_result(
        self, match_data: dict, text: str, hint_type: Optional[str] = None
    ) -> Optional[PriceResult]:
        """
        Create a PriceResult object from raw match data.

        Args:
            match_data: Dictionary from pattern matching functions
            text: Full input text for context extraction
            hint_type: Optional type hint for disambiguation

        Returns:
            PriceResult object or None if confidence too low
        """
        # Calculate confidence score
        confidence = self._calculate_confidence(match_data, text, hint_type)

        # Check if confidence meets threshold
        if confidence < self.min_confidence:
            return None

        # Get context for type detection
        context = self._get_surrounding_context(text, match_data["position"])

        # Detect price type
        price_type = detect_price_type(match_data["raw_text"], context)

        # Apply hint if provided and type is unknown
        if price_type == "unknown" and hint_type:
            price_type = hint_type

        # Handle non-value results (e.g., "competitive", "TBD")
        if match_data.get("value") is None:
            # Create a result with no value but with flags
            result_no_val: PriceResult = {
                "value": 0.0,  # Placeholder since we need a value
                "raw_text": match_data["raw_text"],
                "position": match_data["position"],
                "type": "unknown",
                "confidence": confidence,
                "normalized_annual": None,
                "currency": "USD",
                "is_range": False,
                "flags": match_data.get("flags", []),
            }
            return result_no_val

        # Initialize flags list
        flags = match_data.get("flags", []).copy()

        # Check if range is valid (for ranges)
        if match_data.get("is_range") and isinstance(match_data["value"], tuple):
            if not is_valid_range(match_data["value"]):
                flags.append("invalid_range")

        # Validate the value
        validation_flags = validate_price_value(
            match_data["value"], self.min_salary, self.max_salary, price_type
        )
        flags.extend(validation_flags)

        # Calculate normalized annual value if configured
        normalized_annual = None
        if self.normalize_to_annual and match_data.get("value") is not None:
            normalized_annual = normalize_to_annual(
                match_data["value"], price_type, self.assume_hours_per_year
            )

        # Create the result
        # Ensure price_type is a valid PriceType
        valid_price_type: PriceType = "unknown"
        if price_type in ("hourly", "annual", "monthly", "base", "bonus", "unknown"):
            valid_price_type = price_type  # type: ignore
        
        result_with_val: PriceResult = {
            "value": match_data["value"],
            "raw_text": match_data["raw_text"],
            "position": match_data["position"],
            "type": valid_price_type,
            "confidence": confidence,
            "normalized_annual": normalized_annual,  # type: ignore
            "currency": "USD",
            "is_range": match_data.get("is_range", False),
            "flags": flags,
        }

        return result_with_val

    def _sanitize_input(self, text: Any) -> str | None:
        """
        Sanitize and validate input text.

        Args:
            text: Input to sanitize

        Returns:
            Sanitized string or None if invalid
        """
        # Handle None
        if text is None:
            return None

        # Handle non-string types
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return None

        # Handle empty strings
        if not text or not text.strip():
            return None

        # Truncate extremely long text (>1MB)
        if len(text) > 1_000_000:
            text = text[:1_000_000]

        # Handle various encodings by replacing problematic characters
        # This ensures we don't crash on unusual Unicode
        text = text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

        return str(text)

    def _detect_overlaps(self, results: list[PriceResult]) -> list[PriceResult]:
        """
        Detect and flag overlapping price extractions.

        Args:
            results: List of price results

        Returns:
            Results with overlap flags added
        """
        if len(results) < 2:
            return results

        # Sort by position for easier overlap detection
        sorted_results = sorted(results, key=lambda r: r["position"][0])

        for i in range(len(sorted_results)):
            for j in range(i + 1, len(sorted_results)):
                # Check if positions overlap
                if sorted_results[i]["position"][1] > sorted_results[j]["position"][0]:
                    # Add overlap flag to both
                    if "overlapping" not in sorted_results[i]["flags"]:
                        sorted_results[i]["flags"].append("overlapping")
                    if "overlapping" not in sorted_results[j]["flags"]:
                        sorted_results[j]["flags"].append("overlapping")

        return sorted_results

    def _detect_ambiguity(self, result: PriceResult, text: str) -> PriceResult:
        """
        Detect ambiguous price patterns and add appropriate flags.

        Args:
            result: Price result to check
            text: Full text for context

        Returns:
            Result with ambiguity flags if applicable
        """
        # Check for ambiguous small numbers (could be hourly or thousands)
        if isinstance(result["value"], float) and result["value"] < 1000:
            if result["type"] == "unknown":
                # $50 could be $50/hour or $50k
                context = self._get_surrounding_context(text, result["position"], 100)

                # Look for thousand indicators
                if re.search(r"thousand|k\s|per\s+year|annual", context, re.IGNORECASE):
                    if "ambiguous_scale" not in result["flags"]:
                        result["flags"].append("ambiguous_scale")
                # Look for hourly indicators
                elif not re.search(r"hour|hr|hourly", context, re.IGNORECASE):
                    if "ambiguous_type" not in result["flags"]:
                        result["flags"].append("ambiguous_type")

        return result

    def _handle_special_formats(self, text: str) -> str:
        """
        Pre-process text to handle special formatting cases.

        Args:
            text: Input text

        Returns:
            Processed text
        """
        # Handle prices in parentheses by removing parentheses
        # e.g., "($50k)" -> "$50k"
        text = re.sub(r"\((\$?\d+[kKmM]?(?:,\d{3})*)\)", r"\1", text)

        # Handle footnoted prices by removing superscript markers
        # e.g., "$50k¹" -> "$50k"
        text = re.sub(r"([0-9kKmM])[¹²³⁴⁵⁶⁷⁸⁹⁰*†‡§¶]", r"\1", text)

        # Normalize plus signs (multiple plus signs to single)
        text = re.sub(r"\+{2,}", "+", text)

        # Handle asterisked prices
        # e.g., "$50k*" -> "$50k"
        text = re.sub(r"(\$?\d+[kKmM]?(?:,\d{3})*)\*+", r"\1", text)

        return text

    def _deduplicate_results(self, results: list[PriceResult]) -> list[PriceResult]:
        """
        Remove duplicate extractions, keeping highest confidence version.

        Args:
            results: List of price results

        Returns:
            Deduplicated results
        """
        if len(results) < 2:
            return results

        # Group by position and value
        unique_results: dict[tuple, PriceResult] = {}

        for result in results:
            # Create a key based on position and value
            value_key: tuple[Any, Any]
            if isinstance(result["value"], tuple):
                value_key = result["value"]  # type: ignore
            else:
                value_key = (result["value"], None)  # type: ignore

            key = (result["position"], value_key)  # type: ignore

            # Keep the result with highest confidence
            if (
                key not in unique_results
                or result["confidence"] > unique_results[key]["confidence"]
            ):
                unique_results[key] = result

        return list(unique_results.values())

    def extract(self, text: str, hint_type: Optional[str] = None) -> list[PriceResult]:
        """
        Extract price information from text.

        Args:
            text: Input text to analyze
            hint_type: Optional type hint ("annual", "hourly", etc.) for disambiguation

        Returns:
            List of PriceResult objects sorted by position
        """
        # Input sanitization
        sanitized_text = self._sanitize_input(text)
        if sanitized_text is None:
            return []
        text = sanitized_text

        # Handle special formats
        text = self._handle_special_formats(text)

        results: list[PriceResult] = []

        # Quick pre-check for performance
        if self.fast_mode:
            if not has_price_indicators(text):
                return []

        # Error recovery wrapper
        try:
            # Find numeric prices
            try:
                numeric_matches = find_numeric_prices(text, self.max_results_per_text)
                for match in numeric_matches:
                    # Early termination if we have enough results
                    if (
                        self.max_results_per_text
                        and len(results) >= self.max_results_per_text
                    ):
                        break

                    result = self._create_result(match, text, hint_type)
                    if result:
                        # Skip ambiguity detection in fast mode
                        if not self.fast_mode:
                            result = self._detect_ambiguity(result, text)
                        results.append(result)
            except Exception as e:
                # Log but don't crash - continue with contextual prices
                pass

            # Find contextual prices if configured
            if self.include_contextual:
                try:
                    contextual_matches = find_contextual_prices(text)
                    for match in contextual_matches:
                        result = self._create_result(match, text, hint_type)
                        if result:
                            results.append(result)
                except Exception as e:
                    # Log but don't crash - continue with what we have
                    pass

            # Detect overlaps
            results = self._detect_overlaps(results)

            # Deduplicate
            results = self._deduplicate_results(results)

            # Sort by position for consistent ordering
            results.sort(key=lambda r: r["position"][0])

            # Check consistency across results
            results = validate_consistency(results)  # type: ignore

        except Exception as e:
            # Final fallback - return what we have so far
            pass

        return results

    def extract_batch(
        self, texts: list[str], hint_type: Optional[str] = None, parallel: bool = False
    ) -> list[list[PriceResult]]:
        """
        Extract prices from multiple texts efficiently.

        Args:
            texts: List of texts to process
            hint_type: Optional type hint for all texts
            parallel: Whether to process in parallel (future enhancement)

        Returns:
            List of result lists, one per input text
        """
        results_batch = []

        # Import patterns once for the batch
        from .patterns import _number_cache

        for text in texts:
            # Process each text
            results = self.extract(text, hint_type)
            results_batch.append(results)

            # Clear cache periodically to prevent memory growth
            if len(_number_cache) > 5000:
                _number_cache.clear()

        return results_batch
