"""Compile every standalone Studio review ZIP without checkout access or converters."""
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]

def guide_example(project):
    guides=sorted((project/'guides').glob('*.md'))
    if not guides:return None
    guide=next((path for path in guides if path.stem=='three-cards'),guides[0])
    content=guide.read_text(encoding='utf-8')
    match=re.search(r'## Complete one-slide example[\s\S]*?```latex\n(.*?)\n```',content,re.S)
    if not match or not match.group(1).startswith(r'\documentclass'):
        raise RuntimeError('Missing complete example in '+guide.name)
    return match.group(1)+'\n'


def validate(archive, output, backend='docker', image='bitbeamer-latex:local'):
    output=output/archive.stem;output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='BitBeamer Studio review ') as temporary:
        project=Path(temporary)/'extracted project';project.mkdir()
        with ZipFile(archive) as zipped:
            if zipped.testzip():raise RuntimeError('ZIP checksum failed: '+str(archive))
            for name in zipped.namelist():
                path=PurePosixPath(name)
                if path.is_absolute() or '..' in path.parts or ':' in path.parts[0] or '\\' in name:raise RuntimeError('Unsafe archive entry: '+name)
                if path.suffix.lower() in ('.py','.svg','.json','.sh') or path.parts[0] in ('scripts','.github','.vscode','design-references'):raise RuntimeError('Development file in review archive: '+name)
            zipped.extractall(project)
        # Exercise Biber explicitly, including an ordinary frame after the collection.
        (project/'verification.tex').write_text(r'''\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\usepackage[backend=biber]{biblatex}
\addbibresource{bibliography.bib}
\begin{document}
\begin{frame}{Independent project verification}
Normal Studio content after loading the collection. \asset[width=1cm]{alice}
\nocite{*}
\end{frame}
\begin{frame}[allowframebreaks]{Bibliography}\printbibliography\end{frame}
\end{document}
''', encoding='utf-8')
        documents=['main.tex','catalogue.tex','verification.tex']
        if (project/'customization.tex').is_file():documents.append('customization.tex')
        example=guide_example(project)
        if example:
            (project/'guide-example.tex').write_text(example,encoding='utf-8')
            documents.append('guide-example.tex')
        results=[]
        for document in documents:
            if backend=='docker':
                cmd=['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp']
                if hasattr(os,'getuid'):cmd+=['--user',f'{os.getuid()}:{os.getgid()}']
                cmd+=['--workdir','/project','--mount',f'type=bind,source={project},target=/project,readonly','--mount',f'type=bind,source={output},target=/output',image,'-pdf','-g','-no-shell-escape','-outdir=/output',document]
            else:
                cmd=['latexmk','-pdf','-g','-no-shell-escape','-outdir='+str(output),document]
            env=os.environ.copy()
            for key in ('TEXINPUTS','BIBINPUTS','BSTINPUTS','TEXMFHOME'):env.pop(key,None)
            process=subprocess.run(cmd,cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (output/(Path(document).stem+'-build.txt')).write_text(process.stdout, encoding='utf-8')
            if process.returncode:raise RuntimeError('Compilation failed: '+archive.name+'/'+document+'; see '+str(output))
            stem=Path(document).stem;log=(output/(stem+'.log')).read_text(errors='replace', encoding='utf-8')
            if re.search(r'undefined references|Citation .* undefined|Missing character:|Package bitpolitoassets Warning|Text overflow|Graphic overflow|Overfull \\[hv]box',log,re.I):raise RuntimeError('Unresolved layout/reference diagnostics: '+archive.name+'/'+document)
            if document=='verification.tex':
                inputs=(output/(stem+'.fls')).read_text(encoding='utf-8',errors='replace')
                if 'assets/generated/alice.pdf' not in inputs:
                    raise RuntimeError('The registered illustration was not rendered')
            bbl=output/(stem+'.bbl')
            if document=='verification.tex' and (not bbl.exists() or r'\entry{' not in bbl.read_text(encoding='utf-8')):raise RuntimeError('Bibliography was not resolved')
            item={'document':document,'pdf':str((output/(stem+'.pdf')).relative_to(output.parent.parent))}
            if shutil.which('pdfinfo'):
                info=subprocess.check_output(['pdfinfo',str(output/(stem+'.pdf'))],text=True);item['pages']=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
            if shutil.which('pdffonts'):
                fonts=subprocess.check_output(['pdffonts',str(output/(stem+'.pdf'))],text=True)
                rows=[line for line in fonts.splitlines()[2:] if line.strip()]
                if document=='verification.tex' and 'Inter' not in fonts:raise RuntimeError('Inter is missing: '+document)
                if any(line.split()[-5]!='yes' for line in rows):raise RuntimeError('An unembedded font was found: '+document)
                item['all_fonts_embedded']=True
                item['inter_embedded']=any('Inter' in line for line in rows)
            results.append(item)
        print('Validated '+archive.name,flush=True)
        return {'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'backend':backend,'forced_rebuild':True,'documents':results,'shell_escape':False,'checkout_mounted':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=ROOT/'build/review/overleaf')
    parser.add_argument('--output',type=Path,default=ROOT/'build/review/validation')
    parser.add_argument('--backend',choices=('docker','native'),default='docker')
    parser.add_argument('--image',default='bitbeamer-latex:local');parser.add_argument('--jobs',type=int,default=2)
    args=parser.parse_args();args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
    index=json.loads((args.directory/'index.json').read_text(encoding='utf-8'))
    archives=[]
    for item in index['archives']:
        name=item['archive']
        if Path(name).name!=name:raise RuntimeError('Unsafe archive name in review index')
        archive=args.directory.resolve()/name
        if item.get('sha256') and hashlib.sha256(archive.read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('Review archive differs from its index: '+name)
        archives.append(archive)
    if not archives:raise RuntimeError('No review archives; run package-studio-review.py first')
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        report=list(pool.map(lambda a:validate(a,args.output,args.backend,args.image),archives))
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    print('Validated',len(archives),'independent projects.')
if __name__=='__main__':main()
