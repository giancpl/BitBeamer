"""Check original SVG bounds and actual template placements in source coordinates."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from asset_library import rsvg_modules
ROOT=Path(__file__).resolve().parents[1]

def measure(part, inventory):
    source=ROOT/'design-references/figma/exports'/inventory[part['reference']]['file']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=part['reference_sha256']:
        raise RuntimeError('Changed original reference: '+part['reference'])
    tree=ET.parse(source).getroot()
    def at(address):
        node=tree
        for index in address:node=node[index]
        return node
    for omitted in sorted(part.get('omitted_nodes',[]),reverse=True):
        parent=at(omitted[:-1]);parent.remove(parent[omitted[-1]])
    ids=[]
    for i,address in enumerate(part['nodes']):
        node=at(address);key='studio-geometry-'+str(i);node.set('id',key);ids.append(key)
    cairo,Rsvg=rsvg_modules();handle=Rsvg.Handle.new_with_flags(Rsvg.HandleFlags.FLAG_UNLIMITED)
    handle.set_base_uri(source.resolve().as_uri());handle.write(ET.tostring(tree));handle.close()
    viewport=Rsvg.Rectangle();viewport.x=viewport.y=0;viewport.width=part['canvas'][0];viewport.height=part['canvas'][1]
    boxes=[]
    for key in ids:
        ok,ink,_=handle.get_geometry_for_layer('#'+key,viewport)
        if not ok:raise RuntimeError('Cannot measure '+part['name'])
        boxes.append([ink.x,ink.y,ink.x+ink.width,ink.y+ink.height])
    x,y,w,h=part['render_box'];left=max(x,min(b[0] for b in boxes));top=max(y,min(b[1] for b in boxes))
    right=min(x+w,max(b[2] for b in boxes));bottom=min(y+h,max(b[3] for b in boxes))
    return [round(left,5),round(top,5),round(max(0,right-left),5),round(max(0,bottom-top),5)]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--record',action='store_true',help='Record independently measured content bounds from local originals')
    args=parser.parse_args();path=ROOT/'images/studio/collection/manifest.json';manifest=json.loads(path.read_text(encoding='utf-8'));inventory={f['id']:f for f in json.loads((ROOT/'templates/figma-inventory.json').read_text(encoding='utf-8'))['frames']}
    worst=0;count=0
    for part in manifest['parts']:
        actual=measure(part,inventory)
        if args.record:part['content_box']=actual;part['geometry_method']='Original SVG ink bounds, intersected with the intentional rendering crop; shadows have a separate render box.'
        error=max(abs(a-b) for a,b in zip(actual,part['content_box']))*min(3556/part['canvas'][0],2000/part['canvas'][1]);worst=max(worst,error);count+=1
        if error>5:raise RuntimeError('Content bounds differ by '+str(error)+' pixels: '+part['name'])
    # Check coordinates in the actual LaTeX command, rather than metadata alone.
    placements=0
    entries=json.loads((ROOT/'templates/index.json').read_text(encoding='utf-8'))['templates'];parts={p['name']:p for p in manifest['parts']}
    for e in entries:
        source=(ROOT/e['source']).read_text(encoding='utf-8')
        for f in e.get('fields',[]):
            match=re.search(r'images/studio/collection/([a-z0-9-]+)\.pdf',f.get('default',''))
            if not match:continue
            cmd=re.search(r'\\studiographfield\{'+re.escape(f['name'])+r'\}((?:\{[-+0-9.]+\}){4})',source)
            if not cmd:raise RuntimeError('Missing measured graphic placement: '+e['id']+'/'+f['name'])
            actual=[float(v) for v in re.findall(r'\{([-+0-9.]+)\}',cmd.group(1))];expected=parts[match.group(1)]['render_box'];scale=min(3556/e['canvas'][0],2000/e['canvas'][1])
            error=max(abs(a-b) for a,b in zip(actual,expected))*scale;worst=max(worst,error)
            if error>5:raise RuntimeError('Placement differs by '+str(error)+' pixels: '+e['id']+'/'+f['name'])
            placements+=1
    if args.record:path.write_text(json.dumps(manifest,indent=2)+'\n', encoding='utf-8')
    report={'measured_parts':count,'checked_placements':placements,'maximum_source_coordinate_error_px':round(worst,5),'comparison_height_px':2000,'tolerance_px':5,'scope':'Original source bounds and LaTeX placement coordinates. Effects and rendered boundaries require separate graphical review.'}
    target=ROOT/'build/review/source-geometry.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
