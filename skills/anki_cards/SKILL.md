---
name: anki_cards
description: Build Anki cloze-deletion flashcards (markdown + KaTeX + code) and import them into Anki via the Better Markdown Anki add-on. Use when the user wants to create, generate, convert, or import Anki cards / flashcards / spaced-repetition decks, make cloze deletions, or turn lecture notes, slides, PDFs, or a vault of notes into Anki cards.
---

# Skill: Anki cloze cards (Better Markdown Anki)

End-to-end recipe for turning notes/slides into Anki cloze cards that import cleanly
into the **Better Markdown Anki** add-on (https://ankiweb.net/shared/info/2100166052).
Follow this instead of rediscovering the format each time.

## The one hard rule

**Never ship a `.apkg` to target the add-on's note type.** Anki matches note types by
**ID, not name**. The add-on's note type gets a random ID, so any `.apkg` you generate
creates a *duplicate* note type (Anki renames it with a `+` suffix). Always import via a
**text file with file headers**, which lets Anki target the exact existing note type.

## Target format

- **Note type name:** `Better Markdown : Cloze` (exactly — spaces around the colon)
- **Fields:** `Text`, `Back Extra`, `Difficulty` (order matters)
- **Type:** Cloze
- Rendered by the add-on: markdown, KaTeX (`$...$`, `$$...$$`), syntax-highlighted
  fenced code, and clozes whose content keeps its formatting (code/math inside a cloze).
- `Back Extra` / `Difficulty` may be left empty.

## Workflow

### 1. Get the content
- If the source is PDF slides: render pages to images and read them **one image per
  read call** (vision fails with multiple images in one call):
  ```bash
  pdftoppm -png -r 200 deck.pdf /tmp/cards/deck/page
  ```
  Analyze and write a per-deck markdown note first (the `vision_pdf` skill covers this).
- If the source is already notes/markdown, skip to step 2.

### 2. Author cards — one markdown file per deck
Put them in a cards directory (e.g. `anki/`), named `01_topic.md`, `02_topic.md`, …
Card file rules (also see `scripts/build_import.py` docstring):

- First line: `# <Deck Title> — Cloze Cards`
- One card = **one markdown paragraph** (blank line between cards).
- Cloze syntax: `{{c1::...}}`, `{{c2::...}}`, 1–4 per card. Each cloze tests one
  unambiguous fact. Never nest clozes; never put cloze markers in a heading.
- Lead with the term in `**bold**` where natural. Use `$...$` for math and `` `code` ``
  inline. Put multi-line code in fenced blocks with a language tag (```c, ```text).
- **Cloze inside code/math is supported by the add-on**, but the safe default is:
  show the code as visible context and cloze the answer in prose or inline code, e.g.
  `... the atomic instruction {{c1::`lock xchg`}} ...`
- Group cards under `## <Section>` headings (they become tag sub-levels).
- Include a `## Code & Pseudocode` section when the material has code.
- Target ~15–20 cards per deck. Ground every card in the source; never invent facts.

Example card:
```
**Bias** is the error from a model's {{c1::simplifying assumptions}}, leading to {{c2::underfitting}}. It measures how far the average prediction is from the true value.
```

If there are many decks, delegate one deck per subagent (each reads its source note and
writes its card file) — this parallelizes well.

### 3. Build the import file
```bash
uv run python ~/.config/opencode/skills/anki_cards/scripts/build_import.py <cards_dir> \
  --deck-prefix "CSE 511" --tag-prefix CSE511 --out <cards_dir>/anki-import.txt
```
This emits a tab-separated file whose headers preset everything:
```
#separator:tab
#html:true
#notetype:Better Markdown : Cloze
#tags column:2
#deck column:3
#columns:Text	Tags	Deck
```
It escapes `& < >` and stores newlines as `<br>` (Anki cloze notes cannot span literal
lines; the add-on converts `<br>` back to newlines inside code fences).

### 4. Import in Anki
**File → Import…** → select the `.txt`. In the preview confirm the note type is exactly
`Better Markdown : Cloze`, `Text` ← column 1, and the deck column is applied, then import.
File headers require Anki **2.1.54+**; if the note type isn't auto-selected, pick it manually.

## Troubleshooting

- **Note type shows a `+` suffix / duplicate created:** you imported a `.apkg`. Delete the
  duplicate via **Tools → Manage Note Types** (confirm deleting its cards), then import the `.txt`.
- **Cards render literally (`**bold**`, `$x$`):** the Better Markdown add-on isn't installed/enabled.
- **Code blocks lose their line breaks:** the field must use `<br>` (this script does).
- **`<` disappears from a formula:** escape it as `&lt;` (this script does).
- **Duplicates on re-import:** text imports dedupe on the first field; use the import dialog's
  *update existing notes* option.

## Files

- `scripts/build_import.py` — the converter described above.
