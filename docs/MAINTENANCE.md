# Maintain BitBeamer

See [the repository map](STRUCTURE.md) for editable sources and generated output.
Daily layout work uses [the review launcher](STUDIO-COLLECTION.md).
Use these lower-level tools only when changing their source inputs.

Shared-template corrections automatically follow the
[default maintainer workflow](../.github/CONTRIBUTING.md#default-template-correction-workflow),
including changes first reported on a single example. This procedure applies to
repository maintenance; creating a presentation keeps its existing authoring flow.

| Change | Preparation | Documentation |
| --- | --- | --- |
| Illustration SVG | `prepare-assets.py`, then `build-asset-catalogue.py` | [Artwork](ASSETS.md) |
| Studio theme derivatives | `prepare-studio-assets.py` | [Studio](STUDIO.md) |
| Extracted graphic part | `studio_parts.py` or `studio_collection.py`, then `catalogue-studio-collection.py --previews` | [Parts](STUDIO-PARTS.md) |
| New Figma reconstruction | Extraction and measurements before preparation | [Figma](FIGMA.md) |
| Named-icon contrast resources | `studio_palettes.py prepare`; ordinary checks never convert | [Models](STUDIO-MODELS.md) |
| Metadata, review or selection | `review.py sync` | [Review](STUDIO-COLLECTION.md) |
| Official lessons or topic blocks | `library.py sync`, then targeted build | [Lesson maintenance](../library/MAINTENANCE.md) |
| Release | `release.py` after approval | [Releasing](RELEASING.md) |

Commands above live under `scripts/`; use Python 3.10+ (`py -3` on Windows).
Converters are maintenance-only dependencies. Keep derived sources, prepared outputs,
dependencies and provenance; full original frame exports stay local and ignored.

## Unified slide guide

[Open the slide guide](slides/index.html) or run `python3 scripts/review.py guide --open`.
It is generated from canonical templates, lesson invocations and current prepared
previews. Normal sync and preview updates refresh it; read-only checks reject a
stale copy. Browser assets live beside it; the HTML shell is `scripts/slide-guide.html`.
The guide loads 12 rows at a time and needs no TeX build or original references.

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
