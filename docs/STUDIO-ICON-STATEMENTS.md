# Icon-led statements

All three supplied originals were explicitly approved on 2026-11-13, including
the corrected light preview and centred icon pair. Use `icon-statement` for all three. The compact light and large
blue originals have different icon geometry and icon-to-text spacing, so they
remain distinct variants rather than inventing unprovided palette combinations.

```latex
\studiotemplate[variant=compact,
  statement={A shared purpose}, icon-symbol={wallet}
]{icon-statement}

\studiotemplate[variant=large,
  statement={Learn together.\\Verify together.}, icon-symbol={bitcoin}
]{icon-statement}

\studiotemplate[variant=pair,
  icon-left={bitcoin}, icon-right={wallet}
]{icon-statement}
```

`compact` is the default and uses the native `#f9f9f9` canvas. `large` and `pair`
use the original blue. `statement` accepts at most two lines in its fixed envelope;
automatic wrapping and explicit `\\` are supported. Inter sizes remain fixed:
112.733 / 130.771 units for compact and 113.52 / 131.683 for large (font / leading).
The pair has no text field, matching its original. Unsupported fields or excess
copy produce diagnostics; fonts never shrink.

For a single symbol use `icon-symbol`, `image-symbol` or `graphic-symbol`. For
the pair use `icon-left` / `icon-right`, or the corresponding `image-*` and
`graphic-*` keys. Each replacement fits its original visible-ink envelope with
preserved proportions. Empty values hide only that field. Icon slots are 260 ×
212 source units for compact, 311.371 × 350 for large, and 378.968 × 463.852 /
367 × 631 for the pair. Only transparent source padding is trimmed; default
artwork positions and proportions stay faithful to the SVG originals.

The former model names `icon-spotlight` and `paired-icons-blue` are replaced by
this grouped interface. Original composition IDs remain provenance identifiers.
No obsolete model aliases are added. There are no affected official lesson
consumers. [Customization specimens](../examples/studio-icon-statements.tex)
include long text, empty fields, independent replacements and wide/tall graphics.

The pair aligns the centres of both visible icon envelopes on the same horizontal
axis (y=916.5 source units), as requested during review. This intentionally
replaces the original bottom alignment while retaining both native sizes.
