# Contributing

For a personal deck, read [AGENTS.md](../AGENTS.md) and
[the authoring guide](../docs/AUTHORING.md); work in its ignored project folder.
The guidance below is for shared library changes.

Use the [repository map](../docs/STRUCTURE.md) to find the canonical source for a change.
For a Studio layout, follow [the review workflow](../docs/STUDIO-COLLECTION.md).
For artwork or tooling, use [maintenance](../docs/MAINTENANCE.md).

Before sharing changes, run from the root:

```sh
python3 scripts/review.py check
python3 -m unittest discover -s tests
```

Compile the affected document or composition with the existing build launcher.
Keep authored text and comments in English. Preserve public IDs and compatibility
aliases. Keep prepared artwork, manifests and provenance with their source changes.
Generated files are refreshed through their documented tools. Record review notes
in `templates/review.json`; graphical approval remains an explicit review decision.

Build outputs and original-frame comparisons stay local. Releases follow the
[separate release workflow](../docs/RELEASING.md).
