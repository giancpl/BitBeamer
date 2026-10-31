# Native setup

After cloning as shown in [the README](../README.md), open a terminal in the
repository root. The source project needs **Python 3.10+**, **pdfLaTeX**, **latexmk**, and
**Biber**. The converted illustration library is included. Docker and SVG
converters are optional; neither is used by the default build.

## Debian / Ubuntu

```sh
sudo apt-get update
sudo apt-get install python3 latexmk texlive-latex-extra \
  texlive-fonts-recommended texlive-bibtex-extra biber
python3 scripts/build.py --setup
python3 scripts/build.py
```

## Fedora

Install TeX Live with the template's text, math, and bibliography packages:

```sh
sudo dnf install python3 latexmk biber texlive-scheme-medium \
  texlive-mathpazo texlive-palatino texlive-helvetic texlive-biblatex
python3 scripts/build.py --setup
python3 scripts/build.py
```

Alternatively, use the [TeX Live installer](https://tug.org/texlive/quickinstall.html)
and its full package scheme. If a minimal installation reports a missing
`.sty` or font, install that package through your TeX distribution.

## macOS

Install [MacTeX](https://tug.org/mactex/) and [Python 3](https://www.python.org/downloads/macos/).
MacTeX includes pdfLaTeX, latexmk, and Biber. Ensure `/Library/TeX/texbin` is
on your PATH, then restart the terminal and IDE:

```sh
python3 --version
latexmk --version
pdflatex --version
biber --version
python3 scripts/build.py --setup
python3 scripts/build.py
```

## Windows

Install [Python 3](https://www.python.org/downloads/windows/) with the Python
launcher, and [TeX Live](https://tug.org/texlive/windows.html), preferably the
full scheme. Enable its PATH integration. Restart the terminal and IDE.
In PowerShell, check and build with:

```powershell
py -3 --version
latexmk --version
pdflatex --version
biber --version
py -3 scripts/build.py --setup
py -3 scripts/build.py
```

If the TeX commands are missing, add the TeX Live `bin\windows` directory
inside your installed TeX Live version to PATH. No Bash, Make, or WSL is
required. Windows filenames and project paths may contain spaces.

## IDE workflow

Open the repository folder in VS Code. **Ctrl+Shift+B** builds `main.tex`
using the Python launcher and native TeX. Run Task also offers the asset
example, catalogue, icon cheat sheet, cover comparison, documentation check, setup check, and an explicit Docker build. Windows tasks
use `py -3`; Linux and macOS tasks use `python3`.

With LaTeX Workshop installed, select **BitBeamer: native TeX Live** from the
recipe menu; Windows users select **BitBeamer: native TeX Live — Windows**.
The first recipe is native. Separate optional Docker recipes are provided.
All tasks and recipes call the same `scripts/build.py` launcher.

```sh
python3 scripts/build.py examples/assets-example.tex
python3 scripts/build.py examples/asset-catalogue.tex
python3 scripts/build.py examples/icon-cheatsheet.tex
python3 scripts/build.py examples/cover-layouts.tex
python3 scripts/build.py --force --open
```

On Windows replace `python3` with `py -3`. Outputs are in `build/`.
`latexmk -pdf main.tex` also works directly with the supplied prepared assets;
the launcher additionally checks whether artwork needs regeneration.

## Optional Docker compiler

Install Docker only if you want this backend, and select it explicitly:

```sh
python3 scripts/build.py --backend docker --setup
python3 scripts/build.py --backend docker
make build BACKEND=docker
```

The first explicit Docker invocation builds `bitbeamer-latex:local` if it does
not exist, requiring internet access for its packages. Subsequent builds
run offline with read-only source mounts. Docker Desktop supports the same
workflow on Windows and macOS. `--image NAME` or `LATEX_IMAGE` selects an
existing compatible image. A native build never invokes Docker.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| A TeX command is missing | Run `python3 scripts/build.py --setup`; install the packages listed for your platform and restart the IDE. |
| A prepared icon is stale | Follow [artwork maintenance](ASSETS.md); ordinary compilation never converts SVGs. |
| Docker is unavailable | Start Docker or use the documented native prerequisites. There is no automatic fallback. |
| An icon name is unknown | Check [the icon catalogue](../assets/CATALOGUE.md) and use the generic syntax from [the icon guide](ICONS.md). |
| Verbatim code fails | Mark its frame `[fragile]`; see [the slide guide](SLIDES.md). |

## Checks and releases

```sh
python3 scripts/check-repo.py
python3 scripts/check-docs.py
python3 scripts/build-asset-catalogue.py --check
python3 scripts/prepare-assets.py --check
python3 -m unittest discover -s tests -v
```

[The release guide](RELEASING.md) covers packaging, independent ZIP validation,
and GitHub artifacts. Use `python3 scripts/release.py` for native TeX or add
`--backend docker` explicitly. Building the extracted ZIP requires no conversion
tools or access to the source checkout.
