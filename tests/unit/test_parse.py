from pathlib import Path

import pymupdf
import pytest
from pypdf import PdfReader, PdfWriter

from fraudfirstaid.ingest.parse import (
    ParseError,
    clean_text,
    drop_repeated_lines,
    parse_file,
    parse_html,
    parse_pdf_pymupdf,
    parse_pdf_pypdf,
    parse_text,
    split_pages,
)

BODY = (
    "This is a sufficiently long paragraph of ordinary document text. "
    "It contains enough characters for the parser to recognize a text layer. "
    "The paragraph is repeated where necessary to make a realistic test document."
)


def make_pdf(path: Path, pages: list[str], sizes: list[int] | None = None) -> Path:
    doc = pymupdf.open()
    for index, content in enumerate(pages):
        page = doc.new_page()
        size = sizes[index] if sizes else 11
        page.insert_text((72, 72), content, fontsize=size)
        page.insert_text((72, 110), BODY, fontsize=11)
    doc.save(path)
    doc.close()
    return path


def body_page(page: pymupdf.Page, text: str = BODY) -> None:
    page.insert_text((72, 72), text, fontsize=11)


def test_pdf_page_numbers(tmp_path: Path) -> None:
    path = make_pdf(tmp_path / "pages.pdf", ["First page", "Second page"])
    parsed = parse_pdf_pymupdf(path)
    assert [page.page_no for page in parsed.pages] == [1, 2]
    assert len(parsed.pages) == 2


def test_pdf_detects_large_font_headings_and_page_paths(tmp_path: Path) -> None:
    path = tmp_path / "headings.pdf"
    doc = pymupdf.open()

    page = doc.new_page()
    page.insert_text((72, 72), "Main heading", fontsize=24)
    body_page(page)

    page = doc.new_page()
    page.insert_text((72, 72), "Subheading", fontsize=18)
    body_page(page)

    doc.save(path)
    doc.close()

    parsed = parse_pdf_pymupdf(path)
    assert parsed.title == "Main heading"
    assert parsed.pages[1].headings
    assert "Main heading" in parsed.pages[1].headings


def test_pdf_table_is_extracted_as_markdown(tmp_path: Path) -> None:
    path = tmp_path / "table.pdf"
    doc = pymupdf.open()
    page = doc.new_page()

    x_positions = [72, 180, 300]
    y_positions = [72, 100, 128]

    for x in x_positions:
        page.draw_line((x, y_positions[0]), (x, y_positions[-1]))
    for y in y_positions:
        page.draw_line((x_positions[0], y), (x_positions[-1], y))

    page.insert_text((80, 90), "Name")
    page.insert_text((190, 90), "Value")
    page.insert_text((80, 118), "Example")
    page.insert_text((190, 118), "123")
    page.insert_text((72, 170), BODY, fontsize=11)

    doc.save(path)
    doc.close()

    parsed = parse_pdf_pymupdf(path)
    assert "|" in parsed.pages[0].text


def test_scanned_pdf_without_text_layer_raises(tmp_path: Path) -> None:
    path = tmp_path / "scanned.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(path)
    doc.close()

    with pytest.raises(ParseError) as error:
        parse_pdf_pymupdf(path)

    assert error.value.reason == "no_text_layer"


def test_corrupt_pdf_raises_parse_error(tmp_path: Path) -> None:
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"this is not a PDF")

    with pytest.raises(ParseError) as error:
        parse_pdf_pymupdf(path)

    assert error.value.reason == "corrupt"


def test_encrypted_pdf_raises_parse_error(tmp_path: Path) -> None:
    source = make_pdf(tmp_path / "source.pdf", [BODY])
    reader = PdfReader(source)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt("secret")
    path = tmp_path / "encrypted.pdf"

    with path.open("wb") as output:
        writer.write(output)

    with pytest.raises(ParseError) as error:
        parse_pdf_pypdf(path)

    assert error.value.reason == "encrypted"


def test_repeated_headers_and_footers_are_removed() -> None:
    pages = [f"Organisation Report\nPage {number}\n{BODY}\nConfidential" for number in range(1, 5)]

    cleaned = drop_repeated_lines(pages)
    assert all("Organisation Report" not in page for page in cleaned)
    assert all("Confidential" not in page for page in cleaned)


def test_both_pdf_parsers_return_all_pages(tmp_path: Path) -> None:
    path = make_pdf(
        tmp_path / "both.pdf",
        ["First page", "Second page", "Third page"],
    )

    pymupdf_result = parse_pdf_pymupdf(path)
    pypdf_result = parse_pdf_pypdf(path)

    assert len(pymupdf_result.pages) == 3
    assert len(pypdf_result.pages) == 3
    assert pymupdf_result.parser == "pymupdf"
    assert pypdf_result.parser == "pypdf"


def test_clean_text_normalizes_and_removes_unwanted_characters() -> None:
    result = clean_text("\uff21\uff22\uff23\x00soft\u00adhyphen  \n\n\nNext")
    assert result == "ABCsofthyphen\n\nNext"


def test_tamil_text_survives_cleaning(tmp_path: Path) -> None:
    tamil = (
        "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd\u0ba8\u0bbe\u0b9f\u0bc1 "
        "\u0b87\u0ba3\u0bc8\u0baf "
        "\u0baa\u0bbe\u0ba4\u0bc1\u0b95\u0bbe\u0baa\u0bcd\u0baa\u0bc1 "
        "\u0bb5\u0bbf\u0bb4\u0bbf\u0baa\u0bcd\u0baa\u0bc1"
        "\u0ba3\u0bb0\u0bcd\u0bb5\u0bc1"
    )
    path = tmp_path / "tamil.txt"
    path.write_text(tamil, encoding="utf-8")

    parsed = parse_text(path)
    assert tamil in parsed.pages[0].text


def test_markdown_pages_keep_heading_paths(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text(
        "# Main heading\n\n"
        + (BODY * 15)
        + "\n\n## Account security\n\n"
        + (BODY * 15)
        + "\n\n### Passwords\n\n"
        + (BODY * 15),
        encoding="utf-8",
    )

    parsed = parse_text(path)

    assert parsed.title == "Main heading"
    assert len(parsed.pages) >= 2
    assert parsed.pages[0].headings == []
    assert any("Main heading" in page.headings for page in parsed.pages[1:])


def test_rst_and_asciidoc_headings_are_converted(tmp_path: Path) -> None:
    rst = tmp_path / "guide.rst"
    rst.write_text("Main heading\n============\n\n" + BODY, encoding="utf-8")

    adoc = tmp_path / "guide.adoc"
    adoc.write_text("== Main heading\n\n" + BODY, encoding="utf-8")

    rst_result = parse_text(rst)
    adoc_result = parse_text(adoc)

    assert rst_result.title == "Main heading"
    assert adoc_result.title == "Main heading"


def test_html_extracts_main_content(tmp_path: Path) -> None:
    path = tmp_path / "article.html"
    path.write_text(
        "<html><head><title>Security guide</title></head><body>"
        "<h1>Online safety</h1>"
        f"<p>{BODY}</p>"
        "</body></html>",
        encoding="utf-8",
    )

    parsed = parse_html(path)

    assert parsed.kind == "html"
    assert parsed.pages
    assert parsed.title == "Online safety"
    assert BODY in parsed.pages[0].text


def test_empty_and_unsupported_files_raise_parse_error(tmp_path: Path) -> None:
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")

    with pytest.raises(ParseError) as empty_error:
        parse_file(empty)
    assert empty_error.value.reason == "empty"

    unsupported = tmp_path / "archive.zip"
    unsupported.write_bytes(b"not parsed")

    with pytest.raises(ParseError) as unsupported_error:
        parse_file(unsupported)
    assert unsupported_error.value.reason == "unsupported_type"


def test_split_pages_keeps_paragraphs_together() -> None:
    paragraphs = ["A" * 900, "B" * 900, "C" * 900, "D" * 900]
    pages = split_pages("\n\n".join(paragraphs), size=1800)

    assert len(pages) == 2
    assert "A" * 900 in pages[0]
    assert "B" * 900 in pages[0]
    assert "C" * 900 in pages[1]
    assert "D" * 900 in pages[1]


def test_headings_inside_code_blocks_are_ignored(tmp_path: Path) -> None:
    path = tmp_path / "code.md"
    path.write_text(
        "# Real heading\n\n```python\n# Not a heading\nprint('hello')\n```\n\n" + BODY,
        encoding="utf-8",
    )

    parsed = parse_text(path)

    assert parsed.title == "Real heading"
    assert all("Not a heading" not in page.headings for page in parsed.pages)
