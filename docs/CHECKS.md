# Local verification report

Updated on 31 October 2026. Changes are organized into commits and pushed to
GitHub. No tags or release publication have been performed.

## Completed locally

| Check | Result |
| --- | --- |
| Python checks | The expanded suite covers repository hygiene, failed-release preservation, path aliases, packaging, and artwork. See the audit below for the current test results. |
| Documentation | Offline relative-link checks passed for the repository and both guides extracted from the ZIP. |
| Catalogue freshness | Read-only check passed; entries come from the live library and descriptive metadata. |
| Prepared artwork | All 171 assets are current; ordinary builds performed no conversion. |
| Source preservation | SHA-256 comparison of 361 source and prepared artwork files found no changes. Metadata and provenance files were retained. |
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
| ZIP reproducibility | Host Python 3.14 and container Python 3.11 produced byte-identical ZIPs from the same inputs; no compression library is needed. The allowlist excludes raw SVGs, scripts, Docker files, and IDE configuration. |

The host has no TeX installation. Native compilation was exercised inside an
existing Linux validation container using its TeX Live tools; the launcher used
its native backend there. Docker was selected explicitly for host builds.
The documented native installation steps are still required to build directly
on this workstation without Docker.

Final outputs are in `dist/`: the Overleaf ZIP, showcase, illustration example,
complete catalogue, icon cheat sheet, and two-page cover comparison. Additional
aspect-ratio and header preview PDFs are under `build/verification/`. These output folders are ignored
by Git.

## GitHub verification

[Run 41109201114](https://github.com/giancpl/BitBeamer/actions/runs/41109201114)
passed for commit `15cba3d`: launcher checks on Linux, macOS, and Windows,
native Linux TeX builds, all logo/cover variants, and independent ZIP validation.
The release-publication job was correctly skipped because this was a branch push.

## Repository and release audit

The 31 October audit preserves all 171 icon sources, prepared assets, and
provenance. Four redundant `.gitkeep` files were removed. Compiled root/example
PDFs and local archives are now explicitly ignored. `check-repo.py` rejects
tracked local outputs; CI uploads only the six named release artifacts.

The release script checks inputs before compilation and stages the ZIP and
previews. Compilation/validation failures or missing preview files preserve
previous release outputs; regression tests cover these cases. No SVG conversion
is needed for ordinary builds or packaging.

The 33-test suite passes locally (32 passed and the host Inkscape test skipped).
The validation-container run also passes (its Git-only test is skipped because
Git is absent there). Full native Linux TeX release generation is checked from
an exported source copy in a path containing spaces, and the explicit Docker
release backend is checked from the source checkout. The earlier successful
GitHub run above covers the previous commit; see [current Actions runs](https://github.com/giancpl/BitBeamer/actions?query=branch%3Amain)
for the hosted results of the audit commit.
Hosted Overleaf UI and release publication have not been tested.

For commands to repeat these checks, see [releasing](RELEASING.md).
