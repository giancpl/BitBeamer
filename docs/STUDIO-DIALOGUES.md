# Quotations and dialogue

The quotation and three dialogue compositions were explicitly approved on 2026-11-13.
Native backgrounds and prepared bubble artwork are retained. Text stays editable
in Inter at fixed sizes; graphics fit their documented bounds proportionally.

## Quotation

```latex
\studiotemplate[
  width=standard,
  quote={A clear quotation highlights one idea.},
  attribution={Author, source and date}
]{quotation}
```

Write bare text in `quote` and `attribution`: the template always adds opening
and closing double quotation marks and an em dash before the attribution. These
characters participate in measurement and wrapping. Empty fields add no stray
quotation marks or dash. Do not include this punctuation manually.

The `quotation` model has one selected `layered` variant on blue. Its panel
is `#f9f9f9`, including both layers. The whole panel stays centered. Its height
follows the measured quotation and attribution, with fixed internal padding,
a 90-unit separation when both fields are present, original corner radii and
layer offset. Choose `width=compact|medium|standard|wide` (default `standard`). Their front
panels are 1596, 1884, 2108 and 2427.89 source units wide on the 3556-unit canvas.
Each width retains its original layer offsets and rear corner radius. Width stays
fixed for that choice; automatic wrapping and `\\` are supported.
Both Inter sizes stay fixed (83.9053 and 57.187 source units). An empty field
uses no text height or inter-field gap. Both empty fields leave a minimum panel.
The panel grows to 1300 source units, then reports `Text overflow` instead of
shrinking fonts. Long attributions can wrap; the combined height is the limit.

[All original quotation examples](STUDIO-QUOTATION-REFERENCES.md) are tracked
separately from selection and graphical approval. All four widths were explicitly approved on 2026-11-13. The original low standard panel uses the same width and is
covered by automatic height, without a redundant variant.

## Three messages

```latex
\studiotemplate[variant=three-messages,
  message-one={A first message opens the conversation.},
  message-two={A reply asks for more detail.},
  message-three={A short response.}
]{dialogue}
```

Messages follow reading order. Their capacities differ because the original
bubbles differ: two lines, three lines and one line. Text is vertically centered
inside each bubble body; the tails do not affect centering. Empty messages retain
their bubbles and positions. Automatic wrapping and `\\` are supported.

## Shared speech and three people

```latex
\studiotemplate[variant=people,
  message={A shared idea starts a conversation.},
  caption={Context or date},
  icon-person-one={alice},
  icon-person-two={bob},
  icon-person-three={wallet}
]{dialogue}
```

The shared message accepts two lines, followed by a separate one-line caption.
Each person graphic is independent of the speech panel. The source icon spaces
are 246 by 246 source units after excluding transparent padding. Replacements keep their proportions.

## Individual speech and conclusion

```latex
\studiotemplate[variant=cards,
  message-one={First point}, name-one={Person 1}, icon-person-one={alice},
  message-two={Second point}, name-two={Person 2}, icon-person-two={bob},
  message-three={Third point}, name-three={Person 3}, icon-person-three={wallet},
  conclusion={A shared conclusion connects the three points.},
  show-conclusion=true
]{dialogue}
```

Each person has an independently editable message, name and graphic. Person
graphics use 148 by 148 visible-ink slots; names are centered below those slots. The original
bubbles have different widths. Messages and names support up to two lines in their
fixed envelopes; the conclusion supports two. Set `show-conclusion=false` to hide
both the lower panel and its text while preserving all other positions. An empty
`conclusion={}` leaves its panel visible.

For either people variant, `image-person-one={project/image.png}` selects a local
image and `graphic-person-one={LaTeX graphics}` selects custom graphics. The same
keys exist for persons two and three. An empty replacement hides only that icon.
Bubbles and panels remain independent. Fixed text sizes never shrink; excessive
copy produces a diagnostic. Use shorter text or another slide when needed.

The old quotation access through `dialogue` and numbered semantic labels has been
replaced. Use `quotation`, `attribution`, `message-*`, `name-*` and the person icon
keys above. Official lesson callers and examples use the current fields; no old
field aliases are added. Historical content names remain provenance metadata,
not authoring commands.

[The complete specimen](../examples/studio-dialogue-layouts.tex) demonstrates
longer automatic wrapping, manual breaks, empty fields, replaced icons, image and
custom-graphic proportions, and the hidden conclusion. Approved compositions are removed from the active comparison. The canonical
specimen remains available for reuse and regression checks.
