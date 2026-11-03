"""Build and validate local release artifacts; never commit, tag or publish."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import build
from package import ARCHIVES, LEGACY_ARCHIVE, STYLES, DOCUMENT_SOURCES, package
from studio_assets import prepare_studio
from studio_templates import prepare_catalogue
from asset_catalogue import check_catalogue
from asset_library import check_prepared
from doc_checks import check_docs

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PREVIEW = 'bitbeamer-preview.pdf'
STUDIO_PREVIEWS = {
    'main-studio.pdf': 'bitbeamer-studio-preview.pdf',
    'studio-selected-templates.pdf': 'bitbeamer-studio-templates.pdf',
}
PREVIEWS = {
    'main-academic.pdf': 'bitbeamer-academic-preview.pdf',
    'assets-example.pdf': 'bitbeamer-illustrations.pdf',
    'asset-catalogue.pdf': 'bitbeamer-catalogue.pdf',
    'icon-cheatsheet.pdf': 'bitbeamer-icon-cheatsheet.pdf',
    'cover-layouts.pdf': 'bitbeamer-cover-layouts.pdf',
}


def release(root=ROOT, backend='docker', image=None, style='all', review=False):
    root = root.resolve()
    if style not in (*STYLES, 'all'):
        raise ValueError('Unknown release style: ' + style)
    styles = STYLES if style == 'all' else (style,)
    if 'studio' in styles and not review:
        from studio_review import require_approved
        require_approved(root)
    check_docs(root)
    check_prepared(root)
    check_catalogue(root)
    if 'studio' in styles:
        prepare_studio(root, check=True)
        prepare_catalogue(root, check=True)
    documents = list(dict.fromkeys(DOCUMENT_SOURCES.values())) if 'academic' in styles else []
    previews = dict(PREVIEWS) if 'academic' in styles else {}
    if 'studio' in styles:
        documents += ['main-studio.tex', 'examples/studio-selected-templates.tex']
        previews.update(STUDIO_PREVIEWS)
    for document in documents:
        arguments = [document, '--backend', backend]
        if image:
            arguments += ['--image', image]
        if build.main(arguments, root=root):
            raise RuntimeError(f'Release stopped: {document} did not compile.')
    # Stage and validate every selected style before promoting any release file.
    destination = root / ('build/review/release' if review else 'dist')
    destination.mkdir(parents=True, exist_ok=True)
    archives = [destination / ARCHIVES[item] for item in styles]
    with tempfile.TemporaryDirectory(prefix='.bitbeamer-release-', dir=destination) as temporary:
        stage = Path(temporary)
        for selected, archive in zip(styles, archives):
            prepared = package(root, stage / archive.name, style=selected, review=review)
            command = [sys.executable, str(root / 'scripts/validate-release.py'),
                       str(prepared), '--style', selected, '--backend', backend]
            if image:
                command += ['--image', image]
            subprocess.run(command, cwd=root, check=True)
        for source, target in previews.items():
            shutil.copyfile(root / 'build' / source, stage / target)
        outputs = [archive.name for archive in archives] + list(previews.values())
        if 'academic' in styles:
            # Compatibility downloads are copied from the very same validated bytes.
            shutil.copyfile(stage / ARCHIVES['academic'], stage / LEGACY_ARCHIVE)
            shutil.copyfile(stage / 'bitbeamer-academic-preview.pdf', stage / LEGACY_PREVIEW)
            outputs += [LEGACY_ARCHIVE, LEGACY_PREVIEW]
        for name in outputs:
            (stage / name).replace(destination / name)
    return archives[0] if len(archives) == 1 else tuple(archives)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style', choices=(*STYLES, 'all'), default='all')
    parser.add_argument('--backend', choices=('native', 'docker'), default='docker')
    parser.add_argument('--image', default=os.environ.get('LATEX_IMAGE'))
    parser.add_argument('--review', action='store_true', help='Validate unapproved candidates under build/review/release; preserve dist/')
    args = parser.parse_args()
    try:
        archive = release(backend=args.backend, image=args.image, style=args.style, review=args.review)
        for path in archive if isinstance(archive, tuple) else (archive,):
            print(f'Release verified: {path}', flush=True)
        print('Verified PDF previews are in ' + ('build/review/release/.' if args.review else 'dist/.'), flush=True)
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Release failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
