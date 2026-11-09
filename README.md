# BitBeamer

Create editable LaTeX presentations with **BitBeamer Studio** (default), or choose
**BitBeamer Academic** for conventional Beamer slides. Both use **Inter**, the
BitPolito palette and **171 vector illustrations**.

## Create with an agent

Install **Python 3.10+** and **Docker**, start Docker, then clone:

```sh
git clone https://github.com/giancpl/BitBeamer.git
cd BitBeamer
```

Give your agent this prompt, adding your topic and requirements:

```text
Read AGENTS.md and docs/AUTHORING.md. Create a Studio presentation in
presentations/my-talk/ reusing relevant lessons or topic blocks first,
then existing featured layouts. Complete brief.md
with my goal, audience, duration, language, sources and your assumptions.
Use the standard cover, team, contents and closing where appropriate.
Replace the example content, compile, run checks and visually inspect every
page. Keep all work local to this deck; do not change shared layouts or commit.
My brief: [topic, audience, duration, real author and sources].
```

[Agent instructions](AGENTS.md) · [Authoring guide](docs/AUTHORING.md)

Browse presentations and blocks in the [slide guide](docs/slides/index.html?view=decks) or list it with
`python3 scripts/deck.py library`. Copy a complete lesson with
`python3 scripts/deck.py new my-talk --from bitcoin-introduction-short`, then
edit its private content. Layouts and artwork stay linked to the canonical library.
The guide separates **Ready** and **In review**; approval is always explicit.
The supplied team presentation is available with `--from bitpolito-introduction`.

## Create manually

```sh
python3 scripts/deck.py new my-talk
python3 scripts/deck.py layouts
# Edit presentations/my-talk/main.tex and brief.md, then:
python3 scripts/deck.py build my-talk --open
python3 scripts/deck.py check my-talk --preview
```

Output: `build/presentations/my-talk/main.pdf`, `check.json` and numbered preview
images. Personal sources under `presentations/` are **ignored by Git**; back them
up separately. Existing folders are never overwritten.
On Windows use `py -3` instead of `python3`. Docker is prepared on first use;
installed TeX Live/MacTeX is available with `--backend native`.
[Setup and IDE tasks](docs/SETUP.md) cover prerequisites and troubleshooting.

| Design | Create | Editable starter | Theme |
| --- | --- | --- | --- |
| **Studio** | `deck.py new my-talk` | [start-studio.tex](start-studio.tex) | `bitpolito-studio` |
| **Academic** | `deck.py new my-talk --style academic` | [start-academic.tex](start-academic.tex) | `bitpolito-academic` |

Browse the [slide guide with previews and commands](docs/slides/index.html)
(`python3 scripts/review.py guide --open`), inspect fields with
`python3 scripts/deck.py layouts --model icon-cards --json`, or use
[ordinary Academic frames](docs/SLIDES.md). [Icons](docs/ICONS.md) work with both:
`\alice[height=2cm]` or `\asset[width=2cm]{coin}`.
Studio starts with a classic blue cover, [team page](docs/STUDIO-TEAM.md), contents
and a [closing page with optional QR](docs/STUDIO-CLOSING.md).

For Overleaf, use the separate [Studio](docs/OVERLEAF-STUDIO.md) or
[Academic](docs/OVERLEAF.md) ZIP. Prepared downloads need no Python, Docker or
converters after upload. Local personal decks are never included in these packages.

## Maintain the library

[Repository map](docs/STRUCTURE.md) · [Documentation](docs/README.md) ·
[Review workflow](docs/STUDIO-COLLECTION.md) · [Contributing](.github/CONTRIBUTING.md)

Edit a composition in `templates/studio/` and record selection, notes and explicit
approval in `templates/review.json`. Preview only the affected slide:

```sh
python3 scripts/review.py slide three-cards --open
python3 scripts/review.py sync
python3 scripts/review.py check
```

Ordinary authoring needs no catalogue regeneration. `main.tex` opens the generated
Studio showcase; `main-academic.tex` and the legacy Academic theme remain available.
Builds, comparisons and review packages stay under ignored local output folders.
[Maintenance](docs/MAINTENANCE.md) and [releasing](docs/RELEASING.md) explain checks,
review packages and stable release approval. `make clean` preserves `dist/`.
