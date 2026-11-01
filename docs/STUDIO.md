# BitBeamer Studio

Studio is the visual design for workshops and public talks. **BitBeamer Academic**
is the separate academic design and remains the default. Both share Inter
Regular/Semibold and the 171-icon library; their layouts are independent.
Studio uses blue `#001CE0`, a light `#F9F9F9` canvas and lilac accents.
The current collection supports **16:9**.

## Choose, edit, and build

Start with [start-studio.tex](../start-studio.tex), the short editable document.
The generated [main-studio.tex](../main-studio.tex) is the **24-layout showcase**; copy it before editing.
Each command loads the latest composition from `templates/studio/`. Change its
named fields to write your talk; edit that single source when refining a layout.
The [selected-layout guide](../templates/SELECTION.md) has copyable examples.
The [full collection](TEMPLATES.md) contains every unique composition.

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\title{Your Title}
\author{Your Name}
\institute{Your Community}
\date{}
\begin{document}
\begin{frame}[plain]\titlepage\end{frame}
\begin{frame}{A normal slide}{An optional subtitle}
  Your editable Beamer content.
\end{frame}
\closingframe
\end{document}
```

Run `python3 scripts/build.py main-studio.tex`, `make studio`, or the Studio
VS Code task. Output: `build/main-studio.pdf`. On Windows use `py -3` instead
of `python3`. Docker is the default; add `--backend native` for installed TeX.
On Overleaf upload `bitbeamer-studio-overleaf.zip`, select `main.tex`, and use
pdfLaTeX. Prepared artwork is included, so ordinary compilation needs no
converters or regeneration.

The cover has an entirely blue background and a transparent white pattern on
the right. It never recolours or replaces the Academic cover asset. Keep title
lines concise so they remain clear of the pattern. Empty metadata fields are
allowed; `\date{}` matches the example.

## One source per composition

The library contains **195 current compositions**. The [gallery](templates/index.html)
starts with the 24-layout selection; choose Full archive for every composition.
Nine compatibility names preserve earlier commands by loading the same current
source, with their original example defaults. They are not separate slides.

- `main-studio.tex`: generated showcase; copy it before writing a personal talk.
- `examples/studio-selected-templates.tex`: generated, labelled review of that selection.
- `examples/studio-template-catalogue.tex`: generated review of every unique layout.
- `templates/studio/<name>.tex`: the only implementation to edit for a composition.
- `templates/index.json`: fields, sources, references and compatibility mappings.
- `templates/review.json`: which layouts appear first and their copyable examples.

Catalogues call these sources; they do not contain copies of the layouts.
Original measurements remain in `templates/measurements.json`.
`\studiopilot{name}` remains a compatibility command for `\studiotemplate{name}`.

## Ordinary frames and diagram styles

Normal frames use a light background, blue text, and no fixed header, logos,
footer, or visible page numbers. The internal frame counter still advances.
Standard lists, columns, blocks, math, overlays, citations, and fragile code
frames work normally. `\section{...}` only populates the contents; use
`\studiosectionframe{...}` explicitly for a divider. Keep the index to two–four
concise section names, and compile twice after changing them.

Use normal Beamer/TikZ for one-off diagrams rather than a different command for
every diagram. `studio diagram node` and `studio connection` provide consistent
boxes and arrows; the named diagram templates show their use. The chart requires PGFPlots, already included in the documented TeX setup.
Its data are synthetic, not claims about current markets or network performance.

## Cards, statistics, and panels

```latex
\begin{frame}{From keys to payments}
  \begin{studiocards}[columns=3,arrows=true]
    \studiocard{\code[height=1cm]}{Create a wallet}
    \studiocard{\bitcoin[height=1cm]}{Receive bitcoin}
    \studiocard{\alice[height=1cm]}{Pay a friend}
  \end{studiocards}
\end{frame}
```

Card defaults are `columns=3,arrows=false`; use exactly two or three cards,
matching `columns`. Artwork fits down automatically without distortion.
Captions wrap below the cards. Existing `\asset[options]{hyphenated-name}` and
all icon shortcuts are unchanged; SVG/PDF artwork keeps its fixed colours.

Use `\begin{studiostats}[2]` or `[3]` (default 3) with the matching number of
`\studiostat{value}{caption}` entries. Use `\begin{studiopanels}[2]` or `[3]`
(default 2) with matching `\studiopanel{heading}{body}` entries. Panels accept
text, short lists, and graphics. Keep body content within the fixed panel height.
Count mismatches report a clear LaTeX error. Each container resets its options.

## Images and full-slide layouts

```latex
\studioimageframe[side=left]{A wallet in your pocket}{%
  A short explanation beside the illustration.
}{\phone[height=4cm]}
```

`side=right` is the default. `\includegraphics` works instead of an icon.
The graphic fits within its area while preserving its aspect ratio.
`\studiofitgraphic{width}{height}{graphic}` exposes the same fitting behaviour
for custom grids; it scales down oversized artwork and never stretches it.

`\studiobackgroundframe{title}{text}{graphic}` clips the supplied background
at the slide edges and places an editable light text panel on top. Supply a
large enough graphic to cover the desired region; the base canvas is blue.
`\studiofigureframe{caption}{graphic}` reserves about 64% of slide width for
a diagram and places a caption at lower left. Size that figure to fit its area.

`\studiosplitframe{upper}{lower}` uses a blue upper half and a light lower half.
Use prepared white artwork above: `\bitpolitostudioassetpath/alice-white.pdf`,
`bob-white.pdf`, and `pig-white.pdf`. Text colour does not recolour ordinary icons.

## Timelines, quotations, and numbers

```latex
\begin{frame}{Prepare, practice, present}
  \begin{studiotimeline}[direction=horizontal,steps=3]
    \studioevent{Prepare}{Choose an example.}
    \studioevent{Practice}{Try the workflow.}
    \studioevent{Present}{Share what you learned.}
  \end{studiotimeline}
\end{frame}
```

Use `direction=vertical` for descriptions with more text. Defaults are horizontal
and three events; `steps` accepts 2, 3, or 4. Supply exactly that many events.

`\studioquoteframe{text}{credit}` creates a quotation slide; use an empty credit
when no attribution is needed. `\studiostatframe{value}{caption}` creates a large
number slide. Both are complete frames. Keep the text short and provide real
sources when replacing illustrative values with factual claims.

## Closing

```latex
\closingframe[title={Thank you!},subtitle={Questions?},copyright={}]
```

The interface matches Academic. An empty field hides that element, and every
call resets to “Thank You!”, “Questions?”, and the current-year BitPolito
copyright. Studio places the copyright at the top; Academic keeps it below.
Complete-frame commands belong outside another frame. `\titlepage` belongs
inside a plain frame; cards, statistics, panels, and timelines belong inside one.

## Maintenance and Figma references

Studio has its own entry point, inner/outer layouts, and type-size overrides.
The shared Inter and colour configuration contains no Studio layouts.
Dimensions, radii, shadows, and diagram styles are centralized in Studio's theme
files. The existing Academic layout files and original artwork stay unchanged.

Four prepared Studio derivatives have source/output hashes: three white panel
icons and the transparent white cover pattern. Maintain them with
`python3 scripts/prepare-studio-assets.py`; `--check` is read-only. The cover
conversion preserves its authored canvas. The original 171-icon API is untouched.

For faithful reconstruction of frames you provide, read [the Figma guide](FIGMA.md).
Frame exports are visual references, not whole-slide images to embed. Inter
intentionally replaces SF Pro. No SF Pro files or external reference decks are
shipped. The current examples use available artwork; future photo replacements
can use PDF, PNG, or JPEG without changing the layouts.

Existing visual references include the [English introduction](https://github.com/BitPolito/decks/blob/HEAD/introduzione/introduzione-bitcoin-breve-en.pdf)
(cover, transitions, columns, cards, process, chart, quote, timeline, and closing)
and [BitGeneration 3](https://github.com/BitPolito/decks/blob/HEAD/bitgeneration/bitgeneration-3.pdf)
(index, large diagram, split comparison, decision structures, and development
cycle). Other models are reusable visual and technical compositions in the same
brand style; they are not claimed as exact replicas of unseen Figma frames.

## Measured composition collection

See [the complete template guide](TEMPLATES.md) for editable named fields and
[the graphical review workflow](STUDIO-COLLECTION.md) for all reconstructed models.
The compact showcase remains an independent introduction to the theme.
