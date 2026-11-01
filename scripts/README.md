# Tools

Run from the repository root with Python 3.10+ (`py -3` on Windows).

| Entry point | Purpose |
| --- | --- |
| `build.py` | Compile any deck; Docker default, `--backend native` for local TeX |
| `review.py` | Build one Studio model, the selection or the full archive; sync/check review material |
| `package.py` | Create named Overleaf ZIPs; `--review` keeps candidates outside stable outputs |
| `release.py` | Build and validate staged artifacts before replacement; `--review` preserves dist |

Make and VS Code tasks call these same Python launchers.
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
