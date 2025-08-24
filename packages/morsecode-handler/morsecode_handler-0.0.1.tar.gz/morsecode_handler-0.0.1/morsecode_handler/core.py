"""
Core encode/decode functions for the morsecode_handler package.

Public functions:
- encode(text, language="EN", *, strict=True, unknown="?", uppercase=None)
- decode(morse, language="EN", *, strict=True, unknown="?", uppercase=None)

Language keys follow ISO 2-letter codes (e.g., 'EN').
We avoid duplicating digits/space in every language by using a COMMON section.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from .exceptions import (
    LanguageNotFoundError,
    UnknownCharacterError,
    UnknownMorseCodeError,
)

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "morsecode_handler.json")
with open(_DATA_PATH, "r", encoding="utf-8") as _f:
    _RAW: Dict[str, Dict[str, str]] = json.load(_f)

# Validate required sections
if "EN" not in _RAW:
    raise RuntimeError("morsecode_handler.json must contain an 'EN' base mapping.")
if "COMMON" not in _RAW:
    raise RuntimeError("morsecode_handler.json must contain a 'COMMON' mapping for digits/space.")

DEFAULT_LANG = "EN"


def _normalize_lang(lang: str) -> str:
    """Normalize a language ID to uppercase two-letter form (e.g., 'en' -> 'EN')."""
    return lang.upper()


def _get_language_overrides(language: str) -> Dict[str, str]:
    """
    Return the override dict for the selected language code.

    Raises:
        LanguageNotFoundError: if language code not available and not 'EN'.
    """
    key = _normalize_lang(language)
    if key == "EN":
        return {}
    if key not in _RAW:
        raise LanguageNotFoundError(key, available=[k for k in _RAW.keys() if k not in ("COMMON",)])
    return _RAW[key]


def _merge_language_dict(language: str) -> Dict[str, str]:
    """
    Merge EN base letters + language overrides + COMMON digits/space.

    The result contains:
      - A–Z from EN
      - Any diacritics/overrides from the selected language
      - Digits/space from COMMON
    """
    base = dict(_RAW["EN"])            # letters A–Z
    overrides = _get_language_overrides(language)  # diacritics etc.
    common = _RAW["COMMON"]            # digits/space

    merged: Dict[str, str] = {}
    merged.update(base)       # baseline letters
    merged.update(overrides)  # diacritics override/add
    merged.update(common)     # digits + space

    return merged


def _build_reverse_pref(merged: Dict[str, str], overrides: Dict[str, str]) -> Dict[str, str]:
    """
    Build a reverse map (morse -> char) with a language-aware preference order.

    - If the selected language appears to use a non-ASCII script (e.g., Arabic, Russian),
      prefer its override characters first so collisions resolve to that script.
    - Otherwise (Latin-script languages), prefer ASCII A–Z first (status quo).
    """
    rev: Dict[str, str] = {}

    # Heuristic: if any override key is non-ASCII, treat as non-Latin script.
    non_ascii_script = any(ord(k) > 127 for k in overrides.keys())

    def insert_chars(chars):
        for ch in chars:
            morse = merged.get(ch)
            if morse:
                rev.setdefault(morse, ch)

    ascii_AZ = [chr(cp) for cp in range(ord("A"), ord("Z") + 1)]

    if non_ascii_script:
        # 1) Prefer language-specific overrides (e.g., Arabic/Russian letters)
        insert_chars(overrides.keys())
        # 2) Then ASCII A–Z (useful if input mixes scripts)
        insert_chars(ascii_AZ)
    else:
        # Latin languages: keep original behavior (prefer ASCII A–Z)
        insert_chars(ascii_AZ)
        insert_chars(overrides.keys())

    # 3) Digits & space from COMMON
    insert_chars(_RAW["COMMON"].keys())

    # 4) Any remaining keys (backfill)
    for ch, morse in merged.items():
        rev.setdefault(morse, ch)

    return rev


def encode(
        text: str,
        language: str = DEFAULT_LANG,
        *,
        strict: bool = True,
        unknown: str = "?",
        uppercase: Optional[bool] = None,
) -> str:
    """
    Encode plain text into Morse code.

    Args:
        text: Input text to encode.
        language: Two-letter language code (default: 'EN').
        strict: If True, raise UnknownCharacterError for unmapped characters.
                If False, emit `unknown` for unmapped characters.
        unknown: Placeholder used when `strict=False` and a character is unmapped.
        uppercase: If True, force-uppercase text before encoding. If None, defaults to
                   True when `language` != DEFAULT_LANG, else False.

    Returns:
        Space-separated Morse string, with '/' between words.

    Raises:
        LanguageNotFoundError, UnknownCharacterError.
    """
    lang_norm = _normalize_lang(language)
    if uppercase is None:
        uppercase = (lang_norm != DEFAULT_LANG)

    src = text.upper() if uppercase else text
    mapping = _merge_language_dict(lang_norm)

    out: List[str] = []
    for i, ch in enumerate(src):
        if ch == " ":
            out.append("/")
            continue
        code = mapping.get(ch.upper())
        if code is None:
            if strict:
                raise UnknownCharacterError(ch, i, lang_norm)
            out.append(unknown)
        else:
            out.append(code)

    # Collapse multiple consecutive '/'
    result: List[str] = []
    prev_slash = False
    for tok in out:
        if tok == "/":
            if not prev_slash:
                result.append(tok)
            prev_slash = True
        else:
            result.append(tok)
            prev_slash = False

    return " ".join(result)


def decode(
        morse: str,
        language: str = DEFAULT_LANG,
        *,
        strict: bool = True,
        unknown: str = "?",
        uppercase: Optional[bool] = None,
) -> str:
    """
    Decode Morse code into plain text.

    Args:
        morse: Morse string; letters separated by spaces, words by '/'.
        language: Two-letter language code (default: 'EN').
        strict: If True, raise UnknownMorseCodeError for unmapped tokens.
                If False, insert `unknown` for unmapped tokens.
        unknown: Placeholder used when `strict=False` and a token is unmapped.
        uppercase: If True, force-uppercase the decoded text. If None, defaults to
                   True when `language` != DEFAULT_LANG, else False.

    Returns:
        Decoded plain text (words separated by single spaces).

    Raises:
        LanguageNotFoundError, UnknownMorseCodeError.
    """
    lang_norm = _normalize_lang(language)
    if uppercase is None:
        uppercase = (lang_norm != DEFAULT_LANG)

    merged = _merge_language_dict(lang_norm)
    overrides = _get_language_overrides(lang_norm)
    reverse = _build_reverse_pref(merged, overrides)

    tokens = morse.split()
    out: List[str] = []

    for idx, tok in enumerate(tokens):
        if tok == "/":
            out.append(" ")
            continue
        ch = reverse.get(tok)
        if ch is None:
            if strict:
                raise UnknownMorseCodeError(tok, idx, lang_norm)
            out.append(unknown)
        else:
            out.append(ch)

    text = "".join(out)
    text = " ".join(text.split())
    if uppercase:
        text = text.upper()
    return text
