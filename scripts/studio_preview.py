"""Dependency-scoped preview fingerprints and portable thumbnail rendering."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from asset_library import write_if_changed


def digest(path):
    data = path.read_bytes()
    if path.suffix in {'.tex','.sty','.json','.csv','.bib','.txt'}:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def input_sets(root, entries):
    shared = [p for p in root.glob('*.sty') if 'studio' in p.name or p.name in {
        'beamerfontthemebitpolito.sty','beamercolorthemebitpolito.sty','bitpolitoassets.sty'}]
    shared += [root/'.latexmkrc', root/'assets/generated/catalogue.tex']
    shared += [root/'images/bitpolito'/name for name in ('bull-white.pdf','polito-coat-of-arms-white.pdf')]
    shared += list((root/'images/studio').glob('*.pdf'))
    cache = {}
    def hashed(path):
        key = path.relative_to(root).as_posix()
        if key not in cache:
            cache[key] = digest(path)
        return key, cache[key]
    common = dict(hashed(p) for p in shared)
    icons = {p.stem:p for p in (root/'assets/generated').glob('*.pdf')}
    results = {}
    for number, entry in enumerate(entries, 1):
        files = {root/entry['source']}
        source = (root/entry['source']).read_text(encoding='utf-8')
        source += json.dumps(entry.get('fields', []))
        # Include literal graphic, code and data paths in both source and defaults.
        files.update(root/name for name in re.findall(r'(?:images|examples)/[A-Za-z0-9_./-]+\.(?:pdf|png|jpg|csv|txt)', source))
        # Dedicated data/code inputs may live outside the bundled examples folder.
        literals = [f.get('default','') for f in entry.get('fields',[]) if f.get('type') == 'file']
        literals += re.findall(r'\\(?:input|includegraphics)(?:\[[^\]]*\])?\{([^{}]+)\}', source)
        literals += re.findall(r'\\studiodeclarefield\{(?:code-file|data-file)\}\{([^{}]+)\}', source)
        for name in literals:
            candidate = root/name
            if candidate.is_file() and candidate.resolve().is_relative_to(root.resolve()):
                files.add(candidate)
        for part in entry.get('parts', []):
            candidates = [root/'images/studio'/folder/(part+'.pdf') for folder in ('parts','collection')]
            found = next((p for p in candidates if p.is_file()), None)
            if found is None:
                raise RuntimeError('Missing prepared part for '+entry['id']+': '+part)
            files.add(found)
        for name, path in icons.items():
            if re.search(r'\\'+re.escape(name)+r'\b', source) or re.search(r'\{'+re.escape(name)+r'\}', source):
                files.add(path)
        if re.search(r'\\(?:cite|printbibliography)|references', source):
            files.add(root/'bibliography.bib')
        fields = {key:entry[key] for key in ('id','source','fields','canvas','background','parts') if key in entry}
        fields['page'] = number
        values = dict(common)
        values.update(hashed(path) for path in files)
        values['@layout'] = hashlib.sha256(json.dumps(fields,sort_keys=True).encode()).hexdigest()
        results[entry['id']] = values
    return results


def load_manifest(root):
    path = root/'docs/templates/previews/manifest.json'
    if not path.is_file():
        return {'schema':2,'models':{},'previews':{}}
    return json.loads(path.read_text(encoding='utf-8'))


def save_manifest(root, manifest):
    write_if_changed(root/'docs/templates/previews/manifest.json',
                     (json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode())


def thumbnail(root, pdf, target, backend='docker', image='bitbeamer-latex:local', page=1):
    """Use installed Poppler or the existing compiler image; never convert SVGs."""
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='thumbnail-',dir=target.parent) as temporary:
        prefix = Path(temporary)/'page'
        options = ['-png','-singlefile','-f',str(page),'-l',str(page),'-scale-to-x','480','-scale-to-y','-1']
        if shutil.which('pdftocairo'):
            command = [shutil.which('pdftocairo'),*options,str(pdf),str(prefix)]
        elif backend == 'docker':
            import build
            docker = build.docker_image(root,image)
            command = [docker,'run','--rm','--network','none','--read-only','--tmpfs','/tmp',
                       '--mount',f'type=bind,source={pdf.resolve().parent},target=/input,readonly',
                       '--mount',f'type=bind,source={Path(temporary).resolve()},target=/output',
                       '--entrypoint','pdftocairo',image,*options,'/input/'+pdf.name,'/output/page']
        else:
            raise RuntimeError('Preview updates need Poppler (pdftocairo). Install Poppler or use --backend docker. Compilation itself needs no converter.')
        subprocess.run(command,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        write_if_changed(target,prefix.with_suffix('.png').read_bytes())


def combine_pdfs(root, sources, target, backend='docker', image='bitbeamer-latex:local'):
    """Join the review index and catalogue without a manual Poppler step."""
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='review-index-',dir=target.parent) as temporary:
        prepared = Path(temporary)/target.name
        if shutil.which('pdfunite'):
            command = [shutil.which('pdfunite'),*[str(p) for p in sources],str(prepared)]
        elif backend == 'docker':
            import build
            docker = build.docker_image(root,image)
            command = [docker,'run','--rm','--network','none','--read-only','--tmpfs','/tmp',
                       '--mount',f'type=bind,source={target.parent.resolve()},target=/input,readonly',
                       '--mount',f'type=bind,source={Path(temporary).resolve()},target=/output',
                       '--entrypoint','pdfunite',image,*['/input/'+p.name for p in sources],'/output/'+target.name]
        else:
            raise RuntimeError('The indexed review PDF needs Poppler (pdfunite). Install it or use --backend docker.')
        subprocess.run(command,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        write_if_changed(target,prepared.read_bytes())
    return target
