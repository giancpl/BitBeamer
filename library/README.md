# Official lesson library

This collection reconstructs the official BitPolito presentations as editable
English Studio lessons. It is separate from neutral layout examples and ignored
personal projects. Every slide, topic block and complete deck remains in review.
Browse [Presentations and Reusable blocks in the slide guide](../docs/slides/index.html?view=decks).

```sh
python3 scripts/deck.py library
python3 scripts/deck.py library --deck bitcoin-introduction-short --json
python3 scripts/deck.py library --block hashing --json
python3 scripts/deck.py new my-talk --from bitcoin-introduction-short
python3 scripts/deck.py add my-talk --block hashing
python3 scripts/deck.py check my-talk --preview
```

Imports copy the required content, artwork and references into the personal project.
They never edit library sources or overwrite existing projects. New imports use
the current corrected templates; existing personal copies preserve their own
content and layout snapshots. Themes, Inter and shared icons remain common. Read the private brief and provenance notes, adapt the
speaker details and inspect every page before presenting.

The catalogue preserves source order and composition. English translation, Inter
and verified content updates are documented separately. Source PDFs are pinned to
an upstream revision and remain local references; no original PDF download,
conversion or OCR runs during ordinary authoring. Complex artwork retains prepared
vector parts; text and simple diagrams remain editable LaTeX/TikZ.

Use the [authoring guide](../docs/AUTHORING.md) for private project paths and checks.
The lesson collection is for clones; it is not included in the main Overleaf ZIP.

## Edit and combine

After copying a lesson, edit `presentations/my-talk/slides/*.tex`. Each source
contains a `\studiotemplate` call with the actual content fields. Its copied layout
in `layouts/` fixes the positions, font sizes and proportions; normal changes belong
in the slide content, not the shared library. Required prepared art is in the
private `assets/` folder. The local `library-layouts.tex` registers copied layouts.

New projects contain this marker before their closing page:

```latex
% BITBEAMER: INSERT BLOCKS HERE
```

`add --block` inserts only the content slides at that marker and merges required
references. It adds no cover, team, agenda or closing. For an older project, add
one marker manually. Repeated blocks, repeated slides, changed copied layouts,
conflicting assets and bibliography keys cause a clear error before any file is
changed. To repeat a slide deliberately, reuse the existing personal input yourself.

Inspect `library-imports.json` and `brief.md` for provenance, review status and
source-period data. Citations use namespaced `lesson-*` keys. Add your own verified
references to `references.bib`; keep citation keys distinct. Do not treat historical
product screenshots, prices, legal statements or energy estimates as current facts.

## Browse and verify

Use [the unified slide guide](../docs/slides/index.html) for each template with its
preview and command. Open [the lesson gallery](index.html) for presentations and blocks. It loads only the current page of previews. The [text catalogue](CATALOGUE.md)
works without JavaScript. Use `layouts --model official-layout-<id> --json` to inspect
a measured lesson layout; load `bitpolitostudiolibrary` when using these optional
models directly. Core Studio models remain available unchanged.

```sh
python3 scripts/library.py build --deck bitcoin-introduction-short --preview
python3 scripts/library.py build --block hashing --preview
python3 scripts/library.py check
```

PDFs and reports appear in `build/library/decks/<id>/` or `build/library/blocks/<id>/`.
Previews are retained in this catalogue; original PDF references and comparisons
remain ignored local files. See [maintenance](MAINTENANCE.md) for explicit downloads,
artwork regeneration, full-collection checks and editorial review. None of these
commands replaces stable template release artifacts.

[Source-page coverage](COVERAGE.md) · [Verification and review limits](CHECKS.md)

## Fixed-content slides

Use a [ready-made fixed slide](FIXED.md) when its content should stay unchanged:

```latex
\usepackage{bitpolitostudiolibrary} % after selecting the Studio theme
% Inside the document:
\studiotemplate{bitcoin-supply}
```

Fixed presets accept no text, icon or palette options. They reuse the existing
LaTeX/vector composition rather than embedding a screenshot. Their editable source
layouts remain available for maintenance and intentional adaptations. The gallery
has a **Fixed-content slides** view; all presets remain in review.

The `problem-solution` layout has two interchangeable icon slots and shared soft
panels, matching the existing `three-cards` component. Use `title-one`, `title-two`,
`caption-one`, `caption-two`, `graphic-one` and `graphic-two`. Both captions are
centred paragraphs; use `\\` for an intentional line break.
Quotation slides use the existing `chat-dialogue` template: `title` is the whole
quotation and `text-2` is the credit. Do not position each quoted line independently.

```latex
\studiotemplate[
  title-one={Problem}, title-two={Solution},
  caption-one={Describe the challenge},
  caption-two={Describe the response},
  graphic-one={\alice[height=0.9cm]},
  graphic-two={\cow[height=0.9cm]}
]{problem-solution}
```
