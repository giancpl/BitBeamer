"""Build local high-resolution original/replica comparisons for the full collection."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib
import io
import html
import json
import multiprocessing
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from asset_library import rsvg_modules
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design-references/figma/collection-review'
PILOT_TEXT={865:(None,[1,2,5,6,7,8,19,20,21,25,26,27,28]),175:(0,[2,3,4]),21:(None,[1,3,5,7]),395:(0,[1,2,3,4,5]),793:(0,[2]),1006:(0,[1,4,7,10,36]),453:(None,[4,8]),542:(0,[4])}
def original(task):
    reference,record,addresses=task;source=ROOT/'design-references/figma/exports'/record['file']
    from PIL import Image
    if hashlib.sha256(source.read_bytes()).hexdigest()!=record['sha256']:
        raise RuntimeError('Changed original reference: '+reference)
    for geometry in (False,True):
        target=OUT/(reference+('-geometry' if geometry else '')+'.png')
        cache=target.with_suffix('.json');key={'source':record['sha256'],'geometry':addresses if geometry else None,'size':[3556,2000]}
        if target.exists() and cache.exists() and json.loads(cache.read_text(encoding='utf-8'))==key:continue
        tree=ET.parse(source).getroot()
        if geometry:
            for address in sorted(set(tuple(a) for a in addresses),reverse=True):
                parent=tree
                try:
                    for i in address[:-1]:parent=parent[i]
                    parent.remove(parent[address[-1]])
                except IndexError:pass
        cairo,Rsvg=rsvg_modules();handle=Rsvg.Handle.new_with_flags(Rsvg.HandleFlags.FLAG_UNLIMITED);handle.set_base_uri(source.resolve().as_uri());handle.write(ET.tostring(tree));handle.close()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,3556,2000);ctx=cairo.Context(surface);ctx.set_source_rgb(249/255,249/255,249/255);ctx.paint();vp=Rsvg.Rectangle();vp.x=vp.y=0;vp.width=3556;vp.height=2000;handle.render_document(ctx,vp);surface.write_to_png(str(target));cache.write_text(json.dumps(key)+'\n', encoding='utf-8')
    return reference

def navigation(root):
    base='../../../'
    links='<nav data-review-navigation><p><a href="'+base+'build/review/bitbeamer-studio-review.pdf">Complete indexed PDF</a> · <a href="'+base+'templates/REVIEW.csv">Review sheet</a> · <a href="'+base+'docs/templates/index.html">Replica gallery and fields</a> · <a href="'+base+'docs/studio-parts/index.html">Reusable parts</a></p>'
    links+='<details><summary>Family comparison PDFs and Overleaf projects</summary><ul>'
    for pdf in sorted((root/'build/review/comparisons').glob('*.pdf')):
        links+='<li><a href="'+base+pdf.relative_to(root).as_posix()+'">'+html.escape(pdf.stem.replace('-',' ').title())+' comparisons</a></li>'
    index=root/'build/review/overleaf/index.json'
    if index.exists():
        for archive in json.loads(index.read_text(encoding='utf-8'))['archives']:
            links+='<li><a href="'+base+'build/review/overleaf/'+archive['archive']+'">'+archive['archive']+'</a> ('+str(len(archive['models']))+' models)</li>'
    return links+'</ul></details></nav>'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',type=Path,default=ROOT/'build/review/studio-template-catalogue.pdf');parser.add_argument('--geometry-pdf',type=Path,default=ROOT/'build/review/studio-collection-geometry.pdf');parser.add_argument('--workers',type=int,default=2);parser.add_argument('--skip-render',action='store_true',help='Reuse existing PDF raster pages after checking their source hashes');parser.add_argument('--refresh-pages',help='Explicit comma-separated changed PDF page numbers; other cached pages must be unchanged')
    parser.add_argument('--gallery-only', action='store_true', help='Refresh lightweight web previews from cached comparisons without compiling or rendering PDFs')
    args=parser.parse_args()
    if args.gallery_only:
        from studio_gallery import prepare_comparison_gallery
        prepare_comparison_gallery(ROOT, OUT, navigation(ROOT))
        print(OUT / 'index.html')
        return
    from PIL import Image,ImageChops,ImageFilter
    import numpy as np
    refresh_pages=[int(p) for p in args.refresh_pages.split(',')] if args.refresh_pages else [];OUT.mkdir(parents=True,exist_ok=True)
    from studio_templates import inspect_templates
    entries=inspect_templates(ROOT);inventory={f['id']:f for f in json.loads((ROOT/'templates/figma-inventory.json').read_text(encoding='utf-8'))['frames']};tasks={}
    for e in entries:
        if not e['references']:continue
        ref=e['references'][0];addresses=[f['source_node'] for f in e.get('fields',[]) if 'source_node'in f]
        n=int(ref[6:])
        if n in PILOT_TEXT:
            group,children=PILOT_TEXT[n];addresses=[([group] if group is not None else [])+[i] for i in children]
        if n==907:
            tree=ET.parse(ROOT/'design-references/figma/exports'/inventory[ref]['file']).getroot();addresses=[[i] for i in range(1,len(tree)) if not tree[i].tag.endswith('defs')]
        tasks[ref]=(ref,inventory[ref],addresses)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        for i,future in enumerate(as_completed(pool.submit(original,t) for t in tasks.values()),1):
            future.result()
            if i%20==0:print('Original comparisons',i,'/',len(tasks),flush=True)
    for pdf,prefix in [(args.pdf,'replica'),(args.geometry_pdf,'geometry')]:
        stamp=OUT/(prefix+'-render.json');signature=hashlib.sha256(pdf.read_bytes()).hexdigest()
        fresh=stamp.exists() and json.loads(stamp.read_text(encoding='utf-8')).get('pdf_sha256')==signature and len(list(OUT.glob(prefix+'-*.png')))==len(entries)
        if not fresh:
            if args.skip_render:raise RuntimeError('Stale raster pages for '+str(pdf))
            if refresh_pages:
                if len(list(OUT.glob(prefix+'-*.png')))!=len(entries) or any(p<1 or p>len(entries) for p in refresh_pages):raise RuntimeError('Partial refresh requires a complete unchanged-size page cache')
                for page in refresh_pages:
                    subprocess.run(['pdftocairo','-png','-singlefile','-f',str(page),'-l',str(page),'-scale-to-x','3556','-scale-to-y','2000',str(pdf),str(OUT/(prefix+f'-{page:03d}'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            else:
                subprocess.run(['pdftocairo','-png','-scale-to-x','3556','-scale-to-y','2000',str(pdf),str(OUT/prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            for obsolete in OUT.glob(prefix+'-*.png'):
                if int(obsolete.stem.split('-')[-1]) > len(entries):
                    obsolete.unlink()
            stamp.write_text(json.dumps({'pdf_sha256':signature})+'\n', encoding='utf-8')
        print('Raster pages ready: '+prefix,flush=True)
    saved=OUT/'measurements.json';previous={row['id']:row for row in json.loads(saved.read_text(encoding='utf-8'))} if saved.exists() else {}
    report=[];families={}
    def dilate(mask):
        horizontal=mask.copy()
        for shift in range(1,6):
            horizontal[:,shift:] |= mask[:,:-shift]
            horizontal[:,:-shift] |= mask[:,shift:]
        result=horizontal.copy()
        for shift in range(1,6):
            result[shift:,:] |= horizontal[:-shift,:]
            result[:-shift,:] |= horizontal[shift:,:]
        return result
    for page,e in enumerate(entries,1):
        name=e['id'];reference=e['references'][0] if e['references'] else None
        replicas=sorted(OUT.glob('replica-*.png'),key=lambda p:int(p.stem.split('-')[-1]));geometries=sorted(OUT.glob('geometry-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
        pair={'id':name,'reference':reference,'category':e['category'],'status':e.get('status','in review'),'page':page,'intentional_differences':e.get('intentional_differences',[])}
        cached=previous.get(name,{})
        overlay=OUT/(name+'-overlay.png');difference=OUT/(name+'-difference.png')
        inputs=[replicas[page-1],geometries[page-1]]+([OUT/(reference+'.png'),OUT/(reference+'-geometry.png')] if reference else [])
        reusable=reference and cached.get('page')==page and cached.get('reference')==reference and overlay.exists() and difference.exists() and min(overlay.stat().st_mtime_ns,difference.stat().st_mtime_ns)>max(p.stat().st_mtime_ns for p in inputs)
        if reusable:
            for key in ['tolerance_px','unmatched_boundary_pixels','boundary_pixels','mean_graphic_channel_difference','screen_note']:
                if key in cached:pair[key]=cached[key]
        if reference and not reusable:
            replica=Image.open(replicas[page-1]).convert('RGB').crop((0,0,3556,2000))
            orig=Image.open(OUT/(reference+'.png')).convert('RGB');Image.blend(orig,replica,.5).save(OUT/(name+'-overlay.png'))
            left=Image.open(OUT/(reference+'-geometry.png')).convert('RGB');right=Image.open(geometries[page-1]).convert('RGB').crop((0,0,3556,2000));diff=ImageChops.difference(left,right);diff.point(lambda x:min(255,x*4)).save(OUT/(name+'-difference.png'))
            def edges(im):
                a=np.asarray(im.convert('L').filter(ImageFilter.FIND_EDGES))>35;a[:8,:]=False;a[-40:,:]=False;a[:,:8]=False;a[:,-8:]=False;return Image.fromarray((a*255).astype('uint8'))
            a,b=edges(left),edges(right);aa=np.asarray(a)>0;bb=np.asarray(b)>0;unmatched=int((aa & ~dilate(bb)).sum()+(bb & ~dilate(aa)).sum())
            pair.update(tolerance_px=5,unmatched_boundary_pixels=unmatched,boundary_pixels=int(aa.sum()+bb.sum()),mean_graphic_channel_difference=round(float(np.asarray(diff).mean()),4),screen_note='Boundary/effect screen; not an automatic approval or global fidelity certificate.')
        if page%20==0:print('Compared',page,'/',len(entries),flush=True)
        report.append(pair);families.setdefault(e['category'],[]).append((e,replicas[page-1],reference))
    # Raster original comparisons are local review evidence; source text remains native in the replica PDF.
    cairo,_=rsvg_modules();reviewdir=ROOT/'build/review/comparisons';reviewdir.mkdir(exist_ok=True)
    for family,items in families.items():
        target=reviewdir/(family.lower().replace(' ','-')+'.pdf')
        with cairo.PDFSurface(str(target),1200,430) as surface:
            ctx=cairo.Context(surface)
            for e,replica,ref in items:
                ctx.set_source_rgb(.98,.98,.98);ctx.paint();ctx.set_source_rgb(0,.11,.88);ctx.select_font_face('sans-serif');ctx.set_font_size(15);ctx.move_to(24,24);ctx.show_text(e['id']+' | '+(ref or 'Supplementary'))
                for x,img in [(20,OUT/(ref+'.png') if ref else None),(610,replica)]:
                    if img:
                        thumbnail=Image.open(img).convert('RGB');thumbnail.thumbnail((1140,642));buffer=io.BytesIO();thumbnail.save(buffer,format='PNG');buffer.seek(0);image=cairo.ImageSurface.create_from_png(buffer);ctx.save();ctx.translate(x,45);ctx.scale(570/image.get_width(),321/image.get_height());ctx.set_source_surface(image);ctx.paint();ctx.restore()
                ctx.set_font_size(9);ctx.move_to(24,397);ctx.show_text('Original / editable reconstruction. Inter and English copy intentionally differ. Status: '+e.get('status','in review')+'.');ctx.show_page()
    (OUT/'measurements.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    from studio_gallery import prepare_comparison_gallery
    prepare_comparison_gallery(ROOT, OUT, navigation(ROOT))
    print(OUT/'index.html')
if __name__=='__main__':main()
