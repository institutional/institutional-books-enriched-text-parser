"""
elements.py - models
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Paragraph:
    text: str
    perplexity: float | None
    language: str | None
    is_duplicate: bool


@dataclass(slots=True)
class Section:
    perplexity: float | None
    paragraphs: list[Paragraph]
