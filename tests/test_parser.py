from ibllm_parser.parser import parse_middlematter


def test_basic_section_and_paragraphs():
    html = """
    <section data-perplexity="100.0">
      <p data-perplexity="50.0" data-language="eng">Hello world.</p>
      <p data-perplexity="75.0" data-language="fra">Bonjour le monde.</p>
    </section>
    """
    sections = parse_middlematter(html)
    assert len(sections) == 1
    assert sections[0].perplexity == 100.0
    assert len(sections[0].paragraphs) == 2
    assert sections[0].paragraphs[0].text == "Hello world."
    assert sections[0].paragraphs[0].perplexity == 50.0
    assert sections[0].paragraphs[0].language == "eng"
    assert sections[0].paragraphs[0].is_duplicate is False
    assert sections[0].paragraphs[1].text == "Bonjour le monde."
    assert sections[0].paragraphs[1].language == "fra"


def test_aside_marks_duplicates():
    html = """
    <section data-perplexity="200.0">
      <p data-perplexity="30.0" data-language="eng">Original text.</p>
      <aside data-cluster="book1:42">
        <p data-perplexity="5.0" data-language="eng">Duplicate text.</p>
      </aside>
      <p data-perplexity="60.0" data-language="eng">More original.</p>
    </section>
    """
    sections = parse_middlematter(html)
    assert len(sections) == 1
    paragraphs = sections[0].paragraphs
    assert len(paragraphs) == 3
    assert paragraphs[0].is_duplicate is False
    assert paragraphs[1].is_duplicate is True
    assert paragraphs[1].text == "Duplicate text."
    assert paragraphs[2].is_duplicate is False


def test_multiple_sections():
    html = """
    <section data-perplexity="100.0">
      <p data-perplexity="50.0" data-language="eng">First.</p>
    </section>
    <section data-perplexity="200.0">
      <p data-perplexity="80.0" data-language="deu">Zweite.</p>
    </section>
    """
    sections = parse_middlematter(html)
    assert len(sections) == 2
    assert sections[0].perplexity == 100.0
    assert sections[1].perplexity == 200.0
    assert sections[1].paragraphs[0].language == "deu"


def test_missing_attributes():
    html = """
    <section>
      <p>No attributes at all.</p>
      <p data-perplexity="10.0">Has perplexity but no language.</p>
      <p data-language="eng">Has language but no perplexity.</p>
    </section>
    """
    sections = parse_middlematter(html)
    assert sections[0].perplexity is None
    paragraphs = sections[0].paragraphs
    assert paragraphs[0].perplexity is None
    assert paragraphs[0].language is None
    assert paragraphs[1].perplexity == 10.0
    assert paragraphs[1].language is None
    assert paragraphs[2].perplexity is None
    assert paragraphs[2].language == "eng"


def test_empty_input():
    assert parse_middlematter("") == []
    assert parse_middlematter(None or "") == []


def test_text_concatenation_within_paragraph():
    html = """
    <section data-perplexity="50.0">
      <p data-perplexity="20.0" data-language="eng">Part one. Part two.</p>
    </section>
    """
    sections = parse_middlematter(html)
    assert sections[0].paragraphs[0].text == "Part one. Part two."
