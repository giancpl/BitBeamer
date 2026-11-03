"""Build a lightweight image overview; retain the separate editable/vector model catalogue."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import build
from studio_models import load_models

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend',choices=['docker','native'],default='docker')
    p.add_argument('--image',default='bitbeamer-latex:local')
    a=p.parse_args();pdf=ROOT/'build/review/studio-model-catalogue.pdf'
    if not pdf.is_file():raise RuntimeError('Build the model catalogue with scripts/review.py models first.')
    folder=ROOT/'build/review/model-overview';folder.mkdir(parents=True,exist_ok=True)
    options=['-jpeg','-jpegopt','quality=85,optimize=y','-scale-to-x','1280','-scale-to-y','-1']
    if shutil.which('pdftocairo'):
        command=['pdftocairo',*options,str(pdf),str(folder/'page')]
    elif a.backend=='docker':
        command=['docker','run','--rm','--network','none','--entrypoint','pdftocairo','--mount',f'type=bind,source={pdf.parent},target=/input,readonly','--mount',f'type=bind,source={folder},target=/output',a.image,*options,'/input/'+pdf.name,'/output/page']
    else:raise RuntimeError('Overview maintenance needs Poppler, or --backend docker.')
    subprocess.run(command,check=True)
    images=sorted(folder.glob('page-*.jpg'),key=lambda p:int(p.stem.split('-')[-1]))
    models=load_models(ROOT)['models']
    if len(images)!=len(models):raise RuntimeError('Rebuild the model PDF: its page count does not match the grouped collection.')
    text=r'''\documentclass{article}
\usepackage[paperwidth=160mm,paperheight=90mm,margin=0mm]{geometry}
\usepackage{graphicx,tikz,inter}
\definecolor{brand}{HTML}{001CE0}
\pagestyle{empty}\parindent=0pt
\begin{document}
'''
    for number,(model,image) in enumerate(zip(models,images),1):
        command=r'\studiotemplate[variant='+model['default_variant']+']{'+model['id']+'}'
        text+=r'\null\begin{tikzpicture}[remember picture,overlay]\node[inner sep=0pt] at (current page.center) {\includegraphics[width=\paperwidth,height=\paperheight]{'+image.relative_to(ROOT).as_posix()+'}};'+'\n'
        text+=r'\node[anchor=south,fill=white,text=brand,minimum width=\paperwidth,minimum height=14pt,inner sep=2pt,font=\fontsize{6}{7}\selectfont] at (current page.south) {Image overview '+str(number)+r' \quad\texttt{\detokenize{'+command+'}}};\end{tikzpicture}'+'\n'
        if number<len(models):text+=r'\newpage'+'\n'
    text+=r'\end{document}'+'\n';document=folder/'studio-model-overview.tex';document.write_text(text)
    if build.main([str(document),str(ROOT/'build/review'),'--backend',a.backend,'--image',a.image],root=ROOT):return 1
    result=ROOT/'build/review/studio-model-overview.pdf'
    if shutil.which('pdfinfo'):
        command=['pdfinfo',str(result)]
    else:
        command=['docker','run','--rm','--network','none','--entrypoint','pdfinfo','--mount',f'type=bind,source={result.parent},target=/input,readonly',a.image,'/input/'+result.name]
    details=subprocess.check_output(command,text=True)
    import re
    pages=int(re.search(r'(?m)^Pages:\s+(\d+)',details)[1])
    if pages!=len(models):raise RuntimeError(f'Overview has {pages} pages; expected exactly {len(models)} model pages.')
    print(f'Lightweight overview: {result} ({result.stat().st_size/1024/1024:.2f} MiB)')
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as error:print(error,file=sys.stderr);sys.exit(1)
