# Icon-card rows

Approved on 2026-11-12 for two, three and five cards, both heading states,
replacement icon fitting and the shared caption spacing.

Use one model for a horizontal row of square icon panels with captions:
`\studiotemplate[...]{icon-cards}`. The source compositions share one renderer.

| Variant | Number of boxes | Heading shown by default | Original |
| --- | --- | --- | --- |
| `two` | 2 | No | `figma-0070` |
| `three` | 3 | Yes | `figma-0021` |
| `five` | 5 | Yes | `figma-1022` |

`variant` explicitly chooses the count; it is not inferred from populated fields.
`show-title=true` or `show-title=false` controls the heading independently of
`title={...}`. Hiding the heading keeps the cards and captions in place.
An empty `title={}` also leaves the heading region empty.
The default variant is `three`. Only the original light palette is supported.

```latex
\studiotemplate[
  variant=two,
  show-title=true,
  title={Protect and verify},
  caption-one={Private keys},
  caption-two={Public rules},
  icon-one={key},
  icon-two={shield}
]{icon-cards}
```

The same `caption-one`, `caption-two`, `caption-three`, `caption-four`,
`caption-five` keys follow left-to-right reading order. Supply only fields that
exist for the selected count; an extra field is an error. Omitted captions retain
neutral demonstration text; an explicit empty caption hides only its text.

`icon-one={key}` selects a prepared catalogue icon. `image-one={assets/photo.png}`
loads a project-relative PNG, JPEG or PDF; `graphic-one={\key}` accepts a graphic
command. The corresponding two/three/four/five keys work identically. They all
fit within a centred **216 × 216 source-unit** envelope, preserving aspect ratio.
A wide icon stays wide, a tall icon stays tall. No manual width or height is
needed. The 400 × 400 panel, its SVG-derived shadows and its position stay fixed.
The row's original icon paths are the defaults, also fitted to the same envelope.
Replacement images should have a tight artwork canvas: transparent padding is
part of an image's dimensions and will reduce its visible size.

Headings support two lines at 120 source units. Captions support two lines at
fixed sizes: 76 units for two cards, 88 for three, and 75.16 for five, following
original typography. Automatic wrapping and explicit `\\` are supported;
text that exceeds the fixed box reports overflow and is never shrunk.
Row positions follow the corresponding original exports. Caption boxes start
76 source units below the solid panel's lower edge, consistently for all three
counts. The diffuse shadow is not used as the spacing anchor. Captions share
a fixed first-line baseline, so one- and two-line labels align even when
their first letters have different ascender heights. Interline spacing and
font sizes remain fixed. Adding a
heading to an originally untitled row does not reposition its cards.

See [all examples](../examples/studio-icon-card-rows.tex), the
[model guide](templates/models/icon-cards.md), and the
[replacement content guide](STUDIO-CONTENT.md).

The five-card row now belongs to `icon-cards`, variant `five`; the former
`icon-grid` / `row` syntax is removed. Multirow icon grids, arrow-connected
processes and rectangular cards with body text retain their distinct geometry
and are not converted into this row layout.

Rectangular panels with headings and body text now use the separate
[soft text-card family](STUDIO-SOFT-CARDS.md); former `four-pillars` and
`two-vertical` grouped variants were replaced by its shared syntax.
