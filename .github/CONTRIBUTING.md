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
Keep authored text and comments in English. Preserve public IDs. When command
syntax changes, replace the old syntax and migrate official callers and guides;
do not keep obsolete field aliases. Keep prepared artwork, manifests and provenance
with their source changes.
Generated files are refreshed through their documented tools. Record review notes
in `templates/review.json`; graphical approval remains an explicit review decision.

Build outputs and original-frame comparisons stay local. Releases follow the
[separate release workflow](../docs/RELEASING.md).

## Default template correction workflow

This is the default procedure for maintainers and agents working on shared
BitBeamer sources. Apply it whenever a template or shared visual component is
adjusted, even when feedback identifies a single example slide. No separate
request to propagate the fix or verify its consumers is needed. Ordinary
presentation authoring follows [the authoring guide](../docs/AUTHORING.md).

1. Trace the reported example to its canonical template and components. Search
   both `templates/index.json` and `library/index.json`. Distinguish a content-only
   correction from a layout defect: content belongs in slide fields; alignment,
   font weight, spacing, geometry, shadows and other shared effects belong in
   shared sources.
2. Correct the canonical source once. Reuse existing panels, icon slots and
   quotation fields. Consolidate equivalent lesson copies, extend `reuse_rules`
   with all known consumers and mark superseded layout records with `replaced_by`.
   Preserve public IDs and canonical sources; migrate callers when replacing syntax. Record a different
   composition as an explicit variant with its reason.
3. Identify every affected composition, variant, supported palette and lesson
   consumer. For lessons, run `python3 scripts/library.py affected --changed <path>`;
   pass all changed shared paths together. Use the core template dependency
   metadata for Studio catalogue compositions. Keep Academic unchanged during
   Studio-only work and preserve existing personal copies.
4. Synchronize the relevant metadata, registries and guides using their documented
   launchers. Build affected core compositions with `review.py slide <id>` and
   consuming lessons/blocks with `library.py build --changed <path> --preview`.
   Refresh all affected previews and existing local comparisons. The unified
   [slide guide](../docs/slides/index.html) must show the current preview and
   command before delivery; normal sync and preview updates refresh it automatically.
   Guide thumbnails and HD images are rendered from the compiled PDF, never upscaled
   from a legacy thumbnail. Run `guide_previews.py check`; old gallery generators
   must remain removed. Optional browser checks use `node scripts/check-slide-guide-browser.mjs`.
   Reuse caches;
   a local correction does not require a blanket catalogue rebuild.
5. Inspect every affected rendered page for the reported defect and collateral
   changes. Check the applicable field overrides, empty values, overflow handling
   and supported palettes. Always compile and visually inspect longer editable
   text alongside the short/default example, using automatic wrapping and explicit
   line breaks where supported. Check centering, spacing, overlap and clipping at
   fixed font sizes; use longer words/captions for word-based layouts and verify
   overflow reporting beyond the model's capacity. Include these previews in the
   interactive review. Run `review.py check`, `library.py check` when lessons
   are affected, and tests appropriate to the actual change. Add a regression
   check for a recurring defect when it can be tested meaningfully. Compilation
   and preview generation do not count as visual approval.
6. Record the canonical source, affected consumers, checks performed and remaining
   limitations in the maintenance report. Return changed approved designs to
   `in review`. Keep releases, approvals, commits and pushes behind their existing
   explicit requests.

Commands named without paths above live in `scripts/`. See
[Studio review](../docs/STUDIO-COLLECTION.md) for core compositions and
[lesson maintenance](../library/MAINTENANCE.md) for dependency tracking and reuse
rules. The procedure is internal maintenance policy; it adds no authoring steps,
new authoring obligations or replacements of personal content. Linked layouts
receive the canonical correction at the next build; legacy snapshots are migrated
only when explicitly requested. It is not
included in the Overleaf template's user instructions.

Maintenance background rule: verify each compiled slide canvas against its native
colour before every comparison and guide preview. Light is `#f9f9f9`; preserve
explicit original white/photo exceptions and the original blue. The automatic
`review_backgrounds` check runs on cached comparisons too and on long/empty
specimens. Never sample the white comparison-sheet margin as the slide canvas.
