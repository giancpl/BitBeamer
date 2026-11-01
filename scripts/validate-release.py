"""Compile the release archive in isolation, using Docker by default."""

import argparse
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

from package import ARCHIVES, STYLES, document_sources
from build import docker_image

CHECKOUT = Path(__file__).resolve().parents[1]


def select_theme(source, options):
    result, count = re.subn(
        r'(?m)^\\usetheme(?:\[[^\]]*\])?\{bitpolito(?:-academic)?\}',
        lambda match: '\\usetheme[' + options + ']{' + ('bitpolito-academic' if '-academic' in match.group(0) else 'bitpolito') + '}', source, count=1)
    if count != 1:
        raise RuntimeError('Cannot select theme options: missing BitPolito theme declaration')
    return result


def validate(archive, style='academic'):
    missing = [tool for tool in ('latexmk', 'pdflatex', 'biber') if not shutil.which(tool)]
    if missing:
        raise RuntimeError('Release validation needs native tools: ' + ', '.join(missing))
    environment = os.environ.copy()
    for name in ('TEXINPUTS', 'BIBINPUTS', 'BSTINPUTS', 'TEXMFHOME'):
        environment.pop(name, None)
    with tempfile.TemporaryDirectory(prefix='bitbeamer-overleaf-') as temporary:
        root = Path(temporary)
        with ZipFile(archive) as zipped:
            if zipped.testzip():
                raise RuntimeError('Archive checksum validation failed')
            for name in zipped.namelist():
                path = PurePosixPath(name)
                if not path.parts or path.is_absolute() or ':' in path.parts[0] or '..' in path.parts or '\\' in name:
                    raise RuntimeError(f'Invalid archive path: {name}')
                if path.suffix.lower() in ('.py', '.sh', '.svg', '.json') or path.parts[0] in ('scripts', '.vscode', '.github') or path.name in ('Dockerfile', 'Makefile', '.dockerignore'):
                    raise RuntimeError(f'Development file found in Overleaf archive: {name}')
            zipped.extractall(root)
        if style == 'academic':
            # Exercise logo options using only files shipped in the ZIP.
            variants = {'main-bitpolito.tex': 'group=bitpolito',
                        'main-crypto.tex': 'group=crypto',
                        'main-wordmark.tex': 'group=bitpolito,bitpolitologo=wordmark',
                        'main-monogram.tex': 'group=bitpolito,bitpolitologo=monogram',
                        'main-bull.tex': 'group=bitpolito,bitpolitologo=bull',
                        'main-image-right.tex': 'cover=image-right'}
            source = (root / 'main.tex').read_text(encoding='utf-8')
            for document, option in variants.items():
                (root / document).write_text(select_theme(source, option), encoding='utf-8')
            legacy = source.replace(r'\usetheme{bitpolito-academic}', r'\usetheme{bitpolito}')
            (root / 'main-legacy.tex').write_text(legacy, encoding='utf-8')
            variants['main-legacy.tex'] = ''
            # Verify full decks in 4:3 and both cover orientations with every logo pair.
            for orientation in ('image-left', 'image-right'):
                document = f'main-{orientation}-43.tex'
                variant = select_theme(source, 'cover=' + orientation).replace('aspectratio=169', 'aspectratio=43')
                (root / document).write_text(variant, encoding='utf-8')
                variants[document] = 'cover=' + orientation
            comparison = (root / 'cover-layouts.tex').read_text(encoding='utf-8')
            logos = {'bull': 'bitpolitologo=bull', 'wordmark': 'bitpolitologo=wordmark',
                     'monogram': 'bitpolitologo=monogram', 'crypto': 'group=crypto'}
            for logo, option in logos.items():
                for aspect in ('169', '43'):
                    if logo == 'bull' and aspect == '169':
                        continue  # The original comparison already exercises this combination.
                    document = f'covers-{logo}-{aspect}.tex'
                    variant = select_theme(comparison, option).replace('aspectratio=169', 'aspectratio=' + aspect)
                    if logo == 'bull' and aspect == '43':
                        variant = variant.replace(r'\title[BitBeamer]{BitBeamer}',
                                                  r'\title[BitBeamer]{Bitcoin, Verification, and Open Participation}')
                    (root / document).write_text(variant, encoding='utf-8')
                    variants[document] = option
        else:
            # Generated only inside the extracted archive, never shipped as a fixture.
            source = (root / 'main.tex').read_text(encoding='utf-8')
            variants = {'studio-long-title.tex': None, 'studio-components.tex': None, 'studio-library-components.tex': None}
            long_title = source.replace(r'\title{Bitcoin\\Slide Layouts}',
                r'\title{Bitcoin and\\Open money}')
            if long_title == source:
                raise RuntimeError('Cannot select the Studio long-title scenario')
            (root / 'studio-long-title.tex').write_text(long_title, encoding='utf-8')
            components = r"""\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\begin{document}
\begin{frame}{A longer Studio heading with enough words to demonstrate automatic wrapping onto a second line}{An optional subtitle}
\begin{studiocards}[columns=2,arrows=true]
\studiocard{\alice[height=4cm]}{An icon automatically fitted to its card}
\studiocard{\bob[height=1cm]}{A second card with a wrapped caption}
\end{studiocards}
\end{frame}
\begin{frame}{Defaults reset}
\begin{studiocards}
\studiocard{\cow[height=1cm]}{One}
\studiocard{\bitcoin[height=1cm]}{Two}
\studiocard{\wallet[height=1cm]}{Three}
\end{studiocards}
\end{frame}
\begin{frame}{Two statistics}
\begin{studiostats}[2]
\studiostat{12}{First example}
\studiostat{34}{Second example}
\end{studiostats}
\end{frame}
\begin{frame}{Three short panels}
\begin{studiopanels}[3]
\studiopanel{First}{A short explanation.}
\studiopanel{Second}{Another short explanation.}
\studiopanel{Third}{One final point.}
\end{studiopanels}
\end{frame}
\begin{frame}{Four horizontal events}
\begin{studiotimeline}[steps=4]
\studioevent{One}{Prepare.}
\studioevent{Two}{Check.}
\studioevent{Three}{Practice.}
\studioevent{Four}{Share.}
\end{studiotimeline}
\end{frame}
\begin{frame}{Two vertical events}
\begin{studiotimeline}[direction=vertical,steps=2]
\studioevent{First}{A description that has room to breathe.}
\studioevent{Second}{A second description.}
\end{studiotimeline}
\end{frame}
\studioimageframe[side=left]{A portrait image with a longer headline}{Short body text.}{\phone[height=8cm]}
\studioimageframe{A landscape image}{The default side resets.}{\asset[width=12cm]{cow-love}}
\studioquoteframe{A quotation without attribution.}{}
\studiostatframe{42}{}
\closingframe[title={See you soon!},subtitle={},copyright={}]
\closingframe[title={},subtitle={Discussion},copyright={\textcopyright{} 2030, Example Group}]
\closingframe
\begin{frame}[fragile]{Normal frame after closing}
\begin{verbatim}
print("Studio supports ordinary Beamer code frames")
\end{verbatim}
\end{frame}
\end{document}
"""
            (root / 'studio-components.tex').write_text(components, encoding='utf-8')
            library_components = r"""\documentclass[aspectratio=169]{beamer}
\usetheme{bitpolito-studio}
\usepackage{bitpolitostudiotemplates}
\begin{document}
\studiorailframe[blue]{A longer\\workshop\\checklist}{%
\studiorailitem{Choose one question}{Keep the example focused.}
\studiorailitem{Prepare a small demonstration}{Make every step visible.}
\studiorailitem{Test the result}{Compile without network access.}
\studiorailitem{Write the explanation}{Use clear, editable text.}
\studiorailitem{Share the files}{}
}
\studiorailframe{Options reset}{\studiorailitem{A light canvas}{The preceding blue choice stays local.}}
\studioglowframe{A wrapped\\statement.}
\studioquotecardframe{A quotation without a credit.}{}
\studiospotlightframe[blue]{\includegraphics[height=4cm]{images/studio/alice-white.pdf}}{}
\studiosidebysideframe{First comparison\\heading}{A short body.}{Second comparison\\heading}{Another short body.}
\studiotemplate{code}
\studiotemplate{line-chart}
\begin{frame}{A normal frame after the library}
Text uses the regular Studio foreground and background.
\end{frame}
\end{document}
"""
            registry = (root / 'templates/studio/registry.tex').read_text(encoding='utf-8')
            for name in ('code', 'line-chart'):
                if r'\DeclareStudioTemplate{' + name + '}' not in registry:
                    library_components = library_components.replace(r'\studiotemplate{' + name + '}', '')
            (root / 'studio-library-components.tex').write_text(library_components, encoding='utf-8')
        for document in (*document_sources(style), *variants):
            result = subprocess.run([
                shutil.which('latexmk'), '-pdf', '-outdir=build', document,
            ], cwd=root, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
            if result.returncode:
                raise RuntimeError(f'{document} failed in the extracted archive:\n{result.stdout[-8000:]}')
            stem = Path(document).stem
            log = (root / 'build' / (stem + '.log')).read_text(encoding='utf-8', errors='replace')
            for failure in ('Undefined control sequence', 'LaTeX Error', 'Missing character:', 'Overfull', 'Underfull', 'There were undefined references', 'Package bitpolitoassets Warning', 'Please (re)run Biber'):
                if failure in log:
                    raise RuntimeError(f'{document}: {failure}')
            if not (root / 'build' / (stem + '.pdf')).is_file():
                raise RuntimeError(f'{document}: PDF output is missing')
            for line in (root / 'build' / (stem + '.fls')).read_text(encoding='utf-8', errors='replace').splitlines():
                if line.startswith('INPUT '):
                    source = Path(line[6:])
                    source = (source if source.is_absolute() else root / source).resolve()
                    if style == 'studio' and source.name in (
                            'beamerthemebitpolito.sty', 'beamerinnerthemebitpolito.sty',
                            'beamerouterthemebitpolito.sty', 'beamerthemebitpolito-academic.sty'):
                        raise RuntimeError(f'{document} loads an academic layout: {source}')
                    if source.is_relative_to(CHECKOUT) and not source.is_relative_to(root):
                        raise RuntimeError(f'{document} depends on a source-checkout file: {source}')
            print(f'Isolated archive build passed: {document}', flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, help='Archive path; defaults to the selected style in dist/')
    parser.add_argument('--style', choices=(*STYLES, 'all'), default='academic')
    parser.add_argument('--backend', choices=('native', 'docker'), default='docker')
    parser.add_argument('--image', default=os.environ.get('LATEX_IMAGE', 'bitbeamer-latex:local'))
    args = parser.parse_args(argv)
    try:
        if args.style == 'all':
            if args.archive is not None:
                raise ValueError('--style all uses the standard archives in dist/.')
            for selected in STYLES:
                status = main([str(CHECKOUT / 'dist' / ARCHIVES[selected]), '--style', selected,
                               '--backend', args.backend, '--image', args.image])
                if status:
                    return status
            return 0
        archive = (args.archive or CHECKOUT / 'dist' / ARCHIVES[args.style]).resolve(strict=True)
        if args.backend == 'docker':
            docker = docker_image(CHECKOUT, args.image)
            command = [docker, 'run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp']
            if sys.platform != 'win32' and hasattr(os, 'getuid'):
                command += ['--user', f'{os.getuid()}:{os.getgid()}']
            command += ['--mount', f'type=bind,source={CHECKOUT},target=/source,readonly',
                        '--mount', f'type=bind,source={archive},target=/release.zip,readonly',
                        '--workdir', '/source', '--entrypoint', 'python3', args.image,
                        'scripts/validate-release.py', '/release.zip', '--backend', 'native']
            if args.style != 'academic':
                command += ['--style', args.style]
            subprocess.run(command, check=True)
        else:
            if args.style == 'academic':
                validate(archive)
            else:
                validate(archive, style=args.style)
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Release validation failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
