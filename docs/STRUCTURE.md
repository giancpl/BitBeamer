# Repository structure

There are two workflows: [create a presentation](AUTHORING.md) in a private project,
or [refine the shared library](STUDIO-COLLECTION.md). Studio is the default;
Academic remains independent. Docker is the default backend; `--backend native`
uses installed TeX. On Windows use `py -3` instead of `python3`.

## Where to work

| Location | Role | Edit directly? |
| --- | --- | --- |
| `presentations/<name>/` | Private deck, brief, assets and bibliography; ignored by Git | Yes, only the current deck |
| `AGENTS.md`, `docs/AUTHORING.md` | Agent entry point and complete authoring workflow | When maintaining authoring guidance |
| `start-studio.tex`, `start-academic.tex` | Short editable starting documents | Used by `deck.py new`; never regenerated |
| `main.tex` | Default entry point, forwarding to Studio | Only to change the project entry point |
| `main-studio.tex` | Selected Studio showcase | Generated; copy before editing |
| `main-academic.tex` | Full Academic feature showcase | Yes, or use its starter |
| Root `.sty` files | Academic and Studio theme implementations | When changing a theme |
| `bibliography.bib` | Example bibliography | Yes |
| [examples](../examples/README.md) | Focused examples and generated catalogues | Follow the directory guide |
| [templates](../templates/README.md) | Studio compositions, field contracts, grouping and review ledger | Edit canonical sources and metadata |
| [assets](ASSETS.md) | Shared icon source artwork and prepared library | Use the preparation workflow |
| `images/bitpolito/` | Theme logos and cover artwork | Keep sources, prepared files and manifests together |
| `images/studio/` | Prepared parts, retained derived sources, neutral images and icon contrast alternatives | Use the artwork workflow |
| [docs](README.md) | Authored guides and generated visual references | Follow generated-file notices |
| [scripts](../scripts/README.md) | Build, review, validation and maintenance tools | When maintaining tooling |
| `tests/` | Portable regression tests and TeX fixtures | When verifying changed behaviour |
| `.vscode/` | Tasks and LaTeX Workshop settings | Keep consistent with the Python launchers |
| `.github/` | CI, release configuration and contribution entry point | When maintaining the hosted workflow |

The themes stay at the root so LaTeX and copied examples find them without custom
search paths. Academic and Studio retain their public names; they share fonts,
brand colours and icons, with separate layouts.

## Editable sources and generated references

For Studio, edit one current composition in `templates/studio/<id>.tex`.
Its measured fields belong in `templates/index.json`; grouping, variants and named
field mappings belong in `templates/models.json`. Review notes, approval and ordered
selection belong only in `templates/review.json`.

`review.py sync` generates registries, guides, gallery pages, indices, the CSV sheet
and the selected showcase. `review.py slide <id>` compiles one source and refreshes
its preview. `review.py check` verifies freshness without changing files. Prepared
artwork and browser previews are retained in Git so a clone can build and browse
the library without conversion or Figma exports.

Full frame exports and original comparison renders remain local maintenance inputs.
Prepared SVG/PDF pairs inside `images/` are retained source dependencies, rather than
ordinary build output; preserve them and their provenance when refining a layout.

## Local output

| Location | Contents | Included in Git? |
| --- | --- | --- |
| `build/presentations/<name>/` | Per-deck PDF, cache, report and numbered preview pages | No |
| `build/` | Compiled PDFs, logs, caches, comparisons and review ZIPs | No |
| `dist/` | Validated stable release artifacts | No |
| `design-references/figma/` | Original exports and local graphical comparisons | No |
| Python, test and editor caches | Disposable local state | No |

`make clean` removes `build/`. It preserves `dist/` and local original exports.
The ordinary build and review workflow never publishes, commits or pushes changes.

## Useful commands

```sh
python3 scripts/deck.py new my-talk
python3 scripts/deck.py check my-talk --preview
python3 scripts/build.py
python3 scripts/build.py start-academic.tex
python3 scripts/review.py slide three-cards --open
python3 scripts/review.py sync
python3 scripts/review.py check
```

For artwork preparation see [maintenance](MAINTENANCE.md); for candidates and stable
exports see [releasing](RELEASING.md). Each Overleaf ZIP has its own `main.tex` and
contains only that design's selected dependencies, prepared icons and relevant guides.
