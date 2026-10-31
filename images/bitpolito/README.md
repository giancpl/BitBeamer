# BitPolito assets

Original wordmark, bull and B monogram: [BitPolito/media-kit](https://github.com/BitPolito/media-kit),
commit `b7f60fce51b59c1d175917222679f8638c7d7743`.
Original SVGs are in `source/`; trimmed vector PDFs are supplied in blue and
white so compiling requires no SVG conversion. These media-kit assets
are CC0 1.0 (see `LICENSE`).

The palette comes from the local `bitpolito-slides/brand/bitpolito/tokens.json`:
primary `#001CE0`, background `#FFFFFF`, text `#10163A`, muted `#536080`,
surface `#EEF0FF`, accent `#8090FF`.

Contents and section-divider slides use a plain blue background.

The cover and frame headers pair the white Politecnico coat of arms with the
selected group logo, in that order, with space between the logos.
The default is the white BitPolito bull head beside PoliTo.
`\usetheme[group=crypto]{bitpolito}` selects CrypTO. Use
`bitpolitologo=wordmark` or `bitpolitologo=monogram` for the other BitPolito
marks; `bitpolitologo=bull` explicitly selects the default.
The artwork keeps its original proportions. `source/monogram.svg` preserves
`Icons/icon-bitpolito-b.svg` from the media kit; the generation script prepares
its blue and white PDF variants.
`polito-coat-of-arms-white.pdf` is prepared from the existing
`assets/logos/polito-coat-of-arms.svg` by `scripts/build-bitpolito-assets.py`.
The supplied CrypTO primary and secondary white PNGs are preserved in `source/`.
The same script prepares a cover logo with only the symbol and wordmark,
and a cropped header symbol
without resampling. These PDFs contain raster artwork at the original
resolution. Both logo choices are included in releases; the unused secondary
wordmark PDF remains a maintenance export.

The first-slide pattern uses `source/first-page-background.svg` as its
unchanged source. Its recoloured SVG and ready-to-use vector PDF are supplied
as `first-page-background.svg` and `first-page-background.pdf`. The default
colour is electric blue `#001CE0`; the cover's diagonal accent is pale blue
`#EEF0FF`. Change the pattern colour from the project root with:

```sh
python3 scripts/build-cover-background.py --color 001CE0
```

Use `--color 8090FF` for lilac, or another six-digit hex colour.
On Windows use `py -3` instead of `python3`. Conversion supports librsvg or
Inkscape (`--converter inkscape`). The original SVG is preserved. Unlike
individual icons, this background keeps its authored canvas; the theme crops
it to the selected left or right cover panel without stretching. Ordinary builds
and Overleaf use the supplied PDF and need no conversion tools.

To regenerate the PDFs, run `python3 scripts/build-bitpolito-assets.py` from
the project root (requires PyGObject, librsvg, and pycairo). This step is not
required for normal builds or Overleaf.

The CrypTO header uses `crypto-symbol-white.pdf`, a clipped excerpt of the
primary source PNG containing just the symbol. The original pixels are embedded
without resampling. The cover pairs this symbol with the supplied standalone
CrypTO wordmark, omitting the Italian subtitle from the rendered slides. Header logos
have a shared height and a slightly wider gap. Cover logos and text share one
left edge: at 47.5% of the page width for
`cover=image-left`, or 6% for `cover=image-right`. Both use a text width of
46.5% of the page and adapt to 16:9 and 4:3.

The closing slide uses `bitcoin-white.pdf`, prepared from
`assets/symbols/bitcoin/bitcoin.svg` by `scripts/build-bitpolito-assets.py`.
Its plain frame fills the page in electric blue and centers the white icon
and closing text as one group. The prepared PDF is included in Overleaf releases.
