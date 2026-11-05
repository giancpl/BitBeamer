"""Check template coverage, safe names, and read-only catalogue maintenance."""

import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import studio_templates


class StudioTemplateTests(unittest.TestCase):
    def isolated_library(self, directory):
        root = Path(directory)
        shutil.copytree(ROOT / 'templates', root / 'templates')
        return root

    def test_complete_catalogue_and_previews_are_ready_without_conversion(self):
        before = {path: path.stat().st_mtime_ns for path in (ROOT / 'templates').rglob('*') if path.is_file()}
        with mock.patch.object(studio_templates, 'render_previews', side_effect=AssertionError('Must not render')):
            self.assertEqual(studio_templates.prepare_catalogue(ROOT, check=True), len(studio_templates.inspect_templates(ROOT)))
        entries = studio_templates.inspect_templates(ROOT)
        self.assertEqual(entries[-1]['id'], 'closing')
        for entry in entries:
            self.assertEqual((ROOT / entry['source']).stat().st_mtime_ns, before[ROOT / entry['source']])
            png = (ROOT / 'docs/templates/previews' / (entry['id'] + '.png')).read_bytes()
            self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
            width, height = struct.unpack('>II', png[16:24])
            self.assertEqual(width, 480)
            self.assertIn(height, (270, 271), 'Poppler rounds the PDF page height to whole pixels')
            self.assertNotIn('design-references', (ROOT / entry['source']).read_text(encoding="utf-8"))

    def test_all_exports_have_unique_ids_and_traceable_dispositions(self):
        data = json.loads((ROOT / 'templates/figma-inventory.json').read_text(encoding="utf-8"))
        frames = data['frames']
        self.assertEqual(len(frames), 1073)
        self.assertEqual(len({frame['id'] for frame in frames}), 1073)
        self.assertEqual(len({frame['sha256'] for frame in frames}), 1005)
        self.assertEqual(sum(frame['format'] == 'slide' for frame in frames), 971)
        self.assertTrue(all(frame['review'] == 'contact-sheet' for frame in frames))
        by_id = {frame['id']: frame for frame in frames}
        for frame in frames:
            self.assertFalse(Path(frame['file']).is_absolute())
            if frame['disposition'] == 'exact-source-duplicate':
                self.assertEqual(frame['sha256'], by_id[frame['duplicate_of']]['sha256'])
            if 'visual_candidate_templates' in frame:
                self.assertIn('Automated', frame['match_status'])

    def test_missing_preset_is_reported_before_catalogue_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.isolated_library(directory)
            (root / 'templates/studio/cover.tex').unlink()
            with self.assertRaisesRegex(RuntimeError, 'Missing Studio template'):
                studio_templates.prepare_catalogue(root)
            self.assertFalse((root / 'examples').exists())

    def test_unsafe_name_and_unknown_reference_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.isolated_library(directory)
            index = root / 'templates/index.json'
            data = json.loads(index.read_text(encoding="utf-8"))
            data['templates'][0]['id'] = '../outside'
            index.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, 'Invalid or repeated'):
                studio_templates.inspect_templates(root)
            data['templates'][0]['id'] = 'cover'
            data['templates'][0]['references'] = ['figma-missing']
            index.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, 'Missing Figma reference'):
                studio_templates.inspect_templates(root)

    def test_stale_registry_check_does_not_repair_or_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.isolated_library(directory)
            registry = root / 'templates/studio/registry.tex'
            registry.write_text('% stale\n', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, 'Stale Studio catalogue'):
                studio_templates.prepare_catalogue(root, check=True)
            self.assertEqual(registry.read_text(encoding="utf-8"), '% stale\n')

    def test_changed_render_inputs_make_previews_stale(self):
        with mock.patch('studio_preview.input_sets', return_value={'cover': {'changed.tex': 'new hash'}}):
            with self.assertRaisesRegex(RuntimeError, 'Gallery previews are stale'):
                studio_templates.check_gallery(ROOT)

    def test_wrong_page_count_stops_preview_generation(self):
        with mock.patch.object(studio_templates.shutil, 'which', return_value='/tool'), \
                mock.patch.object(studio_templates.subprocess, 'check_output', return_value='Pages: 3\n'), \
                mock.patch.object(studio_templates.subprocess, 'run') as render:
            with self.assertRaisesRegex(RuntimeError, 'expected '+str(len(studio_templates.inspect_templates(ROOT)))):
                studio_templates.render_previews(ROOT, Path('wrong.pdf'))
            render.assert_not_called()


if __name__ == '__main__':
    unittest.main()
