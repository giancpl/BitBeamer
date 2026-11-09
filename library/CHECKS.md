# Lesson-library checks

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

Local verification dated **2026-11-05**. All content and compositions remain
**in review**. Passing compilation is neither graphic nor editorial approval.

## Unified guide and current maintenance

Use [the slide guide](../docs/slides/index.html?view=decks) for complete lessons
and reusable blocks. Legacy review URLs redirect there. Clean 640 px thumbnails
and 1600 px lossless WebP details are included in the clone; optional local
comparisons open in the same inspector with `?maintenance=1`. Seven reported
card/quotation pages were refreshed, and the accepted supply page remains pixel-identical.
See [the current verification report](../docs/CHECKS.md) for coverage and limits.

## Coverage and technical builds

- Pinned source revision: `85e16ddeaaee1bda8842016710d3ce80f974c272` of
  [BitPolito/decks](https://github.com/BitPolito/decks).
- All **19 source PDFs / 591 pages** have an explicit editable destination in
  [the coverage table](COVERAGE.md). English/Italian duplicates share an English deck.
- **18 presentations, 544 unique slides and 221 thematic blocks**; 543 layout
  records, including shared templates and compatibility entries, plus nine
  fixed-content presets and 387 retained graphic parts. No source page is used as a
  complete-slide bitmap/PDF background.
- Every presentation and standalone block compiles: **239 strict builds**.
  Page counts, embedded fonts, selectable native text, bibliography resolution,
  missing characters and overflow diagnostics are checked. Artwork-only pages
  are explicitly distinguished from pages expected to contain native text.
- Eight runtime cases verify custom and empty fields, return to normal frames,
  custom graphics, unknown fields, unsupported palettes and explicit text/graphic
  overflow errors. Fixed geometry never silently shrinks user text.
- The portable suite passed **171 tests** (one optional converter check skipped
  on this host); Linux native-converter checks remain configured in CI.
- Import tests cover independent copies, aliases, missing insertion markers,
  duplicate imports, edited layout/registration collisions, bibliography collisions,
  traversal rejection and rollback on a failed write.

## Clone and distribution regression

- A clean copy of tracked and prospective sources was tested in a path containing
  spaces. Two separate private presentations were created per backend: a complete
  25-page lesson and a 15-page mixed deck with personal artwork and bibliography.
- Docker and the native launcher **inside the TeX container** passed. Host-native
  compilation was unavailable because TeX is not installed on this host. Windows
  and macOS checks are configured in CI and have not run as part of this local work.
- The copied lesson compiles with the shared `library/` folder removed. Importing,
  editing and building private projects leaves shared sources unchanged. Creating
  the local demonstration also left the working Git status unchanged.
- Academic renders are pixel-identical to a fresh `3138e899` HEAD baseline in
  **16:9 and 4:3**, eleven pages each.
- Studio and Academic Overleaf ZIPs are byte-identical to fresh packages built
  from that HEAD baseline. Both extracted packages compiled independently, including
  their examples and logo variants. Lessons and the optional lesson runtime are
  excluded; existing stable artifacts were not replaced.
- A representative vector part was regenerated from its retained SVG and image
  inputs without mounting original exports; its rendered pixels matched exactly.
  All retained part, prepared output and dependency hashes are checked offline.
  All 3,527 SVG image references resolve to retained, declared local dependencies;
  originals and network resources are not needed.

## Graphic and editorial review

All 19 sources have local original/replica comparisons at **2000 px height**,
50% overlays, graphics residuals and side-by-side PDFs. The local index is
`design-references/figma/official-decks/review/index.html`; it is intentionally
absent from a fresh clone. Use [maintenance commands](MAINTENANCE.md) to recreate it.

Visible source-outline colours were audited, including multiline white text that
hidden PDF text did not describe correctly. Residual outlined paragraphs were
separated from prepared graphics, avoiding overlap with their English LaTeX fields. The 25-page private demonstration was inspected for legibility,
contrast and clipping. Full collection approval remains pending.

Geometry remains measured in original coordinates with one uniform scale. Component matching reports which vector boxes
are within 5 px. **The 5 px criterion is not certified for every anchor:** grouped
paths, raster originals, effects and unmatched components require visual review.

Translations, corrected OCR, updated operational claims and historical examples
have separate provenance notes and dated primary references. Complex illustrations
and screenshots can retain English labels inside prepared graphics; these labels
are not all independent LaTeX fields. Full factual and visual approval remains
outstanding. No lesson or composition was approved automatically.

## Reproduce and inspect

```sh
python3 scripts/library.py check
python3 -m unittest discover -s tests -v
python3 scripts/check_lesson_runtime.py
python3 scripts/check_lesson_workflow.py --also-native-in-container
python3 scripts/library.py build --all --preview --jobs 2
```

Local machine reports live under `build/library/`: `report.json`,
`workflow/report.json`, `runtime-checks/report.json`, `regression/baseline.json`
and `part-regeneration/report.json`. PDFs are separated under `decks/<id>/` and
`blocks/<id>/`. The private example is `presentations/lesson-library-review-demo/`;
it is ignored and not distributed. CI is configured; no new GitHub execution,
commit, push, tag or publication was performed.

## Economics review corrections — 2026-11-05

- Economics 5 and 8, and their full-introduction counterparts, now share the
  `problem-solution` layout. Its 400 × 400 panels use the existing three-card
  panel asset with the complete shadow region. Icon slots and centred captions
  are independently editable; duplicate extracted card plates are not used.
- Economics 44 and full introduction 41 reuse the existing `chat-dialogue`
  quotation template. A single paragraph with deliberate line breaks replaces
  separately positioned lines; the attribution stays in its own field. Reusing
  the common panel geometry is an intentional change from the source-specific box.
- Economics 6 is exposed as `\studiotemplate{bitcoin-supply}`. Its current rendered
  pixels are identical to the previous library preview. The original PDF's fraction
  bar is not newly introduced: this review preserves the accepted reconstruction.
- Nine explicit [fixed-content presets](FIXED.md) accept no content or palette
  overrides. Their original source layouts remain available for maintenance.
  Fixed preset copying, registration and independent compilation were checked;
  this does not approve their content or geometry.

The current reference is the [unified slide guide](../docs/slides/index.html).
The earlier Economics preview and unchanged-slide check are preserved under
`build/archive/reviews/2026-11-05-slide-guide/library/economics-refinement/`.
Full source comparisons remain under the existing local review gallery. Academic,
its public API and stable release artifacts were untouched.

## Shared-template propagation — 2026-11-05

Canonical reuse rules now protect all four problem/solution slides and both
quotation cards. Checks reject their old replaced layouts, mismatched source calls,
missing shared components and undeclared retained dependencies. Merely listing an
unused component in metadata does not satisfy a reuse rule. Rules classify known
compositions; automatic visual-duplicate detection is not claimed.

Dependency discovery follows nested literal inputs and graphics, including inputs
without extensions. Cache signatures and personal imports use this dependency
closure, so a newly introduced shared helper cannot be omitted accidentally.
Eight additional regression tests cover propagation to every consumer, isolation
of unrelated slides, snapshot preservation, source binding, retired layouts,
missing/fake reuse and copying extensionless graphics.

The targeted shared-panel/quotation build passed for **two presentations and four
blocks**. All 544 preview signatures remained current; no slide artwork or layout
geometry changed during this tooling update. The clean-copy Docker workflow was
rerun successfully: separate 25-page complete and 15-page mixed presentations,
path with spaces, independent imports and unchanged shared sources. Existing
Academic and package regression results above remain from the earlier verification;
no new host-native, Windows/macOS or GitHub execution is claimed.

Use `library.py affected --changed <path>` to list consumers and
`library.py build --changed <path> --preview` to check them. Existing CI library
checks enforce the same rules. New imports get current fixes; previously copied
personal layouts remain independent and require an explicit merge.

## Unified slide guide — 2026-11-05

[The slide guide](../docs/slides/index.html) now combines core Studio models,
additional active lesson layouts and fixed presets, with one current preview and
copyable command side by side. Shared/retired entries are not duplicated. Lesson
commands come from the actual editable source that rendered each preview, preserving
line breaks and field overrides. Core variants expose their retained palettes only.

Six additional guide tests passed as part of **164 portable tests** (one optional
converter test skipped). They check complete composition coverage, exact lesson
calls, fixed-slide policy, stale-output detection, automatic core/lesson preview
refresh and bounded browser filtering/pagination. Seventeen representative commands,
including all cover/agenda variants, shared panels, quotation, Merkle tree and fixed
supply, compiled with embedded fonts and no log diagnostics. Desktop and mobile
Chromium checks passed, including a direct link to a selected variant. Current
technical output is `build/checks/slide-guide/`; older one-off reviews were archived
reversibly, preserving originals, caches and stable releases.
