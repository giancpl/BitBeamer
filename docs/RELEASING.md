# Prepare a release

Run from the repository root with the prerequisites in [setup](SETUP.md).
On Windows replace `python3` with `py -3`.

```sh
python3 scripts/release.py
# Explicit Docker alternative:
python3 scripts/release.py --backend docker
```

The command checks documentation links, compiles five documents, checks the
catalogue's freshness, creates the ZIP, and validates the extracted template.
PDF previews are exported after validation succeeds. Local scripts never
commit, tag, push, or publish.

Make provides the same workflow: `make release` or `make release BACKEND=docker`.
`--image NAME` or `LATEX_IMAGE` chooses a compatible Docker image.

## Release files

| File in `dist/` | Purpose |
| --- | --- |
| `bitbeamer-overleaf.zip` | Upload as a new Overleaf project |
| `bitbeamer-preview.pdf` | Compact template showcase |
| `bitbeamer-illustrations.pdf` | Small illustration example |
| `bitbeamer-catalogue.pdf` | All 171 icons with their commands |
| `bitbeamer-icon-cheatsheet.pdf` | Printable two-page usage reference |
| `bitbeamer-cover-layouts.pdf` | Both cover orientations, one per page |

The ZIP places the presentation and reference documents at its root. It also
includes theme files, the bibliography, prepared artwork, licences, an icon
guide, and an Overleaf quick start. An explicit file list excludes development
configuration, raw SVGs, local experiments, and unused artwork variants.

The validator compiles every document and explicit bull, wordmark, monogram,
and CrypTO variants in both cover orientations, plus 4:3 versions. It checks layout warnings, unresolved references, and
recorded inputs for dependencies on the source checkout. The extracted documents
compile with pdfLaTeX and Biber, without Python or shell escape.

See the [local verification report](CHECKS.md) for completed checks and pending
hosted verification.

## Individual checks

```sh
python3 scripts/check-docs.py
python3 scripts/build-asset-catalogue.py --check
python3 scripts/prepare-assets.py --check
python3 -m unittest discover -s tests -v
```

To package only, then validate separately:

```sh
python3 scripts/package.py
python3 scripts/validate-release.py
# Or: python3 scripts/validate-release.py --backend docker
```

Packaging does not convert artwork or update tracked sources. Identical inputs
produce identical ZIP bytes. Regenerate changed artwork and catalogues using
[the maintenance workflow](ASSETS.md) before packaging.

## GitHub automation

Python checks run on Linux, macOS, and Windows. Native Linux TeX runs the same
release command and checks source files remain unchanged. Branch pushes and
pull requests upload the six files as a workflow artifact.

A pushed tag starting with `v` publishes those files after all jobs pass.
Once the repository is reviewed, committed, and pushed, publish when ready:

```sh
git tag v1.0.0
git push origin v1.0.0
```

Creating local release artifacts does not perform either action. Report local
checks separately from GitHub jobs that have not yet run.
