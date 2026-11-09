"""Prepare optional local comparisons for the unified guide, without another gallery."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def sync(root=ROOT):
    from slide_guide import redirect_page,lesson_assets
    core=json.loads((root/'templates/index.json').read_text(encoding="utf-8"))['templates']
    lessons=json.loads((root/'library/index.json').read_text(encoding="utf-8")) if (root/'library/index.json').exists() else None
    records={};folder=root/'design-references/figma/collection-review'
    def url(path):return '../../'+path.relative_to(root).as_posix()
    for entry in core:
        variants=[]
        for number,ref in enumerate(entry['references']):
            original=folder/(ref+'.png')
            if not original.exists():continue
            target=root/'build/checks/slide-guide/comparisons'/entry['id']
            overlay=target/'overlay.webp';difference=target/'difference.webp'
            variants.append({'label':ref,'original':url(original),'overlay':url(overlay) if number==0 and overlay.exists() else None,'difference':url(difference) if number==0 and difference.exists() else None,
              'note':'Original SVG composition. Inter and English text are deliberate adaptations. Component geometry, type and effects need separate review.'})
        external=entry.get('external_reference',{})
        external_preview=folder/(entry['id']+'-external-original.png')
        if external.get('name') and external_preview.is_file():
            variants.insert(0,{'label':external['name'],'original':url(external_preview),
                'overlay':None,'difference':None,
                'note':'Supplied PDF reference for the current composition. Inter and editable defaults are intentional adaptations.'})
        if variants:records[entry['id']]={'variants':variants}
    if lessons:
        mapping=lesson_assets(lessons)
        for source in lessons['sources']:
            base=root/'design-references/figma/official-decks/review'/source['id']
            for page in source['pages']:
                sid=page['slide'];prefix=f"{page['page']:03d}";original=base/(prefix+'-original.png')
                if not original.exists():continue
                overlay=base/(prefix+'-overlay.png');difference=base/(prefix+'-graphics-difference.png')
                value={'label':source['id']+' / '+str(page['page']),'original':url(original),'overlay':url(overlay) if overlay.exists() else None,'difference':url(difference) if difference.exists() else None,
                 'note':'Pinned official PDF page. English translation and Inter are intentional. Metrics do not certify every anchor or approve a slide.'}
                keys={sid,mapping[sid]}
                layout=lessons['layouts'].get(lessons['slides'][sid]['layout'],{})
                if layout.get('registration') and layout.get('example_slide')==sid:
                    keys.add(lessons['slides'][sid]['layout'])
                for key in keys:records.setdefault(key,{'variants':[]})['variants'].append(value)
    out=root/'build/checks/slide-guide';out.mkdir(parents=True,exist_ok=True)
    (out/'comparisons.js').write_text('window.BITBEAMER_COMPARISONS='+json.dumps({'records':records},separators=(',',':'))+';\n',encoding='utf-8')
    # Existing bookmarks keep working; there is only one maintained visual interface.
    for path in [folder/'index.html',folder/'all.html']:
        if path.parent.exists():path.write_text(redirect_page(os.path.relpath(root/'docs/slides/index.html',path.parent)+'?collection=studio&maintenance=1'),encoding='utf-8')
    inventory=root/'design-references/figma/review.html'
    if inventory.exists():inventory.write_text(redirect_page('../../docs/slides/index.html?collection=studio&maintenance=1'),encoding='utf-8')
    official=root/'design-references/figma/official-decks/review'
    if official.exists():
        for path in official.rglob('*.html'):
            name=path.parent.name
            target=os.path.relpath(root/'docs/slides/index.html',path.parent)+'?view=decks&maintenance=1'
            if path.parent!=official:target+='&item='+name
            path.write_text(redirect_page(target),encoding='utf-8')
    return len(records)


def prepare(root=ROOT,names=None):
    from PIL import Image,ImageChops,ImageDraw,ImageOps,ImageStat
    from studio_preview import thumbnail
    from guide_previews import clean_document,context,signature
    from asset_library import write_if_changed
    import build
    entries=json.loads((root/'templates/index.json').read_text(encoding="utf-8"))['templates']
    by_id={e['id']:e for e in entries}
    if names is None:names=list(by_id)
    unknown=set(names)-by_id.keys()
    if unknown:raise ValueError('Unknown core comparison ID: '+', '.join(sorted(unknown)))
    # Current neutral public commands also provide the source for each comparison.
    from slide_guide import catalogue
    commands={c['id']:c['command'] for r in catalogue(root)['rows'] for c in r['choices']}
    cached={};report=root/'build/checks/slide-guide/hd-report.json'
    if report.exists():
        for batch in json.loads(report.read_text(encoding="utf-8")).get('batches',[]):
            for page,name in enumerate(batch['commands'],1):cached[name]=(root/batch['pdf'],page)
    ctx=context(root);records=[]
    for name in names:
        entry=by_id[name]
        external=root/'design-references/figma/collection-review'/(name+'-external-original.png')
        if entry.get('external_reference') and external.exists():
            original=external;reference_id=entry['external_reference']['name']
        elif entry['references']:
            reference_id=entry['references'][0]
            original=root/'design-references/figma/collection-review'/(reference_id+'.png')
        else:continue
        if not original.exists():continue
        output=root/'build/checks/slide-guide/comparisons'/name;output.mkdir(parents=True,exist_ok=True)
        pdf,page=cached.get(name,(None,None))
        if pdf is None or not pdf.exists() or commands[name] not in pdf.with_suffix('.tex').read_text(encoding='utf-8'):
            document=output/'main.tex';write_if_changed(document,clean_document([commands[name]]).encode())
            with (output/'launcher.log').open('w', encoding='utf-8') as log:
                result=subprocess.run([sys.executable,str(root/'scripts/build.py'),str(document),str(output)],cwd=root,stdout=log,stderr=subprocess.STDOUT)
            if result.returncode:raise RuntimeError('Comparison compilation failed: '+str(output/'launcher.log'))
            pdf=output/'main.pdf';page=1
        with tempfile.TemporaryDirectory(prefix='comparison-',dir=output) as temporary:
            target=Path(temporary)/'replica.png';thumbnail(root,pdf,target,page=page,width=3556)
            with Image.open(target) as source:replica=ImageOps.pad(source.convert('RGB'),(3556,2000),color=source.getpixel((0,0)))
            with Image.open(original) as source:reference=ImageOps.pad(source.convert('RGB'),(3556,2000),color=source.getpixel((0,0)))
        Image.blend(reference,replica,.5).save(output/'overlay.webp','WEBP',lossless=True,method=4)
        mask=Image.new('L',replica.size,255);draw=ImageDraw.Draw(mask);w,h=entry['canvas'];scale=min(3556/w,2000/h);ox=(3556-w*scale)/2;oy=(2000-h*scale)/2
        for field in entry['fields']:
            if field['type']=='text' and field.get('box'):
                x,y,width,height=field['box'];draw.rectangle((ox+x*scale-12,oy+y*scale-12,ox+(x+width)*scale+12,oy+(y+height)*scale+12),fill=0)
        difference=Image.composite(ImageChops.difference(reference,replica),Image.new('RGB',replica.size),mask)
        difference.save(output/'difference.webp','WEBP',lossless=True,method=4)
        report={'id':name,'reference':reference_id,'signature':signature(root,name,ctx),'height_px':2000,'graphic_mean_absolute_residual':sum(ImageStat.Stat(difference).mean)/3,
                'geometry':'Source coordinates retained; pixel residual is not a 5 px anchor certificate.','approval':'in review','type':'Inter and English text intentionally differ'}
        (output/'measurements.json').write_text(json.dumps(report,indent=2)+'\n', encoding="utf-8");records.append(report)
        print('Compared:',name,flush=True)
    sync(root);return records


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('sync','prepare'),default='sync',nargs='?');parser.add_argument('--templates',nargs='+')
    args=parser.parse_args(argv)
    try:
        print('Compared compositions: '+str(len(prepare(ROOT,args.templates))) if args.action=='prepare' else 'Local comparison entries: '+str(sync(ROOT)));return 0
    except (ValueError,OSError,RuntimeError) as error:print('Comparison preparation failed:',error,file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
