"""Verify neutral artwork and prepare icon contrast resources, without inventing slide palettes."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n') if path.suffix in {'.svg','.json'} else path.read_bytes()).hexdigest()

def check(root=ROOT):
    """Verify retained neutral images and icon contrast files without conversion."""
    count = 0
    for folder in ('neutral', 'icon-palettes'):
        manifest = root / 'images/studio' / folder / 'manifest.json'
        if not manifest.exists():
            continue
        for part in json.loads(manifest.read_text())['parts']:
            keys = ('source', 'pdf', 'parent') if folder == 'icon-palettes' else ('source', 'pdf')
            for key in keys:
                if digest(root / part[key]) != part[key + '_sha256']:
                    raise RuntimeError('Changed prepared Studio artwork: ' + part[key])
            count += 1
    return count


def prepare_icons(root=ROOT):
    """Regenerate monochrome icon derivatives without touching the shared library."""
    from asset_library import render_svg,write_if_changed
    folder=root/'images/studio/icon-palettes';(folder/'source').mkdir(parents=True,exist_ok=True)
    path=folder/'manifest.json';old={a['name']:a for a in json.loads(path.read_text())['parts']} if path.exists() else {}
    records=[]
    def role(color):
        r,g,b=[int(color[i:i+2],16) for i in (1,3,5)]
        if b>r+60 and b>g+60 or max(r,g,b)<90:return 'ink'
        if min(r,g,b)>225:return 'paper'
        return 'other'
    for row in json.loads((root/'assets/index.json').read_text()):
        if row['category'].split('/')[0] in ['logos','backgrounds']:continue
        parent=root/'assets'/row['category']/(row['name']+'.svg')
        if not parent.exists():continue
        text=parent.read_text();colors=set(re.findall(r'#[0-9a-fA-F]{6}\b',text))
        if not colors or '<image' in text or any(role(c)=='other' for c in colors):continue
        converted=re.sub(r'#[0-9a-fA-F]{6}\b',lambda m:'#FFFFFF' if role(m[0])=='ink' else '#001CE0',text)
        if converted==text:continue
        source=folder/'source'/(row['name']+'.svg');pdf=folder/(row['name']+'.pdf');write_if_changed(source,converted.encode())
        record={'name':row['name'],'parent':parent.relative_to(root).as_posix(),'parent_sha256':digest(parent),'source':source.relative_to(root).as_posix(),'source_sha256':digest(source),'pdf':pdf.relative_to(root).as_posix(),'crop':'same ink bounds as original library'}
        prior=old.get(row['name'])
        if not prior or prior.get('crop')!=record['crop'] or prior['source_sha256']!=record['source_sha256'] or not pdf.exists() or digest(pdf)!=prior['pdf_sha256']:render_svg(source,pdf,crop=True)
        record['pdf_sha256']=digest(pdf);records.append(record)
    path.write_text(json.dumps({'schema':1,'description':'Monochrome named-icon alternatives for blue Studio slides; originals remain unchanged.','parts':records},indent=2)+'\n')
    return len(records)

def prepare(root=ROOT):
    """Prepare icon contrast alternatives; slide colours come from originals."""
    return prepare_icons(root)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','check']);a=p.parse_args()
    print('Prepared Studio artwork:',prepare() if a.action=='prepare' else check())
