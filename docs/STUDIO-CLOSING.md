# Studio closing and optional QR

The Studio closing has one composition: blue background, editable `@BitPolito`,
five social marks (Telegram, Instagram, X, GitHub and YouTube), top-centred
copyright and QR enabled by default. Its geometry and typography are calibrated
to page 11 of the supplied BitPolito introduction. Inter remains selectable text;
its glyph design intentionally differs from the original outlined font.

```latex
\closingframe
\closingframe[qrcode=false]
\studiotemplate{closing}
\studiotemplate[qrcode=false]{closing}
```

There is no social-count selector or four-social layout. Disabling the QR centres
the same handle/social group without changing its typography or icon sizes.
Every call resets its defaults. Academic retains its separate closing behaviour.

## Editable content

```latex
\closingframe[
  title={@YourHandle},
  subtitle={Questions?},
  copyright={\textcopyright{} 2026 Your organization},
  qr-image={images/my-qr.pdf}
]
```

Empty text fields hide that element. The QR is fitted proportionally without
recolouring; with `qrcode=false` its image is not loaded. Only `true` and `false`
are valid QR values. Text boxes retain fixed Inter sizes and report overflow.

The handle uses Inter Medium; the copyright uses Inter Regular. Their separately
measured sizes and letter spacing are applied only inside the closing text boxes. This calibration does not change typography
in other frames. Custom text keeps the same style; shorten or split overflowing
copy instead of reducing the font.

## Catalogue fields

```latex
\studiotemplate[title={@YourHandle},copyright={}]{closing}
\studiotemplate[image-five={images/my-qr.pdf}]{closing}
```

Existing numbered fields remain compatible: `graphic-one`, `graphic-two` and
`graphic-three` replace Telegram, Instagram and X; `graphic-four` remains YouTube;
`image-five` replaces the QR; `github-graphic` or `graphic-six` replaces GitHub.
Graphic replacements include their panels. Empty graphics retain their space.

`\closingframe` requires only the Studio theme; the catalogue command also needs
`bitpolitostudiotemplates`. The optional clone-only `bitpolito-contact` alias uses
the same closing implementation and the introduction's prepared QR.

## Maintenance

The shared implementation is [layout.tex](../images/studio/closing/layout.tex).
The [catalogue adapter](../templates/studio/closing.tex) supplies fields; the
[Studio inner theme](../beamerinnerthemebitpolito-studio.sty) loads the component.
Keep it in standalone and subset exports. No Python, SVG converter or original
reference PDF is needed for ordinary compilation.

[studio-closing.tex](../examples/studio-closing.tex) exercises QR on/off, custom
copy and the catalogue API. Build it with:

```sh
python3 scripts/build.py examples/studio-closing.tex build/review/closing
```

The [artwork notes](../images/studio/closing/README.md) retain crop and provenance
information. The final five-social closing was explicitly approved on 2026-11-09. Its QR
remains a boolean option, enabled by default; subsequent graphical changes require
a new review.
