"""Focused, local-only review of catalogue title, contents and closing layouts."""
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlencode

from asset_library import write_if_changed
from studio_models import membership
from studio_templates import catalogue_document

ROLES = ('title', 'contents', 'closing')
LABELS = {'title': 'Title', 'contents': 'Contents', 'closing': 'Closing'}
PRIMARY_MODELS = {'cover': 'title', 'agenda': 'contents', 'closing': 'closing'}


def candidates(root, entries):
    members = membership(root)
    rows = []
    for order, entry in enumerate(entries):
        model, variant, composition = members[entry['id']]
        primary = model['id'] in PRIMARY_MODELS and entry['id'] != 'cover-script-blue'
        if not primary and entry['category'] not in ('Opening', 'Closing'):
            continue
        role = PRIMARY_MODELS.get(model['id'], 'closing' if entry['category'] == 'Closing' else 'title')
        command = (r'\studiotemplate[variant=' + variant['id'] + ',palette='
                   + composition['native_palette'] + ']{' + model['id'] + '}')
        rows.append(dict(id=entry['id'], title=entry['title'], model=model['id'],
                         variant=variant['id'], palette=composition['native_palette'],
                         role=role, primary=primary, command=command, source=entry['source'],
                         references=entry['references'], status=entry['status'],
                         fields=[f['name'] for f in entry.get('fields', []) if f['type'] == 'text'],
                         observation=('Classified as a cover in the full catalogue, but its current rendering is a process diagram. Confirm its classification during review.' if entry['id'] == 'cover-script-blue' else 'These two agenda compositions currently look almost identical; compare before retaining both.' if entry['id'] in ('tabbed-agenda', 'agenda-with-icons') else ''),
                         order=order, entry=entry))
    rows.sort(key=lambda r: (not r['primary'], ROLES.index(r['role']), r['order']))
    for page, row in enumerate(rows, 1):
        row['page'] = page
    if any(not any(r['primary'] and r['role'] == role for r in rows) for role in ROLES):
        raise RuntimeError('The catalogue must provide a primary candidate for each page role.')
    return rows


def document(rows):
    source = catalogue_document([r['entry'] for r in rows])
    # Preserve the original canvas; review labels belong below the slide in the overview.
    source = source[:source.index('% Catalogue labels')] + source[source.index(r'\begin{document}'):]
    for row in rows:
        source = source.replace(r'\studiotemplate{' + row['id'] + '}', row['command'])
    return source


def overview_document(rows):
    source = r'''\documentclass{article}
\usepackage[paperwidth=160mm,paperheight=100mm,margin=0mm]{geometry}
\usepackage{graphicx,tikz,inter}
\definecolor{brand}{HTML}{001CE0}
\renewcommand{\familydefault}{\sfdefault}
\pagestyle{empty}\parindent=0pt
\begin{document}
'''
    for row in rows:
        source += (r'\null\begin{tikzpicture}[remember picture,overlay]'
                   r'\node[anchor=north,inner sep=0pt] at (current page.north) {'
                   r'\includegraphics[width=\paperwidth]{' + row['image'] + '}};\n')
        label = f"{row['page']} / {len(rows)} — {LABELS[row['role']]} — {row['id']}"
        source += (r'\node[anchor=south west,text=brand,inner sep=0pt,font=\fontsize{6}{7}\selectfont] '
                   r'at ([xshift=4mm,yshift=5.5mm]current page.south west) {' + label + '};\n')
        source += (r'\node[anchor=south west,text=brand,inner sep=0pt,font=\fontsize{5}{6}\selectfont] '
                   r'at ([xshift=4mm,yshift=2mm]current page.south west) {\texttt{\detokenize{'
                   + row.get('label_command', row['command']) + r'}}};\end{tikzpicture}' + '\n')
        if row['page'] < len(rows):
            source += r'\newpage' + '\n'
    return source + r'\end{document}' + '\n'


def gallery(root, folder, rows):
    esc = html.escape
    base = Path(os.path.relpath(root, folder)).as_posix() + '/'
    def card(row):
        query = urlencode(dict(template=row['model'], variant=row['variant'], palette=row['palette']))
        image = Path(row['image']).relative_to(folder.relative_to(root)).as_posix()
        output = f'<article id="{row["id"]}"><h3>{row["page"]}. {esc(row["title"])}</h3>'
        output += f'<img src="{image}" loading="lazy" width="1280" height="720" alt="{esc(row["id"])}">'
        output += f'<p><b>{row["id"]}</b> · {esc(row["status"])} · {row["variant"]} / {row["palette"]}</p>'
        output += '<pre><code>' + esc(row['command']) + '</code></pre><button onclick="copyCode(this)">Copy command</button>'
        if row['observation']:
            output += '<p><strong>Review observation:</strong> ' + esc(row['observation']) + '</p>'
        output += '<p>Text fields: ' + esc(', '.join(row['fields']) or 'See the source') + '</p>'
        output += f'<p><a href="{base}{row["source"]}">Editable source</a> · '
        output += f'<a href="{base}docs/templates/index.html?{query}">Fields and guide</a> · '
        output += f'<a href="studio-pages-catalogue.pdf#page={row["page"]}">Vector PDF</a></p>'
        for reference in row['references']:
            original = root / 'design-references/figma/collection-review/web' / (reference + '.webp')
            if original.is_file():
                url = base + original.relative_to(root).as_posix()
                output += f'<details class="original" data-image="{url}"><summary>Original {reference}</summary><div></div></details>'
        return output + '</article>'
    text = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Studio: title, contents and closing review</title><style>
body{font:16px/1.5 system-ui,sans-serif;margin:auto;padding:24px;max-width:1200px;background:#f9f9f9;color:#171b33}
a{color:#001ce0}nav{display:flex;gap:20px;flex-wrap:wrap}section{margin:40px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,430px),1fr));gap:24px}
article{padding:18px;background:white;border:1px solid #ddd;border-radius:12px;min-width:0}img{width:100%;height:auto;display:block}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef0ff;padding:10px;font-size:12px}button,summary{cursor:pointer}summary{padding:12px 0}h3{margin-top:0}</style>
<h1>Studio: title, contents and closing</h1>
<p>Existing catalogue compositions only. Primary cover, agenda and closing candidates are grouped below. Related or misclassified layouts follow separately. Native palettes and proportions are retained. No selection, default or approval has changed.</p>
<p>Choose the visual layouts by their stable IDs. Plain four/five-item agendas support editable fields and automatic section binding. Other agenda compositions retain their current field APIs.</p>
<p><a href="studio-pages-overview.pdf">Quick review PDF</a> · <a href="studio-pages-catalogue.pdf">Editable/vector PDF</a> · <a href="candidates.json">Candidate metadata</a></p>
<nav><a href="#title">Title</a><a href="#contents">Contents</a><a href="#closing">Closing</a><a href="#related">Related layouts</a></nav>
'''
    example_mode = folder.name == 'examples'
    text += ('<p><strong>English ready-content examples.</strong> <a href="../index.html">Switch to neutral layouts</a></p>' if example_mode else '<p><strong>Neutral reusable layouts.</strong> <a href="examples/index.html">Switch to English content examples</a></p>')
    for role in ROLES:
        text += f'<section id="{role}"><h2>{LABELS[role]}</h2><div class="grid">'
        text += ''.join(card(r) for r in rows if r['primary'] and r['role'] == role) + '</div></section>'
    text += '<details id="related"><summary>Related layouts: separator, opening dashboard, QR closings and a misclassified cover</summary><div class="grid">'
    text += ''.join(card(r) for r in rows if not r['primary']) + '</div></details>'
    text += '''<script>
async function copyCode(button){const value=button.previousElementSibling.textContent;try{await navigator.clipboard.writeText(value);button.textContent='Copied';}catch(e){window.prompt('Copy command',value);}}
document.querySelectorAll('details.original').forEach(d=>d.addEventListener('toggle',()=>{if(d.open&&!d.querySelector('img')){const image=document.createElement('img');image.src=d.dataset.image;image.alt='Original reference';d.querySelector('div').append(image);}}));
</script></html>'''
    return text


def build_review(root, entries, backend, image, compile_document, content='neutral'):
    rows = candidates(root, entries)
    folder = root / 'build/review/pages'
    if content == 'example':
        from studio_examples import exact_command
        folder = folder / 'examples'
        for row in rows:
            row['label_command'] = row['command']
            row['command'] = exact_command(root, row['entry'], 'example')
    for row in rows:
        row['content'] = content
    folder.mkdir(parents=True, exist_ok=True)
    ledger = (root / 'templates/review.json').read_bytes()
    source = folder / 'studio-pages-catalogue.tex'
    write_if_changed(source, document(rows).encode())
    pdf = compile_document(root, source, folder, backend, image)
    renders = folder / 'renders'
    renders.mkdir(exist_ok=True)
    for path in renders.glob('page-*.jpg'):
        path.unlink()
    options = ['-jpeg', '-jpegopt', 'quality=85,optimize=y', '-scale-to-x', '1280', '-scale-to-y', '-1']
    if shutil.which('pdftocairo'):
        command = ['pdftocairo', *options, str(pdf), str(renders / 'page')]
    elif backend == 'docker':
        command = ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'pdftocairo',
                   '--mount', f'type=bind,source={folder},target=/input,readonly',
                   '--mount', f'type=bind,source={renders},target=/output', image,
                   *options, '/input/' + pdf.name, '/output/page']
    else:
        raise RuntimeError('Review rendering needs Poppler, or --backend docker.')
    subprocess.run(command, check=True)
    images = sorted(renders.glob('page-*.jpg'), key=lambda p: int(p.stem.split('-')[-1]))
    if len(images) != len(rows):
        raise RuntimeError('Catalogue page count differs from the candidate list.')
    for row, path in zip(rows, images):
        row['image'] = path.relative_to(root).as_posix()
    source = folder / 'studio-pages-overview.tex'
    write_if_changed(source, overview_document(rows).encode())
    overview = compile_document(root, source, folder, backend, image)
    if shutil.which('pdfinfo'):
        info = subprocess.check_output(['pdfinfo', str(overview)], text=True)
        if int(re.search(r'(?m)^Pages:\s+(\d+)', info)[1]) != len(rows):
            raise RuntimeError('Quick overview page count differs from the candidate list.')
    output = folder / 'index.html'
    write_if_changed(output, gallery(root, folder, rows).encode())
    data = dict(purpose='Manual review; no defaults or approvals changed',
                candidates=[{k: v for k, v in r.items() if k not in ('entry', 'order')} for r in rows])
    write_if_changed(folder / 'candidates.json', (json.dumps(data, indent=2) + '\n').encode())
    if (root / 'templates/review.json').read_bytes() != ledger:
        raise RuntimeError('Focused review must not change the review ledger.')
    return overview, output
