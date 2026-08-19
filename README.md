
# Institutional Books Enriched Text Parser #

This is a simple parser for [Institutional Books — Enriched Text
(IB-HL-ET)](https://huggingface.co/datasets/institutional/institutional-books-hl-enriched-text) datasets.


## Installation ##

Install directly from GitHub:

```bash
# With pip
pip install git+https://github.com/institutional/institutional-books-enriched-text-parser.git

# Or with uv
uv add git+https://github.com/institutional/institutional-books-enriched-text-parser.git
```


## Quick start ##

```python
from itertools import islice
from datasets import load_dataset
from ibet_parser import BookDataset

ds = load_dataset(
    "institutional/institutional-books-hl-enriched-text",
    split="train",
    streaming=True
)
books = BookDataset(ds)

# for book in books:           # for running over all books
for book in islice(books, 10):  # <-- for demonstration, take 10 books
    print(book.barcode, book.primary_language, book.token_count)
    for paragraph in book.paragraphs:
        print(paragraph.text[:100])

# Alternately to iterate over sections
for book in islice(books, 10):
    for section in book.sections:
        for paragraph in section.paragraphs:
            print(paragraph.text[:100])
        print()  # space between sections
```


## Filtering books ##

Filter at the dataset level by language or token count:

```python
# English books with at least 10k tokens
for book in books.filter(language="eng", token_count_min=10000):
    ...

# Multiple languages (the following means "English" or "French")
for book in books.filter(language=["eng", "fra"]):
    ...
```

Filters can be chained. Each call narrows the previous constraints:

```python
long_english_books = books.filter(language="eng").filter(token_count_min=50000)
for book in long_english_books:
    ...
```

## Filtering paragraphs ##

Each book provides `.paragraphs` and `.sections` iterators with their own
`.filter()` method. The `processed_middlematter_gen` column in the HF dataset is
essentially produced by the following filter:

```python
for book in books:
    for p in book.paragraphs.filter(
        language="eng",
        deduplicated=True,
        bpb_min=book.bpb.p10,
        bpb_max=book.bpb.p90,
    ):
        print(p.text)
```

This can be combined with book-level filters.

```python
for book in books.filter(language="eng"):
    for p in book.paragraphs.filter(
        language="eng",
        deduplicated=True,
        bpb_min=book.bpb.p10,
        bpb_max=book.bpb.p90,
    ):
        print(p.text)
```


### Paragraph object description ###

Paragraphs have the following structure

| Name | Type | Description |
|------|------|-------------|
| `paragraph.text` | `str` | Content of the paragraph |
| `paragraph.bpb` | `float` | `Qwen/Qwen3-0.6B-Base` bits-per-byte |
| `paragraph.language` | `str` | ISO 639-3 code for detected language of paragraph |
| `paragraph.is_duplicate` | `bool` | Whether this paragraph is a duplicate of another paragraph in the whole collection |


### Paragraph filter parameters ###

| Parameter | Type | Behavior |
|-----------|------|----------|
| `language` | `str` or `list[str]` | Include paragraphs whose language is in the list |
| `deduplicated` | `bool` | If `True`, exclude duplicate paragraphs |
| `bpb_min` | `float` | Include paragraphs with bits-per-byte >= value |
| `bpb_max` | `float` | Include paragraphs with bits-per-byte <= value |

Paragraphs with `None` for bits-per-byte are excluded when BPB bounds are
specified. Paragraphs with `None` for language are excluded when a language
filter is specified.

Absolute bits-per-byte values can be given. Certain per-book BPB values are
available for convenient reference.

| Parameter          |  Description                             |
|:-------------------|:-----------------------------------------|
| `book.bpb.p10`     | 10th percentile of bits-per-byte in book |
| `book.bpb.p30`     | 30th percentile of bits-per-byte in book |
| `book.bpb.median`  | 50th percentile of bits-per-byte in book |
| `book.bpb.p70`     | 70th percentile of bits-per-byte in book |
| `book.bpb.p90`     | 90th percentile of bits-per-byte in book |
| `book.bpb.avg`     | average bits-per-byte in book            |


## Iterating by section ##

```python
for section in book.sections.filter(deduplicated=True, language="eng"):
    print(f"Section bits-per-byte: {section.bpb}")
    for p in section.paragraphs:
        print(p.text)
```

Section filters apply to the paragraphs within each section. Sections where all
paragraphs are filtered out are silently skipped.


### Section object description ###

| Name | Type | Description |
|------|------|-------------|
| `section.paragraphs` | `list[paragraph]` | Content of the section as a list of paragraphs|
| `section.bpb` | `float` | Average `Qwen/Qwen3-0.6B-Base` bits-per-byte of contained paragraphs |


## Notes ##

- `BookDataset` is a **single-pass iterator**. This matches the behavior of
  HuggingFace streaming datasets. Once consumed, it cannot be restarted.
- HTML parsing of the underlying data is performed lazily on first access to
  `.paragraphs` or `.sections`.
- This library has **no runtime dependencies** beyond the standard library. You
  supply the HuggingFace dataset object yourself. This could be the streaming
  versions as in the examples above. This could also be a downloaded version, or
  specific shards, or even shards saved with similar annotations.


## About IDI ##


The Institutional Data Initiative at Harvard Law School Library works with
knowledge institutions—from libraries and museums to cultural groups and
government agencies—to refine and publish their collections as data. [Reach out
to collaborate on your collections](https://institutional.org/#get-involved).


## Cite ##

> TODO
