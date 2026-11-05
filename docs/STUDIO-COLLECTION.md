# Maintain and review Studio slides

The [slide guide](slides/index.html) is the single visual reference. It opens
offline from a clone and has three views: templates, full presentations and
reusable blocks. Start with featured models; additional lesson layouts and fixed
slides load only when requested. Each page shows at most 12 cards.

```sh
python3 scripts/review.py guide --open
python3 scripts/review.py slide three-cards --open
```

Open a preview for the full canvas at 1600 px, editable areas and measured field
bounds. The command beside it reproduces the displayed example. Copy it outside
any Beamer frame. Choose only the documented original palettes; fixed-content
slides accept no overrides. See [model fields](STUDIO-MODELS.md) for semantic
options and [the authoring guide](AUTHORING.md) for personal presentations.

## Correct the canonical source

Follow the [internal correction workflow](../.github/CONTRIBUTING.md#default-template-correction-workflow).
Edit `templates/studio/<id>.tex` and its measured metadata in `templates/index.json`.
For lesson layouts, use [lesson maintenance](../library/MAINTENANCE.md). Correct
shared panels, typography and geometry once, then rebuild all affected consumers.
Personal copies remain independent; Academic is unchanged by Studio maintenance.

```sh
python3 scripts/review.py slide three-cards
python3 scripts/library.py build --changed templates/studio/three-cards.tex --preview
python3 scripts/review.py sync
python3 scripts/review.py check
```

The single-slide PDF is `build/review/slides/three-cards/slide.pdf`. Preview updates
also refresh the guide. Dependency fingerprints reuse unchanged outputs. A notes-only
edit needs sync, not compilation. Changing a shared source requires fresh previews
before the read-only check passes.

## Record feedback and select

Edit [review.json](../templates/review.json), the single Studio review ledger:

- `selection`: ordered compositions featured in the guide and compact showcase.
- `reusable_selection`: neutral layouts shortlisted for creating new content.
- `templates.<id>.status`: `in review`, `changes requested`, `approved` or `supplementary`.
- `notes` and `feedback`: observations, canonical action and verification evidence.
- `palette_reviews`: explicit review state for the original colour treatment.
- `use` and `example`: purpose and valid copyable overrides.

Lesson observations belong in `library/index.json`. Selection and a successful
build do not approve a slide. Return changed approved designs to `in review`.
Generated CSV sheets, registries, guides and showcase sources are exports; edit
the canonical JSON instead. Keep public IDs and compatibility adapters.

## Prepare HD previews and local comparisons

```sh
# Requires Pillow and Poppler, or Docker for PDF rendering; maintenance only:
python3 scripts/guide_previews.py prepare --templates three-cards
python3 scripts/guide_comparisons.py prepare --templates three-cards
python3 scripts/review.py guide --open
```

Lossless WebP thumbnails (640 px) and HD images (1600 px) are rendered directly
from clean compiled PDFs and versioned under `docs/slides/previews/`. HD files load
only when a detail is opened. Ordinary deck builds need no Pillow or converters.
Use `python3 -m pip install Pillow` in a maintenance virtual environment if needed.

Append `?maintenance=1` to the guide URL to expose **Original comparison** in the
HD inspector. It loads ignored local reference data only on request. Core comparisons
are prepared at 2000 px high with 50% overlays and text-masked graphic differences.
For official pages, run `lesson_review.py --deck <id> --pages <numbers>` after
rebuilding the lesson; see [lesson maintenance](../library/MAINTENANCE.md).
Original exports stay under ignored `design-references/figma/`; comparison data is
indexed in `build/checks/slide-guide/comparisons.js`. No separate gallery is generated.

Review geometry, typography, images and effects separately. Source-coordinate
checks and pixel residuals cannot certify every anchor within 5 px. Record
unmeasurable regions and intentional Inter/English adaptations explicitly.

## Explicit technical PDF exports and compatibility

```sh
python3 scripts/review.py selection --open
python3 scripts/review.py models
python3 scripts/review.py all
python3 scripts/review.py slide three-cards --content example
```

These commands retain compact, model and complete PDF exports under `build/review/`.
The full archive is built only on explicit request. `review.py pages --open` now
opens the guide filtered to cover, contents and closing. Old gallery URLs redirect
to this same guide and retain composition, variant and palette links.
Retained English teaching examples are available in Presentations and Reusable
blocks, alongside [complete example sources](../templates/EXAMPLES.md).

## Share unapproved work

```sh
python3 scripts/package.py --style studio --review
python3 scripts/package-studio-review.py --templates cover,three-cards,merkle-tree
python3 scripts/package-studio-review.py --selection
python3 scripts/validate-studio-review.py
```

Review ZIPs stay under `build/review/`; stable `dist/` artifacts are preserved.
See [releasing](RELEASING.md) for isolated validation and explicit approval gates.
On Windows use `py -3`; append `--backend native` for installed TeX Live/MacTeX.
