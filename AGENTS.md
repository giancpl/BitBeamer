# Creating presentations in BitBeamer

Read [docs/AUTHORING.md](docs/AUTHORING.md) before creating or editing a deck.
Studio is the default; use Academic only when requested. These instructions apply
to the whole repository. A specific request to maintain the library may change
shared files; ordinary presentation authoring must not.

## Work within one presentation

- Create a project with `python3 scripts/deck.py new <kebab-case-name>`.
- Work only in `presentations/<name>/` and its `build/presentations/<name>/`
  outputs. Personal decks are ignored by Git. Do not inspect or modify another
  personal deck unless the user asks. Use explicit paths when searching ignored files.
- Read and complete `brief.md`: goal, audience, duration, language, metadata,
  sources, outline, assumptions and verification. Ask only for essential missing
  information. Proceed without requiring approval of an outline.
- Use English unless the brief explicitly requests another language. All library
  documentation, comments and official examples must remain in English.

## Reuse lessons before designing new content

- Search `python3 scripts/deck.py library` for relevant lessons and topic blocks.
  Inspect `library --deck <id> --json` or `library --block <id> --json`.
- Copy a lesson with `new <name> --from <id>` or insert a block with
  `add <name> --block <id>`. Edit the copied content, never shared lesson files or canonical layouts.
- Read provenance, historical dates, translation and update notes. All lessons
  remain in review until explicitly approved: a successful build is not approval.
  Prefer Ready entries where available; record the use of in-review content in the brief.
- The source lesson sequence takes priority over the generic starter sequence.
  Do not download originals or regenerate the collection during normal authoring.

## Use the existing visual system

- Discover featured models with `python3 scripts/deck.py layouts`. Inspect fields
  with `layouts --model <id> --json`; use `--all` only when needed.
- Prefer `\studiotemplate` with documented semantic fields. Use `\studioframe`
  for simple content. Ordinary Beamer frames also work. Preserve Inter, supported
  palettes, margins, proportions and typography; never shrink text or change
  shared layouts to fit more content. Shorten, split or choose another model.
- Default sequence: classic blue cover → team → contents → content → closing.
  The closing uses five social icons and its QR is enabled by default. Adapt optional pages to the actual brief.
- Explicitly replace demonstrative text and images. Check the built-in team
  figures against supplied information; they are example content, not verified
  live statistics. Do not invent authors, organizations, results, numbers or
  references. Label illustrative data. Use only documented palettes and fields.
- Keep assets and bibliography local to the deck. Compile from the repository
  root; do not copy themes, icon libraries or prepared shared artwork.

## Verify before delivering

Run `python3 scripts/deck.py check <name> --preview` (Docker by default;
`--backend native` for installed TeX). Fix compilation errors, overflow, missing
characters and unresolved references. Check warnings for leftover placeholders.
Inspect **every rendered page visually** for alignment, legibility, contrast,
clipping and correct content. Rendering and a passing technical report are not
visual approval. Record what was checked and any unavailable checks in the brief.
Deliver source, PDF and preview/report paths, plus meaningful limitations.

Normal authoring must not regenerate catalogues, change shared themes, update
review approvals or replace stable releases. Commits, pushes, publication and
library approval require an explicit request. For library work, follow
[CONTRIBUTING](.github/CONTRIBUTING.md) and [MAINTENANCE](docs/MAINTENANCE.md).

## Shared-library maintenance only

For tasks that adjust a shared template or component, automatically follow the
[default maintainer correction workflow](.github/CONTRIBUTING.md#default-template-correction-workflow).
During library maintenance, feedback illustrated by one lesson slide also requires
checking its canonical layout and other consumers. Update the unified slide guide
in `docs/slides/` with its preview and command as part of the same correction.
Apply the workflow without
waiting for a separate request to propagate or verify the correction.
During interactive PDF reviews, open or reveal the refreshed comparison in the
existing VS Code window: use `review_batch.py all --compare --open` for the
combined review, and retain `--open` on subsequent review builds. Set
`active_review_batches` to the current review family: unresolved older families
stay in the ledger but must not reappear automatically. After explicit approval, remove superseded local batch outputs and disposable
export/build trials for that family. Preserve canonical examples, prepared assets,
current guide previews, review decisions and stable releases. Review PDFs must
exclude explicitly approved compositions, including approved fixed lesson presets.
At each interactive handoff, report only the compositions still to verify and their
canonical categories, so the user can decide whether to review related layouts
together. Always include the exact public LaTeX command for the active layout,
with descriptive semantic field names and variant matching the reviewed example.
Prefer purpose-based keys (for example introduction, left-title and left-body)
to numbered labels. When updating a command, replace its old syntax and migrate
official callers and documentation; do not retain obsolete syntax as aliases;
show the command under the PDF
comparison as well as at handoff. Keep deferred/unresolved designs distinct from
approved designs.
For every new template and interactive review, expose all user content through
documented semantic fields: titles, headings, captions, bodies, numbers, icons
and illustrations. Keep text editable rather than embedding it in artwork.
Demonstrate complete content replacement and explicit empty values; every field
must be independently customizable while keeping the layout and fixed typography.
For every template under review, expose every icon through semantic replacement keys
that follow the same reading order as its captions. Keep the panel independent; fit
replacement icons, images and custom graphics into fixed bounds with preserved
aspect ratio. Include replacement examples in the guide and visual review.
For every interactive review of editable text, compile and visually inspect
representative longer copy as well as the short/default example. Include automatic
wrapping and explicit `\\` line breaks where supported. Check vertical centering,
spacing, overlap and clipping at the fixed font sizes. Match samples to the model:
a word-based layout needs a longer word and caption rather than a paragraph.
Verify that text beyond the supported capacity produces a clear overflow report;
never shrink the font to make a sample fit. Include and open the longer-text
previews with the comparison without waiting for another user request.

This scope covers repository maintenance. Presentation authors continue to use
the authoring workflow above. Personal content remains independent; canonical
layout corrections reach linked decks on their next build. Legacy snapshots require
explicit migration. Every official pack must use catalogue entries, including
fixed-content presets when customization is inappropriate.
