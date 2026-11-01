# Build setup

After cloning as shown in [the README](../README.md), open a terminal in the
repository root. **Docker is the default compiler backend.** Install Python
3.10+ and Docker; local TeX packages are only needed for the native alternative.

## Docker setup (default)

1. Install Python 3 and [Docker for your platform](https://docs.docker.com/get-started/get-docker/).
2. Start Docker and confirm the terminal can access it with `docker info`.
3. Build from the repository root:

```sh
python3 scripts/build.py
```

On Windows, use `py -3 scripts/build.py` in PowerShell. Bash, Make, and WSL are
not required by the launcher. Use the platform setup required by Docker itself.

The first build prepares `bitbeamer-latex:local` from the supplied Dockerfile.
It downloads the required TeX tools, so internet access is needed and preparation
can take several minutes. Later builds reuse the image and run offline, with
read-only source files. Cloning the repository alone does not prepare an image.

To prepare or check Docker before compiling:

```sh
python3 scripts/build.py --setup
```

This can build a missing image but does not compile slides. Use `--image NAME`
or `LATEX_IMAGE` to choose an existing compatible image. After deliberately
changing the Dockerfile, rebuild it with
`docker build -t bitbeamer-latex:local .`.

Docker must be installed, running, and accessible to your user. The launcher
reports a missing daemon or executable and offers the native alternative;
it does not switch backends silently.

## Native TeX alternative

Use `--backend native` when you already have or prefer a local TeX installation.
This backend needs Python, pdfLaTeX, latexmk, and Biber and never invokes Docker.
The prepared illustration library is included, so SVG converters are optional.
The theme uses Inter Regular and Semibold; install the Inter font package and
its LY1/Greek encoding support. The commands below include these dependencies.
For an upstream TeX Live installation, use `tlmgr install inter ly1 greek-fontenc cbfonts-fd`
if they are missing; full TeX Live and MacTeX installations already include them.

### Debian / Ubuntu

```sh
sudo apt-get update
sudo apt-get install python3 latexmk texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra texlive-lang-greek \
  texlive-bibtex-extra biber
python3 scripts/build.py --backend native --setup
python3 scripts/build.py --backend native
```

### Fedora

Install TeX Live with the template's text, math, and bibliography packages:

```sh
sudo dnf install python3 latexmk biber texlive-scheme-medium \
  texlive-mathpazo texlive-palatino texlive-inter texlive-ly1 \
  texlive-greek-fontenc texlive-cbfonts-fd texlive-biblatex
python3 scripts/build.py --backend native --setup
python3 scripts/build.py --backend native
```

Alternatively, use the [TeX Live installer](https://tug.org/texlive/quickinstall.html)
and its full package scheme. If a minimal installation reports a missing
`.sty` or font, install that package through your TeX distribution.

### macOS

Install [MacTeX](https://tug.org/mactex/) and [Python 3](https://www.python.org/downloads/macos/).
MacTeX includes pdfLaTeX, latexmk, and Biber. Ensure `/Library/TeX/texbin` is
on your PATH, then restart the terminal and IDE:

```sh
python3 --version
latexmk --version
pdflatex --version
biber --version
python3 scripts/build.py --backend native --setup
python3 scripts/build.py --backend native
```

### Windows

Install [Python 3](https://www.python.org/downloads/windows/) with the Python
launcher, and [TeX Live](https://tug.org/texlive/windows.html), preferably the
full scheme. Enable its PATH integration. Restart the terminal and IDE.
In PowerShell, check and build with:

```powershell
py -3 --version
latexmk --version
pdflatex --version
biber --version
py -3 scripts/build.py --backend native --setup
py -3 scripts/build.py --backend native
```

If the TeX commands are missing, add the TeX Live `bin\windows` directory
inside your installed TeX Live version to PATH. No Bash, Make, or WSL is
required. Windows filenames and project paths may contain spaces.

## IDE workflow

Open the repository in VS Code. **Ctrl+Shift+B** builds Academic through the compatible `main.tex` entry point
with Docker. For your own talk, copy `start-academic.tex` or `start-studio.tex` to
a new root-level document. Starter tasks compile each editable example; **Build active
document** compiles the open .tex file. The separate showcase tasks retain their defaults.
Run Task also offers the separate Studio presentation, illustrations, the catalogue, icon cheat sheet, both covers,
Docker preparation, documentation checks, and an explicit native build/setup.
Windows tasks use `py -3`; Linux and macOS tasks use `python3`.

LaTeX Workshop selects **BitBeamer: Docker** by default. On Windows choose
**BitBeamer: Docker — Windows**. Native TeX Live recipes remain available and
pass `--backend native`. Document build tasks and recipes use `scripts/build.py`; review tasks use
`review.py`, which delegates compilation to that same launcher.

```sh
python3 scripts/build.py main-academic.tex
python3 scripts/build.py main-studio.tex
python3 scripts/build.py examples/assets-example.tex
python3 scripts/build.py examples/asset-catalogue.tex
python3 scripts/build.py examples/icon-cheatsheet.tex
python3 scripts/build.py examples/cover-layouts.tex
python3 scripts/build.py --force --open
```

Outputs are in `build/`. Add `--backend native` to any build to use local TeX.
With native tools installed, `latexmk -pdf main.tex` also works directly; the
launcher additionally checks whether artwork needs regeneration.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Docker is missing or unavailable | Install/start Docker and check `docker info`, or select `--backend native` after installing TeX. |
| The first build takes longer | Docker is preparing the image; subsequent builds reuse it. |
| `inter.sty` is missing | Rebuild an older Docker image with `docker build -t bitbeamer-latex:local .`; for native builds, install the Inter dependencies listed above. |
| A native TeX command is missing | Run `python3 scripts/build.py --backend native --setup`; install the listed tools and restart the IDE. |
| A prepared icon is stale | Follow [artwork maintenance](ASSETS.md); ordinary compilation never converts SVGs. |
| An icon name is unknown | Check [the catalogue](../assets/CATALOGUE.md) and [the icon guide](ICONS.md). |
| Verbatim code fails | Mark its frame `[fragile]`; see [the slide guide](SLIDES.md). |

## Checks and releases

```sh
python3 scripts/check-repo.py
python3 scripts/check-docs.py
python3 scripts/build-asset-catalogue.py --check
python3 scripts/prepare-assets.py --check
python3 -m unittest discover -s tests -v
```

[The release guide](RELEASING.md) covers packaging and independent validation.
`python3 scripts/release.py` uses Docker; `--backend native` selects local TeX.
The extracted Overleaf ZIP compiles directly with pdfLaTeX and Biber and needs
neither Docker nor Python nor artwork converters.

The default `release.py` command validates both styles. Use `--style academic`
or `--style studio` to prepare just one. See [Studio](STUDIO.md) for its separate
16:9 layout and authoring commands.

## Studio review tools

The Docker compiler includes Poppler for individual previews and the indexed review
PDF; no host installation is needed. After updating an older checkout's compiler,
rebuild the existing image with `docker build -t bitbeamer-latex:local .`.
Native review rendering additionally needs Poppler (`pdftocairo` and `pdfunite`)
on PATH; ordinary LaTeX compilation and read-only review checks do not.
On Debian/Ubuntu install `poppler-utils`; on macOS install Poppler with your package
manager. Windows users can use the Docker backend without installing these tools.
