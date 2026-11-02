"""Package measured Studio review sources into deterministic upload-sized projects."""
import argparse
import hashlib
import tempfile
import json
from pathlib import Path
import re
from zipfile import ZipFile,ZipInfo,ZIP_STORED
from package import STUDIO_THEME_FILES,STUDIO_BRAND_FILES,STUDIO_ASSETS
from studio_collection import prepare
from studio_parts import prepare as pilot_parts
from studio_templates import inspect_aliases, registry_document
from studio_guides import portable_guides
ROOT=Path(__file__).resolve().parents[1]
LIMIT=45*1024*1024

def common_files(root):
    files={name:root/name for name in STUDIO_THEME_FILES}
    for name in STUDIO_BRAND_FILES:files['images/bitpolito/'+name]=root/'images/bitpolito'/name
    for name in STUDIO_ASSETS:files['images/studio/'+name]=root/'images/studio'/name
    for path in (root/'assets/generated').glob('*.pdf'):files[path.relative_to(root).as_posix()]=path
    for relative in ['bibliography.bib','LICENSE','assets/generated/catalogue.tex','examples/code/studio-transaction.txt','examples/data/studio-line.csv']:
        files[relative]=root/relative
    return files

def entry_files(root,entry):
    files={entry['source']:root/entry['source']}
    files.update({name:root/name for name in entry.get('slot_parts',[])})
    for part in entry.get('parts',[]):
        folder='images/studio/parts' if (root/'images/studio/parts'/(part+'.pdf')).exists() else 'images/studio/collection'
        name=folder+'/'+part+'.pdf';files[name]=root/name
    return files

def document(entries,short=False):
    chosen=entries[:6] if short else entries
    return ('\\documentclass[aspectratio=169]{beamer}\n\\usetheme{bitpolito-studio}\n\\usepackage{bitpolitostudiotemplates}\n\\usepackage[backend=biber]{biblatex}\n\\addbibresource{bibliography.bib}\n\\begin{document}\n'+''.join('\\studiotemplate{'+e['id']+'}\n' for e in chosen)+'\\end{document}\n').encode()

def generated_data(root,entries):
    data={}
    data['templates/studio/registry.tex']=registry_document([e for e in entries if not e.get('alias_of')], [e for e in entries if e.get('alias_of')]).encode()
    data['main.tex']=document(entries,short=True);data['catalogue.tex']=document(entries)
    data.update(portable_guides(root, entries))
    from studio_content_examples import document as customization_document
    data['customization.tex']=customization_document(entries).encode()
    data['README.md']=('# Studio graphical review\n\nOpen main.tex with pdfLaTeX. It contains at most six models for a quick first build.\nSelect catalogue.tex to render every model in this archive; larger catalogues may need a longer compile timeout.\nSee [the per-slide usage guides](TEMPLATES.md) for complete copyable examples and field tables.\nNo Python, converter, shell escape or Figma export is needed.\n\nLoad the Studio theme and bitpolitostudiotemplates. Each model accepts its documented named fields; edit its source for structural changes.\nAll models are in review or supplementary. No release approval is implied.\n\n## Included compositions\n\n'+''.join('- `\\studiotemplate{'+e['id']+'}` ('+e['status']+')\n' for e in entries)+'\nChoose additional models through the repository review packager; this archive declares only the included model IDs.\n').encode()
    return data

def archive_size(root, entries, files):
    data=generated_data(root,entries)
    names=set(files)|set(data)
    # Stored ZIP entries have a 30-byte local and 46-byte central header.
    return (sum(path.stat().st_size for path in files.values()) + sum(len(raw) for raw in data.values())
            + sum(76 + 2*len(name.encode('utf-8')) for name in names) + 22)

def write_archive(root,target,entries):
    files=common_files(root)
    for e in entries:files.update(entry_files(root,e))
    data={name:path.read_bytes() for name,path in files.items()}
    data.update(generated_data(root,entries))
    target.parent.mkdir(parents=True,exist_ok=True);temporary=target.with_name(target.name+'.tmp')
    try:
        with ZipFile(temporary,'w',compression=ZIP_STORED) as archive:
            for name,raw in sorted(data.items()):
                info=ZipInfo(name,(2026,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
                if Path(name).suffix in ['.tex','.sty','.md','.bib','.csv','.txt']:raw=raw.replace(b'\r\n',b'\n')
                archive.writestr(info,raw)
        if temporary.stat().st_size>50*1024*1024:raise RuntimeError('Review archive exceeds the upload limit: '+str(target))
        if temporary.stat().st_size>45*1024*1024:raise RuntimeError('Review archive exceeds the 45 MiB budget; this model needs smaller prepared dependencies: '+str(target))
        temporary.replace(target)
    finally:temporary.unlink(missing_ok=True)
    return {'archive':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'models':[e['id'] for e in entries]}

def package(root=ROOT,output=None,names=None):
    prepare(root,check=True);pilot_parts(root,check=True)
    from studio_slots import prepare as check_slots
    check_slots(root,check=True)
    from studio_templates import inspect_templates
    entries=inspect_templates(root)
    if names:
        entries += inspect_aliases(root, entries)
        requested=set(names);known={e['id'] for e in entries}
        if requested-known:raise RuntimeError('Unknown models: '+', '.join(sorted(requested-known)))
        entries=[e for e in entries if e['id'] in requested]
    output=Path(output or root/'build/review/overleaf');output.mkdir(parents=True,exist_ok=True)
    base=common_files(root);groups=[];group=[];files=dict(base)
    for e in entries:
        additional=entry_files(root,e);candidate={**files,**additional};size=archive_size(root,group+[e],candidate)
        if group and size>LIMIT:groups.append(group);group=[];files=dict(base);candidate={**files,**additional}
        group.append(e);files=candidate
    if group:groups.append(group)
    # Read/validate everything before replacing any previous upload archive.
    for items in groups:
        for e in items:
            for path in entry_files(root,e).values():path.read_bytes()
    report=[]
    with tempfile.TemporaryDirectory(prefix='.studio-review-',dir=output.parent) as temporary:
        staging=Path(temporary)
        for i,items in enumerate(groups,1):
            target=staging/f'bitbeamer-studio-review-{i:02}.zip'
            report.append(write_archive(root,target,items))
        # Validate every archive before replacing the previous review set.
        for item in report:(staging/item['archive']).replace(output/item['archive'])
        selected={item['archive'] for item in report}
        for previous in output.glob('bitbeamer-studio-review-*.zip'):
            if previous.name not in selected:previous.unlink()
        index=staging/'index.json'
        index.write_text(json.dumps({'status':'in review','budget_bytes':45*1024*1024,'upload_limit_bytes':50*1024*1024,'archives':report},indent=2)+'\n', encoding='utf-8')
        index.replace(output/'index.json')
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    choice=parser.add_mutually_exclusive_group()
    choice.add_argument('--templates', help='Comma-separated model IDs; default is the complete collection')
    choice.add_argument('--selection', action='store_true', help='Package the curated working set into a separate output folder')
    args=parser.parse_args()
    names=args.templates.split(',') if args.templates else None
    output=args.output
    if args.selection:
        from studio_gallery import selection
        entries=json.loads((ROOT/'templates/index.json').read_text(encoding='utf-8'))['templates']
        names=[item['id'] for item in selection(ROOT,entries)]
        output=output or ROOT/'build/review/selection-overleaf'
    for item in package(output=output,names=names):
        print(item['archive'],item['bytes'],len(item['models']),'models')
