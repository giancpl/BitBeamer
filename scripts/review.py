"""Build one Studio slide, the working selection, or the explicit full archive."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import webbrowser

import build
from asset_library import write_if_changed
from studio_templates import inspect_templates, inspect_aliases, catalogue_document, prepare_catalogue
from studio_review import selected
from studio_preview import input_sets, load_manifest, save_manifest, digest, thumbnail, combine_pdfs

ROOT = Path(__file__).resolve().parents[1]


def single_document(entry, page):
    source = catalogue_document([entry])
    return source.replace(r'\begin{document}', r'\begin{document}'+'\n'+r'\setcounter{framenumber}{'+str(page-1)+'}',1)


def compile_document(root, document, output, backend, image, force=False):
    args = [str(document),str(output),'--backend',backend,'--image',image]
    if force:
        args.append('--force')
    if build.main(args, root=root):
        raise RuntimeError('Review compilation failed: '+str(document))
    pdf = output/(document.stem+'.pdf')
    log = output/(document.stem+'.log')
    if log.exists():
        text = log.read_text(encoding='utf-8',errors='replace')
        if any(word in text for word in ('Overfull \\hbox','Overfull \\vbox','Missing character:', 'Missing asset', 'undefined references')):
            raise RuntimeError('Review found overflow, a missing glyph/asset or unresolved references. See '+str(log))
    return pdf


def open_pdf(path):
    if sys.platform == 'win32':
        os.startfile(str(path))
    elif sys.platform == 'darwin':
        subprocess.run(['open',str(path)],check=True)
    elif __import__('shutil').which('xdg-open'):
        subprocess.run(['xdg-open',str(path)],check=True)
    else:
        webbrowser.open(path.as_uri())


def render_slide(root, entry, page, values, backend, image):
    output = root/'build/review/slides'/entry['id']
    output.mkdir(parents=True,exist_ok=True)
    document = output/'slide.tex'
    write_if_changed(document,single_document(entry,page).encode())
    cache = output/'cache.json'
    pdf = output/'slide.pdf'
    expected = {'inputs':values, 'document':digest(document), 'backend':backend, 'image':image}
    stored = json.loads(cache.read_text()) if cache.exists() else {}
    if stored.get('build') == expected and pdf.is_file() and stored.get('pdf') == digest(pdf):
        print('Reused PDF: '+str(pdf))
    else:
        pdf = compile_document(root,document,output,backend,image,force=True)
        write_if_changed(cache,(json.dumps({'build':expected,'pdf':digest(pdf)},indent=2)+'\n').encode())
    manifest = load_manifest(root)
    target = root/'docs/templates/previews'/(entry['id']+'.png')
    if manifest.get('models',{}).get(entry['id']) != values or not target.exists() or digest(target) != manifest.get('previews',{}).get(entry['id']):
        thumbnail(root,pdf,target,backend,image)
        manifest.setdefault('models',{})[entry['id']] = values
        manifest.setdefault('previews',{})[entry['id']] = digest(target)
        manifest['schema'] = 2
        manifest.pop('inputs',None)
        save_manifest(root,manifest)
        print('Updated preview: '+entry['id'])
    return pdf


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('slide','selection','all','sync','check'))
    parser.add_argument('id',nargs='?')
    parser.add_argument('--open',action='store_true',help='Open the resulting PDF')
    parser.add_argument('--backend',choices=('docker','native'),default='docker')
    parser.add_argument('--image',default=os.environ.get('LATEX_IMAGE','bitbeamer-latex:local'))
    args = parser.parse_args(argv)
    try:
        if (args.action == 'slide') != bool(args.id):
            raise ValueError('Only slide requires a model ID')
        if args.open and args.action in ('sync','check'):
            raise ValueError('--open needs slide, selection or all')
        if args.action == 'check':
            prepare_catalogue(root,check=True)
            from doc_checks import check_docs
            from asset_library import check_prepared
            from asset_catalogue import check_catalogue
            from studio_assets import prepare_studio
            from studio_parts import prepare as check_parts
            from studio_collection import prepare as check_collection
            import runpy
            check_docs(root);check_prepared(root);check_catalogue(root);prepare_studio(root,check=True)
            check_parts(root,check=True);check_collection(root,check=True)
            from studio_slots import prepare as check_slots
            check_slots(root,check=True)
            runpy.run_path(str(root/'scripts/catalogue-studio-collection.py'))['catalogue'](root,check=True)
            runpy.run_path(str(root/'scripts/check-repo.py'))['check_repository'](root)
            print('Review sources, documentation, prepared parts and previews are current.')
            return 0
        prepare_catalogue(root)
        if args.action == 'sync':
            import runpy
            runpy.run_path(str(root/'scripts/catalogue-studio-collection.py'))['catalogue'](root)
            print('Synchronized review sheet, registries, guides, galleries and selection showcase. No slides compiled.')
            return 0
        entries = inspect_templates(root)
        by_id = {e['id']:(i,e) for i,e in enumerate(entries,1)}
        if args.action == 'slide':
            name = args.id
            aliases = {a['id']:a['alias_of'] for a in inspect_aliases(root,entries)}
            if name in aliases:
                name = aliases[name]
                print('Reviewing current source for compatibility name '+args.id+': '+name)
            if name not in by_id:
                raise ValueError('Unknown Studio model: '+name)
            values = input_sets(root,entries)
            page, entry = by_id[name]
            pdf = render_slide(root,entry,page,values[name],args.backend,args.image)
        else:
            names = [e['id'] for e in selected(root,entries)] if args.action == 'selection' else list(by_id)
            values = input_sets(root,entries)
            manifest = load_manifest(root)
            for name in names:
                preview = root/'docs/templates/previews'/(name+'.png')
                if manifest.get('models',{}).get(name) != values[name] or not preview.exists() or digest(preview) != manifest.get('previews',{}).get(name):
                    page, entry = by_id[name]
                    render_slide(root,entry,page,values[name],args.backend,args.image)
            source = root/('examples/studio-selected-templates.tex' if args.action == 'selection' else 'examples/studio-template-catalogue.tex')
            pdf = compile_document(root,source,root/'build/review',args.backend,args.image)
            if args.action == 'all':
                index = compile_document(root,root/'examples/studio-review-index.tex',root/'build/review',args.backend,args.image)
                pdf = combine_pdfs(root,[index,pdf],root/'build/review/bitbeamer-studio-review.pdf',args.backend,args.image)
        if args.open:
            open_pdf(pdf)
        print('Review PDF: '+str(pdf))
        return 0
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as error:
        print('Review failed: '+str(error),file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
