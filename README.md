# BitBeamer

Two independent BitPolito Beamer designs, sharing **Inter** and **171 vector illustrations**.

| Design | Best for | Showcase | Theme |
| --- | --- | --- | --- |
| **BitBeamer Academic** — default | Academic talks and structured presentations | `main-academic.tex` | `bitpolito-academic` |
| **BitBeamer Studio** | Visual talks and fixed-composition slides | `main-studio.tex` | `bitpolito-studio` |

Studio contains **194 unique compositions**, with **24 featured layouts**.
All remain available; graphical approval and selection are explicit review decisions.

## Clone and build

Install **Python 3.10+** and **Docker**, then start Docker.

```sh
git clone https://github.com/giancpl/BitBeamer.git
cd BitBeamer
python3 scripts/build.py
python3 scripts/build.py main-studio.tex
```

Outputs: `build/main.pdf` and `build/main-studio.pdf`.
On Windows replace `python3` with `py -3`. VS Code's default build task uses the same launcher.
The first Docker build prepares the compiler image; later builds reuse it offline.
With TeX Live or MacTeX, latexmk and Biber installed, add `--backend native`.
See [installation and troubleshooting](docs/SETUP.md).

## Create a presentation

Choose an editable starting document. These files are never regenerated:

| Starting document | Build | Output |
| --- | --- | --- |
| [start-academic.tex](start-academic.tex) | `python3 scripts/build.py start-academic.tex` | `build/start-academic.pdf` |
| [start-studio.tex](start-studio.tex) | `python3 scripts/build.py start-studio.tex` | `build/start-studio.pdf` |

Copy either file to `my-slides.tex` in the repository root, change its metadata
and content, then run `python3 scripts/build.py my-slides.tex --open`.
On Windows copy with `Copy-Item start-studio.tex my-slides.tex` and use `py -3`.
VS Code provides named starter tasks and **Build active document**; LaTeX Workshop
also builds the open document through the same launcher.

- **Academic:** [slide-writing guide](docs/SLIDES.md), branding, covers and standard Beamer features.
- **Studio:** [choose a layout](docs/templates/index.html), then [use its documented fields](docs/USING-STUDIO.md).
  The [content API](docs/STUDIO-CONTENT.md) provides consistent text, icon and image keys.
- **Icons:** `\alice[height=2cm]`, `\cow[width=3cm]` or `\asset[width=2cm]{qrcode-one}`.
  See [the icon guide](docs/ICONS.md) and [printable cheat sheet](examples/icon-cheatsheet.tex).

`main-academic.tex` is the full Academic showcase; `main.tex` forwards to it.
`main-studio.tex` is a generated Studio showcase. Copy it before editing, because
`review.py sync` regenerates it from the selected layouts.
Every Studio slide has a [copyable usage guide](docs/templates/GUIDES.md).
Ordinary builds use included prepared graphics and need no converter or Figma export.

## Improve the library

```sh
python3 scripts/review.py slide three-cards --open
python3 scripts/review.py selection --open
python3 scripts/review.py sync
python3 scripts/review.py check
```

Edit a composition's current source, inspect its individual PDF, and record notes,
status and selection in `templates/review.json`. Single-slide updates reuse cached
outputs and refresh only affected previews. The full archive is an explicit `review.py all` operation.
See [the review workflow](docs/STUDIO-COLLECTION.md).

## Overleaf and maintenance

Academic and Studio have [separate Overleaf projects](docs/README.md#overleaf).
The main Studio download contains the compact selection and its dependencies;
custom exports can contain any subset. The complete collection stays in the clone.

Use [the documentation map](docs/README.md) for writing, review and maintenance.
[Release instructions](docs/RELEASING.md) explain validation and approval gates.
`build/`, `dist/` and original-reference comparisons are local outputs, excluded from Git.
`main.tex` and `\usetheme{bitpolito}` remain compatible Academic entry points.
