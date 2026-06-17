#!/usr/bin/env python3
"""Convert Markdown files to DOCX locally.

Usage:
  python scripts/md_to_docx.py input.md [output.docx]
  python scripts/md_to_docx.py folder --batch [output_folder]

Dependencies: python-docx markdown beautifulsoup4 lxml
Install: python -m pip install python-docx markdown beautifulsoup4
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

try:
    import markdown as md_lib
    from bs4 import BeautifulSoup, NavigableString, Tag
    from docx import Document
    from docx.enum.text import WD_BREAK
    from docx.shared import Pt
except Exception as exc:
    raise SystemExit(
        "Missing dependencies. Install with: python -m pip install python-docx markdown beautifulsoup4\n"
        f"Import error: {exc}"
    )


def add_runs(paragraph, node):
    if isinstance(node, NavigableString):
        if str(node):
            paragraph.add_run(str(node))
        return
    if not isinstance(node, Tag):
        return
    if node.name == "br":
        paragraph.add_run().add_break(WD_BREAK.LINE)
        return
    if node.name in {"strong", "b"}:
        r = paragraph.add_run(node.get_text())
        r.bold = True
        return
    if node.name in {"em", "i"}:
        r = paragraph.add_run(node.get_text())
        r.italic = True
        return
    if node.name == "code":
        r = paragraph.add_run(node.get_text())
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        return
    if node.name == "a":
        text = node.get_text()
        href = node.get("href")
        paragraph.add_run(f"{text} ({href})" if href and href not in text else text)
        return
    for child in node.children:
        add_runs(paragraph, child)


def paragraph_from_tag(doc, tag, style=None):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    for child in tag.children:
        add_runs(p, child)
    return p


def add_list(doc, list_tag, ordered=False, level=0):
    style = "List Number" if ordered else "List Bullet"
    for li in list_tag.find_all("li", recursive=False):
        p = doc.add_paragraph(style=style)
        if level:
            p.paragraph_format.left_indent = Pt(18 * level)
        for child in li.children:
            if isinstance(child, NavigableString):
                p.add_run(str(child))
            elif isinstance(child, Tag) and child.name not in {"ul", "ol"}:
                add_runs(p, child)
        for nested in li.find_all(["ul", "ol"], recursive=False):
            add_list(doc, nested, ordered=(nested.name == "ol"), level=level + 1)


def add_table(doc, table_tag):
    rows = table_tag.find_all("tr")
    if not rows:
        return
    max_cols = max(len(r.find_all(["th", "td"], recursive=False)) for r in rows)
    if not max_cols:
        return
    table = doc.add_table(rows=len(rows), cols=max_cols)
    table.style = "Table Grid"
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row.find_all(["th", "td"], recursive=False)):
            target = table.cell(ri, ci)
            target.text = cell.get_text(" ", strip=True)
            if cell.name == "th":
                for p in target.paragraphs:
                    for run in p.runs:
                        run.bold = True


def convert(input_path: Path, output_path: Path):
    text = input_path.read_text(encoding="utf-8")
    html = md_lib.markdown(text, extensions=["extra", "sane_lists", "toc", "nl2br"], output_format="html5")
    soup = BeautifulSoup(html, "html.parser")
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)

    for tag in [c for c in soup.children if isinstance(c, Tag)]:
        name = tag.name.lower()
        if re.fullmatch(r"h[1-6]", name):
            doc.add_heading(tag.get_text(" ", strip=True), level=int(name[1]))
        elif name == "p":
            paragraph_from_tag(doc, tag)
        elif name == "ul":
            add_list(doc, tag, ordered=False)
        elif name == "ol":
            add_list(doc, tag, ordered=True)
        elif name == "blockquote":
            paragraph_from_tag(doc, tag, style="Intense Quote")
        elif name == "pre":
            p = doc.add_paragraph()
            r = p.add_run(tag.get_text().rstrip("\n"))
            r.font.name = "Consolas"
            r.font.size = Pt(9)
        elif name == "table":
            add_table(doc, tag)
        elif name == "hr":
            doc.add_paragraph("—" * 20)
        else:
            body = tag.get_text(" ", strip=True)
            if body:
                doc.add_paragraph(body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)


def output_for(input_path: Path, output_arg: str | None) -> Path:
    if output_arg:
        out = Path(output_arg).expanduser()
        return out / (input_path.stem + ".docx") if out.is_dir() else out
    return input_path.with_suffix(".docx")


def main():
    ap = argparse.ArgumentParser(description="Convert Markdown to DOCX locally")
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--batch", action="store_true")
    args = ap.parse_args()
    inp = Path(args.input).expanduser()
    if args.batch:
        out_dir = Path(args.output).expanduser() if args.output else inp
        for md in sorted(inp.glob("*.md")):
            out = out_dir / (md.stem + ".docx")
            convert(md, out)
            print(out)
    else:
        out = output_for(inp, args.output)
        convert(inp, out)
        print(out)


if __name__ == "__main__":
    main()
