# Tools

Run from the repository root with Python 3.10+ (`py -3` on Windows).

| Entry point | Purpose |
| --- | --- |
| `deck.py` | Discover layouts, scaffold private decks, build and inspect their final logs/PDFs |
| `build.py` | Compile any deck; Docker default, `--backend native` for local TeX |
| `review.py` | Open the unified slide guide (`guide --open`); build one model, sync/check review material |
| `package.py` | Create named Overleaf ZIPs; `--review` keeps candidates outside stable outputs |
| `release.py` | Build and validate staged artifacts before replacement; `--review` preserves dist |

Make and VS Code tasks call these same Python launchers.
For ordinary deck creation, follow [authoring](../docs/AUTHORING.md); no catalogue sync is needed.
Use [the repository map](../docs/STRUCTURE.md) to distinguish source and generated files.
See [the review workflow](../docs/STUDIO-COLLECTION.md),
[maintenance map](../docs/MAINTENANCE.md) and [release guide](../docs/RELEASING.md).

## Internal and specialist tools

`studio_review.py` reads the single review ledger. `studio_templates.py`,
`studio_guides.py` and `slide_guide.py` generate derived documentation;
`studio_preview.py` fingerprints dependencies and updates individual thumbnails.
The guide browser renders at most 12 cards per page and loads HD previews on demand.
`build-studio-catalogue.py` remains a compatible generator entry point.

Artwork preparation, extraction and low-level checks remain separate tools;
ordinary builds never invoke converters. `package-studio-review.py` exports arbitrary
subsets or the complete library as upload-sized projects. `validate-studio-review.py`
compiles those projects in isolation. `review-studio-collection.py` maintains optional
local original comparisons; it is not part of the daily single-slide workflow.
`check-repo.py` checks tracked and prospective non-ignored sources, and
`check-docs.py` validates local links without network access.
`build.sh` and `setup.sh` remain compatibility wrappers around `build.py`.

## Studio content slots

`python3 scripts/studio_slots.py check` validates prepared card-only replacement backgrounds.
`prepare` regenerates their PDFs from the retained derived SVGs without Figma exports.
`annotate` is a maintenance operation that initializes missing stable slot numbers
and extracts card-only SVGs from retained collection sources; run `prepare` after it.
The runtime and generated registry need no Python or converter when compiling on Overleaf.

`python3 scripts/check-studio-content.py` verifies typed content, preserved empty
card panels and expected error cases. Add `--backend native` for installed TeX.

## Grouped Studio models

`studio_models.py` validates `templates/models.json`, resolves model/variant/palette choices and generates model guides.
`studio_palettes.py prepare` regenerates monochrome named-icon contrast alternatives; `check` verifies them and retained neutral artwork without converters. It never generates slide colour variants.
`review.py pages --open` opens the unified guide filtered to title, contents and closing. It preserves the selection and approval ledger.
`review.py models` builds the vector model catalogue and quick image overview. `review.py all` explicitly builds every retained composition; `palettes` remains a compatibility alias for that native collection.
Use `package-studio-review.py --models cover,icon-cards` for complete model families or `--templates` for specific legacy compositions.

## Ready content and reusable layouts

`studio_examples.py` restores retained English text and original prepared graphics
through numbered content slots. It generates the explicit full ready-content source
and the neutral reusable shortlist during sync; neither duplicates layout sources.
Use `review.py slide <id> --content example` or `review.py pages --content example`
for a focused build or filtered guide. Neutral remains the default. Edit `reusable_selection` in the
review ledger to curate general layouts independently of the existing showcase.

`check-deck-workflow.py --backend native` is a real-compiler integration check for
private assets, bibliographies, caches, previews and expected errors. It creates
ignored synthetic projects and writes reports under `build/authoring-checks/`.

## Unified slide reference

`slide_guide.py` generates `docs/slides/index.html` and its compact catalogue from
canonical model metadata, lesson sources and prepared previews. `review.py guide
--open` opens it without compiling slides. Core/lesson synchronization and preview
updates refresh it automatically; their read-only checks reject a stale guide.
`guide_previews.py prepare` renders clean PDF commands to versioned 640/1600 px
lossless WebP images; `check` verifies freshness without conversion dependencies.
`guide_comparisons.py prepare` creates optional local 2000 px comparisons; `sync`
indexes existing comparison images and maintains old-URL redirects.
The guide uses content-based cache keys and loads at most
12 rows at a time. No original references or full review PDF is needed to browse.

For a small graphical review, `python3 scripts/review_batch.py <batch-id>` builds
only the pending compositions in that batch. Add `--compare` for local originals
and `--open` to open the result. `python3 scripts/review_batch.py all --compare`
combines pending compositions from registered batches into `build/review/batches/comparisons.pdf`. See the [review workflow](../docs/STUDIO-COLLECTION.md#review-one-small-family-at-a-time).

Graphical review PDFs contain only compositions whose catalogue status is not
`approved`, for both core templates and fixed lesson presets. Fully approved
batches are skipped by `review_batch.py all`; direct approved-batch requests
report that no review is pending. Comparison headers and `all-report.json` list
the canonical category for each pending composition.

`active_review_batches` in the review ledger scopes the combined PDF to the
current family. Older unresolved batches remain recorded without appearing in the
active comparison. Omit the setting to explicitly review all pending batches.
