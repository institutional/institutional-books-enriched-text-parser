"""
parser.py - from HTML to paragraphs and sections
"""

from __future__ import annotations
from html.parser import HTMLParser

from ibllm_parser.elements import Paragraph, Section

#
# Broadly, annotations are in HTML attributes and the underlying text is in the
# data inside tags. There can be limited tag nesting: section can contain aside
# which can contain p. Thus we need to handle the tree recursion appropriately.
#


class _MiddlematterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections: list[Section] = []
        self._current_section_paragraphs: list[Paragraph] = []
        self._current_section_perplexity: float | None = None
        self._in_section = False
        self._in_aside = False
        self._in_p = False
        self._current_text: list[str] = []
        self._current_p_perplexity: float | None = None
        self._current_p_language: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attr_dict = dict(attrs)
        if tag == "section":
            self._in_section = True
            self._current_section_paragraphs = []
            perp = attr_dict.get("data-perplexity")
            self._current_section_perplexity = float(perp) if perp else None
        elif tag == "aside":
            self._in_aside = True
        elif tag == "p":
            self._in_p = True
            self._current_text = []
            perp = attr_dict.get("data-perplexity")
            self._current_p_perplexity = float(perp) if perp else None
            self._current_p_language = attr_dict.get("data-language")

    def handle_endtag(self, tag: str):
        if tag == "p" and self._in_p:
            paragraph = Paragraph(
                text="".join(self._current_text),
                perplexity=self._current_p_perplexity,
                language=self._current_p_language,
                is_duplicate=self._in_aside,
            )
            self._current_section_paragraphs.append(paragraph)
            self._in_p = False
        elif tag == "aside":
            self._in_aside = False
        elif tag == "section" and self._in_section:
            self.sections.append(
                Section(
                    perplexity=self._current_section_perplexity,
                    paragraphs=self._current_section_paragraphs,
                )
            )
            self._in_section = False

    def handle_data(self, data: str):
        if self._in_p:
            self._current_text.append(data)


def parse_middlematter(html: str) -> list[Section]:
    parser = _MiddlematterParser()
    parser.feed(html)
    return parser.sections
