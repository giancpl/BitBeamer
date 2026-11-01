# Studio artwork

The three white icon variants are derived from the existing Alice, Bob,
and pig SVGs in the illustration library. Originals and public icon names are
unchanged. `source/` keeps the derived SVGs, prepared PDFs are ready to compile,
and `manifest.json` records source and output hashes.

Regenerate with `python3 scripts/prepare-studio-assets.py`; use `--check` for a
read-only freshness check. Conversion uses the same librsvg/Inkscape tools as
[the main artwork workflow](../../docs/ASSETS.md). Compiling slides needs neither.
The illustration provenance in [the asset guide](../../docs/ASSETS.md) also
applies to these colour variants.

The fourth derivative, `cover-pattern-white.pdf`, recolours only the pattern
paths and preserves the authored canvas and transparent background. Its source
is the original cover SVG. Academic retains its existing blue pattern.
