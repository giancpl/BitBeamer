"""Verify measured agenda variants, original references and compatible content roles."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import studio_models
import studio_templates
import studio_examples


class StudioAgendaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}

    def test_four_and_five_variants_have_their_own_original_geometry(self):
        for variant,name,count,canvas in [('panels','contents',4,[1920,1080]),('panels-five','contents-five',5,[3556,2000])]:
            model,actual,choice,palette=studio_models.resolve(ROOT,'agenda',variant,'light')
            self.assertEqual(choice['id'],name)
            self.assertEqual(palette,'light')
            entry=self.entries[name]
            self.assertEqual(entry['canvas'],canvas)
            for word in ['one','two','three','four','five'][:count]:
                self.assertIn('item-'+word,choice['fields'])
            self.assertEqual(len([f for f in entry['fields'] if f['type']=='text']),count+1)
        self.assertEqual(self.entries['contents']['references'],['figma-0575'])
        self.assertIn('figma-0883',self.entries['contents-five']['references'])

    def test_legacy_item_roles_survive_the_new_semantic_names(self):
        choice=studio_models.resolve(ROOT,'agenda','panels','light')[2]
        self.assertEqual(choice['fields']['item-one'],choice['fields']['label-one'])
        self.assertEqual(choice['fields']['item-four'],choice['fields']['label-five'])
        self.assertNotIn('item-five',choice['fields'])
        for name in ('contents','contents-five'):
            with self.assertRaisesRegex(ValueError,'Unsupported palette'):
                studio_models.resolve(ROOT,'agenda',self.entries[name]['variant'],'blue')

    def test_ready_content_and_prepared_panels_remain_independent_of_original_exports(self):
        entry=self.entries['contents-five']
        values=studio_examples.example_values(ROOT,entry)
        self.assertEqual(values['text/2'],'Introduction to Bitcoin')
        self.assertEqual(values['text/6'],r'Q\&A')
        for field in entry['fields']:
            if field['type']=='graphic':
                path=ROOT/'images/studio/collection'/(entry['parts'][field['slot']['number']-1]+'.pdf')
                self.assertTrue(path.is_file())
        self.assertEqual(entry['status'],'in review')
        self.assertEqual(entry['palette_reviews']['light']['status'],'in review')


if __name__=='__main__':unittest.main()
