#!/usr/bin/env python3
"""Add a searchable OCR text layer to an image-only PDF, keeping the original images.

Uses ocrmypdf's "sandwich" renderer, so the page images you already have are left
intact and only an invisible text layer is added.

Dense screenshot slides (e.g. a full-page screenshot of the MITRE ATT&CK matrix)
are drawn at a few pixels per glyph and OCR badly. For those pages this script pulls
them into their own sub-PDF, re-OCRs that at higher oversampling, and splices the
improved pages back in, so the rest of the document is untouched.

Run it with the dependencies available, e.g.:
    uv run --with ocrmypdf --with pypdf python ocr_layer.py in.pdf out.pdf
    uv run --with ocrmypdf --with pypdf python ocr_layer.py in.pdf out.pdf \
        --dense-pages 21,22 --oversample 400
"""
import argparse
import os
import sys
import tempfile


def run_ocr(inp, out, lang, jobs, oversample=None):
    import ocrmypdf

    kwargs = dict(language=lang, output_type="pdf", optimize=1, jobs=jobs)
    if oversample:
        kwargs["oversample"] = oversample
    ocrmypdf.ocr(inp, out, **kwargs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--lang", default="eng", help="tesseract language code (default eng)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument(
        "--dense-pages",
        default="",
        help="comma-separated 1-based pages of dense screenshots to re-OCR with oversampling",
    )
    ap.add_argument("--oversample", type=int, default=400, help="DPI used for dense pages (default 400)")
    args = ap.parse_args()

    try:
        import ocrmypdf  # noqa: F401
        from pypdf import PdfReader, PdfWriter  # noqa: F401
    except ImportError as e:
        sys.exit(f"missing dependency ({e}). Run me via:\n"
                 f"  uv run --with ocrmypdf --with pypdf python {os.path.basename(__file__)} ...")

    from pypdf import PdfReader, PdfWriter

    dense = sorted({int(p) for p in args.dense_pages.replace(" ", "").split(",") if p})
    reader = PdfReader(args.input)
    total = len(reader.pages)

    if not dense:
        run_ocr(args.input, args.output, args.lang, args.jobs)
        print(f"OCR'd {total} pages -> {args.output}")
        return

    out_of_range = [p for p in dense if p < 1 or p > total]
    if out_of_range:
        sys.exit(f"--dense-pages out of range 1..{total}: {out_of_range}")

    with tempfile.TemporaryDirectory() as tmp:
        normal = os.path.join(tmp, "normal.pdf")
        dense_in = os.path.join(tmp, "dense-in.pdf")
        dense_out = os.path.join(tmp, "dense-out.pdf")

        # Full document, normal resolution.
        run_ocr(args.input, normal, args.lang, args.jobs)

        # Just the dense pages, oversampled. Extracting them into their own file
        # keeps the oversampling scoped to those pages.
        dw = PdfWriter()
        for p in dense:
            dw.add_page(reader.pages[p - 1])
        with open(dense_in, "wb") as fh:
            dw.write(fh)
        run_ocr(dense_in, dense_out, args.lang, args.jobs, oversample=args.oversample)

        # Non-dense pages come from the normal pass; dense pages from the oversampled pass.
        normal_reader, dense_reader = PdfReader(normal), PdfReader(dense_out)
        if len(dense_reader.pages) != len(dense):
            sys.exit(f"expected {len(dense)} dense pages, got {len(dense_reader.pages)}")

        writer = PdfWriter()
        dense_slot = {page: i for i, page in enumerate(dense)}
        for i in range(total):
            if (i + 1) in dense_slot:
                writer.add_page(dense_reader.pages[dense_slot[i + 1]])
            else:
                writer.add_page(normal_reader.pages[i])
        with open(args.output, "wb") as fh:
            writer.write(fh)

    print(f"OCR'd {total} pages ({len(dense)} dense re-OCR'd @ {args.oversample}dpi) -> {args.output}")


if __name__ == "__main__":
    main()
