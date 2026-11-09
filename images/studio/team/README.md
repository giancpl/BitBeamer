# Team slide artwork

These are cropped vector parts of the user-supplied `team-presentation.pdf`.
The full reference stays in ignored local review storage. `manifest.json` records
its SHA-256, original canvas and crop rectangles. Existing shared artwork is unchanged.

- `collage.pdf`: the original left illustration, including wordmark and poster lettering.
- `panels.pdf`: the original full-canvas background with outlined panels, masks and fades, with no statistics. The continuous canvas avoids a separate painted strip beside the collage.

PDF image streams are copied without recompression. These prepared PDF files are
also the retained vector sources; no SVG conversion is required to use or edit
the template. Statistics are implemented separately in LaTeX.

To repeat the original extraction for maintenance, install `pypdf` in a temporary
virtual environment and run:

```sh
python3 scripts/import-studio-team.py /path/to/team-presentation.pdf
python3 scripts/review.py sync
python3 scripts/review.py slide team
```

The importer checks the original document hash and its measured structure. A new
export needs a new measurement/extraction recipe rather than reusing operation
indices blindly. It refreshes the prepared-resource hashes in the template metadata.
Neither the importer nor `pypdf` is needed by normal compilation or Overleaf.
See [the team guide](../../../docs/STUDIO-TEAM.md) for editable fields and limitations.
