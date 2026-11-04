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
