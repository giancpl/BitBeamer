"""Compile pending compositions from graphical review batches."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import textwrap
import tempfile
from urllib.parse import unquote, urlsplit

import build
from deck import log_issues, pdf_tool
from guide_previews import clean_document, context, signature
from slide_guide import catalogue, review_batches

ROOT = Path(__file__).resolve().parents[1]


def pending_compositions(batch, choices):
    """Use catalogue review status for core templates and fixed lesson presets."""
    return [name for name in batch['compositions'] if choices[name]['status'] != 'approved' and not choices[name].get('edition_exclusion')]


def comparisons(root, folder, names, choices, categories=None, commands=None, backend='docker', image='bitbeamer-latex:local'):
    try:import pymupdf as fitz
    except ImportError as error:
        raise RuntimeError('Original comparisons need the optional lesson-maintenance requirements; normal batch compilation does not.') from error
    from io import BytesIO
    from PIL import Image
    from guide_comparisons import sync
    sync(root)
    script=(root/'build/checks/slide-guide/comparisons.js').read_text(encoding='utf-8')
    records=json.loads(script.split('=',1)[1].strip().rstrip(';'))['records']
    originals={}
    inventory=json.loads((root/'templates/figma-inventory.json').read_text(encoding='utf-8'))
    reference_files={f['id']:f['file'] for f in inventory['frames']}
    original_labels={}
    for name in names:
        variants=records.get(name,{}).get('variants',[])
        if not variants:raise ValueError('No local original for '+name+'. Prepare its reference before requesting --compare.')
        original=(root/'docs/slides'/unquote(urlsplit(variants[0]['original']).path)).resolve()
        if not original.is_relative_to(root.resolve()) or not original.is_file():raise ValueError('Missing or unsafe original: '+name)
        originals[name]=original
        reference_id=variants[0].get('label','')
        original_labels[name]=reference_files.get(reference_id, reference_id)
    with fitz.open(folder/'main.pdf') as replica, fitz.open() as result:
        for number,name in enumerate(names):
            invocation=(commands or {}).get(name,choices[name]['command'])
            command_lines=textwrap.wrap('Use: '+' '.join(invocation.split()),width=190,
                                        break_long_words=False,break_on_hyphens=False)
            page=result.new_page(width=1400,height=460+11*(len(command_lines)-1))
            page.insert_text((20,22),str(number+1)+' / '+str(len(names))+' | '+name+' | '+(categories or {}).get(name,''),fontsize=13)
            page.insert_text((20,46),choices[name].get('reference_note','Original reference')+' | '+original_labels[name],fontsize=10)
            page.insert_text((710,46),'Current template',fontsize=10)
            # Render both sides through the same source-size / thumbnail pipeline.
            # Mixing a thumbnail with live PDF artwork changes fine edges and
            # soft shadows at review zoom levels. The separate main.pdf keeps
            # the full editable/vector template for detailed inspection.
            with Image.open(originals[name]) as source:
                reference=source.convert('RGB')
            original_size=reference.size
            # Poppler preserves the exact light canvas (249); MuPDF truncates
            # the same PDF fill to 248 when rasterising it. Use the guide renderer.
            from studio_preview import thumbnail
            with tempfile.TemporaryDirectory(prefix='comparison-render-',dir=folder) as temporary:
                rendered=Path(temporary)/'current.png'
                thumbnail(root,folder/'main.pdf',rendered,backend,image,number+1,width=original_size[0])
                with Image.open(rendered) as raster:
                    current=raster.convert('RGB')
            if current.size!=original_size:
                current=current.resize(original_size,Image.Resampling.LANCZOS)
            for artwork,rectangle in ((reference,fitz.Rect(20,60,690,437)),
                                      (current,fitz.Rect(710,60,1380,437))):
                artwork.thumbnail((1600,900),Image.Resampling.LANCZOS)
                encoded=BytesIO();artwork.save(encoded,format='PNG',optimize=True)
                page.insert_image(rectangle,stream=encoded.getvalue(),keep_proportion=True)
            for line,text in enumerate(command_lines):
                page.insert_text((20,451+11*line),text,fontsize=9,fontname='cour')
        temporary=folder/'comparisons.tmp.pdf';result.save(temporary,garbage=4,deflate=True);temporary.replace(folder/'comparisons.pdf')
    return {name:path.relative_to(root).as_posix() for name,path in originals.items()}


def prepare(root, name, backend='docker', image='bitbeamer-latex:local', compare=False):
    payload=catalogue(root);batches={b['id']:b for b in review_batches(root,payload)}
    if name not in batches:raise ValueError('Unknown review batch: '+name)
    batch=batches[name];choices={c['id']:c for row in payload['rows'] for c in row['choices']}
    names=pending_compositions(batch,choices)
    if not names:raise ValueError('No compositions pending review in '+name+'. All registered compositions are approved.')
    categories={c['id']:row['family'] for row in payload['rows'] for c in row['choices']}
    folder=root/'build/review/batches'/name;folder.mkdir(parents=True,exist_ok=True)
    commands={n:batch.get('commands',{}).get(n,choices[n]['command']) for n in names}
    document=folder/'main.tex';source=clean_document(list(commands.values()))
    if not document.exists() or document.read_text(encoding='utf-8')!=source:document.write_text(source,encoding='utf-8')
    ctx=context(root)
    fingerprint=hashlib.sha256(json.dumps({'commands':source,'inputs':{n:signature(root,n,ctx) for n in names},'backend':backend,'image':image},sort_keys=True).encode()).hexdigest()
    cache=folder/'cache.json';previous=json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
    pdf=folder/'main.pdf'
    if previous.get('fingerprint')!=fingerprint or not pdf.is_file() or previous.get('pdf')!=hashlib.sha256(pdf.read_bytes()).hexdigest():
        if build.main([str(document),str(folder),'--backend',backend,'--image',image],root=root):raise RuntimeError('Review batch compilation failed; any previous PDF is stale.')
        issues=log_issues((folder/'main.log').read_text(encoding='utf-8',errors='replace'))
        if issues:raise RuntimeError('Batch diagnostics: '+str(issues))
        import re
        info=pdf_tool(root,'pdfinfo',pdf,backend,image)
        if int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1])!=len(names):raise RuntimeError('Incorrect review batch page count.')
        cache.write_text(json.dumps({'fingerprint':fingerprint,'pdf':hashlib.sha256(pdf.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    else:print('Reused batch PDF:',pdf)
    if compare:
        from review_backgrounds import check_pdf
        check_pdf(root,pdf,[(i,n,commands[n]) for i,n in enumerate(names)],folder/'backgrounds.json')
    originals=comparisons(root,folder,names,choices,categories,commands,backend,image) if compare else {}
    report={'batch':name,'family':batch['family'],'compositions':names,'categories':{n:categories[n] for n in names},'pages':len(names),'status':'compiled; graphical review pending','approval':'none inferred','originals':originals,'commands':commands,'guide':'docs/slides/index.html?batch='+name+'&maintenance=1'}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# '+batch['title'],'','Generated review sheet. Record feedback in the existing review ledgers; no approval is inferred.','']
    for n in names:
        lines.extend(['## '+n,'',*['- '+f for f in batch['focus']],'','```latex',commands[n],'```',''])
    (folder/'review.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Batch PDF:',pdf)
    if compare:print('Original / replica PDF:',folder/'comparisons.pdf')
    return pdf


def combine(root, backend='docker', image='bitbeamer-latex:local', compare=False):
    """Combine only unapproved compositions, retaining registered batch order."""
    from catalogue_selection import active_batch, render_candidates
    if active_batch(root):
        if json.loads((root/'templates/review.json').read_text(encoding='utf-8')).get('active_review_batches'):
            raise ValueError('Activate either original selection or template reconstruction, never both.')
        return render_candidates(root)
    try:import pymupdf as fitz
    except ImportError as error:
        raise RuntimeError('Combined review PDFs need the optional lesson-maintenance requirements.') from error
    payload=catalogue(root)
    choices={c['id']:c for row in payload['rows'] for c in row['choices']}
    categories={c['id']:row['family'] for row in payload['rows'] for c in row['choices']}
    batches=[];reports=[]
    registered=review_batches(root,payload)
    ledger=root/'templates/review.json'
    active=json.loads(ledger.read_text(encoding='utf-8')).get('active_review_batches') if ledger.exists() else None
    if active is not None:
        known={b['id'] for b in registered}
        if not isinstance(active,list) or len(active)!=len(set(active)) or set(active)-known:
            raise ValueError('Invalid active_review_batches; use registered batch IDs.')
        registered=[b for b in registered if b['id'] in active]
    for batch in registered:
        names=pending_compositions(batch,choices)
        if not names:continue
        current=dict(batch,compositions=names)
        pdf=prepare(root,batch['id'],backend,image,compare)
        batches.append(current)
        reports.append((current,pdf.parent/'comparisons.pdf' if compare else pdf))
    if not reports:raise ValueError('No compositions pending review. All registered compositions are approved.')
    folder=root/'build/review/batches'
    target=folder/('comparisons.pdf' if compare else 'all.pdf')
    with fitz.open() as result:
        bookmarks=[]
        for batch,pdf in reports:
            start=len(result)
            with fitz.open(pdf) as source:
                if len(source)!=len(batch['compositions']):raise RuntimeError('Stale pending-review batch: '+batch['id'])
                result.insert_pdf(source)
            bookmarks.append([1,batch['family'],start+1])
            bookmarks.extend([2,name,start+i+1] for i,name in enumerate(batch['compositions']))
        result.set_toc(bookmarks)
        result.set_metadata({'title':'BitBeamer - Pending review comparisons' if compare else 'BitBeamer - Pending review batches'})
        if compare:
            for number,(page,name) in enumerate(zip(result,[n for b in batches for n in b['compositions']]),1):
                # Use a single page count while retaining the composition ID.
                page.add_redact_annot(fitz.Rect(19,7,1381,28),fill=(1,1,1))
                page.apply_redactions(images=0,graphics=0)
                page.insert_text((20,22),str(number)+' / '+str(len(result))+' | '+name+' | '+categories[name],fontsize=13)
        temporary=target.with_suffix('.tmp.pdf')
        result.save(temporary,garbage=4,deflate=True);temporary.replace(target)
    pages=sum(len(b['compositions']) for b in batches)
    if compare:
        from review_specimens import append_specimens
        pages=append_specimens(root,target,batches,backend,image) or pages
    surveys=[root/b['reference_survey'] for b in batches if b.get('reference_survey')]
    if surveys:
        with fitz.open(target) as result:
            for survey in surveys:
                if not survey.resolve().is_relative_to((root/'build/review/reference-surveys').resolve()) or not survey.is_file():
                    raise ValueError('Prepare the declared original reference survey before review: '+str(survey))
                with fitz.open(survey) as source:result.insert_pdf(source)
            temporary=target.with_suffix('.survey.pdf');result.save(temporary,garbage=4,deflate=True)
            pages=len(result)
        temporary.replace(target)
    (folder/'all-report.json').write_text(json.dumps({'pdf':target.relative_to(root).as_posix(),'pages':pages,'batches':[b['id'] for b in batches],'pending':[{'id':n,'category':categories[n],'batch':b['id']} for b in batches for n in b['compositions']],'approval':'none inferred'},indent=2)+'\n',encoding='utf-8')
    print('Combined review PDF:',target)
    return target


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch',help='Registered review batch ID, or all; approved compositions are excluded');parser.add_argument('--compare',action='store_true');parser.add_argument('--open',action='store_true')
    parser.add_argument('--backend',choices=('docker','native'),default='docker');parser.add_argument('--image',default=os.environ.get('LATEX_IMAGE','bitbeamer-latex:local'))
    args=parser.parse_args(argv)
    try:
        if args.batch=='all':pdf=combine(ROOT,args.backend,args.image,args.compare)
        else:pdf=prepare(ROOT,args.batch,args.backend,args.image,args.compare)
        if args.open:build.open_pdf(pdf if args.batch=='all' or not args.compare else pdf.parent/'comparisons.pdf')
        return 0
    except (ValueError,RuntimeError,OSError) as error:
        print('Review batch failed:',error,file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
