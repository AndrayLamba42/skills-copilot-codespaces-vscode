"""
Market research validation module.
Validates market research requests before sending to AI.
"""
from typing import Tuple, List, Optional
import re


class MarketResearchValidator:
    """Validates market research input data."""

    # Minimum and maximum lengths
    MIN_INDUSTRY_LENGTH = 2
    MAX_INDUSTRY_LENGTH = 100
    MIN_MARKET_LENGTH = 20
    MAX_MARKET_LENGTH = 5000

    # Valid research types
    VALID_RESEARCH_TYPES = ['competitive', 'pricing', 'economic', 'report']

    # Valid focus areas
    VALID_FOCUS_AREAS = ['competitiveness', 'pricing_analysis', 'economic_perspective', 'comprehensive']

    # Valid timeframes
    VALID_TIMEFRAMES = ['current', 'quarterly', 'yearly', 'historical']

    # Invalid patterns (common spam/noise)
    INVALID_PATTERNS = [
        r'^[^\w\s]+$',  # Only special characters
        r'^(.)\1+$',  # Repeated single character (e.g., "aaaa")
        r'^test\s*$',  # Just "test"
        r'^asdf',  # Common keyboard mashing
    ]

    @staticmethod
    def validate_industry(industry: str) -> Tuple[bool, Optional[str]]:
        """
        Validate industry field.

        Args:
            industry: Industry string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not industry:
            return False, "Industry is required"

        industry = industry.strip()

        # Length validation
        if len(industry) < MarketResearchValidator.MIN_INDUSTRY_LENGTH:
            return False, f"Industry must be at least {MarketResearchValidator.MIN_INDUSTRY_LENGTH} characters"

        if len(industry) > MarketResearchValidator.MAX_INDUSTRY_LENGTH:
            return False, f"Industry must be no more than {MarketResearchValidator.MAX_INDUSTRY_LENGTH} characters"

        # Check for invalid patterns
        for pattern in MarketResearchValidator.INVALID_PATTERNS:
            if re.match(pattern, industry, re.IGNORECASE):
                return False, "Industry appears to be invalid or spam"

        # Check for meaningful content (at least one letter)
        if not re.search(r'[a-zA-Z]', industry):
            return False, "Industry must contain at least one letter"

        return True, None

    @staticmethod
    def validate_market(market: str) -> Tuple[bool, Optional[str]]:
        """
        Validate market description field.

        Args:
            market: Market description string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not market:
            return False, "Market description is required"

        market = market.strip()

        # Length validation
        if len(market) < MarketResearchValidator.MIN_MARKET_LENGTH:
            return False, f"Market description must be at least {MarketResearchValidator.MIN_MARKET_LENGTH} characters"

        if len(market) > MarketResearchValidator.MAX_MARKET_LENGTH:
            return False, f"Market description must be no more than {MarketResearchValidator.MAX_MARKET_LENGTH} characters"

        # Check for invalid patterns
        for pattern in MarketResearchValidator.INVALID_PATTERNS:
            if re.match(pattern, market, re.IGNORECASE):
                return False, "Market description appears to be invalid or spam"

        # Check for meaningful content (at least some words)
        words = market.split()
        if len(words) < 3:
            return False, "Market description must contain at least 3 words"

        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', market):
            return False, "Market description must contain at least one letter"

        # Check for too much repetition (spam detection)
        if len(set(words)) < len(words) * 0.3 and len(words) > 10:
            return False, "Market description appears to have too much repetition"

        return True, None

    @staticmethod
    def validate_research_type(research_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate research type.

        Args:
            research_type: Research type string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not research_type:
            return False, "Research type is required"

        if research_type not in MarketResearchValidator.VALID_RESEARCH_TYPES:
            return False, f"Research type must be one of: {', '.join(MarketResearchValidator.VALID_RESEARCH_TYPES)}"

        return True, None

    @staticmethod
    def validate_focus(focus: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate focus area.

        Args:
            focus: Focus area string to validate (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if focus is None:
            return True, None  # Focus is optional

        if focus not in MarketResearchValidator.VALID_FOCUS_AREAS:
            return False, f"Focus must be one of: {', '.join(MarketResearchValidator.VALID_FOCUS_AREAS)}"

        return True, None

    @staticmethod
    def validate_timeframe(timeframe: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate timeframe.

        Args:
            timeframe: Timeframe string to validate (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if timeframe is None:
            return True, None  # Timeframe is optional

        if timeframe not in MarketResearchValidator.VALID_TIMEFRAMES:
            return False, f"Timeframe must be one of: {', '.join(MarketResearchValidator.VALID_TIMEFRAMES)}"

        return True, None

    @staticmethod
    def validate_all(
        industry: str,
        market: str,
        research_type: str,
        timeframe: Optional[str] = None,
        focus: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate all market research fields.

        Args:
            industry: Industry string
            market: Market description string
            research_type: Research type string
            timeframe: Optional timeframe string
            focus: Optional focus area string

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate each field
        is_valid, error = MarketResearchValidator.validate_industry(industry)
        if not is_valid:
            errors.append(error)

        is_valid, error = MarketResearchValidator.validate_market(market)
        if not is_valid:
            errors.append(error)

        is_valid, error = MarketResearchValidator.validate_research_type(research_type)
        if not is_valid:
            errors.append(error)

        is_valid, error = MarketResearchValidator.validate_focus(focus)
        if not is_valid:
            errors.append(error)

        is_valid, error = MarketResearchValidator.validate_timeframe(timeframe)
        if not is_valid:
            errors.append(error)

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize input text by removing excessive whitespace and trimming.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove leading/trailing whitespace
        text = text.strip()

        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)

        # Remove excessive newlines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text
