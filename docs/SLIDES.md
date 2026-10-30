# Write slides with BitBeamer

The sample [main.tex](../main.tex) demonstrates the template rather than giving
a full Bitcoin lecture. It contains 10 numbered frames and 11 PDF pages,
including a single additional overlay page. Everything is in English.

## Feature map

| Feature | Example frame or location |
| --- | --- |
| Title, subtitle, author, institute, date and partner logos | Cover and preamble |
| Automatic section contents | “Layouts and Graphics” and “Technical Content” |
| Numbered list, columns, highlighted overlay and named asset | “Lists and Columns” |
| Standard, example and alert blocks | “Three Block Styles” |
| Subtitled header, TikZ arrows, Alice and Bob | “Diagrams and Illustrations” |
| Display mathematics, a table and footnote | “Math and Tables” |
| Literal Python code in a fragile frame | “Code Examples” |
| Biber citations and an internal hyperlink | “References and Navigation” |
| Plain frame, full blue background and centered white artwork | Closing slide |

Comments above each frame point out the corresponding Beamer features.
All 171 illustrations remain available through [the asset catalogue](../assets/CATALOGUE.md).
Build the complete visual inventory with
`python3 scripts/build.py examples/asset-catalogue.tex`.

## Theme defaults

The default logo pair is PoliTo + the white BitPolito bull head. The README
lists the explicit wordmark, monogram, and CrypTO alternatives. The header uses
a slightly shorter blue band with a pale blue diagonal accent on the right;
title-only and subtitled frames keep the same nominal height. The default
header icons have equal heights and share a vertical center, with symmetric
outer margins. Both cover orientations use a shared left edge for logos and
text, including the institute when set.

## Choose a cover

```latex
% Classic: artwork on the left, text on the right (default).
\usetheme[cover=image-left]{bitpolito}
% Alternative: text on the left, artwork on the right.
% \usetheme[cover=image-right]{bitpolito}
```

Choose one declaration. You can combine it with branding options, for example
`\usetheme[cover=image-right,group=crypto]{bitpolito}`. The option changes only
the title page; normal frames and the closing slide keep their layouts.

Both covers share text sizes, spacing, logo alignment, and the pale diagonal
accent. The artwork stays in its original orientation, with no conversion.
All metadata still comes from `\title`, `\subtitle`, `\author`, `\institute`,
and `\date`; the presentation's frame structure stays the same.

Build [the two-page comparison](../examples/cover-layouts.tex):

```sh
python3 scripts/build.py examples/cover-layouts.tex
```

Page 1 uses `image-left`; page 2 uses `image-right`. Output:
`build/cover-layouts.pdf`. Releases include `bitbeamer-cover-layouts.pdf`.
The example uses `\bitpolitocover{image-left}` and
`\bitpolitocover{image-right}` to switch within one document. For a complete
deck, select the orientation once through `\usetheme` instead.

For icon syntax, use [the icon guide](ICONS.md) and the
[printable cheat sheet](../examples/icon-cheatsheet.tex).

## Start with a frame

```latex
\begin{frame}{Your title}{An optional subtitle}
  \begin{block}{Main idea}
    Explain one idea at a time.
  \end{block}
\end{frame}
```

Leave out the second argument for a title-only frame. The header adjusts the
font automatically while keeping its standard height. Longer headings can wrap.

## Reveal content progressively

```latex
\begin{frame}{Three points}
  \begin{itemize}
    \item<1-> First point.
    \item<2-> Second point.
    \item<3-> Third point.
  \end{itemize}
\end{frame}
```

Overlays create several PDF pages for one numbered frame. `\pause` introduces
a new overlay; `\uncover<2->{...}` reserves space before revealing content.
The current sample uses a two-step list to demonstrate overlays compactly.

## Include code

```latex
\begin{frame}[fragile]{A code example}
\begin{verbatim}
fee_sat = input_sat - sum(outputs_sat)
\end{verbatim}
\end{frame}
```

Use `[fragile]` with verbatim content. Code is typeset, not executed, so these
examples need no Python interpreter on Overleaf and no shell escape.

## Adjust and compile

Change `aspectratio=169` to `aspectratio=43` for 4:3. The sample is checked in
both formats. Keep the example text concise when replacing it with your content.

Run `python3 scripts/build.py` from the repository root, or choose the default
IDE build task. To regenerate all release artifacts and independently check
all logo variants, run `python3 scripts/release.py`.

The presentation keeps the existing BitBeamer layout; the examples
use standard Beamer, TikZ, and `booktabs`. All are available in the
documented TeX prerequisites and the prepared Overleaf release.
