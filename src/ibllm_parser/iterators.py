"""
iterators.py - tools to iterate sections and paragraphs
"""

from __future__ import annotations
from typing import Iterator

from ibllm_parser.elements import Paragraph, Section
from ibllm_parser.utils import merge_languages, normalize_language, tighten_max, tighten_min


def _paragraph_passes(
    p: Paragraph,
    *,
    languages: list[str] | None,
    deduplicated: bool,
    perplexity_min: float | None,
    perplexity_max: float | None,
) -> bool:
    if deduplicated and p.is_duplicate:
        return False
    if languages is not None:
        if p.language is None or p.language not in languages:
            return False
    if perplexity_min is not None:
        if p.perplexity is None or p.perplexity < perplexity_min:
            return False
    if perplexity_max is not None:
        if p.perplexity is None or p.perplexity > perplexity_max:
            return False
    return True


class ParagraphIterator:
    def __init__(
        self,
        paragraphs: list[Paragraph],
        *,
        languages: list[str] | None = None,
        deduplicated: bool = False,
        perplexity_min: float | None = None,
        perplexity_max: float | None = None,
    ):
        self._paragraphs = paragraphs
        self._languages = languages
        self._deduplicated = deduplicated
        self._perplexity_min = perplexity_min
        self._perplexity_max = perplexity_max

    def filter(
        self,
        *,
        language: str | list[str] | None = None,
        deduplicated: bool = False,
        perplexity_min: float | None = None,
        perplexity_max: float | None = None,
    ) -> ParagraphIterator:
        """
        Return a new paragraph filter with narrower constraints.
        """
        return ParagraphIterator(
            self._paragraphs,
            languages=merge_languages(self._languages, normalize_language(language)),
            deduplicated=self._deduplicated or deduplicated,
            perplexity_min=tighten_min(self._perplexity_min, perplexity_min),
            perplexity_max=tighten_max(self._perplexity_max, perplexity_max),
        )

    def __iter__(self) -> Iterator[Paragraph]:
        for p in self._paragraphs:
            if _paragraph_passes(
                p,
                languages=self._languages,
                deduplicated=self._deduplicated,
                perplexity_min=self._perplexity_min,
                perplexity_max=self._perplexity_max,
            ):
                yield p


class SectionIterator:
    def __init__(
        self,
        sections: list[Section],
        *,
        languages: list[str] | None = None,
        deduplicated: bool = False,
        perplexity_min: float | None = None,
        perplexity_max: float | None = None,
    ):
        self._sections = sections
        self._languages = languages
        self._deduplicated = deduplicated
        self._perplexity_min = perplexity_min
        self._perplexity_max = perplexity_max

    def filter(
        self,
        *,
        language: str | list[str] | None = None,
        deduplicated: bool = False,
        perplexity_min: float | None = None,
        perplexity_max: float | None = None,
    ) -> SectionIterator:
        """
        Return a new section filter with narrower constraints.
        """
        return SectionIterator(
            self._sections,
            languages=merge_languages(self._languages, normalize_language(language)),
            deduplicated=self._deduplicated or deduplicated,
            perplexity_min=tighten_min(self._perplexity_min, perplexity_min),
            perplexity_max=tighten_max(self._perplexity_max, perplexity_max),
        )

    def __iter__(self) -> Iterator[Section]:
        for section in self._sections:
            filtered = [
                p
                for p in section.paragraphs
                if _paragraph_passes(
                    p,
                    languages=self._languages,
                    deduplicated=self._deduplicated,
                    perplexity_min=self._perplexity_min,
                    perplexity_max=self._perplexity_max,
                )
            ]
            # Filters are applied to underlying paragraphs. It could be that all
            # paragraphs are filtered away. In that case, don't return that
            # (empty) section and instead move to the next.
            if filtered:
                yield Section(
                    perplexity=section.perplexity,
                    paragraphs=filtered,
                )
