# Closing artwork

Prepared parts come from the user-supplied `final-slide.pdf`; provenance, crop
boxes and hashes are recorded in `manifest.json`. Full references remain local.
The QR retains its original 2277 × 2277 JPEG stream and alpha mask without
recompression. Social icons and their outlined panels remain vectors.
The prepared PDFs are retained sources, not full-slide screenshots.

Normal builds and Overleaf require no conversion, Python PDF library or source
export. To repeat extraction from the measured reference, install `pypdf` in a
temporary environment and run:

```sh
python3 scripts/import-studio-closing.py /path/to/final-slide.pdf
python3 scripts/review.py sync
python3 scripts/review.py slide closing
```

The importer refuses unknown document hashes or content structures. New exports
need a newly measured recipe. It refreshes PDF hashes in the template metadata.
The shared 171-icon library is unchanged. See [the closing guide](../../../docs/STUDIO-CLOSING.md).

The default five-social closing includes `github.pdf`; its retained `github.svg`
comes from the supplied
`Presentazione BitPolito.pdf` introduction. Its panel reuses the Telegram outline and clipping path on the same 103 × 98
canvas, with matching white, border thickness and corner radii. Adjacent
pixel cells are snapped to one uniform grid and merged into continuous vector
outlines. See `github-manifest.json` for source crop and extraction notes.
Regenerate the prepared PDF from the retained SVG using the standard artwork
converter; full original decks are unnecessary for ordinary compilation.
