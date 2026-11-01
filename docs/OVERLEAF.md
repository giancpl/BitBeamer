# BitBeamer Academic — Overleaf template

1. Upload `bitbeamer-academic-overleaf.zip` (legacy alias: `bitbeamer-overleaf.zip`) as a new Overleaf project.
2. Select **main.tex** as the main document and **pdfLaTeX** as the compiler.
3. Edit the title, author, date, and slide content. Overleaf runs Biber for citations.

For a shorter editable document, select `start.tex` as the main document. It includes
a cover, ordinary frames, an illustration and a closing slide. `main.tex` is the full showcase.

The default typeface is Inter, with Regular body text and Semibold headings.
It uses the TeX distribution's Inter package with pdfLaTeX.

This is **BitBeamer Academic**. **BitBeamer Studio** is a separate download,
`bitbeamer-studio-overleaf.zip`. The legacy `\usetheme{bitpolito}` also selects
Academic.

The compact English showcase has 10 numbered frames and 11 PDF pages, including
one overlay. Its source comments identify columns, blocks, diagrams, formulas,
tables, code, footnotes, and navigation.

## Choose a logo pair

The default is **PoliTo + the white BitPolito bull head**. Use one declaration:

```latex
\usetheme{bitpolito-academic}
% Alternatives:
% \usetheme[bitpolitologo=wordmark]{bitpolito-academic}
% \usetheme[bitpolitologo=monogram]{bitpolito-academic}
% \usetheme[group=crypto]{bitpolito-academic}
```

The choice applies to both cover and headers. `bitpolitologo=bull` explicitly
selects the default again. All prepared logo files are included.

## Choose a cover

The default has the image on the left and left-aligned text on the right.
To place text on the left and the image on the right, use:

```latex
\usetheme[cover=image-right]{bitpolito-academic}
% Classic: \usetheme[cover=image-left]{bitpolito-academic}
```

Choose one theme declaration. Combine options when needed, for example
`\usetheme[cover=image-right,group=crypto]{bitpolito-academic}`. Select
`cover-layouts.tex` as the main document to preview both orientations.

## Add the closing slide

Insert `\closingframe` before `\end{document}`, outside any frame. It creates
the standard blue closing slide with white text and the current-year copyright.
Use `\closingframe[title={Thank you!},subtitle={Questions?},copyright={}]`
to customize the text or hide the copyright.

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
