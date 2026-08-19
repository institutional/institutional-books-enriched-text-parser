"""
book.py - represent a book and access iterators to its sections and paragraphs
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ibllm_parser.elements import Section
from ibllm_parser.iterators import ParagraphIterator, SectionIterator
from ibllm_parser.parser import parse_middlematter


if TYPE_CHECKING:
    from typing import Any


@dataclass(slots=True, frozen=True)
class PerplexityStats:
    min: float
    max: float
    median: float
    avg: float
    p10: float
    p30: float
    p70: float
    p90: float


class Book:
    __slots__ = (
        "barcode",
        "primary_language",
        "token_count",
        "char_count",
        "word_count",
        "sentence_count",
        "paragraph_count",
        "section_count",
        "perplexity",
        "_middlematter",
        "_parsed",
    )

    def __init__(self, row: dict[str, Any]):
        self.barcode: str = row["barcode_src"]
        self.primary_language: str = row["primary_language_gen"]
        self.token_count: int = row["token_count_gen"]
        self.char_count: int = row["char_count_gen"]
        self.word_count: int = row["word_count_gen"]
        self.sentence_count: int = row["sentence_count_gen"]
        self.paragraph_count: int = row["paragraph_count_gen"]
        self.section_count: int = row["section_count_gen"]
        self.perplexity = PerplexityStats(
            min=row["perplexity_min_gen"],
            max=row["perplexity_max_gen"],
            median=row["perplexity_median_gen"],
            avg=row["perplexity_avg_gen"],
            p10=row["perplexity_p10_gen"],
            p30=row["perplexity_p30_gen"],
            p70=row["perplexity_p70_gen"],
            p90=row["perplexity_p90_gen"],
        )
        self._middlematter: str | None = row.get("middlematter_gen")
        self._parsed: list[Section] | None = None

    def _ensure_parsed(self) -> list[Section]:
        if self._parsed is None:
            self._parsed = parse_middlematter(self._middlematter or "")
        return self._parsed

    @property
    def paragraphs(self) -> ParagraphIterator:
        sections = self._ensure_parsed()
        all_paragraphs = [p for s in sections for p in s.paragraphs]
        return ParagraphIterator(all_paragraphs)

    @property
    def sections(self) -> SectionIterator:
        sections = self._ensure_parsed()
        return SectionIterator(sections)
