# BitBeamer

A BitPolito Beamer theme with blue diagonal headers, a patterned cover, and
**171 vector illustrations**. The compact English showcase contains 10 numbered
frames and 11 PDF pages, including one overlay.

## Clone and build

Install **Python 3.10+**, **TeX Live** (MacTeX on macOS), **latexmk**, and **Biber**.
[Installation instructions](docs/SETUP.md) cover Linux, macOS, and Windows.

```sh
git clone git@github.com:giancpl/BitBeamer.git
cd BitBeamer
python3 scripts/build.py --setup
python3 scripts/build.py
```

Output: `build/main.pdf`. On Windows, replace `python3` with `py -3`.
You can also clone over HTTPS: `https://github.com/giancpl/BitBeamer.git`.

Open the folder in VS Code and press **Ctrl+Shift+B** for the default native
build. LaTeX Workshop recipes use the same launcher; Windows users choose the
Windows native recipe. Docker is optional and selected explicitly:

```sh
python3 scripts/build.py --backend docker
```

A normal build needs neither Docker nor an SVG converter. Prepared artwork is
included; the launcher reports stale or missing assets before compiling.

## Edit slides

Edit `main.tex` and `bibliography.bib`. Keep the theme files beside your deck.
The [slide guide](docs/SLIDES.md) maps the showcase to reusable Beamer examples.

The default logo pair is **PoliTo + the white BitPolito bull head**:

```latex
\usetheme{bitpolito}
% Optional alternatives; use one theme declaration:
% \usetheme[bitpolitologo=wordmark]{bitpolito}
% \usetheme[bitpolitologo=monogram]{bitpolito}
% \usetheme[group=crypto]{bitpolito}
```

Choose the cover orientation in the same theme declaration:

```latex
\usetheme[cover=image-left]{bitpolito}  % Default: image left, text right.
% Or: \usetheme[cover=image-right]{bitpolito}  % Text left, image right.
```

Both covers use left-aligned text and logos. Preview both with
`python3 scripts/build.py examples/cover-layouts.tex` (output:
`build/cover-layouts.pdf`). See [cover options](docs/SLIDES.md#choose-a-cover).

Title-only and subtitled frames share a standard header height. Wrapped titles
expand the header when needed. Use `aspectratio=43` for 4:3 instead of 16:9.

## Use icons

```latex
\alice[height=2cm]
\cow[width=3cm]
\bitcoin[height=1cm]
\asset[width=2cm]{qrcode-one}
```

Read the [icon guide](docs/ICONS.md), browse the [complete catalogue](assets/CATALOGUE.md),
or compile the printable reference:

```sh
python3 scripts/build.py examples/icon-cheatsheet.tex
python3 scripts/build.py examples/asset-catalogue.tex
```

## Download or prepare a release

Download `bitbeamer-overleaf.zip` from a GitHub release, upload it as a new
Overleaf project, and select **main.tex** with **pdfLaTeX**. The ZIP includes
prepared artwork and an [Overleaf quick start](docs/OVERLEAF.md).

To build the ZIP and all five PDF references locally:

```sh
python3 scripts/release.py
# Optional: python3 scripts/release.py --backend docker
```

Outputs are in `dist/`. The script validates the ZIP before replacing a
previous release. Local scripts never commit, tag, push, or publish.
Use `python3 scripts/check-repo.py` to check tracked files. See
[releasing](docs/RELEASING.md) for repository contents and GitHub automation.

## Find your way around

| Location | Purpose |
| --- | --- |
| `main.tex`, `bibliography.bib`, `*.sty` | Presentation, references, and theme |
| `examples/` | Illustration example, full catalogue, printable cheat sheet, cover comparison |
| `assets/` | Illustration sources, metadata, and prepared library |
| `images/bitpolito/` | Theme logos, cover pattern, and their sources |
| `docs/` | [Setup](docs/SETUP.md), [slides](docs/SLIDES.md), [icons](docs/ICONS.md), [artwork](docs/ASSETS.md), [releases](docs/RELEASING.md) |
| `scripts/`, `tests/` | [Build and maintenance tools](scripts/README.md), automated checks |
| `build/`, `dist/` | Local outputs, excluded from Git |

Authored documentation, comments, and slides use English. Original artwork and
original export names are preserved for provenance. The repository retains its
[licence](LICENSE); supplied brand artwork has its own [licence](images/bitpolito/LICENSE).
