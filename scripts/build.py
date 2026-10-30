"""Portable native LaTeX launcher. Docker is used only with --backend docker."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import webbrowser

from asset_library import check_prepared

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ('latexmk', 'pdflatex', 'biber')


def install_help(platform=None):
    platform = platform or sys.platform
    if platform == 'win32':
        return ('On Windows, install Python 3 and TeX Live (including latexmk and Biber) from '
                'https://tug.org/texlive/windows.html, then restart your IDE/terminal. '
                'See docs/SETUP.md for PATH checks.')
    if platform == 'darwin':
        return ('Install MacTeX from https://tug.org/mactex/ and add '
                '/Library/TeX/texbin to PATH, then restart your IDE/terminal.')
    return ('Install TeX Live, latexmk, and Biber. Debian/Ubuntu: sudo apt-get install '
            'latexmk texlive-latex-extra texlive-fonts-recommended texlive-bibtex-extra biber. '
            'Fedora: see docs/SETUP.md. Restart your IDE/terminal after updating PATH.')


def native_tools():
    missing = [tool for tool in TOOLS if not shutil.which(tool)]
    if missing:
        raise RuntimeError('Missing native tools: ' + ', '.join(missing) + '.\n'
                           + install_help() + '\nDocker is optional: explicitly use --backend docker.')
    return shutil.which('latexmk')


def docker_image(root, image):
    docker = shutil.which('docker')
    if not docker:
        raise RuntimeError('Docker was explicitly selected but is not installed. Install Docker or use native TeX Live.')
    probe = subprocess.run([docker, 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode:
        raise RuntimeError('Cannot access Docker. Start Docker and check your user permissions.')
    probe = subprocess.run([docker, 'image', 'inspect', image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode:
        subprocess.run([docker, 'build', '-t', image, '.'], cwd=root, check=True)
    return docker


def docker_command(docker, root, output, document, image, force=False):
    command = [docker, 'run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp']
    if sys.platform != 'win32' and hasattr(os, 'getuid'):
        command += ['--user', f'{os.getuid()}:{os.getgid()}']
    command += ['--workdir', '/source',
                '--mount', f'type=bind,source={root},target=/source,readonly',
                '--mount', f'type=bind,source={output},target=/output',
                image, '-pdf', '-outdir=/output']
    if force:
        command.append('-g')
    return command + ['./' + document.as_posix()]


def main(argv=None, root=None):
    root = (root or ROOT).resolve()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', nargs='?', default='main.tex')
    parser.add_argument('output', nargs='?', default='build')
    parser.add_argument('--backend', choices=('native', 'docker'), default='native')
    parser.add_argument('--image', default=os.environ.get('LATEX_IMAGE', 'bitbeamer-latex:local'))
    parser.add_argument('--setup', action='store_true', help='Check dependencies without compiling')
    parser.add_argument('--force', '-g', action='store_true', help='Force latexmk to rebuild')
    parser.add_argument('--open', action='store_true', help='Open the compiled PDF in the default viewer')
    args = parser.parse_args(argv)
    try:
        document = Path(args.document)
        if not document.is_absolute():
            document = root / document
        document = document.resolve()
        if not document.is_file() or document.suffix.lower() != '.tex':
            raise RuntimeError(f'TeX document not found: {document}')
        try:
            relative = document.relative_to(root)
        except ValueError as error:
            raise RuntimeError('The document must be inside the project.') from error
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        output = output.resolve()
        count = check_prepared(root)
        tool = native_tools() if args.backend == 'native' else docker_image(root, args.image)
        print(f'Ready: {args.backend} compiler; {count} prepared assets.', flush=True)
        if args.setup:
            return 0
        output.mkdir(parents=True, exist_ok=True)
        if args.backend == 'native':
            command = [tool, '-pdf', '-outdir=' + output.as_posix()]
            if args.force:
                command.append('-g')
            command.append('./' + relative.as_posix())
        else:
            command = docker_command(tool, root, output, relative, args.image, args.force)
        subprocess.run(command, cwd=root, check=True)
        pdf = output / (document.stem + '.pdf')
        print(f'PDF: {pdf}', flush=True)
        if args.open:
            if sys.platform == 'win32':
                os.startfile(str(pdf))
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(pdf)], check=True)
            elif shutil.which('xdg-open'):
                subprocess.run(['xdg-open', str(pdf)], check=True)
            else:
                webbrowser.open(pdf.as_uri())
        return 0
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
