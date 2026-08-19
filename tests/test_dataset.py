from ibllm_parser import BookDataset


def _make_row(barcode="book1", language="eng", token_count=5000, middlematter=""):
    """
    Make a mock row.
    """
    return {
        "barcode_src": barcode,
        "primary_language_gen": language,
        "token_count_gen": token_count,
        "char_count_gen": token_count * 4,
        "word_count_gen": token_count // 2,
        "sentence_count_gen": token_count // 20,
        "paragraph_count_gen": token_count // 100,
        "section_count_gen": token_count // 500,
        "perplexity_min_gen": 5.0,
        "perplexity_max_gen": 1000.0,
        "perplexity_median_gen": 100.0,
        "perplexity_avg_gen": 150.0,
        "perplexity_p10_gen": 20.0,
        "perplexity_p30_gen": 50.0,
        "perplexity_p70_gen": 200.0,
        "perplexity_p90_gen": 500.0,
        "middlematter_gen": middlematter,
    }


def _sample_dataset():
    """
    A dataset of 5 mock books.
    """
    return [
        _make_row("book1", "eng", 10000),
        _make_row("book2", "fra", 5000),
        _make_row("book3", "eng", 20000),
        _make_row("book4", "deu", 15000),
        _make_row("book5", "spa", 3000),
    ]


class TestBookDataset:
    def test_iteration(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds)
        assert len(books) == 5
        assert books[0].barcode == "book1"

    def test_single_pass(self):
        ds = BookDataset(iter(_sample_dataset()))
        first = list(ds)
        second = list(ds)
        assert len(first) == 5
        assert len(second) == 0

    def test_filter_language_string(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds.filter(language="eng"))
        assert len(books) == 2
        assert all(b.primary_language == "eng" for b in books)

    def test_filter_language_list(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds.filter(language=["eng", "fra"]))
        assert len(books) == 3

    def test_filter_token_count_min(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds.filter(token_count_min=10000))
        assert len(books) == 3
        assert all(b.token_count >= 10000 for b in books)

    def test_filter_token_count_max(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds.filter(token_count_max=5000))
        assert len(books) == 2

    def test_filter_combined(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds.filter(language="eng", token_count_min=15000))
        assert len(books) == 1
        assert books[0].barcode == "book3"

    def test_filter_chained(self):
        ds = BookDataset(_sample_dataset())
        books = list(ds.filter(language=["eng", "fra"]).filter(token_count_min=8000))
        assert len(books) == 2
        barcodes = {b.barcode for b in books}
        assert barcodes == {"book1", "book3"}

    def test_chained_language_narrows(self):
        ds = BookDataset(_sample_dataset())
        books = list(
            ds.filter(language=["eng", "fra", "deu"]).filter(language=["eng", "spa"])
        )
        # Intersection: only "eng"
        assert len(books) == 2
        assert all(b.primary_language == "eng" for b in books)


class TestBookParsing:
    def test_paragraphs_from_middlematter(self):
        html = """
        <section data-perplexity="100.0">
          <p data-perplexity="50.0" data-language="eng">Hello.</p>
          <p data-perplexity="75.0" data-language="eng">World.</p>
        </section>
        """
        row = _make_row(middlematter=html)
        ds = BookDataset([row])
        book = next(iter(ds))
        paragraphs = list(book.paragraphs)
        assert len(paragraphs) == 2
        assert paragraphs[0].text == "Hello."

    def test_perplexity_stats(self):
        row = _make_row()
        ds = BookDataset([row])
        book = next(iter(ds))
        assert book.perplexity.p10 == 20.0
        assert book.perplexity.p90 == 500.0
        assert book.perplexity.min == 5.0

    def test_empty_middlematter(self):
        row = _make_row(middlematter="")
        ds = BookDataset([row])
        book = next(iter(ds))
        assert list(book.paragraphs) == []
        assert list(book.sections) == []

    def test_none_middlematter(self):
        row = _make_row()
        row["middlematter_gen"] = None
        ds = BookDataset([row])
        book = next(iter(ds))
        assert list(book.paragraphs) == []
