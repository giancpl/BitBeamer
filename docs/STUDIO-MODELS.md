# Studio models, variants and palettes

Start with the [slide guide](slides/index.html) or the [95-model index](../templates/MODELS.md).
The library retains all 194 compositions behind 95 model cards. The featured set contains
21 models; every one of the 24 former featured composition choices remains recorded in the review ledger.

Use `\studiotitleframe`, `\studiotocframe` and `\closingframe` for the standard
cover, automatic contents and final slide. `\studioframe{Title}{Content}` provides
a simple aligned content slide. These are [theme commands](STUDIO.md), independent
of the measured catalogue; `\studiotemplate` remains the API for its fixed compositions.

## Choose a model

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\studiosetup{palette=light}
\begin{document}
\studiotemplate[
  variant=pattern,
  palette=blue,
  title={Presentation title},
  author={Author name},
  institute={Organization}
]{cover}
\studiotemplate[variant=three,title={Three concepts},
  caption-one={Learn},caption-two={Build},caption-three={Share},
  icon-one={alice},icon-two={cow},icon-three={bob}]{icon-cards}
\end{document}
```

A model groups related compositions. A variant chooses geometry. Palette switching selects an existing original of that same composition; it does not generate a second colour version.
Read the model's guide before changing variants: a simple cover, for example, does not
have the same content roles as a statistics dashboard. A two-caption composition need
not have the heading field available in a composition with a separate heading.

## Suggested two-slide sequence

The blue section divider and white incoming-arrow statement can form a continuous
visual transition. The slide guide links them under **Suggested sequence** and
lets you copy both commands in their intended order:

```latex
\studiotemplate[title={A new section}]{section-divider}
\studiotemplate[variant=arrow,title={Introduce the key idea.}]{statement}
```

Each call inserts one slide and has its own editable title. The second call also
works independently, without a preceding divider. See the
[multiline example](../examples/studio-section-pair.tex) for paired and standalone
use. The sequence is a recommendation, so no slide is inserted implicitly.

Both compositions support up to two centred lines at fixed font sizes. The
section title grows upward for its second line, preserving the gap above the
vertical rail. The arrow statement wraps within its own fixed box below the
arrow. Use `\\` to choose a deliberate line break:

```latex
\studiotemplate[title={Understanding\\digital money}]{section-divider}
\studiotemplate[variant=arrow,
  title={A shared system\\without a central owner.}]{statement}
```

Shorten copy that would need a third line; overflow is reported instead of
reducing the font. The example includes short text, automatic wrapping, explicit
breaks and independent incoming-arrow statements.


## Change the palette

`\studiosetup{palette=light}` or `palette=blue` sets the default for measured templates.
A template's own `palette` overrides it. `\studiosetup{palette=native}` restores each
composition's original treatment. Without setup, native treatment is the default.

A global palette applies only where the original composition exists in that colour. All other compositions retain their native treatment. For example, `levels` has original light and blue versions; most compositions have only one. The compact light and large blue icon spotlights remain separate variants because their proportions differ. Explicitly asking one of them for an unsupported
palette produces an error; unavailable variants and unknown fields also fail clearly.
Ordinary Beamer frames and the Academic theme do not inherit this template setting.

No opposite-colour slide artwork is generated. Named monochrome library icons use prepared white variants on blue slides. Original icon commands outside Studio keep their colours. Photographs, raster images
and graphics you supply retain their pixels. Choose custom artwork with enough contrast;
coloured imported files are not automatically inverted. A clone includes prepared PDFs:
slide compilation needs no SVG converter, Python on Overleaf, or shell escape.

## Change the content

Named fields describe roles: `title`, `author`, `institute`, `caption-one`, and the labels
listed for the chosen variant. The [individual model guides](../templates/MODELS.md) list
exact supported fields, source files, default text and fixed dimensions. Numbered technical slots remain available through the [advanced composition guides](templates/GUIDES.md).
Replaced public semantic names are not retained as aliases. For rectangular
`text-cards`, use `card-one={title={...},body={...}}` and subsequent card blocks;
see the [command order and layout reference](STUDIO-SOFT-CARDS.md).

For graphic slots, `icon-one={alice}` selects a library icon; `image-one={my-picture.pdf}`
selects an image; `graphic-one={\cow}` accepts LaTeX graphics. These follow the stable slot
numbers in the full guide. Complex slots can represent complete panels or diagrams.

Defaults are short, descriptive English examples. Numeric values, tables and charts are
illustrative. BitPolito and PoliTo remain the theme's branding. External logos, event
screenshots and specific resource covers use neutral image placeholders; replace these
with your own project-relative images. Generic QR examples point to `https://example.org`.

Geometry, fonts and alignment stay fixed. Empty fields retain their space. Shorten an
overflowing text or deliberately edit its source; fonts never shrink automatically.

## Review one choice

```sh
python3 scripts/review.py slide levels --palette blue --open
python3 scripts/review.py models --open
python3 scripts/review.py selection --open
```

`review.py models` produces the vector catalogue and a lightweight image overview. The quick overview contains one page per model; its command captions are selectable. The separate vector model PDF retains selectable slide text and full graphics quality. The selection contains one representative per
featured model. Choose variants and palettes in the gallery without loading every image.
Use the advanced archive only when reviewing every retained source composition.

```sh
python3 scripts/package-studio-review.py --models cover,icon-cards
python3 scripts/review.py all
python3 scripts/review.py palettes --previews
```

These explicit full-collection operations are slower. `all` builds all 194 native compositions;
`palettes` is a compatibility alias for `all`; `--previews` refreshes the 194 native thumbnails. Neither command creates opposite-colour versions or a duplicate palette PDF.
Windows uses `py -3`; append `--backend native` for installed TeX. Default builds use Docker.
The [migration table](../templates/MIGRATION.md) maps all old names to grouped models.

## Maintain the library

Edit `templates/models.json` for grouping, variants, supported palettes and semantic mappings.
Continue using `templates/review.json` for notes, approval, examples and ordered selection;
model selection is derived from that ledger, never a second editable selection file.
Run `python3 scripts/review.py sync` after metadata changes. Source references and former
example values are retained only as maintenance provenance, not shipped visible defaults.

Named-icon contrast alternatives are separate derivatives for use on existing blue slides. Regenerate them with
`python3 scripts/studio_palettes.py prepare`; `check` only verifies hashes and needs no converter. This command never creates slide colour variants.
The original source artwork is retained. New palettes and changed defaults require graphical
review. Packaging checks selected approvals and preserves previous stable artifacts on failure.

Composition approval and each supplied palette are separate review records in `review.json`.
Approving a composition does not approve its other colours. Stable packaging requires explicit
approval of the selected compositions and their included palettes; review packages remain available.

## Corrected composition names

The three-party relay is `protocol` with `variant=message-relay`; `cover-script-blue`
and `cover/script` remain compatible. The former `statement-with-credit` is a
`timeline` with `variant=three-milestones`. Quotations use `dialogue` with
`variant=quotation`, including a single `quote` paragraph and separate `credit`.
Previous `statement/credit` and `dialogue/two-messages` calls remain accepted.
See [the migration table](../templates/MIGRATION.md).


## Unified bullet lists

Use [list-rail](templates/models/list-rail.md) for three, four or five items
(`variant=three-items`, `four-items` or `five-items`) with `palette=light` or
`palette=blue` (dark). This family explicitly supports semantic colour changes.
The `detailed`, `grouped` and `illustrated` variants use the same title
and item fields, with their documented extra fields and native palettes.

See the [complete bullet-list command reference](STUDIO-LISTS.md) for explicit
counts, native defaults, empty fields, palette names and wrapping limits.
