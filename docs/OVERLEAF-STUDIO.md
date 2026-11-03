# BitBeamer Studio on Overleaf

Studio is the default BitBeamer design. For the simpler Academic project,
see [Academic on Overleaf](OVERLEAF.md).

Upload **bitbeamer-studio-overleaf.zip** as a new project, select **main.tex**,
and choose **pdfLaTeX**. Overleaf runs Biber when bibliography content is present.
The project contains the 21-model featured selection, its retained variants, both optional BitGeneration covers, four/five-item agendas, prepared graphics in their original colour treatments and all 171 icons.

Select `start.tex` for a five-slide editable deck: standard cover, automatic
contents, two content slides and closing. Use `\studiotitleframe`,
`\studiotocframe`, `\studioframe{Title}{Content}` and `\closingframe` for these
standard pages. The contents comes from your `\section` declarations.
`main.tex` is the selection showcase. The default title page is classic blue.
Choose `\studiotitleframe[variant=bitgeneration]` for the light cover or
`variant=bitgeneration-photo` for the photographic version; both use your title,
author and institute. Use a short title for the photo cover.

Open `MODELS.md` and `STUDIO-MODELS.md` for variants, named fields and palette switching.
`TEMPLATES.md` retains the advanced composition guides. Create your
own root-level .tex document, copy a guide's complete example and select it as the
main document. `studio-template-catalogue.tex` shows the working selection; the additional cover guides are included separately.
Prepared graphics compile without Python, Docker, conversion or shell escape.

The clone contains the complete library. To export other models or share unapproved
work, follow [the review workflow](STUDIO-COLLECTION.md). The main download is kept
within the upload budget; the complete collection can be exported in multiple projects.
See [the documentation map](README.md) for Academic and Studio workflows.

Use `\studiotocframe[variant=panels]` for four section names or
`variant=panels-five` for five. [The agenda guide](STUDIO-AGENDAS.md) also documents
manual item fields and overflow limits.
