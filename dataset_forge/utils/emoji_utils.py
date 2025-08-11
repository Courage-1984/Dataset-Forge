"""
Emoji Utilities for Dataset Forge

This module provides comprehensive emoji handling capabilities including:
- Unicode normalization and encoding handling
- Emoji validation and sanitization
- Integration with existing printing utilities
- Comprehensive error handling for Unicode issues
- Emoji categorization and management
"""

import re
import sys
import unicodedata
import json
from typing import List, Dict, Optional, Tuple, Union, Any, Set
from pathlib import Path

# Lazy imports for emoji libraries
try:
    import emoji

    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False
    emoji = None

try:
    import demoji

    DEMOJI_AVAILABLE = True
except ImportError:
    DEMOJI_AVAILABLE = False
    demoji = None

# Lazy imports for printing utilities to avoid circular dependencies
from .color import Mocha

# Import the emoji mapping
try:
    from .emoji_mapping import EMOJI_TO_DESC

    EMOJI_MAPPING_AVAILABLE = True
except ImportError:
    EMOJI_MAPPING_AVAILABLE = False
    EMOJI_TO_DESC = {}


# Helper function for lazy printing imports
def _get_printing_functions():
    """Get printing functions with fallback for circular import issues."""
    try:
        from .printing import print_warning, print_error, print_info
        return print_warning, print_error, print_info
    except ImportError:
        # Fallback if printing utilities are not available
        def print_warning(msg):
            # Use sys.stderr.write to avoid circular import issues
            import sys
            sys.stderr.write(f"WARNING: {msg}\n")
            sys.stderr.flush()

        def print_error(msg):
            # Use sys.stderr.write to avoid circular import issues
            import sys
            sys.stderr.write(f"ERROR: {msg}\n")
            sys.stderr.flush()

        def print_info(msg):
            # Use sys.stdout.write to avoid circular import issues
            import sys
            sys.stdout.write(f"INFO: {msg}\n")
            sys.stdout.flush()

        return print_warning, print_error, print_info


class EmojiHandler:
    """Comprehensive emoji handling and management system."""

    def __init__(self):
        """Initialize the emoji handler with proper Unicode support."""
        self._initialize_emoji_libraries()
        self._setup_unicode_environment()
        self._emoji_cache = {}
        self._validation_cache = {}
        self._load_emoji_mapping()
        self._setup_emoji_categories()

    def _initialize_emoji_libraries(self) -> None:
        """Initialize emoji libraries with proper error handling."""
        # Skip printing during initialization to avoid circular import issues
        # The libraries will be initialized silently

        if not EMOJI_AVAILABLE:
            pass  # Silently skip if not available

        if not DEMOJI_AVAILABLE:
            pass  # Silently skip if not available

        # Initialize demoji if available (no longer needs download_codes)
        if DEMOJI_AVAILABLE and demoji:
            try:
                # demoji.download_codes() is deprecated - emoji codes are now distributed with the package
                pass  # Silently initialize
            except Exception as e:
                pass  # Silently skip on error

    def _setup_unicode_environment(self) -> None:
        """Setup proper Unicode environment for emoji handling."""
        # Skip printing during initialization to avoid circular import issues

        # Ensure UTF-8 encoding for stdout/stderr
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
            except Exception as e:
                pass  # Silently skip on error

        # Set environment variables for better Unicode support
        import os

        os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    def _load_emoji_mapping(self) -> None:
        """Load emoji mapping from JSON file for enhanced functionality."""
        # Skip printing during initialization to avoid circular import issues

        self.emoji_mapping = EMOJI_TO_DESC
        self.reverse_mapping = {desc: emoji for emoji, desc in EMOJI_TO_DESC.items()}

        if not EMOJI_MAPPING_AVAILABLE:
            pass  # Silently skip if not available
        else:
            pass  # Silently load mappings

    def _setup_emoji_categories(self) -> None:
        """Setup emoji categories for better organization and validation."""
        # Define emoji categories based on common usage patterns
        self.emoji_categories = {
            "faces": {
                "smiling",
                "grinning",
                "laughing",
                "crying",
                "angry",
                "surprised",
                "winking",
                "kissing",
            },
            "emotions": {
                "love",
                "heart",
                "sad",
                "happy",
                "excited",
                "worried",
                "confused",
                "proud",
            },
            "actions": {
                "running",
                "dancing",
                "singing",
                "playing",
                "working",
                "studying",
                "sleeping",
                "eating",
            },
            "objects": {
                "phone",
                "computer",
                "book",
                "car",
                "house",
                "food",
                "drink",
                "clothing",
            },
            "nature": {
                "tree",
                "flower",
                "sun",
                "moon",
                "star",
                "rain",
                "snow",
                "ocean",
            },
            "animals": {
                "dog",
                "cat",
                "bird",
                "fish",
                "lion",
                "elephant",
                "monkey",
                "panda",
            },
            "symbols": {
                "check",
                "cross",
                "arrow",
                "star",
                "diamond",
                "circle",
                "square",
                "triangle",
            },
            "flags": {"flag", "country", "nation", "region"},
            "activities": {
                "sport",
                "game",
                "music",
                "art",
                "travel",
                "party",
                "celebration",
            },
            "professions": {
                "doctor",
                "teacher",
                "police",
                "firefighter",
                "chef",
                "artist",
                "scientist",
            },
            "body_parts": {
                "hand",
                "foot",
                "eye",
                "ear",
                "nose",
                "mouth",
                "heart",
                "brain",
            },
            "food_drink": {
                "pizza",
                "burger",
                "cake",
                "coffee",
                "beer",
                "wine",
                "water",
                "milk",
            },
            "transport": {
                "car",
                "bus",
                "train",
                "plane",
                "bike",
                "boat",
                "rocket",
                "helicopter",
            },
            "time": {"clock", "watch", "calendar", "hourglass", "timer", "schedule"},
            "weather": {
                "sunny",
                "rainy",
                "snowy",
                "cloudy",
                "stormy",
                "windy",
                "hot",
                "cold",
            },
        }

        # Create category lookup for quick validation
        self.category_lookup = {}
        for category, keywords in self.emoji_categories.items():
            for keyword in keywords:
                self.category_lookup[keyword] = category

    def normalize_unicode(self, text: str, form: str = "NFC") -> str:
        """
        Normalize Unicode text to prevent encoding issues.

        Args:
            text: Input text to normalize
            form: Normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')

        Returns:
            Normalized text string

        Raises:
            ValueError: If normalization form is invalid
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        valid_forms = ["NFC", "NFD", "NFKC", "NFKD"]
        if form not in valid_forms:
            raise ValueError(f"Normalization form must be one of: {valid_forms}")

        try:
            return unicodedata.normalize(form, text)
        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Unicode normalization failed: {e}")
            return text

    def is_valid_emoji(self, text: str) -> bool:
        """
        Check if a string is a valid emoji.

        Args:
            text: String to check

        Returns:
            True if the string is a valid emoji, False otherwise
        """
        if not text or not isinstance(text, str):
            return False

        # Use cache for performance
        if text in self._validation_cache:
            return self._validation_cache[text]

        try:
            # Normalize the text first
            normalized = self.normalize_unicode(text)

            # Check if it's a single emoji using emoji library
            if EMOJI_AVAILABLE and emoji:
                is_emoji = emoji.is_emoji(normalized)
                self._validation_cache[text] = is_emoji
                return is_emoji

            # Fallback: check Unicode properties
            if len(normalized) == 1:
                char = normalized[0]
                # Check if character is in emoji ranges
                emoji_ranges = [
                    (0x1F600, 0x1F64F),  # Emoticons
                    (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
                    (0x1F680, 0x1F6FF),  # Transport and Map Symbols
                    (0x1F1E0, 0x1F1FF),  # Regional Indicator Symbols
                    (0x2600, 0x26FF),  # Miscellaneous Symbols
                    (0x2700, 0x27BF),  # Dingbats
                    (0xFE00, 0xFE0F),  # Variation Selectors
                    (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
                    (0x1F018, 0x1F270),  # Various symbols
                ]

                code_point = ord(char)
                for start, end in emoji_ranges:
                    if start <= code_point <= end:
                        self._validation_cache[text] = True
                        return True

            self._validation_cache[text] = False
            return False

        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Emoji validation failed: {e}")
            self._validation_cache[text] = False
            return False

    def extract_emojis(self, text: str) -> List[str]:
        """
        Extract all emojis from text.

        Args:
            text: Input text to extract emojis from

        Returns:
            List of emoji strings found in the text
        """
        if not text or not isinstance(text, str):
            return []

        try:
            # Use demoji if available for better extraction
            if DEMOJI_AVAILABLE and demoji:
                # demoji.findall() returns a dict mapping emoji chars to descriptions
                emoji_dict = demoji.findall(text)
                return list(emoji_dict.keys())

            # Fallback: use emoji library
            if EMOJI_AVAILABLE and emoji:
                emoji_list = emoji.emoji_list(text)
                return [item["emoji"] for item in emoji_list]

            # Manual extraction using regex
            emoji_pattern = re.compile(
                "["
                "\U0001f600-\U0001f64f"  # emoticons
                "\U0001f300-\U0001f5ff"  # symbols & pictographs
                "\U0001f680-\U0001f6ff"  # transport & map symbols
                "\U0001f1e0-\U0001f1ff"  # flags (iOS)
                "\U00002600-\U000027bf"  # miscellaneous symbols
                "\U0001f900-\U0001f9ff"  # supplemental symbols
                "]+",
                flags=re.UNICODE,
            )

            return emoji_pattern.findall(text)

        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Emoji extraction failed: {e}")
            return []

    def sanitize_emoji(self, text: str, replace_invalid: str = "❓") -> str:
        """
        Sanitize text by validating and replacing invalid emojis.

        Args:
            text: Input text to sanitize
            replace_invalid: Character to replace invalid emojis with

        Returns:
            Sanitized text string
        """
        if not text or not isinstance(text, str):
            return text

        try:
            # Normalize the text first
            normalized = self.normalize_unicode(text)

            # Extract all emojis
            emojis = self.extract_emojis(normalized)

            # Replace invalid emojis
            for emoji_char in emojis:
                if not self.is_valid_emoji(emoji_char):
                    normalized = normalized.replace(emoji_char, replace_invalid)

            return normalized

        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Emoji sanitization failed: {e}")
            return text

    def emoji_to_unicode(self, emoji_char: str) -> str:
        """
        Convert emoji to Unicode escape sequence.

        Args:
            emoji_char: Single emoji character

        Returns:
            Unicode escape sequence string
        """
        if not self.is_valid_emoji(emoji_char):
            raise ValueError("Input is not a valid emoji")

        try:
            # Handle multi-character emojis (like ⚙️ which is ⚙ + ️)
            if len(emoji_char) == 1:
                return f"\\U{ord(emoji_char):08X}"
            else:
                # For multi-character emojis, convert each character
                unicode_parts = []
                for char in emoji_char:
                    unicode_parts.append(f"\\U{ord(char):08X}")
                return "".join(unicode_parts)
        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Emoji to Unicode conversion failed: {e}")
            return emoji_char

    def unicode_to_emoji(self, unicode_seq: str) -> str:
        """
        Convert Unicode escape sequence to emoji.

        Args:
            unicode_seq: Unicode escape sequence (e.g., "\\U0001F600")

        Returns:
            Emoji character string
        """
        try:
            # Handle multiple Unicode sequences (for multi-character emojis)
            if "\\U" in unicode_seq and unicode_seq.count("\\U") > 1:
                # Split by \U and process each part
                parts = unicode_seq.split("\\U")
                result = ""
                for part in parts[1:]:  # Skip first empty part
                    if len(part) >= 8:
                        code_point = int(part[:8], 16)
                        result += chr(code_point)
                    else:
                        raise ValueError("Invalid Unicode escape sequence format")
                return result

            # Handle single Unicode sequence
            if unicode_seq.startswith("\\U"):
                code_point = int(unicode_seq[2:], 16)
                return chr(code_point)
            elif unicode_seq.startswith("\\u"):
                code_point = int(unicode_seq[2:], 16)
                return chr(code_point)
            else:
                raise ValueError("Invalid Unicode escape sequence format")
        except ValueError:
            # Re-raise ValueError for invalid sequences
            raise
        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Unicode to emoji conversion failed: {e}")
            return unicode_seq

    def get_emoji_description(self, emoji_char: str) -> str:
        """
        Get description/name of an emoji.

        Args:
            emoji_char: Single emoji character

        Returns:
            Description of the emoji
        """
        if not self.is_valid_emoji(emoji_char):
            return "Invalid emoji"

        try:
            # Use demoji if available
            if DEMOJI_AVAILABLE and demoji:
                descriptions = demoji.findall(emoji_char)
                if descriptions:
                    return list(descriptions.values())[0]

            # Use emoji library
            if EMOJI_AVAILABLE and emoji:
                return emoji.demojize(emoji_char, delimiters=(":", ":"))

            # Fallback: use Unicode name
            return unicodedata.name(emoji_char, "Unknown emoji")

        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Failed to get emoji description: {e}")
            return "Unknown emoji"

    def categorize_emoji(self, emoji_char: str) -> str:
        """
        Categorize emoji by type.

        Args:
            emoji_char: Single emoji character

        Returns:
            Category of the emoji
        """
        if not self.is_valid_emoji(emoji_char):
            return "invalid"

        try:
            description = self.get_emoji_description(emoji_char).lower()

            # Define categories
            categories = {
                "face": ["face", "smile", "laugh", "cry", "angry", "sad", "happy"],
                "hand": ["hand", "finger", "thumbs", "clap", "wave"],
                "heart": ["heart", "love"],
                "nature": ["tree", "flower", "sun", "moon", "star", "cloud"],
                "food": ["food", "pizza", "hamburger", "apple", "banana"],
                "animal": ["animal", "dog", "cat", "bird", "fish"],
                "transport": ["car", "bus", "train", "plane", "bike"],
                "activity": ["sport", "game", "music", "dance"],
                "object": ["book", "phone", "computer", "clock"],
                "symbol": ["symbol", "arrow", "check", "cross"],
            }

            for category, keywords in categories.items():
                if any(keyword in description for keyword in keywords):
                    return category

            return "other"

        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Emoji categorization failed: {e}")
            return "unknown"

    def validate_menu_emojis(
        self, menu_options: Dict[str, Tuple[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Validate emojis in menu options and return issues found.

        Args:
            menu_options: Dictionary of menu options with (description, action) tuples

        Returns:
            Dictionary with 'valid' and 'invalid' emoji lists
        """
        issues = {"valid": [], "invalid": []}

        for key, (description, action) in menu_options.items():
            emojis = self.extract_emojis(description)

            for emoji_char in emojis:
                if self.is_valid_emoji(emoji_char):
                    issues["valid"].append(emoji_char)
                else:
                    issues["invalid"].append(emoji_char)

        return issues

    def get_emoji_description_from_mapping(self, emoji_char: str) -> Optional[str]:
        """
        Get emoji description from the comprehensive mapping.

        Args:
            emoji_char: The emoji character to look up

        Returns:
            Description string or None if not found
        """
        return self.emoji_mapping.get(emoji_char)

    def find_emoji_by_description(self, description: str) -> List[str]:
        """
        Find emojis by description (partial match).

        Args:
            description: Description to search for

        Returns:
            List of matching emoji characters
        """
        description = description.lower()
        matches = []

        for emoji_char, desc in self.emoji_mapping.items():
            if description in desc or desc in description:
                matches.append(emoji_char)

        return matches

    def get_emoji_category(self, emoji_char: str) -> str:
        """
        Get the category of an emoji based on its description.

        Args:
            emoji_char: The emoji character

        Returns:
            Category name or 'unknown' if not found
        """
        description = self.get_emoji_description_from_mapping(emoji_char)
        if not description:
            return "unknown"

        return self.category_lookup.get(description, "unknown")

    def validate_emoji_appropriateness(
        self, emoji_char: str, context: str
    ) -> Dict[str, Any]:
        """
        Validate if an emoji is appropriate for a given context.

        Args:
            emoji_char: The emoji character to validate
            context: The context where the emoji will be used

        Returns:
            Dictionary with validation results
        """
        result = {
            "is_valid": False,
            "is_appropriate": False,
            "category": "unknown",
            "description": None,
            "suggestions": [],
            "warnings": [],
        }

        # Check if emoji exists in mapping
        if emoji_char not in self.emoji_mapping:
            result["warnings"].append("Emoji not found in comprehensive mapping")
            return result

        result["is_valid"] = True
        result["description"] = self.emoji_mapping[emoji_char]
        result["category"] = self.get_emoji_category(emoji_char)

        # Context-specific appropriateness checks
        context_lower = context.lower()

        # Check for professional contexts
        if any(
            word in context_lower
            for word in ["professional", "business", "formal", "work"]
        ):
            professional_emojis = {"check", "star", "heart", "smiling", "thumbs"}
            if result["description"] not in professional_emojis:
                result["warnings"].append(
                    "Consider using more professional emojis in this context"
                )
                result["suggestions"].extend(self.find_emoji_by_description("check"))
                result["suggestions"].extend(self.find_emoji_by_description("star"))

        # Check for technical contexts
        if any(
            word in context_lower
            for word in ["technical", "code", "programming", "development"]
        ):
            technical_emojis = {
                "computer",
                "phone",
                "gear",
                "check",
                "cross",
                "warning",
            }
            if result["description"] not in technical_emojis:
                result["warnings"].append(
                    "Consider using more technical emojis in this context"
                )
                result["suggestions"].extend(self.find_emoji_by_description("computer"))
                result["suggestions"].extend(self.find_emoji_by_description("gear"))

        # Check for casual contexts
        if any(
            word in context_lower for word in ["casual", "fun", "social", "personal"]
        ):
            result["is_appropriate"] = (
                True  # Most emojis are appropriate in casual contexts
            )

        # Check for educational contexts
        if any(
            word in context_lower
            for word in ["education", "learning", "teaching", "school"]
        ):
            educational_emojis = {
                "book",
                "star",
                "check",
                "smiling",
                "thinking",
                "lightbulb",
            }
            if result["description"] not in educational_emojis:
                result["warnings"].append(
                    "Consider using more educational emojis in this context"
                )
                result["suggestions"].extend(self.find_emoji_by_description("book"))
                result["suggestions"].extend(self.find_emoji_by_description("star"))

        return result

    def suggest_appropriate_emojis(
        self, context: str, category: Optional[str] = None
    ) -> List[str]:
        """
        Suggest appropriate emojis for a given context and optional category.

        Args:
            context: The context where emojis will be used
            category: Optional category to filter suggestions

        Returns:
            List of suggested emoji characters
        """
        suggestions = []
        context_lower = context.lower()

        # Context-based suggestions
        if any(word in context_lower for word in ["success", "complete", "done"]):
            suggestions.extend(self.find_emoji_by_description("check"))
            suggestions.extend(self.find_emoji_by_description("star"))
            suggestions.extend(self.find_emoji_by_description("trophy"))

        elif any(word in context_lower for word in ["error", "fail", "problem"]):
            suggestions.extend(self.find_emoji_by_description("cross"))
            suggestions.extend(self.find_emoji_by_description("warning"))
            suggestions.extend(self.find_emoji_by_description("sad"))

        elif any(word in context_lower for word in ["love", "heart", "romance"]):
            suggestions.extend(self.find_emoji_by_description("heart"))
            suggestions.extend(self.find_emoji_by_description("love"))
            suggestions.extend(self.find_emoji_by_description("kissing"))

        elif any(word in context_lower for word in ["food", "eat", "hungry"]):
            suggestions.extend(self.find_emoji_by_description("pizza"))
            suggestions.extend(self.find_emoji_by_description("burger"))
            suggestions.extend(self.find_emoji_by_description("cake"))

        elif any(word in context_lower for word in ["travel", "vacation", "trip"]):
            suggestions.extend(self.find_emoji_by_description("plane"))
            suggestions.extend(self.find_emoji_by_description("car"))
            suggestions.extend(self.find_emoji_by_description("beach"))

        # Category-based filtering
        if category and category in self.emoji_categories:
            category_keywords = self.emoji_categories[category]
            category_suggestions = []
            for keyword in category_keywords:
                category_suggestions.extend(self.find_emoji_by_description(keyword))
            suggestions = [s for s in suggestions if s in category_suggestions]

        return list(set(suggestions))[:10]  # Return unique suggestions, limit to 10

    def analyze_emoji_usage(self, text: str) -> Dict[str, Any]:
        """
        Analyze emoji usage in text for insights and recommendations.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with analysis results
        """
        emojis = self.extract_emojis(text)
        analysis = {
            "total_emojis": len(emojis),
            "unique_emojis": len(set(emojis)),
            "categories": {},
            "most_used": [],
            "potential_issues": [],
            "recommendations": [],
        }

        if not emojis:
            analysis["recommendations"].append(
                "No emojis found - consider adding some for better engagement"
            )
            return analysis

        # Count categories
        category_counts = {}
        emoji_counts = {}

        for emoji_char in emojis:
            category = self.get_emoji_category(emoji_char)
            category_counts[category] = category_counts.get(category, 0) + 1
            emoji_counts[emoji_char] = emoji_counts.get(emoji_char, 0) + 1

        analysis["categories"] = category_counts

        # Find most used emojis
        sorted_emojis = sorted(emoji_counts.items(), key=lambda x: x[1], reverse=True)
        analysis["most_used"] = [emoji for emoji, count in sorted_emojis[:5]]

        # Check for potential issues
        if len(emojis) > 10:
            analysis["potential_issues"].append(
                "High emoji density - consider reducing for better readability"
            )

        if len(set(emojis)) < len(emojis) * 0.3:
            analysis["potential_issues"].append(
                "Low emoji variety - consider using different emojis"
            )

        # Generate recommendations
        if "faces" in category_counts and category_counts["faces"] > len(emojis) * 0.5:
            analysis["recommendations"].append(
                "High proportion of face emojis - consider adding more object/action emojis"
            )

        if "unknown" in category_counts and category_counts["unknown"] > 0:
            analysis["recommendations"].append(
                "Some emojis couldn't be categorized - verify they're appropriate"
            )

        return analysis

    def safe_print_emoji(self, text: str, use_colors: bool = True) -> None:
        """
        Safely print text containing emojis with proper encoding handling.

        Args:
            text: Text to print
            use_colors: Whether to use color formatting
        """
        try:
            # Normalize and sanitize the text
            normalized = self.normalize_unicode(text)
            sanitized = self.sanitize_emoji(normalized)

            # Print with proper encoding using sys.stdout.write to avoid circular imports
            import sys
            sys.stdout.write(sanitized + "\n")
            sys.stdout.flush()

        except UnicodeEncodeError as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Unicode encoding error: {e}")
            # Fallback: print without emojis
            import re
            fallback_text = re.sub(r"[^\x00-\x7F]+", "", text)
            import sys
            sys.stdout.write(fallback_text + "\n")
            sys.stdout.flush()
        except Exception as e:
            print_warning, print_error, print_info = _get_printing_functions()
            print_error(f"Error printing emoji text: {e}")
            import sys
            sys.stdout.write(text + "\n")
            sys.stdout.flush()


# Global emoji handler instance
_emoji_handler = None


def get_emoji_handler() -> EmojiHandler:
    """Get the global emoji handler instance."""
    global _emoji_handler
    if _emoji_handler is None:
        _emoji_handler = EmojiHandler()
    return _emoji_handler


# Convenience functions for easy access
def normalize_unicode(text: str, form: str = "NFC") -> str:
    """Normalize Unicode text."""
    return get_emoji_handler().normalize_unicode(text, form)


def is_valid_emoji(text: str) -> bool:
    """Check if text is a valid emoji."""
    return get_emoji_handler().is_valid_emoji(text)


def extract_emojis(text: str) -> List[str]:
    """Extract all emojis from text."""
    return get_emoji_handler().extract_emojis(text)


def sanitize_emoji(text: str, replace_invalid: str = "❓") -> str:
    """Sanitize text by validating and replacing invalid emojis."""
    return get_emoji_handler().sanitize_emoji(text, replace_invalid)


def emoji_to_unicode(emoji_char: str) -> str:
    """Convert emoji to Unicode escape sequence."""
    return get_emoji_handler().emoji_to_unicode(emoji_char)


def unicode_to_emoji(unicode_seq: str) -> str:
    """Convert Unicode escape sequence to emoji."""
    return get_emoji_handler().unicode_to_emoji(unicode_seq)


def get_emoji_description(emoji_char: str) -> str:
    """Get description/name of an emoji."""
    return get_emoji_handler().get_emoji_description(emoji_char)


def categorize_emoji(emoji_char: str) -> str:
    """Categorize emoji by type."""
    return get_emoji_handler().categorize_emoji(emoji_char)


def validate_menu_emojis(
    menu_options: Dict[str, Tuple[str, Any]],
) -> Dict[str, List[str]]:
    """Validate emojis in menu options."""
    return get_emoji_handler().validate_menu_emojis(menu_options)


def safe_print_emoji(text: str, use_colors: bool = True) -> None:
    """Safely print text containing emojis."""
    return get_emoji_handler().safe_print_emoji(text, use_colors)


# New convenience functions for enhanced emoji mapping functionality
def get_emoji_description_from_mapping(emoji_char: str) -> Optional[str]:
    """Get emoji description from the comprehensive mapping."""
    return get_emoji_handler().get_emoji_description_from_mapping(emoji_char)


def find_emoji_by_description(description: str) -> List[str]:
    """Find emojis by description (partial match)."""
    return get_emoji_handler().find_emoji_by_description(description)


def get_emoji_category(emoji_char: str) -> str:
    """Get the category of an emoji based on its description."""
    return get_emoji_handler().get_emoji_category(emoji_char)


def validate_emoji_appropriateness(emoji_char: str, context: str) -> Dict[str, Any]:
    """Validate if an emoji is appropriate for a given context."""
    return get_emoji_handler().validate_emoji_appropriateness(emoji_char, context)


def suggest_appropriate_emojis(
    context: str, category: Optional[str] = None
) -> List[str]:
    """Suggest appropriate emojis for a given context and optional category."""
    return get_emoji_handler().suggest_appropriate_emojis(context, category)


def analyze_emoji_usage(text: str) -> Dict[str, Any]:
    """Analyze emoji usage in text for insights and recommendations."""
    return get_emoji_handler().analyze_emoji_usage(text)
