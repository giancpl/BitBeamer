# Personal presentations

Create a deck from the repository root:

```sh
python3 scripts/deck.py new my-talk
python3 scripts/deck.py build my-talk
python3 scripts/deck.py check my-talk --preview
```

Studio is the default. Add `--style academic` when creating an Academic deck.
On Windows use `py -3`. Build/check accept `--backend native`; Docker is the default.

Each project contains `main.tex`, `brief.md`, `assets/` and `references.bib`.
Read [the authoring guide](../docs/AUTHORING.md) and [agent instructions](../AGENTS.md)
before writing. Outputs and caches live in `build/presentations/<name>/`.
Only this README is versioned; personal decks are ignored, excluded from releases
and must be backed up separately. Do not store shared theme changes here.
