"""Prepare clean 640/1600 px lossless guide previews from compiled slide commands."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
VERSION=1


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(root):
    path=root/'docs/slides/previews/manifest.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'schema':VERSION,'previews':{}}


def save(root,data):
    """Merge independent preview updates under a portable inter-process lock."""
    import time
    path=root/'docs/slides/previews/manifest.json';path.parent.mkdir(parents=True,exist_ok=True)
    lock=path.with_suffix('.lock');deadline=time.monotonic()+60
    while True:
        try:
            descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(descriptor);break
        except FileExistsError:
            if time.monotonic()>deadline:raise RuntimeError('Guide preview registry is locked by another maintenance build.')
            time.sleep(.05)
    temporary=None
    try:
        merged=manifest(root);merged['previews'].update(data['previews'])
        raw=(json.dumps(merged,indent=2,sort_keys=True)+'\n').encode()
        if not path.exists() or path.read_bytes()!=raw:
            with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.tmp',delete=False) as handle:
                handle.write(raw);temporary=Path(handle.name)
            temporary.chmod(0o644);temporary.replace(path)
    finally:
        if temporary:temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def context(root):
    from studio_templates import inspect_templates
    from studio_preview import input_sets
    from slide_guide import catalogue
    entries=inspect_templates(root)
    core=input_sets(root,entries)
    path=root/'library/index.json';lessons=json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    choices={c['id']:c for row in catalogue(root)['rows'] for c in row['choices']}
    if lessons:
        from slide_guide import lesson_assets,lesson_command
        for sid,key in lesson_assets(lessons).items():
            if key not in choices:choices[key]={'command':lesson_command(root,lessons['slides'][sid]),'library_slide':sid}
    return {'core':core,'lessons':lessons,'choices':choices}


def signature(root,name,ctx):
    choice=ctx['choices'][name]
    if name in ctx['core']:inputs=ctx['core'][name]
    else:
        from library import fingerprint
        data=ctx['lessons'];preset=data.get('presets',{}).get(name)
        sid=choice.get('library_slide') or (preset['slide'] if preset else data['layouts'][name]['example_slide'])
        inputs=fingerprint(root,[sid],data)
    return hashlib.sha256(json.dumps({'version':VERSION,'inputs':inputs,'command':choice['command']},sort_keys=True).encode()).hexdigest()


def current(root,name,expected,records=None):
    record=(records or manifest(root))['previews'].get(name,{})
    if record.get('signature')!=expected:return False
    return all((root/value['file']).is_file() and sha(root/value['file'])==value['sha256'] for value in record.get('images',{}).values()) and set(record.get('images',{}))=={'thumb','hd'}


def record(root,name,pdf,page,expected,backend='docker',image='bitbeamer-latex:local'):
    from PIL import Image
    from studio_preview import thumbnail
    output=root/'docs/slides/previews';output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='guide-render-',dir=output) as temporary:
        rendered=Path(temporary)/'native.png';thumbnail(root,pdf,rendered,backend,image,page,width=1600)
        with Image.open(rendered) as source:
            source=source.convert('RGB');source.thumbnail((1600,900),Image.Resampling.LANCZOS)
            canvas=Image.new('RGB',(1600,900),source.getpixel((0,0)))
            canvas.paste(source,((1600-source.width)//2,(900-source.height)//2))
        images={}
        for kind,width in [('thumb',640),('hd',1600)]:
            target=output/('hd' if kind=='hd' else '')/(name+'.webp');target.parent.mkdir(parents=True,exist_ok=True)
            frame=canvas if width==1600 else canvas.resize((640,360),Image.Resampling.LANCZOS)
            prepared=Path(temporary)/(kind+'.webp');frame.save(prepared,'WEBP',lossless=True,method=4)
            prepared.replace(target)
            images[kind]={'file':target.relative_to(root).as_posix(),'sha256':sha(target),'width':width,'height':width*9//16,'lossless':True}
        # Keep existing field-guide PNG paths compatible; they now have a clean canvas too.
        if name in {p.stem for p in (root/'templates/studio').glob('*.tex')}:
            legacy=root/'docs/templates/previews'/(name+'.png');legacy.parent.mkdir(parents=True,exist_ok=True)
            canvas.resize((480,270),Image.Resampling.LANCZOS).save(legacy,'PNG',optimize=True)
        return {'signature':expected,'images':images,'canvas':'complete slide; no catalogue labels','render_source':'pdf','page':page}


def refresh(root,name,pdf,page=1,backend='docker',image='bitbeamer-latex:local',ctx=None,update_guide=True):
    if not (root/'docs/slides/guide.js').is_file():return
    ctx=ctx or context(root)
    if name not in ctx['choices']:return
    expected=signature(root,name,ctx);data=manifest(root)
    if not current(root,name,expected,data):
        save(root,{'previews':{name:record(root,name,pdf,page,expected,backend,image)}})
        from slide_guide import sync
        if update_guide:sync(root)
        if (root/'build/checks/slide-guide/comparisons'/name).is_dir():
            from guide_comparisons import prepare as compare
            compare(root,[name])


def clean_document(commands):
    return '\n'.join([r'\documentclass[aspectratio=169]{beamer}',r'\usetheme{bitpolito-studio}',r'\usepackage{bitpolitostudiotemplates}',r'\usepackage{bitpolitostudiolibrary}',r'\usepackage[backend=biber]{biblatex}',r'\addbibresource{bibliography.bib}',r'\addbibresource{library/references.bib}',r'\begin{document}',*commands,r'\end{document}',''])


def prepare(root=ROOT,names=None,backend='docker',image='bitbeamer-latex:local',jobs=2):
    import build
    from asset_library import write_if_changed
    from deck import log_issues,pdf_tool
    ctx=context(root);data=manifest(root);requested=list(ctx['choices']) if names is None else names
    unknown=set(requested)-ctx['choices'].keys()
    if unknown:raise ValueError('Unknown guide composition: '+', '.join(sorted(unknown)))
    expected={name:signature(root,name,ctx) for name in requested}
    pending=[name for name in requested if not current(root,name,expected[name],data)]
    folder=root/'build/checks/slide-guide/commands';folder.mkdir(parents=True,exist_ok=True)
    chunks=[pending[i:i+24] for i in range(0,len(pending),24)]
    print('Guide commands needing compilation:',len(pending),'/',len(requested),flush=True)
    def run(chunk):
        identity=hashlib.sha256('\n'.join(chunk).encode()).hexdigest()[:16];output=folder/identity;output.mkdir(exist_ok=True)
        source=output/'main.tex';write_if_changed(source,clean_document([ctx['choices'][name]['command'] for name in chunk]).encode())
        with (output/'launcher.log').open('w', encoding='utf-8') as log:
            command=[sys.executable,str(root/'scripts/build.py'),str(source),str(output),'--backend',backend,'--image',image]
            result=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('Guide command batch failed: '+str(output/'launcher.log'))
        issues=log_issues((output/'main.log').read_text(encoding='utf-8',errors='replace'))
        if issues:raise RuntimeError('Guide command diagnostics: '+str(issues[:3])+' in '+str(output))
        pdf=output/'main.pdf';info=pdf_tool(root,'pdfinfo',pdf,backend,image)
        if int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1])!=len(chunk):raise RuntimeError('Guide command page count differs.')
        fonts=pdf_tool(root,'pdffonts',pdf,backend,image)
        if any(re.search(r'\sno\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',row) for row in fonts.splitlines()[2:]):raise RuntimeError('Unembedded guide font: '+str(pdf))
        results={name:record(root,name,pdf,page,expected[name],backend,image) for page,name in enumerate(chunk,1)}
        return results,{'pdf':pdf.relative_to(root).as_posix(),'commands':chunk,'status':'passed','font_embedding':'checked','diagnostics':[]}
    previous=folder.parent/'hd-report.json'
    reports=json.loads(previous.read_text(encoding="utf-8")).get('batches',[]) if previous.exists() else []
    completed=0;errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures=[pool.submit(run,chunk) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            try:records,report=future.result()
            except (ValueError,RuntimeError,OSError) as error:
                errors.append(str(error));print('Guide batch failed:',error,flush=True);continue
            data['previews'].update(records);save(root,{'previews':records});reports.append(report);completed+=len(records)
            print('Prepared guide previews:',completed,'/',len(pending),flush=True)
    # PNG compatibility manifests refer to the same clean rendered defaults.
    from studio_preview import digest,load_manifest,save_manifest
    legacy=load_manifest(root)
    for name,values in ctx['core'].items():
        path=root/'docs/templates/previews'/(name+'.png')
        if name in data['previews']:
            legacy.setdefault('models',{})[name]=values;legacy.setdefault('previews',{})[name]=digest(path)
    save_manifest(root,legacy)
    from slide_guide import sync
    sync(root)
    (folder.parent/'hd-report.json').write_text(json.dumps({'batches':reports},indent=2)+'\n', encoding="utf-8")
    existing=[name for name in pending if (root/'build/checks/slide-guide/comparisons'/name).is_dir()]
    if existing and not errors:
        from guide_comparisons import prepare as compare
        try:compare(root,existing)
        except (ValueError,RuntimeError,OSError) as error:errors.append(str(error))
    report={'status':'failed' if errors else 'passed','errors':errors,'requested':len(requested),'prepared':len(pending),'reused':len(requested)-len(pending),'batches':reports,'approval':'in review'}
    (root/'build/checks/slide-guide/hd-report.json').write_text(json.dumps(report,indent=2)+'\n', encoding="utf-8")
    if errors:raise RuntimeError('Guide command failures; inspect build/checks/slide-guide/hd-report.json')
    return report


def webp_size(content):
    """Read dimensions from the lossless VP8L chunk without converter dependencies."""
    if content[:4]!=b'RIFF' or content[8:12]!=b'WEBP':raise ValueError('Invalid WebP container')
    position=12
    while position+8<=len(content):
        kind=content[position:position+4];length=int.from_bytes(content[position+4:position+8],'little');start=position+8
        if start+length>len(content):raise ValueError('Truncated WebP chunk')
        if kind==b'VP8L':
            if length<5 or content[start]!=0x2f:raise ValueError('Invalid VP8L image')
            bits=int.from_bytes(content[start+1:start+5],'little')
            return (bits&0x3fff)+1,((bits>>14)&0x3fff)+1
        position=start+length+(length%2)
    raise ValueError('Lossless VP8L image is required')


def check(root=ROOT):
    ctx=context(root);data=manifest(root)
    if data.get('schema')!=VERSION or set(data['previews'])!=set(ctx['choices']):raise ValueError('Guide HD coverage differs; run scripts/guide_previews.py prepare.')
    for name in ctx['choices']:
        if not current(root,name,signature(root,name,ctx),data):raise ValueError('Stale or missing HD guide preview: '+name)
        for kind,width in [('thumb',640),('hd',1600)]:
            value=data['previews'][name]['images'][kind];content=(root/value['file']).read_bytes()
            if value['width']!=width or value['height']!=width*9//16 or not value.get('lossless') or content[:4]!=b'RIFF' or content[8:12]!=b'WEBP' or webp_size(content)!=(width,width*9//16):raise ValueError('Invalid lossless guide image: '+name)
    return len(ctx['choices'])


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','check'))
    parser.add_argument('--templates',nargs='+');parser.add_argument('--backend',choices=('docker','native'),default='docker')
    parser.add_argument('--image',default=os.environ.get('LATEX_IMAGE','bitbeamer-latex:local'));parser.add_argument('--jobs',type=int,choices=range(1,5),default=2)
    args=parser.parse_args(argv)
    try:
        result=prepare(ROOT,args.templates,args.backend,args.image,args.jobs) if args.action=='prepare' else {'checked':check(ROOT)}
        print(json.dumps({k:v for k,v in result.items() if k!='batches'}));return 0
    except (ValueError,RuntimeError,OSError,subprocess.CalledProcessError) as error:print('Guide preview failed:',error,file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
