# Verification report

Verified locally on **2026-11-04**, on Linux. Studio is ready for individual graphical
review; compilation and structural checks do not approve a design.

## Current collection

| Item | Count |
| --- | --- |
| Grouped Studio models | 101 |
| Retained composition presets | 196 |
| Featured models | 21 |
| Preserved featured composition choices | 24 |
| Existing compatibility aliases | 9 |
| Shared illustrations | 171 |

[models.json](../templates/models.json) records variants, semantic fields and original
palette choices. [review.json](../templates/review.json) remains the editable source
for notes, status, ordered selection and examples. No graphical approval was inferred.

A composition advertises only its original colour treatment. The retained light/blue
`levels` pair supports a palette switch. Compact light and large blue icon spotlights
remain different variants because their original proportions differ. No synthetic
opposite-colour slide sources, artwork or thumbnails remain.

## Completed local checks

- **133 portable tests:** 132 passed; one optional Inkscape converter check skipped.
  Coverage includes complete legacy membership, semantic mappings, real palette
  selection, unsupported choices, subset exports, dependency invalidation, cached
  single-slide reuse, review preservation and deterministic packaging.
- All **196 native composition defaults** compile in the full vector catalogue.
  Their 196 native previews and all generated registries and guides are current.
  Semantic defaults use descriptive English; old example values and original
  references remain in maintenance metadata.
- **43 real compiler cases** pass: editable and empty fields, icon fitting, structured
  text, aliases, missing resources, unknown fields and variants, explicit overflow,
  original palette switching, fixed-colour fallback and ordinary-frame isolation.
  Invalid cases fail with the expected diagnostic.
- The grouped vector catalogue and quick overview each contain **101 pages**.
  The quick PDF is approximately **4.93 MiB**, with selectable command captions and
  no blank interleaved pages. Its builder verifies the final page count. The separate
  vector catalogue preserves selectable slide text and full graphics quality.
- The selected catalogue and showcase contain **21 pages**. All 24 previously
  selected composition IDs remain in the ledger; the compact project additionally includes
  the two optional BitGeneration cover sources, measured four/five-item agendas
  and the team introduction.
- The main Studio review ZIP compiles independently: showcase, editable starter,
  all 171 illustrations, icon cheat sheet, selected catalogue, customization examples,
  wrapped headings and Studio components. pdfLaTeX and Biber run without a checkout
  mount, SVG converters, network access or shell escape.
- An additional isolated four-composition project verifies both original `levels`
  colours and both icon spotlight variants. Its catalogue, guide example and explicit
  bibliography verification compile; embedded fonts are checked.
- A clean source copy in a directory containing spaces builds the Studio showcase
  with the native launcher and the starter with Docker. Native TeX runs inside the
  existing Linux compiler container; the host has no separate native TeX installation.
- The offline gallery renders in Firefox. It presents grouped models, existing
  variants, palette controls only for original pairs, semantic field names and
  matching copyable commands. Filtering and bounded pagination have behaviour tests;
  image previews and comparison details load progressively.
- Offline documentation links, prospective Git content, prepared-artwork hashes,
  generated-file freshness and whitespace checks pass. Review ZIPs remain below
  the 45 MiB target and reproduce identical bytes for unchanged inputs.

## Focused title, contents and closing review

`python3 scripts/review.py pages` compiles 14 existing catalogue compositions:
four cover candidates, four agenda candidates, one closing, plus five related or
misclassified layouts in a separate group. `cover-script-blue` currently renders
a process diagram and is flagged rather than treated as a title-page candidate.
`tabbed-agenda` and `agenda-with-icons` are flagged as visually similar.

Both PDFs have exactly 14 pages. The quick overview is approximately 0.74 MiB;
the separate editable/vector catalogue is approximately 12.24 MiB. Review labels
are outside the slide canvas. All 14 canonical commands resolve to their exact
source compositions and native palettes. Gallery images and local links exist.
The overview fonts are embedded; slide text remains selectable in the vector PDF.
The existing 14 review-workflow tests pass, and the read-only repository review
check passes. The ledger, selected layouts and approvals remain unchanged.
These artifacts are local review outputs, not stable release replacements.

## Ready content and neutral reusable layouts

Verified on 2026-11-03. All 194 compositions are preserved. Retained English text
is recovered for 180 compositions; the other 14 keep their current defaults.
Original prepared graphics previously replaced by neutral placeholders are selected
through explicit numbered graphic slots. No layout, artwork source or approval is
duplicated or changed. The historical code block's doubled escapes are decoded in
the example generator without altering the archived content.

- The complete ready-content source compiles to exactly 194 pages, with no text
  or graphic overflow, overfull boxes, missing glyphs or unresolved references.
  Its optional vector PDF is approximately 178 MiB and remains an ignored local
  output; ordinary galleries do not load it.
- The independent neutral shortlist contains title, contents and closing: three
  pages, approximately 70 KiB. `reusable_selection` is editable in the review ledger;
  the existing showcase selection and graphical approval states are preserved.
- All 14 opening/closing candidates also compile with recovered content. Their
  separate quick PDF is approximately 0.81 MiB. Both gallery paths and original
  reference links are checked; switching modes does not replace neutral thumbnails.
- The 114-test portable suite passes (113 passed, one optional Inkscape check
  skipped), including new content-restoration and neutral-default isolation cases.
  Generated source and guide freshness, offline links and Git content checks pass.

English reconstructions remain editable examples. Historical numbers and links
need checking before reuse; original Figma exports stay local and optional.
Release artifacts and theme defaults are unchanged.

## Studio default and Academic

`main.tex`, the default build task and the no-argument package/validation commands
now select Studio. Explicit Academic commands and the legacy Academic theme name
retain their behaviour. The launcher follows local TeX inputs when checking artwork,
so the default wrapper performs the same checks as `main-studio.tex`.

- The default `build/main.pdf` is pixel-identical to the selected Studio showcase
  on all **21 pages**, compared at 480px width.
- Academic's Overleaf `main.tex` is the **four-slide editable starter**.
  `academic-showcase.tex` preserves the full example; the theme retains its existing
  layouts, options, font and all 171 illustrations. `make start-academic` builds the starter.
- Review ZIP sizes are approximately **0.58 MiB for Academic** and **15.24 MiB
  for Studio**. The Academic archive contains no Studio layouts, parts or registry.
  Both archives reproduce the exact validated bytes.
- Isolated validation covers the short Academic main, optional full Academic showcase,
  logos, covers, 4:3 variants and bibliography, plus the selected Studio project.
  The validator passes the selected style explicitly into its compiler container.
- Studio's graphical approval gate still applies to stable exports. All new packages
  are review candidates under `build/review/`; stable files and legacy download
  names were not replaced.

## Academic and graphical evidence

Academic layout files and shared font/palette configuration are unchanged. The saved
Academic baseline comparison records **11 pixel-identical pages**, at 800px width,
for both **16:9 and 4:3**. Studio's 194 source canvases, measured field boxes and
native drawing geometry retain their recorded dimensions.

Local original/replica comparisons remain under ignored `design-references/figma/`.
They include 2000px-high renders, overlays and separate graphical comparisons.
Neutral wording and image placeholders are intentional differences from the original
content. These comparisons are review evidence, not a claim that every original
matches within five pixels or that visual refinement is complete.

Use [the grouped gallery](templates/index.html), [model guide](STUDIO-MODELS.md)
and [review workflow](STUDIO-COLLECTION.md) to choose and refine one composition.
Full-resolution originals, comparison PDFs, build logs and candidate packages stay
outside Git. The full 194-composition vector archive is an explicit export.

## Repository structure cleanup

The README and documentation map now lead to separate authoring, graphical review
and maintenance workflows. The repository map and directory guides identify editable
sources and generated references. Theme files and public TeX paths remain in place.
The contribution entry point links to the same workflows.

Obsolete empty palette manifests and duplicate-palette bookkeeping were removed.
Real neutral images, icon contrast files and shared geometry remain explicit package
dependencies. Cache folders are ignored and rejected by the prospective Git-content
check; VS Code search excludes generated builds and local original exports.

The 111-test suite passes (one optional converter check skipped), and all **327
Markdown files** pass offline link checks. A source-only copy in a path containing
spaces passes the complete read-only review check and compiles the default Studio
presentation with Docker, without original Figma exports. Both review ZIPs are
byte-identical to the candidates from before this cleanup. Build and release files
remain local; no stable artifact replacement, commit or push was performed.

## Studio standard presentation pages

The editable Studio starter now contains **five pages**: cover, automatic contents,
two content examples and closing. The theme provides `\studiotitleframe`, the
existing `\studiotocframe` with an optional heading, `\studioframe` for a simple
aligned body, and the existing `\closingframe`. They are available without the
optional catalogue package. Normal Beamer frames and catalogue commands remain supported.

Three additional real compiler cases verify metadata, actual section names in the
contents, optional subtitle reset, empty fields, theme-only use, invalid options
and return to an ordinary frame after closing. All **21 content cases** and the
111 portable tests pass (one optional converter test skipped). The refreshed Studio
ZIP compiles in isolation, including its five-page starter and catalogue examples;
its portable documentation links also pass.

All **194 catalogue preview PNGs remain byte-identical** after recompilation, and
their dependency fingerprints are refreshed. No measured composition or Academic
layout was changed. The standard pages are authoring helpers, not new catalogue
variants or automatic graphical approvals. Stable release files remain untouched.

## Hosted checks and remaining decisions

Linux, macOS and Windows launcher checks and native Linux builds are configured in
CI. They were not run on GitHub during this local change. macOS and Windows are not
claimed as locally tested environments.

Remaining decisions are graphical corrections, explicit approval and final selection.
Stable release artifacts were not replaced. No commit, push, tag or publication was
performed. See [release instructions](RELEASING.md) for the separate approval gate.

## Studio cover selector

Verified on 2026-11-03. `\studiotitleframe` defaults to the existing classic blue
cover. `variant=bitgeneration` and `variant=bitgeneration-photo` select the retained
light and photo catalogue sources using the document title, author and institute.
Canonical `wide-pattern` and `photo` names remain accepted; `classic` aliases the
default. Every call resets its cover choice. Subtitle/date slots remain exclusive
to classic, and the photo composition requires a short, single-line title.

- All 25 real content cases pass, including cover metadata, empty values, option
  reset, normal-frame colours, missing optional library and invalid variants.
- All 194 catalogue previews are pixel-identical after recompilation; fingerprints
  are refreshed only after this comparison. All five default starter pages also
  match their previous rendering at 480px width.
- The compact Studio review ZIP includes the two optional cover sources, their
  prepared graphics and guides. The existing catalogue/showcase selection is
  unchanged. The archive is approximately 15.24 MiB, below the 45 MiB budget.
- Isolated archive validation passes all documents, including a new cover-variant
  fixture. The 114 portable tests pass: 113 passed and one optional Inkscape check
  skipped. Sources, guides, links, prepared-artwork checks and Git hygiene pass.
- Stable packaging requires explicit approval for optional covers as well as the
  showcase selection. No review state, Academic layout or stable release is changed.

## Four- and five-item Studio agendas

Verified locally on 2026-11-03. The existing four-item composition (`figma-0575`)
and a newly separated five-item composition (`figma-0883`, also represented by
`figma-0589`) are grouped under the same `agenda` model. The library now has
195 compositions behind 100 model cards. All previous IDs remain available.

- `variant=panels` and `variant=panels-five` share semantic `item-one` through
  `item-four`/`item-five` fields. Legacy four-item field names remain compatible.
  Title text areas extend into the empty left column for English headings;
  source anchors, font sizes, card geometry and native light treatment are retained.
- The five-item layout retains seven extracted vector panels with masks and
  gradients. Their independently checked source bounds differ by at most
  0.00001 pixels at a 2000px reference height, below the 5px geometry tolerance.
  Derived SVGs, prepared PDFs and provenance are retained for converter-free builds.
- Automatic `\studiotocframe` variants read actual top-level section titles and
  share the manual templates' geometry. Subsections are ignored, unused slots
  stay blank, and excess sections/unknown fields/text overflow report errors.
  The existing flexible default contents layout is preserved.
- All 32 compiler cases pass, including the seven agenda-specific scenarios.
  The 117-test portable suite passes: 116 passed, one optional Inkscape check skipped.
  Additional package and agenda-specific checks pass after the final export update.
- The neutral catalogue compiles to 195 pages. Only the revised four-item preview,
  the added five-item preview and the closing catalogue page number differ;
  all other 192 existing previews are pixel-identical. Prepared-part and model
  gallery caches, generated sources, guides and relative links are current.
- The four-page editable agenda example is approximately 82 KiB. A separate local
  comparison page pairs each replica with its original export. Original comparison
  material remains outside Git and release packages.
- The Studio review ZIP compiles in isolation, including both automatic agenda
  variants and the manual examples. It includes prepared panels and both variant
  sources. The reusable shortlist contains title, both agendas and closing;
  the existing showcase selection remains unchanged. Stable releases are untouched,
  and no composition or palette was approved automatically.

## Supplied team introduction

Verified locally on 2026-11-04. The user-supplied `team-presentation.pdf` is the
1920 × 1080 reference for the new `team` model (`team-presentation` composition).
The original 1,073-frame inventory is unchanged; the external PDF reference and
its hash are recorded separately. The model remains in review.

- The editable starter and `examples/studio-team.tex` each compile to six pages,
  following cover → team → contents → two content frames → closing. The selected
  showcase remains unchanged; the team command is explicit and optional.
- Four values and four captions are selectable Inter Semibold text. Original
  numbers are retained as example data, not live statistics. The generic model
  has a neutral fourth caption; the helper and ready-content example restore the
  supplied Bitcoin wording.
- The collage is retained as one replaceable vector illustration. Poster lettering,
  photographs, QR and badges remain artwork. Separate text-free panel decoration
  preserves the original outlines, masks, edge fades and crops. Images are copied
  without recompression; no full-slide bitmap is embedded.
- Both original and reconstruction are rendered at 2000px height, with a side-by-side
  and 50% overlay in `build/review/team/index.html`. Inter substitution and the fixed
  text inside artwork are documented in `docs/STUDIO-TEAM.md`.
- All 196 compositions compile. Comparing refreshed thumbnails shows every previous
  composition unchanged except the closing catalogue page number. The new model
  and its prepared-part hashes participate in dependency-scoped cache checks.
- All 37 real content cases pass, including team customization, empty fields, image
  replacement, unknown keys, overflow, unsupported palette and normal-frame isolation.
  The 120 portable tests pass with one optional converter check skipped.
- The Studio review ZIP is approximately 20.35 MiB, below the 45 MiB budget. Independent
  extracted-archive compilation passes the starter, complete team example, custom
  team fields, both agendas, cover variants and existing release fixtures. Packaging
  remains byte-reproducible. The archive ships only prepared PDF parts, without the
  original PDF, importer, raw references or JSON maintenance metadata.
- Academic layouts, shared fonts, brand palette and all 171 source illustrations
  are unchanged. Stable release files, approvals and the showcase selection remain
  untouched. No commit, push or publication was performed for this addition.

## Optional QR on the Studio closing

Verified locally on 2026-11-04. The supplied `final-slide.pdf` defines the standard
blue ending with a white social handle, four social icons, top copyright and QR.
`\closingframe` and the compatible catalogue adapter now use one layout engine.

- `qrcode=true` is the default for both APIs. `qrcode=false` hides the QR and centres
  the same text/social group. Title, optional subtitle, copyright and custom QR
  images remain editable. Every call resets; invalid booleans and overflow fail
  with explicit diagnostics. The catalogue retains all previous field names and
  numbered slots, plus an optional subtitle and fifth graphic slot for the QR.
- The original 2277 × 2277 JPEG QR stream and alpha mask are retained without
  recompression. Social glyphs and outlined panels remain vector. Prepared PDF
  parts, source hashes, exact crops and a maintenance-only importer are retained.
  Ordinary compilation needs no converter or PDF library.
- All 43 real compiler cases pass. Closing-specific cases verify reset to true,
  both catalogue modes, invalid values, missing images, overflow and ordinary-frame
  isolation. A disabled QR is not loaded, including when its image path is missing.
  All 120 portable tests pass with one optional Inkscape check skipped.
- The full 196-page catalogue and its previews are refreshed. Only the closing
  differs among previously tracked slide images; Academic layouts, shared fonts,
  brand palette, the 171-icon library and the other Studio compositions are unchanged.
- `examples/studio-closing.tex` compiles to five comparison pages. The starter retains
  the six-page cover → team → contents → content → closing sequence. The original,
  QR-on, QR-off and 50% overlay are available at `build/review/closing/index.html`,
  rendered at 2000px height.
- The main Studio review ZIP includes both closing modes and prepared parts. The
  extracted archive compiles independently, including the toggle/reset fixture,
  theme-only closing, complete examples and existing release checks. Packaging is
  reproducible and stays below the 45 MiB budget. Full reference PDFs, import scripts
  and JSON maintenance records remain excluded.
- Review approval, stable release files, commits and remote branches are unchanged.


## Private deck authoring (2026-11-04)

The root [agent instructions](../AGENTS.md) and [authoring guide](AUTHORING.md)
define the brief, layout selection, local asset/bibliography paths and separate
technical/visual verification. `scripts/deck.py` reads the current metadata and
uses the existing build launcher; ordinary authoring does not regenerate the library.

Completed locally:

- All 133 portable tests completed: 132 passed and one optional Inkscape converter
  check was skipped. New coverage includes portable names, overwrite refusal,
  scoped inputs, isolated build paths, model/field discovery, diagnostic parsing,
  missing PDF tools, embedding checks and numbered preview cleanup.
- The real Docker authoring workflow passed for two Studio projects with distinct
  images and bibliographies using identical local filenames/citation keys. PDF,
  Biber and latexmk caches stayed separate. Cached compilation reused its PDF;
  overwrites, unresolved citations, overflow, placeholders and compilation failures
  produced the expected outcomes. Failed builds did not trust an older PDF.
- Repeated that workflow with the native backend in a clean copy of distributable
  sources at a path containing spaces. This used the installed TeX/Poppler tools
  inside the existing compiler container. No host-native TeX installation was
  available: its failure message was checked separately and correctly listed
  latexmk, pdfLaTeX and Biber with installation guidance, without starting Docker.
- Created and checked an additional Academic project. Git status was byte-for-byte
  unchanged before and after personal deck creation, compilation and previews.
  Repository hygiene rejects force-added personal sources; Markdown checks skip
  personal briefs while retaining the tracked presentation entry guide.
- The local `agent-workflow-demo` contains nine pages: classic blue cover, team,
  contents, statement, custom icon cards, a local image, checklist, bibliography
  and closing with QR. It builds with resolved citations, embedded fonts and no
  overflow or missing glyphs. Every page was visually inspected; its private brief
  records the separate inspection and illustrative team counters. The automated
  report deliberately does not claim graphical approval.
- All 43 existing real-compiler Studio content fixtures pass. Read-only library,
  documentation and prospective Git-content checks pass. All nine Academic theme,
  shared font/palette, starter and showcase source files match the Git HEAD baseline.
- Both review Overleaf ZIPs compile independently after extraction, including
  existing Academic logo/aspect-ratio checks and Studio customization/closing cases.
  Deterministic packaging and archive-local links pass the portable tests. Personal
  sources are absent from both ZIPs. Stable `dist/` artifacts were not replaced.

Local evidence is under `build/authoring-checks/`, with the demonstration PDF,
`check.json` and numbered page images under
`build/presentations/agent-workflow-demo/`. The native clean-copy evidence lives
under `/tmp/BitBeamer authoring clean clone/build/authoring-checks/`.
These are ignored working outputs, not distribution sources.

CI now discovers layouts on Linux, macOS and Windows and runs the real private-deck
workflow in its native Linux job. Hosted CI, native macOS/Windows compilers and the
interactive VS Code UI were not run locally. Existing portable tests validate task
configuration and launcher arguments. No library approval, commit, push or
publication was performed.
