"""Formatting helpers for CLI output."""

from __future__ import annotations

from collections.abc import Iterable


def format_bullet_list(items: Iterable[str], markdown: bool) -> str:
    """Return ``items`` formatted as a bullet list.

    Args:
        items: Sequence of strings to format.
        markdown: When ``True``, wrap items in backticks for Markdown output.

    Returns:
        Newline-separated bullet points or ``"(none)"`` when ``items`` is empty.
    """

    if not items:
        return "(none)"
    template = "- `{}`" if markdown else "- {}"
    return "\n".join(template.format(item) for item in items)
