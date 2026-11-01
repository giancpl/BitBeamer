# Verification report

Local verification completed on **2026-11-01**. The repository is ready for
individual graphical refinement and selection. No model was approved automatically.

## Current library

| Item | Count |
| --- | --- |
| Unique Studio compositions | 195 |
| Featured working selection | 24 |
| Public names, including compatibility aliases | 204 |
| Prepared graphic parts | 867 |
| Illustrations | 171 |

Each composition has one current editable source and one generated usage guide.
[review.json](../templates/review.json) is the sole editable source for review
status, feedback, ordered selection and examples. CSV, guides, registries and
showcase follow that ledger; generated files are marked.

## Completed local checks

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

The current visual-review pass restores reference-matched Inter Semibold in
**52 fields across 13 featured models**. Mixed card headings and code commands
retain distinct weights from their body text and instructions. Coordinates, box
sizes, font sizes, leading and artwork remain unchanged. Two English captions
use equivalent shorter wording to stay in their original fixed boxes.

The showcase, selection, all 195 catalogue pages, customization fixture and
compatibility fixture compile without overflow. The 91-test suite still passes
with the same optional converter skip. Updated comparisons and before/after
images are local under `build/review/style-validation/typography/`.
This typography pass does not approve any model or update stable release files.

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
