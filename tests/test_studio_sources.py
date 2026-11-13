"""One current implementation per composition and compatibility without copies."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from studio_templates import inspect_templates, inspect_aliases, registry_document
from studio_parts import prepare, references, extract


class CurrentStudioSourceTests(unittest.TestCase):
    def test_user_background_survives_extraction_without_original_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = 'images/studio/parts/source/statement-glow-background-f9f9f9.pdf'
            supplied = (ROOT / relative).read_bytes()
            target = root / relative
            target.parent.mkdir(parents=True)
            target.write_bytes(supplied)
            recipe = next(p for p in json.loads((ROOT / 'images/studio/parts/recipes.json').read_text())['parts']
                          if p['name'] == 'radial-glow')
            (root / 'images/studio/parts/recipes.json').write_text(json.dumps({'parts': [recipe]}))
            (root / 'templates').mkdir()
            (root / 'templates/figma-inventory.json').write_text(json.dumps({'frames': [
                {'id': recipe['reference'], 'file': 'unavailable-original.svg', 'sha256': 'historical-reference'}]}))
            records = extract(root, exports=root / 'unavailable-exports')
            self.assertEqual(target.read_bytes(), supplied)
            self.assertEqual(records[0]['source'], relative)
            self.assertEqual(records[0]['canvas'], [1920, 1080])
            self.assertEqual(records[0]['background_override']['color'], '#F9F9F9')
            self.assertEqual(records[0]['source_sha256'], hashlib.sha256(supplied).hexdigest())
            self.assertEqual(records[0]['source_origin']['kind'], 'user-supplied background')
            self.assertEqual(prepare(root), 1)
            self.assertEqual((root / 'images/studio/parts/radial-glow.pdf').read_bytes(), supplied)

    def test_every_composition_has_one_distinct_current_implementation(self):
        entries = inspect_templates(ROOT)
        self.assertEqual(len(entries), len(json.loads((ROOT/'templates/index.json').read_text())['templates']))
        self.assertEqual(len({entry['source'] for entry in entries}), len(entries))
        shapes = {}
        for entry in entries:
            source = (ROOT / entry['source']).read_text(encoding='utf-8')
            source = re.sub(r'^\\studiodeclarefield[^\n]*\n', '', source, flags=re.M)
            source = re.sub(r'%[^\n]*', '', source).replace('{' + entry['id'] + '}', '{MODEL}')
            shape = re.sub(r'\s+', '', source)
            if shape in shapes:
                from studio_models import membership
                members=membership(ROOT);previous=next(e for e in entries if e['id']==shapes[shape])
                self.assertEqual((members[entry['id']][0]['id'],members[entry['id']][1]['id']),
                                 (members[previous['id']][0]['id'],members[previous['id']][1]['id']))
                self.assertTrue(entry.get('shared_sources'))
                self.assertEqual(entry['shared_sources'],previous.get('shared_sources'))
            shapes[shape] = entry['id']

    def test_compatibility_names_preserve_the_public_api_without_source_copies(self):
        entries = inspect_templates(ROOT)
        aliases = inspect_aliases(ROOT, entries)
        self.assertEqual(len(aliases), 9)
        self.assertEqual(len(entries) + len(aliases), json.loads((ROOT/'templates/figma-inventory.json').read_text())['counts']['templates'])
        sources = {entry['source'] for entry in entries}
        for alias in aliases:
            self.assertIn(alias['source'], sources)
            self.assertFalse((ROOT / 'templates/studio' / (alias['id'] + '.tex')).exists())
        registry = registry_document(entries, aliases)
        self.assertEqual(registry.count('\\DeclareStudioTemplate{'), len(entries))
        self.assertEqual(registry.count('\\DeclareStudioTemplateAlias{'), 9)
        self.assertIn(r'\DeclareStudioTemplateAlias{photo-triptych-no-title}{photo-triptych}{title={}}', registry)
        wrapper = (ROOT / 'bitpolitostudiopilots.sty').read_text(encoding='utf-8')
        self.assertIn(r'\studiotemplate{#1}', wrapper)
        self.assertNotIn('templates/pilots', wrapper)

    def test_invalid_compatibility_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'templates').mkdir()
            metadata = json.loads((ROOT / 'templates/index.json').read_text(encoding='utf-8'))
            metadata['aliases'][0]['alias_of'] = 'missing-current-source'
            (root / 'templates/index.json').write_text(json.dumps(metadata), encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'Invalid Studio compatibility'):
                inspect_aliases(root)

    def test_showcase_and_measurements_point_to_current_sources(self):
        selected = __import__('studio_review').selected(ROOT)
        main = (ROOT / 'main-studio.tex').read_text(encoding='utf-8')
        names = re.findall(r'\\studiotemplate(?:\[.*?\])?\{([^}]+)\}', main)
        from studio_models import load_models
        self.assertEqual(names,[entry['model'] for entry in load_models(ROOT)['selection']])
        measurements = json.loads((ROOT / 'templates/measurements.json').read_text(encoding='utf-8'))['models']
        self.assertEqual(len(measurements), 8)
        for entry in measurements:
            self.assertEqual(entry['source'], 'templates/studio/' + entry['id'] + '.tex')
            self.assertTrue((ROOT / entry['source']).is_file())
        for relative in ['templates/pilots', 'examples/studio-pilots.tex',
                         'examples/studio-pilot-geometry.tex', 'scripts/package-studio-pilots.py',
                         'scripts/review-studio-pilots.py', 'docs/templates/pilots']:
            self.assertFalse((ROOT / relative).exists(), relative)
        self.assertTrue((ROOT / 'tests/fixtures/studio-fields.tex').is_file())

    def test_prepared_parts_remain_self_contained(self):
        self.assertEqual(prepare(ROOT, check=True), 40)
        manifest = json.loads((ROOT / 'images/studio/parts/manifest.json').read_text(encoding='utf-8'))
        for part in manifest['parts']:
            if part.get('rendering') == 'copy-pdf':
                self.assertEqual((ROOT / part['source']).read_bytes(),
                                 (ROOT / 'images/studio/parts' / (part['name'] + '.pdf')).read_bytes())
                continue
            svg = ET.parse(ROOT / part['source']).getroot()
            ids = {node.get('id') for node in svg.iter() if node.get('id')}
            self.assertFalse(references([svg]) - ids, part['name'])
            for node in svg.iter():
                for key, value in node.attrib.items():
                    if key.endswith('href') and not value.startswith('#'):
                        self.assertTrue(((ROOT / part['source']).parent / value).is_file())


if __name__ == '__main__':
    unittest.main()
