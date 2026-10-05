---
name: slides_to_searchable_pdf
description: Turn a view-only slide deck that is open in the browser into a PDF, and add a searchable OCR text layer. Use this whenever the user wants slides, a deck, a presentation, lecture slides, or a class deck saved, downloaded, exported, compiled, archived, or dumped into a PDF — especially a published Google Slides deck (docs.google.com/presentation/d/e/.../pub) that is view-only or where download/export is disabled. Also use when the user wants the slides made searchable, wants the deck turned into a study document or flashcard source, says they cannot download the slides, or when the deck is full of diagrams that must be read visually rather than copied as text. Applies to any browser-rendered paged deck (Google Slides, Canva, SlideShare, Notion, PDF-in-browser, internal viewers), not only Google Slides.
---

# Deck in the browser → searchable PDF

A published / view-only deck cannot be downloaded or exported, so the only way to
get it is to drive the browser and capture it page by page, then compile the pages
into a PDF and OCR them so the result is searchable.

Read this whole file before starting. The capture phase is the part that goes
wrong; the compile and OCR phases are scripted for you.

## When to use

- "compile/export/save these slides as a PDF", "I can't download this deck"
- A Google Slides URL of the form `docs.google.com/presentation/d/e/<ID>/pub?...`
- A deck is view-only, permission-denied for download, or published to the web
- The user wants lecture slides turned into a searchable or studyable PDF

If the deck is a normal (owned) Google Slides file the user can already export,
just say so — File → Download is easier than this whole pipeline.

## Two conditions worth knowing up front

**Published `/pub` decks are rendered as images, not text.** Google's viewer (`punch-viewer`)
draws each slide as SVG vector paths, or as a single raster `<image>` fetched from
`docs.google.com/slides-images-rt/...`. Either way there is no selectable text in the
DOM, so `get_page_text` returns almost nothing and you cannot scrape it. You *must*
look at the slides — capture them as images.

**There is no export endpoint.** `/d/e/<ID>/export/pdf` and `/export/pptx` return 404
for published decks. Don't waste turns on URL tricks. Screen capture is the reliable route.

## Phase 0 — Find the deck and pick a browser

A deck can live in more than one browser surface. Check them all before asking the user:

| Surface | Tools | Notes |
|---|---|---|
| Firefox automation | `tools["firefox-devtools"]` | **Preferred.** Keyboard navigation, `saveTo` paths, full control |
| OpenChamber browser panel | `tools.openchamber_web` | Runs with the user's real logins; `browser.capture` saves a JPEG but has no crop control |
| Desktop browser | `tools.browser.*` | Only if connected; usually the highest-resolution screenshots |

If more than one is live, prefer Firefox: it can drive the deck with the keyboard and
write screenshots straight to disk. Fall back to OpenChamber when the deck needs the
user's authenticated session, or when Firefox is unavailable.

Confirm the deck is what the user means (title, URL) before capturing. A published deck's
title reads like `"<Deck name> - Google Slides"`.

## Phase 1 — Measure before capturing

Two numbers matter: how many slides, and the rectangle the slide occupies on screen.

**Slide count and current position** — the viewer kept the count in the page control:

```js
() => JSON.stringify({
  current: (document.querySelector('.punch-viewer-navbar-page') || {}).textContent,
  totalHint: (document.querySelector('[alt^="Slide "]') || {}).alt   // e.g. "Slide 1 of 22"
})
```

`"Slide N of M"` gives the total directly. If it is absent, step to the end and read the
counter, or open the slide picker in the navbar.

**Slide rectangle** — measure it, because the slide is letterboxed inside the window and
the crop geometry depends on the actual window size (which you often cannot change):

```js
() => {
  const el = document.querySelector('.punch-viewer-page-wrapper');
  const r = el.getBoundingClientRect();
  return JSON.stringify({
    window: `${innerWidth}x${innerHeight}`,
    crop: `${Math.round(r.width)}x${Math.round(r.height)}+${Math.round(r.x)}+${Math.round(r.y)}`
  });
}
```

That `crop` value (`WxH+X+Y`) is exactly what Phase 3 needs. In one real 22-slide run the
window was `1143x1313` and the slide occupied `1143x643+0+335` — i.e. 335px of black
letterbox above and below.

Do **not** assume you can enlarge the window first: Firefox's `set_viewport_size` may
report success without actually resizing the real window. Measure, don't assume, and
accept the resolution you get.

## Phase 2 — Capture every slide, in order

The critical discipline: **verify the slide counter against the filename on every step.**
That is what guarantees the PDF pages are in the right order.

Firefox recipe:

```
1. press_key({ key: "Home" })                       # jump to slide 1
2. for n = 1..N:
     read the counter  (must equal n)
     screenshot_page({ saveTo: `slides/raw-${String(n).padStart(2,"0")}.png` })
     press_key({ key: "ArrowRight" })               # omit after the last slide
```

Notes that save time:

- `saveTo` paths resolve against the **current working directory**. Keep them inside it,
  e.g. `slides/raw-01.png`. Downloads, by contrast, are restricted to the MCP output
  folder — screenshots are the right mechanism here.
- Do **3–5 slides per tool-code block**. Bigger batches risk long, fragile round trips.
- If the counter and the filename ever disagree, stop and resync (press `Home`, recount)
  rather than capturing a misaligned page.
- Dismiss anything covering the slide first (cookie banners, ad interstitials — a
  `#google_vignette` fragment in the URL is a common one). A Cloudflare "Just a moment…"
  page usually clears itself; re-snapshot before declaring it blocked.

OpenChamber alternative: `browser.open` the deck, then `browser.snapshot` to get the
navbar button selectors (`div.punch-viewer-navbar-next`), `browser.click` to advance, and
`browser.capture` per slide. Remember its captures land in `.openchamber/screenshots/`
and are viewport-only, so you still need the measured crop.

## Phase 3 — Crop and build the PDF

Strip the letterbox and assemble. `scripts/images_to_pdf.py` natural-sorts the pages
(so `slide-2` comes before `slide-10`), applies the crop, and writes the PDF:

```bash
python scripts/images_to_pdf.py 'slides/slide-*.png' \
    --out Deck.pdf --crop 1143x643+0+335 --dpi 144
```

If you prefer to crop separately first, ImageMagick works:

```bash
for f in slides/raw-*.png; do n=${f#slides/raw-}; n=${n%.png}; \
  magick "$f" -crop 1143x643+0+335 +repage "slides/slide-$n.png"; done
```

`--dpi` only sets the PDF page *size* metadata (page inches = pixels / dpi); it does not
add detail. 144 dpi keeps a normal 16:9 page and reads well.

## Phase 4 — Add the OCR text layer

`scripts/ocr_layer.py` wraps ocrmypdf's sandwich renderer: the page images stay exactly
as they are, and an invisible text layer is laid over them. Run it with its dependencies
supplied on the fly:

```bash
uv run --with ocrmypdf --with pypdf python scripts/ocr_layer.py Deck.pdf Deck-searchable.pdf
```

**Dense screenshot slides need special handling.** A slide that is a full-page screenshot
of a dense web page (the MITRE ATT&CK / D3FEND matrices are the classic case) has glyphs
only a few pixels tall and OCRs into noise. Test for this:

```bash
pdftotext -layout Deck-searchable.pdf - | grep -i "some term you expect on that slide"
```

If a page's text is garbled, identify it and re-run with those pages oversampled — the
script OCRs them again at higher resolution and splices only those pages back in:

```bash
uv run --with ocrmypdf --with pypdf python scripts/ocr_layer.py Deck.pdf Deck-searchable.pdf \
    --dense-pages 21,22 --oversample 400
```

Upscaling genuinely helps: on one ATT&CK slide it lifted recognized words from ~339 to
~558 and recovered tactic names like *Reconnaissance*, *Exfiltration*, *Credential*.

## Phase 5 — Verify and hand over

Always verify rather than assume:

```bash
pdftotext -layout Deck-searchable.pdf /tmp/check.txt
grep -c $'\f' /tmp/check.txt          # page count must match the slide count
grep -i "NEAT\|least privilege" /tmp/check.txt   # a couple of distinctive terms
```

Open the result for the user (`tools.openchamber` → `file.open`, or `browser.preview` if
the desktop browser is connected) and report:

- the page count and file path,
- that the text layer is **for search and copy, not typesetting** — the pages remain images,
- which pages OCR'd poorly, if any, and that the fix is higher-resolution source images.

## Gotchas worth remembering

- **Don't try to scrape the deck's image URLs.** The published HTML embeds only a partial,
  unordered subset of `slides-images-rt` URLs (16 of 22 in one real deck), and the
  per-slide URLs are opaque hashes. Screen capture is the reliable path. A single slide's
  `<image href>` can be read live and fetched at `=s2048` for that one page, but do not
  build the whole deck that way.
- **Code Mode `fetch` cannot do binary.** Its response has no `arrayBuffer`, and
  `getPrototypeOf` is unavailable. For anything binary, work *in the page* via
  `evaluate_script` (the browser realm is fully featured), not in Code Mode.
- **OCR slips are normal.** `ATT&CK` can OCR as `ATTECK`. Tell the user to search
  distinctive words, not generic ones.
- **The text layer cannot fix a low-resolution image.** If the user needs legible dense
  diagrams, the real fix is a higher-resolution capture — which usually means connecting
  the desktop browser, or fetching that slide's `=s2048` image.

## Generic fallback (non-Google decks)

The same five phases work for any browser-rendered deck — Canva, SlideShare, Notion export
views, PDF-in-browser, internal viewers. Only Phase 1 and Phase 2 change:

1. **Find the paging control.** Snapshot the page and look for next/prev controls, or try
   `ArrowRight` / `PageDown` / `Space`. Read whatever element shows the page number so you
   can keep the same counter-verification discipline.
2. **Measure the content rectangle** the same way (`getBoundingClientRect()` on the element
   that holds the page), then reuse Phase 3–5 unchanged.

Everything else — natural-sorted assembly, letterbox crop, OCR with dense-page
oversampling, verification — is identical.

## Requirements

- `python3` with Pillow (for `images_to_pdf.py`); `uv` to supply ocrmypdf + pypdf on demand
- `tesseract` (with the language pack you need), `ghostscript`, `pdfunite`, `pdftotext`
- Optional: ImageMagick (`magick`) for standalone cropping
