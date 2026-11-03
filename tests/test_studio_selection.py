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
import studio_gallery
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
        chosen = studio_gallery.selection(ROOT, self.entries)
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
            self.assertIn(studio_gallery.example_command(item), generated[Path('templates/SELECTION.md')])

    def test_unknown_selection_id_and_example_field_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'templates').mkdir()
            target = root / 'templates/review.json'
            original = json.loads((ROOT/'templates/review.json').read_text())
            for unknown in (False,True):
                data = json.loads(json.dumps(original))
                if unknown:
                    data['templates']['cover']['example']['unknown-field'] = 'Text'
                else:
                    data['selection'] = ['not-a-template']
                target.write_text(json.dumps(data))
                with self.assertRaisesRegex(RuntimeError, 'Unknown example fields' if unknown else 'Invalid or repeated'):
                    studio_gallery.selection(root, self.entries)

    def test_initial_html_creates_no_archive_card_or_image_elements(self):
        for comparison in [False, True]:
            page = studio_gallery.gallery_html(self.entries, comparison=comparison)
            parser = Tags()
            parser.feed(page)
            self.assertNotIn('article', parser.tags)
            self.assertNotIn('img', parser.tags)
            payload = page.split('id="gallery-data" type="application/json">')[1].split('</script>')[0]
            data = json.loads(payload)
            self.assertEqual(len(data['entries']), len(self.entries))
            self.assertEqual(len(data['selection']), 24)
            self.assertEqual(data['pageSize'], 6 if comparison else 12)
            self.assertIn('loading="lazy"', page)
            if comparison:
                self.assertTrue(data['entries'][0]['preview'].startswith('web/'))
                self.assertTrue(data['entries'][0]['original']['full'].endswith('.png'))

    @unittest.skipUnless(shutil.which('node'), 'Optional JavaScript runtime is not installed')
    def test_browser_selection_filter_and_page_boundaries(self):
        script = r'''
const assert = require('node:assert/strict');
const {selectRows, pageRows} = require(process.argv[1]);
const rows = Array.from({length:204}, (_,i)=>({id:'layout-'+i,title:'Title '+i,
  category:i%2?'Cards':'Opening',status:'in review',references:['figma-'+i]}));
const ids = rows.slice(0,24).map(r=>r.id).reverse();
const selected=selectRows(rows,ids,'selected','','','');
assert.equal(selected.length,24);assert.equal(selected[0].id,ids[0]);
assert.equal(pageRows(selected,0,12).rows.length,12);
assert.equal(pageRows(selected,999,12).page,1);
assert.equal(selectRows(rows,ids,'all','','','').length,204);
assert.equal(selectRows(rows,ids,'all','FIGMA-203','','')[0].id,'layout-203');
assert.equal(selectRows(rows,ids,'selected','','Cards','').length,12);
assert.equal(pageRows([],0,12).pages,1);
assert.equal(selectRows([{...rows[0],aliases:['Legacy']}],ids,'all','LEGACY','','')[0].id,'layout-0');
assert.equal(selectRows(rows,ids,'all','','','approved').length,0);
'''
        subprocess.run([shutil.which('node'), '-e', script, str(ROOT / 'scripts/studio-gallery.js')], check=True)


if __name__ == '__main__':
    unittest.main()
