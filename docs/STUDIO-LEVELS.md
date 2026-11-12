# Three icon levels

The Lists family `levels` contains the same three-row composition in the original
light and blue palettes. The title is on the left; captions and icons follow
reading order from top to bottom. No card background is involved.

```latex
\studiotemplate[
  palette={light},
  title={Learning\\together},
  item-one={
    text={Explore the shared rules.},
    icon={book}
  },
  item-two={
    text={Build and compare examples.},
    icon={code}
  },
  item-three={
    text={Review each result independently.},
    icon={shield}
  }
]{levels}
```

Set `palette={blue}` for the original blue treatment. Rows are ordered top to
bottom: `item-one`, `item-two`, `item-three`. Each block accepts `text` plus one
of `icon`, `image` (a PDF/PNG path) or `graphic` (TeX artwork).

Omitted fields keep their defaults. `text={}` hides only the description;
`icon={}` hides only the symbol. `title={}` hides the heading independently.
Icons preserve aspect ratio within fixed 209 x 209 source-unit bounds. Named
icons adapt to the selected palette; imported files retain their own colours.

Descriptions support two lines with automatic wrapping or explicit `\\` breaks,
vertically centred beside the icon. The title supports two short lines. Fonts
never shrink; excess text raises a clear overflow error. The old flat caption
and icon keys have been replaced by the grouped syntax.

See the [model reference](templates/models/levels.md),
[unified guide](slides/index.html?model=levels) and
[short, longer, replacement and empty examples](../examples/studio-levels.tex).
