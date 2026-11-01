"""Extract reproducible SVG regions while closing definitions and raster dependencies."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from studio_parts import digest, references, NS, HREF
ROOT = Path(__file__).resolve().parents[1]

def extract_part(root, reference, name, nodes, box, omit=(), content_box=None):
    inventory = {f['id']:f for f in json.loads((root/'templates/figma-inventory.json').read_text(encoding='utf-8'))['frames']}
    record = inventory[reference]
    original = root/'design-references/figma/exports'/record['file']
    if hashlib.sha256(original.read_bytes()).hexdigest() != record['sha256']:
        raise RuntimeError('Changed original: ' + reference)
    tree = ET.parse(original).getroot()
    def at(address):
        n=tree
        for index in address:n=n[index]
        return n
    folder=root/'images/studio/collection'
    svg=ET.Element('{'+NS+'}svg',{k:v for k,v in tree.attrib.items() if k not in ('width','height','viewBox')})
    x,y,w,h=box;svg.attrib.update(width=str(w),height=str(h),viewBox=f'{x} {y} {w} {h}')
    defs=ET.SubElement(svg,'{'+NS+'}defs');clones={}
    for address in sorted(nodes):
        parent=svg
        for depth in range(1,len(address)):
            prefix=tuple(address[:depth])
            if prefix not in clones:
                ancestor=at(prefix);clones[prefix]=ET.SubElement(parent,ancestor.tag,dict(ancestor.attrib))
            parent=clones[prefix]
        leaf=copy.deepcopy(at(address))
        for excluded in sorted(omit,reverse=True):
            if list(excluded[:len(address)])!=list(address):continue
            relative=excluded[len(address):]
            if not relative:continue
            selected=leaf
            for index in relative[:-1]:selected=selected[index]
            selected.remove(selected[relative[-1]])
        parent.append(leaf)
    lookup={n.get('id'):n for n in tree.iter() if n.get('id')}
    while True:
        known={n.get('id') for n in svg.iter() if n.get('id')};pending=references([svg])-known
        if not pending:break
        key=sorted(pending)[0]
        if key not in lookup:raise RuntimeError('Unresolved definition: '+key)
        defs.append(copy.deepcopy(lookup[key]))
    resources={}
    for n in svg.iter():
        for key in (HREF,'href'):
            value=n.get(key,'')
            if not value.startswith('data:image/'):continue
            header,payload=value.split(',',1);raw=base64.b64decode(payload)
            filename=hashlib.sha256(raw).hexdigest()+('.jpg' if 'jpeg' in header else '.png')
            target=folder/'source/resources'/filename;target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(raw)
            n.set(key,'resources/'+filename);resources[target.relative_to(root).as_posix()]={'path':target.relative_to(root).as_posix(),'sha256':digest(target)}
    source=folder/'source'/(name+'.svg');source.parent.mkdir(parents=True,exist_ok=True)
    source.write_bytes(ET.tostring(svg,encoding='utf-8')+b'\n')
    return {'name':name,'reference':reference,'reference_sha256':record['sha256'],'canvas':[record['width'],record['height']],
            'source':source.relative_to(root).as_posix(),'source_sha256':digest(source),'nodes':nodes,'omitted_nodes':list(omit),
            'render_box':box,'content_box':content_box or box,'anchor':box[:2],'dependencies':list(resources.values()),'definition_ids':sorted(references([svg]))}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name');parser.add_argument('--reference',required=True)
    parser.add_argument('--nodes',required=True,help='JSON list of SVG child-index paths')
    parser.add_argument('--box',required=True,help='JSON [x,y,width,height] in original source units')
    parser.add_argument('--omit',default='[]',help='JSON list of nested child-index paths to remove')
    args=parser.parse_args()
    if not args.name.replace('-','').isalnum():raise ValueError('Use a simple alphanumeric part name')
    part=extract_part(ROOT,args.reference,args.name,json.loads(args.nodes),json.loads(args.box),json.loads(args.omit))
    path=ROOT/'images/studio/collection/manifest.json';data=json.loads(path.read_text(encoding='utf-8'))
    data['parts']=[p for p in data['parts'] if p['name']!=args.name]+[part]
    path.write_text(json.dumps(data,indent=2)+'\n', encoding='utf-8')
    print('Extracted '+args.name+'. Prepare its PDF with python3 scripts/studio_collection.py prepare.')
if __name__=='__main__':main()
