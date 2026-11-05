"""Maintain and render the official lesson collection; authoring uses deck.py."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

import build
from asset_library import write_if_changed
from lesson_library import (load, validate, safe_file, source_dependencies,
                            core_dependencies, slide_dependencies, validate_binding)
from studio_preview import thumbnail

ROOT = Path(__file__).resolve().parents[1]


def document(root, slide_ids, data, diagnostic=False):
    references = sorted({key for s in slide_ids for key in data['slides'][s].get('references', [])})
    lines = [r'\documentclass[aspectratio=169]{beamer}', r'\usetheme{bitpolito-studio}',
             r'\usepackage{bitpolitostudiolibrary}', r'\usepackage[backend=biber,style=numeric]{biblatex}']
    if references:
        lines.append(r'\addbibresource{library/references.bib}')
    if diagnostic:lines.append(r'\studioreviewdiagnosticstrue')
    lines += [r'\begin{document}']
    lines += [r'\input{' + data['slides'][s]['source'] + '}' for s in slide_ids]
    lines += [r'\end{document}', '']
    return '\n'.join(lines)


def fingerprint(root, slide_ids, data):
    digest = hashlib.sha256()
    for path in sorted(root.glob('*.sty')):
        digest.update(path.name.encode());digest.update(path.read_bytes())
    for sid in slide_ids:
        slide=data['slides'][sid]
        inputs=[slide['source'],*slide.get('resources',{})]
        if slide.get('core_reuse'):
            digest.update(json.dumps(core_dependencies(root,slide),sort_keys=True).encode())
        inputs += sorted(source_dependencies(root,slide) - set(inputs))
        for name in inputs:
            digest.update(name.encode());digest.update((root/name).read_bytes())
        digest.update(json.dumps({key:slide[key] for key in ('layout','fields','references') if key in slide},sort_keys=True).encode())
    references={key for sid in slide_ids for key in data['slides'][sid].get('references',[])}
    for key in sorted(references):digest.update((root/data['references'][key]['source']).read_bytes())
    return digest.hexdigest()


def render(root, kind, name, backend='docker', image='bitbeamer-latex:local', previews=False, diagnostic=False):
    data=load(root)
    if name not in data[kind]:raise ValueError('Unknown '+kind[:-1]+': '+name)
    item=data[kind][name];slide_ids=item['slides']
    for sid in slide_ids:validate_binding(root,data,sid)
    output=root/'build/library'/kind/name
    output.mkdir(parents=True,exist_ok=True)
    source=output/'main.tex';write_if_changed(source,document(root,slide_ids,data,diagnostic).encode())
    signature=hashlib.sha256((fingerprint(root,slide_ids,data)+str(diagnostic)).encode()).hexdigest()
    manifest=output/'build.json'
    current=json.loads(manifest.read_text()) if manifest.exists() else {}
    if current.get('fingerprint')!=signature or not (output/'main.pdf').is_file():
        if build.main([str(source),str(output),'--backend',backend,'--image',image],root=root):
            (output/'check.json').write_text(json.dumps({'status':'failed','errors':[{'kind':'compilation','message':'Compilation failed; any previous PDF is stale.'}],'backend':backend},indent=2)+'\n')
            raise RuntimeError('Library compilation failed: '+name)
    from deck import log_issues, pdf_tool
    errors=log_issues((output/'main.log').read_text(encoding='utf-8',errors='replace'))
    if errors and not diagnostic:
        (output/'check.json').write_text(json.dumps({'status':'failed','errors':errors},indent=2)+'\n')
        raise RuntimeError('Library diagnostics in '+name+': '+str(errors[:5]))
    info=pdf_tool(root,'pdfinfo',output/'main.pdf',backend,image)
    import re
    count=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1])
    if count!=len(slide_ids):raise RuntimeError('Incorrect page count: '+name)
    fonts=pdf_tool(root,'pdffonts',output/'main.pdf',backend,image)
    for row in fonts.splitlines()[2:]:
        if re.search(r'\sno\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',row):errors.append({'kind':'font embedding','message':row.strip()})
    preview_records={}
    text=pdf_tool(root,'pdftotext',output/'main.pdf',backend,image)
    expects_text=any(f['type']=='text' for sid in slide_ids for f in data['layouts'][data['slides'][sid]['layout']]['fields'])
    if expects_text and not text.strip():errors.append({'kind':'text selection','message':'No selectable native text found.'})
    if previews:
        from guide_previews import context as guide_context
        guide_ctx=guide_context(root) if (root/'docs/slides/guide.js').is_file() else None
        for number,sid in enumerate(slide_ids,1):
            target=root/'library/previews'/(sid+'.png')
            slide_signature=fingerprint(root,[sid],data)
            old_preview=preview_manifest(root).get(sid,{})
            if not target.exists() or old_preview.get('fingerprint')!=slide_signature:
                thumbnail(root,output/'main.pdf',target,backend,image,number)
            from guide_previews import refresh
            from slide_guide import lesson_assets
            refresh(root,lesson_assets(data)[sid],output/'main.pdf',number,backend,image,ctx=guide_ctx,update_guide=False)
            preview_records[sid]={'fingerprint':slide_signature,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
        save_preview_records(root,preview_records)
    report={'status':'failed' if errors else 'passed','errors':errors,'pages':count,'fingerprint':signature,'backend':backend,'font_embedding':'checked','selectable_text':'checked' if expects_text else 'artwork-only composition',
            'visual_review':'in review; rendering does not approve a slide'}
    manifest.write_text(json.dumps(report,indent=2)+'\n')
    (output/'check.json').write_text(json.dumps(report,indent=2)+'\n')
    if errors and not diagnostic:raise RuntimeError('PDF inspection failed: '+name)
    print('Library PDF:',output/'main.pdf',flush=True)
    return output/'main.pdf'


def preview_manifest(root):
    path=root/'library/previews/manifest.json'
    return json.loads(path.read_text()).get('slides',{}) if path.exists() else {}


def save_preview_records(root,records):
    import time
    path=root/'library/previews/manifest.json';lock=path.with_suffix('.lock')
    deadline=time.monotonic()+30
    while True:
        try:
            descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(descriptor);break
        except FileExistsError:
            if time.monotonic()>deadline:raise RuntimeError('Preview registry is locked; finish the other library build before retrying.')
            time.sleep(.1)
    try:
        merged=preview_manifest(root);merged.update(records);temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'schema':1,'slides':merged},indent=2)+'\n');temporary.replace(path)
        from slide_guide import refresh_if_present
        refresh_if_present(root)
    finally:lock.unlink(missing_ok=True)


def check_previews(root=ROOT):
    data=load(root);records=preview_manifest(root)
    for sid in data['slides']:
        record=records.get(sid,{});path=root/'library/previews'/(sid+'.png')
        if not path.exists() or record.get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest() or record.get('fingerprint')!=fingerprint(root,[sid],data):
            raise ValueError('Stale lesson preview: '+sid+'. Rebuild its lesson with --preview.')


def generated(root):
    data=load(root)
    lines=['<!-- Generated by scripts/library.py sync; edit library/index.json. -->','# Ready-to-use Studio lessons','',
           'All reconstructions remain **in review**. Copy a whole presentation or a topic block into a private project.',
           'Read [the library guide](README.md) and open [the unified slide guide](../docs/slides/index.html?view=decks).','',
           '| Presentation | Slides | Audience | Copy |','| --- | --- | --- | --- |']
    for name,d in data['decks'].items():lines.append('| '+d['title']+' | '+str(len(d['slides']))+' | '+d['audience']+' | `deck.py new my-talk --from '+name+'` |')
    lines+=['','## Topic blocks','','| Block | Slides | Prerequisites | Copy |','| --- | --- | --- | --- |']
    for name,b in data['blocks'].items():lines.append('| '+b['title']+' | '+str(len(b['slides']))+' | '+(', '.join(b.get('prerequisites',[])) or 'None')+' | `deck.py add my-talk --block '+name+'` |')
    inventory=['<!-- Generated by scripts/library.py sync; edit library/index.json. -->','# Source-page coverage','',
               'Every upstream page has a destination. Mappings document reconstruction coverage, not visual approval.','',
               '| Source | Page | Editable slide | Disposition |','| --- | --- | --- | --- |']
    for source in data['sources']:
        for page in source['pages']:
            inventory.append('| '+source['path']+' | '+str(page['page'])+' | ['+page['slide']+']('+data['slides'][page['slide']]['source'].replace('library/','',1)+') | '+page['disposition']+' |')
    outputs={root/'library/CATALOGUE.md':('\n'.join(lines)+'\n').encode(),root/'library/COVERAGE.md':('\n'.join(inventory)+'\n').encode()}
    registry=[r'\DeclareStudioLibraryLayout{'+name+'}{'+layout['source']+'}' for name,layout in data['layouts'].items() if not layout.get('registration')]
    fixed=['<!-- Generated by scripts/library.py sync; edit library/index.json. -->','# Fixed-content slides','',
           'Load `bitpolitostudiolibrary` after the Studio theme. These ready-made slides accept no options. Their existing rendering is retained; editable source layouts remain available for maintenance.','',
           '| Slide | Command | Lesson source |','| --- | --- | --- |']
    for name,preset in data.get('presets',{}).items():
        slide=data['slides'][preset['slide']];layout=data['layouts'][slide['layout']]
        options=[key+'={'+value+'}' for key,value in slide['fields'].items()]
        if layout.get('registration'):options.insert(0,'palette='+layout['palette'])
        call=r'\studiotemplate'+('['+','.join(options)+']' if options else '')+'{'+slide['layout']+'}'
        code=('% Generated fixed-content preset; edit its lesson record and run scripts/library.py sync.\n'
              +r'\ifx\studiotemplateoptions\empty\else'+'\n'
              +r'\PackageError{bitpolitostudiolibrary}{Fixed-content slide '+name+r' accepts no options}{Use the editable source layout for a different composition.}'+'\n'
              +r'\fi'+'\n'+call+'\n')
        outputs[root/preset['source']]=code.encode()
        registry.append(r'\DeclareStudioLibraryLayout{'+name+'}{'+preset['source']+'}')
        fixed.append('| '+preset['title']+r' | `\studiotemplate{'+name+'}` | ['+preset['slide']+']('+slide['source'].replace('library/','',1)+') |')
    outputs[root/'library/layouts/registry.tex']=('\n'.join(registry)+'\n').encode()
    outputs[root/'library/FIXED.md']=('\n'.join(fixed)+'\n').encode()
    return outputs


def sync(root=ROOT,check=False):
    if not check:
        for path,content in generated(root).items():
            path.parent.mkdir(parents=True,exist_ok=True)
            write_if_changed(path,content)
        data=load(root);changed=False
        for slide in data['slides'].values():
            for name in sorted(source_dependencies(root,slide) - {slide['source']} - slide.get('resources',{}).keys()):
                slide.setdefault('resources',{})[name]=hashlib.sha256(safe_file(root,name).read_bytes()).hexdigest();changed=True
            for name,expected in list(slide.get('resources',{}).items()):
                if Path(name).suffix!='.tex':continue
                actual=hashlib.sha256((root/name).read_bytes()).hexdigest()
                if actual!=expected:slide['resources'][name]=actual;changed=True
        if changed:write_if_changed(root/'library/index.json',(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
    for path,content in generated(root).items():
        if check:
            if not path.exists() or path.read_bytes()!=content:raise ValueError('Stale library guide: '+str(path))
        else:write_if_changed(path,content)
    from slide_guide import refresh_if_present
    refresh_if_present(root,check=check)


def fetch(root=ROOT):
    data=load(root);folder=root/'design-references/figma/official-decks/pdfs';folder.mkdir(parents=True,exist_ok=True)
    for source in data['sources']:
        target=folder/Path(source['path']).name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==source['sha256']:continue
        with urllib.request.urlopen(source['url'],timeout=120) as response:content=response.read()
        if hashlib.sha256(content).hexdigest()!=source['sha256']:raise ValueError('Upstream PDF checksum mismatch: '+source['id'])
        write_if_changed(target,content)
    print('Pinned source PDFs:',folder)


def prepare_part(name):
    from asset_library import render_svg
    source=Path(name);target=source.with_suffix('.pdf');temporary=source.with_suffix('.preparing.pdf')
    try:render_svg(source,temporary,crop=False)
    except ValueError as error:
        # librsvg's ink bounds omit image-only compositions. Keep their full canvas.
        if 'no visible artwork' not in str(error) or not any(token in source.read_text() for token in ('<image','<ns0:image')):raise
        from asset_library import rsvg_modules
        cairo,Rsvg=rsvg_modules();handle=Rsvg.Handle.new_from_file(str(source.resolve()))
        _,width,height=handle.get_intrinsic_size_in_pixels()
        viewport=Rsvg.Rectangle();viewport.x=viewport.y=0;viewport.width=width;viewport.height=height
        with cairo.PDFSurface(str(temporary),width,height) as surface:
            surface.restrict_to_version(cairo.PDF_VERSION_1_5)
            handle.render_document(cairo.Context(surface),viewport)
    temporary.replace(target)
    return name


def prepare(root=ROOT, backend='docker', image='bitbeamer-latex:local'):
    """Prepare retained vector parts; never needs complete source PDF exports."""
    manifest_path=root/'library/parts/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    pending=[]
    for part in manifest['parts'].values():
        source=safe_file(root,part['source']);target=root/part['pdf']
        if source.suffix.lower()!='.svg' or target!=source.with_suffix('.pdf'):
            raise ValueError('Prepared part must use its retained SVG basename: '+part['source'])
        changed=hashlib.sha256(source.read_bytes()).hexdigest()!=part['source_sha256']
        for name,expected in part['dependencies'].items():
            changed=hashlib.sha256(safe_file(root,name).read_bytes()).hexdigest()!=expected or changed
        if changed or not target.exists() or part.get('pdf_sha256')!=hashlib.sha256(target.read_bytes()).hexdigest():
            pending.append(part['source'])
    if pending and backend=='docker':
        docker=build.docker_image(root,image)
        program="import sys;sys.path.insert(0,'scripts');from library import prepare;prepare(backend='native')"
        subprocess.run([docker,'run','--rm','--network','none',*(['--user',f'{os.getuid()}:{os.getgid()}'] if hasattr(os,'getuid') else []),'--mount',f'type=bind,source={root},target=/work','--workdir','/work','--entrypoint','python3',image,'-c',program],check=True)
        return
    import concurrent.futures
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        for number,_ in enumerate(pool.map(prepare_part, [str(root/name) for name in pending]),1):
            if number%10==0:print('Prepared part',number,'/',len(pending),flush=True)
    for part in manifest['parts'].values():
        part['source_sha256']=hashlib.sha256(safe_file(root,part['source']).read_bytes()).hexdigest()
        part['dependencies']={name:hashlib.sha256(safe_file(root,name).read_bytes()).hexdigest() for name in part['dependencies']}
        part['pdf_sha256']=hashlib.sha256(safe_file(root,part['pdf']).read_bytes()).hexdigest()
    write_if_changed(manifest_path,(json.dumps(manifest,indent=2)+'\n').encode())
    data=load(root)
    for slide in data['slides'].values():
        for name in slide.get('resources',{}):slide['resources'][name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
    write_if_changed(root/'library/index.json',(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
    print('Prepared vector parts:',len(manifest['parts']))


def affected(root, changed):
    """List consumers of actual shared dependencies, without building anything."""
    data=load(root)
    paths=set()
    for name in changed:
        path=Path(name)
        if path.is_absolute():
            try:path=path.relative_to(root.resolve())
            except ValueError:raise ValueError('Changed file is outside the checkout: '+name)
        relative=path.as_posix();safe_file(root,relative);paths.add(relative)
    slides={sid:sorted(paths & slide_dependencies(root,slide,data)) for sid,slide in data['slides'].items()}
    slides={sid:dependencies for sid,dependencies in slides.items() if dependencies}
    return {'changed':sorted(paths),'slides':slides,
            **{kind:{name:[sid for sid in item['slides'] if sid in slides] for name,item in data[kind].items()
                     if any(sid in slides for sid in item['slides'])} for kind in ('decks','blocks')}}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('check','sync','fetch','prepare','build','affected'))
    choice=parser.add_mutually_exclusive_group()
    choice.add_argument('--deck');choice.add_argument('--block');choice.add_argument('--all',action='store_true')
    choice.add_argument('--changed',nargs='+',metavar='PATH',help='Select consumers of changed shared files')
    parser.add_argument('--json',action='store_true',help='Machine-readable affected-file report')
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--jobs',type=int,choices=range(1,9),default=2,help='Independent build workers for --all')
    parser.add_argument('--diagnostic',action='store_true',help='Render drafts despite layout warnings; reports remain failed')
    parser.add_argument('--backend',choices=('docker','native'),default='docker')
    parser.add_argument('--image',default=os.environ.get('LATEX_IMAGE','bitbeamer-latex:local'))
    args=parser.parse_args(argv)
    try:
        if args.action=='check':print('Lesson library:',validate(ROOT));sync(ROOT,check=True);check_previews(ROOT)
        elif args.action=='sync':sync(ROOT);validate(ROOT)
        elif args.action=='fetch':fetch(ROOT)
        elif args.action=='prepare':prepare(ROOT,args.backend,args.image)
        elif args.action=='affected':
            if not args.changed:raise ValueError('Choose --changed PATH [PATH ...].')
            result=affected(ROOT,args.changed)
            if args.json:print(json.dumps(result,indent=2))
            else:
                print('Affected slides:',len(result['slides']))
                for sid in result['slides']:print('  '+sid)
                for kind in ('decks','blocks'):
                    print(kind.capitalize()+': '+str(len(result[kind])))
                    for name in result[kind]:print('  python3 scripts/library.py build --'+kind[:-1]+' '+name+' --preview')
        else:
            if args.all or args.changed:
                import concurrent.futures
                data=load(ROOT);selected=affected(ROOT,args.changed) if args.changed else data
                jobs=[(kind,name) for kind in ('decks','blocks') for name in selected[kind]]
                if not jobs:raise ValueError('No lesson consumers found for the supplied files.')
                def run_job(job):
                    kind,name=job;output=ROOT/'build/library'/kind/name;output.mkdir(parents=True,exist_ok=True)
                    command=[sys.executable,str(ROOT/'scripts/library.py'),'build','--deck' if kind=='decks' else '--block',name,'--backend',args.backend,'--image',args.image]
                    if args.diagnostic:command.append('--diagnostic')
                    if args.preview and kind=='decks':command.append('--preview')
                    with (output/'launcher.log').open('w') as log:
                        result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                    report=json.loads((output/'check.json').read_text()) if (output/'check.json').exists() else {'status':'failed','errors':['Compilation failed; inspect launcher.log']}
                    print(kind+'/'+name+': '+report['status'],flush=True)
                    return kind+'/'+name,dict(report,exit_code=result.returncode)
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:reports=dict(pool.map(run_job,jobs))
                (ROOT/'build/library'/('affected-report.json' if args.changed else 'report.json')).write_text(json.dumps(reports,indent=2)+'\n')
                if any(r['exit_code'] or r['status']!='passed' for r in reports.values()) and not args.diagnostic:
                    raise RuntimeError('Collection has failed checks; inspect build/library reports')
            elif args.deck or args.block:
                render(ROOT,'decks' if args.deck else 'blocks',args.deck or args.block,args.backend,args.image,args.preview,args.diagnostic)
            else:raise ValueError('Choose --deck ID, --block ID, --changed PATH or explicitly --all.')
        return 0
    except (ValueError,RuntimeError,OSError,subprocess.CalledProcessError) as error:
        print('Library failed:',error,file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
