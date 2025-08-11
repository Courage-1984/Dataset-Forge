"""
Tests for emoji utilities module.

This module tests the comprehensive emoji handling capabilities including:
- Unicode normalization and encoding handling
- Emoji validation and sanitization
- Integration with existing printing utilities
- Comprehensive error handling for Unicode issues
- Emoji categorization and management
"""

import pytest
import sys
import unicodedata
from unittest.mock import patch, MagicMock
from typing import Dict, List, Tuple, Any

# Add project root to path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.emoji_utils import (
    EmojiHandler,
    get_emoji_handler,
    normalize_unicode,
    is_valid_emoji,
    extract_emojis,
    sanitize_emoji,
    emoji_to_unicode,
    unicode_to_emoji,
    get_emoji_description,
    categorize_emoji,
    validate_menu_emojis,
    safe_print_emoji,
)


class TestEmojiHandler:
    """Test the EmojiHandler class."""

    def test_initialization(self):
        """Test EmojiHandler initialization."""
        handler = EmojiHandler()
        assert handler is not None
        assert hasattr(handler, "_emoji_cache")
        assert hasattr(handler, "_validation_cache")

    def test_normalize_unicode_valid_forms(self):
        """Test Unicode normalization with valid forms."""
        handler = EmojiHandler()
        text = "café"

        # Test all valid normalization forms
        forms = ["NFC", "NFD", "NFKC", "NFKD"]
        for form in forms:
            result = handler.normalize_unicode(text, form)
            assert result is not None
            assert isinstance(result, str)

    def test_normalize_unicode_invalid_form(self):
        """Test Unicode normalization with invalid form."""
        handler = EmojiHandler()
        text = "test"

        with pytest.raises(ValueError):
            handler.normalize_unicode(text, "INVALID")

    def test_normalize_unicode_non_string(self):
        """Test Unicode normalization with non-string input."""
        handler = EmojiHandler()

        with pytest.raises(ValueError):
            handler.normalize_unicode(123)

    def test_is_valid_emoji_valid_emojis(self):
        """Test emoji validation with valid emojis."""
        handler = EmojiHandler()
        valid_emojis = ["😀", "🚀", "📁", "🔍", "🎨", "⚙️", "💾"]

        for emoji_char in valid_emojis:
            assert handler.is_valid_emoji(emoji_char) is True

    def test_is_valid_emoji_invalid_inputs(self):
        """Test emoji validation with invalid inputs."""
        handler = EmojiHandler()
        invalid_inputs = ["", "abc", "123", "😀😀", None, 123]

        for invalid_input in invalid_inputs:
            assert handler.is_valid_emoji(invalid_input) is False

    def test_extract_emojis_with_emojis(self):
        """Test emoji extraction from text containing emojis."""
        handler = EmojiHandler()
        text = "Hello 😀 world 🚀 test 📁"
        emojis = handler.extract_emojis(text)

        assert len(emojis) == 3
        assert "😀" in emojis
        assert "🚀" in emojis
        assert "📁" in emojis

    def test_extract_emojis_no_emojis(self):
        """Test emoji extraction from text without emojis."""
        handler = EmojiHandler()
        text = "Hello world test"
        emojis = handler.extract_emojis(text)

        assert len(emojis) == 0

    def test_extract_emojis_empty_input(self):
        """Test emoji extraction with empty or invalid input."""
        handler = EmojiHandler()

        assert handler.extract_emojis("") == []
        assert handler.extract_emojis(None) == []
        assert handler.extract_emojis(123) == []

    def test_sanitize_emoji_valid_text(self):
        """Test emoji sanitization with valid text."""
        handler = EmojiHandler()
        text = "Hello 😀 world 🚀 test"
        sanitized = handler.sanitize_emoji(text)

        assert sanitized is not None
        assert isinstance(sanitized, str)
        assert len(sanitized) > 0

    def test_sanitize_emoji_custom_replacement(self):
        """Test emoji sanitization with custom replacement."""
        handler = EmojiHandler()
        text = "Hello 😀 world"
        sanitized = handler.sanitize_emoji(text, replace_invalid="X")

        assert sanitized is not None
        assert isinstance(sanitized, str)

    def test_emoji_to_unicode_valid_emoji(self):
        """Test emoji to Unicode conversion with valid emoji."""
        handler = EmojiHandler()
        emoji_char = "😀"

        unicode_seq = handler.emoji_to_unicode(emoji_char)
        assert unicode_seq.startswith("\\U")
        assert len(unicode_seq) == 10  # \U + 8 hex digits

    def test_emoji_to_unicode_invalid_emoji(self):
        """Test emoji to Unicode conversion with invalid emoji."""
        handler = EmojiHandler()

        with pytest.raises(ValueError):
            handler.emoji_to_unicode("abc")

    def test_unicode_to_emoji_valid_sequence(self):
        """Test Unicode to emoji conversion with valid sequence."""
        handler = EmojiHandler()
        unicode_seq = "\\U0001F600"  # 😀

        emoji_char = handler.unicode_to_emoji(unicode_seq)
        assert emoji_char == "😀"

    def test_unicode_to_emoji_invalid_sequence(self):
        """Test Unicode to emoji conversion with invalid sequence."""
        handler = EmojiHandler()

        with pytest.raises(ValueError):
            handler.unicode_to_emoji("invalid")

    def test_get_emoji_description(self):
        """Test getting emoji description."""
        handler = EmojiHandler()
        emoji_char = "😀"

        description = handler.get_emoji_description(emoji_char)
        assert description is not None
        assert isinstance(description, str)
        assert len(description) > 0

    def test_categorize_emoji(self):
        """Test emoji categorization."""
        handler = EmojiHandler()
        emoji_char = "😀"

        category = handler.categorize_emoji(emoji_char)
        assert category is not None
        assert isinstance(category, str)
        assert len(category) > 0

    def test_validate_menu_emojis(self):
        """Test menu emoji validation."""
        handler = EmojiHandler()
        menu_options = {
            "1": ("📁 Create Dataset", None),
            "2": ("🔍 Analyze Dataset", None),
            "3": ("Invalid emoji: 🚀", None),
        }

        issues = handler.validate_menu_emojis(menu_options)
        assert "valid" in issues
        assert "invalid" in issues
        assert isinstance(issues["valid"], list)
        assert isinstance(issues["invalid"], list)

    @patch("sys.stdout.write")
    def test_safe_print_emoji(self, mock_write):
        """Test safe emoji printing."""
        handler = EmojiHandler()
        text = "Hello 😀 world"

        handler.safe_print_emoji(text)
        mock_write.assert_called()

    @patch("sys.stdout.write")
    def test_safe_print_emoji_unicode_error(self, mock_write):
        """Test safe emoji printing with Unicode error."""
        handler = EmojiHandler()
        text = "Hello 😀 world"

        # Mock UnicodeEncodeError with correct arguments
        with patch(
            "dataset_forge.utils.emoji_utils.normalize_unicode",
            side_effect=UnicodeEncodeError("utf-8", text, 0, 1, "invalid"),
        ):
            handler.safe_print_emoji(text)
            mock_write.assert_called()


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_emoji_handler_singleton(self):
        """Test that get_emoji_handler returns a singleton."""
        handler1 = get_emoji_handler()
        handler2 = get_emoji_handler()
        assert handler1 is handler2

    def test_normalize_unicode_function(self):
        """Test normalize_unicode convenience function."""
        text = "café"
        result = normalize_unicode(text)
        assert result is not None
        assert isinstance(result, str)

    def test_is_valid_emoji_function(self):
        """Test is_valid_emoji convenience function."""
        assert is_valid_emoji("😀") is True
        assert is_valid_emoji("abc") is False

    def test_extract_emojis_function(self):
        """Test extract_emojis convenience function."""
        text = "Hello 😀 world 🚀"
        emojis = extract_emojis(text)
        assert len(emojis) == 2
        assert "😀" in emojis
        assert "🚀" in emojis

    def test_sanitize_emoji_function(self):
        """Test sanitize_emoji convenience function."""
        text = "Hello 😀 world"
        sanitized = sanitize_emoji(text)
        assert sanitized is not None
        assert isinstance(sanitized, str)

    def test_emoji_to_unicode_function(self):
        """Test emoji_to_unicode convenience function."""
        emoji_char = "😀"
        unicode_seq = emoji_to_unicode(emoji_char)
        assert unicode_seq.startswith("\\U")

    def test_unicode_to_emoji_function(self):
        """Test unicode_to_emoji convenience function."""
        unicode_seq = "\\U0001F600"
        emoji_char = unicode_to_emoji(unicode_seq)
        assert emoji_char == "😀"

    def test_get_emoji_description_function(self):
        """Test get_emoji_description convenience function."""
        emoji_char = "😀"
        description = get_emoji_description(emoji_char)
        assert description is not None
        assert isinstance(description, str)

    def test_categorize_emoji_function(self):
        """Test categorize_emoji convenience function."""
        emoji_char = "😀"
        category = categorize_emoji(emoji_char)
        assert category is not None
        assert isinstance(category, str)

    def test_validate_menu_emojis_function(self):
        """Test validate_menu_emojis convenience function."""
        menu_options = {
            "1": ("📁 Create Dataset", None),
            "2": ("🔍 Analyze Dataset", None),
        }
        issues = validate_menu_emojis(menu_options)
        assert "valid" in issues
        assert "invalid" in issues

    @patch("sys.stdout.write")
    def test_safe_print_emoji_function(self, mock_write):
        """Test safe_print_emoji convenience function."""
        text = "Hello 😀 world"
        safe_print_emoji(text)
        mock_write.assert_called()


class TestEmojiIntegration:
    """Test emoji integration with other systems."""

    def test_emoji_with_menu_system(self):
        """Test emoji integration with menu system."""
        menu_options = {
            "1": ("📁 Create Dataset", None),
            "2": ("🔍 Analyze Dataset", None),
            "3": ("🎨 Color Adjustments", None),
            "0": ("⬅️  Back", None),
        }

        # Validate emojis in menu options
        issues = validate_menu_emojis(menu_options)
        assert len(issues["valid"]) > 0
        assert len(issues["invalid"]) == 0

    def test_emoji_with_printing_utilities(self):
        """Test emoji integration with printing utilities."""
        test_messages = [
            "✅ Operation completed successfully",
            "⚠️ Warning: Low memory detected",
            "❌ Error: File not found",
            "ℹ️ Processing images...",
        ]

        for message in test_messages:
            # Test that emojis can be extracted
            emojis = extract_emojis(message)
            assert len(emojis) > 0

            # Test that emojis are valid
            for emoji_char in emojis:
                assert is_valid_emoji(emoji_char)

    def test_emoji_unicode_roundtrip(self):
        """Test emoji Unicode conversion roundtrip."""
        original_emojis = ["😀", "🚀", "📁", "🔍", "🎨", "⚙️", "💾"]

        for emoji_char in original_emojis:
            # Convert to Unicode
            unicode_seq = emoji_to_unicode(emoji_char)
            assert unicode_seq.startswith("\\U")

            # Convert back to emoji
            converted_emoji = unicode_to_emoji(unicode_seq)
            assert converted_emoji == emoji_char

    def test_emoji_categorization_consistency(self):
        """Test emoji categorization consistency."""
        emoji_categories = {
            "face": ["😀", "😍", "😭"],
            "object": ["📁", "💾", "⚙️"],
            "transport": ["🚀", "🚗", "✈️"],
            "nature": ["🌲", "🌸", "☀️"],
        }

        for category, emojis in emoji_categories.items():
            for emoji_char in emojis:
                detected_category = categorize_emoji(emoji_char)
                assert detected_category is not None
                assert isinstance(detected_category, str)


class TestEmojiErrorHandling:
    """Test emoji error handling and edge cases."""

    def test_emoji_handler_with_missing_libraries(self):
        """Test emoji handler behavior when libraries are missing."""
        with patch("dataset_forge.utils.emoji_utils.EMOJI_AVAILABLE", False):
            with patch("dataset_forge.utils.emoji_utils.DEMOJI_AVAILABLE", False):
                handler = EmojiHandler()
                assert handler is not None

                # Should still work with fallback methods
                assert handler.is_valid_emoji("😀") is True
                assert len(handler.extract_emojis("Hello 😀 world")) > 0

    def test_emoji_handler_initialization_errors(self):
        """Test emoji handler initialization error handling."""
        with patch(
            "dataset_forge.utils.emoji_utils.demoji.download_codes",
            side_effect=Exception("Download failed"),
        ):
            handler = EmojiHandler()
            assert handler is not None  # Should not crash

    def test_unicode_normalization_errors(self):
        """Test Unicode normalization error handling."""
        handler = EmojiHandler()

        # Test with problematic text
        problematic_text = "test\x00string"  # Contains null byte
        result = handler.normalize_unicode(problematic_text)
        assert result is not None

    def test_emoji_extraction_errors(self):
        """Test emoji extraction error handling."""
        handler = EmojiHandler()

        # Test with various problematic inputs
        problematic_inputs = [
            "test\x00string",  # Null bytes
            "test\xffstring",  # Invalid UTF-8
            "",  # Empty string
            None,  # None
            123,  # Non-string
        ]

        for input_text in problematic_inputs:
            result = handler.extract_emojis(input_text)
            assert isinstance(result, list)

    def test_emoji_validation_cache(self):
        """Test emoji validation caching."""
        handler = EmojiHandler()
        emoji_char = "😀"

        # First call should cache the result
        result1 = handler.is_valid_emoji(emoji_char)
        assert result1 is True

        # Second call should use cache
        result2 = handler.is_valid_emoji(emoji_char)
        assert result2 is True

        # Check that cache was used
        assert emoji_char in handler._validation_cache


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
