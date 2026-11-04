# Refine the Studio library

Start with [grouped models, variants and palettes](STUDIO-MODELS.md). The advanced composition API remains compatible.

The library has 196 current compositions and nine compatibility names.
Start with the 21 featured models (24 retained composition choices); the full archive remains available.
Academic is independent. Compilation never approves a design.

## Choose title, contents and closing layouts

Build a focused review from the existing complete catalogue:

```sh
python3 scripts/review.py pages --open
```

The first ten pages show four cover variants, five agenda variants and the closing
composition. Five related layouts follow separately: a section divider, an opening
dashboard, two QR closing layouts and `cover-script-blue`. The latter is classified
as a cover in the complete catalogue but currently renders a process diagram, so
it is flagged separately for review. Only their retained native palettes are used.

Open `build/review/pages/index.html` for grouped previews, copyable commands,
editable sources and optional local original references. The quick PDF is
`build/review/pages/studio-pages-overview.pdf`; the separate
`studio-pages-catalogue.pdf` preserves vector graphics and selectable slide text.
Review labels sit below the slide in the quick PDF, leaving its full canvas visible.

Use composition IDs to record feedback. This command does not change defaults,
selection or approvals. Agenda presets expose manual catalogue fields; the plain four/five-item layouts
also support automatic section binding through `\studiotocframe[variant=...]`. These are catalogue candidates,
separate from the standard theme helpers used in `start-studio.tex`.

The same candidates can be reviewed with retained English content:

```sh
python3 scripts/review.py pages --content example --open
```

This produces a separate gallery and PDFs under `build/review/pages/examples/`.
The two galleries link to each other. It does not overwrite neutral previews.
[Ready-content sources](../templates/EXAMPLES.md) preserve the full collection;
[reusable_selection](../templates/REUSABLE.md) is a separate, initially four-slide
shortlist in `review.json`. Existing showcase selection and approvals are retained.

## Review one slide

Open [the gallery](templates/index.html), choose **Open slide**, and inspect the editable areas.
Use the stable model ID for comments rather than a PDF page number.

```sh
python3 scripts/review.py slide three-cards --open
```

Edit `templates/studio/three-cards.tex` for layout changes. Its PDF is
`build/review/slides/three-cards/slide.pdf`. The same command recompiles that slide
and updates only its preview when inputs change. An unchanged PDF is reused.
Compatibility IDs resolve to their current composition for review; their public LaTeX defaults remain intact.

Text and graphic fields keep fixed geometry. Check margins, proportions, crops,
shadows and optical alignment. Overflow is reported rather than automatically fitted.
Changing the field API or measured boxes also requires the corresponding update in
`templates/index.json`. Shared changes invalidate dependent previews.

## Record feedback and curate

Edit [review.json](../templates/review.json):

- `reusable_selection`: ordered neutral layouts for creating new content, initially title, contents and closing.
- `selection`: ordered composition IDs. The gallery and showcase group these into 21 featured models; the compact project retains all 24 selected composition choices.
- `templates.<id>.status`: `in review`, `changes requested`, `approved` or `supplementary`.
- `notes`: requested changes or review observations.
- `palette_reviews`: explicit review state for the retained original colour treatment.
- `use` and `example`: purpose and copyable field overrides.

Selection is separate from approval. Supplementary models have no corresponding
original; they also need explicit approval before inclusion in a stable release.
Keep all unique compositions; removing an ID from selection only removes its featured position.
After altering an approved design, return its status to `in review` until rechecked.

```sh
python3 scripts/review.py sync
python3 scripts/review.py check
```

Sync updates registries, the CSV sheet, usage guides, galleries, selection deck and
showcase without compiling. Never edit generated files directly. Notes and selection
changes do not invalidate artwork previews. Check is read-only and needs no TeX or converter.
On Windows use `py -3`; append `--backend native` to build commands for installed TeX.

## Selection and full archive

```sh
python3 scripts/review.py selection --open
python3 scripts/review.py all
```

Outputs: `build/review/studio-selected-templates.pdf` and
`build/review/studio-template-catalogue.pdf`. The full command also builds the index and
combines it into `build/review/bitbeamer-studio-review.pdf`; no manual PDF merge is needed.
Only the explicit full-archive command
builds every model. Browser galleries display bounded pages and load images on demand.
The [per-slide guides](templates/GUIDES.md) describe how to reuse each composition.

## Optional original comparisons

Original exports and comparison images remain under ignored `design-references/figma/`.
They are not needed to compile or refine a current LaTeX composition.
For measured comparisons at 2000 pixels high, follow [the reconstruction guide](FIGMA.md).
The maintenance renderer can reuse cached original images and refresh known changed pages:

```sh
python3 scripts/build.py tests/fixtures/studio-collection-geometry.tex build/review
python3 scripts/review-studio-collection.py
# Refresh only browser presentation from existing comparisons:
python3 scripts/review-studio-collection.py --gallery-only
```

The comparison renderer needs Poppler, Pillow, NumPy, pycairo, PyGObject and librsvg;
these are optional maintenance dependencies. Geometry is checked separately from
Inter/English typography and effects. A measured 5-pixel tolerance never implies visual approval.

## Share unapproved work

```sh
python3 scripts/package.py --style studio --review
python3 scripts/package-studio-review.py --templates cover,three-cards,merkle-tree
python3 scripts/package-studio-review.py --selection
# Complete library, split into upload-sized projects:
python3 scripts/package-studio-review.py
python3 scripts/validate-studio-review.py
```

The main review ZIP is under `build/review/packages/`; custom and full split projects
are under `build/review/overleaf/`, and the working selection has its own
`build/review/selection-overleaf/` directory. The split validator defaults to the full directory;
use `--directory` and `--output` to validate another set separately.
All packages include prepared graphics and the icon registry. No converters, original
exports, Python or shell escape are needed after extraction.

See [maintenance](MAINTENANCE.md) for prepared artwork and [releasing](RELEASING.md)
for stable approval gates. Review actions never replace files in `dist/`.
