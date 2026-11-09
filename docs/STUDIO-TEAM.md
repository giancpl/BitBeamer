# Studio team introduction

Use the team slide immediately after the cover and before the contents page:

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\title{Your presentation}
\author{Author name}
\institute{Organization}
\date{}
\begin{document}
\studiotitleframe
\studioteamframe
\studiotocframe[variant=panels]
\section{Introduction}
\studioframe{Introduction}{Your content.}
\closingframe
\end{document}
```

The team page is explicit, so it never appears automatically in an unrelated deck.
Remove the `\studioteamframe` line when it is not needed. Complete-frame commands
must be outside another `frame`. Academic does not load this layout.

## Update the statistics

```latex
\studioteamframe[
  value-one={50+},caption-one={Active members},
  value-two={210},caption-two={Alumni},
  value-three={8000+},caption-three={Followers on social media},
  value-four={25+},caption-four={Working in Bitcoin}
]
```

These figures are copied from the supplied team slide, not live statistics. Update
them before presenting. Each value and caption accepts LaTeX; an empty field, such
as `value-two={}`, keeps its original space. Values and captions use Inter Semibold, with distinct sizes
matching the source's hierarchy. Keep values and captions to
one short line. Font sizes and positions are fixed; overflow is reported.
Unknown fields are errors. Options do not carry over into later frames.

The equivalent reusable model is:

```latex
\studiotemplate[variant=collage,
  value-one={50+},caption-one={Active members},
  value-two={210},caption-two={Alumni},
  value-three={8000+},caption-three={Followers on social media},
  value-four={25+},caption-four={Working in Bitcoin}
]{team}
```

The catalogue model uses the generic fourth caption **Industry members**. The
team helper and ready-content example use the supplied **Working in Bitcoin**.
The compatibility composition ID is `team-presentation`. The original supports
only the light palette; an explicitly requested blue palette produces an error.

## Replace the collage

```latex
\studioteamframe[image-one={images/my-team.pdf}]
```

The image slot occupies the left 988 × 1080 source units, including the wordmark.
An image is fitted proportionally and centred; prepare the same aspect ratio to
fill the slot exactly. The right panel decoration stays in place. Advanced users
can provide LaTeX artwork through `graphic-one={...}` or edit the
[current layout source](../templates/studio/team-presentation.tex).

The default collage preserves the supplied posters, photographs, badges, QR and
lettering. Text inside those illustrations belongs to the artwork; it is not a
separate LaTeX text field. Replace the collage to change it. Original poster text
is retained as artwork; the template's authored content and documentation are English.

## Source and review

The reference is the user-supplied `team-presentation.pdf`, one 1920 × 1080 page.
The cropped collage sits over a continuous full-canvas vector background, avoiding
a differently rendered strip between the images and panels. Both parts preserve
their source coordinates and crop with a single
uniform scale. The decorative outlines, masks, edge fades and original images
are retained as PDF parts; four values and four captions are rebuilt as selectable
LaTeX text. Inter replaces SF Pro in those editable fields. No full-slide bitmap
is embedded.

[Artwork provenance](../images/studio/team/manifest.json) records the input hash,
exact crop boxes and prepared-part hashes. The retained PDF parts are their own
vector sources; ordinary builds and Overleaf need no original Figma export,
Python PDF library, converter or shell escape. A maintenance-only importer can
re-extract them from the same reference; see the [artwork notes](../images/studio/team/README.md).
The current composition was explicitly **approved** by the user on 2026-11-06
after the continuous-background correction. This is graphical approval; verify
the editable example figures before presenting.

Copy [the complete example](../examples/studio-team.tex), or build one slide:

```sh
python3 scripts/review.py slide team --open
python3 scripts/build.py examples/studio-team.tex build/review/team
```

The latter produces `build/review/team/studio-team.pdf`. On Windows use `py -3`;
add `--backend native` for installed TeX Live/MacTeX. The main Studio review ZIP
includes this template and its prepared artwork; a custom subset needs the
`team-presentation` composition (or the `team` model).
