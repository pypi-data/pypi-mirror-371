"""
Custom exception types for the morsecode_handler package.
"""

from typing import Optional


class MorseCodeError(Exception):
    """Base class for all morsecode_handler errors."""
    pass


class LanguageNotFoundError(MorseCodeError):
    """Raised when a requested language dictionary is not available."""

    def __init__(self, language: str, available: Optional[list[str]] = None):
        self.language = language
        self.available = available or []
        msg = f"Language '{language}' not found. Available: {', '.join(self.available) or 'None'}."
        super().__init__(msg)


class UnknownCharacterError(MorseCodeError):
    """Raised when encoding encounters a character not present in the selected language."""

    def __init__(self, char: str, position: int, language: str):
        self.char = char
        self.position = position
        self.language = language
        super().__init__(f"Unknown character {char!r} at position {position} for language '{language}'.")


class UnknownMorseCodeError(MorseCodeError):
    """Raised when decoding encounters a token not present in the selected language."""

    def __init__(self, token: str, index: int, language: str):
        self.token = token
        self.index = index
        self.language = language
        super().__init__(f"Unknown Morse token {token!r} at index {index} for language '{language}'.")
