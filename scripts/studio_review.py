"""Read the sole editable Studio review ledger; never infer graphical approval."""
import csv
import io
import json

STATUSES = {'in review', 'changes requested', 'approved', 'supplementary'}


def load_review(root, entries=None):
    if entries is None:
        entries = json.loads((root / 'templates/index.json').read_text(encoding='utf-8'))['templates']
    data = json.loads((root / 'templates/review.json').read_text(encoding='utf-8'))
    known = {e['id']: e for e in entries}
    if data.get('schema') != 1 or set(data.get('templates', {})) != set(known):
        raise RuntimeError('Review ledger must contain every current composition exactly once')
    chosen = data.get('selection', [])
    if not isinstance(chosen, list) or not chosen or len(set(chosen)) != len(chosen) or set(chosen) - set(known):
        raise RuntimeError('Invalid or repeated selected template in templates/review.json')
    reusable = data.get('reusable_selection', [])
    if not isinstance(reusable, list) or len(reusable) != len(set(reusable)) or set(reusable) - set(known):
        raise RuntimeError('Invalid reusable_selection in templates/review.json')
    for name, item in data['templates'].items():
        if item.get('status') not in STATUSES or not isinstance(item.get('notes'), str):
            raise RuntimeError('Invalid review status or notes for ' + name)
        if not isinstance(item.get('use', ''), str) or not isinstance(item.get('example', {}), dict):
            raise RuntimeError('Invalid usage example for ' + name)
        palette_reviews=item.get('palette_reviews',{})
        if set(palette_reviews)-set(known[name].get('palettes',[])):
            raise RuntimeError('Unknown palette review for '+name)
        for palette,review in palette_reviews.items():
            if review.get('status') not in STATUSES or not isinstance(review.get('notes'),str):raise RuntimeError('Invalid palette review for '+name+'/'+palette)
        unknown = set(item.get('example', {})) - {f['name'] for f in known[name].get('fields', [])}
        if unknown:
            raise RuntimeError('Unknown example fields for ' + name + ': ' + ', '.join(sorted(unknown)))
        if not all(isinstance(v, str) for v in item.get('example', {}).values()):
            raise RuntimeError('Example values must be LaTeX strings for ' + name)
    return data


def reviewed_entries(root, entries):
    ledger = load_review(root, entries)
    return [dict(e, status=ledger['templates'][e['id']]['status'],
                 review_notes=ledger['templates'][e['id']]['notes'],
                 palette_reviews=ledger['templates'][e['id']].get('palette_reviews',{})) for e in entries]


def selected(root, entries=None):
    data = load_review(root, entries)
    return [dict(id=name, **data['templates'][name]) for name in data['selection']]


def review_csv(root, entries):
    data = load_review(root, entries)
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['id','category','reference','status','catalogue_page','alias_of','requested_changes'])
    for page, entry in enumerate(entries, 1):
        item = data['templates'][entry['id']]
        writer.writerow([entry['id'],entry['category'],','.join(entry['references']),item['status'],page,'',item['notes']])
    return output.getvalue()


STANDARD_COVERS = ('cover', 'cover-light', 'cover-photo')
STANDARD_AGENDAS = ('contents', 'contents-five')
STANDARD_INTRODUCTIONS = ('team-presentation',)


def package_selection(root):
    # Include optional covers, team introduction and measured agendas without changing the showcase selection.
    data = load_review(root)
    names = list(dict.fromkeys(data['selection'] + list(STANDARD_COVERS) + list(STANDARD_AGENDAS) + list(STANDARD_INTRODUCTIONS)))
    return [dict(id=name, **data['templates'][name]) for name in names]


def require_approved(root):
    pending = [item['id'] for item in package_selection(root) if item['status'] != 'approved']
    metadata={e['id']:e for e in json.loads((root/'templates/index.json').read_text())['templates']}
    for item in package_selection(root):
        for palette in metadata[item['id']].get('palettes',[]):
            if item.get('palette_reviews',{}).get(palette,{}).get('status')!='approved':pending.append(item['id']+'/'+palette)
    if pending:
        raise RuntimeError('Studio release requires explicit approval of selected models: ' + ', '.join(pending)
                           + '. Use review packaging until graphical review is complete.')


def example_command(item):
    from studio_guides import command
    return command(item['id'],item.get('example',{}))
