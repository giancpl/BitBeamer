"""Keep restored teaching content isolated from neutral Studio presets and review state."""
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import studio_examples
import studio_templates


class StudioExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = studio_templates.inspect_templates(ROOT)
        cls.by_id = {e['id']: e for e in cls.entries}

    def test_ready_content_is_english_and_does_not_replace_neutral_defaults(self):
        entry = self.by_id['three-cards']
        values = studio_examples.example_values(ROOT, entry)
        self.assertEqual(values['text/1'], 'Financial exclusion')
        self.assertEqual(values['text/2'], 'Unbanked')
        self.assertEqual(values['text/3'], 'Remittances')
        self.assertEqual(values['text/4'], 'Censorship')
        self.assertEqual(entry['fields'][0]['default'], 'Slide title')
        neutral = studio_examples.exact_command(ROOT, entry)
        example = studio_examples.exact_command(ROOT, entry, 'example')
        self.assertNotIn('Financial exclusion', neutral)
        self.assertIn('Financial exclusion', example)
        self.assertIn('variant={three}', neutral)
        self.assertIn('variant={three}', example)

    def test_renamed_semantic_fields_preserve_historical_content(self):
        entry = self.by_id['chat-dialogue']
        values = studio_examples.example_values(ROOT, entry)
        self.assertIn('A private matter', values['text/1'])
        self.assertIn('Eric Hughes', values['text/2'])
        self.assertFalse(values['text/1'].startswith(('\"', '“', '``')))
        self.assertFalse(values['text/1'].endswith(('\"', '”', "''")))
        self.assertFalse(values['text/2'].startswith(('---', '—')))

        self.assertEqual({f['name'] for f in entry['fields'] if f['type'] == 'text'},
                         {'quote', 'attribution'})
        self.assertIn(']{quotation}', studio_examples.exact_command(ROOT, entry, 'example'))

    def test_cover_examples_use_generic_authors(self):
        for name in ['cover','cover-light','cover-photo','cover-wide-title']:
            command=studio_examples.exact_command(ROOT,self.by_id[name],'example')
            self.assertIn('Author name',command)
            self.assertNotIn('Cappiello',command)
            self.assertNotIn('Sibilla Merlo',command)

    def test_original_graphics_replace_neutral_placeholders_in_examples_only(self):
        entry = self.by_id['contact-qr']
        values = studio_examples.example_values(ROOT, entry)
        self.assertIn('figma-0943-part-01.pdf', values['graphic/2'])
        self.assertIn('figma-0943-part-02.pdf', values['graphic/1'])
        self.assertNotIn('neutral/', ''.join(values.values()))
        self.assertTrue(any('neutral/' in f['default'] for f in entry['fields']))

    def test_full_examples_and_small_neutral_shortlist_preserve_review_state(self):
        ledger = ROOT / 'templates/review.json'
        before = hashlib.sha256(ledger.read_bytes()).hexdigest()
        files = studio_examples.generated(ROOT, self.entries)
        full = files[Path('examples/studio-ready-content.tex')]
        compact = files[Path('examples/studio-reusable.tex')]
        self.assertEqual(full.count('\\studiotemplate['), len(studio_templates.inspect_templates(ROOT)))
        self.assertEqual(compact.count('\\studiotemplate['), 4)
        self.assertNotIn('Bitcoin is not', compact)
        self.assertIn('Bitcoin is not', full)
        self.assertEqual(before, hashlib.sha256(ledger.read_bytes()).hexdigest())
        for path, content in files.items():
            self.assertEqual((ROOT / path).read_text(encoding="utf-8"), content, str(path))


if __name__ == '__main__':
    unittest.main()
