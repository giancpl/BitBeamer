"""Usage-guide coverage, valid examples, field maps and portable links."""
import json
import importlib.util
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import studio_templates
from studio_guides import generated_guides, guide_info, portable_guides
from doc_checks import check_docs


class StudioGuideTests(unittest.TestCase):
    def setUp(self):
        self.entries = studio_templates.inspect_templates(ROOT)
        self.selected = {entry['id']:entry for entry in __import__('studio_review').selected(ROOT)}

    def test_card_command_groups_content_and_orders_cards_visually(self):
        from studio_guides import command
        result=command('text-cards',{
            'card-two/body':'Second, supporting detail.',
            'card-one/icon':'book',
            'card-one/body':r'First line\\Second line',
            'introduction':'Context',
            'card-two/title':'Second',
            'title':'Overview',
            'card-one/title':'First',
            'variant':'two-icon-stacked'})
        self.assertLess(result.index('variant='),result.index('title={Overview}'))
        self.assertLess(result.index('title={Overview}'),result.index('introduction='))
        self.assertLess(result.index('card-one='),result.index('card-two='))
        self.assertLess(result.index('title={First}'),result.index('body={First line'))
        self.assertLess(result.index('body={First line'),result.index('icon={book}'))
        self.assertIn('body={Second, supporting detail.}',result)
        self.assertIn(r'body={First line\\Second line}',result)
        self.assertNotIn('card-one/title=',result)
        # Preserve invalid keys for the compiler to reject; never silently drop them.
        invalid=command('text-cards',{'card-one/title':'First','card-six':'title={Extra}','card-one/typo':'Bad'})
        self.assertIn('card-six=',invalid)
        self.assertIn('card-one/typo=',invalid)

    def test_every_current_composition_has_one_fresh_guide(self):
        generated = generated_guides(ROOT, self.entries, studio_templates.inspect_aliases(ROOT))
        paths = set((ROOT / 'docs/templates/guides').glob('*.md'))
        self.assertEqual(len(paths), len(self.entries))
        self.assertEqual(paths, {ROOT / path for path in generated if path.parent.name == 'guides'})
        for path, content in generated.items():
            self.assertEqual((ROOT / path).read_text(encoding='utf-8'), content)
        for alias in studio_templates.inspect_aliases(ROOT):
            self.assertFalse((ROOT / 'docs/templates/guides' / (alias['id'] + '.md')).exists())

    def test_complete_examples_use_real_fields_and_fixed_geometry(self):
        for entry in self.entries:
            info = guide_info(entry, self.selected.get(entry['id']))
            text = (ROOT / 'docs/templates/guides' / (entry['id'] + '.md')).read_text(encoding='utf-8')
            self.assertIn(info['document'].rstrip(), text)
            self.assertIn(r'\documentclass[aspectratio=169]{beamer}', info['document'])
            self.assertIn(r'\addbibresource{bibliography.bib}', info['document'])
            expected = {field['name'] for field in entry['fields']}
            expected |= {field['slot']['key'] for field in entry['fields']}
            expected |= {prefix+'/'+str(field['slot']['number']) for field in entry['fields'] if field.get('block') for prefix in ('heading','body')}
            options = set(re.findall(r'^\s*([a-z][a-z0-9/-]*)=\{', info['example'], re.M))
            self.assertTrue(options <= expected, entry['id'])
            self.assertEqual({field['name'] for field in info['fields']}, {field['name'] for field in entry['fields']})
            for field in info['fields']:
                self.assertIn('<code>' + field['name'] + '</code>', text)
                self.assertTrue(field['role'])
                self.assertTrue(field['space'])
            if info['replacement']:
                self.assertIn('icon/', info['replacement'])
                graphic_name = re.search(r'^\s*([a-z][a-z0-9/-]*)=\{', info['replacement'], re.M).group(1)
                self.assertIn(graphic_name, {'icon/'+str(f['slot']['number']) for f in entry['fields'] if f['type']=='graphic'})

    def test_native_source_defined_areas_are_described_without_invented_boxes(self):
        entry = next(entry for entry in self.entries if entry['id'] == 'table')
        info = guide_info(entry)
        self.assertTrue(all(field['space'] == 'Source-defined' for field in info['fields']))
        self.assertIsNone(info['replacement'])

    def test_stale_guide_check_is_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = Path('docs/templates/guides/three-cards.md')
            (root / path).parent.mkdir(parents=True)
            (root / path).write_text('stale guide', encoding="utf-8")
            with mock.patch.object(studio_templates, 'generated_files', return_value={path:'current guide'}):
                with self.assertRaisesRegex(RuntimeError, 'Stale Studio catalogue'):
                    studio_templates.prepare_catalogue(root, check=True)
            self.assertEqual((root / path).read_text(encoding="utf-8"), 'stale guide')

    def test_archive_validation_reads_a_complete_user_example(self):
        spec=importlib.util.spec_from_file_location('guide_validator',ROOT/'scripts/validate-studio-review.py')
        validator=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            self.assertIsNone(validator.guide_example(root))
            (root/'guides').mkdir()
            entry=next(entry for entry in self.entries if entry['id']=='three-cards')
            data=portable_guides(ROOT,[entry])
            (root/'guides/three-cards.md').write_bytes(data['guides/three-cards.md'])
            self.assertEqual(validator.guide_example(root),guide_info(entry,self.selected['three-cards'])['document'])
            (root/'guides/three-cards.md').write_text('Incomplete guide', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,'Missing complete example'):
                validator.guide_example(root)

    def test_portable_guides_reference_only_the_included_project(self):
        entries = [entry for entry in self.entries if entry['id'] in ['three-cards','line-chart','code','table','equation']]
        data = portable_guides(ROOT, entries)
        from studio_models import model_guides
        self.assertEqual(len(data),len(entries)+len(model_guides(ROOT,entries))+5)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, value in data.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(value)
                self.assertNotIn(b'python3 scripts', value)
                self.assertNotIn(b'docs/templates/previews', value)
            for entry in entries:
                target = root / entry['source']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
            self.assertEqual(check_docs(root), len(data)-1)
            self.assertFalse((root / 'guides/cover.md').exists())
            self.assertNotIn('Show editable areas', (root / 'guides/table.md').read_text(encoding="utf-8"))


if __name__ == '__main__':
    unittest.main()
