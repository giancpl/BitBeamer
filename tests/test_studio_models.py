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
        self.assertEqual(studio_models.validate(ROOT,entries),len(studio_models.load_models(ROOT)['models']))
        members=studio_models.membership(ROOT)
        self.assertEqual(set(members),{e['id'] for e in entries})
        self.assertEqual(members['privacy-levels'][0]['id'],members['privacy-levels-blue'][0]['id'])
        self.assertEqual(members['privacy-levels'][1]['id'],members['privacy-levels-blue'][1]['id'])
        self.assertNotEqual(members['cover'][1]['id'],members['cover-light'][1]['id'])
        self.assertNotEqual(members['cover'][0]['id'],members['cover-dashboard'][0]['id'])
        self.assertNotEqual(members['milestone-cards'][0]['id'],members['two-step-process'][0]['id'])
        self.assertEqual(members['milestone-cards'][0]['id'],'milestone-badges')

    def test_word_grids_share_twelve_cells_in_reading_order(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        models=studio_models.load_models(ROOT)['models']
        model=next(m for m in models if m['id']=='word-grid')
        self.assertEqual({v['id'] for v in model['variants']},{'plain','annotated'})
        words=['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve']
        for variant in model['variants']:
            contract=variant['compositions'][0];entry=entries[contract['id']]
            native=[contract['fields']['word-'+w] for w in words]
            self.assertEqual(len(set(native)),12)
            positions=[next(f['box'] for f in entry['fields'] if f['name']==n) for n in native]
            for i in range(11):
                if i%3==2:self.assertLess(positions[i][1],positions[i+1][1])
                else:self.assertLess(positions[i][0],positions[i+1][0])
            self.assertFalse(any(f['type']=='graphic' for f in entry['fields']))
            self.assertEqual(entry['parts'],['figma-0662-part-01'])
            self.assertTrue(all(f['font_weight']=='semibold' for f in entry['fields'] if f['name'].startswith('word-')))
            self.assertEqual(set(entry['options']),{'words','numbered'})
            self.assertEqual('explanation' in contract['fields'],variant['id']=='annotated')
        icons=next(m for m in models if m['id']=='icon-grid')
        self.assertEqual({v['id'] for v in icons['variants']},{'four','eight'})

    def test_levels_icons_match_caption_order_and_visible_source_bounds(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        members=studio_models.membership(ROOT)
        for name in ['privacy-levels','privacy-levels-blue']:
            entry=entries[name];contract=members[name][2]
            for number,word in enumerate(['one','two','three'],1):
                graphic=next(f for f in entry['fields'] if f['type']=='graphic' and f['slot']['number']==number)
                caption=next(f for f in entry['fields'] if f['name']==contract['fields']['item-'+word+'/text'])
                self.assertEqual(graphic['box'][2:],[209,209])
                self.assertEqual(graphic['slot']['content'],[104.5,104.5,209,209])
                self.assertEqual(graphic['box'][1],caption['box'][1])
                self.assertEqual(caption['box'][3],209)
                self.assertIn('trim={0 48 48 0}',graphic['default'])
                self.assertEqual(caption['font_weight'],'semibold')

    def test_grouped_list_commands_keep_each_rows_content_together(self):
        from studio_guides import command
        from slide_guide import semantic_fields
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        members=studio_models.membership(ROOT)
        levels=members['privacy-levels'][2]
        self.assertEqual({f['name'] for f in semantic_fields(entries['privacy-levels'],levels) if f['type']=='graphic'},
                         {'item-one/graphic','item-two/graphic','item-three/graphic'})
        text=command('levels',{'item-one/text':'First','item-one/icon':'shield','item-two/text':'Second'})
        self.assertIn('item-one={\n    text={First},\n    icon={shield}\n  }',text)
        self.assertNotIn('item-one/text=',text)
        self.assertNotIn('caption-one=',text)
        rows=members['labelled-rows'][2]
        self.assertEqual(set(rows['fields']),{'title'}|{'item-'+w+'/'+f for w in ['one','two','three'] for f in ['label','body']})
        text=command('labelled-rows',{'item-one/label':'Name','item-one/body':'Details'})
        self.assertIn('item-one={\n    label={Name},\n    body={Details}\n  }',text)

    def test_two_column_lists_expose_semantic_items_and_migrate_historical_bullets(self):
        from studio_examples import exact_command
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        contract=studio_models.membership(ROOT)['title-two-column-list'][2]
        self.assertEqual(contract['fields'],{'title':'title','left-items':'text-2','right-items':'text-3'})
        example=exact_command(ROOT,entries['title-two-column-list'],content='example')
        self.assertIn('left-items={',example)
        self.assertIn('right-items={',example)
        self.assertIn(r'\item',example)
        self.assertNotIn(r'\textbullet',example)
        self.assertNotIn('label-two=',example)
        self.assertNotIn('label-three=',example)
        for name in ['text-2','text-3']:
            field=next(f for f in entries['title-two-column-list']['fields'] if f['name']==name)
            self.assertEqual(field['leading'],95.25)

    def test_partner_contacts_follow_reading_order_and_logos_exclude_panels(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        entry=entries['partner-rail'];contract=studio_models.membership(ROOT)['partner-rail'][2]
        self.assertEqual(len(contract['graphic_slots']),15)
        for i,word in enumerate(['one','two','three','four','five']):
            for offset,role in enumerate(['logo','website','social'],1):
                self.assertEqual(contract['graphic_slots'][role+'-'+word],i*3+offset)
            for role in ['website','social']:
                self.assertIn(role+'-'+word,contract['fields'])
            logo=next(f for f in entry['fields'] if f['type']=='graphic' and f['slot']['number']==i*3+1)
            self.assertNotIn('frame',logo['slot'])
            self.assertEqual(logo['slot']['content'],[123,123,206,206])
        self.assertEqual(entry['parts'][:3],['partner-panel','partner-website','partner-social'])
        source=(ROOT/entry['source']).read_text()
        self.assertEqual(source.count(r'\studiomeasuredpart{partner-panel}'),5)
        self.assertNotIn(r'\path[',source)

    def test_sponsor_presets_keep_real_defaults_bold_contacts_and_short_commands(self):
        from slide_guide import catalogue
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        for name in ['partner-rail','partner-media-grid']:
            self.assertEqual(entries[name]['content_mode'],'sponsor-preset')
            self.assertEqual(entries[name]['category'],'Lists')
            texts=[f for f in entries[name]['fields'] if f['type']=='text']
            self.assertTrue(all(f.get('font_weight')=='semibold' for f in texts))
            self.assertTrue(any('bitbox.swiss' in f['default'] for f in texts))
        contacts=[f for f in entries['partner-rail']['fields'] if f['name'].startswith('contact-')]
        self.assertEqual(len(contacts),10)
        self.assertTrue(all(f['box'][2:]==[76,76] for f in contacts))
        rail=(ROOT/'templates/studio/partner-rail.tex').read_text()
        self.assertIn('partner-logo-three.pdf',rail)
        self.assertNotIn('assets/generated/bitcoin.pdf',rail)
        media=(ROOT/'templates/studio/partner-media-grid.tex').read_text()
        self.assertIn(r'\input{library/layouts/bitpolito-partners.tex}',media)
        self.assertEqual(len(entries['partner-media-grid']['prepared_resources']),3)
        choices={c['id']:c for row in catalogue(ROOT)['rows'] for c in row['choices']}
        for name in ['partner-rail','partner-media-grid']:
            self.assertEqual(choices[name]['command'],r'\studiotemplate{'+name+'}')

    def test_division_icons_follow_caption_order_and_have_independent_bounds(self):
        entries={e['id']:e for e in studio_templates.inspect_templates(ROOT)}
        members=studio_models.membership(ROOT)
        registry="\n".join(studio_models.registry(ROOT,list(entries.values())))
        words=['one','two','three','four','five','six','seven','eight']
        for name,count in [('square-icon-grid',4),('eight-icon-grid',8)]:
            entry=entries[name];contract=members[name][2]
            self.assertEqual(list(contract['graphic_slots']),words[:count])
            self.assertEqual(len([f for f in entry['fields'] if f['type']=='graphic']),count)
            for word in words[:count]:
                number=contract['graphic_slots'][word]
                graphic=next(f for f in entry['fields'] if f['type']=='graphic' and f['slot']['number']==number)
                caption=next(f for f in entry['fields'] if f['name']==contract['fields']['caption-'+word])
                self.assertEqual(graphic['box'][2:],[240,240])
                self.assertNotIn('frame',graphic['slot'])
                self.assertLess(abs(graphic['box'][0]+120-caption['box'][0]-caption['box'][2]/2),8)
                self.assertIn('\\DeclareStudioGraphicSemantic{'+name+'}{'+word+'}{'+str(number)+'}',registry)
            source=(ROOT/entry['source']).read_text()
            self.assertNotIn('\\path[',source,'Native symbols must disappear when their icon field is replaced')
            self.assertIn('card-1',entry['parts'])

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
        self.assertEqual({v['id'] for v in outlines['variants']},{'callout'})

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
assert.equal(matches(d.rows,'','studio').length,d.rows.filter(r=>r.kind==='studio').length);
assert.equal(matches(d.rows,'','featured').length,d.rows.filter(r=>r.featured).length);
assert.equal(resolveChoice(d,'cover','pattern','blue').row.id,'cover');
assert.equal(resolveChoice(d,'levels','default','blue').row.choices[resolveChoice(d,'levels','default','blue').index].id,'privacy-levels-blue');
assert.equal(resolveChoice(d,'cover','script').row.id,'protocol');
assert.equal(resolveChoice(d,'statement','credit').row.id,'timeline');
assert.equal(resolveChoice(d,'quotation','layered').row.choices[resolveChoice(d,'quotation','layered').index].id,'chat-dialogue');
assert.equal(d.variant_aliases.some(a=>a.model==='dialogue' && a.variant==='two-messages'),false);
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

    def test_icon_statement_groups_native_geometry_and_semantic_replacements(self):
        models = studio_models.load_models(ROOT)['models']
        grouped = next(m for m in models if m['id'] == 'icon-statement')
        self.assertEqual([v['id'] for v in grouped['variants']], ['compact', 'large', 'pair'])
        self.assertNotIn('icon-spotlight', {m['id'] for m in models})
        self.assertNotIn('paired-icons-blue', {m['id'] for m in models})
        single, large, pair = [v['compositions'][0] for v in grouped['variants']]
        self.assertEqual(single['fields'], {'statement': 'statement'})
        self.assertEqual(large['fields'], single['fields'])
        self.assertEqual(single['graphic_slots'], {'symbol': 1})
        self.assertEqual(pair['fields'], {})
        entry=next(t for t in studio_templates.inspect_templates(ROOT) if t['id']=='paired-icons-blue')
        boxes=[f['box'] for f in entry['fields'] if f['type']=='graphic']
        self.assertAlmostEqual(boxes[0][1]+boxes[0][3]/2, boxes[1][1]+boxes[1][3]/2, places=3)
        # Stable slots follow visual left/right labels despite historical slot numbering.
        self.assertEqual(pair['graphic_slots'], {'left': 2, 'right': 1})
        self.assertEqual([c['palettes'] for c in (single, large, pair)], [['light'], ['blue'], ['blue']])

    def test_shared_geometry_edits_invalidate_both_colour_presets_only(self):
        import studio_preview
        entries=studio_templates.inspect_templates(ROOT);before=studio_preview.input_sets(ROOT,entries)
        edited=ROOT/'templates/studio/shared/levels.tex';real=studio_preview.digest
        with mock.patch.object(studio_preview,'digest',side_effect=lambda p:'changed' if p==edited else real(p)):
            after=studio_preview.input_sets(ROOT,entries)
        self.assertEqual({name for name in before if before[name]!=after[name]},{'privacy-levels','privacy-levels-blue'})

    def test_grouped_subset_export_retains_every_requested_composition(self):
        models=studio_models.load_models(ROOT)['models']
        self.assertEqual(set(studio_models.expand_model_names(ROOT,[m['id'] for m in models])),{e['id'] for e in json.loads((ROOT/'templates/index.json').read_text())['templates']})
        subset=studio_models.expand_model_names(ROOT,['cover','icon-cards'])
        self.assertEqual(len(subset),7)
        self.assertTrue({'cover','cover-light','cover-photo','three-cards','two-cards'}<=set(subset))
        self.assertNotIn('three-card-summary',subset)
        self.assertIn('three-card-summary',studio_models.expand_model_names(ROOT,['text-cards']))
        with self.assertRaisesRegex(ValueError,'Unknown Studio models'):
            studio_models.expand_model_names(ROOT,['missing-model'])
