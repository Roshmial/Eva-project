#!/usr/bin/env python3
"""
Convert Markdown files to DOCX locally.

Usage:
  python ~/.hermes/scripts/md_to_docx.py input.md [output.docx]
  python ~/.hermes/scripts/md_to_docx.py /path/to/folder --batch

Notes:
- Local-only conversion, no cloud/API calls.
- Best effort formatting: headings, paragraphs, ordered/unordered lists,
  blockquotes, code blocks, simple tables, bold/italic inline text.
- DOCX is supported directly. Legacy .doc requires LibreOffice, if installed.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable

try:
    import markdown as md_lib
    from bs4 import BeautifulSoup, NavigableString, Tag
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_BREAK
except Exception as exc:  # pragma: no cover
    print(
        "Missing dependencies. Install with: python -m pip install python-docx markdown beautifulsoup4",
        file=sys.stderr,
    )
    print(f"Import error: {exc}", file=sys.stderr)
    raise SystemExit(2)


def output_path_for(input_path: Path, output_arg: str | None) -> Path:
    if output_arg:
        out = Path(output_arg).expanduser()
        if out.is_dir():
            return out / (input_path.stem + ".docx")
        return out
    return input_path.with_suffix(".docx")


def add_runs(paragraph, node) -> None:
    """Add inline content preserving basic bold/italic/code/links."""
    if isinstance(node, NavigableString):
        text = str(node)
        if text:
            paragraph.add_run(text)
        return

    if not isinstance(node, Tag):
        return

    if node.name == "br":
        paragraph.add_run().add_break(WD_BREAK.LINE)
        return

    if node.name in {"strong", "b"}:
        run = paragraph.add_run(node.get_text())
        run.bold = True
        return

    if node.name in {"em", "i"}:
        run = paragraph.add_run(node.get_text())
        run.italic = True
        return

    if node.name == "code":
        run = paragraph.add_run(node.get_text())
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        return

    if node.name == "a":
        text = node.get_text()
        href = node.get("href")
        if href and href not in text:
            text = f"{text} ({href})"
        paragraph.add_run(text)
        return

    for child in node.children:
        add_runs(paragraph, child)


def add_paragraph_from_tag(document: Document, tag: Tag, style: str | None = None):
    paragraph = document.add_paragraph(style=style) if style else document.add_paragraph()
    for child in tag.children:
        add_runs(paragraph, child)
    return paragraph


def iter_direct_children(container: Tag) -> Iterable[Tag]:
    for child in container.children:
        if isinstance(child, Tag):
            yield child


def add_list(document: Document, list_tag: Tag, ordered: bool = False, level: int = 0) -> None:
    style = "List Number" if ordered else "List Bullet"
    for li in list_tag.find_all("li", recursive=False):
        paragraph = document.add_paragraph(style=style)
        if level:
            paragraph.paragraph_format.left_indent = Pt(18 * level)
        for child in li.children:
            if isinstance(child, NavigableString):
                paragraph.add_run(str(child))
            elif isinstance(child, Tag) and child.name not in {"ul", "ol"}:
                add_runs(paragraph, child)
        for nested in li.find_all(["ul", "ol"], recursive=False):
            add_list(document, nested, ordered=(nested.name == "ol"), level=level + 1)


def add_table(document: Document, table_tag: Tag) -> None:
    rows = table_tag.find_all("tr")
    if not rows:
        return
    max_cols = max(len(row.find_all(["th", "td"], recursive=False)) for row in rows)
    if max_cols == 0:
        return
    table = document.add_table(rows=len(rows), cols=max_cols)
    table.style = "Table Grid"
    for r_idx, row in enumerate(rows):
        cells = row.find_all(["th", "td"], recursive=False)
        for c_idx, cell in enumerate(cells):
            docx_cell = table.cell(r_idx, c_idx)
            docx_cell.text = cell.get_text(" ", strip=True)
            if cell.name == "th":
                for paragraph in docx_cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True


def convert_md_to_docx(input_path: Path, output_path: Path) -> Path:
    text = input_path.read_text(encoding="utf-8")
    html = md_lib.markdown(
        text,
        extensions=["extra", "sane_lists", "toc", "nl2br"],
        output_format="html5",
    )
    soup = BeautifulSoup(html, "html.parser")

    document = Document()
    styles = document.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"].font.size = Pt(11)

    root_children = list(iter_direct_children(soup))
    if not root_children:
        document.add_paragraph(text)

    for tag in root_children:
        name = tag.name.lower()
        if re.fullmatch(r"h[1-6]", name):
            level = int(name[1])
            document.add_heading(tag.get_text(" ", strip=True), level=level)
        elif name == "p":
            add_paragraph_from_tag(document, tag)
        elif name == "ul":
            add_list(document, tag, ordered=False)
        elif name == "ol":
            add_list(document, tag, ordered=True)
        elif name == "blockquote":
            p = add_paragraph_from_tag(document, tag)
            p.style = "Intense Quote" if "Intense Quote" in [s.name for s in styles] else p.style
        elif name == "pre":
            code = tag.get_text().rstrip("\n")
            p = document.add_paragraph()
            run = p.add_run(code)
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif name == "table":
            add_table(document, tag)
        elif name == "hr":
            document.add_paragraph("—" * 20)
        else:
            text_value = tag.get_text(" ", strip=True)
            if text_value:
                document.add_paragraph(text_value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)
    return output_path


def convert_one(input_file: Path, output_arg: str | None = None) -> Path:
    input_path = input_file.expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in {".md", ".markdown", ".txt"}:
        raise ValueError(f"Expected markdown file, got: {input_path}")

    output_path = output_path_for(input_path, output_arg).expanduser().resolve()
    if output_path.suffix.lower() != ".docx":
        raise ValueError("This converter writes .docx directly. Use .docx as output extension.")
    return convert_md_to_docx(input_path, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to DOCX locally")
    parser.add_argument("input", help="Input .md file or folder with --batch")
    parser.add_argument("output", nargs="?", help="Output .docx file or output folder")
    parser.add_argument("--batch", action="store_true", help="Convert all .md files in input folder")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    try:
        if args.batch:
            if not input_path.is_dir():
                raise ValueError("--batch expects input to be a folder")
            output_dir = Path(args.output).expanduser() if args.output else input_path
            converted = []
            for md_file in sorted(input_path.glob("*.md")):
                converted.append(convert_one(md_file, str(output_dir)))
            for path in converted:
                print(path)
            print(f"Converted {len(converted)} file(s).")
        else:
            print(convert_one(input_path, args.output))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
