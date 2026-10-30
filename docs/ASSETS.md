# Maintain artwork

To insert existing icons, start with [the icon guide](ICONS.md).
This page is for adding or changing the shared library.

## Where files belong

| Location | Contents |
| --- | --- |
| `assets/characters/` | Alice, Bob, and other characters |
| `assets/objects/` | Animals, tools, devices, and buildings |
| `assets/symbols/` | Bitcoin symbols, arrows, and QR illustrations |
| `assets/backgrounds/` | Background illustrations |
| `assets/logos/` | Logos available through named icon commands |
| `assets/generated/` | Prepared files, manifest, and LaTeX registrations |
| `images/bitpolito/` | Theme logos and cover pattern, separate from the icon library |

Subfolders are welcome. Use one source per icon, such as
`assets/characters/alice.svg`. Keep names unique across all categories:
lowercase, starting with a letter, followed by letters, digits, hyphens, or
underscores. Existing asset names remain stable.

The reviewed collection contains 171 original SVGs. `assets/index.json` records
original filenames, descriptions, and identification notes. Newly added assets
appear in the generated catalogue even before descriptive metadata is added.

## Add or update an icon

1. Put the source in an input folder, outside `assets/generated/`.
2. Run the preparation and catalogue commands below.
3. Check the visual catalogue, then keep source and generated changes together.

```sh
python3 scripts/prepare-assets.py
python3 scripts/build-asset-catalogue.py
python3 scripts/build.py examples/asset-catalogue.tex
```

Commit the source artwork, prepared files, manifest, registrations, and regenerated
catalogue together when you publish the change. Do not hand-edit generated files.
Preparation removes obsolete outputs only when they were previously recorded
in its manifest; it does not delete source artwork.

Supported formats are SVG, PDF, PNG, and JPEG. SVG converts to a tightly bounded
vector PDF. PDF, PNG, and JPEG are copied without conversion. Export SVG text
as paths and embed referenced images. Transparent backgrounds are supported.
PDF page boundaries are retained; use `page=2` in an icon's options to select
another page of a multi-page PDF.

## Conversion tools

Ordinary builds and Overleaf use prepared files and need no converter.
Only SVG preparation needs either **Inkscape** or **librsvg with Python bindings**.

```sh
python3 scripts/prepare-assets.py --converter inkscape
python3 scripts/prepare-assets.py --converter rsvg
python3 scripts/prepare-assets.py --force
```

The default converter is librsvg when available, then Inkscape. `--force`
regenerates existing outputs, for example after deliberately switching converters.

Install [Inkscape](https://inkscape.org/release/) and place it on PATH, or set
`INKSCAPE` to its executable. Standard macOS and Windows install locations are
also checked. On Windows use `py -3` instead of `python3`.

For librsvg, use the system Python with these packages:

```sh
# Debian / Ubuntu
sudo apt-get install python3-gi python3-gi-cairo python3-cairo gir1.2-rsvg-2.0
# Fedora
sudo dnf install python3-gobject python3-cairo librsvg2
```

## Read-only checks

```sh
python3 scripts/prepare-assets.py --check
python3 scripts/build-asset-catalogue.py --check
```

A regular build checks prepared artwork before invoking TeX. Missing or stale
files produce regeneration instructions; compilation never converts artwork.
Packaging also checks that the complete icon catalogue is current.

## Theme artwork

Theme logos and the cover have their own sources and prepared PDFs in
`images/bitpolito/`. See [the theme artwork guide](../images/bitpolito/README.md)
for recolouring and regeneration. These files are not added to the 171-icon library.
Original filenames and source bytes are retained for provenance.
