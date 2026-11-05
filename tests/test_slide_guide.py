"""Keep the unified preview/command guide complete, current and bounded."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import slide_guide
import studio_preview
import library


class SlideGuideTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='BitBeamer slide guide ')
        self.addCleanup(temporary.cleanup);self.root=Path(temporary.name)
        def write(name,content):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
        self.write=write
        entry={'id':'cover','title':'Cover','source':'templates/studio/cover.tex',
               'fields':[{'name':'title','type':'text','default':'Presentation title'}]}
        write('templates/index.json',json.dumps({'templates':[entry]}))
        write('templates/models.json',json.dumps({'models':[{'id':'cover','title':'Cover','category':'Opening',
             'default_variant':'pattern','variants':[{'id':'pattern','compositions':[
             {'id':'cover','native_palette':'blue','fields':{'title':'title'}}]}]}]}))
        write('templates/review.json',json.dumps({'selection':['cover'],'templates':{'cover':{'status':'in review'}}}))
        write('templates/studio/cover.tex','% Source fixture\n')
        write('docs/templates/previews/cover.png','preview fixture')
        write('docs/slides/guide.js','// Browser fixture\n')
        write('scripts/slide-guide.html',(ROOT/'scripts/slide-guide.html').read_text())
        write('library/slides/example.tex',r'\studiotemplate[caption={Two\\lines}]{panels}'+'\n'+r'\nocite{source}')
        write('library/layouts/panels.tex','% Shared panels\n')
        write('library/layouts/fixed.tex',r'\studiotemplate[caption={Fixed}]{panels}')
        write('library/previews/example.png','lesson preview fixture')
        write('library/previews/fixed.png','fixed preview fixture')
        self.data={'layouts':{'panels':{'title':'Panels','source':'library/layouts/panels.tex','palette':'light',
                  'topic':'Cards','fields':[{'name':'caption','type':'text'}],'example_slide':'example'}},
                  'slides':{'example':{'source':'library/slides/example.tex','layout':'panels','status':'in review',
                            'fields':{'caption':r'Two\\\\lines'}},
                            'fixed':{'source':'library/slides/fixed.tex','layout':'panels','preset':'fixed','status':'in review'}},
                  'presets':{'fixed':{'title':'Fixed','source':'library/layouts/fixed.tex','slide':'fixed','status':'in review'}}}
        self.save()

    def save(self):self.write('library/index.json',json.dumps(self.data))

    def test_retained_commands_match_their_preview_source_and_fixed_policy(self):
        rows={row['id']:row for row in slide_guide.catalogue(self.root)['rows']}
        self.assertEqual(rows['panels']['choices'][0]['command'],r'\studiotemplate[caption={Two\\lines}]{panels}')
        self.assertEqual(rows['fixed']['choices'][0]['command'],r'\studiotemplate{fixed}')
        self.assertEqual(rows['fixed']['choices'][0]['fields'],[])
        self.assertIn('palette={blue}',rows['cover']['choices'][0]['command'])

    def test_copyable_command_uses_one_preferred_name_per_native_field(self):
        path=self.root/'templates/models.json';models=json.loads(path.read_text())
        models['models'][0]['variants'][0]['compositions'][0]['fields']['heading-title']='title'
        path.write_text(json.dumps(models))
        choice=slide_guide.catalogue(self.root)['rows'][0]['choices'][0]
        self.assertIn('heading-title={Presentation title}',choice['command'])
        self.assertNotIn('\n  title={',choice['command'])
        self.assertEqual(choice['fields'][0]['name'],'heading-title')

    def test_read_only_check_detects_source_and_preview_changes(self):
        slide_guide.sync(self.root)
        target=self.root/'docs/slides/catalogue.js';before=target.read_bytes()
        self.write('templates/studio/cover.tex','% Updated shared template\n')
        with self.assertRaisesRegex(ValueError,'Stale unified slide guide'):slide_guide.sync(self.root,check=True)
        self.assertEqual(before,target.read_bytes())
        slide_guide.sync(self.root)
        self.write('docs/templates/previews/cover.png','new preview')
        with self.assertRaisesRegex(ValueError,'Stale unified slide guide'):slide_guide.sync(self.root,check=True)

    def test_core_and_lesson_preview_updates_refresh_the_same_guide(self):
        slide_guide.sync(self.root)
        self.write('docs/templates/previews/cover.png','new core preview')
        studio_preview.save_manifest(self.root,{'schema':2,'models':{},'previews':{}})
        slide_guide.sync(self.root,check=True)
        self.write('library/previews/example.png','new lesson preview')
        library.save_preview_records(self.root,{'example':{'fingerprint':'fixture'}})
        slide_guide.sync(self.root,check=True)
        self.assertFalse((self.root/'library/previews/manifest.lock').exists())

    def test_retired_and_core_layouts_are_not_duplicated(self):
        self.data['layouts']['retired']={'replaced_by':'panels'}
        self.data['layouts']['shared']={'registration':'shared core'}
        self.save()
        self.assertEqual([r['id'] for r in slide_guide.catalogue(self.root)['rows']],['cover','panels','fixed'])

    def test_current_collection_has_every_retained_composition_once(self):
        result=slide_guide.catalogue(ROOT)
        core={e['id'] for e in json.loads((ROOT/'templates/index.json').read_text())['templates']}
        rows=result['rows'];actual=[c['id'] for row in rows if row['kind']=='studio' for c in row['choices']]
        self.assertEqual(set(actual),core);self.assertEqual(len(actual),len(core))
        self.assertEqual(len({row['id'] for row in rows}),len(rows))
        self.assertTrue(all(c['preview']['available'] for row in rows for c in row['choices']))
        pair=next(c for row in rows for c in row['choices'] if c['id']=='two-cards')
        graphics=[f for f in pair['fields'] if f['type']=='graphic']
        self.assertTrue(all(f['box'][2:]==[260.0,260.0] for f in graphics))

    def test_browser_filter_and_pagination_are_bounded(self):
        node=shutil.which('node')
        if not node:self.skipTest('Node is optional outside browser checks.')
        script=r'''
const assert=require('node:assert/strict');
const guide=require(process.argv[1]);
const rows=Array.from({length:30},(_,i)=>({id:'slide-'+i,title:'Example '+i,family:i%2?'Cards':'Opening',kind:'studio',featured:i<3,choices:[{id:'slide-'+i,label:'blue',fields:[{name:'title'}]}]}));
assert.equal(guide.matches(rows,'','featured').length,3);
assert.equal(guide.matches(rows,'title','all','Cards').length,15);
assert.equal(guide.matches(rows,'not present').length,0);
assert.equal(guide.pageRows(rows,0).length,12);
assert.equal(guide.pageRows(rows,2).length,6);
assert.equal(guide.pageRows(rows,3).length,0);
'''
        subprocess.run([node,'-e',script,str(ROOT/'docs/slides/guide.js')],check=True,capture_output=True,text=True)


if __name__=='__main__':unittest.main()
