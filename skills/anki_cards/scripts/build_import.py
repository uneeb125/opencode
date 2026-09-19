#!/usr/bin/env python3
"""Build an Anki text-import file targeting the "Better Markdown : Cloze" note type.

Reads a directory of per-deck markdown cloze files (see SKILL.md) and writes a
tab-separated .txt with Anki file headers that preset the note type, tags and deck.

Usage
-----
    uv run python build_import.py CARDS_DIR [options]

Options
-------
    --out FILE            output path (default: CARDS_DIR/anki-import.txt)
    --notetype NAME       default "Better Markdown : Cloze"
    --deck-prefix NAME    parent deck, e.g. "CSE 511" -> "CSE 511::01 Processes"
    --tag-prefix NAME     tag root, e.g. "CSE511" -> CSE511::01_process
    --pattern GLOB        which files are card decks (default "[0-9]*.md")

Card-file rules
---------------
  * Optional first line `# <Deck Title>` names the deck (a trailing
    " - Cloze Cards" / "- Cloze Cards" is stripped).
  * `## <Section>` headings become tag sub-levels.
  * Cards are blank-line separated; fenced code blocks are respected, so blank
    lines inside ``` fences do NOT split a card.
  * A blank-line-separated segment that contains no {{cN::...}} (for example a
    code block shown purely as context) is merged into the NEXT cloze-bearing
    card, so context never becomes an invalid cloze-less note.
  * `&`, `<`, `>` are HTML-escaped and newlines become `<br>` (required: Anki
    cloze notes cannot span literal lines). The add-on turns `<br>` back into
    newlines inside code fences.
"""
from __future__ import annotations

import argparse
import glob
import html
import os
import re
import sys


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def parse_file(path: str):
    """Return (deck_title | None, [(segment_text, section), ...])."""
    title = None
    section = "General"
    segs: list[tuple[str, str]] = []
    buf: list[str] = []
    in_code = False

    def flush():
        if buf:
            txt = "\n".join(buf).strip()
            if txt:
                segs.append((txt, section))
        buf.clear()

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.lstrip().startswith("```"):
                in_code = not in_code
                buf.append(line.rstrip())
                continue
            if in_code:
                buf.append(line.rstrip())
                continue
            if not line.strip():
                flush()
                continue
            if line.startswith("## "):
                flush()
                section = line[3:].strip()
                continue
            if line.startswith("# "):
                flush()
                if title is None:
                    title = re.sub(r"\s*[\u2014\u2013-]\s*Cloze Cards\s*$", "", line[2:].strip())
                continue
            buf.append(line.strip())
        flush()
    return title, segs


def cards_from(segs):
    """Merge cloze-less segments into the next card; return [(text, section), ...]."""
    cards: list[tuple[str, str]] = []
    pending: list[str] = []
    for txt, sec in segs:
        if "{{c" in txt:
            cards.append(("\n\n".join(pending + [txt]) if pending else txt, sec))
            pending = []
        else:
            pending.append(txt)
    if pending and cards:
        cards[-1] = (cards[-1][0] + "\n\n" + "\n\n".join(pending), cards[-1][1])
    return cards


def enc(text: str) -> str:
    return html.escape(text, quote=False).replace("\n", "<br>")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build an Anki import file from markdown cloze decks.")
    ap.add_argument("cards_dir")
    ap.add_argument("--out")
    ap.add_argument("--notetype", default="Better Markdown : Cloze")
    ap.add_argument("--deck-prefix", default="")
    ap.add_argument("--tag-prefix", default="Anki")
    ap.add_argument("--pattern", default="[0-9]*.md")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.cards_dir, args.pattern)))
    if not files:
        sys.exit(f"No card files matching {args.pattern!r} in {args.cards_dir}")

    rows: list[str] = []
    for path in files:
        fname = os.path.splitext(os.path.basename(path))[0]
        title, segs = parse_file(path)
        # Deck name: keep any leading "NN" ordering from the filename, then the heading title.
        m = re.match(r"^(\d+)[_\-\s]*(.*)$", fname)
        if m:
            num, rest = m.group(1), m.group(2)
            deck_title = f"{num} {(title or rest.replace('_', ' ').strip())}".strip()
        else:
            deck_title = title or fname.replace("_", " ").strip()
        deck = f"{args.deck_prefix}::{deck_title}" if args.deck_prefix else deck_title
        base_tag = f"{args.tag_prefix}::{slug(fname)}"
        for text, sec in cards_from(segs):
            if "{{c" not in text:
                continue
            tags = f"{base_tag} {base_tag}::{slug(sec)}"
            rows.append("\t".join([enc(text), tags, deck]))

    out = args.out or os.path.join(args.cards_dir, "anki-import.txt")
    header = [
        "#separator:tab",
        "#html:true",
        f"#notetype:{args.notetype}",
        "#tags column:2",
        "#deck column:3",
        "#columns:Text\tTags\tDeck",
    ]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(header) + "\n")
        f.write("\n".join(rows) + "\n")

    decks = {r.split("\t")[2] for r in rows}
    print(f"wrote {out}: {len(rows)} notes across {len(decks)} deck(s)")


if __name__ == "__main__":
    main()
