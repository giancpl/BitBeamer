# Reconstruct a Figma frame in Studio

Use exported frames as references for editable LaTeX layouts. Do not add whole
reference slides as flattened images to the theme. Inter remains the chosen
font, replacing SF Pro while matching the composition and visual hierarchy.

## What to export

Provide PDF with one frame per page, or an SVG per frame. Keep text as text
when the exporter permits it. A PNG at 2x resolution is a useful additional
reference for shadows, transparency, clipping, and visual effects. Export
illustrations, logos, and decorative layers separately as SVG when available.
Preserve the frame's original dimensions and use descriptive filenames such as
`payment-comparison.pdf` or `wallet-process.svg`. A note identifying the Figma
frame and any intended differences is useful; no account connection is required.

## Where references go

Store received exports in `design-references/figma/`. This folder is ignored by
Git, rejected by the repository check if force-added, and excluded from both
Overleaf packages. Create a subfolder per incoming set when needed. Keep raw
exports and visual comparisons there; they are local design inputs.

The tracked sources are the resulting LaTeX composition, any required graphic
elements and prepared PDFs, and a short English description of their origin.
New graphic elements belong with the Studio artwork. Retain their source and
provenance; do not rename or overwrite existing public illustration assets.

## Reconstruction process

1. Identify the reference's dimensions, safe margins, alignment axes, colour
   values, type sizes/weights, spacing, graphic bounds, radii, and shadows.
2. Match it to an existing model in [the Studio guide](STUDIO.md). Reuse a
   component when the layout already exists; add one only for a recurring need.
3. Rebuild headings, captions, body text, arrows, cards, tables, and diagrams in
   LaTeX/TikZ. Use graphic exports only for artwork that needs them, with no
   baked-in slide text. Record which elements are deliberately different.
4. Prepare any required PDF artwork using [the artwork workflow](ASSETS.md).
   Preserve transparency and the correct canvas where clipping matters.
   Ordinary document compilation must not require conversion.
5. Render the reconstruction at the same aspect ratio and compare side by side
   with the reference, including a same-scale overlay when helpful. Inspect
   text baselines, whitespace, clipping, layer order, and effects, not just colour.
6. Test short and wrapped text, missing optional fields, and different image
   proportions. Confirm fonts are embedded and editable text stays selectable.
7. Record the source frame, corresponding model, intentional differences,
   remaining asset needs, and review status in a short English note. A received
   reference is not considered finalized until its rendered version is reviewed.

New frame sets are integrated incrementally. Keep confirmed components stable
while refining a new model. Rebuild both designs and their isolated packages
when changing shared resources; never adjust the Academic layouts to implement
a Studio reference. Commit and push only after explicit approval of the result.

## Received export set

The first supplied set contains 1,073 SVG exports. All are preserved locally in
`design-references/figma/exports/`; thumbnails, contact sheets, and the local
render inventory are beside them. Raw references stay outside Git and releases.
The tracked [source inventory](../templates/figma-inventory.json) records their
hashes, dimensions, and review dispositions without shipping the SVGs.

The [current template library](TEMPLATES.md) reconstructs the useful recurring slide
families with a 24-layout working showcase. Representative frame IDs
are recorded in [template metadata](../templates/index.json). Unselected-frame
similarity suggestions are automated candidates, not exact reconstruction
claims. Portrait reports, proposals, and fragments remain references; the
current template library targets 16:9.

Future exports can refine a specific composition or contribute a new layout.
Keep the reference ID, intended differences, and the editable LaTeX result
together during review. Do not publish comparison frames as theme assets.
