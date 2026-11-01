"""Studio artwork freshness checks must be offline and read-only."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from studio_assets import SOURCES, prepare_studio


class StudioAssetTests(unittest.TestCase):
    def test_prepared_derivatives_are_current_without_rewriting_sources(self):
        paths = [ROOT / name for name in SOURCES.values()]
        paths += list((ROOT / 'images/studio').rglob('*'))
        before = {path: path.read_bytes() for path in paths if path.is_file()}
        self.assertEqual(prepare_studio(ROOT, check=True), 4)
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_changed_source_or_missing_pdf_is_reported_without_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'images/studio', root / 'images/studio')
            for relative in SOURCES.values():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            self.assertEqual(prepare_studio(root, check=True), 4)
            target = root / next(iter(SOURCES.values()))
            target.write_bytes(target.read_bytes() + b'<!-- edit -->')
            with self.assertRaisesRegex(RuntimeError, 'missing or stale'):
                prepare_studio(root, check=True)
            target.write_bytes((ROOT / next(iter(SOURCES.values()))).read_bytes())
            (root / 'images/studio/alice-white.pdf').unlink()
            with self.assertRaisesRegex(RuntimeError, 'missing or stale'):
                prepare_studio(root, check=True)

    def test_white_cover_preserves_the_authored_canvas_and_transparency(self):
        original = ET.fromstring((ROOT / SOURCES['cover-pattern']).read_bytes())
        prepared = ET.fromstring((ROOT / 'images/studio/source/cover-pattern-white.svg').read_bytes())
        for attribute in ('width', 'height', 'viewBox'):
            self.assertEqual(prepared.get(attribute), original.get(attribute))
        self.assertEqual(prepared.get('fill'), 'none')
        paints = [e.get('fill') for e in prepared.iter() if e.get('fill') not in (None, 'none')]
        self.assertTrue(paints)
        self.assertEqual(set(paints), {'#FFFFFF'})
        self.assertEqual([e.tag for e in original.iter()], [e.tag for e in prepared.iter()])


if __name__ == '__main__':
    unittest.main()
