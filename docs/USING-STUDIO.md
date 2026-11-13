# Use a Studio slide

For a new deck, follow [the authoring workflow](AUTHORING.md).
Start with [grouped models, variants and palettes](STUDIO-MODELS.md). The advanced composition API remains compatible.

For consistent text, icon and image customization, use the [typed content API](STUDIO-CONTENT.md).

Studio groups retained compositions into named models. Start with the featured models;
every composition has a [usage guide](templates/GUIDES.md) and one editable source.
The collection compiles locally and remains in graphical review.

## Two ways to start

- [Reusable layouts](../templates/REUSABLE.md): neutral fields for a new presentation;
  the initial shortlist contains title, contents and closing.
- [Ready-content examples](../templates/EXAMPLES.md): retained English content and
  original graphic parts, with the same editable layouts. Historical facts and
  figures are examples to check before use.

To inspect the same slide with its retained example content:

```sh
python3 scripts/review.py slide three-cards --content example --open
```

Omit `--content example` for neutral defaults. Neither mode changes the composition,
its native palette or approval status. The two catalogues share sources; original
Figma exports remain optional local comparisons.

## 1. Choose a layout

Open [the slide guide](slides/index.html). Select a family or search a
layout name. Open the preview to inspect one composition at a time, or
**Field guide** for its copyable examples and field table.

In the individual view, enable **Show editable areas** or select a field. The
coloured outlines locate its allocated box; they are guide overlays and never
appear in your PDF. Some graphics combine a panel, image and decoration into one
replaceable part. Native shapes may require library maintenance; the [standard closing QR](STUDIO-CLOSING.md) has a boolean option.

Thumbnails are 640 px; opening the detail loads the 1600 px full-canvas preview.
Optional local original comparisons are in the same guide with `?maintenance=1`;
see [maintenance](STUDIO-COLLECTION.md).

The [guide index](templates/GUIDES.md) groups every layout by family and lists the
24 selected layouts first. Compatibility names lead to the same current source.

## 2. Create your document

Start from [start-studio.tex](../start-studio.tex), an editable six-slide document
that is never regenerated. It includes a cover, team introduction, automatic contents, two content
slides and a closing page:

```sh
python3 scripts/deck.py new my-talk
python3 scripts/deck.py build my-talk --open
```

On Windows replace `python3` with `py -3`. Edit
`presentations/my-talk/main.tex` and complete its brief. Each deck has its own assets,
bibliography and output directory; see [authoring](AUTHORING.md) for paths.
Change title, author and institute, then replace the example frames.
The cover is classic blue by default. Choose `\studiotitleframe[variant=bitgeneration]`
for the light lettering cover or `variant=bitgeneration-photo` for the photographic
version. Both use the same title, author and institute; see [cover options](STUDIO.md#choose-the-cover)
for title limits and available metadata.
For measured templates, use the following complete alternative:

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\usepackage[backend=biber]{biblatex}
\addbibresource{bibliography.bib}
\title{Your presentation}
\author{Your name}
\institute{Your institute}
\date{}
\begin{document}

\studiotitleframe
\studioteamframe % Check and replace the example team data.
\studiotocframe
\section{First ideas}

\studiotemplate[
  title={Three useful tools},
  caption-one={Learn},
  caption-two={Build},
  caption-three={Share},
  graphic-one={\asset[width=1cm]{alice}}
]{three-cards}

\closingframe[title={Thank you!},subtitle={Questions?}]
\end{document}
```

The standard cover, contents, base content and closing commands are described in
[Studio standard pages](STUDIO.md#standard-pages-and-the-default-frame). Every
`\studiotemplate` inserts a complete frame. Place it outside another
`frame` environment. You can repeat a layout with different field values;
each call starts with its own defaults. A guide's **Complete one-slide example**
is also ready to adapt inside your document; use deck-local paths for additional inputs.

## 3. Build and inspect

With the [documented prerequisites](SETUP.md) installed:

```sh
python3 scripts/deck.py build my-talk
# With installed TeX Live or MacTeX:
python3 scripts/deck.py build my-talk --backend native
```

Output: `build/presentations/my-talk/main.pdf`. Run `deck.py check my-talk --preview` before delivery. On Windows use `py -3` instead of `python3`.
Docker is the default backend. VS Code and LaTeX Workshop use the same launcher.
The current showcase is `main-studio.tex`; `make studio` builds it.

For an extracted Overleaf project, create the .tex file at the project root,
select it as the main document and use pdfLaTeX. Use the per-slide guides shipped
inside that project; they list only the included models. Compilation requires
no Python, SVG converter or shell escape.

## 4. Change text, images and data

Use the exact field names shown in the guide. Names such as `text-2` identify
specific fixed boxes; the field map shows where each one belongs. Omitted fields
retain their default content. `title={}` hides a title without moving anything.
Protect values with braces, especially commas, math and multiline LaTeX.

Keep text within its box. Use `\\` for an intentional line break. If the log
reports overflow, shorten the text, split the content or choose another composition.
Fonts and anchors do not shrink or move automatically.

Graphic fields accept `\asset`, `\includegraphics`, TikZ and math. Each guide
provides a replacement example sized conservatively for one actual graphic slot.
Keep `keepaspectratio` when setting both width and height. Graphic colours remain
part of the artwork; changing the surrounding text colour does not recolour it.
See [the icon guide](ICONS.md) for shortcuts and hyphenated names.

The [code guide](templates/guides/code.md) explains `code-file`;
[the chart guide](templates/guides/line-chart.md) explains `data-file` and the
`x,y` CSV format. Paths are relative to the project root. Code is displayed,
not executed, and example chart values are illustrative. The
[bibliography guide](templates/guides/references.md) covers references.

## 5. Review and refine a composition

Open a single slide from the guide and review its margins, hierarchy, text,
crops and effects. Use the stable composition ID when adding comments to
[review.json](../templates/review.json). The CSV sheet is a generated export. The source comparison workflow is in
[the collection guide](STUDIO-COLLECTION.md). A successful build does not approve
the graphical result.

For content changes, edit the options in your document. For a shared layout
improvement, edit `templates/studio/<name>.tex` and its field metadata in
`templates/index.json`. There is one implementation per composition; the
showcase, catalogues and usage guides reuse it.

Refresh generated guides and indices with:

```sh
python3 scripts/review.py sync
python3 scripts/check-docs.py
```

If the layout or its default content changed, rebuild its catalogue/previews as
described in [the maintenance workflow](STUDIO-COLLECTION.md). Ordinary slide
writing needs no regeneration or conversion. Guides are generated files; change
the field metadata or `scripts/studio_guides.py` instead of editing 196 pages.
