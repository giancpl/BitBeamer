# Use a Studio slide

For consistent text, icon and image customization, use the [typed content API](STUDIO-CONTENT.md).

Studio has 194 current compositions. Start with the 24 selected layouts;
every composition has a [usage guide](templates/GUIDES.md) and one editable source.
The collection compiles locally and remains in graphical review.

## 1. Choose a layout

Open [the visual gallery](templates/index.html). Select a family or search a
layout name. Choose **Open slide** to inspect one composition at a time, or
**Usage guide** for its copyable examples and field table.

In the individual view, enable **Show editable areas** or select a field. The
coloured outlines locate its allocated box; they are guide overlays and never
appear in your PDF. Some graphics combine a panel, image and decoration into one
replaceable part. Native shapes and QR codes may require a source edit.

Gallery previews stay lightweight. Use the vector review PDF or the 2000px images
in the local comparison gallery when checking fine graphical details.

The [guide index](templates/GUIDES.md) groups every layout by family and lists the
24 selected layouts first. Compatibility names lead to the same current source.

## 2. Create your document

Start from [start-studio.tex](../start-studio.tex), an editable four-slide document
that is never regenerated. It demonstrates a cover, ordinary frame, cards and closing:

```sh
cp start-studio.tex my-slides.tex
python3 scripts/build.py my-slides.tex --open
```

On Windows use `Copy-Item start-studio.tex my-slides.tex` and replace `python3`
with `py -3`. Keep your document at the repository root beside the theme files.
Change title, author and institute, then replace the example frames.
For measured templates, use the following complete alternative:

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\usepackage[backend=biber]{biblatex}
\addbibresource{bibliography.bib}
\begin{document}

\studiotemplate[
  title={Your talk\\title},
  author={Your name},
  institute={Your institute}
]{cover}

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

Every `\studiotemplate` inserts a complete frame. Place it outside another
`frame` environment. You can repeat a layout with different field values;
each call starts with its own defaults. A guide's **Complete one-slide example**
is also ready to paste into a new root-level document.

## 3. Build and inspect

With the [documented prerequisites](SETUP.md) installed:

```sh
python3 scripts/build.py my-slides.tex
# With installed TeX Live or MacTeX:
python3 scripts/build.py my-slides.tex --backend native
```

Output: `build/my-slides.pdf`. On Windows use `py -3` instead of `python3`.
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
reports overflow, shorten the text or change the source geometry deliberately.
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

Open a single slide from the gallery and review its margins, hierarchy, text,
crops and effects. Use the stable model ID when adding comments to
[REVIEW.csv](../templates/REVIEW.csv). The source comparison workflow is in
[the collection guide](STUDIO-COLLECTION.md). A successful build does not approve
the graphical result.

For content changes, edit the options in your document. For a shared layout
improvement, edit `templates/studio/<name>.tex` and its field metadata in
`templates/index.json`. There is one implementation per composition; the
showcase, catalogues and usage guides reuse it.

Refresh generated guides and indices with:

```sh
python3 scripts/build-studio-catalogue.py
python3 scripts/check-docs.py
```

If the layout or its default content changed, rebuild its catalogue/previews as
described in [the maintenance workflow](STUDIO-COLLECTION.md). Ordinary slide
writing needs no regeneration or conversion. Guides are generated files; change
the field metadata or `scripts/studio_guides.py` instead of editing 194 pages.
