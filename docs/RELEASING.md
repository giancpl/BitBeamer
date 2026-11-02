# Prepare a release

Ordinary editing and review do not require a release. Use [the review workflow](STUDIO-COLLECTION.md)
until the compact Studio selection has been reviewed.

## Validate candidates without changing stable files

```sh
python3 scripts/release.py --review
# With installed native TeX:
python3 scripts/release.py --review --backend native
```

This builds both designs, stages deterministic ZIPs, validates their extracted
projects and writes candidate artifacts under `build/review/release/`.
Previous files in `dist/` are untouched. Use `--style academic` or `--style studio`
for one design. Package-only candidates use `package.py --style all --review`.

## Stable artifacts

```sh
python3 scripts/release.py
```

Default: both styles, Docker. Add `--backend native` for installed TeX Live/MacTeX.
Stable Studio packaging requires every selected model's status to be `approved`
in [the review ledger](../templates/review.json). Supplementary models also require
an explicit approval. Selection alone is insufficient; no script grants approval.
All styles requested in a release must validate before any final file is replaced.

| Artifact | Contents |
| --- | --- |
| `bitbeamer-academic-overleaf.zip` | Academic showcase, themes, icons and references |
| `bitbeamer-academic-preview.pdf` | Academic presentation |
| `bitbeamer-overleaf.zip`, `bitbeamer-preview.pdf` | Identical Academic compatibility aliases |
| `bitbeamer-studio-overleaf.zip` | Selected Studio compositions, prepared dependencies and individual guides |
| `bitbeamer-studio-preview.pdf` | Selected Studio showcase |
| `bitbeamer-studio-templates.pdf` | Labelled catalogue of the selected Studio models |
| `bitbeamer-illustrations.pdf`, `bitbeamer-catalogue.pdf` | Icon examples and all 171 illustrations |
| `bitbeamer-icon-cheatsheet.pdf`, `bitbeamer-cover-layouts.pdf` | Printable icon guide and Academic cover variants |

The full 194-model review catalogue is separate from stable release previews.
Both ZIPs open their own showcase as `main.tex` and include an editable `start.tex`. Studio includes only selected models
and compatible aliases whose current compositions are included. The complete library
remains in the repository; custom subsets and split review packages remain available.

Prepared PDFs and the complete 171-icon registry are included. Raw SVGs, original
frames, scripts, IDE and Docker configuration are excluded. Studio targets 45 MiB;
archives over 50 MiB are rejected. An oversized selection requires smaller review
exports or an intentional selection change; packaging never silently drops models.
The ZIP is deterministic for unchanged inputs and uses normalized text line endings.

## GitHub checks and publication

Portable checks run on Linux, macOS and Windows. Native Linux builds Academic,
the selected Studio project and the full Studio review catalogue, then validates
extracted packages. Branches and pull requests validate unapproved candidates;
version tags additionally require approval before stable artifacts can be published.
Local and hosted check results are recorded separately in [the report](CHECKS.md).

No local script commits, tags, pushes or publishes. Creating a future `v*` tag and
pushing it is a separate explicit action; the configured workflow publishes the
validated named assets only after its checks pass.
