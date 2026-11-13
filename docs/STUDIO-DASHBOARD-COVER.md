# Dashboard cover

The unified model for figma-0609, figma-0610 and figma-0611 was explicitly
approved on 2026-11-13, including the generic byline and customization options. The exported
numbers are historical examples, not verified current organization statistics.

```latex
\studiotemplate[
  byline={Presentation 2024/25},
  participants-number={55}, participants-label={Participants},
  alumni-number={180}, alumni-label={Alumni},
  followers-number={7000+}, followers-label={Followers on multiple channels},
  events-number={40+}, events-label={Events organized}
]{cover-dashboard}
```

The native palette is blue. The original SVG outline panels are fixed decoration;
all four numbers and labels are independent editable LaTeX fields. Each metric
has one line per field at fixed Inter sizes (194.4-unit semibold numbers and
65.76-unit regular labels). Omitted fields retain illustrative defaults; empty
fields hide their content without moving the panels. Excess copy produces an
overflow diagnostic and never shrinks the font.

`byline` supports two lines at 79.1467 units. The original pixel wordmark is the
default brand artwork. A nonempty `title` replaces it with editable semibold
170-unit text, supporting two lines and automatic wrapping or explicit `\\`.
Clear the title to restore the brand artwork. These fields do not move metrics.

The two top logos are independently replaceable with `icon-left`, `image-left`,
`graphic-left` and their `right` equivalents. Their visible bounds follow the
original (192.751 × 157.679 and 157.686 × 157.689 source units). The wordmark has
`icon-brand`, `image-brand`, `graphic-brand`, in a 1089 × 193 envelope. Its
replacement is visible only when `title` is empty. Every replacement preserves
proportions; explicit empty values hide only that slot.

```latex
\studiotemplate[
  title={A growing\\community},
  byline={Learning, sharing and building\\together across the university},
  icon-left={bitcoin},
  image-right={images/studio/icon-palettes/alice.pdf}
]{cover-dashboard}
```

The former `label-one` … `label-nine` fields and numbered decoration overrides
are replaced by the semantic interface. There are no compatibility aliases.
No official lesson or block consumes this composition. See the
[customization examples](../examples/studio-dashboard-cover.tex) for all field
replacements, empty fields, wide/tall graphics and historical content versions.
