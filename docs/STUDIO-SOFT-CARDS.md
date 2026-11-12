# Soft text cards

Canonical category: **Cards**. All ten `text-cards` variants are approved.
Use one `\studiotemplate` call per slide. Each card keeps its own content together:

```latex
\studiotemplate[
  variant=two-icon-stacked,
  title={Compare the systems},
  introduction={Explain each responsibility.},
  card-one={
    title={Research},
    body={Study the shared public rules.},
    icon={book}
  },
  card-two={
    title={Protocol},
    body={Verify each update independently.},
    icon={bitcoin}
  }
]{text-cards}
```

## Command order

Use the same order in every variant:

1. Select `variant` and any visibility options you need to change.
2. Write the slide `title`, its optional `title-icon`, and the sidebar `introduction` where supported.
3. Fill `card-one`, `card-two`, and subsequent cards in visual reading order.
4. Inside each card, write `title`, then `body`, then its optional `icon` (or `image` / `graphic`).

Generated commands follow this order. Options do not depend on their input order;
all fields are available before the slide is rendered. Omitted values retain the
shipped defaults. Set a particular value to `{}` to leave its measured area empty.
Use the documented card blocks for new slides; low-level numbered technical slots
remain available for maintenance.

## Choose a layout

| Variant | Cards | Arrangement | Original composition |
| --- | ---: | --- | --- |
| `three-summary` (default) | 3 | Two above, one centred below | `three-card-summary` / `36.svg` |
| `two` | 2 | Two horizontal panels | `benefits-limits` / `50.svg` |
| `four` | 4 | Two-by-two panels | `four-pillar-cards` / `51.svg` |
| `four-bullets` | 4 | Two-by-two panels with larger body type | `four-card-grid` / bitgeneration 1-5 |
| `two-stacked` | 2 | Two stacked panels beside an introduction | `two-card-vertical` / introduction 132 |
| `two-icon-stacked` | 2 | Stacked icon panels beside an introduction | `feature-spotlight` / introduction 131 |
| `five` | 5 | Two panels left, three right, unequal heights | `incentives-card-grid` / `Frame 1019.svg` |
| `four-network` | 4 | Two-by-two panels with taller lower descriptions | `network-environments` / `Frame 1024.svg` |
| `four-nodes` | 4 | Two-by-two panels with source-specific text insets | `node-type-grid` / `Frame 1026.svg` |
| `three-asymmetric` | 3 | Two panels left, one tall panel right | `mining-card-grid` / `Frame 1017.svg` |


The variant explicitly selects the layout and number of cards. Add exactly the
card blocks you want to edit, up to that count; an extra `card-four` in a three-card
layout is an error. All variants use the original light palette and Inter Semibold
at fixed, source-specific sizes.

## Visual reading order

The order is left-to-right, then top-to-bottom. The same card block always holds
that panel's title, body and icon. Text is never reassigned according to its length.

| Arrangement | Reading order |
| --- | --- |
| Horizontal pair | `card-one` left, `card-two` right |
| Two-by-two grid | `card-one` upper left, `card-two` upper right, `card-three` lower left, `card-four` lower right |
| Three-card summary | `card-one` upper left, `card-two` upper right, `card-three` centred below |
| Sidebar variants | Slide title/introduction at left; `card-one` upper right, `card-two` lower right |
| Five uneven cards | `card-one` upper left, `card-two` upper right, `card-three` lower left, `card-four` middle right, `card-five` lower right |
| Asymmetric three | `card-one` upper left, `card-two` tall right, `card-three` lower left |

The last two arrangements can be read as:

```text
five             three-asymmetric
+---+---+        +---+---+
| 1 | 2 |        | 1 |   |
+---+---+        +---+ 2 |
|   | 4 |        | 3 |   |
| 3 +---+        +---+---+
|   | 5 |
+---+---+
```

## Optional content

All visibility options default to `true`; omit them for the normal appearance.
Only `true` and `false` are accepted. Hidden content leaves the original layout
positions intact.

| Option | Effect |
| --- | --- |
| `show-title` | Show the slide title, including the heading at left in sidebar layouts |
| `show-introduction` | Show the left introduction in the two sidebar variants |
| `show-card-titles` | Show each card title, including captions below icons |
| `show-card-bodies` | Show each card description |
| `show-icons` | Show all icons in the two icon-bearing variants |

```latex
\studiotemplate[
  variant=two,
  show-title=false,
  card-one={title={Privacy}, body={}},
  card-two={title={}, body={Keep evidence you can verify.}}
]{text-cards}
```

## Icons and images

In `two-icon-stacked`, put the replacement inside its card block:

```latex
card-one={
  title={Research},
  body={Explain the first system.},
  icon={book}
}
```

Choose one of `icon={catalogue-name}`, `image={path/to/local.pdf}`, or
`graphic={\tikz \draw (0,0) circle (3mm);}`. Use `{}` to hide just that icon.
Original icons are used when no replacement is provided. Replacements are centred,
keep their aspect ratio and fit a 240 × 240 source-unit envelope. Panel artwork
and all text coordinates remain fixed.

In `five`, the symbol belongs to the slide heading, so use the separate
`title-icon`, `title-image` or `title-graphic` key before the card blocks. Its
maximum size is 209 × 209 source units. For example:

```latex
\studiotemplate[
  variant=five,
  title={Incentives},
  title-icon={bitcoin},
  card-one={title={Miner}, body={Block rewards.\\Transaction fees.}},
  card-two={title={Merchant}, body={Open participation.}},
  card-three={title={Node operator}, body={Verify the shared record.}},
  card-four={title={Developer}, body={Build on an open protocol.}},
  card-five={title={Holder}, body={Consider the long-term trade-offs.}}
]{text-cards}
```

Icon fields are accepted only where the original layout has an icon. Use the
[icon substitution examples](../examples/studio-soft-card-icons.tex) for named
icons, images, wide/tall graphics, empty values and longer text.

## Text capacity and wrapping

Bodies wrap automatically. Use `\\` for an intentional line break. All card
titles are single-line fields; captions under icons need short labels such as
“Network”. Only the slide title in `three-summary` supports two lines; other
slide titles support one line within their original width.

Capacity depends on the original panel. In `two-stacked`, the upper body supports
two lines and the lower body four. The two short right-hand panels in `five`
support one body line. Other variants have larger paragraph areas, including
the tall panel in `three-asymmetric`. See the [measured field guide](templates/models/text-cards.md)
for exact dimensions, font sizes and leading. Overflow requires shorter text,
a roomier variant or another slide; text never shrinks to fit.

[Thirty text examples](../examples/studio-soft-cards.tex) cover short copy,
automatic wrapping and explicit breaks for every variant.

## Migration and provenance

The grouped syntax replaces the old flat `caption-one`, `body-one` and
`icon-one` keys for this family. Use `card-one={title={...},body={...},icon={...}}`;
the `five` heading icon is `title-icon`. The visibility names are now
`show-card-titles` and `show-card-bodies`. Replaced names are rejected, not aliases.
Other model families keep their own documented commands.

Canonical composition IDs and original graphics remain stable. The ten layouts
were verified against source-file hashes after inspecting 38 inventory candidates.
All ten were explicitly approved on 2026-11-12. This command reorganization retains
the approved visual layouts; approved compositions stay out of pending comparisons.
