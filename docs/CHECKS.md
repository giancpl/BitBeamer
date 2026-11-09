# Verification report

## Five-social-only closing and handle calibration — 2026-11-09

The four-social drawing and both social-count selectors have been removed.
The review batch now contains only `closing`, paired with the introduction's
page 11. The combined review PDF contains nine pages. Existing individual social
replacement fields retain their numbering; the QR remains enabled by default.

The visible handle was too large: 564 × 110 px versus the reference's 538 × 100 px
at 3556 × 2000. Fixed Inter Semibold size 58.9 and tracking 27 now reproduce the
reference ink bounds exactly at the measured white threshold: `[2268,819,2806,919]`.
Copyright uses separately calibrated size 34.2 and tracking -43; its edge residuals
are `[0,-1,2,0]` px. Glyph forms remain Inter, intentionally distinct from the
original outlined font. No image or text stretching is used; text stays selectable.
Measurements and original/current crops are under
`build/review/batches/closing-01/typography/`.

The closing definitions now live in `images/studio/closing/layout.tex`, included
in standalone and subset exports and explicitly tracked by the two actual guide
consumers. Code outside the extracted closing definitions is byte-identical.
The 749 unaffected guide records and 554 unaffected lesson thumbnails were reused
only after validating their original fingerprints and image hashes, and proving
that all non-closing dependencies were unchanged with the old theme hash.
The local `cache-migration.json` records this proof. The closing previews and the
consuming eleven-page introduction were rebuilt sequentially.

Six example pages, the isolated closing-only export, original/current comparisons,
QR on/off and custom content were inspected. Runtime checks reject the removed
selectors and still reject invalid fields and overflow. Repository review and
lesson freshness checks pass. The closing remains in review; previous approvals
for covers, Team and agendas are retained. This section supersedes the previous
four-social compatibility state below. No commit or publication was made.

## Closing defaults and combined comparisons — 2026-11-09

The shared Studio closing helper and catalogue adapter now default to five socials
(Telegram, Instagram, X, GitHub and YouTube), `@BitPolito` and the QR enabled.
The four-social reference remains available through `variant=four-socials` in the
helper or `socials=4` in the catalogue. YouTube remains graphic slot 4, QR remains
slot 5, and the additional GitHub override uses slot 6. The artwork importer
preserves independently prepared resources when refreshing the four-social crops.

`review_batch.py all --compare` creates one bookmarked, ten-page PDF at
`build/review/batches/comparisons.pdf`: five covers, Team, two agendas and the two
closing references. The four-social comparison explicitly selects `socials=4`;
the ordinary catalogue command retains the five-social default. Both closing
comparisons use `@BitPolito`. All ten pages were inspected visually.

The nine-page closing example passed compilation and diagnostics, including both
social counts, QR on/off, custom fields and subsequent calls. Inter is embedded.
The exported closing-only package includes GitHub and compiled in a Docker mount
containing only the extracted archive. All 19 official presentation builds passed;
the 751 command previews were refreshed. Four overlapping preview writes were
reconciled sequentially before the final freshness check. The affected closing
overlay and the combined comparison PDF were refreshed.

`review.py check`, `library.py check`, the PDF page/title/bookmark checks and
`git diff --check` passed. The 187-test run exposed two outdated archive assertions
that omitted the shared agenda component introduced by the preceding correction.
Those assertions now check the declared dependencies and both passed on rerun;
the other 184 tests passed, with one existing environment skip. No failures remain
unresolved. Closing designs remain in review; the previous cover, Team and agenda
approvals are retained. No commit, publication or stable release was created.

## Agenda typography refinement — 2026-11-09

The four- and five-item Studio agendas were calibrated against the same wording
as their pinned original references, independently of the neutral English defaults.
Title and item sizes compensate the shared Inter scale; all items within each
layout now use one size. Left anchors were corrected for glyph side bearings.
Prepared panel paths and placements are unchanged. Academic, approved covers and
Team were not modified by this correction.

In the initial source-copy calibration at 2000 px height, measured ink starts
differed by at most 3 px and ink heights by
at most 3 px for the calibrated strings. Word widths still differ between Inter
and SF Pro; this is an intentional typography difference, not a certificate for
arbitrary replacement text. Local measurements are retained in
`build/review/batches/contents-01/typography/measurements.json`.

Docker builds passed for the two published commands, four neutral/ready-content
examples, custom fields, empty fields, an automatic five-section contents page
and a subsequent normal Studio frame. Both excessive-text cases failed with the
correct composition/field diagnostic. The consuming BitGeneration mining deck
and its previews were rebuilt. Thirteen targeted agenda/guide tests passed.
The guide previews and both local original overlays were refreshed.

A subsequent user request centers the actual item text vertically within every
original panel, including labels with descenders. A shared agenda-only helper
preserves the existing measured-text overflow checks; subset exports retain that
helper. Four neutral/English examples show ink-center offsets below 0.5 px at
2000 px height. This intentional vertical adjustment supersedes the initial
source-top alignment. Current measurements are in
`build/review/batches/contents-01/typography/centering.json`.
Both corrected agenda compositions were explicitly approved by the user on
2026-11-09. Closing compositions are the next review group. No stable release,
commit or push was produced.

## Canonical library update — 2026-11-06

The catalogue now backs both ready-content packs and personal imports. New imports
copy editable content and references, while linking canonical layouts and shared
artwork. Legacy snapshots require explicit migration; other personal projects were
not changed. The unified guide separates **Ready** and **In review**, with no
inferred approvals.

Completed locally:

- **20 source documents / 602 mapped pages**, including the 19 pinned official PDFs
  and the supplied 11-page introduction: **19 decks, 223 blocks, 555 unique slides**.
- **242 strict deck/block builds passed**. Every page calls a registered canonical
  template or fixed preset. Ten fixed presets expose no customization fields.
- **751 command examples** have current compiled 640/1600 px lossless previews;
  the guide publishes 729 composition choices. Initial core data is 404,835 bytes.
- **183 portable tests completed without failures**, with one optional Inkscape-dependent test skipped;
  15 runtime cases cover custom/empty fields, overflow, fixed-slide restrictions,
  four/five-social closing variants, invalid options and return to normal frames.
- Clean source copies in paths containing spaces passed Docker and native TeX
  **inside the container**. Independent private content, image/bibliography separation,
  duplicate/overwrite rejection and unchanged shared sources were verified.
- A temporary canonical colour correction changed an imported deck's rendered
  preview without changing its personal TeX. Restoring the shared source restored
  the original rendering. The experiment ran only in the disposable source copy.
- The BitPolito pack imports independently, with all 11 pages and linked layouts.
  The active personal deck retains its inline `main.tex`. Its first ten pages are
  pixel-identical to the preserved PDF at 1600 px width; the closing intentionally
  uses the shared five-social engine and repaired continuous vector GitHub mark.
- Academic remains pixel-identical in 16:9 and 4:3, eleven pages each. Both review
  Overleaf ZIPs compiled after isolated extraction, including catalogue, icon guide,
  bibliography and applicable logo/layout variants. Stable releases were not replaced.
- The offline Chromium guide check passed pagination, lazy HD, fields, copying,
  search, redirects, status filters, sequence navigation and mobile layout.
  Local 2000 px original/replica comparisons for all eleven new pages are available
  through the same guide in maintenance mode; no new gallery was introduced.

Evidence: `build/checks/canonical-library/report.json`, `build/library/report.json`,
`build/library/workflow/report.json`, `build/library/runtime-checks/report.json`,
and `build/checks/slide-guide/browser/browser.json`. These are ignored local outputs.
Full originals and comparison images remain local; the clone retains prepared
artwork, commands and clean previews. Checks reject unknown/private layouts,
unregistered dependencies, incomplete page mappings and altered retained artwork.

Limits: graphical/content approval remains pending; source team figures, partner
claims and links are draft historical content. Host-native TeX is not installed;
Windows, macOS and GitHub-hosted execution remain CI checks. Existing CI invokes
the extended import, runtime, guide and clean-clone checks. No commit or push was made.

## Earlier verification — 2026-11-05

The following sections retain the previous baseline and its historical counts.

Local verification: **2026-11-05**, Linux. All Studio designs remain in review;
technical verification is not graphical approval.

## Single visual reference

[The slide guide](slides/index.html) is the only maintained slide browser. It has
Templates, Presentations and Reusable blocks views, with 12 cards per page.
The initial dataset is below **400 KiB**; additional layouts and lesson data
load on request. HD images open only in the inspector. The clone contains both
**640 × 360** thumbnails and **1600 × 900** lossless WebP previews, rendered from
clean PDFs without catalogue labels. No browser server or original files are needed.

| Coverage | Count |
| --- | --- |
| Core Studio models / compositions | 101 / 196 |
| Featured models / retained featured choices | 21 / 24 |
| Active additional lesson layouts / fixed presets | 517 / 9 |
| Published composition commands | 722 |
| Prepared examples, including complete deck sequences | 740 |
| Presentations / topic blocks / unique lesson slides | 18 / 221 / 544 |
| Source PDFs / original pages | 19 / 591 |
| Shared illustrations | 171 |

Old template, lesson and local-review URLs are small redirects, preserving query
parameters and IDs. Retired gallery generators and their independent datasets are
removed. Icon and graphic-part catalogues are retained. About **2.47 GiB** of
superseded local review output was deleted after feedback and useful evidence were
recovered; personal snapshots, originals and stable releases were preserved.

## Graphical feedback and corrections

The editable ledgers contain **93 core observations across 62 compositions** and
seven lesson observations. They combine conversation feedback and archived review
notes, with a problem, canonical action and verification evidence. A full 196-slide
overview was inspected; 42 priority compositions received an original/current audit.

Corrections include:

- Consistent cover author roles, with Regular institute/detail text and Semibold headings.
- A protocol relay correctly classified as `protocol/message-relay`; compatible
  `cover/script` and `cover-script-blue` access remains available.
- A three-milestone timeline correctly classified, with its previously embedded
  middle value editable. Quotations use one paragraph and a separate attribution.
- Coherent checklist numbering, separate arrow labels, and tighter measured cells
  in the outcome matrix and layered overview.
- Editable ninth labels in both twelve-tile compositions, with retained blank panels.
- Regular supporting card copy, preserved Semibold headings, and white native QR
  foregrounds on blue canvases.
- Shared problem/solution panels and quotation consumers preserved and rechecked.
  Three-card icons retain the agreed 10% reduction and their original centres.
- Transaction-node numeric text allocations fit inside the original nodes across
  Inter metrics, preserving centres, values, font sizes and prepared artwork.

Canonical sources and all affected guide examples were updated together. Existing
personal copies remain independent. New and corrected designs were not approved.

## Completed technical checks

- **171 portable tests:** 170 passed; one optional Inkscape check skipped on this host.
- All **740 prepared commands** compile with embedded fonts and no reported overflow,
  missing characters or unresolved references. Every published variant/palette is covered.
- **45 Studio runtime cases** and **eight lesson cases** cover customization, empty
  fields, icons, normal-frame isolation and expected invalid-input/overflow errors.
  Compatibility adapters and the semantic `body` option are exercised.
- All **239 complete lessons and standalone blocks** pass strict page-count, font,
  selectable-text, bibliography and diagnostic checks. Preview fingerprints are current.
- Both Overleaf packages compile after isolated extraction, including icon catalogues,
  cheat sheets, branding variants and Studio components. Prepared packages require no
  checkout, conversion, Python or shell escape for their TeX builds. Both ZIPs
  are reproducible, with unchanged package contents since isolated validation.
- Docker and the native launcher inside the TeX container pass the private-deck
  workflow in a clean source copy with spaces in its path. Private assets,
  bibliographies, caches, duplicate rejection and source isolation are checked.
- Chromium verifies desktop and 390 px mobile layouts, search, copy, pagination,
  HD details, editable-area overlays, variant/palette links, legacy redirects and
  optional local comparisons. No JavaScript errors or HTTP requests occur.
- Offline checks validate Markdown and deferred guide links, generated-file freshness,
  HD hashes/dimensions, and the absence of retired gallery generators.
- Academic is pixel-identical to the baseline in **16:9 and 4:3**, eleven pages each.
  The accepted fixed supply slide is unchanged. **1,049 protected source/artwork
  hashes** match the earlier baseline.

## Local comparisons and limits

The same guide exposes local originals with `?maintenance=1`. Prepared comparisons
cover 193 core compositions at 2000 px and the existing 591 official source-page
references. Seven reported card/quotation lesson pages were explicitly refreshed.
Inter and English copy are intentional adaptations; diagrams, effects and text
must be assessed separately. Pixel residuals do **not** certify every component
within 5 px. Grouped paths, raster regions, shadows and optical spacing remain
subject to review. Detailed approval of all lesson layouts is still open.

Host-native TeX is not installed. Native launcher verification ran inside the TeX
container. The previous GitHub run exposed a Windows default-encoding failure and
two narrow transaction labels under TeX Live 2025. Path-based text reads and writes
now specify UTF-8; the example tests also pass with UTF-8 locale coercion disabled.
Extensionless graphic imports keep forward-slash TeX paths on Windows.
The transaction text boxes were widened within the existing nodes. Portable
Windows/macOS and native Linux/browser verification is configured in GitHub Actions;
the new run must confirm these corrections on those platforms.

The detailed report, feedback coverage and baseline/browser evidence are under
`build/checks/studio-unified/`; command and preview records are under
`build/checks/slide-guide/`. Stable releases and personal projects were not replaced.
The repository changes were committed and pushed at the user's explicit request.
No release, publication or automatic graphical approval was performed.

## Small-family graphical review — covers-01

The first active review batch contains four editable cover compositions and the
fixed BitPolito wordmark cover. Five canonical commands were compiled into one
five-page PDF; a separate five-page original/replica PDF and a generated review
sheet remain local under `build/review/batches/covers-01/`. The existing guide
shows these five compositions separately and opens local comparisons directly.

Ten targeted guide tests and the offline Chromium check passed, including exact
batch ordering, one card per composition, comparison loading and mobile navigation.
No design was approved or graphically corrected by this preparation. Earlier
pixel-identity claims for ten BitPolito pages compared against our pre-migration
reconstruction, not a certification of fidelity to the source draft. Matching
anchors and successful compilation do not replace the pending visual review.
Additional lesson topics are now kept separate from visual families; unclassified
layouts remain visible as Needs classification until reviewed.

## Closing handle weight — 2026-11-09

User feedback identified excessive apparent boldness. The shared closing component
now selects Inter Medium locally, with a fixed 60-unit size, 27 tracking and
y=443.1. The core `closing` and clone-only `bitpolito-contact` share this style;
only `bitpolito-introduction-11` consumes the latter. Global headings are unchanged.

Compared Semibold, Medium and Regular renders against the original page 11.
Medium gives lighter stems; the original outlined font has different glyph
proportions, so this remains an optical adaptation in Inter. At 3556 by 2000,
the handle ink bounds are [2268, 819, 2806, 920], versus the original
[2268, 819, 2806, 919]. Inter Medium is embedded in the rebuilt PDF.

Refreshed the consuming deck, both guide entries and the nine-page combined
comparison. Visually inspected QR on/off, custom and empty copy, default resets
and the catalogue adapter. The closing remains in review; no new graphical
approval is inferred. Verification results are recorded with the local build logs.

Validation: `review.py check`, `library.py check`, documentation links and
`git diff --check` pass. The full suite ran 187 tests: 184 passed and one
environment-dependent test was skipped. Two package tests initially encountered
the closing preview while it was being refreshed; both passed when rerun after
preview generation. No test failures remain.

## GitHub closing panel — 2026-11-09

The GitHub artwork used a fully exposed 3.24-unit outline on a 104.22 × 98.81
canvas, while the other closing assets clip their panel to 103 × 98. This made
the GitHub border visibly heavier. `images/studio/closing/github.svg` now reuses
the Telegram panel path and clip, with the same 103 × 98 canvas and white.
The retained GitHub pixel artwork is centred without changing its silhouette.
Updated the prepared PDF, its provenance manifest and affected resource hashes.

At 20× render scale the visible left border is 1.60 units for GitHub and Telegram;
the other icons measure 1.60–1.65 units due to their original subpixel offsets.
Visually inspected all five panels, QR on/off, custom copy, the core adapter and
the consuming introduction closing. Refreshed both guide entries and the combined
nine-page comparison. The user's tentative “then I think it is fine” is retained
as feedback rather than a separate explicit graphical approval.

Validation: all 187 unit tests completed successfully (one environment-dependent
skip). `review.py check`, `library.py check` and `git diff --check` pass.
The consuming deck reports no compilation or font diagnostics.

## PDF opening in editor reviews — 2026-11-09

Review commands now delegate to the same editor-aware PDF viewer as ordinary
builds. Added the VS Code task “build and open all comparisons”, with `--open`
on both its Python and Windows commands, and documented the terminal invocation.
Interactive review instructions retain `--open` for subsequent updates. The
previous batch invocations omitted this option; generating a PDF alone does
not request its opening. Workspace PDF associations already select LaTeX Workshop.

Validation: 23 targeted build, viewer and batch tests pass, including editor reuse
and Windows command handling. The installed LaTeX Workshop extension was found;
the VS Code CLI accepted opening the existing combined comparison.

## Closing approval and QR option — 2026-11-09

The user explicitly approved the final five-social closing after typography and
GitHub-panel corrections. Recorded approval for `closing` and its blue palette
in the review ledger and refreshed the unified guide. This approves the closing
composition, without approving other lesson content or publishing a release.
Verified that both `\closingframe` and `\studiotemplate{closing}` retain
`qrcode=true` by default and accept `qrcode=false`. The latter hides the QR and
centres the same handle/social group; the previously rendered on/off examples
remain current. No rendering or geometry changed in this approval update.

## Closing QR confirmation and next review — 2026-11-09

Recorded the user's explicit confirmation after viewing both QR-on and QR-off
closing previews. Preserved the approved closing and its boolean QR option.
Registered `dividers-01` for the next unapproved featured composition,
`section-divider`, and its local reference `figma-0697`. It remains in review.
No template geometry, artwork, font or lesson content changed.

Refreshed the unified guide and prepared the section-divider comparison as
page 10 of the combined review PDF, retaining the nine previous comparison pages.
Interactive review builds request opening in the existing VS Code window.

Validation: `review.py check`, all 12 slide-guide/batch tests and
`git diff --check` pass. Inspected the freshly compiled section-divider comparison
and verified all ten pages and the final composition ID in the combined PDF.
The combined PDF and focused section-divider comparison were opened via VS Code.

## Optional section sequence and multiline examples — 2026-11-09

Added an editorial sequence in `templates/models.json`: `section-divider` then
`statement-arrow`. Both unified-guide cards expose ordered links and Copy sequence;
each primary command still creates one independent slide. Other statement variants
do not inherit the recommendation. Generated both model guides from this metadata;
subset guides omit a sequence if either composition is unavailable. Fixed portable
documentation so clone-only example links do not escape a standalone package.

The section divider now accepts two title lines at its original fixed font size.
Its second line grows upward by one baseline step, preserving the original
one-line position and gap above the rail; three lines report overflow. The arrow
statement retains its original geometry and handles two lines within its existing
text box. No personal decks, approved wrappers or Academic layouts changed.
Dependency tracing found no canonical lesson consumers for `section-divider`.

`examples/studio-section-pair.tex` demonstrates eight pages: three optional pairs
(short, longer automatic wrapping, explicit line breaks), followed by two
independent arrow statements. Both preview and example PDF use compiled artwork.
The combined original/template review has eleven pages, with the pair on 10–11.
Both compositions remain in review; the relationship is not graphical approval.

Validation: the eight-page PDF was visually inspected, including automatic and
explicit wrapping on both models and standalone arrow slides. Extracted text
confirms two lines; the font remains 28.457 pt for all divider examples and
9.693 pt for all arrow examples on the standard Beamer canvas. At an 800 px
render width, both adjoining connectors occupy pixels 399–400. All 20 runtime
cases pass, including valid two-line pairs, independent arrows, rejected third
lines, empty content, option reset and existing closing/palette checks.

The offline Chromium guide check passes with no JavaScript errors or network
requests; it exercises sequence copying, navigation to the standalone arrow
and absence of the suggestion on unrelated variants. `review.py check` and
`git diff --check` pass. The two portable-guide/package tests pass after fixing
the clone-only example link in standalone documentation.

The complete suite ran 192 tests. One package test initially used the old
portable-link transformation before that fix was loaded; rerunning both affected
package/portable-guide checks passes. The remaining full-suite cases pass, with
one environment-dependent skip. No unresolved test failures remain.

## Section-pair approval and remaining statements — 2026-11-09

Recorded explicit user approval for `section-divider` (blue) and `statement-arrow`
(light), including their optional sequence, independent use and reviewed two-line
behavior. Approval metadata and the unified guide are synchronized; no geometry
or font changed in this approval step. Other statement variants remain in review.

Registered `statements-01`: `glow-statement`, `blue-statement`, `oversized-word`.
Their original references are `figma-0793`, `figma-0121` and `figma-0895`. The
combined comparison retains the previous eleven pages and adds these as pages
12–14. `examples/studio-statements.tex` supplies six representative short/longer
examples using existing fixed font sizes and native palettes. The credit variant
is a compatibility alias for a timeline and is outside this statement batch.

Validation: all 192 unit tests pass (one environment-dependent skip).
`review.py check` and `git diff --check` pass. Visually inspected all three
original/current comparisons and all six short/longer examples. The sample
PDF reports no text/overflow diagnostics and embeds Inter Semibold. Verified
the combined PDF has fourteen pages with statement bookmarks at pages 12–14.
Opened the combined PDF, six-page examples and focused statement comparison
in the existing VS Code window. No approval is inferred for these three variants.


## Radial statement background and text review — 2026-11-09

User feedback concerns the gradient background and colors. The retained SVG now
includes the original `#F9F9F9` paper as well as the radial effect. Its preparation
composites the original color and opacity interpolation jointly onto that paper
using 257 opaque vector stops. The PDF has no soft mask; the original gradient
transform, central `#001CE0` and stop positions are retained. This avoids relying
on the PDF viewer's transparency compositor without rasterizing the background.
A numerical regression checks the original transform, endpoints and midpoint.

The statement is also measured before drawing so that one or two lines center on
`(1793, 1000)` at the original 120/136 size. The 1386 × 290 capacity is unchanged;
three lines still produce an explicit overflow error. The example deck now has
seven pages, including short text and automatic/explicit two-line glow examples.
The library dependency audit identifies `bitpolito-introduction-04`, the
`bitpolito-introduction` deck and the `bitpolito-mission` block as consumers.
The composition and native palette remain in review; no approval is inferred.

Validation: all 193 unit tests pass (two environment-dependent skips); all 23
runtime cases pass, including the three new glow cases. `review.py check`,
`library.py check`, the 751-entry guide-preview check and `git diff --check`
pass. Visually inspected all seven custom-text pages, the refreshed original
comparison at combined page 12/14 and the mission slide in both consumers.
Confirmed that the prepared gradient PDF contains zero soft masks. Regenerated
the component thumbnail, template/guide previews, consumer previews and focused
comparison sheet; opened the combined PDF and the short/long example PDF in the
existing VS Code window. Compilation is not graphical approval.


## Radial statement banding correction — 2026-11-09

The user reported visible concentric bands after the multi-stop vector attempt.
That preparation is superseded. The canonical background now samples the original
continuous elliptical color/alpha profile on `#F9F9F9` at 3556 × 2000 pixels.
Deterministic stochastic rounding keeps every RGB channel within one code value
of the continuous result while breaking equal-color quantization contours. The
lossless image is embedded only as the background; the statement stays selectable,
editable vector text at the same fixed font size. The PDF background has neither
shading objects nor soft masks, avoiding viewer-specific gradient tessellation.

Retained SVG geometry, center `(1793, 1000)`, radii, stop locations and colors are
unchanged. Numerical tests cover the source transform and profile, reproducible
preparation, bounded error and neutral average rounding. The seven-page example
deck still covers short, automatically wrapped and explicitly wrapped text.

Registered `images/studio/parts/radial-glow.pdf` as an explicit resource of
`bitpolito-introduction-04`: the existing wrapper linked its template but omitted
this prepared part. The wrapper also selected a separate legacy drawing; it now
uses the canonical background. Asset-only corrections now select and invalidate
the mission slide, `bitpolito-introduction` deck and `bitpolito-mission` block.
The superseded lesson drawing is retained; personal presentations are independent. Graphical
status remains in review.

Validation: exercised 194 unit tests with two environment-dependent skips. Two
archive checks initially encountered the glow preview while it was regenerating;
both pass on rerun after preview synchronization. All other suite cases pass;
the 29 lesson-library cases and seven current-source cases also pass separately.
`review.py check`, `library.py check`, documentation links and `git diff --check`
pass. Both lesson PDFs now embed the actual 3556 × 2000 canonical background;
their mission-page renders are identical. Inspected those renders, all seven
example pages and combined comparison page 12/14. Automatic and explicit wrapping
produce the same two-line result at 14.540 pt, with no text/overflow diagnostics.
Updated the prepared part, component thumbnail, template/guide/lesson previews
and focused contact sheet. Opened the refreshed comparison and text examples;
no graphical approval is inferred.


## Soft glow visual redesign — 2026-11-09

The user rejected the previous background again and requested a suitable visual
transition. This revision changes the actual falloff rather than its encoding:
a soft elliptical Gaussian replaces the flat central stop and its slope break.
The center stays at `(1793, 1000)`, with sigma 800 × 530 source units. Brand blue
`#001CE0` fades directly toward `#F9F9F9`; the statement keeps its fixed geometry,
Inter typography and editable vector layer. This is an intentional adaptation of
the original composition, awaiting explicit graphical review.

The extraction recipe records the Gaussian adaptation and sigma. Extraction
applies the same authoring helper used for the retained SVG, so a later extraction
does not restore the rejected flat stop. Prepared artwork evaluates the profile
continuously at source resolution and retains the existing bounded stochastic
rounding. Tests check a strictly changing profile near the center, smooth
first derivatives across the former stop boundary, source color/center, and
reproducible, bounded, unbiased quantization. Short and both automatic/explicit
longer-text examples are retained for review. The original references remain
unchanged; no new palette or automatic approval is introduced.

Validation: all 194 unit tests pass (two environment-dependent skips).
`review.py check`, `library.py check`, documentation links and `git diff --check`
pass. Verified that applying the adaptation recipe to the local original export
reproduces the retained gradient attributes and all SVG stops. Inspected all
seven example pages, combined comparison page 12/14 and the mission page in both
consumers; those consumer renders are identical. The example PDF has no text or
overflow diagnostics; short and automatic/manual two-line statements retain the
same 14.540 pt font. Updated the part, part thumbnail, template and guide previews,
lesson previews and focused comparison sheet. Opened the updated combined PDF
and example deck; retained a full-size long-text preview for the visual review.
No approval is inferred from these checks.


## User-supplied statement background — 2026-11-09

The user explicitly selected an SVG background. Copied it verbatim into
`images/studio/parts/source/statement-glow-background.svg`, replacing the
experimental background. SHA-256:
`721e582ce42c2fcb7c471e41076df56089ac7a0f61e9e25f375999988e2a1b84`.
The original download is unchanged. Its original filename and hash are recorded
in the part's provenance; the public `radial-glow` part ID/PDF name stays compatible.

Removed the previous Gaussian authoring, analytical sampling and dithering code.
The background now renders directly from the supplied SVG, with its own geometry
and colors, at 3556 × 2000, then embeds losslessly in the PDF. Editable text stays
separate, at the same font size and capacity; its horizontal center now matches
the supplied artwork at `(1778, 1000)`. The retained-source extraction branch
preserves the supplied bytes and works without the older original frame export;
a regression test covers that behavior. The superseded experimental SVG is removed.

The supplied background is an explicitly chosen component; the complete statement
composition remains in review. Short, automatic-wrap and explicit-wrap examples
are retained alongside the other statement variants.

Validation: all 193 unit tests pass (two environment-dependent skips).
`review.py check`, `library.py check`, documentation links and `git diff --check`
pass. Verified that the retained SVG and supplied download are byte-identical.
Inspected all seven example pages, combined comparison page 12/14 and the mission
page in both affected consumers; those consumer renders are identical and embed
the supplied background at 3556 × 2000. The example PDF has no text or overflow
diagnostics; short and automatic/manual two-line statements retain the same
14.540 pt font. Refreshed the part, template, guide and lesson previews, along
with the focused comparison sheet. Opened the combined comparison PDF and
longer-text example deck. No approval of the full composition is inferred.


## Fixed supplied PDF statement background — 2026-11-09

The user supplied `statement.pdf` and a transparent `Ellipse 67.png` after rejecting
the SVG conversion. The supplied PDF contains the background only (one 1920 × 1080
page, two vector drawings, no text or images). It is retained as
`images/studio/parts/source/statement-glow-background.pdf` and copied byte-for-byte
to the compatible `images/studio/parts/radial-glow.pdf`, with SHA-256
`f82a19c0aeb0655052322423f56340367570089b5d80a5c45c0f2274c77ad61d`.
No conversion, rasterization, clipping, recoloring or reconstruction is performed
on this PDF asset. The supplied transparent PNG is retained unchanged under
`images/studio/parts/source/resources/statement-glow-gradient.png` as an alternative
asset, not composited into the active background. The previous supplied SVG remains
an inactive source; its raster preparation branch and generated PNG are removed.
The current comparison reference is the newly supplied PDF. Independent editable
text retains its existing fixed typography and centered one/two-line geometry.
Extraction and preparation preserve the native PDF; regression coverage checks
that both the source and prepared output retain the complete supplied bytes.
The complete composition remains in review.

Validation: six Studio source tests pass, including byte-identical PDF extraction
and preparation. The batch tests pass (one optional dependency skip in the default
Python environment). `review.py check`, `library.py check`, documentation links
and whitespace checks pass. Regenerated canonical/guide/part previews, both linked
consumers and unified comparisons. Both mission consumer renders are identical,
with no raster images embedded. Inspected all seven short/long example pages and
one/two-line statements at the same 14.540 pt font; compilation has no text or
overflow diagnostics. Comparing native background and compiled page at 1600 × 900,
excluding text, gives mean RGB residual below 0.031/255 per channel.

Following further user feedback, retain this native PDF provisionally without
visual approval. Prepared a local comparison-only transparent-PNG alternative,
placing the unchanged 1774 × 1080 image at (73, 0) on a 1920 × 1080 #F9F9F9 page.
Compiled short, automatic-wrap and explicit-wrap text with the same canonical
layout via a local part-path override. Neither supplied asset removes the visible
central blue region in the rendered comparison. The current unified PDF includes
two supplementary PDF/PNG comparison pages (15–16), and both the examples and
unified PDF were opened. Canonical sources continue to use the supplied native
PDF; the PNG alternative is not a new approved layout or automatic replacement.


## Standard paper for the fixed statement background — 2026-11-09

The user requested standard #F9F9F9 paper. Confirmed that the theme defines
`studio-paper` as F9F9F9, while the supplied PDF's solid paper fill used 0.975 per
channel. Preserved the original supplied PDF and created the active derivative
`images/studio/parts/source/statement-glow-background-f9f9f9.pdf`.
Only the solid paper color operator in form stream 13 changes to DeviceRGB
249/255 per channel; every other decoded stream remains byte-identical to the
supplied PDF, including gradient color functions, alpha functions and masks.
No gradient reconstruction, rasterization, text geometry or font change occurs.
The retained-source recipe copies this derivative to `radial-glow.pdf` unchanged.
Its SHA-256 is `fae641b41caa8f1b8b6f0a61ac791f70fa5f317a4ca999e66ef56535eecda115`.

Verified the native derivative and all three compiled short/automatic-wrap/manual-
wrap statement examples render the exposed paper as exact RGB (249, 249, 249).
The six Studio source tests pass. Visually inspected the three updated statement
examples at their existing fixed font size. Original PDF and transparent PNG
sources remain available; complete composition stays provisionally in review.

Refreshed part/template/guide previews, linked mission block and introduction deck,
short/long example previews, and all comparison batches. Both consuming mission
pages render exact (249, 249, 249) corner pixels with zero embedded raster images;
their renders are identical. `review.py check`, `library.py check`, documentation
links and whitespace checks pass. Inspected combined comparison page 12 and the
three current statement examples. Reopened the 16-page unified comparison,
including the retained short/long PDF-versus-PNG supplemental pages 15–16.
No graphical approval is inferred.


## Direct full-width supplied PNG — 2026-11-09

The user again requested the supplied PDF as background or PNG as a large image.
The canonical `glow-statement.tex` now includes the supplied PNG directly with
`\includegraphics[width=3556\studiounit]`, centered at (1778, 1000) on studio-paper
#F9F9F9. It does not call the prepared PDF for its background. The original PNG file
and hash are unchanged (`599aef6363f467d49ba17edba5ee4281f2ee4bf4797d8c3ea0095d3b496c9ae5`).
The 1774 × 1080 image is enlarged proportionally to full slide width; the canvas
clips only excess height, equivalent to y=-44.442 and height=1168.884 on 1920 × 1080.
No SVG conversion or gradient reconstruction occurs. Text remains independent.
The matching standalone `radial-glow.pdf` is retained via the fixed PDF-copy recipe
for part reuse; its alpha samples and opaque color samples match the source PNG.
Original supplied PDF and inactive prior derivatives remain available.

Six source tests pass. Compiled all seven example pages and inspected the three
statement examples: each embeds a 1774 × 1080 image and retains a 14.540 pt font,
including automatic and explicit two-line wrapping. Recorded a separate local
three-page original-PDF baseline with identical text/layout for comparison against
the current full-width PNG. No visual approval is inferred.

Updated part/template/guide previews, linked mission block and introduction deck,
and unified review. Both linked mission pages embed the supplied 1774 × 1080 PNG
and have identical rendered hashes. Visually inspected the canonical comparison,
the current longer-text examples and both consumer outputs. Added short/long
original-PDF versus direct-PNG comparisons as pages 15–16 of the unified PDF and
opened that PDF and the examples. Source tests, review/library consistency checks,
documentation links and whitespace checks pass. PNG use is provisional and no
approval is inferred.


## Statement cleanup and two-column review — 2026-11-09

The user requested cleanup of the unsuccessful gradient experiments and continuation.
Retain one provisional native-PDF background at the supplied original proportions,
with only the solid paper rectangle normalized to standard #F9F9F9. The canonical
template again uses the prepared radial-glow part. Gradient streams and independent
editable text are retained. The issue remains open; this is deferral, not approval.
Removed the superseded SVG and full-width PNG-derived PDF, plus the local
png-alternative, pdf-reference and image-background-review output directories.
Original supplied PDF and PNG inputs remain available. Unified comparison
regeneration removes the experimental supplementary pages automatically.

Added the columns-01 review batch for two-columns, the next selected composition.
Its comparison uses a short neutral example. The official studio-two-columns.tex
example includes short, longer automatic-wrap and explicitly wrapped bodies and
introduction, using the public semantic fields at unchanged font sizes. All three
pages compile successfully and have been visually inspected for alignment, gaps,
wrapping and clipping. A deliberately excessive body produces an explicit
Text overflow in two-columns/text-2 error instead of shrinking the font.
The six Studio source tests, documentation links and whitespace checks pass.
No statements or column composition are newly approved.

Refreshed the retained background, template/guide/part previews and both lesson
consumers. Their mission renders are identical, with no embedded raster images.
Regenerated the combined review to 15 pages: no experimental supplements remain,
and two-columns is page 15 with its own bookmark. Inspected the original/current
column comparison and all three longer-text examples. Reopened the example PDF
and combined comparison. Review and library consistency checks, six source tests,
batch tests (one optional dependency skip), documentation links and whitespace
checks pass. Removed the temporary overflow trial after recording its expected
failure in build/review/two-columns/report.json.


## Pending-only interactive review — 2026-11-09

The user requested exclusion of already confirmed slides and a concise list of
pending compositions with their categories at each handoff. Review batch builds
now filter by catalogue approval status, covering both core templates and fixed
lesson presets. Fully approved batches are skipped in the combined PDF. Mixed
batches retain only unapproved compositions in registered order. Direct requests
for a fully approved batch stop before compilation/opening rather than presenting
an old approved PDF. No review status or approval ledger is changed.

Comparison headers now identify the canonical catalogue category. Batch reports
record categories; the combined report lists pending IDs, categories and batches.
The current combined review contains four pages: glow-statement, blue-statement,
oversized-word (Statements), then two-columns (Lists). The glow remains deferred
and unresolved, not approved. The interactive handoff convention is recorded in
AGENTS.md so subsequent reviews report only pending names and categories.

Four targeted tests pass with the optional PDF maintenance tools available. They
cover approved core/fixed entries in mixed batches, approved-only batches,
category headers/reports, navigation, order and opening behavior.

Regenerated and opened the four-page pending-only PDF. Verified every header,
page count, order and bookmarks against the pending report; all eleven approved
compositions are absent, including the fixed wordmark cover. Inspected the four
comparison pages. Review consistency checks, documentation links and whitespace
checks pass. No slide design, lesson source or approval status was changed.


## Two-column text sizes and usage command — 2026-11-09

The user found the overall layout suitable but requested a careful typography
check and an actual usage command at each handoff. The two headings previously
used different source-scale sizes (84.5507 and 85.1373); the introduction used
74.0627 while both bodies used 75.16. Normalized the hierarchy to title 120/140,
both headings 90/105, introduction and both bodies 80/95 (size/leading). Source
outlined cap-height ratios support the common hierarchy: title 84.551, heading
63.413 and introduction 56.367; this is geometric evidence, not embedded font
metadata. Retained Inter, Semibold weights, original anchors and text capacities.
No text is shrunk to fit. Updated canonical metadata, guides and previews.

All three short/automatic/manual-wrap examples compile without overflow or missing
characters. Their PDF font sets are identical: 14.540 pt title, 10.905 pt headings,
9.693 pt introduction/body. Inspected all three pages for wrapping and clipping.
A deliberately excessive body still fails with the clear two-columns/text-2
capacity error; the temporary failing document was removed after recording its
expected result. No linked lesson slides, decks or blocks use this core template.

Comparison PDFs now print the exact public command used to compile the shown
example, including batch field overrides. Command lines wrap without splitting
LaTeX tokens and receive enough page space. The four-page pending-only PDF retains
canonical categories; verified the actual two-column command at page 4 and opened
the comparison and longer-text examples. Five targeted review-batch tests pass,
including a regression distinguishing the reviewed invocation from catalogue
defaults. Handoff guidance in AGENTS.md requires the matching public command.
Final visual approval remains pending.


## Descriptive two-column LaTeX fields — 2026-11-09

The user requested clearer LaTeX commands. The two-columns model now publishes
`title`, `introduction`, `left-title`, `right-title`, `left-body` and `right-body`.
The prior label-two through label-six keys remain compatibility aliases to the
same native fields; raw slot access is unchanged. Optional composition-level
field_aliases are validated against canonical keys and emitted through the existing
semantic-key registry. No template geometry, font size or drawing is changed.

Updated the official short/long examples and review batch invocation, generated
model guide, registry and unified slide guide. The complete model-guide example
now shows every named field for this composition and compiles successfully.
Old aliases are documented as compatibility names, not preferred command fields.
The usage command below the PDF comparison follows the new names automatically.

Fourteen model tests pass, including new checks for public fields, retained aliases,
guide coverage and rejection of shadowed/unknown alias targets. Compiled the
four-page studio-two-columns-api fixture: canonical keys, numbered labels and both
mixed-key orders render identically (same 2x-resolution hash on all four pages).
The three short/automatic/manual-wrap examples compile and retain the same three
font sizes and visual layout. Original capacities and overflow behavior remain
unchanged. No graphical approval is inferred.


## Two-column approval and syntax replacement — 2026-11-09

The user explicitly approved `two-columns` and requested replacement of obsolete
command syntax, without compatibility aliases. The public fields are now `title`,
`introduction`, `left-title`, `left-body`, `right-title` and `right-body`.
The older `label-two` through `label-six` keys are rejected. The optional field-alias
feature from the previous experiment has been removed; examples, registry, model
guide, review status and maintainer instructions use the replacement syntax.
This entry supersedes the alias behavior described in the preceding check log.

The complete public-command fixture compiles. A negative compilation using
`label-two` fails explicitly with "is not available in two-columns/default".
The existing short, automatic-wrap and explicit-wrap examples retain the approved
geometry and typography. The approved composition is excluded from pending PDFs.

Verification: 197 tests ran (one optional-environment test skipped). Two packaging
tests initially found the previous two-column preview signature; after refreshing
that preview, both passed on rerun, together with all five review-batch tests.
`review.py check`, `library.py check`, `check-docs.py` and `git diff --check` pass.
The remote was fetched before committing; local main had no incoming commits.
