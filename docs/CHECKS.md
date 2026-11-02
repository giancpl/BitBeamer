# Verification report

Local content-API verification completed on **2026-11-02**. The repository is ready for
individual graphical refinement and selection. No model was approved automatically.

## Current library

| Item | Count |
| --- | --- |
| Unique Studio compositions | 194 |
| Featured working selection | 24 |
| Public names, including compatibility aliases | 203 |
| Reference graphic parts | 867 |
| Separated replacement-card panels | 34 |
| Illustrations | 171 |

Each composition has one current editable source and one generated usage guide.
[review.json](../templates/review.json) is the sole editable source for review
status, feedback, ordered selection and examples. CSV, guides, registries and
showcase follow that ledger; generated files are marked.

## Collection cleanup (2026-11-02)

The supplementary `quotation` preset (Quiet quotation) was removed because it has
no matching Figma original. The featured selection remains unchanged at 24 layouts.
The earlier checks below record the collection before this removal. The 194-page
catalogue and 204-page indexed review were rebuilt, along with previews and local
original/replica comparisons. The 98-test suite passes (one optional converter
check skipped); generated-file freshness and offline documentation checks pass.

## Typed content API checks (2026-11-02)

- Every field in all 195 models has a stable typed slot: `text/N`, `icon/N`,
  `image/N`, `graphic/N` or `file/N`. Seven mixed text blocks also support
  `heading/N` and `body/N`. Existing fields and all nine aliases remain compatible.
- All 195 defaults and all 195 guide examples compile without overflow. Default
  preview PNGs are byte-identical to the pre-API baseline on every page at 480px.
- The eight-page customization example compiles with replacement icons, images,
  lists, heading/body blocks and code-file input. Replacements preserve fixed text
  styles and graphic proportions; 34 separated card frames retain their shadows.
- Nine real compiler cases pass: clear-option ordering, fitted/empty graphics,
  empty structured text, alias handling, unknown fields, missing icons/images/files
  and excessive text. Expected error cases fail with model/field diagnostics.
- The 98-test suite passes with one optional Inkscape converter check skipped.
- An isolated eight-model Overleaf review project compiles its main document,
  catalogue, typed customization example, guide example and Biber verification.
  The compiler has no source-checkout mount, converter, network or shell escape.
- Generated guides, template dependencies, prepared panels and offline links are
  current. Original artwork and Academic layout files are unchanged. No graphical
  approval, stable-artifact replacement, commit or push is part of this work.

See [the content API](STUDIO-CONTENT.md) and
[the editable examples](../examples/studio-customization.tex).

## Earlier baseline checks (2026-11-01)

- **91 regression tests:** 90 passed; one optional Inkscape converter test skipped.
- All **195 compositions compile**, with embedded fonts and selectable text.
  The full command also produces the **205-page indexed review** automatically.
- The compact selection and showcase contain **24 pages**. Single-slide compilation
  and cached-PDF reuse pass; source/part/data changes invalidate the affected models.
  Notes and selection changes do not invalidate artwork previews.
- Field customization, empty content, graphic replacement, code/CSV input and return
  to ordinary frames pass. All nine compatibility names and pilot commands compile.
  Unknown fields, excessive text and oversized graphics fail with model/field diagnostics.
- Academic is pixel-identical to the saved baseline on all **11 pages** in both
  **16:9 and 4:3**, compared at 800px width. The recorded Academic and source-artwork
  hashes are unchanged.
- Both candidate Overleaf ZIPs pass isolated validation. Academic logo/cover variants,
  wrapped headings, Studio components, all 171 illustrations and bibliography checks pass.
- All **five split review projects** compile independently: **20 documents**, including
  all **195 catalogue pages**, guide examples and explicit Biber verification.
  The extracted projects have no checkout mount, converter, network or shell escape.
- The compact Studio ZIP is **3,118,802 bytes (2.97 MiB)**. Split ZIPs account for guides
  and ZIP overhead and remain below the 45 MiB budget; the largest is 44,381,074 bytes.
  Both main ZIPs reproduce identical bytes and match the validated candidates.
- A clean source copy in a path containing spaces builds Academic, Studio and the
  selection with the native launcher. This uses installed Linux TeX inside the existing
  compiler container; it is not a claim of a separate native-host installation.
- Docker-only thumbnail generation and PDF merging pass with host Poppler hidden.
  The compiler image now includes those tools; ordinary builds need no SVG conversion.
- The parts gallery displays at most 24 entries. Pagination, filtering, empty results
  and copying pass behaviour tests; Firefox renders the offline page successfully.
  The existing slide-gallery navigation and field-map tests continue to pass.
- Offline documentation links, generated-file freshness, prepared dependencies and
  tracked/prospective repository-content checks pass. Stable artifacts remain byte-identical.

## Studio typography refinement

The latest graphical pass revised 35 compositions: stronger Inter text, source
left edges, centred icon captions, checklist hierarchy and the clockwise diagonal
title. Text boxes and English copy were adjusted explicitly where needed; fonts
never shrink automatically. Academic and original artwork stayed unchanged.
All current templates still require human graphical approval.

## Editable starters and clone handoff

`start-academic.tex` and `start-studio.tex` are short editable documents, independent
of catalogue regeneration. Both compile to four pages with the shared launcher.
VS Code provides named starter tasks and an active-document build task. The clone
guides distinguish these documents from the full Academic and generated Studio showcases.
Each Overleaf package also contains a corresponding editable `start.tex`, included
in isolated package validation. The 91-test suite passes with one optional converter skip.

## Start the graphical review

```sh
python3 scripts/review.py slide three-cards --open
python3 scripts/review.py selection --open
```

Use [the gallery](templates/index.html), [individual slide guides](templates/GUIDES.md)
and [review workflow](STUDIO-COLLECTION.md). Refine the current source, record notes
and status in the ledger, then run `review.py sync` and `review.py check`.
Fonts and geometry remain fixed; compilation is not graphical approval.

Current local outputs:

- `build/review/slides/<id>/slide.pdf`: one composition.
- `build/review/studio-selected-templates.pdf`: labelled working selection.
- `build/review/bitbeamer-studio-review.pdf`: complete indexed review.
- `build/review/release/`: both validated candidate ZIPs and preview PDFs.
- `build/review/finalization-checks.json`: aggregate machine report.
- `build/review/finalize-overleaf-validation/report.json`: isolated full-library checks.

Stable files in `dist/` are preserved. Review packages remain available without
approval; stable Studio exports require every selected model to be explicitly approved.

## Pending outside this local verification

Graphical refinement, approval and final selection remain human review decisions.
Original-frame geometry/effect comparisons are a separate optional maintenance
workflow; the checks above do not newly certify every reconstruction against Figma.

Linux/macOS/Windows portable jobs and native Linux CI are configured. Hosted jobs,
a real Overleaf service upload, version-tag checks and publication have not run in
this local session. This report records local verification. Repository synchronization is recorded in
Git history; no version tag or release publication is part of this handoff.
