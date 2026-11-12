# Preconfigured sponsor slides

These two Lists compositions retain the sponsor rosters supplied in the originals.
They are ready to insert without repeating names, websites, social accounts or artwork:

```latex
\studiotemplate{partner-rail}
\studiotemplate{partner-media-grid}
```

`partner-rail` shows five sponsors with their original logos and contact pairs.
`partner-media-grid` shows ten sponsors in two columns and the retained media logos.
The second composition shares its canonical renderer and prepared artwork with
`library/layouts/bitpolito-partners.tex`; lesson and catalogue cannot drift apart.

This is retained reference content. Updating the sponsor roster is a deliberate
maintenance action. Optional text/artwork overrides remain available, but routine
use needs only the short calls above. Text remains native LaTeX and semibold.

Five-sponsor contact keys are `website-one`, `social-one` through five;
artwork uses `image-logo-one`, `icon-website-one`, `icon-social-one` and their
corresponding image/graphic forms. The original logos retain their individually
measured visible dimensions: a wide wordmark and a tall monogram have different
optical proportions. Replacement logos fit fixed inner bounds with preserved
aspect ratio. Contact symbols share 76 x 76 source-unit slots and aligned centres.

The media composition keeps `title`, `left-website-1`, `left-handle-1` through 5,
and the corresponding `right-` fields. Three optional graphic replacements are
`graphic-left-sponsors`, `graphic-right-sponsors` and `graphic-media`; these replace
complete prepared artwork groups, rather than individual company logos.

See [preset and longer-copy specimens](../examples/studio-sponsors.tex),
[the five-sponsor model](templates/models/partner-rail.md) and
[the sponsor/media model](templates/models/partner-media-grid.md).
Both compositions were explicitly approved by the user on 2026-11-12.

The five-sponsor title and contact labels support two lines. The denser media
composition retains one line per title/contact at the source sizes; use short
websites and handles. Excess content produces a field overflow diagnostic.

The three shared sponsor/media artwork groups have transparent paper so they
inherit the slide background, including the standard `#f9f9f9`. Logo vectors and
embedded image streams remain unchanged. Maintenance after re-extraction uses
`python3 scripts/normalize_sponsor_backgrounds.py`; provenance is recorded in
`library/parts/bitpolito/manifest.json`.
