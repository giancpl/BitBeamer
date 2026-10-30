# Use icons in slides

The theme loads all 171 illustrations automatically. No SVG conversion is
needed to use the prepared artwork. See the [full catalogue](../assets/CATALOGUE.md)
for every name, description, and copyable command.

For a printable reference, build [the two-page cheat sheet](../examples/icon-cheatsheet.tex):

```sh
python3 scripts/build.py examples/icon-cheatsheet.tex
```

Output: `build/icon-cheatsheet.pdf`. Releases also provide
`bitbeamer-icon-cheatsheet.pdf`.

## Start with a shortcut

```latex
\alice[height=2cm]
\bob[height=2cm]
\cow[width=3cm]
\bitcoin[height=1cm]
\wallet[width=2cm]
\coin[height=1cm]
```

Without options, an icon is 2.5 cm wide. These shortcuts insert the blue
library artwork; choosing a white theme logo does not recolour slide icons.

## Use any icon by name

```latex
\asset[width=2cm]{alice-and-bob}
\asset[height=1.5cm]{qrcode-one}
\asset[height=1cm,angle=15]{key}
```

`\asset[options]{name}` works for every registered icon. Names with hyphens,
digits, or underscores use this form. Letter-only names get a shortcut only
when that command is not already defined. The library never overwrites an
existing LaTeX command. `\bitpolitoasset` is the unambiguous generic entry point.

## Size and align

Standard `\includegraphics` options are accepted. Set a width or height;
setting both fits the artwork inside that box while preserving proportions.

```latex
\cow[width=0.25\textwidth]
\asset[width=2cm,height=1cm]{cow}
Pay with \raisebox{-0.15\height}{\bitcoin[height=1em]} Bitcoin.
```

To align a pair, give both the same height:

```latex
\begin{columns}[c,onlytextwidth]
  \begin{column}{0.45\textwidth}
    \centering
    \alice[height=2cm]
  \end{column}
  \begin{column}{0.45\textwidth}
    \centering
    \bob[height=2cm]
  \end{column}
\end{columns}
```

## Colour and missing artwork

Prepared PDFs retain their artwork colours. `\textcolor` does not recolour
an imported icon. For another colour, prepare a separate artwork variant;
see [artwork maintenance](ASSETS.md).

A missing name or file produces a visible placeholder and compile warning.
Check the catalogue spelling first. In a clone, run
`python3 scripts/prepare-assets.py --check` to check prepared files without
changing anything. After editing source artwork, follow the regeneration steps
in the maintenance guide. On Overleaf, upload the prepared PDF rather than a raw SVG.

## Use the library without the theme

Copy `bitpolitoassets.sty` and `assets/generated/` beside your document, then use:

```latex
\usepackage{bitpolitoassets}
```

If the prepared files live elsewhere, define `\bitpolitolibrarypath` before
loading the package. For ordinary slides, use the supplied folder layout.
