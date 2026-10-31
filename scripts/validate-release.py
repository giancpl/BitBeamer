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

from package import DOCUMENTS
from build import docker_image

CHECKOUT = Path(__file__).resolve().parents[1]


def select_theme(source, options):
    result, count = re.subn(
        r'(?m)^\\usetheme(?:\[[^\]]*\])?\{bitpolito\}',
        lambda match: '\\usetheme[' + options + ']{bitpolito}', source, count=1)
    if count != 1:
        raise RuntimeError('Cannot select theme options: missing BitPolito theme declaration')
    return result


def validate(archive):
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
        for document in (*DOCUMENTS, *variants):
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
                    if source.is_relative_to(CHECKOUT) and not source.is_relative_to(root):
                        raise RuntimeError(f'{document} depends on a source-checkout file: {source}')
            print(f'Isolated archive build passed: {document}', flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, default=Path(__file__).resolve().parents[1] / 'dist/bitbeamer-overleaf.zip')
    parser.add_argument('--backend', choices=('native', 'docker'), default='docker')
    parser.add_argument('--image', default=os.environ.get('LATEX_IMAGE', 'bitbeamer-latex:local'))
    args = parser.parse_args(argv)
    try:
        archive = args.archive.resolve(strict=True)
        if args.backend == 'docker':
            docker = docker_image(CHECKOUT, args.image)
            command = [docker, 'run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp']
            if sys.platform != 'win32' and hasattr(os, 'getuid'):
                command += ['--user', f'{os.getuid()}:{os.getgid()}']
            command += ['--mount', f'type=bind,source={CHECKOUT},target=/source,readonly',
                        '--mount', f'type=bind,source={archive},target=/release.zip,readonly',
                        '--workdir', '/source', '--entrypoint', 'python3', args.image,
                        'scripts/validate-release.py', '/release.zip', '--backend', 'native']
            subprocess.run(command, check=True)
        else:
            validate(archive)
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Release validation failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
