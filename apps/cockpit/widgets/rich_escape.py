"""Escape untrusted text before writing to Rich markup widgets."""

from __future__ import annotations

from rich.markup import escape


def escape_rich(text: str) -> str:
    return escape(text)
