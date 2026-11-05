# Measured lesson layouts

These optional compositions belong to the clone-only educational collection.
They do not expand the compact Studio Overleaf template. Core Studio layouts are
reused where their measured composition matches the source.

```latex
\usepackage{bitpolitostudiolibrary}
% Then copy an actual model ID and its documented fields from the lesson gallery.
```

Inspect a model with `python3 scripts/deck.py layouts --model official-layout-ID
--json`. Every model declares its supported native palette, source canvas, text
fields and fixed boxes. No alternate palette is synthesized. `text/1`, `text/2`,
and so on are aliases for that model's ordered text fields. Empty text preserves
the geometry; unknown fields and overflow produce explicit diagnostics.

`graphic-one`, where listed, replaces the complex artwork plate while preserving
the editable text layer. Supply appropriately sized LaTeX graphics; the original
plate includes its measured transparent padding. Small native diagrams remain
TikZ in the copied part source. Detailed annotations inside historical diagrams,
photographs and screenshots can remain source artwork; see each slide's notes.

Full lesson imports copy these layouts to the personal project. Their local
registrations override the shared collection, so edits remain independent.
