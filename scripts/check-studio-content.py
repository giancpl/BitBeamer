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

CASES.update({
 'grouped-covers':(r'''\studiosetup{palette=light}
\studiotemplate[variant=pattern,palette=blue,title={Your title},author={Author name},institute={Organization}]{cover}
\studiotemplate[variant=wide-pattern,title={Your title},author={Author name}]{cover}
\studiotemplate[variant=photo,title={Your title},author={Author name}]{cover}
\studiotemplate[variant=script,title={Your title}]{cover}
''',None),
 'palette-reset':(r'''\studiosetup{palette=blue}
\studiotemplate{levels}
\studiotemplate[palette=light]{levels}
\studiotemplate[variant=photo]{cover}
\begin{frame}{Normal frame}Ordinary content.\end{frame}
''',None),
 'semantic-captions':(r'\studiotemplate[variant=two,caption-one={One},caption-two={Two},icon-one={alice},icon-two={cow}]{icon-cards}',None),
 'unknown-variant':(r'\studiotemplate[variant=missing]{cover}','Unknown model or variant'),
 'unsupported-palette':(r'\studiotemplate[palette=blue]{horizontal-split}','Unsupported palette'),
 'unavailable-heading':(r'\studiotemplate[variant=two,title={Heading}]{icon-cards}',"not available")
})


CASES['synthetic-palette-rejected']=(r'\studiotemplate[variant=three,palette=blue]{icon-cards}','Unsupported palette')
CASES['legacy-palette-pair']=(r'\studiotemplate[palette=blue]{privacy-levels}',None)
CASES['fixed-table-palette']=(r'''\studiosetup{palette=blue}
\studiotemplate{table}
\studiotemplate[palette=light]{table}
\begin{frame}{Normal frame}Ordinary content.\end{frame}
''',None)

CASES['standard-pages']=(r'\title{Default presentation}\author{Author name}\institute{Organization}\date{}'+r'''
\studiotitleframe
\studiotocframe[title={Outline}]
\section{Alpha topic}
\studioframe[subtitle={Optional subtitle}]{Default content}{First explanation.}
\section{Beta topic}
\studioframe{Next content}{Second explanation.}
\studiotemplate[variant=three]{icon-cards}
\closingframe[title={Goodbye},subtitle={},copyright={}]
\begin{frame}{Normal frame}Ordinary content after the closing.\end{frame}
''',None)
CASES['standard-pages-theme-only']=(r'\title{}\author{}\institute{}\date{}'+r'''
\studiotitleframe
\studiotocframe[title={}]
\section{Single topic}
\studioframe{}{}
\closingframe[title={},subtitle={},copyright={}]
''',None)
CASES['standard-frame-unknown-option']=(r'\studioframe[unknown-option=value]{Title}{Body}','unknown-option')


CASES['standard-cover-variants']=(r'\title{Your title}\author{Author name}\institute{Organization}\date{}'+'\n'+r"""
\studiotitleframe
\studiotitleframe[variant=bitgeneration]
\studiotitleframe[variant=bitgeneration-photo]
\studiotitleframe
\studiotitleframe[variant=wide-pattern]
\studiotitleframe[variant=photo]
\studiotitleframe[variant=classic]
\studioframe{Normal frame}{Ordinary content.}
""",None)
CASES['standard-cover-empty']=(r'\title{}\author{}\institute{}\date{}'+r'\studiotitleframe[variant=bitgeneration]\studiotitleframe[variant=photo]\studiotitleframe',None)
CASES['standard-cover-unknown-variant']=(r'\studiotitleframe[variant=not-a-cover]','not-a-cover')
CASES['standard-cover-missing-library']=(r'\studiotitleframe[variant=bitgeneration]','Optional cover variants require')


def corner(pdf,page,backend,image,full=False):
    options=['-f',str(page),'-singlefile','-scale-to-x','320' if full else '16','-scale-to-y','180' if full else '9']
    tool=shutil.which('pdftoppm')
    if tool:command=[tool,*options,str(pdf)]
    elif backend=='docker':command=['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp','--mount',f'type=bind,source={pdf.parent.resolve()},target=/input,readonly','--entrypoint','pdftoppm',image,*options,'/input/'+pdf.name]
    else:raise RuntimeError('Colour verification needs Poppler (pdftoppm).')
    raw=subprocess.check_output(command);pixels=raw.split(b'\n',3)[3]
    return pixels if full else tuple(pixels[:3])



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
        preamble=PREAMBLE.replace(r'\usepackage{bitpolitostudiotemplates}'+'\n','') if name in ('standard-pages-theme-only','standard-cover-missing-library') else PREAMBLE
        document=folder/'test.tex';document.write_text(preamble+body+'\n\\end{document}\n',encoding='utf-8')
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
            if name in ['palette-reset','fixed-table-palette']:
                pages=([(1,(0,28,224)),(2,(249,249,249)),(4,(249,249,249))] if name=='palette-reset' else [(1,(249,249,249)),(2,(249,249,249)),(3,(249,249,249))])
                for page,expected in pages:
                    actual=corner(folder/'test.pdf',page,backend,image)
                    if actual!=expected:raise RuntimeError(f'Palette state/normal-frame leak in {name} page {page}: {actual}, expected {expected}')
            if name=='standard-cover-variants':
                pages=[' '.join(p.split()) for p in pdf_text(folder/'test.pdf',backend,image).split('\f') if p.strip()]
                if len(pages)!=8 or any(not all(value in page for value in ('Your title','Author name','Organization')) for page in pages[:7]):
                    raise RuntimeError('Cover variants did not preserve shared metadata')
                for page in (1,4,7):
                    if corner(folder/'test.pdf',page,backend,image)!=(0,28,224):
                        raise RuntimeError('Classic blue cover was not the default/reset treatment')
                if corner(folder/'test.pdf',2,backend,image)!=(249,249,249) or corner(folder/'test.pdf',8,backend,image)!=(249,249,249):
                    raise RuntimeError('Cover variant colours leaked into a normal frame')
                if corner(folder/'test.pdf',1,backend,image,full=True)!=corner(folder/'test.pdf',4,backend,image,full=True):
                    raise RuntimeError('Cover variant option did not reset between calls')
            if name=='standard-pages':
                pages=[' '.join(p.split()) for p in pdf_text(folder/'test.pdf',backend,image).split('\f') if p.strip()]
                if len(pages)!=7 or 'Default presentation' not in pages[0] or any(label not in pages[1] for label in ['Outline','Alpha topic','Beta topic']):
                    raise RuntimeError('Standard cover/automatic contents did not render their metadata and sections')
                if 'Optional subtitle' not in pages[2] or 'Optional subtitle' in pages[3] or 'Goodbye' not in pages[5] or 'Ordinary content after the closing.' not in pages[6]:
                    raise RuntimeError('Default frame options or closing state leaked into another page')
                for page,expected in [(1,(0,28,224)),(2,(249,249,249)),(7,(249,249,249))]:
                    if corner(folder/'test.pdf',page,backend,image)!=expected:raise RuntimeError('Unexpected standard page background')
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
