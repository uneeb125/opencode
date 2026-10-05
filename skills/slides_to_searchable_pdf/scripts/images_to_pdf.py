#!/usr/bin/env python3
"""Assemble slide images into a PDF.

Natural-sorts the inputs (slide-2 before slide-10), optionally crops the same
geometry off every image (e.g. to remove black letterbox bands), and writes a
PDF with a sensible page size.

Examples
--------
    # basic
    python images_to_pdf.py 'slides/slide-*.png' --out deck.pdf

    # remove a letterbox band measured from the browser window
    python images_to_pdf.py 'slides/slide-*.png' --out deck.pdf \
        --crop 1143x643+0+335 --dpi 144
"""
import argparse
import glob
import re
import sys

from PIL import Image


def natural_key(path):
    name = path.rsplit("/", 1)[-1]
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def parse_crop(spec):
    m = re.fullmatch(r"(\d+)x(\d+)\+(\d+)\+(\d+)", spec)
    if not m:
        sys.exit("--crop must look like WxH+X+Y, e.g. 1143x643+0+335")
    w, h, x, y = (int(g) for g in m.groups())
    return w, h, x, y


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", help="image paths or globs, e.g. 'slides/slide-*.png'")
    ap.add_argument("--out", required=True, help="output PDF path")
    ap.add_argument("--crop", default=None, help="WxH+X+Y removed from every image (letterbox trim)")
    ap.add_argument("--dpi", type=float, default=144.0, help="page DPI metadata (default 144)")
    args = ap.parse_args()

    files = []
    for pattern in args.images:
        files.extend(glob.glob(pattern))
    files = sorted({f for f in files if re.search(r"\.(png|jpe?g|webp|gif|bmp|tiff?)$", f, re.I)}, key=natural_key)
    if not files:
        sys.exit(f"no images matched: {args.images}")

    crop = parse_crop(args.crop) if args.crop else None
    pages = []
    for f in files:
        im = Image.open(f).convert("RGB")
        if crop:
            w, h, x, y = crop
            if x + w > im.width or y + h > im.height:
                sys.exit(f"crop {args.crop} does not fit inside {f} ({im.width}x{im.height})")
            im = im.crop((x, y, x + w, y + h))
        pages.append(im)

    pages[0].save(args.out, save_all=True, append_images=pages[1:], resolution=args.dpi)
    print(f"{len(pages)} pages -> {args.out} (page {pages[0].width}x{pages[0].height}px @ {args.dpi}dpi)")


if __name__ == "__main__":
    main()
