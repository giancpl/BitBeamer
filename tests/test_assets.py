"""Exercise the artwork pipeline with real files in temporary projects."""

import base64
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'prepare-assets.py'
sys.path.insert(0, str(ROOT / 'scripts'))
import asset_library
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60"><rect width="100" height="60" fill="{}"/></svg>'
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1ioAAAAASUVORK5CYII=')


class AssetPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = self.root / 'assets' / 'characters'
        self.sources.mkdir(parents=True)
        self.output = self.root / 'assets' / 'generated'

    def prepare(self, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--root', str(self.root)],
            capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_native_files_are_preserved_and_removed_assets_leave_catalogue(self):
        source = self.sources / 'alice.pdf'
        shutil.copyfile(ROOT / 'images/bitpolito/bull-blue.pdf', source)
        (self.sources / 'bitcoin.png').write_bytes(PNG)
        self.prepare()
        self.assertEqual((self.output / 'alice.pdf').read_bytes(), source.read_bytes())
        self.assertEqual((self.output / 'bitcoin.png').read_bytes(), PNG)
        catalogue = (self.output / 'catalogue.tex').read_text()
        self.assertIn(r'\DeclareBitPolitoAsset{alice}{alice.pdf}', catalogue)
        stamp = (self.output / 'alice.pdf').stat().st_mtime_ns
        self.prepare()
        self.assertEqual((self.output / 'alice.pdf').stat().st_mtime_ns, stamp)
        source.unlink()
        self.prepare()
        self.assertNotIn('alice', (self.output / 'catalogue.tex').read_text())
        self.assertFalse((self.output / 'alice.pdf').exists())
        self.assertTrue((self.sources / 'bitcoin.png').exists())

    @unittest.skipUnless(asset_library.converter_available(), 'An SVG converter is required')
    def test_viewbox_only_svg_converts_and_content_changes_refresh_pdf(self):
        source = self.sources / 'cow.svg'
        source.write_text(SVG.format('#001CE0'))
        self.prepare()
        original = (self.output / 'cow.pdf').read_bytes()
        self.assertTrue(original.startswith(b'%PDF-'))
        source.write_text(SVG.format('#FFFFFF'))
        self.prepare()
        self.assertNotEqual((self.output / 'cow.pdf').read_bytes(), original)
        manifest = json.loads((self.output / 'manifest.json').read_text())
        self.assertEqual(manifest['cow']['source'], 'assets/characters/cow.svg')

    def test_duplicate_names_fail_without_changing_previous_catalogue(self):
        (self.sources / 'alice.png').write_bytes(PNG)
        self.prepare()
        before = (self.output / 'catalogue.tex').read_bytes()
        (self.sources / 'alice.svg').write_text(SVG.format('#001CE0'))
        result = self.prepare(success=False)
        self.assertIn('Duplicate asset name', result.stderr)
        self.assertEqual((self.output / 'catalogue.tex').read_bytes(), before)

    @unittest.skipUnless(shutil.which('pdfinfo') and asset_library.converter_available(), 'Poppler and an SVG converter are required')
    def test_svg_padding_is_trimmed_for_predictable_latex_sizing(self):
        (self.sources / 'padded.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">'
            '<rect x="400" y="500" width="20" height="30" fill="blue"/></svg>'
        )
        self.prepare()
        info = subprocess.check_output(['pdfinfo', str(self.output / 'padded.pdf')], text=True)
        bounds = re.search(r'Page size:\s+([\d.]+) x ([\d.]+) pts', info)
        self.assertIsNotNone(bounds)
        width, height = (float(value) for value in bounds.groups())
        self.assertAlmostEqual(width / height, 2 / 3, places=4)
        self.assertLess(width, 100)
        # Cover/background artwork must optionally preserve its authored canvas.
        page = self.root / 'full-page.pdf'
        asset_library.render_svg(self.sources / 'padded.svg', page, crop=False)
        info = subprocess.check_output(['pdfinfo', str(page)], text=True)
        bounds = re.search(r'Page size:\s+([\d.]+) x ([\d.]+) pts', info)
        self.assertIsNotNone(bounds)
        page_width, page_height = (float(value) for value in bounds.groups())
        self.assertEqual(page_width, page_height)
        self.assertGreater(page_width, 10 * width)

    def test_read_only_check_needs_no_converter_and_does_not_write(self):
        (self.sources / 'alice.png').write_bytes(PNG)
        self.prepare()
        files = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.output.iterdir()}
        with mock.patch.object(asset_library, 'render_svg', side_effect=AssertionError('Must not convert')):
            self.assertEqual(asset_library.check_prepared(self.root), 1)
        for path, (data, stamp) in files.items():
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (data, stamp))
        (self.sources / 'alice.png').write_bytes(PNG + b'changed')
        with self.assertRaisesRegex(RuntimeError, 'stale or missing'):
            asset_library.check_prepared(self.root)

    def test_auto_converter_uses_inkscape_when_python_libraries_are_missing(self):
        source = self.sources / 'cow.svg'
        source.write_text(SVG.format('#001CE0'))
        target = self.root / 'cow.pdf'
        def exported(command, **kwargs):
            filename = next(arg.split('=', 1)[1] for arg in command if arg.startswith('--export-filename='))
            Path(filename).write_bytes(b'%PDF-1.5 test fixture')
        with mock.patch.object(asset_library, 'rsvg_modules', side_effect=RuntimeError('unavailable')), \
                mock.patch.object(asset_library, 'inkscape_executable', return_value='inkscape'), \
                mock.patch.object(asset_library.subprocess, 'run', side_effect=exported) as run:
            asset_library.render_svg(source, target)
        self.assertIn('--export-area-drawing', run.call_args.args[0])
        self.assertTrue(target.read_bytes().startswith(b'%PDF-'))

    def test_svg_line_endings_survive_git_normalization(self):
        source = self.sources / 'cow.svg'
        svg = (SVG.format('#001CE0') + '\n').encode('utf-8')
        source.write_bytes(svg.replace(b'\n', b'\r\n'))
        def render(original, target, converter):
            target.write_bytes(b'%PDF-1.5 fixture')
        with mock.patch.object(asset_library, 'render_svg', side_effect=render):
            asset_library.prepare(self.root)
        source.write_bytes(svg)
        self.assertEqual(asset_library.check_prepared(self.root), 1)

    @unittest.skipUnless(asset_library.inkscape_executable(), 'Inkscape is required')
    def test_inkscape_exports_vector_pdf(self):
        (self.sources / 'cow.svg').write_text(SVG.format('#001CE0'))
        asset_library.prepare(self.root, converter='inkscape')
        self.assertTrue((self.output / 'cow.pdf').read_bytes().startswith(b'%PDF-'))
        self.assertEqual(asset_library.check_prepared(self.root), 1)

    def test_unsafe_filename_is_rejected_before_generating_tex(self):
        (self.sources / 'bad%name.png').write_bytes(PNG)
        result = self.prepare(success=False)
        self.assertIn('lowercase filename', result.stderr)
        self.assertFalse((self.output / 'catalogue.tex').exists())


if __name__ == '__main__':
    unittest.main()
