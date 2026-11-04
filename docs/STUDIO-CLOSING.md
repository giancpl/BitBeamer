# Studio closing and optional QR

The standard ending uses a blue background, white `@BitPolito` handle, the four
social icons and a top-centred copyright. The QR from the supplied `final-slide.pdf`
is visible by default. It is the original QR artwork, not a catalogue example.

```latex
\closingframe                 % Same as qrcode=true.
\closingframe[qrcode=true]    % QR on the left; text and social icons on the right.
\closingframe[qrcode=false]   % No QR; text and social icons centred on the slide.
```

Use this sequence in [the editable starter](../start-studio.tex): cover, team,
contents, content frames and closing. Each command creates a complete frame:

```latex
\studiotitleframe
\studioteamframe
\studiotocframe
% Your sections and content frames go here.
\closingframe
```

The team command requires `bitpolitostudiotemplates`; `\closingframe` needs only
the Studio theme. Academic retains its separate closing behaviour.

## Change the content

```latex
\closingframe[
  qrcode=true,
  title={@YourHandle},
  subtitle={Questions?},
  copyright={\textcopyright{} 2026 Your organization}
]
```

The defaults are `title={@BitPolito}`, `subtitle={}`, the current-year BitPolito
copyright and `qrcode=true`. Empty text fields hide that element. Each call resets
all defaults, so disabling the QR on one page does not disable it on the next.
Only `true` and `false` are valid boolean values; other values produce an explicit
error. Text boxes keep their fixed Inter sizes and report overflow.

Title, optional subtitle and copyright are selectable LaTeX text. Original social
icons, outlined panels and the QR are prepared PDF parts. The source proportions,
spacing and blue treatment come from the supplied 1920 × 1080 reference. The QR-off
version centres the same content group without resizing it.

## Use another QR

```latex
\closingframe[qr-image={images/my-qr.pdf}]
```

Use a square PDF or high-resolution PNG with a quiet border. The image is fitted
proportionally in the original QR box and is not recoloured. It must have sufficient
contrast against blue, or contain its own contrasting background. When `qrcode=false`,
the QR image is not loaded or embedded. No QR generation or SVG conversion is needed.

## Use the catalogue model

The measured catalogue and `\closingframe` share one layout implementation:

```latex
\studiotemplate[qrcode=true,title={@YourHandle},copyright={}]{closing}
\studiotemplate[qrcode=false,title={Thank you}]{closing}
```

The catalogue keeps its neutral `Thank you` title. Existing text/graphic fields and
numbered slots remain compatible. `subtitle` is an additional text field; `qrcode`
is a strict boolean option, not a text slot. `image-five` or `image/5` replaces the
QR image; `graphic-one` through `graphic-four` replace the social icons together
with their outlined panels. Empty graphic fields keep their allocated space.

```latex
\studiotemplate[qrcode=true,image-five={images/my-qr.pdf}]{closing}
```

For structural changes, edit [the Studio inner theme](../beamerinnerthemebitpolito-studio.sty).
[The catalogue adapter](../templates/studio/closing.tex) supplies editable fields;
it does not duplicate the drawing code.

## Preview and maintenance

[studio-closing.tex](../examples/studio-closing.tex) compares QR on, QR off,
custom text, the catalogue API and the return to a normal frame:

```sh
python3 scripts/build.py examples/studio-closing.tex build/review/closing
```

This creates `build/review/closing/studio-closing.pdf`. On Windows use `py -3`;
add `--backend native` for installed TeX. The Studio Overleaf ZIP includes these
examples and all prepared closing parts. No source PDF, converter or PDF-processing
library is needed for ordinary compilation.

[Artwork provenance](../images/studio/closing/manifest.json) records the original
hash and crops. The QR retains its original JPEG stream and alpha mask without
recompression; social artwork remains vector. See [the extraction notes](../images/studio/closing/README.md)
for the maintenance-only importer. The updated design remains in review.
