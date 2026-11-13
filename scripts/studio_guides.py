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
    values = dict(values or {})
    words = ['one','two','three','four','five']
    grouped = any(re.fullmatch(r'(?:card-(?:one|two|three|four|five)(?:/.*)?|item-(?:one|two|three|four|five)/.*)', key) for key in values)
    if grouped:
        groups = {}
        for key in list(values):
            match = re.fullmatch(r'((?:card|item)-(?:one|two|three|four|five))/(title|body|text|label|icon|image|graphic)',key)
            if match:groups.setdefault(match[1],{})[match[2]] = values.pop(key)
        for card, fields in groups.items():
            values[card] = ',\n    '.join(key+'={'+fields[key]+'}' for key in ('title','label','body','text','icon','image','graphic') if key in fields)
        general = ['variant','palette','show-title','show-introduction','show-card-titles',
                   'show-card-bodies','show-icons','title','title-icon','title-image','title-graphic','introduction']
        order = [key for key in general if key in values]
        cards = [prefix+'-'+word for prefix in ['card','item'] for word in words if prefix+'-'+word in values]
        order += [key for key in values if key not in order and key not in cards]
        order += cards
        options = ',\n  '.join(key+'={'+ ('\n    '+values[key]+'\n  ' if key.startswith(('card-','item-')) else values[key]) +'}' for key in order)
    else:
        options = ',\n  '.join(key + '={' + value + '}' for key, value in values.items())
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
        if field.get('slot',{}).get('frame') or entry['id']=='three-cards':
            return 'Icon or image inside a fixed composition'
        return 'Complete graphic, image or decoration'
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
    by_name = {field['name']: field for field in fields}
    values = {by_name[key]['slot']['key']: value.replace(r'\\\\', r'\\') for key, value in values.items()}
    normalized = {}
    for key,value in values.items():
        field=next(field for field in fields if field['slot']['key']==key)
        if field.get('block'):
            n=field['slot']['number']
            normalized['heading/'+str(n)]=field['block']['heading']
            normalized['body/'+str(n)]=field['block']['body']
        else:
            normalized[key]=value
    values=normalized
    example = command(entry['id'], values)
    graphics = sorted((field for field in fields if field['type']=='graphic' and field.get('box')),
                      key=lambda field: (field['slot'].get('role') != 'card content', field['slot']['number']))
    graphic = graphics[0] if graphics else None
    replacement = None
    if graphic and entry['id'] != 'equation':
        replacement = command(entry['id'], {'icon/'+str(graphic['slot']['number']): 'alice'})
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
    api = '../STUDIO-CONTENT.md' if portable else '../../STUDIO-CONTENT.md'
    index = '../TEMPLATES.md' if portable else '../GUIDES.md'
    lines = ([] if portable else ['<!-- Generated by scripts/review.py sync. Edit template metadata or review.json. -->', '']) + ['# ' + entry['title'], '', info['purpose'], '',
             f"Model: `{name}` · Family: {entry['category']} · Status: **{entry.get('status', 'in review')}**.", '',
             f'[Getting started]({home}) · [All slide guides]({index}) · [Content API]({api}) · [Current LaTeX source]({source})', '']
    if not portable:
        lines += [f'[Open this slide individually](../../slides/index.html?template={name})', '',
                  f"![{entry['title']}](../previews/{name}.png)", '',
                  'The preview shows the shipped defaults. The thin bottom label belongs to the review catalogue.', '']
    from studio_models import membership
    member=membership().get(name)
    if member and not portable:
        model,variant,composition=member
        lines += ['## Grouped model', '', '[Model variants and named fields](../models/'+model['id']+'.md)', '', '```latex', r'\studiotemplate[variant='+variant['id']+',palette='+composition['native_palette']+']{'+model['id']+'}', '```', '', 'Use the documented semantic fields or the lower-level numbered slots; replaced semantic names are not retained.' if model['id'] in ('list-rail','two-columns','text-cards','paragraphs','statement') else 'Named fields are coherent across related variants. All old fields and numbered slots remain available.', '', 'Numeric defaults and charts are illustrative.', '']
    if entry.get('options'):
        lines += ['## Layout options', '', '| Option | Type | Default | Purpose |', '| --- | --- | --- | --- |']
        for key, option in entry['options'].items():
            default = str(option['default']).lower()
            lines.append(f"| `{key}` | {option['type']} | `{default}` | {option['description']} |")
        lines += ['', 'For example: `\\studiotemplate[qrcode=false]{closing}`. Options are not text slots; invalid values produce an error.', '']
    lines += ['## Typed content slots', '',
              'Use `text/N` for text, `icon/N` for an icon name, `image/N` for an image path,',
              'and `graphic/N` for LaTeX graphics. Numbers are local to this model and stored',
              'in its metadata; the map below shows their positions. Supplied graphics are fitted',
              'proportionally. Text fonts and alignment remain fixed.', '',
              'Use `clear=text` to remove shipped copy before adding your own; option order does not matter.',
              'Omitted fields keep their defaults. Named aliases such as `text/title` also work.', '',
              '| Public slot | Existing field | Content and appearance |',
              '| --- | --- | --- |']
    for field in info['fields']:
        key=field['slot']['key']
        if field['type']=='graphic':
            n=field['slot']['number']; keys=f'`icon/{n}`, `image/{n}`, `graphic/{n}`'
            detail=('Card panel and shadow stay in place; only the inner content changes.'
                    if field['slot'].get('frame') else 'Replaces this complete graphic; other elements stay fixed.')
        else:
            keys='`'+key+'`';detail=field['role']
            if field.get('block'):
                n=field['slot']['number'];keys+=f', `heading/{n}`, `body/{n}`'
                detail='Use heading/body separately to retain the measured text hierarchy.'
        lines.append('| '+keys+' | `'+field['name']+'` | '+detail+' |')
    lines += ['', 'Original unscoped field names remain compatible. For a labelled block, changing',
              '`text/N` replaces the complete box; use `heading/N` and `body/N` for structured edits.', '']
    lines += ['## Insert this slide', '',
 'Place this command outside another `frame`:', '',
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
        lines += ['## Replace a graphic', '', 'This example selects an icon by catalogue name; its size and position come from the slot:', '',
                  '```latex', info['replacement'], '```', '',
                  'Use a numbered slot listed above to target another graphic. Some slots contain a complete',
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
              '- Use `text/N={}` or `icon/N={}` to hide content while retaining its space; separated card panels stay visible.',
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
        lines += ['## Review', '', 'Reference: ' + (', '.join(entry['references']) or entry.get('external_reference',{}).get('name') or 'Supplementary; no original Figma reference') + '.', '',
                  'Review margins, text, crops, shadows and optical balance using this stable model ID.',
                  'Record feedback in [the review ledger](../../../templates/review.json). Compilation is not graphical approval.', '']
    return '\n'.join(lines)


def guides_index(entries, selected, portable=False):
    chosen = {item['id'] for item in selected}
    lines = ['# Slide-by-slide guides', '',
             f'{len(entries)} current compositions. Each guide has a complete one-slide example, exact field names and layout constraints.', '']
    if not portable:
        lines += ['[Getting started](../USING-STUDIO.md) · [Slide guide](../slides/index.html)', '',
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
    from studio_content_examples import document as customization_document
    api=(root/'docs/STUDIO-CONTENT.md').read_text(encoding='utf-8')
    api=api.replace('templates/GUIDES.md','TEMPLATES.md').replace('../examples/studio-customization.tex','customization.tex')
    files['STUDIO-CONTENT.md']=api.encode('utf-8')
    files['customization.tex']=customization_document(entries).encode('utf-8')
    from studio_models import model_guides,load_models
    model_files=model_guides(root,entries)
    for path,text in model_files.items():
        # Full clone-only list reference includes variants absent from small archives.
        text=re.sub(r'\[Complete usage reference:[^\n]+\]\(../../STUDIO-LISTS.md\)\n', '', text)
        text=re.sub(r'Horizontal rows: see \[count, optional heading and icon sizing\]\(../../STUDIO-ICON-CARDS.md\)[^\n]*\n', '', text)
        text=text.replace('../../../templates/MODELS.md','../MODELS.md').replace('../../STUDIO-MODELS.md','../STUDIO-MODELS.md').replace('../../../templates/studio/','../templates/studio/')
        files['models/'+path.name]=text.encode('utf-8')
    files['MODELS.md']=('# Included Studio models\n\n'+''.join('- ['+path.stem+'](models/'+path.name+')\n' for path in model_files)).encode('utf-8')
    text=(root/'docs/STUDIO-MODELS.md').read_text(encoding="utf-8")
    text=text[:text.index('## Review one choice')]
    start=text.index('```latex');end=text.index('```',start+8)+3
    first=next(iter(model_files)).stem if model_files else entries[0]['id']
    text=text[:start]+'```latex\n'+r'\studiosetup{palette=light}'+'\n'+r'\studiotemplate{'+first+'}\n```'+text[end:]
    text=text.replace('slides/index.html','MODELS.md').replace('templates/index.html','MODELS.md').replace('../templates/MODELS.md','MODELS.md').replace('templates/GUIDES.md','TEMPLATES.md')
    # Clone-only examples must not leave broken links or unavailable calls in subsets.
    start=text.index('## Suggested two-slide sequence')
    end=text.index('## Change the palette',start)
    if not {'section-divider','statement-arrow'} <= {entry['id'] for entry in entries}:
        text=text[:start]+text[end:]
    else:
        text=re.sub(r'\[[^]]+\]\(\.\./examples/studio-section-pair\.tex\)',
                    'paired and standalone commands above',text)
    text=text.replace('(STUDIO-SOFT-CARDS.md)', '(models/text-cards.md)' if any(e.get('model')=='text-cards' for e in entries) else '(MODELS.md)')
    text=re.sub(r'\[\d+-model index\]', '[included model index]', text)
    text=re.sub(r'The library retains all \d+ compositions behind \d+ model cards\. The featured set contains\n\d+ models; every one of the \d+ former featured composition choices remains recorded in the review ledger\.',
                'This standalone project contains only the models and variants listed in MODELS.md.', text)
    text=text.replace('[theme commands](STUDIO.md)','theme commands')
    files['STUDIO-MODELS.md']=text.encode('utf-8')
    return files
