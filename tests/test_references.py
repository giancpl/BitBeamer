"""Check offline navigation and references generated from the active asset library."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from asset_catalogue import catalogue_files, check_catalogue
from doc_checks import check_docs

class ReferenceTests(unittest.TestCase):
    def test_catalogue_tracks_unindexed_additions_and_removed_artwork(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / 'assets/objects'
            assets.mkdir(parents=True)
            source = assets / 'new-icon.svg'
            source.write_text('<svg/>')
            (root / 'assets/index.json').write_text(json.dumps([
                {'name': 'old-icon', 'description': 'Removed artwork'},
                {'name': 'new-icon', 'description': 'A useful icon', 'original': 'Original.svg'}]))
            files = catalogue_files(root)
            self.assertIn(b'A useful icon', files['assets/CATALOGUE.md'])
            self.assertIn(b'Original.svg', files['assets/CATALOGUE.md'])
            self.assertNotIn(b'old-icon', files['examples/asset-catalogue.tex'])
            for name, content in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            stamps = {name: (root / name).stat().st_mtime_ns for name in files}
            self.assertEqual(check_catalogue(root), 2)
            for name, stamp in stamps.items():
                self.assertEqual((root / name).stat().st_mtime_ns, stamp)
            (assets / 'unindexed.svg').write_text('<svg/>')
            self.assertIn(b'unindexed', catalogue_files(root)['examples/asset-catalogue.tex'])
            with self.assertRaisesRegex(RuntimeError, 'stale'):
                check_catalogue(root)
            self.assertEqual((root / 'examples/asset-catalogue.tex').read_bytes(), files['examples/asset-catalogue.tex'])
            source.unlink()
            self.assertNotIn(b'new-icon', catalogue_files(root)['examples/asset-catalogue.tex'])

    def test_all_live_icons_have_copyable_commands(self):
        from asset_library import inspect_library
        files = catalogue_files(ROOT)
        for name in inspect_library(ROOT)[0]:
            command = ('\\asset{' + name + '}').encode()
            self.assertIn(command, files['assets/CATALOGUE.md'])
            self.assertIn(command, files['examples/asset-catalogue.tex'])

    def test_offline_links_accept_files_anchors_references_and_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'docs/with spaces.txt').write_text('target')
            (root / 'README.md').write_text(
                '[file](docs/with%20spaces.txt#section)\n'
                '[reference]: <docs/with spaces.txt>\n'
                '[online](https://example.invalid/unreachable)\n'
                '[anchor](#heading)\n'
                '`[example](missing.txt)`\n'
                '```md\n[example](missing.txt)\n```\n')
            (root / 'build').mkdir()
            (root / 'build/ignored.md').write_text('[missing](missing.txt)')
            self.assertEqual(check_docs(root), 1)

    def test_broken_document_and_image_links_report_locations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[missing](gone.md)\n![image](gone.png)\n')
            with self.assertRaises(RuntimeError) as error:
                check_docs(root)
            self.assertIn('README.md:1', str(error.exception))
            self.assertIn('README.md:2', str(error.exception))

if __name__ == '__main__':
    unittest.main()
