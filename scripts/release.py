"""Build and validate local release artifacts; never commit, tag or publish."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import build
from package import DOCUMENT_SOURCES, package
from asset_catalogue import check_catalogue
from asset_library import check_prepared
from doc_checks import check_docs

ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = {
    'main.pdf': 'bitbeamer-preview.pdf',
    'assets-example.pdf': 'bitbeamer-illustrations.pdf',
    'asset-catalogue.pdf': 'bitbeamer-catalogue.pdf',
    'icon-cheatsheet.pdf': 'bitbeamer-icon-cheatsheet.pdf',
    'cover-layouts.pdf': 'bitbeamer-cover-layouts.pdf',
}


def release(root=ROOT, backend='native', image=None):
    root = root.resolve()
    check_docs(root)
    check_prepared(root)
    check_catalogue(root)
    for document in DOCUMENT_SOURCES.values():
        arguments = [document, '--backend', backend]
        if image:
            arguments += ['--image', image]
        if build.main(arguments, root=root):
            raise RuntimeError(f'Release stopped: {document} did not compile.')
    # Validate a staged ZIP before replacing any successful release files.
    destination = root / 'dist'
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / 'bitbeamer-overleaf.zip'
    with tempfile.TemporaryDirectory(prefix='.bitbeamer-release-', dir=destination) as temporary:
        stage = Path(temporary)
        prepared = package(root, stage / archive.name)
        command = [sys.executable, str(root / 'scripts/validate-release.py'),
                   str(prepared), '--backend', backend]
        if image:
            command += ['--image', image]
        subprocess.run(command, cwd=root, check=True)
        # Stage every preview before promoting the validated set.
        for source, target in PREVIEWS.items():
            shutil.copyfile(root / 'build' / source, stage / target)
        for name in (archive.name, *PREVIEWS.values()):
            (stage / name).replace(destination / name)
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=('native', 'docker'), default='native')
    parser.add_argument('--image', default=os.environ.get('LATEX_IMAGE'))
    args = parser.parse_args()
    try:
        archive = release(backend=args.backend, image=args.image)
        print(f'Release verified: {archive}', flush=True)
        print('PDF previews: ' + ', '.join(PREVIEWS.values()), flush=True)
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Release failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
