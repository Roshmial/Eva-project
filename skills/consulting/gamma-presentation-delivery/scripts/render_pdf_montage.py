#!/usr/bin/env python3
"""Render a PDF deck to individual PNG pages and a contact sheet."""
import argparse
import math
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--scale", type=float, default=1.6)
    parser.add_argument("--columns", type=int, default=3)
    args = parser.parse_args()

    output = args.output_dir or args.pdf.with_name(args.pdf.stem + "_render")
    output.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.pdf)
    pages = []
    for index, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), alpha=False)
        path = output / f"slide-{index:02d}.png"
        pix.save(path)
        pages.append(path)

    thumb_w, thumb_h, label_h = 480, 270, 28
    rows = math.ceil(len(pages) / args.columns)
    sheet = Image.new("RGB", (args.columns * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(pages, 1):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = ((index - 1) % args.columns) * thumb_w + (thumb_w - image.width) // 2
        y = ((index - 1) // args.columns) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.text((x + 8, y + thumb_h + 4), f"Slide {index}", fill="black")
    montage = output / "montage.png"
    sheet.save(montage)
    print(montage)


if __name__ == "__main__":
    main()
