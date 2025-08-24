"""
Command-line interface for the morsecode_handler package.

Examples:
    morsecode_handler encode "HELLO WORLD"
    morsecode_handler decode "... --- ..."
    morsecode_handler encode "Hello 🙂" --lang EN --lenient
"""

import argparse
import sys

from .core import encode, decode, DEFAULT_LANG
from .exceptions import MorseCodeError


def _add_common_args(p):
    # NOTE: Default for --lang is None so we can detect if user explicitly set it.
    p.add_argument("--lang", default=None, help=f"Language short code (default: {DEFAULT_LANG})")
    p.add_argument(
        "--lenient",
        action="store_true",
        help="Allow unknown chars/tokens (use '?') instead of raising errors.",
    )
    p.add_argument(
        "--preserve-case",
        action="store_true",
        help="Do not force uppercase even when --lang is provided.",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="morsecode_handler",
        description="Encode and decode Morse code with language support.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc = subparsers.add_parser("encode", help="Encode plain text to Morse code")
    enc.add_argument("text", help="The text to encode")
    _add_common_args(enc)

    dec = subparsers.add_parser("decode", help="Decode Morse code to plain text")
    dec.add_argument("morse", help="The Morse code string to decode")
    _add_common_args(dec)

    args = parser.parse_args(argv)

    # If user didn't pass --lang, fall back to DEFAULT_LANG and do NOT force uppercase.
    lang = args.lang or DEFAULT_LANG

    try:
        if args.command == "encode":
            result = encode(
                args.text,
                language=lang,
                strict=not args.lenient,
                unknown="?",
            )
        else:  # decode
            result = decode(
                args.morse,
                language=lang,
                strict=not args.lenient,
                unknown="?",
            )

        print(result)
        return 0

    except MorseCodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
