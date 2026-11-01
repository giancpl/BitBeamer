# Studio library data

Edit `studio/<id>.tex` for a composition, `index.json` for its field/measurement
metadata, and `review.json` for notes, status, ordered selection and examples.
There is exactly one source per current composition. Compatibility aliases share it.

`REVIEW.csv`, `CATALOGUE.md`, `SELECTION.md` and `studio/registry.tex` are generated
by `python3 scripts/review.py sync`. Do not edit them directly.
`measurements.json` and `figma-inventory.json` retain original-source measurements
and provenance. They are maintenance data, not daily review forms.

See [the workflow](../docs/STUDIO-COLLECTION.md).
