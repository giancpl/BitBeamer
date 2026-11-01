"""Extract reviewed SVG regions, then independently prepare/check clone-ready PDFs."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from asset_library import render_svg, rsvg_modules
ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
HREF = '{http://www.w3.org/1999/xlink}href'
ET.register_namespace('', NS)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
def digest(path):
    data = path.read_bytes()
    if path.suffix in ('.svg', '.json', '.tex', '.sty'):
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()
def references(elements):
    result = set()
    for root in elements:
        for e in root.iter():
            for value in e.attrib.values():
                result.update(re.findall(r'url\(#([^)]*)\)', value))
            for key in (HREF, 'href'):
                value = e.get(key, '')
                if value.startswith('#'):
                    result.add(value[1:])
    return result

def extract(root=ROOT, exports=None):
    folder = root / 'images/studio/parts'
    recipes = json.loads((folder / 'recipes.json').read_text())['parts']
    inventory = {r['id']: r for r in json.loads((root / 'templates/figma-inventory.json').read_text())['frames']}
    exports = exports or root / 'design-references/figma/exports'
    records = []
    for recipe in recipes:
        record = dict(recipe)
        original = inventory[record['reference']]
        source = exports / original['file']
        if hashlib.sha256(source.read_bytes()).hexdigest() != original['sha256']:
            raise RuntimeError('Reference changed: ' + str(source))
        tree = ET.parse(source).getroot()
        parent = tree if recipe['group'] is None else tree[recipe['group']]
        chosen = [copy.deepcopy(parent[i]) for i in recipe['children']]
        lookup = {e.get('id'): e for e in tree.iter() if e.get('id')}
        known = {e.get('id') for node in chosen for e in node.iter() if e.get('id')}
        definitions = []
        pending = references(chosen) - known
        while pending:
            key = sorted(pending)[0]
            if key not in lookup:
                raise RuntimeError('Unresolved SVG definition: ' + key)
            node = copy.deepcopy(lookup[key]); definitions.append(node)
            known.update(e.get('id') for e in node.iter() if e.get('id'))
            pending = references(chosen + definitions) - known
        x,y,w,h = recipe['render_box']
        attributes = {k:v for k,v in tree.attrib.items() if k not in ('width','height','viewBox')}
        attributes.update(width=str(w),height=str(h),viewBox=f'{x} {y} {w} {h}')
        svg = ET.Element('{'+NS+'}svg', attributes)
        defs = ET.SubElement(svg, '{'+NS+'}defs'); defs.extend(definitions)
        # The selected group's inherited transforms and clipping remain in force.
        group = ET.SubElement(svg, '{'+NS+'}g', dict(parent.attrib) if parent is not tree else {})
        group.extend(chosen)
        # Include any inherited clipping dependencies, too.
        extra = references([group]) - known
        for key in sorted(extra):
            if key in lookup:
                defs.append(copy.deepcopy(lookup[key]))
        dependencies = []
        for e in svg.iter():
            for key in (HREF, 'href'):
                value=e.get(key, '')
                if value.startswith('data:image/'):
                    header, encoded = value.split(',',1)
                    raw=base64.b64decode(encoded)
                    ext='.jpg' if 'jpeg' in header else '.png'
                    name=hashlib.sha256(raw).hexdigest()+ext
                    path=folder/'source/resources'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
                    e.set(key,'resources/'+name)
                    dependencies.append({'path':str(path.relative_to(root)), 'sha256':digest(path)})
        path=folder/'source'/(recipe['name']+'.svg');path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(ET.tostring(svg,encoding='utf-8')+b'\n')
        record.update(source=str(path.relative_to(root)),source_sha256=digest(path),
                      reference_sha256=original['sha256'],canvas=[original['width'],original['height']],
                      dependencies=dependencies,definition_ids=sorted(references([svg])))
        records.append(record)
    (folder/'manifest.json').write_text(json.dumps({'schema':1,'status':'in-review','parts':records},indent=2)+'\n')
    return records

def prepare(root=ROOT, check=False, converter='auto'):
    folder=root/'images/studio/parts';manifest=folder/'manifest.json'
    data=json.loads(manifest.read_text()); records=data['parts']
    for part in records:
        source=root/part['source']; target=folder/(part['name']+'.pdf')
        dependencies=all((root/d['path']).is_file() and digest(root/d['path'])==d['sha256'] for d in part['dependencies'])
        if not dependencies:
            raise RuntimeError('Missing or changed resource for '+part['name'])
        current=(digest(source)==part['source_sha256'] and target.is_file() and digest(target)==part.get('pdf_sha256') and (not part.get('png_sha256') or (target.with_suffix('.png').is_file() and digest(target.with_suffix('.png'))==part['png_sha256'])))
        if check and not current:
            raise RuntimeError('Stale Studio part '+part['name']+'. Run python3 scripts/studio_parts.py prepare.')
        if not check and not current:
            from studio_jpeg import jpeg_pdf
            photographic=converter!='inkscape' and any(d['path'].lower().endswith(('.jpg','.jpeg')) for d in part['dependencies'])
            if photographic and jpeg_pdf(source,target):
                part['renderer']='Original JPEG streams; no recompression.'
            elif part['name'] in ('card-1','card-2','card-3') and converter != 'inkscape':
                # Cairo PDF produces a hairline at the boundary of this compound
                # inset/drop-shadow filter. Rasterize only the panel at the original 2000px canvas resolution (~564 dpi on a 90mm slide).
                cairo,Rsvg=rsvg_modules()
                handle=Rsvg.Handle.new_from_file(str(source))
                w,h=part['render_box'][2:]
                surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,round(w),round(h))
                context=cairo.Context(surface);context.set_source_rgb(249/255,249/255,249/255);context.paint()
                viewport=Rsvg.Rectangle();viewport.x=viewport.y=0;viewport.width=w;viewport.height=h
                handle.render_document(context,viewport)
                png=target.with_suffix('.png');surface.write_to_png(str(png))
                with cairo.PDFSurface(str(target),w,h) as pdf:
                    context=cairo.Context(pdf)
                    context.set_source_surface(surface);context.paint()
                part['effect_fallback']='Panel filter only, original source resolution (~564 dpi), composited on the fixed paper background; icons and text remain vector.'
                part['png_sha256']=digest(png)
            else:
                render_svg(source,target,converter,crop=False)
            part['source_sha256']=digest(source);part['pdf_sha256']=digest(target)
    if not check:
        manifest.write_text(json.dumps(data,indent=2)+'\n')
    return len(records)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('extract','prepare','check'))
    parser.add_argument('--exports',type=Path)
    parser.add_argument('--converter',choices=('auto','rsvg','inkscape'),default='auto')
    args=parser.parse_args()
    if args.action=='extract':
        print('Extracted',len(extract(exports=args.exports)),'parts; run prepare next.')
    else:
        print('Checked' if args.action=='check' else 'Prepared',prepare(check=args.action=='check',converter=args.converter),'Studio parts.')
if __name__=='__main__':
    main()
