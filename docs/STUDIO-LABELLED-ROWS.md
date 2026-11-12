# Label and explanation rows

Category: Lists. Three outlined labels and three filled explanation panels,
with a separate heading on the left. All text is editable. No icon is embedded.

```latex
\studiotemplate[
  title={What if someone\\tries to cheat?},
  item-one={
    label={The change},
    body={One friend changes their notebook.}
  },
  item-two={
    label={The comparison},
    body={The others notice the mismatch and discard it.}
  },
  item-three={
    label={New arrivals},
    body={Copy and verify from the first page: do not trust, verify.}
  }
]{labelled-rows}
```

Rows follow top-to-bottom order. Each `item-one`, `item-two` or `item-three`
block accepts `label` and `body`. Omitted values keep defaults; explicit empty
values hide only that text. Panels remain in place. The original light palette
is supported. Labels and the first body fit one line; the remaining
bodies fit two lines, with automatic wrapping or explicit `\\` breaks. All
panels reserve 16 source units of clear space above and below the text. Keep the heading to two short lines. Fonts never shrink;
excess text raises an overflow error.

See the [longer and empty examples](../examples/studio-labelled-rows.tex) and
[model guide](templates/models/labelled-rows.md). Approved by the user on 2026-11-12.
