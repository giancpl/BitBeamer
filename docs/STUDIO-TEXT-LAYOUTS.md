# Paragraphs and statements

Selected from the supplied original SVGs and explicitly approved on 2026-11-13,
including longer copy, empty fields and the native backgrounds.
This family uses Inter Semibold at fixed sizes. Overflow is reported rather than
shrinking the text. No icon or illustration is embedded in these four layouts.

```latex
\studiotemplate[title={A heading},
  paragraph-one={First paragraph},
  paragraph-two={Second paragraph},
  paragraph-three={Third paragraph},
  paragraph-four={Fourth paragraph},
  paragraph-five={Fifth paragraph}
]{paragraphs}

\studiotemplate[variant=centered,title={A heading},
  upper-body={First explanation},
  separator={HOWEVER},
  lower-body={Second explanation}
]{paragraphs}

\studiotemplate[variant=plain,
  title={A clear statement}
]{statement}

\studiotemplate[variant=clipped,
  introduction={Explore},
  word={Discovery}
]{statement}
```

The left variant has five independently editable paragraphs in reading order.
The centered variant centers its heading, separator and content envelopes; the
paragraph text itself stays left aligned, as in the original. Both use the
original light treatment. Headings accept two lines and paragraphs accept short
wrapped text at their documented bounds. `\\` inserts a deliberate line break.

The plain statement uses the original blue palette, a centered text block and
up to two lines. Its vertical position follows the actual text height rather
than pinning the first line of a multiline statement to the single-line baseline.

The clipped variant keeps one large word and a separate centered introduction.
Its native type size is intentionally large; use a shorter word when it exceeds
the canvas. It never scales a long word down. The original near-edge treatment
is retained, and copy extending beyond capacity produces a diagnostic.

Every field supports an explicit empty value without moving the others. The old
`label-two` through `label-six` paragraph keys and clipped `label-one`/`title`
keys have been replaced by the semantic keys above; no public aliases are added.

[The specimen](../examples/studio-text-layouts.tex) contains source-related short
examples, longer automatic wraps, explicit breaks and independent empty values.
The active comparison contains only these four compositions, with commands under
every original/current pair. See [catalogue progress](CATALOGUE-REVIEW.md) for the
separate selection and graphical approval decisions.
