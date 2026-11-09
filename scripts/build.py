"""Portable LaTeX launcher. Docker is the default; native TeX is opt-in."""

import argparse
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import webbrowser

from asset_library import check_prepared
from studio_assets import prepare_studio

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
            'latexmk texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-lang-greek texlive-bibtex-extra biber. '
            'Fedora: see docs/SETUP.md. Restart your IDE/terminal after updating PATH.')


def native_tools():
    missing = [tool for tool in TOOLS if not shutil.which(tool)]
    if missing:
        raise RuntimeError('Missing native tools: ' + ', '.join(missing) + '.\n'
                           + install_help() + '\nUse --backend docker to compile in the configured container instead.')
    return shutil.which('latexmk')


def docker_image(root, image):
    docker = shutil.which('docker')
    if not docker:
        raise RuntimeError('Docker is the default compiler but is not installed. Install and start Docker, or use --backend native with TeX Live/MacTeX; see docs/SETUP.md.')
    probe = subprocess.run([docker, 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode:
        raise RuntimeError('Cannot access Docker. Start Docker and check your user permissions, or use --backend native with an installed TeX distribution.')
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




def resolve_tex_root(root, document):
    """Follow editor root comments when a build task targets an included TeX file."""
    visited = set()
    while True:
        document = document.resolve()
        if not document.is_relative_to(root):
            raise RuntimeError('The document must be inside the project.')
        if document in visited:
            raise RuntimeError('Cyclic TeX root comments: ' + str(document))
        visited.add(document)
        if not document.is_file() or document.suffix.lower() != '.tex':
            raise RuntimeError('TeX document not found: ' + str(document))
        header = '\n'.join(document.read_text(encoding='utf-8').splitlines()[:30])
        match = re.search(r'^\s*%\s*!TEX\s+root\s*=\s*(.+?)\s*$', header, re.I | re.M)
        if not match:
            return document
        name = match[1]
        if len(name) > 1 and name[0] == name[-1] and name[0] in ('"', "'"):
            name = name[1:-1]
        target = (document.parent / name).resolve()
        if target == document:
            return document
        document = target


def open_pdf(pdf):
    """Reuse the VS Code preview in editor sessions; otherwise use the system viewer."""
    in_editor = (os.environ.get('TERM_PROGRAM') == 'vscode'
                 or os.environ.get('VSCODE_PID') or os.environ.get('VSCODE_IPC_HOOK_CLI'))
    if in_editor:
        code = next((value for name in ('code', 'code-insiders', 'codium')
                     if (value := shutil.which(name))), None)
        if code:
            command = [code, '--reuse-window', str(pdf.resolve())]
            kwargs = {}
            if sys.platform == 'win32' and Path(code).suffix.lower() in ('.cmd', '.bat'):
                # Invoke the shipped CLI through Electron directly, without a
                # batch shell interpreting special characters in project paths.
                install = Path(code).resolve().parent.parent
                cli = install / 'resources/app/out/cli.js'
                executable = next((install / name for name in ('Code.exe', 'Code - Insiders.exe', 'VSCodium.exe')
                                   if (install / name).is_file()), None)
                if executable and cli.is_file():
                    command = [str(executable), str(cli), '--reuse-window', str(pdf.resolve())]
                    kwargs['env'] = dict(os.environ, ELECTRON_RUN_AS_NODE='1')
                else:
                    command = None
            if command:
                subprocess.run(command, check=True, **kwargs)
                return
    if sys.platform == 'win32':
        os.startfile(str(pdf))
    elif sys.platform == 'darwin':
        subprocess.run(['open', str(pdf)], check=True)
    elif shutil.which('xdg-open'):
        subprocess.run(['xdg-open', str(pdf)], check=True)
    else:
        webbrowser.open(pdf.as_uri())


def compile_preserving_pdf(command, root, pdf):
    """Keep the last successful PDF when a new compilation fails or is cancelled."""
    with tempfile.TemporaryDirectory(prefix='.bitbeamer-pdf-', dir=pdf.parent) as temporary:
        previous = Path(temporary) / pdf.name
        if pdf.is_file():
            shutil.copy2(pdf, previous)
        try:
            subprocess.run(command, cwd=root, check=True)
        except (OSError, subprocess.CalledProcessError, KeyboardInterrupt):
            if previous.is_file():
                os.replace(previous, pdf)
                print(f'Kept last successful PDF: {pdf}', file=sys.stderr, flush=True)
            else:
                pdf.unlink(missing_ok=True)
            raise


def document_sources_text(root, document):
    """Inspect project-local TeX inputs, including a thin default entry point."""
    pending = [document]
    visited = set()
    texts = []
    while pending:
        source = pending.pop().resolve()
        if source in visited or not source.is_relative_to(root) or not source.is_file():
            continue
        visited.add(source)
        text = source.read_text(encoding='utf-8')
        texts.append(text)
        for name in re.findall(r'\\(?:input|include)\s*\{([^{}\n]+)\}', text):
            if any(token in name for token in ('\\', '#')):
                continue
            relative = Path(name)
            if not relative.suffix:
                relative = relative.with_suffix('.tex')
            candidates = [source.parent / relative, root / relative]
            local = next((path for path in candidates if path.is_file()), None)
            if local is not None:
                pending.append(local)
    return '\n'.join(texts)


def main(argv=None, root=None):
    root = (root or ROOT).resolve()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', nargs='?', default='main.tex')
    parser.add_argument('output', nargs='?', help='Output directory (personal decks are isolated automatically)')
    parser.add_argument('--backend', choices=('native', 'docker'), default='docker')
    parser.add_argument('--image', default=os.environ.get('LATEX_IMAGE', 'bitbeamer-latex:local'))
    parser.add_argument('--setup', action='store_true', help='Prepare the selected backend without compiling (builds a missing Docker image)')
    parser.add_argument('--force', '-g', action='store_true', help='Force latexmk to rebuild')
    parser.add_argument('--open', action='store_true', help='Open or reveal the PDF in VS Code when running there, otherwise the system viewer')
    args = parser.parse_args(argv)
    try:
        document = Path(args.document)
        if not document.is_absolute():
            document = root / document
        document = resolve_tex_root(root, document)
        if not document.is_file() or document.suffix.lower() != '.tex':
            raise RuntimeError(f'TeX document not found: {document}')
        try:
            relative = document.relative_to(root)
        except ValueError as error:
            raise RuntimeError('The document must be inside the project.') from error
        personal = len(relative.parts) >= 3 and relative.parts[0] == 'presentations'
        default_output = Path('build/presentations') / relative.parts[1] if personal else Path('build')
        output = Path(args.output) if args.output else default_output
        if not output.is_absolute():
            output = root / output
        output = output.resolve()
        count = check_prepared(root)
        source_text = document_sources_text(root, document)
        if 'bitpolito-studio' in source_text:
            prepare_studio(root, check=True)
        if any(package in source_text for package in ('bitpolitostudiopilots', 'bitpolitostudiotemplates')) and (root / 'images/studio/parts/manifest.json').is_file():
            from studio_parts import prepare as check_studio_parts
            check_studio_parts(root, check=True)
        if any(package in source_text for package in ('bitpolitostudiopilots', 'bitpolitostudiotemplates')) and (root / 'images/studio/collection/manifest.json').is_file():
            from studio_collection import prepare as check_collection
            check_collection(root, check=True)
            from studio_slots import prepare as check_slots
            check_slots(root, check=True)
            from studio_palettes import check as check_palettes
            check_palettes(root)
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
        pdf = output / (document.stem + '.pdf')
        compile_preserving_pdf(command, root, pdf)
        print(f'PDF: {pdf}', flush=True)
        if args.open:
            open_pdf(pdf)
        return 0
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
