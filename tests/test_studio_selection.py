"""Keep the working set reusable and bound offline gallery loading."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import studio_review
import slide_guide
import studio_templates


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)


class StudioSelectionTests(unittest.TestCase):
    def setUp(self):
        self.entries = studio_templates.inspect_templates(ROOT)

    def test_selection_is_small_distinct_and_field_examples_are_valid(self):
        chosen = studio_review.selected(ROOT, self.entries)
        self.assertEqual(len(chosen), 24)
        self.assertLess(len(chosen), len(self.entries) // 4)
        self.assertEqual(chosen[0]['id'], 'cover')
        self.assertEqual(chosen[-1]['id'], 'closing')
        self.assertIn('merkle-tree', [item['id'] for item in chosen])
        self.assertTrue(all(item['use'] for item in chosen))
        generated = studio_templates.generated_files(ROOT)
        deck = generated[Path('examples/studio-selected-templates.tex')]
        from studio_models import load_models
        grouped=load_models(ROOT)['selection']
        self.assertEqual(deck.count(r'\studiotemplate['),len(grouped))
        for group in grouped:self.assertIn(']{'+group['model']+'}',deck)
        for item in chosen:
            self.assertIn(studio_review.example_command(item), generated[Path('templates/SELECTION.md')])

    def test_unknown_selection_id_and_example_field_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'templates').mkdir()
            target = root / 'templates/review.json'
            original = json.loads((ROOT/'templates/review.json').read_text(encoding="utf-8"))
            for unknown in (False,True):
                data = json.loads(json.dumps(original))
                if unknown:
                    data['templates']['cover']['example']['unknown-field'] = 'Text'
                else:
                    data['selection'] = ['not-a-template']
                target.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, 'Unknown example fields' if unknown else 'Invalid or repeated'):
                    studio_review.selected(root, self.entries)

    def test_legacy_gallery_is_only_a_redirect(self):
        page=studio_templates.gallery_html(self.entries,ROOT)
        parser=Tags();parser.feed(page)
        self.assertNotIn('article',parser.tags)
        self.assertNotIn('img',parser.tags)
        self.assertIn('location.replace',page)
        self.assertIn('../slides/index.html',page)
        self.assertLess(len(page.encode()),4096)

    def test_single_guide_has_no_eager_hd_sources(self):
        page=(ROOT/'docs/slides/index.html').read_text(encoding="utf-8")
        self.assertNotIn('previews/hd/',page)
        self.assertNotIn('catalogue-lessons.js',page)
        self.assertIn('data-view="blocks"',page)
        self.assertLess((ROOT/'docs/slides/catalogue.js').stat().st_size,1024*1024)


if __name__=='__main__':unittest.main()
