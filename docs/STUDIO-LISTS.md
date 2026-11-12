# Bullet lists: command reference

Use `\studiotemplate[...]{list-rail}`. Each call creates one complete slide.

## Item count and palette

| Variant | Item fields | Supported palette | Default palette |
| --- | --- | --- | --- |
| `three-items` | `item-one` to `item-three` | `light`, `blue` | `light` |
| `four-items` | `item-one` to `item-four` | `light`, `blue` | `blue` |
| `five-items` | `item-one` to `item-five` | `light`, `blue` | `light` |

`variant` selects the count explicitly. It is never inferred from populated fields.
Omitting `variant` selects `three-items`. Use an explicit `palette` for predictable
results; `blue` is the dark blue treatment, not a `dark` alias. An existing global
`\studiosetup{palette=...}` can override the native default when supported.

```latex
\studiotemplate[
  variant=five-items,
  palette=light,
  title={Key ideas},
  item-one={Verify rules},
  item-two={Check state},
  item-three={Compare copies},
  item-four={Share results},
  item-five={Repeat checks}
]{list-rail}
```

For four items, use `variant=four-items` and omit `item-five`. For three, use
`variant=three-items` and omit both `item-four` and `item-five`. An omitted field
retains its shipped demonstrative text: omission does not remove a bullet or infer
a smaller count. An explicit empty value, such as `item-two={}`, keeps its allocated
space. Fields outside the selected variant are rejected.

## Specialized variants

These calls keep the same `title` and `item-one`, `item-two`, etc. interface.
Their layouts have additional roles; they do not infer their structure from count.

| Variant | Items | Native palette | Extra fields and title meaning |
| --- | --- | --- | --- |
| `detailed` | 4 | `blue` | `title` is the left heading; each item replaces a complete text block |
| `grouped` | 4 | `light` | `group-one-title` labels items one/two; `group-two-title` labels items three/four |
| `illustrated` | 3 | `light` | `title` is the caption below the icon; `illustration` can replace the graphic |

For `illustrated`, `icon-one={alice}` selects a named icon and
`image-one={assets/my-image.pdf}` selects a project-local image. Use
`graphic-one={...}` or `illustration={...}` for a LaTeX graphic. Supply one replacement
method per slot. The original icon remains when none is supplied. Other explicit
palettes are rejected for these specialized variants. The zig-zag variant is removed.

## Wrapping and capacity

| Variant | Title | Each item |
| --- | --- | --- |
| `three-items` | Up to 2 lines | 1 line; the original widths differ |
| `four-items` | 1 line | 1 line |
| `five-items` | Up to 2 lines | Up to 2 lines |
| `detailed` | Up to 2 lines | Up to 2 normal-size lines; shipped blocks also contain smaller detail text |
| `grouped` | 1 line, including group headings | 1 line |
| `illustrated` | Up to 2 centred caption lines | 1 line |

These are line-count limits, not a character guarantee: word widths still have to
fit their box. Supported boxes wrap naturally; `\\` requests an explicit break.
Fonts never shrink. Overflow is an error: shorten the text, split the content, or
choose a layout with more room. The detailed variant's typed heading/body controls
are documented in its [slot guide](templates/guides/checklist-rail.md).

See the [field-by-field model guide](templates/models/list-rail.md) for exact box
capacities and defaults, and [short/long examples](../examples/studio-list-rail.tex)
for complete calls. The simple and specialized list variants were explicitly
approved on 2026-11-09.
