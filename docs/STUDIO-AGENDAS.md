# Studio agendas: four or five items

Two plain panel layouts are selected from the original Figma collection. They keep
the light background, blue Semibold text, rounded outlines and cropped gradient
panels at the top and bottom. Icon lists and schedules remain separate alternatives.

| Capacity | Model variant | Current source | Original references |
| --- | --- | --- | --- |
| Four items | `panels` | [contents.tex](../templates/studio/contents.tex) | `figma-0575` |
| Five items | `panels-five` | [contents-five.tex](../templates/studio/contents-five.tex) | `figma-0883`, same geometry as `figma-0589` |

Both use Inter and their original light palette. No opposite-colour version is generated.
The original canvases are 1920 × 1080 and 3556 × 2000 respectively; each composition
uses one uniform scale. The title text area extends into the empty left column to
accommodate English headings while retaining its anchor and font size.

## Use actual section names

Load the Studio theme and catalogue package in the preamble:

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\begin{document}

\studiotocframe[variant=panels,title={Contents}]
% Use variant=panels-five when you have five sections.

\section{Introduction}
\studioframe{Introduction}{Your content.}
\section{First concept}
\studioframe{First concept}{Your content.}
\section{Second concept}
\studioframe{Second concept}{Your content.}
\section{Next steps}
\studioframe{Next steps}{Your content.}

\end{document}
```

The launcher and Overleaf repeat compilation to populate section titles. Subsections
and subsubsections are ignored. All top-level section declarations are collected.
Unused slots remain empty; more than four/five sections produces an explicit error.
The existing `\studiotocframe` without `variant` retains its flexible automatic layout
and does not require the catalogue package. Each call resets its options.

## Write the agenda manually

```latex
\studiotemplate[variant=panels,title={Contents},
  item-one={Introduction},item-two={First concept},
  item-three={Second concept},item-four={Next steps}
]{agenda}

\studiotemplate[variant=panels-five,title={Contents},
  item-one={Introduction},item-two={First concept},
  item-three={Second concept},item-four={Examples},item-five={Next steps}
]{agenda}
```

Fields accept LaTeX. `item-five` is available only in `panels-five`; using it on the
four-item template is an error. Omitted fields retain descriptive defaults. Use
`item-two={}` for empty text while keeping the panel. Font sizes and positions are
fixed; overlong content reports overflow instead of shrinking. Keep each item to
one short line. The legacy `\studiotemplate{contents}` and its numbered/old fields
remain available.

## Inspect and refine

[studio-agendas.tex](../examples/studio-agendas.tex) contains both neutral layouts
and retained English content examples. Copy a command to your document or build:

```sh
python3 scripts/build.py examples/studio-agendas.tex build/review/agendas
python3 scripts/review.py slide contents --open
python3 scripts/review.py slide contents-five --open
```

The first command produces `build/review/agendas/studio-agendas.pdf`. On Windows
use `py -3`; add `--backend native` for installed TeX. Complete-frame commands go
outside any surrounding `frame` environment.

Both layouts and their prepared graphics are included in the main Studio Overleaf
review ZIP. Custom subset exports must include the variants they use. No converters
or original Figma exports are needed for ordinary compilation. All templates remain
in review; selection does not imply graphical approval.
