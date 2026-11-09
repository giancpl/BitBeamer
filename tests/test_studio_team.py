"""Team field contracts and dependency-scoped, converter-free PDF parts."""
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))

import studio_models
import studio_templates
import studio_preview
import studio_review


class StudioTeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = studio_templates.inspect_templates(ROOT)
        cls.entry = next(e for e in cls.entries if e['id']=='team-presentation')

    def test_supplied_reference_and_editable_statistic_roles(self):
        model,variant,choice,palette = studio_models.resolve(ROOT,'team')
        self.assertEqual(choice['id'],'team-presentation')
        self.assertEqual(self.entry['canvas'],[1920,1080])
        self.assertEqual(self.entry['external_reference']['name'],'team-presentation.pdf')
        self.assertEqual(len([f for f in self.entry['fields'] if f['type']=='text']),8)
        self.assertEqual(palette,'light')
        with self.assertRaisesRegex(ValueError,'Unsupported palette'):
            studio_models.resolve(ROOT,'team',palette='blue')
        self.assertEqual(self.entry['status'],studio_review.load_review(ROOT)['templates']['team-presentation']['status'])

    def test_subset_resources_and_scoped_preview_invalidation(self):
        resources = self.entry['prepared_resources']
        files = studio_models.dependencies(ROOT,[self.entry])
        self.assertTrue(set(resources).issubset(files))
        self.assertTrue(all(path.is_file() for path in files.values()))
        self.assertIn('team-presentation',[item['id'] for item in studio_review.package_selection(ROOT)])
        before = studio_preview.input_sets(ROOT,self.entries)
        changed = ROOT/'images/studio/team/collage.pdf'
        digest = studio_preview.digest
        with mock.patch.object(studio_preview,'digest',side_effect=lambda p:'changed' if p==changed else digest(p)):
            after = studio_preview.input_sets(ROOT,self.entries)
        self.assertEqual({name for name in before if before[name]!=after[name]},{'team-presentation'})

    def test_modified_prepared_pdf_is_detected_without_conversion(self):
        import hashlib
        real = hashlib.sha256
        data = (ROOT/'images/studio/team/panels.pdf').read_bytes()
        def altered(value):
            return real(b'changed' if value==data else value)
        with mock.patch.object(studio_templates.hashlib,'sha256',side_effect=altered):
            with self.assertRaisesRegex(RuntimeError,'Changed prepared Studio resource'):
                studio_templates.check_prepared_resources(ROOT)


if __name__=='__main__':
    unittest.main()
