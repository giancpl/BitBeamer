# Verification report

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
