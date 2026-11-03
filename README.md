# BitBeamer

**BitBeamer Studio** is the default design. **BitBeamer Academic** is the simpler
alternative for standard Beamer authoring. Both share **Inter** and **171 vector illustrations**.

| Design | Editable starter | Showcase | Theme |
| --- | --- | --- | --- |
| **Studio** — default | [start-studio.tex](start-studio.tex) | `main-studio.tex` | `bitpolito-studio` |
| **Academic** | [start-academic.tex](start-academic.tex) | `main-academic.tex` | `bitpolito-academic` |

## Clone and build

Install **Python 3.10+** and **Docker**, start Docker, then run:

```sh
git clone https://github.com/giancpl/BitBeamer.git
cd BitBeamer
python3 scripts/build.py
```

Output: `build/main.pdf`, the selected Studio showcase. The first build prepares
the compiler image; later builds reuse it offline. With TeX Live/MacTeX, latexmk
and Biber installed, add `--backend native`. See [setup and troubleshooting](docs/SETUP.md).
On Windows replace `python3` with `py -3`. VS Code tasks use the same launcher.

## Create your presentation

Copy a starter to a new `.tex` file at the repository root:

```sh
cp start-studio.tex my-slides.tex
python3 scripts/build.py my-slides.tex --open
```

Use `start-academic.tex` for Academic. On Windows copy with
`Copy-Item start-studio.tex my-slides.tex`.
Edit the title, author and content in your copied file; starter files are never regenerated.
Studio includes standard cover, automatic contents and closing commands; see
[standard pages](docs/STUDIO.md#standard-pages-and-the-default-frame).
The title page is classic blue; [optional BitGeneration covers](docs/STUDIO.md#choose-the-cover) use the `variant` field.

- **Studio:** [browse the gallery](docs/templates/index.html), then use the [model and palette guide](docs/STUDIO-MODELS.md).
  Each model has copyable examples and named fields for text and graphics.
- **Academic:** use ordinary Beamer frames; see [writing slides](docs/SLIDES.md).
- **Icons:** `\alice[height=2cm]`, `\cow[width=3cm]` or `\asset[width=2cm]{qrcode-one}`.
  See [icons](docs/ICONS.md) and the [printable cheat sheet](examples/icon-cheatsheet.tex).

`main.tex` forwards to Studio. `main-studio.tex` is generated from the working
selection; copy it before editing. `main-academic.tex` is the full Academic showcase.
Explicit Academic theme names and the legacy `\usetheme{bitpolito}` remain available.

Studio offers two complementary catalogues: [neutral reusable layouts](templates/REUSABLE.md)
for a new presentation, and [ready-content examples](templates/EXAMPLES.md) retaining
editable English subject matter. Both use the same layout sources. The reusable
shortlist starts with title, contents and closing; the full collection remains available.

## Find files and refine the library

[Repository map](docs/STRUCTURE.md) · [Documentation](docs/README.md) · [Examples](examples/README.md)

Edit the current composition under `templates/studio/`; keep notes and selection
in `templates/review.json`. [The review workflow](docs/STUDIO-COLLECTION.md) explains
source files, generated references and graphical approval.

```sh
python3 scripts/review.py slide three-cards --open
python3 scripts/review.py sync
python3 scripts/review.py check
```

Use `review.py models --open` for the quick model PDF. The complete archive is an
explicit `review.py all` operation. See [maintenance](docs/MAINTENANCE.md) and
[contributing](.github/CONTRIBUTING.md) for tooling and checks.

## Overleaf downloads

[Studio](docs/OVERLEAF-STUDIO.md) and [Academic](docs/OVERLEAF.md) have separate ZIPs.
Studio includes the curated selection. Academic opens a short editable starter and
includes its full showcase separately. Both contain prepared icons and need no
Python, Docker or converters after upload.

```sh
python3 scripts/package.py --review
python3 scripts/package.py --style academic --review
```

Candidates go to `build/review/packages/`. [Releasing](docs/RELEASING.md) covers
validation, approval and stable artifacts. `build/`, `dist/` and original Figma
comparisons are local outputs, excluded from Git. `make clean` removes `build/`.
