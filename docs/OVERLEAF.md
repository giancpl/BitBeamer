# BitBeamer — Overleaf template

1. Upload this ZIP as a new Overleaf project.
2. Select **main.tex** as the main document and **pdfLaTeX** as the compiler.
3. Edit the title, author, date, and slide content. Overleaf runs Biber for citations.

The compact English showcase has 10 numbered frames and 11 PDF pages, including
one overlay. Its source comments identify columns, blocks, diagrams, formulas,
tables, code, footnotes, and navigation.

## Choose a logo pair

The default is **PoliTo + the white BitPolito bull head**. Use one declaration:

```latex
\usetheme{bitpolito}
% Alternatives:
% \usetheme[bitpolitologo=wordmark]{bitpolito}
% \usetheme[bitpolitologo=monogram]{bitpolito}
% \usetheme[group=crypto]{bitpolito}
```

The choice applies to both cover and headers. `bitpolitologo=bull` explicitly
selects the default again. All prepared logo files are included.

## Choose a cover

The default has the image on the left and left-aligned text on the right.
To place text on the left and the image on the right, use:

```latex
\usetheme[cover=image-right]{bitpolito}
% Classic: \usetheme[cover=image-left]{bitpolito}
```

Choose one theme declaration. Combine options when needed, for example
`\usetheme[cover=image-right,group=crypto]{bitpolito}`. Select
`cover-layouts.tex` as the main document to preview both orientations.

## Insert icons

```latex
\alice[height=2cm]
\cow[width=3cm]
\bitcoin[height=1cm]
\asset[width=2cm]{qrcode-one}
```

Read [the icon guide](ICONS.md) for sizing, rotation, and placement. Names with
hyphens use `\asset{name}`. Existing LaTeX commands are never overwritten.

Select another main document to explore the supplied references:

| Document | Contents |
| --- | --- |
| `cover-layouts.tex` | Two finalized cover orientations |
| `assets-example.tex` | Alice and cow usage examples |
| `icon-cheatsheet.tex` | Printable two-page icon cheat sheet |
| `asset-catalogue.tex` | All 171 icons with copyable commands |

These filenames refer to files in the release ZIP. In the source repository, the
four reference documents are under `examples/`.

## Compile or add artwork

The ZIP also works with TeX Live or MacTeX:

```sh
latexmk -pdf main.tex
```

Output: `build/main.pdf`. Document compilation needs no Python, Docker,
SVG conversion, or shell escape. To add artwork directly on Overleaf, upload
PDF, PNG, or JPEG and use `\includegraphics[width=3cm]{my-image.pdf}`.
For editable SVGs, named-command registration, and conversion tools, use the
source repository and its artwork-maintenance guide.
