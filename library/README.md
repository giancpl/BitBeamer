# Studio presentation library

This collection contains editable English Studio presentations and topic blocks,
including official BitPolito lessons and supplied drafts. It is separate from neutral layout examples and ignored
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

Imports copy editable content, data and references into the personal project.
Canonical layouts and shared artwork stay linked to this checkout: a graphical
correction reaches every linked deck on its next build without replacing its
personal text. Imports never edit library sources or overwrite existing projects.
Read the private brief and provenance notes, adapt speaker details and inspect
every page before presenting. Older snapshot imports require explicit migration;
see [maintenance](MAINTENANCE.md#legacy-personal-projects).

The catalogue preserves source order and composition. English translation, Inter
and verified content updates are documented separately. Source PDFs are pinned to
an upstream revision and remain local references; no original PDF download,
conversion or OCR runs during ordinary authoring. Complex artwork retains prepared
vector parts; text and simple diagrams remain editable LaTeX/TikZ.

Use the [authoring guide](../docs/AUTHORING.md) for private project paths and checks.
The lesson collection is for clones; it is not included in the main Overleaf ZIP.

## Edit and combine

After copying a lesson, edit `presentations/my-talk/slides/*.tex`. Each source
contains a `\studiotemplate` call with its actual content fields.
`library-layouts.tex` points to canonical sources under `library/layouts/`;
it does not contain independent layout copies. Shared panels, icons and prepared
parts also stay in the library. Use the project's `assets/` for your own images.

New projects contain this marker before their closing page:

```latex
% BITBEAMER: INSERT BLOCKS HERE
```

`add --block` inserts only the content slides at that marker and merges required
references. It adds no cover, team, agenda or closing. For an older project, add
one marker manually. Repeated blocks, repeated slides, edited layout registrations,
conflicting assets and bibliography keys cause a clear error before any file is
changed. To repeat a slide deliberately, reuse the existing personal input yourself.

Inspect `library-imports.json` and `brief.md` for provenance, review status and
source-period data. Citations use namespaced `lesson-*` keys. Add your own verified
references to `references.bib`; keep citation keys distinct. Do not treat historical
product screenshots, prices, legal statements or energy estimates as current facts.

## Browse and verify

Use [the unified slide guide](../docs/slides/index.html) for each template with its
preview and command. Select [Presentations or Reusable blocks](../docs/slides/index.html?view=decks) for presentations and blocks. It loads only the current page of previews. The [text catalogue](CATALOGUE.md)
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

## One catalogue, three kinds of reuse

- **Templates** expose documented fields while keeping fixed visual geometry.
- **Fixed slides** expose no content or palette options; their native source remains maintainable.
- **Presentations and blocks** contain ordered calls to catalogue entries, never private layouts.

The guide separates **Ready** from **In review**. Ready requires explicit approval
of both the pack and all its slides. A passing build never grants approval.
The supplied introduction is available as `bitpolito-introduction`, with
`bitpolito-mission` and `bitpolito-opportunities` content blocks:

```sh
python3 scripts/deck.py new my-team-talk --from bitpolito-introduction
python3 scripts/deck.py add my-talk --block bitpolito-mission
```

The supplied figures, partner list and links are draft content, not verified current claims.
