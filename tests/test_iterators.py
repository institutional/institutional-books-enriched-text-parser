from ibllm_parser.elements import Paragraph, Section
from ibllm_parser.iterators import ParagraphIterator, SectionIterator


def _make_paragraphs():
    return [
        Paragraph(
            "English low perp", perplexity=20.0, language="eng", is_duplicate=False
        ),
        Paragraph(
            "English high perp", perplexity=500.0, language="eng", is_duplicate=False
        ),
        Paragraph(
            "French mid perp", perplexity=100.0, language="fra", is_duplicate=False
        ),
        Paragraph("Duplicate eng", perplexity=50.0, language="eng", is_duplicate=True),
        Paragraph("No perplexity", perplexity=None, language="eng", is_duplicate=False),
        Paragraph("No language", perplexity=30.0, language=None, is_duplicate=False),
    ]


class TestParagraphIterator:
    def test_no_filter(self):
        paragraphs = _make_paragraphs()
        it = ParagraphIterator(paragraphs)
        assert list(it) == paragraphs

    def test_filter_by_language_string(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(language="eng"))
        assert all(p.language == "eng" for p in filtered)
        assert len(filtered) == 4

    def test_filter_by_language_list(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(language=["eng", "fra"]))
        assert all(p.language in ("eng", "fra") for p in filtered)
        assert len(filtered) == 5

    def test_filter_deduplicated(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(deduplicated=True))
        assert all(not p.is_duplicate for p in filtered)
        assert len(filtered) == 5

    def test_filter_perplexity_min(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(perplexity_min=50.0))
        assert all(p.perplexity is not None and p.perplexity >= 50.0 for p in filtered)
        assert len(filtered) == 3

    def test_filter_perplexity_max(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(perplexity_max=50.0))
        assert all(p.perplexity is not None and p.perplexity <= 50.0 for p in filtered)
        assert len(filtered) == 3

    def test_filter_perplexity_range(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(perplexity_min=25.0, perplexity_max=200.0))
        assert len(filtered) == 3
        texts = {p.text for p in filtered}
        assert texts == {"French mid perp", "Duplicate eng", "No language"}

    def test_filter_excludes_none_perplexity(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(perplexity_min=0.0))
        assert all(p.perplexity is not None for p in filtered)

    def test_filter_excludes_none_language(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(language="eng"))
        assert all(p.language is not None for p in filtered)

    def test_chained_filters(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(
            it.filter(language="eng", deduplicated=True).filter(
                perplexity_min=10.0, perplexity_max=100.0
            )
        )
        assert len(filtered) == 1
        assert filtered[0].text == "English low perp"

    def test_chained_language_narrows(self):
        it = ParagraphIterator(_make_paragraphs())
        filtered = list(it.filter(language=["eng", "fra"]).filter(language="eng"))
        assert all(p.language == "eng" for p in filtered)


class TestSectionIterator:
    def _make_sections(self):
        return [
            Section(
                perplexity=100.0,
                paragraphs=[
                    Paragraph(
                        "S1P1", perplexity=50.0, language="eng", is_duplicate=False
                    ),
                    Paragraph(
                        "S1P2", perplexity=200.0, language="fra", is_duplicate=False
                    ),
                ],
            ),
            Section(
                perplexity=300.0,
                paragraphs=[
                    Paragraph(
                        "S2P1", perplexity=10.0, language="eng", is_duplicate=True
                    ),
                ],
            ),
            Section(
                perplexity=50.0,
                paragraphs=[
                    Paragraph(
                        "S3P1", perplexity=80.0, language="deu", is_duplicate=False
                    ),
                ],
            ),
        ]

    def test_no_filter(self):
        sections = self._make_sections()
        result = list(SectionIterator(sections))
        assert len(result) == 3

    def test_filter_skips_empty_sections(self):
        sections = self._make_sections()
        result = list(SectionIterator(sections).filter(deduplicated=True))
        # Section 2 has only a duplicate paragraph, so it gets skipped
        assert len(result) == 2
        assert result[0].perplexity == 100.0
        assert result[1].perplexity == 50.0

    def test_filter_narrows_paragraphs(self):
        sections = self._make_sections()
        result = list(SectionIterator(sections).filter(language="eng"))
        # Section 1 has one eng paragraph, Section 2 has one eng (dup), Section 3 has none
        assert len(result) == 2
        assert len(result[0].paragraphs) == 1
        assert result[0].paragraphs[0].text == "S1P1"

    def test_section_perplexity_unchanged_after_filter(self):
        sections = self._make_sections()
        result = list(SectionIterator(sections).filter(language="eng"))
        # Original section perplexity is preserved
        assert result[0].perplexity == 100.0
