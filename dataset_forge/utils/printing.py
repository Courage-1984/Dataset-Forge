from .color import Mocha
from .audio_utils import play_error_sound


def _safe_print(text: str, color: str = "") -> None:
    """Safely print text with emoji handling and color support."""
    try:
        # Normalize and sanitize text for emoji safety
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_text = sanitize_emoji(normalize_unicode(text))

        # Print with color and proper encoding
        if color:
            print(color + safe_text + Mocha.reset, flush=True)
        else:
            print(safe_text, flush=True)
    except UnicodeEncodeError as e:
        # Fallback: print without emojis
        import re

        fallback_text = re.sub(r"[^\x00-\x7F]+", "", text)
        if color:
            print(color + fallback_text + Mocha.reset, flush=True)
        else:
            print(fallback_text, flush=True)
    except Exception as e:
        # Final fallback: print original text
        if color:
            print(color + text + Mocha.reset, flush=True)
        else:
            print(text, flush=True)


def print_header(title, char="#", color=Mocha.mauve):
    """Print a header with emoji-safe handling."""
    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_title = sanitize_emoji(normalize_unicode(title))
    except ImportError:
        safe_title = title

    _safe_print(char * 50, color + Mocha.bold)
    _safe_print(f"{safe_title.center(50)}", color + Mocha.bold)
    _safe_print(char * 50, color + Mocha.bold)


def print_section(title, char="-", color=Mocha.sapphire):
    """Print a section header with emoji-safe handling."""
    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_title = sanitize_emoji(normalize_unicode(title))
    except ImportError:
        safe_title = title

    _safe_print(char * 40, color)
    _safe_print(f"{safe_title.center(40)}", color + Mocha.bold)
    _safe_print(char * 40, color)


def print_success(msg):
    """Print success message with emoji-safe handling."""
    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_msg = sanitize_emoji(normalize_unicode(msg))
    except ImportError:
        safe_msg = msg

    _safe_print("  " + safe_msg, Mocha.green + Mocha.bold)


def print_warning(msg):
    """Print warning message with emoji-safe handling."""
    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_msg = sanitize_emoji(normalize_unicode(msg))
    except ImportError:
        safe_msg = msg

    _safe_print("! " + safe_msg, Mocha.peach + Mocha.bold)


def print_error(msg):
    """Print error message with emoji-safe handling."""
    play_error_sound(block=False)

    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_msg = sanitize_emoji(normalize_unicode(msg))
    except ImportError:
        safe_msg = msg

    _safe_print("  " + safe_msg, Mocha.red + Mocha.bold)


def print_info(msg):
    """Print info message with emoji-safe handling."""
    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_msg = sanitize_emoji(normalize_unicode(msg))
    except ImportError:
        safe_msg = msg

    _safe_print(safe_msg, Mocha.sky)


def print_prompt(msg):
    """Print prompt message with emoji-safe handling."""
    try:
        from .emoji_utils import normalize_unicode, sanitize_emoji

        safe_msg = sanitize_emoji(normalize_unicode(msg))
        print(Mocha.yellow + safe_msg + Mocha.reset, end="", flush=True)
    except ImportError:
        # Fallback if emoji utilities are not available
        print(Mocha.yellow + msg + Mocha.reset, end="", flush=True)


def print_emoji_safe(text: str, color: str = "") -> None:
    """
    Print text with comprehensive emoji safety handling.

    Args:
        text: Text to print
        color: Optional color code
    """
    try:
        from .emoji_utils import safe_print_emoji

        safe_print_emoji(text, use_colors=bool(color))
    except ImportError:
        # Fallback to regular printing
        if color:
            print(color + text + Mocha.reset, flush=True)
        else:
            print(text, flush=True)
