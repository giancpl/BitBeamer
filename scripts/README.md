# Tools

Run from the repository root with Python 3.10+ (`py -3` on Windows).

| Entry point | Purpose |
| --- | --- |
| `build.py` | Compile any deck; Docker default, `--backend native` for local TeX |
| `review.py` | Build one Studio model, the selection or the full archive; sync/check review material |
| `package.py` | Create named Overleaf ZIPs; `--review` keeps candidates outside stable outputs |
| `release.py` | Build and validate staged artifacts before replacement; `--review` preserves dist |

Make and VS Code tasks call these same Python launchers.
Use [the repository map](../docs/STRUCTURE.md) to distinguish source and generated files.
See [the review workflow](../docs/STUDIO-COLLECTION.md),
[maintenance map](../docs/MAINTENANCE.md) and [release guide](../docs/RELEASING.md).

## Internal and specialist tools

`studio_review.py` reads the single review ledger. `studio_templates.py`,
`studio_guides.py` and `studio_gallery.py` generate derived documentation;
`studio_preview.py` fingerprints dependencies and updates individual thumbnails.
The JavaScript files render bounded offline gallery pages.
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
`review.py pages` builds the focused title, contents and closing review with a lightweight PDF and local gallery. It preserves the selection and approval ledger.
`review.py models` builds the vector model catalogue and quick image overview. `review.py all` explicitly builds every retained composition; `palettes` remains a compatibility alias for that native collection.
Use `package-studio-review.py --models cover,icon-cards` for complete model families or `--templates` for specific legacy compositions.

## Ready content and reusable layouts

`studio_examples.py` restores retained English text and original prepared graphics
through numbered content slots. It generates the explicit full ready-content source
and the neutral reusable shortlist during sync; neither duplicates layout sources.
Use `review.py slide <id> --content example` or `review.py pages --content example`
for focused builds. Neutral remains the default. Edit `reusable_selection` in the
review ledger to curate general layouts independently of the existing showcase.
