"""
utils.py - common utilities
"""

from __future__ import annotations


def normalize_language(language: str | list[str] | None) -> list[str] | None:
    """
    Always expect lists of languages.
    """
    if language is None:
        return None
    if isinstance(language, str):
        return [language]
    return list(language)


def merge_languages(
    existing: list[str] | None, new: list[str] | None
) -> list[str] | None:
    """
    Intersect two language inclusion lists. None means "no constraint".
    """
    if existing is None:
        return new
    if new is None:
        return existing
    return [l for l in new if l in existing]


def tighten_min(
    existing: float | None, new: float | None
) -> float | None:
    """
    Combine two lower bounds by taking the stricter (larger) one.
    """
    if existing is None:
        return new
    if new is None:
        return existing
    return max(existing, new)


def tighten_max(
    existing: float | None, new: float | None
) -> float | None:
    """
    Combine two upper bounds by taking the stricter (smaller) one.
    """
    if existing is None:
        return new
    if new is None:
        return existing
    return min(existing, new)
