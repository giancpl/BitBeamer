# Personal presentations

Keep each active presentation in its own `presentations/<name>/` folder.
Open that project's **`main.tex`** to edit the deck; the root-level `main.tex`
is the template showcase, not your personal presentation.

```text
presentations/<name>/
  main.tex          presentation entry point and slide content
  README.md         project-specific instructions, when supplied
  brief.md          requirements, sources and verification
  assets/           presentation-specific artwork
  references.bib    presentation-specific references
  layouts/          optional presentation-specific compositions
```

For short decks, keep the slide calls in `main.tex`. Longer decks may use included
sections, with their locations explained in the project's README. Shared themes
and icon resources stay in the repository root.

Create and build from the repository root:

```sh
python3 scripts/deck.py new my-talk
python3 scripts/deck.py build my-talk
python3 scripts/deck.py check my-talk --preview
```

Studio is the default; add `--style academic` when creating an Academic deck.
On Windows use `py -3`. Build/check accept `--backend native`; Docker is the default.

Generated PDFs, previews, reports and caches live in
`build/presentations/<name>/`. Open **`build/presentations/<name>/main.pdf`**.
A project's optional `main.pdf` shortcut links to that generated file; it is not
a separate source or manually maintained copy.

Retained local validation projects belong under `presentations/_archive/`,
separate from active decks. Archive source snapshots outside `build/` so ordinary
build cleanup cannot delete them.

Read [the authoring guide](../docs/AUTHORING.md) and
[agent instructions](../AGENTS.md) before writing. Only this README is versioned;
personal decks and local archives are ignored, excluded from releases and must
be backed up separately. Do not store shared theme changes here.
