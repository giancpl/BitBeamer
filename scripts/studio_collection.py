"""Maintain prepared measured Studio parts; ordinary builds only check hashes."""
import argparse
import hashlib
import json
from pathlib import Path
from asset_library import render_svg,rsvg_modules
from studio_parts import digest
ROOT=Path(__file__).resolve().parents[1]
def prepare(root=ROOT,check=False,converter='auto'):
    folder=root/'images/studio/collection';path=folder/'manifest.json'
    data=json.loads(path.read_text(encoding='utf-8'));parts=data['parts']
    for i,part in enumerate(parts,1):
        source=root/part['source'];target=folder/(part['name']+'.pdf')
        if any(not (root/d['path']).is_file() or digest(root/d['path'])!=d['sha256'] for d in part['dependencies']):
            raise RuntimeError('Missing or changed dependency in '+part['name'])
        current=source.is_file() and digest(source)==part['source_sha256'] and target.is_file() and digest(target)==part.get('pdf_sha256')
        if check and not current:raise RuntimeError('Stale Studio collection part '+part['name']+'. Run python3 scripts/studio_collection.py prepare.')
        if not check and not current:
            from studio_jpeg import jpeg_pdf
            photographic = converter!='inkscape' and any(d['path'].lower().endswith(('.jpg','.jpeg')) for d in part['dependencies'])
            if photographic and jpeg_pdf(source,target):
                part['renderer']='Original JPEG streams with native crop transforms and separate filter layers; no JPEG recompression.'
            elif '<filter ' in source.read_text(encoding='utf-8') and converter!='inkscape':
                # Preserve compound filter appearance at the original source resolution.
                cairo,Rsvg=rsvg_modules();handle=Rsvg.Handle.new_from_file(str(source))
                w,h=part['render_box'][2:];scale=part.get('render_scale',1)
                surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,round(w*scale),round(h*scale));context=cairo.Context(surface);context.scale(scale,scale)
                if part.get('paper_background')=='F9F9F9':
                    context.set_source_rgb(249/255,249/255,249/255);context.paint()
                # Preserve transparent padding so the crop cannot hide adjacent text.
                viewport=Rsvg.Rectangle();viewport.x=viewport.y=0;viewport.width=w;viewport.height=h;handle.render_document(context,viewport)
                with cairo.PDFSurface(str(target),w,h) as pdf:
                    pdf.restrict_to_version(cairo.PDF_VERSION_1_5)
                    context=cairo.Context(pdf);context.scale(1/scale,1/scale);context.set_source_surface(surface);context.paint()
                part['effect_fallback']=('Twice-source-resolution SVG filter on F9F9F9 paper; avoids PDF mask seams. Main text remains editable.' if part.get('paper_background')=='F9F9F9' else 'Original-source-resolution compound filter with transparent padding. Main text remains editable.')
            else:render_svg(source,target,converter,crop=False)
            part['source_sha256']=digest(source);part['pdf_sha256']=digest(target)
        if not check and i%40==0:print('Prepared',i,'/',len(parts),flush=True)
    if not check:path.write_text(json.dumps(data,indent=2)+'\n', encoding='utf-8')
    return len(parts)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','check'));parser.add_argument('--converter',choices=('auto','rsvg','inkscape'),default='auto')
    args=parser.parse_args();print('Collection parts:',prepare(check=args.action=='check',converter=args.converter))
