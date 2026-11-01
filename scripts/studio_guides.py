"""Generate user guides from the current Studio field declarations."""
import html
import json
from pathlib import Path
import re

PREAMBLE = r'''\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\usepackage[backend=biber]{biblatex}
\addbibresource{bibliography.bib}
\begin{document}
'''
END = '\\end{document}\n'
PURPOSES = {
    'Opening': 'Open a talk or introduce its structure',
    'Statements': 'Focus attention on one message',
    'Lists': 'Organize related explanations or talking points',
    'Cards': 'Group concepts into a visual set',
    'Comparisons': 'Place alternatives in a shared composition',
    'Data': 'Explain values, metrics or relationships',
    'Images': 'Build a visual explanation around images',
    'Diagrams': 'Explain connections, sequences or structure',
    'Technical': 'Present technical content in a measured composition',
    'Closing': 'Close a talk or offer a next step',
}
ROLES = {
    'author': 'Author name', 'institute': 'Affiliation', 'title': 'Main text',
    'statement': 'Central statement', 'explanation': 'Supporting explanation',
    'caption-one': 'First caption', 'caption-two': 'Second caption',
    'caption-three': 'Third caption', 'expression': 'Displayed formula',
    'body': 'Body content, including LaTeX markup', 'root': 'Root label',
    'ab': 'Left intermediate hash label', 'cd': 'Right intermediate hash label',
    'code-file': 'Path to a literal code file', 'data-file': 'Path to an x,y CSV file',
}


def command(name, values=None):
    options = ',\n  '.join(key + '={' + value + '}' for key, value in (values or {}).items())
    return '\\studiotemplate' + ('[\n  ' + options + '\n]' if options else '') + '{' + name + '}'


def location(entry, field):
    box = field.get('box')
    if not box:
        return 'See source'
    x, y, width, height = box
    canvas_width, canvas_height = entry['canvas']
    horizontal = ('left', 'centre', 'right')[min(2, max(0, int((x + width / 2) / canvas_width * 3)))]
    vertical = ('upper', 'middle', 'lower')[min(2, max(0, int((y + height / 2) / canvas_height * 3)))]
    return vertical + ' ' + horizontal


def dimensions(entry, field):
    if not field.get('box'):
        return 'Source-defined'
    return f"{field['box'][2] / entry['canvas'][0] * 100:.1f}% wide × {field['box'][3] / entry['canvas'][1] * 100:.1f}% high"


def field_role(entry, field):
    name = field['name']
    if name == 'title' and entry['id'] in ('hero-number', 'line-chart'):
        return 'Headline value'
    if name in ROLES:
        return ROLES[name]
    if field['type'] == 'graphic':
        return 'Replaceable graphic or decoration'
    if name.startswith('hash-'):
        return 'Leaf hash label'
    if name.startswith('tx-'):
        return 'Transaction label'
    if name.startswith('item-'):
        return 'List or contents entry'
    return 'Editable text'


def guide_info(entry, selected=None):
    """Keep web, Markdown and archive examples on the same documented API."""
    selected = selected or {}
    fields = []
    for field in entry.get('fields', []):
        fields.append({**field, 'role': field_role(entry, field),
                       'location': location(entry, field), 'space': dimensions(entry, field)})
    values = dict(selected.get('example', {}))
    if not values:
        # Reusing short shipped values gives a valid editable example without
        # inventing text that might overflow a fixed box.
        text_fields = sorted((field for field in fields if field['type'] == 'text'),
                             key=lambda field: field['name'] != 'title')
        for field in text_fields:
            value = field.get('default', '')
            if value and len(value) <= 180 and '\n' not in value:
                values[field['name']] = value
                if len(values) == 2:
                    break
    example = command(entry['id'], values)
    graphic = next((field for field in fields if field['type'] == 'graphic' and field.get('box')), None)
    replacement = None
    if graphic and entry['id'] != 'equation':
        width = graphic['box'][2] / entry['canvas'][0] * .9
        height = graphic['box'][3] / entry['canvas'][1] * .9
        options = f'width={width:.5f}\\paperwidth,height={height:.5f}\\paperheight,keepaspectratio'
        replacement = command(entry['id'], {graphic['name']: '\\asset[' + options + ']{alice}'})
    purpose = selected.get('use') or PURPOSES[entry['category']] + ' using the ' + entry['title'].lower() + ' layout.'
    return dict(purpose=purpose, fields=fields, example=example,
                document=PREAMBLE + example + '\n' + END, replacement=replacement)


def inline(value):
    # HTML code inside a Markdown table preserves literal backslashes and pipes.
    return '<code>' + html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ') + '</code>'


def guide_markdown(entry, selected=None, aliases=(), portable=False):
    info = guide_info(entry, selected)
    name = entry['id']
    source = '../' + entry['source'] if portable else '../../../' + entry['source']
    home = '../TEMPLATES.md' if portable else '../../USING-STUDIO.md'
    index = '../TEMPLATES.md' if portable else '../GUIDES.md'
    lines = ([] if portable else ['<!-- Generated by scripts/review.py sync. Edit template metadata or review.json. -->', '']) + ['# ' + entry['title'], '', info['purpose'], '',
             f"Model: `{name}` · Family: {entry['category']} · Status: **{entry.get('status', 'in review')}**.", '',
             f'[Getting started]({home}) · [All slide guides]({index}) · [Current LaTeX source]({source})', '']
    if not portable:
        lines += [f'[Open this slide individually](../index.html?template={name})', '',
                  f"![{entry['title']}](../previews/{name}.png)", '',
                  'The preview shows the shipped defaults. The thin bottom label belongs to the review catalogue.', '']
    lines += ['## Insert this slide', '', 'Place this command outside another `frame`:', '',
              '```latex', command(name), '```', '', '## Change the content', '',
              'This example uses supported fields. Omitted fields keep their shipped defaults.', '',
              '```latex', info['example'], '```', '', '## Complete one-slide example', '',
              'Create `my-slide.tex` in the project root and paste:', '', '```latex', info['document'].rstrip(), '```', '']
    if portable:
        lines += ['On Overleaf, select `my-slide.tex` as the main document and use pdfLaTeX.',
                  'With installed TeX, run `latexmk -pdf my-slide.tex`.', '']
    else:
        lines += ['```sh', 'python3 scripts/build.py my-slide.tex', '# Installed TeX alternative:',
                  'python3 scripts/build.py my-slide.tex --backend native', '```', '',
                  'Output: `build/my-slide.pdf`. On Windows use `py -3` instead of `python3`.', '']
    lines += ['## Editable fields', '', 'Positions and available space refer to the original, fixed composition.',
              ('Use the position column to locate each field in the compiled slide.' if portable else 'In the individual web view, select a field or enable **Show editable areas** to locate it.'), '',
              '| Field | What it changes | Position | Available space | Shipped value |', '| --- | --- | --- | --- | --- |']
    for field in info['fields']:
        default = field.get('default', '')
        sample = default if len(default) <= 120 else default[:117] + '...'
        lines.append('| ' + ' | '.join([inline(field['name']), field['role'] + ' (' + field['type'] + ')',
                     field['location'], field['space'], inline(sample or '(empty)')]) + ' |')
    lines += ['', 'Truncated values are shown in full at the start of the current source file.',
              'A text field accepts LaTeX; a graphic field accepts an icon, `\\includegraphics`, TikZ or math.', '']
    if info['replacement']:
        lines += ['## Replace a graphic', '', 'This example fits an icon inside the first graphic slot, preserving its proportions:', '',
                  '```latex', info['replacement'], '```', '',
                  'Use any graphic field listed above to target another slot. Some slots contain a complete',
                  'panel, background, screenshot or decoration. Inspect the preview before replacing them.', '']
    if name == 'code':
        lines += ['## Code file', '', 'Set `code-file` to a UTF-8 text file, relative to the project root.',
                  'The file is typeset literally and is never executed. An empty `code-file` keeps the shipped text.', '']
    if name == 'line-chart':
        lines += ['## Chart data', '', 'Set `data-file` to a CSV with header `x,y`. An empty value keeps the shipped graphic.',
                  'Update the labels as well as the curve; example CSV values are illustrative.', '',
                  '```csv', 'x,y', '1,2', '2,3', '3,5', '```', '']
    if name == 'references':
        lines += ['## Bibliography', '', 'Edit `bibliography.bib` and keep biblatex/Biber enabled as in the complete example.',
                  'Citation keys and resource text can be changed through the listed fields or the source.', '']
    if name == 'contents':
        lines += ['## Contents entries', '', 'Change `item-2-1` through `item-2-4` for the four visible entries.',
                  'This measured template uses explicit fields; it does not read Beamer section names.', '']
    lines += ['## Keep the composition', '',
              '- Keep replacements within their allocated boxes. Shorten text or use explicit `\\\\` line breaks.',
              '- Use `field={}` to hide content while retaining its space.',
              '- Fonts, anchors and geometry remain fixed; unknown fields and overflowing content produce diagnostics.',
              '- Text colour does not recolour supplied graphics; prepare another asset when its fixed colours must change.',
              '- Some diagrams, QR codes and decorations are native source elements rather than configurable fields.',
              f'- For structural changes, edit [the current source]({source}). Catalogues and the showcase reuse it.', '']
    matching = [alias for alias in aliases if alias['alias_of'] == name]
    if matching:
        lines += ['## Compatibility names', '',
                  'These names share this source and may apply different shipped field defaults:', '']
        lines += ['- `' + command(alias['id']) + '`' for alias in matching]
        lines += ['']
    if not portable:
        lines += ['## Review', '', 'Reference: ' + (', '.join(entry['references']) or 'Supplementary; no original Figma reference') + '.', '',
                  'Review margins, text, crops, shadows and optical balance using this stable model ID.',
                  'Record feedback in [the review ledger](../../../templates/review.json). Compilation is not graphical approval.', '']
    return '\n'.join(lines)


def guides_index(entries, selected, portable=False):
    chosen = {item['id'] for item in selected}
    lines = ['# Slide-by-slide guides', '',
             f'{len(entries)} current compositions. Each guide has a complete one-slide example, exact field names and layout constraints.', '']
    if not portable:
        lines += ['[Getting started](../USING-STUDIO.md) · [Visual gallery](index.html)', '',
                  'Start with the selected layouts, then browse the full collection by family.', '',
                  '## Selected layouts', '']
        by_id = {entry['id']: entry for entry in entries}
        lines += ['- [' + by_id[item['id']]['title'] + '](guides/' + item['id'] + '.md)' for item in selected if item['id'] in by_id]
    for category in dict.fromkeys(entry['category'] for entry in entries):
        lines += ['', '## ' + category, '']
        for entry in entries:
            if entry['category'] == category:
                lines.append('- [' + entry['title'] + '](guides/' + entry['id'] + '.md)' + (' — selected' if entry['id'] in chosen else ''))
    return '\n'.join(lines) + '\n'


def generated_guides(root, entries, aliases):
    from studio_review import selected as review_selection
    selected = review_selection(root)
    by_id = {item['id']: item for item in selected}
    files = {Path('docs/templates/guides/' + entry['id'] + '.md'): guide_markdown(entry, by_id.get(entry['id']), aliases)
             for entry in entries}
    files[Path('docs/templates/GUIDES.md')] = guides_index(entries, selected)
    return files


def portable_guides(root, entries):
    """Archive guides reference only included files and need no browser assets."""
    from studio_review import selected as review_selection
    selected = review_selection(root)
    by_id = {item['id']: item for item in selected}
    files = {'guides/' + entry['id'] + '.md': guide_markdown(entry, by_id.get(entry['id']), portable=True).encode('utf-8') for entry in entries}
    header = '''# Studio template collection

Load the Studio theme and bitpolitostudiotemplates. Every named template inserts a complete frame.
Choose a guide below, then copy its complete example into a new .tex file in the project root.
On Overleaf select that file as the main document and use pdfLaTeX. With installed TeX,
run `latexmk -pdf my-slide.tex`. Ordinary compilation needs no Python, Docker, converter or shell escape.
Select `catalogue.tex` in a review project or `studio-template-catalogue.tex` in the complete package
to preview all included models. With installed TeX, use `latexmk -pdf studio-template-catalogue.tex`
for the latter document. The guide index contains only models included in this archive.

Fields accept LaTeX. Omitted fields retain defaults; empty fields keep their geometry.
Use only the documented field names and keep text and graphics within their fixed boxes.
All reconstructed compositions remain in graphical review until explicitly approved.

'''
    files['TEMPLATES.md'] = (header + guides_index(entries, selected, portable=True)).encode('utf-8')
    return files
