"""Verify typed Studio content, empty slots, strict errors and normal-frame isolation."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PREAMBLE=r'''\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\begin{document}
'''
CASES={
 'clear-order':(r'''\studiotemplate[text/1={People},clear=text,icon/1={},icon/2={bitcoin}]{two-cards}
\studiotemplate[clear=text,text/1={People},icon/1={},icon/2={bitcoin}]{two-cards}
\begin{frame}{Normal frame}Ordinary content.\end{frame}
''',None),
 'fitted-graphic':(r'\studiotemplate[graphic/1={\rule{25cm}{10cm}},icon/2={cow}]{two-cards}',None),
 'structured-empty':(r'\studiotemplate[body/1={},heading/1={},clear=text,text/title={Checklist}]{checklist-rail}',None),
 'alias':(r'\studiotemplate[text/title={Your message}]{quote-card-blue}',None),
 'unknown-slot':(r'\studiotemplate[text/999={Unknown}]{two-cards}','Unknown field'),
 'missing-icon':(r'\studiotemplate[icon/1={missing-studio-test-icon}]{two-cards}','Unknown icon'),
 'missing-image':(r'\studiotemplate[image/1={missing-studio-test-image.pdf}]{two-cards}','Missing image'),
 'missing-file':(r'\studiotemplate[file/1={missing-studio-test-code.txt}]{code}','Missing file'),
 'text-overflow':(r'\studiotemplate[text/1={One\\Two\\Three\\Four\\Five\\Six}]{two-cards}','Text overflow')}


def pdf_text(pdf,backend,image):
    tool=shutil.which('pdftotext')
    if tool:return subprocess.check_output([tool,str(pdf),'-'],text=True)
    if backend=='docker':
        return subprocess.check_output(['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp',
          '--mount',f'type=bind,source={pdf.parent.resolve()},target=/input,readonly',
          '--entrypoint','pdftotext',image,'/input/'+pdf.name,'-'],text=True)
    raise RuntimeError('Content verification needs Poppler (pdftotext).')


def check(root=ROOT,backend='docker',image='bitbeamer-latex:local'):
    output=root/'build/review/content-api';output.mkdir(parents=True,exist_ok=True)
    report=[]
    for name,(body,error) in CASES.items():
        folder=output/name;folder.mkdir(exist_ok=True)
        document=folder/'test.tex';document.write_text(PREAMBLE+body+'\n\\end{document}\n',encoding='utf-8')
        result=subprocess.run([sys.executable,str(root/'scripts/build.py'),str(document),str(folder),
          '--backend',backend,'--image',image,'--force'],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (folder/'build.txt').write_text(result.stdout,encoding='utf-8')
        if error:
            if result.returncode==0 or "".join(error.split()) not in "".join(result.stdout.split()):
                raise RuntimeError('Expected '+error+' for '+name+'. See '+str(folder/'build.txt'))
        else:
            if result.returncode:raise RuntimeError('Content case failed: '+name+'. See '+str(folder/'build.txt'))
            log=(folder/'test.log').read_text(errors='replace')
            if any(word in log for word in ['Text overflow','Graphic overflow','Overfull \\hbox','Overfull \\vbox','Missing character:']):
                raise RuntimeError('Unexpected layout diagnostics: '+name)
            if name=='clear-order':
                text=pdf_text(folder/'test.pdf',backend,image)
                if text.count('People')!=2 or any(word in text for word in ['Security','Privacy']):
                    raise RuntimeError('clear=text changed with option order or retained shipped text.')
                inputs=(folder/'test.fls').read_text(errors='replace')
                if 'slots/figma-0070-part-02-panel.pdf' not in inputs:
                    raise RuntimeError('Clearing the icon removed its card background.')
        report.append({'case':name,'result':'pass','expected_error':error})
        print('Passed content case:',name,flush=True)
    (output/'checks.json').write_text(json.dumps({'backend':backend,'cases':report},indent=2)+'\n')
    return len(report)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend',choices=('docker','native'),default='docker')
    parser.add_argument('--image',default='bitbeamer-latex:local')
    args=parser.parse_args()
    try:print('Studio content checks:',check(backend=args.backend,image=args.image))
    except (OSError,RuntimeError,subprocess.CalledProcessError) as error:
        print('Studio content checks failed:',error,file=sys.stderr);sys.exit(1)
