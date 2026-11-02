"""Ensure the release download stays independent of developer tools."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import asset_library
from doc_checks import check_docs
import package


class PackageTests(unittest.TestCase):
    def test_release_contains_ready_assets_and_no_development_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'template.zip'
            before = {path: path.stat().st_mtime_ns for path in (ROOT / 'assets/generated').iterdir()}
            with mock.patch.object(asset_library, 'render_svg', side_effect=AssertionError('Must not convert')), \
                    mock.patch('zipfile.zlib', None):
                package.package(ROOT, target)
            first = target.read_bytes()
            package.package(ROOT, target)
            self.assertEqual(first, target.read_bytes(), 'Packaging should be reproducible')
            for path, stamp in before.items():
                self.assertEqual(path.stat().st_mtime_ns, stamp)
            with ZipFile(target) as archive:
                names = archive.namelist()
                self.assertIsNone(archive.testzip())
                self.assertTrue(set(package.DOCUMENTS).issubset(names))
                self.assertIn('bitpolitoassets.sty', names)
                self.assertIn('ICONS.md', names)
                self.assertIn('icon-cheatsheet.tex', names)
                for name, source in package.DOCUMENT_SOURCES.items():
                    self.assertEqual(archive.read(name), (ROOT / source).read_bytes())
                self.assertFalse(any(name.startswith('examples/') for name in names))
                self.assertEqual({name for name in names if name.startswith('images/bitpolito/')},
                                 {'images/bitpolito/' + name for name in package.BRAND_FILES})
                self.assertIn('assets/generated/catalogue.tex', names)
                self.assertIn('images/bitpolito/first-page-background.pdf', names)
                self.assertIn('images/bitpolito/polito-coat-of-arms-white.pdf', names)
                self.assertIn('images/bitpolito/crypto-primary-white.pdf', names)
                self.assertIn('images/bitpolito/crypto-symbol-white.pdf', names)
                self.assertIn('images/bitpolito/monogram-white.pdf', names)
                self.assertEqual(sum(name.startswith('assets/generated/') and name.endswith('.pdf') for name in names), 171)
                for name in names:
                    self.assertFalse(name.endswith(('.py', '.sh', '.svg', '.json')), name)
                    self.assertFalse(name.startswith(('scripts/', '.vscode/', '.github/')), name)
                    self.assertNotIn(Path(name).name, ('Dockerfile', 'Makefile', '.dockerignore'))
                self.assertIn('Overleaf template', archive.read('README.md').decode('utf-8'))
                self.assertNotIn('scripts/build.py', archive.read('README.md').decode('utf-8'))
                extracted = Path(directory) / 'extracted'
                archive.extractall(extracted)
            self.assertEqual(check_docs(extracted), 2, 'Release guides must link only to shipped files')

    def test_unlisted_local_files_are_excluded_and_missing_theme_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            # Reuse the library read-only while isolating the release file selection.
            root = Path(directory)
            sources = [*package.DOCUMENT_SOURCES.values(), *package.THEME_FILES,
                       'bibliography.bib', 'LICENSE', '.latexmkrc', 'docs/OVERLEAF.md', 'docs/ICONS.md']
            sources += ['images/bitpolito/' + name for name in package.BRAND_FILES]
            for name in sources:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            (root / 'images/bitpolito/local-experiment.pdf').write_bytes(b'%PDF-test')
            (root / 'beamerthemelocalbitpolito.sty').write_text('local experiment')
            records = asset_library.inspect_library(ROOT)[1]
            for record in records.values():
                source = ROOT / 'assets/generated' / record['output']
                target = root / 'assets/generated' / record['output']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            (root / 'assets/generated/catalogue.tex').write_bytes((ROOT / 'assets/generated/catalogue.tex').read_bytes())
            target = root / 'release.zip'
            with mock.patch.object(package, 'check_prepared'), \
                    mock.patch.object(package, 'check_catalogue'), \
                    mock.patch.object(package, 'inspect_library', return_value=asset_library.inspect_library(ROOT)):
                package.package(root, target)
                with ZipFile(target) as archive:
                    self.assertNotIn('images/bitpolito/local-experiment.pdf', archive.namelist())
                    self.assertNotIn('beamerthemelocalbitpolito.sty', archive.namelist())
                canonical = package.package(root)
                self.assertEqual(canonical.name, 'bitbeamer-academic-overleaf.zip')
                self.assertEqual((root / 'dist/bitbeamer-overleaf.zip').read_bytes(), canonical.read_bytes())
                previous = target.read_bytes()
                (root / package.THEME_FILES[0]).unlink()
                with self.assertRaises(FileNotFoundError):
                    package.package(root, target)
                self.assertEqual(target.read_bytes(), previous)

    def test_studio_archive_is_independent_and_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'studio.zip'
            package.package(ROOT, target, style='studio', review=True)
            first = target.read_bytes()
            package.package(ROOT, target, style='studio', review=True)
            self.assertEqual(first, target.read_bytes())
            with ZipFile(target) as archive:
                names = set(archive.namelist())
                self.assertTrue(set(package.STUDIO_THEME_FILES).issubset(names))
                self.assertTrue(set(package.STUDIO_DOCUMENT_SOURCES).issubset(names))
                self.assertFalse({'beamerthemebitpolito.sty', 'beamerinnerthemebitpolito.sty',
                                  'beamerouterthemebitpolito.sty', 'beamerthemebitpolito-academic.sty', 'cover-layouts.tex'} & names)
                self.assertEqual(archive.read('main.tex'), (ROOT / 'main-studio.tex').read_bytes())
                self.assertNotIn(b'main-studio.tex', archive.read('STUDIO.md'))
                self.assertNotIn(b'scripts/build.py', archive.read('STUDIO.md'))
                self.assertIn(b'latexmk -pdf main.tex', archive.read('STUDIO.md'))
                for name in ('assets-example.tex', 'asset-catalogue.tex'):
                    self.assertIn(b'\\usetheme{bitpolito-studio}', archive.read(name))
                    self.assertNotIn(b'\\usetheme{bitpolito}', archive.read(name))
                for name in package.STUDIO_ASSETS:
                    self.assertIn('images/studio/' + name, names)
                self.assertEqual(sum(name.startswith('assets/generated/') and name.endswith('.pdf') for name in names), 171)
                self.assertNotIn(b'scripts/build', archive.read('TEMPLATES.md'))
                self.assertNotIn(b'--previews', archive.read('TEMPLATES.md'))
                self.assertIn(b'latexmk -pdf studio-template-catalogue.tex', archive.read('TEMPLATES.md'))
                self.assertIn('studio-template-catalogue.tex', names)
                self.assertIn('templates/studio/registry.tex', names)
                self.assertEqual(sum(name.startswith('templates/studio/') and name.endswith('.tex') for name in names), 1 + len(__import__('studio_review').selected(ROOT)))
                self.assertFalse(any(name.startswith(('docs/templates/', 'design-references/')) for name in names))
                self.assertFalse(any(name.endswith(('.svg', '.py', '.json')) for name in names))
                extracted = Path(directory) / 'extracted'
                archive.extractall(extracted)
            self.assertEqual(check_docs(extracted), 5 + len(__import__('studio_review').selected(ROOT)))
            self.assertTrue((extracted / 'guides/three-cards.md').is_file())
            self.assertNotIn('Show editable areas', (extracted / 'guides/three-cards.md').read_text())


if __name__ == '__main__':
    unittest.main()
