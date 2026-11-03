# Studio content API

Start with [grouped models, variants and palettes](STUDIO-MODELS.md). The advanced composition API remains compatible.

Use one interface across all 195 Studio compositions. Copy a complete example
from an [individual guide](templates/GUIDES.md), or start with the
[customization examples](../examples/studio-customization.tex).

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\begin{document}
\studiotemplate[
  text/title={Your concepts},
  text/caption-one={Learn},
  text/caption-two={Build},
  text/caption-three={Share},
  icon/1={alice},
  icon/2={cow},
  icon/3={bitcoin}
]{three-cards}
\end{document}
```

The command creates a complete slide; place it outside a `frame` environment.
Select pdfLaTeX on Overleaf. Locally, compile with the documented Python launcher.
No artwork conversion is needed. A subset download contains only the models
listed in its own guide; its `customization.tex` adapts to those models. Some
examples below refer to models in the complete repository.

## Syntax

| Key | Value | Result |
| --- | --- | --- |
| `text/N` | LaTeX text | Changes a fixed text box. |
| `text/name` | LaTeX text | Names the same box by its existing field, such as `text/title`. |
| `icon/N` | Catalogue name, such as `alice` | Fits the prepared icon into graphic slot N. |
| `image/N` | Project-relative PDF, PNG or JPEG path | Fits your image into the same slot. |
| `graphic/N` | A graphic command, TikZ, QR code or math | Fits supplied LaTeX graphics into the same slot. |
| `heading/N`, `body/N` | LaTeX text | Edits a structured text block without losing its heading/detail hierarchy. |
| `file/N` | Project-relative filename | Changes a declared code or data input. |
| `clear=text` | Literal keyword | Removes shipped text before applying your explicit text values. |

`N` is a positive slot number local to the model. Text, graphics and file inputs
have separate numbering. Initial numbering follows reading order; stored numbers
remain stable when a layout is refined. A model with no graphics has no graphic,
icon or image keys. Only measured mixed-text blocks expose heading/body keys.

The individual guide lists every supported key and its position. The visual
field map labels the same numbered slots. Numbered and named keys are aliases:
`text/1` and `text/title` refer to the same field in `three-cards`.
`icon/1`, `image/1` and `graphic/1` address one shared graphic slot. If you supply
several values for that slot, the last one wins.

Names are case-sensitive. Brace every value, especially when it contains commas,
line breaks or LaTeX commands. All existing unscoped field names and template
compatibility names continue to work.

## Start with your own copy

```latex
\studiotemplate[
  clear=text,
  text/title={Your concepts},
  text/caption-one={Learn},
  icon/1={alice}
]{three-cards}
```

Omitted fields retain their shipped defaults. `clear=text` removes those defaults
for text only; it preserves artwork, logos, panels and diagrams. Explicit values
are applied after clearing, regardless of where `clear=text` appears in the
options. You can also hide one field with `text/2={}` or `icon/1={}`. Every anchor
and neighbouring element stays in place. For a separated card slot, an empty
icon keeps the panel and shadow.

## Swap icons and images

```latex
\studiotemplate[
  text/1={People}, text/2={Bitcoin},
  icon/1={alice}, icon/2={bitcoin}
]{two-cards}

\studiotemplate[image/1={assets/generated/cow.pdf}]{image-left}

\studiotemplate[graphic/2={\cow}]{three-cards}
```

The slot supplies width, height, centre and padding. Graphics scale uniformly
and keep their aspect ratio; no image is stretched. Separated icon-card slots
retain their original rounded panel, shadow and content centre. Their safe
inner area is 65% of the original square panel. Other graphic slots use their documented measured safe area and replace their
complete graphic, as identified in the field guide.
A slot can contain a whole diagram, screenshot, background or decoration; do not
assume every graphic is an isolated icon.

Use an asset name without a leading backslash for `icon/N`. Use `graphic/N` when
you want a command such as `\alice`, `\studiopart` or `\qrcode`. Images and literal graphic commands retain their colours. Named monochrome icons use prepared
Studio alternatives on blue slides; the shared asset library itself stays unchanged.
Only graphics are fitted. Text is never scaled to make it fit. On blue slides,
choose artwork with enough contrast. Prepared white character variants can be
used with `image/1={images/studio/alice-white.pdf}` (also `bob-white.pdf` and
`pig-white.pdf`); the ordinary `alice` icon keeps its original blue ink.

## Preserve heading and detail sizes

The practical-checklist model has structured step blocks:

```latex
\studiotemplate[
  clear=text,
  text/title={Your checklist},
  heading/1={Choose hardware},
  body/1={Use a device that meets your needs.},
  heading/2={Install software},
  body/2={Follow the official project instructions.}
]{checklist-rail}
```

A heading/body pair shares the number of its text box; the slide title can appear
between step boxes in reading order, so consult the map for subsequent numbers.
Named aliases such as `heading/text-2` are available too. Editing one component
preserves the other component's default, unless you use `clear=text`.
`text/N` remains available for replacing the complete mixed box with advanced
LaTeX content.

For bullet lists, use a structured helper inside a normal text slot:

```latex
\studiotemplate[
  text/2={\studiolist{{First point},{Second point},{Third point}}}
]{title-two-column-list}
```

Each braced item keeps commas and LaTeX markup together. The list inherits the
slot's text font and colour and uses hanging bullets.

## Files and advanced content

```latex
\studiotemplate[file/1={examples/code/studio-transaction.txt}]{code}
\studiotemplate[file/1={examples/data/studio-line.csv}]{line-chart}
```

Code files are typeset literally. Chart data uses CSV columns `x,y`; update its
labels as well as its values. Table, equation and native-diagram labels use their
documented text slots. Text inside an imported screenshot remains part of that
image; replace the image to change it.

## Keep the visual identity

Changing content preserves the model's palette, Inter font, type hierarchy,
alignment, geometry and decorative layers. Unknown keys, missing assets and
text overflow produce diagnostics identifying the model and affected field.
Keep titles concise and use deliberate `\\` line breaks. Shorten copy when it
exceeds a measured box. For structural changes, edit the current model source
rather than adding font-size or placement overrides to ordinary slide content.

Compile `examples/studio-customization.tex` to see the API in use. After editing
a library layout, refresh and inspect its comparison before approving it.
