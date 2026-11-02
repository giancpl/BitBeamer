"""Typed Studio content slots and reproducible card-only replacement backgrounds."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    raw = path.read_bytes()
    if path.suffix in ('.svg', '.json', '.tex', '.sty'):
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()


def card_recipe(root, field):
    match = re.search(r'images/studio/collection/([a-z0-9-]+)\.pdf', field.get('default', ''))
    if not match:
        return None
    name = match.group(1)
    source = root/'images/studio/collection/source'/(name+'.svg')
    tree = ET.parse(source).getroot()
    nodes = [n for n in tree if not n.tag.endswith('defs')]
    panels = [n for n in nodes if n.tag.endswith('g') and n.get('filter') and
              len(n) == 1 and n[0].tag.endswith('rect')]
    if len(panels) != 1 or len(nodes) < 2:
        return None
    rect = panels[0][0]
    w, h = float(rect.get('width', 0)), float(rect.get('height', 0))
    if abs(w-h) >= 2 or not rect.get('rx') or not 0 < w < 1200:
        return None
    x, y, rw, rh = map(float, tree.get('viewBox').split())
    # Preserve definitions, inherited transforms and the exact shadow canvas.
    derived = copy.deepcopy(tree)
    for child in list(derived):
        if not child.tag.endswith('defs'):
            derived.remove(child)
    derived.append(copy.deepcopy(panels[0]))
    body = ET.tostring(derived, encoding='utf-8')+b'\n'
    cx = float(rect.get('x'))+w/2-x
    cy = float(rect.get('y'))+h/2-y
    return dict(name=name+'-panel', parent=source.relative_to(root).as_posix(),
                parent_sha256=digest(source), source_bytes=body,
                frame_box=[rw, rh], content=[cx, cy, w*.65, h*.65])


def annotate(root=ROOT):
    """Assign once; stored slot numbers survive source/metadata reordering."""
    path = root/'templates/index.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    recipes = {}
    for entry in data['templates']:
        counts = {'text': 0, 'graphic': 0, 'file': 0}
        for field in entry['fields']:
            if field.get('slot'):
                counts[field['type']] = max(counts[field['type']], field['slot']['number'])
        # Stable initial reading order, grouping very small vertical differences.
        def order(field):
            box = field.get('box')
            return (round(box[1]/(entry['canvas'][1]*.04)), box[0]) if box else (999, 0)
        for field in sorted(entry['fields'], key=order):
            kind = field['type']
            if not field.get('slot'):
                counts[kind] += 1
                field['slot'] = {'number': counts[kind], 'key': f'{kind}/{counts[kind]}'}
            if kind != 'graphic':
                continue
            field['slot'].setdefault('role', 'whole graphic')
            recipe = card_recipe(root, field)
            if recipe:
                field['slot'].update(role='card content', frame='images/studio/slots/'+recipe['name']+'.pdf',
                                     content=recipe['content'])
                recipes[recipe['name']] = recipe
        entry['slot_parts'] = sorted({f['slot']['frame'] for f in entry['fields'] if f.get('slot',{}).get('frame')})
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    folder = root/'images/studio/slots'
    (folder/'source').mkdir(parents=True, exist_ok=True)
    records = []
    for name, recipe in sorted(recipes.items()):
        target = folder/'source'/(name+'.svg')
        target.write_bytes(recipe.pop('source_bytes'))
        recipe.update(source=target.relative_to(root).as_posix(), source_sha256=digest(target),
                      pdf='images/studio/slots/'+name+'.pdf')
        records.append(recipe)
    (folder/'manifest.json').write_text(json.dumps({'schema': 1, 'parts': records}, indent=2)+'\n', encoding='utf-8')
    return len(records)


def prepare(root=ROOT, check=False):
    path = root/'images/studio/slots/manifest.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for item in data['parts']:
        source, target = root/item['source'], root/item['pdf']
        if digest(root/item['parent']) != item['parent_sha256'] or digest(source) != item['source_sha256']:
            raise RuntimeError('Changed Studio slot source: '+item['name'])
        current = target.is_file() and digest(target) == item.get('pdf_sha256')
        if check and not current:
            raise RuntimeError('Stale Studio slot background: '+item['name']+'. Run python3 scripts/studio_slots.py prepare.')
        if not check and not current:
            from asset_library import rsvg_modules
            cairo, Rsvg = rsvg_modules()
            w,h=item['frame_box']
            handle=Rsvg.Handle.new_from_file(str(source))
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,round(w),round(h))
            viewport=Rsvg.Rectangle();viewport.x=viewport.y=0;viewport.width=w;viewport.height=h
            handle.render_document(cairo.Context(surface),viewport)
            with cairo.PDFSurface(str(target),w,h) as pdf:
                pdf.restrict_to_version(cairo.PDF_VERSION_1_5)
                context=cairo.Context(pdf);context.set_source_surface(surface);context.paint()
            item['pdf_sha256']=digest(target)
    if not check:
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    return len(data['parts'])


def validate(entries):
    for entry in entries:
        expected_frames={f.get('slot',{}).get('frame') for f in entry['fields'] if f.get('slot',{}).get('frame')}
        if expected_frames != set(entry.get('slot_parts', [])):
            raise RuntimeError('Studio slot dependencies disagree in '+entry['id'])
        keys = set()
        for field in entry['fields']:
            slot=field.get('slot',{})
            key=slot.get('key')
            if not isinstance(slot.get('number'),int) or slot['number'] < 1 or not key or key in keys or key != f"{field['type']}/{slot.get('number')}":
                raise RuntimeError('Invalid Studio slot in '+entry['id']+'/'+field['name'])
            keys.add(key)
            if field['type']=='graphic' and (not field.get('box') or any(v <= 0 for v in field['box'][2:])):
                raise RuntimeError('Graphic slot needs positive bounds: '+entry['id']+'/'+field['name'])


def declarations(entry):
    lines=[]
    for field in entry['fields']:
        slot=field['slot'];n=slot['number'];native=field['name'];name=entry['id']
        if field['type']=='text':
            lines.append(r'\DeclareStudioTextSlot{'+name+'}{'+str(n)+'}{'+native+'}')
        elif field['type']=='file':
            lines.append(r'\DeclareStudioFileSlot{'+name+'}{'+str(n)+'}{'+native+'}')
        else:
            w,h=field['box'][2:];frame=slot.get('frame','')
            cx,cy,fw,fh=slot.get('content',[w/2,h/2,w*.9,h*.9])
            values=[name,str(n),native,f'{w:g}',f'{h:g}',frame,','.join(f'{v:g}' for v in (cx,cy,fw,fh))]
            lines.append(r'\DeclareStudioGraphicSlot'+''.join('{'+v+'}' for v in values))
        if field.get('block'):
            block=field['block']
            values=[name,str(n),native,block['heading'],block['body'],f"{block['heading_size']:g}",f"{block['heading_leading']:g}",f"{block['body_size']:g}",f"{block['body_leading']:g}"]
            lines.append(r'\DeclareStudioBlockSlot'+''.join('{'+v+'}' for v in values))
    return lines


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('annotate','prepare','check'))
    args=parser.parse_args()
    if args.action=='annotate':print('Separated card frames:',annotate())
    else:print('Prepared Studio slot frames:',prepare(check=args.action=='check'))
