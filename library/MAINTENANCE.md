# Maintain the official lessons

Normal authoring uses [the library guide](README.md) and `scripts/deck.py`.
It never downloads originals, performs OCR or converts artwork. Everything below
is an explicit maintenance operation, run from the repository root.

## Correct content or geometry

Edit the current slide in `library/slides/`; its stable ID stays unchanged.
The corresponding record in `library/index.json` contains content fields,
source-page origins, references, translation notes, updates and review status.
Measured geometry lives in `library/layouts/`. Text stays at the declared size;
shorten or split an overflowing field instead of shrinking it automatically.

```sh
python3 scripts/library.py sync
python3 scripts/library.py build --deck bitcoin-introduction-short --preview
python3 scripts/library.py build --block hashing --preview
python3 scripts/library.py check
```

`sync` refreshes generated guides, catalogue data and all registered resource
hashes, including prepared PDF/image artwork as well as LaTeX. Run it after
maintaining shared assets so every consuming lesson receives the new fingerprints.
Artwork provenance manifests remain independently checked; sync does not rebuild
assets or approve altered artwork. `check` is read-only. Builds cache each presentation/block by its actual
source, layout, artwork, font and reference dependencies. Changing editorial notes
alone does not invalidate a PDF. Preview caching is per slide, shared between its
presentations and blocks. Do not run overlapping builds of the same presentation.

Keep translations, factual updates and graphic differences separate. Source-period
prices, statistics and screenshots are historical examples. Recheck operational
instructions against dated primary documentation before teaching them. A technical
verification date does not imply editorial approval. Never approve a slide automatically.

## Apply a correction everywhere

The [unified slide guide](../docs/slides/index.html) is the single preview/command
reference. Sync and preview updates refresh it automatically; `check` verifies its
freshness. Keep it current with every template correction.

Apply the [default maintainer correction workflow](../.github/CONTRIBUTING.md#default-template-correction-workflow)
whenever a shared layout or component is adjusted. Feedback about one lesson page
triggers this procedure automatically during library maintenance. Presentation
authors are not required to perform these maintenance operations.

Use one canonical composition for every equivalent slide. Look up the existing
Studio model and lesson layout before adding another source. Change shared layout
code for geometry, alignment and typography; change slide fields only for content.
Reuse the same prepared panel and shadow assets wherever the visual component is
the same. Do not patch individual lesson copies or split a quotation into separately
positioned lines.

`reuse_rules` in `index.json` records canonical layouts, their known consumers and
required components. It currently protects problem/solution panels and quotation
cards. Extend it when consolidating another family. Mark retired layout records
with `replaced_by` while retaining their sources for compatibility. A different
composition needs its own documented variant; equivalent content does not.

```sh
python3 scripts/library.py sync
# Inspect every affected lesson slide, deck and topic block without rendering:
python3 scripts/library.py affected --changed library/layouts/components.tex
# The same report is available to agents with --json.
# Build only consuming decks/blocks; unchanged PDFs and previews use their cache:
python3 scripts/library.py build --changed library/layouts/components.tex --preview
python3 scripts/library.py check
```

For a core quotation-card change, replace the path with
`templates/studio/chat-dialogue.tex`. Supply several paths after `--changed` when
needed. Reports for targeted builds use `build/library/affected-report.json`,
leaving the previous full-collection report intact. For core models, also follow
[the Studio review workflow](../docs/STUDIO-COLLECTION.md).

The dependency scan follows literal LaTeX inputs, graphic paths and named
`\asset` calls recursively. `sync` records new dependencies for checks and imports;
cache signatures also discover them before synchronization. Dynamic macro paths
and other non-literal resources must still be declared in `resources`. Static
analysis does not identify visually equivalent new compositions: classify these
in review and extend the reuse rules explicitly.

Checks reject replaced layouts, content that calls a different template from its
record, omitted dependencies and violations of declared reuse rules. These checks
also run before a lesson is built or copied where relevant, and in the existing
CI library checks. A shared-component change invalidates all consuming slide
previews and PDFs; editorial notes alone do not. Visually inspect the affected
pages before handing them off. No check grants automatic approval.

New imports copy personal content but reference the canonical layouts and shared
artwork directly. Correct the shared source once; linked decks render that
correction on their next build. Never replace their personal content files.

## Legacy personal projects

Old imports without `binding: shared-layouts` in `library-imports.json` are frozen
snapshots. They are not changed automatically, and block import refuses to mix
snapshot and linked layouts. Back up the project before an explicit migration:

1. Compare each recorded layout with the canonical registry and retain personal
   structural changes as a separately reviewed library variant if needed.
2. Replace matching registration paths with their canonical `library/layouts/`
   paths. Restore canonical shared artwork paths; preserve personal field values,
   images, references and slide order.
3. Remove redundant local layout/artwork copies only after a successful build and
   visual comparison. Record `binding: shared-layouts` in the import manifest.
4. Run the deck checks and inspect every page. Do not migrate another person's
   project as a side effect of library maintenance.

The explicitly requested BitPolito introduction has been migrated; its pre-migration
sources and PDF are backed up locally under `build/checks/canonical-library/before/`.

## Prepare artwork

Retained vector sources and prepared PDFs live in `library/parts/`; deduplicated
image inputs are under `library/parts/resources/`. The manifest records dependencies,
origins and hashes. Complete Figma exports and source PDF decks are unnecessary
for regenerating these parts.

```sh
python3 scripts/library.py prepare
python3 scripts/library.py sync
```

Preparation uses the existing Docker image, updates changed sources/dependencies
and replaces each prepared PDF only after conversion succeeds. Ordinary builds
use the prepared outputs with shell escape disabled. Native preparation uses the
librsvg/PyGObject/Cairo maintenance environment from [artwork setup](../docs/ASSETS.md).
An unchanged checkout does not need preparation.

For optional lossless JPEG-stream optimization and comparison generation, install
the separate maintenance requirements in a virtual environment:

```sh
python3 -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r scripts/requirements-lesson-maintenance.txt
python scripts/optimize_lesson_parts.py
python scripts/library.py sync
```

Optimization restores original JPEG bytes only after decoded-pixel equality;
it does not recompress images. Neither these dependencies nor OCR/translation tools
are needed to compile, copy or customize a lesson. The guarded import script is a
bootstrap tool, not the source of truth for curated slides.

## Compare with the originals

```sh
python3 scripts/library.py fetch
python3 scripts/lesson_review.py --deck bitcoin-introduction-short
# After a complete comparison exists, refresh only corrected pages:
python3 scripts/lesson_review.py --deck bitgeneration-economics --pages 5 6 44
# Explicit full local comparison export:
python3 scripts/lesson_review.py --all
```

`fetch` downloads only the pinned upstream revision into ignored
`design-references/figma/official-decks/pdfs/`. Comparison output goes to
`design-references/figma/official-decks/review/`, with one side-by-side
PDF per source, 2000 px images, 50% overlays and text-masked graphics residuals.
Browse them in the [unified guide](../docs/slides/index.html?view=decks&maintenance=1):
open a slide and choose **Original comparison**. The comparison renderer generates
image/data files and redirects only; it never creates a separate gallery.
Originals and comparisons never enter Git or releases. `--pages` retains unselected
page images, measurements and PDF panels from the previous complete comparison;
select every page whose content or shared dependencies changed.

Inspect geometry, typography, effects and images separately. Matched vector boxes
are measured against a 5 px tolerance; unmatched/grouped paths and raster originals
need visual inspection. A whole-canvas metric or pixel residual cannot certify
every component. Inter and English translations are intentional differences.
Complex diagrams may retain internal English vector labels as part of their
prepared graphic; the surrounding native text remains editable. Record such limits.

## Verify a change

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_lesson_runtime.py
python3 scripts/check_lesson_workflow.py
# Explicitly compile all presentations and standalone blocks:
python3 scripts/library.py build --all --preview --jobs 2
python3 scripts/library.py check
python3 scripts/review.py check
```

Docker is the default; use `--backend native` with installed TeX Live/MacTeX.
The workflow check uses a clean source copy in a path containing spaces, separate
personal assets/bibliographies and compilation without the shared lesson content folder (canonical layouts remain available).
`--also-native-in-container` additionally tests the native launcher in the TeX
container; it does not establish host-native prerequisites.

A diagnostic build can render drafts despite warnings; its report remains failed.
See [the current check report](CHECKS.md) and [page coverage](COVERAGE.md).
Lesson maintenance never replaces stable template ZIPs or publishes releases.

## Shared components and fixed presets

`library/layouts/components.tex` reuses the prepared `card-1.pdf` panel from the
existing Studio three-card layout. Its complete render box includes shadows;
`\studiolessoniconcard{x}{y}{field}` positions the 400 × 400 content panel, not
its larger shadow box. Keep icon content inside its centred 260 × 260 slot.

`index.json` has a `presets` registry for explicitly fixed, ready-made content.
Each entry points to one existing slide and declares no editable fields. `sync`
generates its wrapper under `layouts/fixed/` and registers its public name.
The lesson source calls that public name; its recorded fields remain the canonical
fixed copy. Include the wrapper in the slide's resource list. Personal imports
reference the shared wrapper and underlying measured layout; they do not copy either.
Do not freeze covers, speaker metadata, editable lists or figures requiring updates
merely because the current example already contains text. Fixed status is a content
policy, not graphical approval; source files remain available for maintenance.

## Add a presentation pack

Register each page in `index.json` with its existing canonical template or fixed
preset, fields, dependencies, origin and review state. Register a genuinely missing
composition before using it in a pack. Slide content must not define layouts,
redirect shared artwork paths or draw private frames. Checks reject these escapes,
unknown templates, private/build dependencies and incomplete source-page mappings.
Update the unified guide, command previews and consuming packs together. Keep full
reference PDFs local; user-supplied local references are marked `local_only` and
are skipped by the explicit upstream downloader.

The BitPolito parts under `parts/bitpolito/` are retained cropped source PDFs;
their manifest records source hash, crop, removed text and prepared-file hashes.
They are artwork only, never full-slide screenshots.
