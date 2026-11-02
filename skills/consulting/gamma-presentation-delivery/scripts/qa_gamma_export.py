#!/usr/bin/env python3
"""Deterministic QA for a Gamma-exported PPTX, with optional PDF and prior-version checks."""
import argparse
import json
import re
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def walk(shapes):
    for shape in shapes:
        yield shape
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(shape.shapes)


def extract(path):
    prs = Presentation(str(path))
    slides = []
    bounds = []
    for index, slide in enumerate(prs.slides, 1):
        text, sizes = [], []
        for shape in walk(slide.shapes):
            if getattr(shape, "has_text_frame", False):
                for paragraph in shape.text_frame.paragraphs:
                    value = "".join(run.text for run in paragraph.runs).strip()
                    if value:
                        text.append(value)
                    for run in paragraph.runs:
                        if run.font.size is not None:
                            sizes.append(round(run.font.size.pt, 2))
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0 or shape.left + shape.width > prs.slide_width or shape.top + shape.height > prs.slide_height:
                bounds.append({"slide": index, "shape": shape.name})
        joined = "\n".join(text)
        slides.append({
            "slide": index,
            "text": joined,
            "words": len(re.findall(r"[A-Za-zА-Яа-яЁё0-9·/–-]+", joined)),
            "minExplicitFontPt": min(sizes) if sizes else None,
            "maxExplicitFontPt": max(sizes) if sizes else None,
        })
    return prs, slides, bounds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--slides", type=int)
    parser.add_argument("--prior", type=Path)
    parser.add_argument("--changed", default="", help="Comma-separated slide numbers allowed to change")
    parser.add_argument("--must", action="append", default=[], help="Literal required in the combined text; repeatable")
    parser.add_argument("--forbid", action="append", default=[], help="Regex forbidden in combined text; repeatable")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    prs, slides, bounds = extract(args.pptx)
    combined = "\n\n".join(x["text"] for x in slides)
    failures = []
    if args.slides is not None and len(slides) != args.slides:
        failures.append(f"slide_count={len(slides)} expected={args.slides}")
    ratio = prs.slide_width / prs.slide_height
    if abs(ratio - 16 / 9) > 0.01:
        failures.append(f"ratio={ratio:.4f} expected=1.7778")
    if bounds:
        failures.append(f"out_of_bounds={bounds}")
    missing = [x for x in args.must if x.lower() not in combined.lower()]
    if missing:
        failures.append(f"missing={missing}")
    forbidden = {pattern: re.findall(pattern, combined, re.I) for pattern in args.forbid}
    forbidden = {k: v for k, v in forbidden.items() if v}
    if forbidden:
        failures.append(f"forbidden={forbidden}")

    changed_actual = []
    if args.prior:
        _, prior, _ = extract(args.prior)
        if len(prior) != len(slides):
            failures.append("prior_slide_count_differs")
        else:
            changed_actual = [i + 1 for i, (a, b) in enumerate(zip(prior, slides)) if a["text"] != b["text"]]
            allowed = {int(x) for x in args.changed.split(",") if x.strip()}
            collateral = sorted(set(changed_actual) - allowed)
            if collateral:
                failures.append(f"collateral_changes={collateral}")

    pdf_pages = None
    if args.pdf:
        try:
            import fitz
            pdf_pages = len(fitz.open(args.pdf))
            if pdf_pages != len(slides):
                failures.append(f"pdf_pages={pdf_pages} pptx_slides={len(slides)}")
        except ImportError:
            failures.append("pymupdf_not_installed")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "pptx": str(args.pptx),
        "slideCount": len(slides),
        "pdfPages": pdf_pages,
        "ratio": round(ratio, 4),
        "wordCounts": [x["words"] for x in slides],
        "minimumExplicitFontPt": min((x["minExplicitFontPt"] for x in slides if x["minExplicitFontPt"] is not None), default=None),
        "outOfBounds": bounds,
        "changedSlides": changed_actual,
        "failures": failures,
        "slides": slides,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json:
        args.json.write_text(output, encoding="utf-8")
    print(output)
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
