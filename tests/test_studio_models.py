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
        self.assertEqual(studio_models.validate(ROOT,entries),95)
        members=studio_models.membership(ROOT)
        self.assertEqual(set(members),{e['id'] for e in entries})
        self.assertEqual(members['privacy-levels'][0]['id'],members['privacy-levels-blue'][0]['id'])
        self.assertEqual(members['privacy-levels'][1]['id'],members['privacy-levels-blue'][1]['id'])
        self.assertNotEqual(members['cover'][1]['id'],members['cover-light'][1]['id'])
        self.assertNotEqual(members['cover'][0]['id'],members['cover-dashboard'][0]['id'])
        self.assertNotEqual(members['milestone-cards'][0]['id'],members['two-step-process'][0]['id'])
        self.assertEqual(members['milestone-cards'][0]['id'],'milestone-badges')

    def test_soft_card_icon_names_target_symbols_instead_of_panels(self):
        entries=studio_templates.inspect_templates(ROOT)
        members=studio_models.membership(ROOT)
        registry="\n".join(studio_models.registry(ROOT,entries))
        from slide_guide import semantic_fields
        for name,expected in [('feature-spotlight',{'card-one/graphic':3,'card-two/graphic':4}),
                              ('incentives-card-grid',{'title-graphic':1})]:
            entry=next(e for e in entries if e['id']==name)
            exposed=[f for f in semantic_fields(entry,members[name][2]) if f['type']=='graphic']
            self.assertEqual({f['name'] for f in exposed},set(expected))
            for key,number in expected.items():
                field=next(f for f in entry['fields'] if f['type']=='graphic' and f['slot']['number']==number)
                self.assertLessEqual(max(field['box'][2:]),240)
        self.assertIn(r'\studiocardfields{one}{text-6}{text-5}{3}',registry)
        self.assertIn(r'\studiocardtitlegraphic{1}',registry)
        self.assertNotIn(r'\DeclareStudioGraphicSemantic{feature-spotlight}{one}',registry)

    def test_soft_cards_share_semantics_and_keep_distinct_original_layouts(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        models=studio_models.load_models(ROOT)['models']
        model=next(m for m in models if m['id']=='text-cards')
        expected={'three-summary':3,'two':2,'four':4,'four-bullets':4,
                  'two-stacked':2,'two-icon-stacked':2,'five':5,
                  'four-network':4,'four-nodes':4,'three-asymmetric':3}
        self.assertEqual({v['id'] for v in model['variants']},set(expected))
        words=['one','two','three','four','five']
        for variant in model['variants']:
            composition=variant['compositions'][0]
            entry=entries[composition['id']]
            for word in words[:expected[variant['id']]]:
                self.assertIn('card-'+word+'/title',composition['fields'])
                self.assertIn('card-'+word+'/body',composition['fields'])
            for word in words[expected[variant['id']]:]:
                self.assertNotIn('card-'+word+'/title',composition['fields'])
                self.assertNotIn('card-'+word+'/body',composition['fields'])
            self.assertEqual(set(entry['options']),{'show-title','show-card-titles',
                'show-card-bodies','show-introduction','show-icons'})
            self.assertTrue(all(o['type']=='boolean' for o in entry['options'].values()))
            self.assertIn('templates/studio/components/text-card-options.tex',entry['shared_sources'])
        outlines=next(m for m in models if m['id']=='outlined-cards')
        self.assertEqual({v['id'] for v in outlines['variants']},{'callout','six-outline','six-detailed'})

    def test_icon_card_rows_share_count_fields_title_and_renderer(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        members=studio_models.membership(ROOT)
        for source,count,variant,default in [('two-cards',2,'two',False),('three-cards',3,'three',True),('five-icon-row',5,'five',True)]:
            entry=entries[source];model,choice,composition=members[source]
            self.assertEqual(model['id'],'icon-cards')
            self.assertEqual(choice['id'],variant)
            self.assertEqual(entry['options']['show-title']['default'],default)
            graphics=[f for f in entry['fields'] if f['type']=='graphic']
            self.assertEqual(len(graphics),count)
            self.assertEqual([f['slot']['number'] for f in graphics],list(range(1,count+1)))
            self.assertTrue(all(f['slot']['content'][2:]==[216,216] for f in graphics))
            for graphic in graphics:
                caption=next(f for f in entry['fields'] if f['name']==graphic['name'].replace('graphic-','caption-'))
                panel_bottom=graphic['box'][1]+108+200
                self.assertAlmostEqual(caption['box'][1]-panel_bottom,76)
                self.assertAlmostEqual(caption['box'][0]+caption['box'][2]/2,graphic['box'][0]+108)
            self.assertEqual(entry['shared_sources'],['templates/studio/components/icon-card-row.tex'])
            self.assertIn('title',composition['fields'])
            self.assertNotIn('rejected_semantic_fields',composition)
        grid=next(m for m in studio_models.load_models(ROOT)['models'] if m['id']=='icon-grid')
        self.assertNotIn('row',[v['id'] for v in grid['variants']])

    def test_process_captions_follow_reading_order_and_heading_is_not_a_caption(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        members=studio_models.membership(ROOT)
        for name,count in [('two-step-process',2),('three-step-process',3),('four-step-process',4)]:
            entry=entries[name];composition=members[name][2]
            fields={f['name']:f for f in entry['fields']}
            graphics=sorted((f for f in entry['fields'] if f['type']=='graphic'),key=lambda f:f['slot']['number'])
            self.assertEqual('title' in composition['fields'],count==4)
            if count!=4:self.assertIn('title',composition['rejected_semantic_fields'])
            for word,graphic in zip(['one','two','three','four'],graphics):
                caption=fields[composition['fields']['caption-'+word]]
                cx,cy,_,_=graphic['slot']['content']
                self.assertAlmostEqual(caption['box'][0]+caption['box'][2]/2,graphic['box'][0]+cx)
                self.assertAlmostEqual(caption['box'][1]-(graphic['box'][1]+cy+200),76)
                self.assertEqual((caption['font_size'],caption['leading']),(76,88))

    def test_two_columns_uses_named_fields_and_rejects_replaced_syntax(self):
        entries=studio_templates.inspect_templates(ROOT)
        composition=studio_models.membership(ROOT)['two-columns'][2]
        expected={'title':'title','introduction':'text-6','left-title':'text-4',
                  'right-title':'text-5','left-body':'text-2','right-body':'text-3'}
        self.assertEqual(composition['fields'],expected)
        self.assertNotIn('field_aliases',composition)
        registry='\n'.join(studio_models.registry(ROOT,[e for e in entries if e['id']=='two-columns']))
        for field,native in expected.items():
            if field != native:
                self.assertIn(r'\DeclareStudioSemantic{two-columns}{'+field+'}{'+native+'}',registry)
        for field in ['label-two','label-three','label-four','label-five','label-six']:
            self.assertIn(r'\DeclareStudioRejectedSemantic{two-columns}{'+field+'}',registry)
            self.assertNotIn(r'\DeclareStudioSemantic{two-columns}{'+field+'}',registry)
        guide=studio_models.model_guides(ROOT,entries)[Path('docs/templates/models/two-columns.md')]
        for name in expected:
            self.assertIn('| `'+name+'` |',guide)
            self.assertIn(name+'={',guide)
        self.assertNotIn('Compatibility names remain accepted',guide)

    def test_list_family_shares_fields_and_declares_requested_palettes(self):
        model=next(m for m in studio_models.load_models(ROOT)['models'] if m['id']=='list-rail')
        self.assertEqual([v['id'] for v in model['variants']],
                         ['three-items','four-items','five-items','grouped','detailed','illustrated'])
        for v in model['variants']:
            for c in v['compositions']:
                self.assertTrue({'title','item-one','item-two','item-three'}<=set(c['fields']))
        for variant,count in [('three-items',3),('four-items',4),('five-items',5)]:
            for palette in ['light','blue']:
                _,_,c,p=studio_models.resolve(ROOT,'list-rail',variant,palette)
                self.assertEqual(p,palette)
                self.assertEqual(len([k for k in c['fields'] if k.startswith('item-')]),count)
        with self.assertRaisesRegex(ValueError,'Unsupported palette'):
            studio_models.resolve(ROOT,'list-rail','grouped','blue')

    def test_optional_sequences_validate_members_without_merging_models(self):
        sequence=studio_models.suggested_sequences(ROOT)[0]
        self.assertEqual(sequence['compositions'],['section-divider','statement-arrow'])
        self.assertNotEqual(studio_models.membership(ROOT)['section-divider'][0]['id'],
                            studio_models.membership(ROOT)['statement-arrow'][0]['id'])
        data=json.loads((ROOT/'templates/models.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'templates').mkdir()
            for members in [['section-divider'],['section-divider','section-divider'],['section-divider','missing']]:
                data['sequences'][0]['compositions']=members
                (root/'templates/models.json').write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError,'Invalid suggested slide sequence'):
                    studio_models.suggested_sequences(root)

    def test_single_composition_export_omits_unavailable_sequence_commands(self):
        entries=studio_templates.inspect_templates(ROOT)
        divider=[entry for entry in entries if entry['id']=='section-divider']
        text=studio_models.model_guides(ROOT,divider)[Path('docs/templates/models/section-divider.md')]
        self.assertNotIn('Suggested sequence',text)
        self.assertNotIn(']{statement}',text)

    def test_selection_retains_each_original_choice_and_order(self):
        d=studio_models.load_models(ROOT)
        original=json.loads((ROOT/'templates/review.json').read_text(encoding="utf-8"))['selection']
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
        parts=[a for folder in ['neutral','icon-palettes'] for a in json.loads((ROOT/'images/studio'/folder/'manifest.json').read_text(encoding="utf-8"))['parts']]
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
        from slide_guide import catalogue
        data=catalogue(ROOT)
        data['variant_aliases']=studio_models.load_models(ROOT).get('variant_aliases',[])
        script=r'''const assert=require('node:assert/strict');const {matches,pageRows,resolveChoice}=require(process.argv[1]);
const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
assert.equal(matches(d.rows,'','studio').length,95);
assert.equal(matches(d.rows,'','featured').length,21);
assert.equal(resolveChoice(d,'cover','pattern','blue').row.id,'cover');
assert.equal(resolveChoice(d,'levels','default','blue').row.choices[resolveChoice(d,'levels','default','blue').index].id,'privacy-levels-blue');
assert.equal(resolveChoice(d,'cover','script').row.id,'protocol');
assert.equal(resolveChoice(d,'statement','credit').row.id,'timeline');
assert.equal(resolveChoice(d,'dialogue','two-messages').row.choices[resolveChoice(d,'dialogue','two-messages').index].id,'chat-dialogue');
assert.equal(pageRows(d.rows,0).length,12);'''
        subprocess.run(['node','-e',script,str(ROOT/'docs/slides/guide.js')],input=json.dumps(data),check=True,capture_output=True,text=True)

    def test_only_original_colour_versions_are_declared(self):
        entries=studio_templates.inspect_templates(ROOT)
        for entry in entries:
            semantic=studio_models.membership(ROOT)[entry['id']][2].get('palette_mode')=='semantic'
            if semantic:
                self.assertEqual(entry['palettes'],['light','blue'])
                self.assertEqual(studio_models.choice_inputs(ROOT,entry,'blue',{})['@palette'],'blue')
            else:
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
        self.assertEqual(len(studio_models.expand_model_names(ROOT,[m['id'] for m in models])),196)
        subset=studio_models.expand_model_names(ROOT,['cover','icon-cards'])
        self.assertEqual(len(subset),7)
        self.assertTrue({'cover','cover-light','cover-photo','three-cards','two-cards'}<=set(subset))
        self.assertNotIn('three-card-summary',subset)
        self.assertIn('three-card-summary',studio_models.expand_model_names(ROOT,['text-cards']))
        with self.assertRaisesRegex(ValueError,'Unknown Studio models'):
            studio_models.expand_model_names(ROOT,['missing-model'])
