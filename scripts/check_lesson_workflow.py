"""Exercise lesson reuse in a clean source copy, including a path with spaces."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root=ROOT,backend='docker',image='bitbeamer-latex:local',also_native_container=False):
    output=root/'build/library/workflow';output.mkdir(parents=True,exist_ok=True)
    names=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root,check=True,stdout=subprocess.PIPE).stdout.decode().split('\0')
    with tempfile.TemporaryDirectory(prefix='clone with spaces ',dir=output) as temporary:
        clone=Path(temporary)
        for name in names:
            if not name:continue
            source=root/name
            if not source.is_file():continue
            target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        shared={p.relative_to(clone).as_posix():digest(p) for p in clone.rglob('*') if p.is_file()}
        data=json.loads((clone/'library/index.json').read_text());hash_slides=set(data['blocks']['hashing']['slides'])
        second=next(name for name,item in data['blocks'].items() if not hash_slides.intersection(item['slides']))
        reports=[]
        modes=[backend]+(['native-container'] if also_native_container else [])
        def execute(mode,arguments,label,expected=0):
            if mode=='native-container':
                command=['docker','run','--rm','--network','none']
                if hasattr(os,'getuid'):command+=['--user',f'{os.getuid()}:{os.getgid()}']
                command+=['--mount',f'type=bind,source={clone},target=/source','--workdir','/source','--entrypoint','python3',image,'scripts/deck.py',*arguments]
            else:command=[sys.executable,str(clone/'scripts/deck.py'),*arguments]
            result=subprocess.run(command,cwd=clone,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (output/(label+'.log')).write_text(result.stdout)
            if result.returncode!=expected:raise RuntimeError(label+': unexpected exit status; inspect '+str(output/(label+'.log')))
            return result.stdout
        for number,mode in enumerate(modes):
            token='native' if mode=='native-container' else mode;whole=token+'-lesson-whole';mixed=token+'-lesson-mixed'
            execute(mode,['new',whole,'--from','bitcoin-introduction-short'],token+'-copy')
            execute(mode,['new',whole,'--from','bitcoin-introduction-short'],token+'-overwrite-rejected',expected=1)
            execute(mode,['new',mixed],token+'-new')
            project=clone/'presentations'/mixed;prefix='presentations/'+mixed
            # This is an explicitly labelled local workflow test, not a fictional public talk.
            source=r'''\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\title{Reusable lesson review}
\author{Local workflow check}
\institute{BitBeamer}
\date{}
\begin{document}
\studiotitleframe
\studioteamframe[value-one={},value-two={},value-three={},value-four={},caption-one={Learning},caption-two={Open source},caption-three={Local work},caption-four={Review}]
\studiotocframe
\section{Reusable content}
\studioframe{A personal illustration}{\alice[height=1.6cm]\quad\cow[height=1.4cm]}
% BITBEAMER: INSERT BLOCKS HERE
\begin{frame}[allowframebreaks]{Sources}\printbibliography\end{frame}
\closingframe
\end{document}
'''
            (project/'main.tex').write_text(source)
            execute(mode,['add',mixed,'--block','hashing'],token+'-add-hashing')
            execute(mode,['add',mixed,'--block',second],token+'-add-second')
            before={p.relative_to(project).as_posix():digest(p) for p in project.rglob('*') if p.is_file()}
            execute(mode,['add',mixed,'--block','hashing'],token+'-duplicate-rejected',expected=1)
            if before!={p.relative_to(project).as_posix():digest(p) for p in project.rglob('*') if p.is_file()}:raise RuntimeError('A rejected import changed the personal deck.')
            # Give each project its own bibliography key and image, then prove content independence.
            shutil.copy2(clone/'assets/generated/coin.pdf',project/'assets/custom.pdf')
            personal='workflow-'+token
            with (project/'references.bib').open('a') as bib:bib.write('\n@online{'+personal+',title={BitPolito educational presentations},url={https://github.com/BitPolito/decks},urldate={2026-11-04}}\n')
            main=(project/'main.tex').read_text().replace(r'\cow[height=1.4cm]',r'\includegraphics[height=1.4cm]{'+prefix+'/assets/custom.pdf}'+r'\nocite{'+personal+'}')
            (project/'main.tex').write_text(main)
            local_state=json.loads((project/'library-imports.json').read_text());local_slide=project/'slides'/(local_state['slides'][0]+'.tex');original=local_slide.read_text();local_slide.write_text('% Personal copy verification.\n'+original)
            compiler='native' if mode=='native-container' else mode
            execute(mode,['check',mixed,'--backend',compiler,'--preview'],token+'-mixed-check')
            # The whole copied lesson must build without any shared lesson directory.
            library=clone/'library';hidden=clone/'library unavailable'
            library.rename(hidden)
            try:execute(mode,['check',whole,'--backend',compiler,'--preview'],token+'-independent-whole-check')
            finally:hidden.rename(library)
            for name in (whole,mixed):
                result=json.loads((clone/'build/presentations'/name/'check.json').read_text())
                if result['errors']:raise RuntimeError('Personal check failed: '+name)
                reports.append({'project':name,'backend':mode,'pages':result['pages'],'preview_pages':len(result['preview']),'status':'passed'})
        after={name:digest(clone/name) for name in shared}
        if shared!=after:raise RuntimeError('Authoring changed shared source files in the clean copy.')
        report={'status':'passed','source_copy':'tracked and prospective distributable files; ignored originals and personal decks excluded','path_with_spaces':True,'shared_sources_unchanged':True,'independent_lesson_copy':True,'overwrite_and_duplicate_rejection':True,'projects':reports,'visual_approval':'not performed by this technical check'}
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--backend',choices=('docker','native'),default='docker');parser.add_argument('--image',default='bitbeamer-latex:local');parser.add_argument('--also-native-in-container',action='store_true');args=parser.parse_args(argv)
    try:check(backend=args.backend,image=args.image,also_native_container=args.also_native_in_container);return 0
    except (OSError,RuntimeError,subprocess.CalledProcessError) as error:print('Lesson workflow failed:',error,file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
