---
name: anki_cards
description: Build Anki cloze-deletion flashcards from notes, slides, or PDFs and import them into Anki through the Better Markdown Anki add-on (markdown + KaTeX + syntax-highlighted code). Use this whenever the user wants to make, generate, convert, or import Anki cards / flashcards / a spaced-repetition deck; turn lecture notes, slides, a PDF, or a notes vault into Anki cards; write cloze deletions; fix or re-import an Anki deck; or asks why their cards won't import. If the user is studying for an exam and has material, reach for this even when they don't say "Anki".
---

# Anki cloze cards (Better Markdown Anki)

Turn source material into Anki cloze cards that import cleanly into the **Better Markdown
Anki** add-on (https://ankiweb.net/shared/info/2100166052). The add-on renders markdown,
KaTeX (`$...$`, `$$...$$`), and syntax-highlighted code, and supports clozes whose content
keeps its formatting (code/math inside a cloze).

## Why the import path matters (read first)

Anki matches note types by **ID, not name**. The add-on creates its note type with a random
ID, so a `.apkg` you generate will *never* attach to it — Anki silently makes a duplicate
note type (renamed with a `+` suffix). That is the single most common way this task goes
wrong, so don't reach for `genanki`/`.apkg` at all.

The reliable path is a **text import file with file headers**. Anki's text importer lets you
target the existing note type by name and set the note's fields, tags, and deck per row. The
whole workflow builds toward that one file.

## Target format

- Note type: `Better Markdown : Cloze` (exact spacing around the colon)
- Fields: `Text`, `Back Extra`, `Difficulty` (order matters)
- Type: Cloze; `Back Extra` / `Difficulty` may be left empty.

## Fast path — you already have markdown notes

1. Write one markdown card file per deck in a cards directory, named `01_topic.md`, `02_topic.md`, …
   (authoring rules: `references/card-authoring.md`).
2. Build the import file:
   ```bash
   uv run python scripts/build_import.py <cards_dir> \
     --deck-prefix "CSE 511" --tag-prefix CSE511 --out <cards_dir>/anki-import.txt
   ```
3. In Anki: **File → Import…** → the `.txt`. In the preview confirm note type
   `Better Markdown : Cloze`, `Text` ← column 1, tags ← column 2, deck ← column 3, then import.

`scripts/build_import.py` is deterministic — the intelligence is in the card files, so spend
your effort there.

## Full path — source is slides / PDFs

1. **Extract content.** For PDF slides, render pages and read them **one image per read call**
   (vision fails when several images are sent together):
   ```bash
   pdftoppm -png -r 200 deck.pdf /tmp/cards/deck/page
   ```
   For decks that only exist in a browser, or for richer PDF handling, prefer the dedicated
   `pdf`, `pptx`, or `slides_to_searchable_pdf` skill.
2. **Write per-deck study notes** (the `vision_pdf` skill covers the diagram-heavy reading).
   Keep code verbatim and interpret diagrams — cards will be built from these notes.
3. **Author card files** from the notes (`references/card-authoring.md`). With many decks,
   delegate one deck per subagent: each reads its note and writes its card file, which
   parallelizes cleanly.
4. **Build and import** as in the fast path.

## The import file (what the script emits)

Tab-separated, one note per line, with headers that preset everything:

```
#separator:tab
#html:true
#notetype:Better Markdown : Cloze
#tags column:2
#deck column:3
#columns:Text	Tags	Deck
```

Two encoding choices in the script exist for concrete reasons, so keep them:

- **`<br>` for newlines** — an Anki cloze note cannot contain literal line breaks, so the
  script joins lines with `<br>` and sets `#html:true`. The add-on converts `<br>` back to
  newlines inside code fences, so multi-line code survives.
- **`&`/`<`/`>` escaped** as `&amp;`/`&lt;`/`&gt;` — otherwise Anki's HTML parser can swallow
  a stray `<` such as the one in `C(a) < C(b)`. The add-on decodes entities on render.

The script also merges a blank-line-separated segment that has no `{{cN::…}}` (for example a
code block shown as context) into the next cloze-bearing card, so a code snippet never becomes
an invalid cloze-less note. Headings become decks/sections: `# Title` names the deck,
`## Section` becomes a tag level.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Note type shows a `+` suffix, or a duplicate appears | A `.apkg` was imported. Delete the duplicate in **Tools → Manage Note Types** (confirm deleting its cards), then import the `.txt`. |
| Cards show `**bold**` / `$x$` literally | The Better Markdown add-on isn't installed/enabled. |
| Code blocks collapse to one line | Newlines weren't stored as `<br>` (see above). |
| A `<` vanishes from a formula | It wasn't escaped as `&lt;`. |
| Note type not auto-selected on import | File headers need Anki **2.1.54+**; pick `Better Markdown : Cloze` manually in the dialog. |
| Duplicates on re-import | Text imports dedupe on the first field; choose *update existing notes* in the dialog. |

## Files

- `scripts/build_import.py` — markdown card files → Anki import file (the only executable step).
- `references/card-authoring.md` — how to write cards worth studying (read before authoring).
- `evals/evals.json` — sample prompts for testing this skill.
