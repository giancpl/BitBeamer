# Twelve-word grids

Both variants were explicitly approved on 2026-11-12. The later cross-family
card-shadow review remains deferred.

The Technical family `word-grid` preserves two original compositions:
`plain` (`twelve-word-grid`) and `annotated` (`seed-grid-caption`).
Both use the standard `#F9F9F9` paper and fixed font sizes. At the user's
request, both variants share the rounded inset-shadow panels from the annotated
original. Cell labels use consistent semibold type, thin spacing after numbers
and vertical centering; the two original grid arrangements remain distinct.
The annotated variant also uses semibold for both explanatory bodies.

```latex
\studiotemplate[
  variant={plain},
  title={Example words},
  words={alpha,bravo,charlie,delta,echo,foxtrot,
         golf,hotel,india,juliet,kilo,lima}
]{word-grid}
```

Supply exactly twelve nonempty, comma-separated values. Reading order is left to
right across each of four rows. The slide adds the numbers; omit numbers from the
values themselves. Omit `words` to use the twelve neutral defaults.

`numbered={false}` hides the numeric prefixes without changing the grid. A cell
also accepts a short phrase and an explicit `\\` break; its fixed height supports
two lines. Long phrases wrap automatically. Single words that exceed the available
width must be shortened or explicitly split. Text never shrinks to fit.

For the version with explanatory text, keep the same word list and use:

```latex
\studiotemplate[
  variant={annotated},
  title={Reading a sequence},
  words={alpha,bravo,charlie,delta,echo,foxtrot,
         golf,hotel,india,juliet,kilo,lima},
  grid-title={Example words},
  explanation-title={Reading order},
  explanation={Read each row from left to right.
               Continue with the following row.},
  note-title={Supporting note},
  note={Keep labels concise.\\Use this area for a short explanation.}
]{word-grid}
```

The plain variant rejects annotation fields. Empty annotation values preserve the
original spacing. For an individual cell override, `word-one` through `word-twelve`
are available; place an override after `words` in the option list.

Incorrect list counts and excessive cell content produce explicit errors. The
panels are fixed background components; these word grids contain no icon slots.
The obsolete `icon-grid` / `twelve` variant is replaced by `word-grid` / `plain`.

See the [model reference](templates/models/word-grid.md),
[unified slide guide](slides/index.html?model=word-grid) and
[short and longer examples](../examples/studio-word-grid.tex).
