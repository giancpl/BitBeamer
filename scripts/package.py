"""Create a minimal, self-contained Overleaf ZIP from prepared artwork."""

import argparse
from pathlib import Path
import sys
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from asset_library import check_prepared, inspect_library
from asset_catalogue import check_catalogue

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_SOURCES = {
    'main.tex': 'main.tex',
    'assets-example.tex': 'examples/assets-example.tex',
    'asset-catalogue.tex': 'examples/asset-catalogue.tex',
    'icon-cheatsheet.tex': 'examples/icon-cheatsheet.tex',
    'cover-layouts.tex': 'examples/cover-layouts.tex',
}
DOCUMENTS = tuple(DOCUMENT_SOURCES)
THEME_FILES = (
    'beamerthemebitpolito.sty', 'beamerinnerthemebitpolito.sty',
    'beamerouterthemebitpolito.sty', 'beamercolorthemebitpolito.sty',
    'beamerfontthemebitpolito.sty', 'bitpolitoassets.sty',
)
# A fixed list keeps unused PDFs and local experiments out of release downloads.
BRAND_FILES = (
    'logo-white.pdf', 'bull-white.pdf', 'monogram-white.pdf', 'bitcoin-white.pdf',
    'polito-coat-of-arms-white.pdf', 'crypto-primary-white.pdf',
    'crypto-symbol-white.pdf', 'first-page-background.pdf', 'LICENSE',
)


def package(root=ROOT, target=None):
    root = root.resolve()
    check_prepared(root)
    check_catalogue(root)
    _, records, _, _ = inspect_library(root)
    target = Path(target) if target else root / 'dist/bitbeamer-overleaf.zip'
    files = {name: root / source for name, source in DOCUMENT_SOURCES.items()}
    files.update({name: root / name for name in (*THEME_FILES, 'bibliography.bib', 'LICENSE', '.latexmkrc')})
    files['README.md'] = root / 'docs/OVERLEAF.md'
    files['ICONS.md'] = root / 'docs/ICONS.md'
    for name in BRAND_FILES:
        path = root / 'images/bitpolito' / name
        files[path.relative_to(root).as_posix()] = path
    files['assets/generated/catalogue.tex'] = root / 'assets/generated/catalogue.tex'
    for record in records.values():
        path = root / 'assets/generated' / record['output']
        files[path.relative_to(root).as_posix()] = path
    # Read everything before creating the archive, so incomplete inputs fail cleanly.
    data = {name: path.read_bytes() for name, path in files.items()}
    data['ICONS.md'] = data['ICONS.md'].replace(b'../assets/CATALOGUE.md', b'asset-catalogue.tex')
    data['ICONS.md'] = data['ICONS.md'].replace(b'../examples/icon-cheatsheet.tex', b'icon-cheatsheet.tex')
    data['ICONS.md'] = data['ICONS.md'].replace(b'(ASSETS.md)', b'(README.md)')
    # Adapt the icon guide to the flattened archive layout.
    data['ICONS.md'] = data['ICONS.md'].replace(
        b'python3 scripts/build.py examples/icon-cheatsheet.tex', b'latexmk -pdf icon-cheatsheet.tex')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.tmp')
    try:
        # Prepared PDFs are compact; storing entries avoids zlib-version differences.
        with ZipFile(temporary, 'w', ZIP_STORED) as archive:
            for name, content in sorted(data.items()):
                info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_STORED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, content)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        print(package(target=args.output))
    except (OSError, RuntimeError, ValueError) as error:
        print(f'Packaging failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
