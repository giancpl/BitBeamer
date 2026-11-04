# Studio template structure

Start with [grouped models, variants and palettes](STUDIO-MODELS.md). The advanced composition API remains compatible.

For slide writing, start with [Use a Studio slide](USING-STUDIO.md) and the
[individual guides](templates/GUIDES.md). For visual refinement, use
[the review workflow](STUDIO-COLLECTION.md).

## Source of truth

| Content | Editable source |
| --- | --- |
| Layout, native diagrams and fixed geometry | `templates/studio/<id>.tex` |
| Fields, boxes, references and compatibility mappings | [index.json](../templates/index.json) |
| Grouped models, variants, original palettes and semantic field mappings | [models.json](../templates/models.json) |
| Review status, notes, ordered selection and examples | [review.json](../templates/review.json) |
| Prepared graphic dependencies and provenance | [parts guide](STUDIO-PARTS.md) |

There is one implementation for each of 196 compositions. Nine aliases share current
sources with compatible defaults. The featured models are a working selection,
not a separate library. IDs stay stable when a layout is refined.

Registry, command indices, CSV review sheet, showcase, gallery and per-slide guides
are generated. Run `python3 scripts/review.py sync` after metadata/review changes.
Run `python3 scripts/review.py slide <id>` after changing a layout; it refreshes that
preview. `python3 scripts/review.py check` checks freshness without rewriting files.

## Typed content API

Read [the content API](STUDIO-CONTENT.md) for a common syntax across every model.
Use numbered `text/N`, `icon/N`, `image/N` and `graphic/N` slots, or named aliases
such as `text/title`. Structured blocks also expose `heading/N` and `body/N`.
The individual guides and visual field maps show the stable slot numbers.
Original field names remain compatible.

## Public commands

```latex
\usepackage{bitpolitostudiotemplates}
\studiotemplate[title={Your title},caption-one={First idea}]{three-cards}
\studiopart[width=3cm]{cover-pattern}
```

Select the Studio theme before loading the package. Each template inserts a complete
frame. Omitted fields retain defaults; empty fields keep their box. Unknown fields
and overflow produce diagnostics. `\studiopilot{name}` remains compatible.
All prepared dependencies are included in the clone; original Figma exports are optional.
