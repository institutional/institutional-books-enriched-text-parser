"""
dataset.py - Take a HF IBLLM Dataset, yield Book objects

This is the primary interface.
"""

from __future__ import annotations
from typing import Iterator, Iterable, Any

from ibllm_parser.book import Book
from ibllm_parser.utils import merge_languages, normalize_language, tighten_max, tighten_min


class BookDataset:
    """
    Wraps an iterable of dataset rows and yields Book objects.

    This is a single-pass iterator. Once consumed, it cannot be restarted.
    """

    def __init__(
        self,
        dataset: Iterable[dict[str, Any]],
        *,
        _languages: list[str] | None = None,
        _token_count_min: int | None = None,
        _token_count_max: int | None = None,
    ):
        self._dataset = dataset
        self._languages = _languages
        self._token_count_min = _token_count_min
        self._token_count_max = _token_count_max

    def filter(
        self,
        *,
        language: str | list[str] | None = None,
        token_count_min: int | None = None,
        token_count_max: int | None = None,
    ) -> BookDataset:
        return BookDataset(
            self._dataset,
            _languages=merge_languages(self._languages, normalize_language(language)),
            _token_count_min=tighten_min(self._token_count_min, token_count_min),
            _token_count_max=tighten_max(self._token_count_max, token_count_max),
        )

    def _row_passes(self, row: dict[str, Any]) -> bool:
        if self._languages is not None:
            if row.get("primary_language_gen") not in self._languages:
                return False
        if self._token_count_min is not None:
            if row.get("token_count_gen", 0) < self._token_count_min:
                return False
        if self._token_count_max is not None:
            if row.get("token_count_gen", 0) > self._token_count_max:
                return False
        return True

    def __iter__(self) -> Iterator[Book]:
        for row in self._dataset:
            if self._row_passes(row):
                yield Book(row)
