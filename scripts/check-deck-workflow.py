"""Exercise private deck isolation and expected diagnostics with a real compiler."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import deck

ROOT = Path(__file__).resolve().parents[1]


def run(root, arguments, log, expected=0):
    result = subprocess.run([sys.executable, '-B', str(root / 'scripts/deck.py'), *arguments], cwd=root,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout, encoding='utf-8')
    if result.returncode != expected:
        raise RuntimeError(f'Expected exit {expected}, received {result.returncode}: {arguments}. See {log}')
    return result.stdout


def snapshot(root):
    """All distributable files, including prospective sources, excluding private outputs."""
    ignored = {'.git', 'build', 'dist', 'presentations', 'design-references', '__pycache__', '.venv', '.pytest_cache'}
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not any(part in ignored for part in p.relative_to(root).parts)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=('docker', 'native'), default='docker')
    parser.add_argument('--image', default='bitbeamer-latex:local')
    args = parser.parse_args(argv)
    root = ROOT
    token = 'workflow-' + uuid.uuid4().hex[:8]
    report_dir = root / 'build/authoring-checks' / token
    report_dir.mkdir(parents=True)
    before = snapshot(root)
    names = [token + '-alpha', token + '-beta']
    source = r'''\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\usepackage[backend=biber,style=numeric]{biblatex}
\addbibresource{presentations/NAME/references.bib}
\graphicspath{{presentations/NAME/assets/}}
\title{Build isolation}
\author{Fixture author}
\institute{Synthetic test content}
\date{}
\begin{document}
\studiotitleframe
\studioteamframe[value-one={1},caption-one={Test group},value-two={2},caption-two={Test stages},value-three={3},caption-three={Test roles},value-four={4},caption-four={Test sources}]
\studiotocframe
\section{Roles}
\studiotemplate[variant=three,title={Three test roles},caption-one={People},caption-two={Processes},caption-three={Tools},icon-one={alice},icon-two={cow},icon-three={coin}]{icon-cards}
\section{Local assets}
\studioframe{Local image}{\centering\includegraphics[height=1cm]{sample.pdf}\par Synthetic reference: \cite{local}.}
\studioframe{Sources}{\printbibliography}
\closingframe
\end{document}
'''
    common = ['--backend', args.backend, '--image', args.image]
    for index, name in enumerate(names):
        run(root, ['new', name], report_dir / f'{index}-new.log')
        project = root / 'presentations' / name
        (project / 'main.tex').write_text(source.replace('NAME', name), encoding='utf-8')
        shutil.copyfile(root / f'assets/generated/{("alice", "cow")[index]}.pdf', project / 'assets/sample.pdf')
        (project / 'references.bib').write_text('@misc{local, title={' + ('Alpha', 'Beta')[index] + ' source fixture}, year={2026}, note={Synthetic reference for isolation testing}}\n', encoding='utf-8')
        run(root, ['check', name, *common, '--preview'], report_dir / f'{index}-check.log')
        output = root / 'build/presentations' / name
        report = json.loads((output / 'check.json').read_text(encoding="utf-8"))
        if report['technical_status'] != 'passed' or not report['preview'] or report['pages'] != 7:
            raise RuntimeError(f'Unexpected fixture report: {output}')
        bbl = (output / 'main.bbl').read_text(encoding="utf-8")
        if ('Alpha', 'Beta')[index] not in bbl or ('Beta', 'Alpha')[index] in bbl:
            raise RuntimeError('Bibliography isolation failed')
        fls = (output / 'main.fls').read_text(encoding="utf-8")
        if f'presentations/{name}/assets/sample.pdf' not in fls.replace('//', '/'):
            raise RuntimeError('Local asset lookup failed')
        run(root, ['new', name], report_dir / f'{index}-overwrite.log', expected=1)
    alpha_pdf = root / 'build/presentations' / names[0] / 'main.pdf'
    alpha_before = hashlib.sha256(alpha_pdf.read_bytes()).hexdigest()
    run(root, ['build', names[0], *common], report_dir / 'cached-build.log')
    if hashlib.sha256(alpha_pdf.read_bytes()).hexdigest() != alpha_before:
        raise RuntimeError('Cached build changed the PDF unexpectedly')
    beta_output = root / 'build/presentations' / names[1]
    beta_before = hashlib.sha256((beta_output / 'main.pdf').read_bytes()).hexdigest()
    target = root / 'presentations' / names[0] / 'main.tex'
    original = target.read_text(encoding="utf-8")
    cases = {
        'citation': (original.replace(r'\cite{local}', r'\cite{missing}'), 'unresolved citation'),
        'overflow': (original.replace('Synthetic reference:', r'\noindent\rule{40cm}{1pt}\par Synthetic reference:'), 'overflow'),
        'placeholder': (original.replace('Fixture author', 'Your name'), None),
        'compile-error': (original.replace(r'\section{Roles}', r'\DefinitelyUndefinedCommand'), 'compilation'),
    }
    for label, (text, expected_kind) in cases.items():
        target.write_text(text, encoding='utf-8')
        run(root, ['check', names[0], *common], report_dir / f'{label}.log', expected=1 if expected_kind else 0)
        report = json.loads((root / 'build/presentations' / names[0] / 'check.json').read_text(encoding="utf-8"))
        if expected_kind and not any(e['kind'] == expected_kind for e in report['errors']):
            raise RuntimeError(f'Expected diagnostic not found: {label}')
        if not expected_kind and not any('placeholder' in w for w in report['warnings']):
            raise RuntimeError('Placeholder warning not found')
    target.write_text(original, encoding='utf-8')
    run(root, ['check', names[0], *common, '--preview'], report_dir / 'restored.log')
    if hashlib.sha256((beta_output / 'main.pdf').read_bytes()).hexdigest() != beta_before:
        raise RuntimeError('Checking the first project changed the second PDF')
    if snapshot(root) != before:
        raise RuntimeError('Authoring changed a shared source file')
    result = {'backend': args.backend, 'projects': names, 'status': 'passed', 'checks': [
        'independent assets, bibliography, PDF and cache', 'existing folder rejected',
        'cached PDF reused', 'unresolved citations', 'overflow', 'placeholder warning',
        'compilation error and stale PDF rejection', 'numbered previews', 'shared sources unchanged'],
        'visual_review': 'not performed by this script'}
    (report_dir / 'report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Private deck workflow passed: {report_dir / "report.json"}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
