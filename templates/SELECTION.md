# Selected Studio layouts

A proposed working set of 24 distinct, reusable compositions. Selection is not graphical approval.
All other commands remain in the [full archive](CATALOGUE.md).
Browse the [paginated gallery](../docs/templates/index.html) or build the
[copyable selected deck](../examples/studio-selected-templates.tex):

```sh
python3 scripts/build.py examples/studio-selected-templates.tex build/review
```

Output: `build/review/studio-selected-templates.pdf`. Use `py -3` on Windows;
append `--backend native` for an installed TeX distribution.

## Choose and reuse

Load the Studio theme and `bitpolitostudiotemplates`, then insert a command outside
any frame. Copy an example below to replace its text or graphics. Open the source
to change the arrangement. Defaults remain visible in the review PDF.

| Selection page | Layout | Use | Source |
| --- | --- | --- | --- |
| 1 | `cover` | Introduce a talk and its author. | [cover.tex](studio/cover.tex) |
| 2 | `contents` | Outline four sections. | [contents.tex](studio/contents.tex) |
| 3 | `section-divider` | Separate sections. | [section-divider.tex](studio/section-divider.tex) |
| 4 | `statement-arrow` | Introduce a short claim. | [statement-arrow.tex](studio/statement-arrow.tex) |
| 5 | `glow-statement` | Emphasize a central message. | [glow-statement.tex](studio/glow-statement.tex) |
| 6 | `blue-statement` | Present a statement on blue. | [blue-statement.tex](studio/blue-statement.tex) |
| 7 | `two-columns` | Explain two approaches side by side. | [two-columns.tex](studio/two-columns.tex) |
| 8 | `list-rail-light` | Pair a concept with a short list. | [list-rail-light.tex](studio/list-rail-light.tex) |
| 9 | `three-cards` | Show three illustrated concepts. | [three-cards.tex](studio/three-cards.tex) |
| 10 | `three-step-process` | Explain a three-step process. | [three-step-process.tex](studio/three-step-process.tex) |
| 11 | `four-card-grid` | Group four short explanations. | [four-card-grid.tex](studio/four-card-grid.tex) |
| 12 | `vertical-split` | Compare two alternatives. | [vertical-split.tex](studio/vertical-split.tex) |
| 13 | `image-left` | Pair a large image with a short label. | [image-left.tex](studio/image-left.tex) |
| 14 | `image-right` | Explain a figure or photograph. | [image-right.tex](studio/image-right.tex) |
| 15 | `four-images` | Compare four images. | [four-images.tex](studio/four-images.tex) |
| 16 | `hero-number` | Highlight one key number. | [hero-number.tex](studio/hero-number.tex) |
| 17 | `line-chart` | Present a chart; data can come from CSV. | [line-chart.tex](studio/line-chart.tex) |
| 18 | `horizontal-timeline` | Show events along a timeline. | [horizontal-timeline.tex](studio/horizontal-timeline.tex) |
| 19 | `cycle` | Explain a repeating process. | [cycle.tex](studio/cycle.tex) |
| 20 | `merkle-tree` | Explain a tree with editable labels. | [merkle-tree.tex](studio/merkle-tree.tex) |
| 21 | `table` | Present a compact table. | [table.tex](studio/table.tex) |
| 22 | `equation` | Explain a formula. | [equation.tex](studio/equation.tex) |
| 23 | `code` | Show code from a separate text file. | [code.tex](studio/code.tex) |
| 24 | `closing` | Close the talk. | [closing.tex](studio/closing.tex) |

## Copyable examples

### cover

Introduce a talk and its author.

```latex
\studiotemplate[
  title={Your talk\\title},
  author={Your name},
  institute={Your institute}
]{cover}
```

### contents

Outline four sections.

```latex
\studiotemplate[
  title={Contents},
  item-2-1={Motivation},
  item-2-2={How it works},
  item-2-3={Examples},
  item-2-4={Discussion}
]{contents}
```

### section-divider

Separate sections.

```latex
\studiotemplate[
  title={Your section}
]{section-divider}
```

### statement-arrow

Introduce a short claim.

```latex
\studiotemplate[
  title={Your statement}
]{statement-arrow}
```

### glow-statement

Emphasize a central message.

```latex
\studiotemplate[
  statement={Your main idea}
]{glow-statement}
```

### blue-statement

Present a statement on blue.

```latex
\studiotemplate[
  title={Your statement}
]{blue-statement}
```

### two-columns

Explain two approaches side by side.

```latex
\studiotemplate[
  title={Two approaches}
]{two-columns}
```

### list-rail-light

Pair a concept with a short list.

```latex
\studiotemplate[
  title={Your concept}
]{list-rail-light}
```

### three-cards

Show three illustrated concepts.

```latex
\studiotemplate[
  title={Three useful tools},
  caption-one={Learn},
  caption-two={Build},
  caption-three={Share},
  graphic-one={\asset[width=1cm]{alice}}
]{three-cards}
```

### three-step-process

Explain a three-step process.

```latex
\studiotemplate[
  title={First step},
  text-2={Second step},
  text-3={Third step}
]{three-step-process}
```

### four-card-grid

Group four short explanations.

```latex
\studiotemplate[
  title={Four ideas}
]{four-card-grid}
```

### vertical-split

Compare two alternatives.

```latex
\studiotemplate[
  title={Second option},
  text-1={First option}
]{vertical-split}
```

### image-left

Pair a large image with a short label.

```latex
\studiotemplate[
  title={Your subject},
  graphic-1={\asset[width=3cm]{alice}}
]{image-left}
```

### image-right

Explain a figure or photograph.

```latex
\studiotemplate[
  title={Your example}
]{image-right}
```

### four-images

Compare four images.

```latex
\studiotemplate{four-images}
```

### hero-number

Highlight one key number.

```latex
\studiotemplate[
  title={21 million},
  text-2={A short explanation}
]{hero-number}
```

### line-chart

Present a chart; data can come from CSV.

```latex
\studiotemplate[
  title={Demo},
  text-1={Example curve},
  text-3={},
  text-4={Illustrative data},
  data-file={examples/data/studio-line.csv}
]{line-chart}
```

### horizontal-timeline

Show events along a timeline.

```latex
\studiotemplate[
  title={Your timeline}
]{horizontal-timeline}
```

### cycle

Explain a repeating process.

```latex
\studiotemplate[
  title={Your process}
]{cycle}
```

### merkle-tree

Explain a tree with editable labels.

```latex
\studiotemplate[
  title={Merkle\\Tree}
]{merkle-tree}
```

### table

Present a compact table.

```latex
\studiotemplate[
  title={Your table}
]{table}
```

### equation

Explain a formula.

```latex
\studiotemplate[
  expression={\color{bitpolito}\Large$E=mc^2$}
]{equation}
```

### code

Show code from a separate text file.

```latex
\studiotemplate[
  title={Your example},
  code-file={examples/code/studio-transaction.txt}
]{code}
```

### closing

Close the talk.

```latex
\studiotemplate[
  title={Thank you!}
]{closing}
```

Edit [review.json](review.json) to change this working set, then run
`python3 scripts/review.py sync`. This changes the selection and
navigation without regenerating artwork or removing archive entries.
