# Writing cards worth studying

The script only packs cards; quality comes from how you write them. Aim for cards that build
understanding, not cards that test whether the reader can fill in an arbitrary word.

## Card shape

One card is **one markdown paragraph**. Start with the term in `**bold**` when it reads
naturally, then a precise statement containing 1–4 clozes `{{c1::…}}`, `{{c2::…}}`.

```
**Bias** is the error from a model's {{c1::simplifying assumptions}}, leading to {{c2::underfitting}}. It measures how far the average prediction is from the true value.
```

Guidelines:

- **One fact per cloze.** If a cloze hides two independent ideas, split the card.
- **Make the cloze the testable part**, not filler words. Hide a mechanism, a reason, a value,
  a name that matters — never "the" or "process".
- **Self-contained.** No "this slide", "above", or "the diagram". A card read in isolation
  next month must still make sense.
- **Prefer understanding over recall.** Where you can, cloze the *why* or the consequence
  ("…because it guarantees {{c1::strict ordering on the same process}}") rather than only a term.
- **Number clozes c1, c2, … within a card** and never nest them or put them in a heading.
- Group cards under `## Section` headings; the heading becomes a tag level.

## Deriving cards from diagrams

Diagrams carry the mechanism, so don't reduce them to labels. Describe the dynamics — what
happens over time, which element changes, what causes the next step — and cloze the moving
parts:

```
In the context-switch diagram, the crossing control-flow curves mean the return from
`Context_switch()` resumes {{c1::a different process}} than the one that called it; each
process needs its own {{c2::stack}} to hold its saved registers and {{c3::return address}}.
```

## Code and math

The add-on highlights fenced code and renders KaTeX. The safest card puts the code as visible
context and clozes the answer in prose or inline code:

```
In `Context_switch()`, the `push` must come **before** `PCB[curr].SP = SP`, otherwise the later
`pop` reads {{c1::garbage}}.
```

Clozes *inside* code/math are supported by the add-on, but only use that when it genuinely
reads better — code-as-context is more robust. Tag fences with a language (```c, ```text, ```asm).
Use `$...$` for math, and write `&lt;`/`&gt;`/`&amp;` for `<`/`>`/`&` (the script does this for you).

## Coverage and volume

- Cover every source slide/section: definitions, mechanisms, algorithms, formulas, diagram
  concepts, conventions, and pitfalls.
- Target **~15–20 cards per deck** (~45–70 clozes) for balanced coverage; scale up for
  exam-prep decks if asked.
- When a single idea spans several slides, write one card for the group and say so in a
  `## Slides N–M — <theme>` heading.
- Include a `## Code & Pseudocode` section whenever the material has code.

## Anti-patterns

- Cloze that hides a word the sentence doesn't actually test.
- Two questions crammed into one cloze.
- Cards that depend on a figure the reader can't see.
- Copying a bullet list verbatim with one cloze per bullet and no reasoning.
- Inventing facts not present in the source — if a diagram is ambiguous, write what is
  defensible and say so, rather than guessing.
