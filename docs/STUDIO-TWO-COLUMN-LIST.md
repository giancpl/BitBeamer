# Two-column bullet list

Category: Lists. Original: BTC Prague 106, `figma-0183`. A centred heading and
two independent bullet columns, in the original light palette. All text is editable;
there are no icons or embedded labels.

```latex
\studiotemplate[
  title={Topics and practical examples},
  left-items={
    \item Explore the shared rules and compare the assumptions used by each participant.
    \item Review the practical example.\\Record the checks performed locally.
    \item Explain how the available information supports each conclusion.},
  right-items={
    \item Compare the available approaches and describe the trade-offs for new participants.
    \item Repeat the example independently.\\Check the result before accepting it.
    \item Summarize the remaining questions and identify the next useful experiment.}
]{title-two-column-list}
```

Use `title`, `left-items` and `right-items`. Each list contains standard LaTeX
`\item` commands; bullets and indentation are automatic. Wrapped lines and
explicit `\\` breaks align with the text of that item, rather than the bullet.
Do not insert a second `itemize` environment inside these fields.

Each column supports at most eleven lines, including wrapped lines, at the fixed
75.16/95.25 source font and leading. Use a one-line heading. Text never shrinks;
excess content is reported. The heading's centre is retained from the original,
with room for a longer title. Empty fields hide only that field and retain the
column's position. Omitted fields retain neutral demonstration text.
The obsolete `label-two` and `label-three` public keys have been replaced.

See the [model guide](templates/models/title-two-column-list.md) and
[short, long and empty examples](../examples/studio-two-column-list.tex).
Explicitly approved on 2026-11-12.
