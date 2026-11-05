"""Generate local 2000 px source/replica comparisons; original exports never enter Git."""
import argparse
import hashlib
import html
import json
import math
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def measure_anchors(original,replica,mask,layout,width,height):
    """Match vector component boxes independently of the text and appearance residual."""
    source_scale=min(width/original.rect.width,height/original.rect.height)
    ox=(width-original.rect.width*source_scale)/2;oy=(height-original.rect.height*source_scale)/2
    target_scale=min(width/replica.rect.width,height/replica.rect.height)
    tx=(width-replica.rect.width*target_scale)/2;ty=(height-replica.rect.height*target_scale)/2
    def box(rect,scale,x,y):return (rect.x0*scale+x,rect.y0*scale+y,rect.x1*scale+x,rect.y1*scale+y)
    candidates={}
    for drawing in replica.get_drawings():
        bounds=box(drawing['rect'],target_scale,tx,ty);key=(round((bounds[0]+bounds[2])/40),round((bounds[1]+bounds[3])/40))
        candidates.setdefault(key,[]).append(bounds)
    total=matched=0;deltas=[];unmatched=[]
    for drawing in original.get_drawings():
        bounds=box(drawing['rect'],source_scale,ox,oy);x0,y0,x1,y1=bounds
        if x1<0 or y1<0 or x0>=width or y0>=height:continue
        if x1-x0<2 and y1-y0<2:continue
        # Ignore native text areas. Large panels are retained even when text lies inside.
        sample=mask.crop((max(0,int(x0)),max(0,int(y0)),min(width,max(int(x0)+1,int(x1)+1)),min(height,max(int(y0)+1,int(y1)+1))))
        if sample.width and sample.height and sample.resize((1,1)).getpixel((0,0))<70:continue
        total+=1;key=(round((x0+x1)/40),round((y0+y1)/40));near=[b for dx in (-1,0,1) for dy in (-1,0,1) for b in candidates.get((key[0]+dx,key[1]+dy),[])]
        delta=min((max(abs(a-z) for a,z in zip(bounds,b)) for b in near),default=float('inf'))
        if delta<=5:matched+=1;deltas.append(round(delta,3))
        elif len(unmatched)<40:unmatched.append([round(v,2) for v in bounds])
    return {'source_components':total,'matched':matched,'maximum_matched_delta_px':max(deltas,default=None),'unmatched_examples':unmatched,'interpretation':'Unmatched boxes can reflect grouped paths, source changes or geometry errors; inspect the overlay. Raster originals require separate component review.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--deck');selection.add_argument('--all',action='store_true')
    parser.add_argument('--pages',type=int,nargs='+',help='Refresh only these pages of an existing deck comparison; keep other comparison pages cached.')
    parser.add_argument('--originals',type=Path,default=ROOT/'design-references/figma/official-decks/pdfs')
    args=parser.parse_args(argv)
    if args.pages and not args.deck:parser.error('--pages requires --deck.')
    try:
        import pymupdf as fitz
        from PIL import Image,ImageChops,ImageDraw,ImageOps,ImageStat
    except ImportError:
        parser.error('Comparison maintenance requires PyMuPDF and Pillow; ordinary builds do not.')
    data=json.loads((ROOT/'library/index.json').read_text());folder=ROOT/'design-references/figma/official-decks/review';folder.mkdir(parents=True,exist_ok=True)
    selected=[args.deck] if args.deck else [source['id'] for source in data['sources']]
    if any(name not in data['decks'] and name not in data.get('aliases',{}) for name in selected):parser.error('Unknown lesson ID.')
    reports=json.loads((folder/'report.json').read_text()) if (folder/'report.json').exists() else {};links=[]
    for name in selected:
        canonical=data.get('aliases',{}).get(name,name);deck=data['decks'][canonical];source=next(s for s in data['sources'] if s['id']==name);original=args.originals/Path(source['path']).name
        if not original.exists():parser.error('Missing pinned original: '+str(original)+'. Run scripts/library.py fetch explicitly.')
        if hashlib.sha256(original.read_bytes()).hexdigest()!=source['sha256']:parser.error('Original PDF checksum mismatch: '+name)
        pdf=ROOT/'build/library/decks'/canonical/'main.pdf'
        if not pdf.exists():parser.error('Build the lesson first: scripts/library.py build --deck '+name)
        target=folder/name;target.mkdir(exist_ok=True);items=[];geometry=[];comparison=fitz.open()
        snapshot=target/'replica-snapshot.pdf';shutil.copyfile(pdf,snapshot);pdf=snapshot
        existing_comparison=fitz.open(target/'comparisons.pdf') if args.pages and (target/'comparisons.pdf').exists() else None
        if args.pages and any(n<1 or n>len(deck['slides']) for n in args.pages):parser.error('Page selection is outside this lesson.')
        previous=json.loads((target/'geometry.json').read_text()) if (target/'geometry.json').exists() else []
        with fitz.open(original) as source_pdf,fitz.open(pdf) as replica:
            if len(source_pdf)!=len(replica):parser.error('Source/replica page counts differ: '+name)
            for number,sid in enumerate(deck['slides']):
                slide=data['slides'][sid];layout=data['layouts'][slide['layout']];images=[]
                cached=bool(args.pages and number+1 not in args.pages)
                if cached:
                    base=f'{number+1:03d}'
                    if number>=len(previous) or not all((target/(base+'-'+label+'.png')).exists() for label in ('original','replica','overlay','graphics-difference')):
                        parser.error('A partial refresh requires an existing complete comparison. Run without --pages first.')
                    entry=dict(previous[number]);entry['cached_from_previous_comparison']=True;geometry.append(entry);measured=entry['anchors']
                else:
                    for document in (source_pdf,replica):
                        page=document[number];pix=page.get_pixmap(matrix=fitz.Matrix(2000/page.rect.height,2000/page.rect.height),alpha=False)
                        image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                        image=ImageOps.contain(image,(3556,2000));canvas=Image.new('RGB',(3556,2000),image.getpixel((0,0)));canvas.paste(image,((3556-image.width)//2,(2000-image.height)//2));images.append(canvas)
                    base=f'{number+1:03d}';a,b=images
                    unchanged=all((target/(base+'-'+label+'.png')).exists() and ImageChops.difference(image,Image.open(target/(base+'-'+label+'.png')).convert('RGB')).getbbox() is None for label,image in zip(('original','replica'),images))
                    if not unchanged:
                        a.save(target/(base+'-original.png'),compress_level=2);b.save(target/(base+'-replica.png'),compress_level=2)
                    if not unchanged or not (target/(base+'-overlay.png')).exists():Image.blend(a,b,.5).save(target/(base+'-overlay.png'),compress_level=2)
                    mask=Image.new('L',a.size,255);draw=ImageDraw.Draw(mask);w,h=layout['canvas'];scale=min(3556/w,2000/h);ox=(3556-w*scale)/2;oy=(2000-h*scale)/2
                    for field in layout.get('fields',[]):
                        if field['type']!='text':continue
                        if 'box' in field:x,y,width,height=field['box'];size=field.get('font_size',0);points=[(x,y),(x+width,y),(x+width,y+height),(x,y+height)]
                        else:
                            x,y=field['origin'];width=field['width'];size=field['font_size'];height=field['height'];angle=math.radians(-field.get('rotation',0));points=[]
                            for px,py in [(0,-size),(width,-size),(width,height),(0,height)]:points.append((x+px*math.cos(angle)-py*math.sin(angle),y+px*math.sin(angle)+py*math.cos(angle)))
                        points=[(ox+px*scale,oy+py*scale) for px,py in points];xs=[p[0] for p in points];ys=[p[1] for p in points];draw.rectangle((min(xs)-12,min(ys)-12,max(xs)+12,max(ys)+12),fill=0)
                    difference=ImageChops.difference(a,b);difference=Image.composite(difference,Image.new('RGB',a.size),mask);
                    if not unchanged or not (target/(base+'-graphics-difference.png')).exists():difference.save(target/(base+'-graphics-difference.png'),compress_level=2)
                    # Separate appearance residual from geometric evidence; never call it approval.
                    mean=sum(ImageStat.Stat(difference).mean)/3
                    bounds=[]
                    for image in images:
                        paper=Image.new('RGB',image.size,image.getpixel((0,0)));foreground=ImageChops.difference(image,paper).convert('L').point(lambda n:255 if n>24 else 0);foreground=ImageChops.multiply(foreground,mask);bounds.append(foreground.getbbox())
                    delta=max(abs(x-y) for x,y in zip(*bounds)) if all(bounds) else None
                    measured=previous[number]['anchors'] if unchanged and number<len(previous) else measure_anchors(source_pdf[number],replica[number],mask,layout,3556,2000)
                    geometry.append({'anchors':measured,'page':number+1,'slide':sid,'canvas_foreground_bbox_delta_px':delta,'graphics_mean_absolute_residual':round(mean,4),'within_5px_for_this_metric':delta is not None and delta<=5,'component_anchor_review':'pending; whole-canvas bounds do not certify every component'})
                cp=comparison.new_page(width=1190,height=370)
                if cached and existing_comparison is not None:
                    cp.show_pdf_page(cp.rect,existing_comparison,number)
                else:
                    cp.insert_text((20,20),f'{name} / {number+1:03d} / {sid}',fontsize=10);cp.show_pdf_page(fitz.Rect(10,35,590,362),source_pdf,number);cp.show_pdf_page(fitz.Rect(600,35,1180,362),replica,number)
        if existing_comparison is not None:existing_comparison.close()
        prepared=target/'comparisons.tmp.pdf';comparison.save(prepared,garbage=4,deflate=True);comparison.close();prepared.replace(target/'comparisons.pdf')
        (target/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
        from slide_guide import redirect_page
        import os
        destination=os.path.relpath(ROOT/'docs/slides/index.html',target)+'?view=decks&item='+canonical+'&maintenance=1'
        (target/'index.html').write_text(redirect_page(destination),encoding='utf-8')
        reports[name]=geometry
        (folder/'report.json').write_text(json.dumps(reports,indent=2)+'\n')
        print('Compared',name,len(geometry),'pages',flush=True)
    (folder/'report.json').write_text(json.dumps(reports,indent=2)+'\n')
    from guide_comparisons import sync
    sync(ROOT)
    print('Comparison data ready for:',ROOT/'docs/slides/index.html')
    return 0


if __name__=='__main__':raise SystemExit(main())
