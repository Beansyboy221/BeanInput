"""Tests that relative links in docs/usage.md point to existing files."""

import pathlib
import re

DOCS_DIR = pathlib.Path(__file__).resolve().parents[1] / "docs"

FILE_LINK_REGEX = re.compile(r"\[.*?\]\(([^)]+)\)")


def test_relative_links_in_usage_doc():
    md_path = DOCS_DIR / "usage.md"
    text = md_path.read_text(encoding="utf-8")

    for match in FILE_LINK_REGEX.finditer(text):
        link = match.group(1)
        if link.startswith("http") or link.startswith("#"):
            continue

        resolved = (DOCS_DIR / link).resolve()
        assert resolved.exists(), f"Broken link '{link}' -> {resolved}"
