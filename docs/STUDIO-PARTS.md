# Studio graphical parts

Use the [single offline parts gallery](studio-parts/index.html) to browse all
897 prepared parts, including the 22 parts from the initial measured frames.
They are shared by the current slide sources; there is no separate pilot library.

```latex
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
% Inside a normal frame:
\studiopart[width=2cm]{protocol-alice}
\studiopart[width=3cm]{figma-0032-part-01}
```

Sizing preserves proportions. Card panels include their original shadows and
fixed background colours. The command finds prepared PDFs in both artwork folders.
Ordinary compilation requires no converter.

The [initial-parts manifest](../images/studio/parts/manifest.json) and
[expanded-parts manifest](../images/studio/collection/manifest.json) retain source
regions, dependencies and hashes. Derived SVGs and original raster resources
allow maintenance without exporting the full Figma frames again.

```sh
python3 scripts/studio_parts.py check
python3 scripts/studio_collection.py check
python3 scripts/catalogue-studio-collection.py --previews
```

Use `prepare` instead of `check` after changing artwork. Add
`--converter inkscape` to choose that converter. See [artwork maintenance](ASSETS.md)
and [the collection workflow](STUDIO-COLLECTION.md) for extraction and review.

The partner rail also retains its panel, five independent logos and two contact
symbols as vector parts. See [replacement commands](STUDIO-PARTNER-RAIL.md).
