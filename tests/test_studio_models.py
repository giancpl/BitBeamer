"""Grouped variants, stable legacy coverage, palette contracts and bounded gallery selection."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import studio_models
import studio_palettes
import studio_templates

class StudioModelTests(unittest.TestCase):
    def test_every_legacy_composition_maps_once_without_merging_distinct_geometry(self):
        entries=studio_templates.inspect_templates(ROOT)
        self.assertEqual(studio_models.validate(ROOT,entries),100)
        members=studio_models.membership(ROOT)
        self.assertEqual(set(members),{e['id'] for e in entries})
        self.assertEqual(members['privacy-levels'][0]['id'],members['privacy-levels-blue'][0]['id'])
        self.assertEqual(members['privacy-levels'][1]['id'],members['privacy-levels-blue'][1]['id'])
        self.assertNotEqual(members['cover'][1]['id'],members['cover-light'][1]['id'])
        self.assertNotEqual(members['cover'][0]['id'],members['cover-dashboard'][0]['id'])

    def test_selection_retains_each_original_choice_and_order(self):
        d=studio_models.load_models(ROOT)
        original=json.loads((ROOT/'templates/review.json').read_text())['selection']
        self.assertEqual(len(d['selection']),21)
        retained=[name for s in d['selection'] for name in s['selected_compositions']]
        self.assertCountEqual(original,retained)
        self.assertEqual(d['selection'][0]['model'],'cover')
        self.assertEqual(d['selection'][-1]['model'],'closing')

    def test_explicit_palette_selects_retained_native_pair_when_available(self):
        _,_,c,p=studio_models.resolve(ROOT,'levels',palette='blue')
        self.assertEqual(c['id'],'privacy-levels-blue');self.assertEqual(p,'blue')
        with self.assertRaisesRegex(ValueError,'Unsupported palette'):
            studio_models.resolve(ROOT,'cover',variant='wide-pattern',palette='blue')
        _,_,c,_=studio_models.resolve(ROOT,'privacy-levels',palette='blue')
        self.assertEqual(c['id'],'privacy-levels-blue')
        with self.assertRaisesRegex(ValueError,'Unsupported palette'):
            studio_models.resolve(ROOT,'horizontal-split',palette='blue')
        with self.assertRaisesRegex(ValueError,'Unknown variant'):
            studio_models.resolve(ROOT,'cover',variant='not-a-variant')

    def test_subset_advertises_only_installed_variants_and_resources(self):
        entries=studio_templates.inspect_templates(ROOT)
        subset=[e for e in entries if e['id']=='cover-photo']
        registry='\n'.join(studio_models.registry(ROOT,subset))
        self.assertIn(r'\DeclareStudioModel{cover}{photo}',registry)
        self.assertNotIn(r'\DeclareStudioVariant{cover}{pattern}',registry)
        self.assertTrue(all(p.is_file() for p in studio_models.dependencies(ROOT,subset).values()))

    def test_palette_check_is_read_only_and_has_no_converter_dependency(self):
        parts=[a for folder in ['neutral','icon-palettes'] for a in json.loads((ROOT/'images/studio'/folder/'manifest.json').read_text())['parts']]
        before={p:(ROOT/p).stat().st_mtime_ns for a in parts for p in [a['source'],a['pdf']]}
        self.assertTrue(before)
        with mock.patch('asset_library.rsvg_modules',side_effect=AssertionError('No converter')):
            self.assertEqual(studio_palettes.check(ROOT),len(parts))
        self.assertEqual(before,{p:(ROOT/p).stat().st_mtime_ns for p in before})

    def test_visible_defaults_are_neutral_without_synthetic_artwork(self):
        entries=studio_templates.inspect_templates(ROOT)
        for e in entries:
            for f in e['fields']:
                if f['type']=='text':
                    self.assertNotRegex(f['default'],r'(?i)bitcoin|bitgeneration|gianluca|sibilla|musumeci|raspiblitz|satoshi|lightning|no-kyc')

    @unittest.skipUnless(shutil.which('node'),'Optional Node runtime unavailable')
    def test_browser_grouping_preserves_variants_and_filters_before_loading(self):
        config=studio_models.load_models(ROOT)
        rows=[{'id':c['id'],'title':c['id'],'references':[]} for m in config['models'] for v in m['variants'] for c in v['compositions']]
        script=r'''const assert=require('node:assert/strict');const {groupRows,pageRows}=require(process.argv[1]);
const d=JSON.parse(process.argv[2]);
assert.equal(groupRows(d.rows,d.models,d.selection,'models').length,100);
assert.equal(groupRows(d.rows,d.models,d.selection,'selected').length,21);
assert.equal(groupRows(d.rows,d.models,d.selection,'all').length,194);
const chosen=groupRows(d.rows,d.models,d.selection,'models',{cover:{variant:'wide-pattern',palette:'blue'}});
assert.equal(chosen.find(r=>r.model.id==='cover').id,'cover-light');
assert.equal(chosen.find(r=>r.model.id==='cover').modelPalette,'light');
const pair=groupRows(d.rows,d.models,d.selection,'models',{levels:{palette:'blue'}});
assert.equal(pair.find(r=>r.model.id==='levels').id,'privacy-levels-blue');
assert.equal(pageRows(chosen,0,12).rows.length,12);'''
        subprocess.run(['node','-e',script,str(ROOT/'scripts/studio-gallery.js'),json.dumps(dict(config,rows=rows))],check=True,capture_output=True,text=True)

    def test_only_original_colour_versions_are_declared(self):
        entries=studio_templates.inspect_templates(ROOT)
        for entry in entries:
            self.assertEqual(entry['palettes'],[entry['native_palette']])
            with self.assertRaisesRegex(ValueError,'No original'):
                studio_models.choice_inputs(ROOT,entry,'light' if entry['native_palette']=='blue' else 'blue',{})
        models=studio_models.load_models(ROOT)['models']
        pairs=[(m['id'],v['id']) for m in models for v in m['variants'] if len({c['native_palette'] for c in v['compositions']})>1]
        self.assertEqual(pairs,[('levels','default')])
        members=studio_models.membership(ROOT)
        self.assertNotEqual(members['icon-spotlight-light'][1]['id'],members['icon-spotlight-blue'][1]['id'])
        self.assertFalse(list((ROOT/'docs/templates/previews').glob('*--*.png')))
        self.assertFalse((ROOT/'images/studio/palettes').exists())

    def test_shared_geometry_edits_invalidate_both_colour_presets_only(self):
        import studio_preview
        entries=studio_templates.inspect_templates(ROOT);before=studio_preview.input_sets(ROOT,entries)
        edited=ROOT/'templates/studio/shared/levels.tex';real=studio_preview.digest
        with mock.patch.object(studio_preview,'digest',side_effect=lambda p:'changed' if p==edited else real(p)):
            after=studio_preview.input_sets(ROOT,entries)
        self.assertEqual({name for name in before if before[name]!=after[name]},{'privacy-levels','privacy-levels-blue'})

    def test_grouped_subset_export_retains_every_requested_composition(self):
        models=studio_models.load_models(ROOT)['models']
        self.assertEqual(len(studio_models.expand_model_names(ROOT,[m['id'] for m in models])),194)
        subset=studio_models.expand_model_names(ROOT,['cover','icon-cards'])
        self.assertEqual(len(subset),10)
        self.assertTrue({'cover','cover-light','cover-photo','three-cards','two-cards'}<=set(subset))
        with self.assertRaisesRegex(ValueError,'Unknown Studio models'):
            studio_models.expand_model_names(ROOT,['missing-model'])
