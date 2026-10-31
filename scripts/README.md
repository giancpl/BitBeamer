# Build and maintenance tools

Run from the repository root with Python 3.10+. On Windows use `py -3`.

| Script | When to use it |
| --- | --- |
| `build.py` | Compile `main.tex` or a document in `examples/`; native by default |
| `release.py` | Build and validate the ZIP and five previews before replacing previous release files |
| `package.py` | Create only `dist/bitbeamer-overleaf.zip` from prepared files |
| `check-repo.py` | Reject tracked local outputs, caches, archives, and redundant placeholders |
| `check-docs.py` | Check local Markdown links offline without writing files |
| `validate-release.py` | Validate the extracted ZIP and all logo options |
| `prepare-assets.py` | Regenerate illustration PDFs after artwork changes; `--check` is read-only |
| `build-asset-catalogue.py` | Regenerate the searchable and visual icon catalogue; `--check` checks freshness |
| `build-bitpolito-assets.py` | Regenerate theme logo PDFs from their SVG/PNG sources |
| `build-cover-background.py` | Recolour and regenerate the prepared cover pattern |
| `import-assets.py` | Reimport the reviewed original collection using `assets/index.json` |

`asset_library.py` contains artwork checks and conversion. `asset_catalogue.py`
generates icon references from the live library and descriptive metadata.
`doc_checks.py` implements the offline Markdown-link check.
`build.sh` and `setup.sh` are thin compatibility wrappers around `build.py`.
Artwork conversion dependencies are only needed for artwork maintenance.
[The artwork guide](../docs/ASSETS.md) describes the conversion backends.
