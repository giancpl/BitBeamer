# Maintain BitBeamer

Daily layout work uses [the review launcher](STUDIO-COLLECTION.md).
Use these lower-level tools only when changing their source inputs.

| Change | Preparation | Documentation |
| --- | --- | --- |
| Illustration SVG | `prepare-assets.py`, then `build-asset-catalogue.py` | [Artwork](ASSETS.md) |
| Studio theme derivatives | `prepare-studio-assets.py` | [Studio](STUDIO.md) |
| Extracted graphic part | `studio_parts.py` or `studio_collection.py`, then `catalogue-studio-collection.py --previews` | [Parts](STUDIO-PARTS.md) |
| New Figma reconstruction | Extraction and measurements before preparation | [Figma](FIGMA.md) |
| Metadata, review or selection | `review.py sync` | [Review](STUDIO-COLLECTION.md) |
| Release | `release.py` after approval | [Releasing](RELEASING.md) |

Commands above live under `scripts/`; use Python 3.10+ (`py -3` on Windows).
Converters are maintenance-only dependencies. Keep derived sources, prepared outputs,
dependencies and provenance; full original frame exports stay local and ignored.

## Checks

```sh
python3 scripts/review.py check
python3 -m unittest discover -s tests -v
python3 scripts/build-asset-catalogue.py --check
```

Review checks validate documentation links, canonical sources, selection, prepared
artwork and preview freshness without rendering. The repository check covers tracked
and new non-ignored files, including work not yet added to Git.
Full TeX and isolated package checks are separate; see [verification](CHECKS.md).

## Local output

- `build/`: ordinary compiled documents and disposable review artifacts/caches.
- `dist/`: validated stable release files; ordinary cleanup preserves this directory.
- `design-references/figma/`: optional original exports and comparison outputs.

`make clean` removes build output only. Archive review PDFs elsewhere if needed before
cleaning. Never treat original comparison outputs as distributable source.
