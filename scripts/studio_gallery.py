"""Small offline review pages with a curated default and bounded image loading."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def selection(root, entries):
    """Read the ordered working set from the single review ledger."""
    from studio_review import selected
    return selected(root, entries)


def example_command(item):
    values = item.get('example', {})
    options = ',\n  '.join(key + '={' + value + '}' for key, value in values.items())
    return '\\studiotemplate' + ('[\n  ' + options + '\n]' if options else '') + '{' + item['id'] + '}'


def rows_for_gallery(root, entries, comparison=False):
    from studio_guides import guide_info
    chosen = {item['id']: item for item in selection(root, entries)}
    aliases_by_target = {}
    for alias in json.loads((root / 'templates/index.json').read_text(encoding='utf-8')).get('aliases', []):
        aliases_by_target.setdefault(alias['alias_of'], []).append(alias['id'])
    base = '../../../' if comparison else '../../'
    rows = []
    for page, entry in enumerate(entries, 1):
        name = entry['id']
        item = chosen.get(name, {})
        usage = guide_info(entry, item)
        row = dict(id=name, title=entry['title'], category=entry['category'], status=entry.get('status', 'in review'),
                   page=page, references=entry['references'], aliases=aliases_by_target.get(name, []), fields=usage['fields'],
                   canvas=entry.get('canvas', []), notes=entry.get('intentional_differences', []) + ([entry['review_notes']] if entry.get('review_notes') else []),
                   source=base + entry['source'], purpose=usage['purpose'],
                   example=usage['example'], document=usage['document'], replacement=usage['replacement'],
                   guide=base + 'docs/templates/guides/' + name + '.md',
                   single='index.html?template=' + name, parts=[])
        for part in entry.get('parts', []):
            folder = 'parts' if (root / 'images/studio/parts' / (part + '.pdf')).exists() else 'collection'
            row['parts'].append(dict(name=part, url=base + 'images/studio/' + folder + '/' + part + '.pdf'))
        row.update(preview='previews/' + name + '.png', full='previews/' + name + '.png')
        if comparison:
            full = f'replica-{page:03}.png'
            row.update(preview='web/' + Path(full).stem + '.webp', full=full)
            if entry['references']:
                reference = entry['references'][0]
                for key, stem in [('original', reference), ('overlay', name + '-overlay'), ('difference', name + '-difference')]:
                    row[key] = dict(preview='web/' + stem + '.webp', full=stem + '.png')
        rows.append(row)
    return rows


def gallery_html(entries, root=ROOT, comparison=False, navigation=''):
    chosen = selection(root, entries)
    rows = rows_for_gallery(root, entries, comparison)
    options = ''.join('<option>' + html.escape(category) + '</option>' for category in sorted({e['category'] for e in entries}))
    config = dict(entries=rows, selection=[item['id'] for item in chosen], pageSize=6 if comparison else 12,
                  mode='comparisons' if comparison else 'replicas',
                  aliases={entry['id']: entry['alias_of'] for entry in json.loads((root / 'templates/index.json').read_text(encoding='utf-8')).get('aliases', [])})
    payload = json.dumps(config, separators=(',', ':'), ensure_ascii=True).replace('<', '\\u003c')
    script = Path(__file__).with_name('studio-gallery.js').read_text(encoding='utf-8')
    base = '../../../' if comparison else '../../'
    navigation += '<p><a href="' + base + 'docs/USING-STUDIO.md">Getting started</a> · <a href="' + base + 'docs/templates/GUIDES.md">Slide guides</a> · <a href="' + base + 'templates/SELECTION.md">Selected layouts</a> · <a href="' + base + 'build/review/studio-selected-templates.pdf">Selected PDF (' + str(len(chosen)) + ' layouts)</a> · <a href="' + base + 'templates/CATALOGUE.md">Full command index</a></p>'
    if not comparison:
        navigation += '<p><a href="../studio-parts/index.html">Reusable parts</a> · <a href="../../examples/studio-selected-templates.tex">Copyable selected deck</a></p>'
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BitBeamer Studio — selected layouts</title>
<style>body{font:16px Inter,system-ui,sans-serif;background:#f9f9f9;color:#001ce0;margin:32px}header{max-width:1100px}h1{font-size:38px}a{color:inherit}nav.controls{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}input,select,button{font:inherit;color:inherit;background:white;padding:10px;border:1px solid #c7cdf8;border-radius:8px}input{flex:1;min-width:180px}button,summary{cursor:pointer}button:disabled{opacity:.4;cursor:default}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(360px,100%),1fr));gap:24px}body.comparisons main{grid-template-columns:1fr}article{background:white;border:1px solid #e0e3f3;border-radius:12px;overflow:hidden;scroll-margin-top:20px}.body{padding:18px}img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain}small{font-size:12px}article>a+small{padding:0 18px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}.pair small{padding:8px;display:block}code,pre{font:12px ui-monospace,monospace;overflow-wrap:anywhere}pre{white-space:pre-wrap;background:#f4f5fc;padding:12px;border-radius:6px}details{margin-top:12px;overflow-x:auto}td,th{font-size:12px;padding:7px;text-align:left;vertical-align:top;border-bottom:1px solid #eee}table{width:100%;border-collapse:collapse}.pagination{display:flex;gap:12px;margin:20px 0}.purpose:empty{display:none}@media(max-width:650px){body{margin:16px}.pair{grid-template-columns:1fr}}
 .single>header,.single>.pagination{display:none}.single main{display:block;max-width:1150px;margin:auto}.single nav{margin-bottom:18px}.slide-image{position:relative;aspect-ratio:16/9;overflow:hidden}.field-map{display:none;position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.show-areas .field-map{display:block}.field-map .muted{display:none}.map-controls{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}.map-controls select{max-width:100%}.single article{margin-bottom:24px}
</style><body class="''' + ('comparisons' if comparison else 'replicas') + '''"><header><h1>BitBeamer Studio</h1><p>Start with ''' + str(len(chosen)) + ''' distinct, reusable layouts. The full archive retains ''' + str(len(entries)) + ''' unique compositions. This is a working selection for review; no model is approved automatically.</p><p>Only the current page loads preview images. Open fields or comparisons when needed; click an image for full resolution.</p>''' + navigation + '''<nav class="controls" id="controls"><select id="scope" aria-label="Collection"><option value="selected">Selected layouts</option><option value="all">Full archive</option></select><input id="search" type="search" aria-label="Search templates" placeholder="Search name or Figma reference"><select id="category" aria-label="Family"><option value="">All families</option>''' + options + '''</select><select id="status" aria-label="Review status"><option value="">All statuses</option><option>in review</option><option>changes requested</option><option>approved</option><option>supplementary</option></select></nav><p id="count" role="status"></p><div class="pagination"><button data-page="-1">Previous</button><button data-page="1">Next</button></div></header><main></main><div class="pagination"><button data-page="-1">Previous</button><button data-page="1">Next</button></div><noscript>Enable JavaScript to browse this offline gallery. The selected-layout guide and copyable LaTeX sources are also available through the links above.</noscript><script id="gallery-data" type="application/json">''' + payload + '</script><script>\n' + script + '\n</script></body></html>\n'


def prepare_comparison_gallery(root=ROOT, output=None, navigation=''):
    """Refresh browser-sized previews without rerendering slides or comparisons."""
    from PIL import Image
    output = output or root / 'design-references/figma/collection-review'
    from studio_templates import inspect_templates
    entries = inspect_templates(root)
    rows = rows_for_gallery(root, entries, comparison=True)
    images = {}
    for row in rows:
        images[row['preview']] = row['full']
        for key in ['original', 'overlay', 'difference']:
            if key in row:
                images[row[key]['preview']] = row[key]['full']
    for index, (preview, full) in enumerate(images.items(), 1):
        source, target = output / full, output / preview
        if not source.is_file():
            raise RuntimeError('Missing cached comparison: ' + str(source))
        if not target.exists() or target.stat().st_mtime_ns < source.stat().st_mtime_ns:
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as image:
                image.thumbnail((800, 450), Image.Resampling.LANCZOS)
                image.convert('RGB').save(target, 'WEBP', quality=85, method=4)
        if index % 100 == 0:
            print('Web previews ready:', index, '/', len(images), flush=True)
    for obsolete in (output / 'web').glob('*.webp'):
        if obsolete.relative_to(output).as_posix() not in images:
            obsolete.unlink()
    (output / 'index.html').write_text(gallery_html(entries, root, comparison=True, navigation=navigation), encoding='utf-8')
    return len(rows)
