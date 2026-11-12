# Maintain and review Studio slides

The [slide guide](slides/index.html) is the single visual reference. It opens
offline from a clone and has three views: templates, full presentations and
reusable blocks. Start with featured models; additional lesson layouts and fixed
slides load only when requested. Each page shows at most 12 cards.

```sh
python3 scripts/review.py guide --open
python3 scripts/review.py slide three-cards --open
```

Open a preview for the full canvas at 1600 px, editable areas and measured field
bounds. The command beside it reproduces the displayed example. Copy it outside
any Beamer frame. Choose only the documented original palettes; fixed-content
slides accept no overrides. See [model fields](STUDIO-MODELS.md) for semantic
options and [the authoring guide](AUTHORING.md) for personal presentations.

## Review one small family at a time

Review **three to five compositions per batch**, using function rather than lesson
subject to classify them. Bitcoin, mining and money remain searchable topics;
additional layouts without a reviewed visual family show **Needs classification**.
Do not infer a layout family from its topic or treat compilation as graphical approval.

Every batch with editable text must also include compiled examples with longer
copy, appropriate to each model's role, alongside its short/default examples.
Visually inspect automatic wrapping and explicit line breaks where supported,
vertical centering, spacing, overlap and clipping. Keep the documented font sizes;
verify clear overflow reporting beyond the supported capacity. Include the sample
source and open its PDF with the comparisons during interactive reviews.

The five compositions in **covers-01** were explicitly approved by the user on
2026-11-06. Their current graphics are finalized, in this order:

| ID | Composition | Content policy |
| --- | --- | --- |
| `cover` | Classic blue pattern cover | Editable title, author and organization |
| `cover-light` | Light cover with lettering | Editable text and documented graphics |
| `cover-photo` | Photo cover with lettering | Editable text and documented graphic |
| `cover-wide-title` | Blue cover with a wide title | Editable title, author and date |
| `bitpolito-wordmark-cover` | Cropped BitPolito wordmark | Fixed content |

Choose **Review batch** in the unified guide, or append
`?batch=covers-01&maintenance=1` to its URL. Each composition has its own card;
variants are not hidden behind a model selector in this view. **Compare original /
replica** opens its local reference alongside the current template. The rest of
the catalogue remains available by choosing **Browse the catalogue**.

```sh
python3 scripts/review_batch.py covers-01
# Optional local originals and lesson-maintenance dependencies:
python3 scripts/review_batch.py covers-01 --compare --open
```

The compiled five-page deck, editable generated source, review sheet and optional
comparison PDF stay under `build/review/batches/covers-01/`. No full catalogue is
compiled. Batch definitions and their order live in `templates/review.json` under
`review_batches`; comparison originals remain local. Unknown IDs, duplicate entries
and batches above five compositions are rejected.

To collect **pending compositions from registered batches** into one bookmarked PDF, run
`python3 scripts/review_batch.py all --compare --open`. The result is
`build/review/batches/comparisons.pdf`, in batch order, with a single page count.
Approved core templates and fixed lesson presets are excluded automatically;
entirely approved batches are skipped. Categories are shown in each comparison
header and in the report. The exact public command used to build each comparison
is printed below it; the handoff repeats the active layout command. The launcher reuses current builds and does not compile
the full catalogue. A direct request for a fully approved batch reports that no
compositions are pending. Report only pending names and canonical categories at
each interactive handoff; a deferred design is not an approved design.

Record feedback by stable composition ID in the existing review ledgers. Check
canvas/cropping, margins and alignment, font weights, visual hierarchy, graphics,
field behavior and the published command. Neutral text and Inter are intentional
adaptations. Fix the canonical source and refresh its consumers before approval.
The corrected **team-01** composition was explicitly approved by the user on
2026-11-06. Its figures remain editable examples, not verified live statistics.

Both compositions in **contents-01** were explicitly approved by the user on
2026-11-09 after the size and vertical-centering corrections:

| ID | Composition |
| --- | --- |
| `contents` | Four-item panels |
| `contents-five` | Five-item panels |

Open `?batch=contents-01&maintenance=1` in the unified guide, or compile:

```sh
python3 scripts/review_batch.py contents-01 --compare
```

The legacy `tabbed-agenda` and `agenda-with-icons` entries originate from benefits
lists; `agenda-with-schedule` originates from an activity schedule. They remain
available under their compatible names, but are excluded from this contents review.

Review title hierarchy, weights, item spacing, panel proportions and deliberate
edge crops. The **closing-01** batch contains one five-social composition:

| ID | Purpose |
| --- | --- |
| `closing` | Five-social closing matched to page 11 of the supplied introduction |

```sh
python3 scripts/review_batch.py closing-01 --compare
python3 scripts/review_batch.py all --compare --open
```

The previously reviewed wrappers comprise nine pages: five covers, Team, two
agendas and one closing. The four-social variant has been removed. The clone-only
`bitpolito-contact` name remains a consumer of the same closing component;
its duplicate review page is omitted. QR-off centres this composition and does
not introduce another model. The final closing and both QR states were explicitly
approved by the user on 2026-11-09.

## Approved section introduction and key idea

The **dividers-01** batch contains two consecutive compositions:

1. `section-divider`: blue introduction with a white line leaving the bottom edge.
2. `statement-arrow`: white key-idea slide with a blue arrow entering from the top.

Their aligned lines create a visual connection when used in this order. The
unified guide offers a **Suggested sequence** on both cards, with links to each
slide and a **Copy sequence** action for both commands. Each primary command
still inserts only its own slide. The incoming-arrow statement can be used alone.
Other statement variants do not inherit this recommendation.

Review the connection, title/statement hierarchy, line thickness, cropping and
spacing against `figma-0697` and `figma-0055`. Both compositions, paired and
independent use, and their reviewed multiline behavior were explicitly approved
on 2026-11-09. Inter and neutral English copy are intentional adaptations.

```sh
python3 scripts/review_batch.py dividers-01 --compare --open
python3 scripts/review_batch.py all --compare --open
```

This approved pair is excluded from the current combined review.
The [editable sequence example](../examples/studio-section-pair.tex) contains eight pages:
three divider/arrow pairs (short, longer, explicit two-line copy), followed by
two standalone arrow statements. Font sizes stay fixed throughout.

## Current review: other statements

The **statements-01** batch contains the three remaining statement variants:

| Composition | Public variant | Review focus |
| --- | --- | --- |
| `glow-statement` | `statement`, `variant=glow` | Radial gradient and white text |
| `blue-statement` | `statement`, `variant=plain` | Wide statement on blue |
| `oversized-word` | `statement`, `variant=clipped` | Oversized short headline and upper caption |

```sh
python3 scripts/review_batch.py statements-01 --compare --open
python3 scripts/review_batch.py all --compare --open
```

The pending statement batch occupies pages 1–3 of the current combined comparison.
These three compositions remain in review. The incoming-arrow variant is already
approved and retains its optional connection with the section divider. The legacy
`variant=credit` alias points to a timeline and is not included in this batch.

The [editable statement examples](../examples/studio-statements.tex) alternate
short and longer copy for each variant. Glow includes a short phrase and both
automatic and explicit two-line wrapping, centered on the radial gradient at the
same font size. One provisional background is retained: the supplied native PDF
at its original proportions, with only its paper rectangle normalized to standard
`#F9F9F9`. It is retained at
`images/studio/parts/source/statement-glow-background-f9f9f9.pdf` and copied to
`radial-glow.pdf`. Gradient and transparency streams remain unchanged; text stays
separately editable. The original supplied PDF and PNG are retained as source
inputs. Experimental SVG/PNG-derived backgrounds and supplementary comparison
pages are retired. The visual issue remains open; the user requested deferral.
The plain blue statement uses a wide single line. The oversized variant is for
a short word or headline; it retains a fixed large font and a separate caption.

## Two-column review

The `two-columns` layout (canonical category: Lists) was explicitly approved on
2026-11-09 and is excluded from pending review PDFs.
[Short and longer examples](../examples/studio-two-columns.tex) check automatic
and explicit wrapping at fixed font sizes. The type hierarchy is fixed at
120/140 for the title, 90/105 for both headings and 80/95 for introduction and
both bodies (size/leading in source units). The public fields are `title`,
`introduction`, `left-title`, `right-title`, `left-body` and `right-body`.
These names replace `label-two` through `label-six`; the obsolete keys are rejected.

```sh
python3 scripts/build.py examples/studio-two-columns.tex build/review/two-columns --open
```

## Active bullet-list review

The list family was explicitly approved on 2026-11-09 and is excluded from
pending comparisons. [The full usage reference](STUDIO-LISTS.md) explains counts,
fields, native defaults, palettes, empty values and wrapping. Older unresolved
Statements stay in the ledger and are excluded from the current PDF. Set `active_review_batches` when
switching the review focus; approval and active scope are independent.

All bullet-and-rail compositions use `list-rail`, with `title`, `item-one`,
`item-two`, `item-three`, and further items where available:

| Variant | Items | Palette | Extra fields |
| --- | --- | --- | --- |
| `three-items` | 3 | light, blue | — |
| `four-items` | 4 | light, blue | — |
| `five-items` | 5 | light, blue | — |
| `detailed` | 4 | blue | Two-line item text |
| `grouped` | 4 in two groups | light | `group-one-title`, `group-two-title` |
| `illustrated` | 3 | light | `illustration` |

Blue is the dark treatment. The five-item layout is an adaptation of the related
four-item source; the comparison reference is explicitly shared, not an original
five-item design. Native geometry of the existing specialized variants is retained.
Labelled boxes, column prose, partner-logo grids and level diagrams remain distinct
models because they are not bullet-and-rail lists.

```latex
\studiotemplate[
  variant=five-items,
  palette=blue,
  title={Key ideas},
  item-one={Verify rules},
  item-two={Check state},
  item-three={Compare copies},
  item-four={Share results},
  item-five={Repeat checks}
]{list-rail}
```

[All short and longer examples](../examples/studio-list-rail.tex) test automatic
and explicit wrapping where the original text slots support it. Fonts never shrink.

```sh
python3 scripts/review_batch.py all --compare --open
python3 scripts/build.py examples/studio-list-rail.tex build/review/list-rail --open
```

## Card review families

The approved icon-card rows use `icon-cards`; see
[their guide](STUDIO-ICON-CARDS.md). Rectangular cards with descriptions use
[text-cards](STUDIO-SOFT-CARDS.md); all ten compositions are approved.

## Correct the canonical source

Follow the [internal correction workflow](../.github/CONTRIBUTING.md#default-template-correction-workflow).
Edit `templates/studio/<id>.tex` and its measured metadata in `templates/index.json`.
For lesson layouts, use [lesson maintenance](../library/MAINTENANCE.md). Correct
shared panels, typography and geometry once, then rebuild all affected consumers.
Personal content remains independent. Linked layouts receive canonical graphical
fixes; legacy snapshots require explicit migration. Academic remains unchanged.

```sh
python3 scripts/review.py slide three-cards
python3 scripts/library.py build --changed templates/studio/three-cards.tex --preview
python3 scripts/review.py sync
python3 scripts/review.py check
```

The single-slide PDF is `build/review/slides/three-cards/slide.pdf`. Preview updates
also refresh the guide. Dependency fingerprints reuse unchanged outputs. A notes-only
edit needs sync, not compilation. Changing a shared source requires fresh previews
before the read-only check passes.

## Record feedback and select

Edit [review.json](../templates/review.json), the single Studio review ledger:

- `selection`: ordered compositions featured in the guide and compact showcase.
- `reusable_selection`: neutral layouts shortlisted for creating new content.
- `templates.<id>.status`: `in review`, `changes requested`, `approved` or `supplementary`.
- `notes` and `feedback`: observations, canonical action and verification evidence.
- `palette_reviews`: explicit review state for the original colour treatment.
- `use` and `example`: purpose and valid copyable overrides.

Lesson observations belong in `library/index.json`. Selection and a successful
build do not approve a slide. Return changed approved designs to `in review`.
Generated CSV sheets, registries, guides and showcase sources are exports; edit
the canonical JSON instead. Keep public IDs and compatibility adapters.

## Prepare HD previews and local comparisons

```sh
# Requires Pillow and Poppler, or Docker for PDF rendering; maintenance only:
python3 scripts/guide_previews.py prepare --templates three-cards
python3 scripts/guide_comparisons.py prepare --templates three-cards
python3 scripts/review.py guide --open
```

Lossless WebP thumbnails (640 px) and HD images (1600 px) are rendered directly
from clean compiled PDFs and versioned under `docs/slides/previews/`. HD files load
only when a detail is opened. Ordinary deck builds need no Pillow or converters.
Use `python3 -m pip install Pillow` in a maintenance virtual environment if needed.

Append `?maintenance=1` to the guide URL to expose **Original comparison** in the
HD inspector. It loads ignored local reference data only on request. Core comparisons
are prepared at 2000 px high with 50% overlays and text-masked graphic differences.
For official pages, run `lesson_review.py --deck <id> --pages <numbers>` after
rebuilding the lesson; see [lesson maintenance](../library/MAINTENANCE.md).
Original exports stay under ignored `design-references/figma/`; comparison data is
indexed in `build/checks/slide-guide/comparisons.js`. No separate gallery is generated.

Review geometry, typography, images and effects separately. Source-coordinate
checks and pixel residuals cannot certify every anchor within 5 px. Record
unmeasurable regions and intentional Inter/English adaptations explicitly.

## Explicit technical PDF exports and compatibility

```sh
python3 scripts/review.py selection --open
python3 scripts/review.py models
python3 scripts/review.py all
python3 scripts/review.py slide three-cards --content example
```

These commands retain compact, model and complete PDF exports under `build/review/`.
The full archive is built only on explicit request. `review.py pages --open` now
opens the guide filtered to cover, contents and closing. Old gallery URLs redirect
to this same guide and retain composition, variant and palette links.
Retained English teaching examples are available in Presentations and Reusable
blocks, alongside [complete example sources](../templates/EXAMPLES.md).

## Share unapproved work

```sh
python3 scripts/package.py --style studio --review
python3 scripts/package-studio-review.py --templates cover,three-cards,merkle-tree
python3 scripts/package-studio-review.py --selection
python3 scripts/validate-studio-review.py
```

Review ZIPs stay under `build/review/`; stable `dist/` artifacts are preserved.
See [releasing](RELEASING.md) for isolated validation and explicit approval gates.
On Windows use `py -3`; append `--backend native` for installed TeX Live/MacTeX.

The active three-card comparison uses `1900.svg` from the original graphics export,
verified against its inventory SHA-256. Its review command repeats the original
Italian copy so typography can be compared directly. Inter retains the original
text height and centred axes, with slightly different glyph widths from outlined
SF Pro; the previously accepted 10% icon reduction remains intentional.

The three-card layout uses the original extracted panel SVGs, prepared as PDF
for pdfLaTeX. SVG geometry and filters are retained; the filtered panels are rendered
internally at twice source resolution to avoid dark seams in Cairo PDF masks. Pre-extracted PNG panels are
not used by this layout. Icons and captions remain separate editable layers.

The three-card composition was approved on 2026-11-11. Its default icons fit
a common 216 × 216 source-unit envelope (54% of the 400-unit panel), preserving
aspect ratios and centres. This supersedes the earlier individual 10% reduction.
The active review is now `icon-cards`, variant `two` (Cards), with equal 76-unit
caption sizes, centred 660-unit caption boxes and up to two lines.
See `examples/studio-two-cards.tex` for short, automatic and explicit wrapping.

Icon replacement in `icon-cards` variants `two` and `three` uses a shared
216 × 216 source-unit envelope, preserving aspect ratio and centred placement.
Use named `icon-one`, `icon-two`, `icon-three` catalogue keys or the corresponding
`image-one` / `graphic-one` keys; no explicit dimensions are needed.
The two-card review examples include wide and tall replacement artwork.

## Unified icon-card row review

The two-, three- and five-icon horizontal rows now share one renderer and the
`icon-cards` model. `variant=two|three|five` selects the item count;
`show-title=true|false` independently controls the heading. Every default and
replacement icon fits the same centred 216 × 216 envelope. The unified renderer was approved on 2026-11-12, including both heading states,
icon replacement, the 76-unit caption gap and fixed first-line alignment.
See [the complete row syntax](STUDIO-ICON-CARDS.md) and
[all title, text and replacement examples](../examples/studio-icon-card-rows.tex).

The unified `icon-cards` row family (two, three and five boxes) was explicitly
approved on 2026-11-12. Approved rows are
excluded from pending comparison output.

## Approved horizontal icon processes

The Cards family `icon-process`, variants `two`, `three` and `four`, was explicitly
approved on 2026-11-12,
with horizontal arrows. Public `caption-one` through `caption-four` follow
reading order. `title` is a heading only for `four`; the shorter original
processes have no heading. Captions share a 76-unit panel gap, centred fixed
76-unit typography and 88-unit leading, with capacity for two lines.
Original artwork remains the default; replacement icons fit 216 × 216.
See [short and long examples](../examples/studio-icon-process.tex).

Compatibility audit: inspected all 29 inventory assignments to these three
compositions and the related milestone, statistics, split-process, outline,
transaction, signature, encryption and proof-of-work layouts. The compatible
horizontal icon sequences use the same two/three/four-stage variants with different
captions and artwork. Similarity assignments are candidates, not approvals.
Originals with additional headings above two or three stages (figma-0566/0567
and figma-0825/0826/0827) need separate review for those headings; current
commands intentionally expose a heading only for four stages. Five hanging
milestone badges and multi-row or branching diagrams are separate compositions.
This approval covers the three reviewed canonical compositions, not every
inventory example or the hanging-badge composition, now exposed separately as
`milestone-badges`. Approved process comparisons have been cleaned up locally.

## Approved hanging milestone badges

The Cards composition `milestone-cards` was explicitly approved on 2026-11-12, exposed as
`milestone-badges` with its default `five` variant. Its original is `8907.svg`
(figma-0105), verified against the inventory hash. Five hanging badges differ from
horizontal arrow processes, so the old `icon-process/milestones` command was
replaced rather than retained as an alias.

```latex
\studiotemplate[
  title={Missions},
  badge-one={Plan B Forum\\El Salvador},
  badge-two={Barcelona\\Cypher\\Conference},
  badge-three={BitCuneo},
  badge-four={BitCare Forum},
  badge-five={BTC Prague}
]{milestone-badges}
```

Badge text uses fixed 72-unit type and 84-unit leading, the original left anchors
and capacity for three lines. Measured text blocks share the original visual
centre regardless of line count. The centred heading supports two lines. Short copy,
automatic wrapping and explicit breaks are demonstrated in
[the canonical example](../examples/studio-milestone-badges.tex). This template
was explicitly approved after restoring the original text alignment. Its old local
comparison and trial PDFs have been removed; source examples and guide previews remain.

After approval, remove obsolete local batch outputs and disposable export trials;
keep canonical examples, prepared graphics, current guide previews and recorded
approval decisions. Unresolved review work and stable releases remain available.


## Approved unified soft cards

All ten `text-cards` compositions in Cards were explicitly approved on
2026-11-12 after text-weight correction and editable-icon verification. The
`soft-cards-01` and `soft-cards-02` ledger records remain as review history.

See [all variants, optional content and the exact syntax](STUDIO-SOFT-CARDS.md)
and [all short and longer text examples](../examples/studio-soft-cards.tex).
Approved compositions are excluded from pending-review PDFs. The icon examples
also cover custom images, wide/tall artwork, hidden icons and longer copy.

## Approved Divisions grids

The four- and eight-icon variants were explicitly approved on 2026-11-12.
They use matching numbered caption and icon keys.
See the [complete commands and replacement rules](STUDIO-DIVISIONS.md).

## Approved twelve-word grids

The plain and annotated layouts share `word-grid`, separately from icon grids.
Both were explicitly approved on 2026-11-12 after the paper and body-weight
corrections. General card-shadow refinement remains a deferred cross-family task.
See the [word list, numbering and annotation commands](STUDIO-WORD-GRID.md).

## Three icon levels

The Lists family `levels`, in the original light and blue palettes, is approved.
See [commands, caption capacity and editable icons](STUDIO-LEVELS.md) and
[the short and longer examples](../examples/studio-levels.tex).

## Label and explanation rows

The Lists family `labelled-rows` is approved. See [grouped commands and text capacity](STUDIO-LABELLED-ROWS.md).

## Approved two-column bullet list

The approved Lists model is `title-two-column-list`, from BTC Prague 106.
See [commands, per-item indentation and capacity](STUDIO-TWO-COLUMN-LIST.md).

## Approved sponsor presets

The approved Lists compositions are `partner-rail` (figma-0996) and
`partner-media-grid` (figma-0930), retained as preconfigured sponsor slides.
See [preset commands, bold contacts and original logo sizing](STUDIO-SPONSORS.md).
