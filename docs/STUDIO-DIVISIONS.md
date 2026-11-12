# Divisions: four or eight editable icons

Use `icon-grid` with `variant=four` or `variant=eight`. The count is explicit;
it does not depend on the number of filled fields. Both variants use their original
light palette. The twelve-word grid is a separate layout.

Fields follow reading order: left to right across the top row, then the bottom row.
Each `caption-one` has a matching `icon-one`, continuing through `four` or `eight`.

```latex
\studiotemplate[
  variant={four},
  title={Divisions},
  caption-one={Education}, icon-one={book},
  caption-two={IT}, icon-two={code},
  caption-three={Marketing}, icon-three={heart},
  caption-four={Management}, icon-four={bitcoin}
]{icon-grid}
```

For eight elements, use `variant={eight}` and add the following pairs:

```latex
caption-five={Security}, icon-five={key},
caption-six={Operations}, icon-six={padlock},
caption-seven={Verification}, icon-seven={shield},
caption-eight={Community}, icon-eight={alice}
```

Omit an icon field to retain its original symbol. Use `icon-one={}` to hide only
that symbol. The panel remains visible. A supplied icon replaces the entire symbol;
no original paths remain behind it.

Each symbol fits a fixed 240 × 240 source-unit area centered within its panel.
Its aspect ratio is preserved. Icons, images and custom graphics share these
bounds and never change the panel or caption position. Use one replacement type
per position:

```latex
image-one={images/my-icon.pdf},
graphic-two={\textcolor{studio-foreground}{\rule{10pt}{100pt}}}
```

Images accept project-relative PDF, PNG or JPEG paths. Named icons come from the
[icon catalogue](ICONS.md). An unknown icon, missing file or unavailable position
produces an explicit error. The four-item variant rejects `icon-five`.

Caption font sizes remain fixed. Captions support two lines; wrapping is automatic
and `\\` inserts an explicit line break. Shorten copy that exceeds its allocated
space. Empty captions preserve their spacing.

See the [model field reference](templates/models/icon-grid.md),
[unified guide](slides/index.html?model=icon-grid) and
[complete compiled examples](../examples/studio-divisions.tex) for originals,
long captions, replacement icons, different aspect ratios and a blank symbol.
