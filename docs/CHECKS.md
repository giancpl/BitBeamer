# Local verification report

Verified on 30 October 2026. Changes are organized into local commits. No
pushes, tags, GitHub runs, or publication were performed.

## Completed locally

| Check | Result |
| --- | --- |
| Python checks | All 27 tests passed with both SVG converters available. The host run passed 26 and skipped the Inkscape test because it is not installed on the host. |
| Documentation | Offline relative-link checks passed for the repository and both guides extracted from the ZIP. |
| Catalogue freshness | Read-only check passed; entries come from the live library and descriptive metadata. |
| Prepared artwork | All 171 assets are current; ordinary builds performed no conversion. |
| Source preservation | SHA-256 comparison of 360 original and prepared artwork files found no changes. Metadata and provenance files were retained. |
| Showcase | 11 PDF pages in both 16:9 and 4:3, with resolved Biber references. |
| Header | Short titles and subtitles share the nominal 22% minimum. Wrapped headings expand it; text and both logos remain in the solid blue region. The accent uses pale blue `#EEF0FF` and the `0.99` edge; both default header logos use the same 9.5% slide-height size, centered vertically with equal outer page margins. |
| Cover | The logos sit 9% below the top edge; title, subtitle, author, institute, and date share a left edge with the logos. Both `cover=image-left` and `cover=image-right` are included, with a two-page comparison. Optional logo pairs and the 4:3 layout were checked. |
| Branding | Default bull head and explicit BitPolito, bull, wordmark, monogram, and CrypTO options compiled from the extracted ZIP. |
| Complete catalogue | 22 pages; recorder output confirms all 171 prepared illustrations were read. Commands are printed beneath the icons in a three-column, three-row grid. |
| Icon cheat sheet | Exactly two A4 pages, with vector code fonts, rendered shortcuts, and copyable examples. |
| Icon API | Generic hyphenated names, sizing, rotation, existing-command preservation, and missing-icon warnings checked. |
| Clean project copy | Native launcher and explicit Docker backend built successfully from a copy without Git metadata or previous outputs, in a path containing spaces. |
| Overleaf package | All five documents, both cover orientations in 16:9 and 4:3, and the explicit logo selections compiled after extraction. Layout, missing assets, unresolved references, and recorded checkout dependencies passed validation. |
| Independent TeX build | All five documents also compiled with only extracted release files mounted, using `latexmk` and Biber directly, with no Python launcher, converter, source checkout, network, or shell escape. |
| ZIP reproducibility | Two packages from the same inputs produced identical bytes. The allowlist excludes raw SVGs, scripts, Docker files, and IDE configuration. |

The host has no TeX installation. Native compilation was exercised inside an
existing Linux validation container using its TeX Live tools; the launcher used
its native backend there. Docker was selected explicitly for host builds.
The documented native installation steps are still required to build directly
on this workstation without Docker.

Final outputs are in `dist/`: the Overleaf ZIP, showcase, illustration example,
complete catalogue, icon cheat sheet, and two-page cover comparison. Additional aspect-ratio and header
preview PDFs are under `build/verification/`. These output folders are ignored
by Git.

## Configured but not run on GitHub

- Python launcher, asset, catalogue, and documentation checks on Linux, macOS,
  and Windows.
- Native Linux TeX compilation, converter tests, isolated ZIP validation,
  source-change checks, and artifact upload.
- Publication of the ZIP and five PDFs after a pushed `v*` tag passes all jobs.

No actual macOS, Windows, IDE UI, or hosted Overleaf session was available for
local testing. Cross-platform command construction and editor configuration
are covered by the Python tests; hosted jobs remain pending.

For commands to repeat these checks, see [releasing](RELEASING.md).
