# Selected Studio models

The showcase presents 21 models. The ledger retains 24 selected composition choices, including alternate variants. Selection is not graphical approval.
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
| 1 | `cover` | Demonstrate this reusable composition. | [cover.tex](studio/cover.tex) |
| 2 | `contents` | Show four agenda items in the measured panel composition. | [contents.tex](studio/contents.tex) |
| 3 | `section-divider` | Demonstrate this reusable composition. | [section-divider.tex](studio/section-divider.tex) |
| 4 | `statement-arrow` | Demonstrate this reusable composition. | [statement-arrow.tex](studio/statement-arrow.tex) |
| 5 | `glow-statement` | Demonstrate this reusable composition. | [glow-statement.tex](studio/glow-statement.tex) |
| 6 | `blue-statement` | Demonstrate this reusable composition. | [blue-statement.tex](studio/blue-statement.tex) |
| 7 | `two-columns` | Demonstrate this reusable composition. | [two-columns.tex](studio/two-columns.tex) |
| 8 | `list-rail-light` | Demonstrate this reusable composition. | [list-rail-light.tex](studio/list-rail-light.tex) |
| 9 | `three-cards` | Demonstrate this reusable composition. | [three-cards.tex](studio/three-cards.tex) |
| 10 | `three-step-process` | Demonstrate this reusable composition. | [three-step-process.tex](studio/three-step-process.tex) |
| 11 | `four-card-grid` | Demonstrate this reusable composition. | [four-card-grid.tex](studio/four-card-grid.tex) |
| 12 | `vertical-split` | Demonstrate this reusable composition. | [vertical-split.tex](studio/vertical-split.tex) |
| 13 | `image-left` | Demonstrate this reusable composition. | [image-left.tex](studio/image-left.tex) |
| 14 | `image-right` | Demonstrate this reusable composition. | [image-right.tex](studio/image-right.tex) |
| 15 | `four-images` | Demonstrate this reusable composition. | [four-images.tex](studio/four-images.tex) |
| 16 | `hero-number` | Demonstrate this reusable composition. | [hero-number.tex](studio/hero-number.tex) |
| 17 | `line-chart` | Demonstrate this reusable composition. | [line-chart.tex](studio/line-chart.tex) |
| 18 | `horizontal-timeline` | Demonstrate this reusable composition. | [horizontal-timeline.tex](studio/horizontal-timeline.tex) |
| 19 | `cycle` | Demonstrate this reusable composition. | [cycle.tex](studio/cycle.tex) |
| 20 | `merkle-tree` | Demonstrate this reusable composition. | [merkle-tree.tex](studio/merkle-tree.tex) |
| 21 | `table` | Demonstrate this reusable composition. | [table.tex](studio/table.tex) |
| 22 | `equation` | Demonstrate this reusable composition. | [equation.tex](studio/equation.tex) |
| 23 | `code` | Demonstrate this reusable composition. | [code.tex](studio/code.tex) |
| 24 | `closing` | Demonstrate this reusable composition. | [closing.tex](studio/closing.tex) |

## Copyable examples

### cover

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Presentation\\title},
  author={Author name},
  institute={Department or organization}
]{cover}
```

### contents

Show four agenda items in the measured panel composition.

```latex
\studiotemplate[
  title={Contents},
  item-2-1={First section},
  item-2-2={Second section},
  item-2-3={Third section},
  item-2-4={Fourth section}
]{contents}
```

### section-divider

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{section-divider}
```

### statement-arrow

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{statement-arrow}
```

### glow-statement

Demonstrate this reusable composition.

```latex
\studiotemplate[
  statement={Slide title}
]{glow-statement}
```

### blue-statement

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{blue-statement}
```

### two-columns

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{two-columns}
```

### list-rail-light

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Title}
]{list-rail-light}
```

### three-cards

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title},
  caption-one={Label 2},
  caption-two={Label 3},
  caption-three={Label 4},
  graphic-one={\asset[width=1cm]{alice}}
]{three-cards}
```

### three-step-process

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title},
  text-2={Label 3},
  text-3={Label 1}
]{three-step-process}
```

### four-card-grid

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{four-card-grid}
```

### vertical-split

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title},
  text-1={Supporting explanation.\\Add your own details.}
]{vertical-split}
```

### image-left

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title},
  graphic-1={\asset[width=3cm]{alice}}
]{image-left}
```

### image-right

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{image-right}
```

### four-images

Demonstrate this reusable composition.

```latex
\studiotemplate{four-images}
```

### hero-number

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Title},
  text-2={Supporting explanation}
]{hero-number}
```

### line-chart

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Title},
  text-1={Label 1},
  text-3={Item},
  text-4={Supporting explanation},
  data-file={examples/data/studio-line.csv}
]{line-chart}
```

### horizontal-timeline

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{horizontal-timeline}
```

### cycle

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{cycle}
```

### merkle-tree

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Binary\\tree}
]{merkle-tree}
```

### table

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title}
]{table}
```

### equation

Demonstrate this reusable composition.

```latex
\studiotemplate[
  expression={\color{bitpolito}\Large$E=mc^2$}
]{equation}
```

### code

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Slide title},
  code-file={examples/code/studio-transaction.txt}
]{code}
```

### closing

Demonstrate this reusable composition.

```latex
\studiotemplate[
  title={Thank you}
]{closing}
```

Edit [review.json](review.json) to change this working set, then run
`python3 scripts/review.py sync`. This changes the selection and
navigation without regenerating artwork or removing archive entries.
