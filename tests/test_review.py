"""Verify review state, dependency isolation, portable caching and release gates."""
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import review
import studio_review
import studio_preview
import studio_templates
import studio_models
import package
import release


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.entries = studio_templates.inspect_templates(ROOT)

    def test_review_pdf_uses_the_editor_aware_build_viewer(self):
        pdf = ROOT / 'build/review/batches/comparisons.pdf'
        with mock.patch.object(review.build, 'open_pdf') as open_pdf:
            review.open_pdf(pdf)
        open_pdf.assert_called_once_with(pdf)

    def test_single_ledger_retains_selection_and_drives_generated_sheet(self):
        data = studio_review.load_review(ROOT)
        self.assertEqual(len(data['templates']),194)
        self.assertEqual(len(data['selection']),24)
        metadata = json.loads((ROOT/'templates/index.json').read_text(encoding="utf-8"))
        self.assertTrue(all('status' not in entry for entry in metadata['templates']))
        rows = list(csv.DictReader(io.StringIO(studio_review.review_csv(ROOT,self.entries))))
        self.assertEqual(len(rows),194)
        for row in rows:
            item = data['templates'][row['id']]
            self.assertEqual(row['status'],item['status'])
            self.assertEqual(row['requested_changes'],item['notes'])

    def test_notes_and_selection_order_survive_csv_generation(self):
        data = studio_review.load_review(ROOT)
        data['templates']['cover']['notes'] = 'Move right, then review.\nKeep the title.'
        data['selection'][1:3] = reversed(data['selection'][1:3])
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'templates').mkdir()
            (root/'templates/review.json').write_text(json.dumps(data), encoding="utf-8")
            text=studio_review.review_csv(root,self.entries)
            rows={r['id']:r for r in csv.DictReader(io.StringIO(text))}
            self.assertEqual(rows['cover']['requested_changes'],data['templates']['cover']['notes'])
            self.assertEqual([e['id'] for e in studio_review.selected(root,self.entries)],data['selection'])
            self.assertEqual(studio_review.load_review(root,self.entries),data)

    def test_single_slide_preserves_full_catalogue_number(self):
        entry=next(e for e in self.entries if e['id']=='three-cards')
        source=review.single_document(entry,37)
        self.assertIn(r'\setcounter{framenumber}{36}',source)
        self.assertEqual(source.count(r'\studiotemplate{three-cards}'),1)

    def test_unknown_status_and_missing_model_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'templates').mkdir()
            data=studio_review.load_review(ROOT)
            data['templates']['cover']['status']='automatically approved'
            (root/'templates/review.json').write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,'Invalid review status'):
                studio_review.load_review(root,self.entries)
            del data['templates']['cover']
            (root/'templates/review.json').write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,'every current composition'):
                studio_review.load_review(root,self.entries)

    def test_source_edit_invalidates_only_its_model_and_notes_do_not(self):
        before=studio_preview.input_sets(ROOT,self.entries)
        actual=studio_preview.digest
        changed=ROOT/'templates/studio/three-cards.tex'
        with mock.patch('studio_preview.digest',side_effect=lambda path:'edited' if path==changed else actual(path)):
            after=studio_preview.input_sets(ROOT,self.entries)
        self.assertEqual([name for name in before if before[name]!=after[name]],['three-cards'])
        changed_entries=[dict(entry,status='approved',review_notes='Please adjust this',notes='Review only') for entry in self.entries]
        self.assertEqual(before,studio_preview.input_sets(ROOT,changed_entries))

    def test_dedicated_root_code_file_invalidates_its_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('.latexmkrc','assets/generated/catalogue.tex','images/bitpolito/bull-white.pdf','images/bitpolito/polito-coat-of-arms-white.pdf','templates/studio/custom.tex'):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'fixture')
            (root/'snippet.txt').write_text('first version', encoding="utf-8")
            entry={'id':'custom','source':'templates/studio/custom.tex','parts':[],
                   'fields':[{'name':'code-file','type':'file','default':'snippet.txt'}]}
            before=studio_preview.input_sets(root,[entry])
            (root/'snippet.txt').write_text('edited code', encoding="utf-8")
            after=studio_preview.input_sets(root,[entry])
            self.assertNotEqual(before['custom'],after['custom'])
            self.assertIn('snippet.txt',before['custom'])

    def test_shared_part_invalidates_exactly_its_dependents(self):
        before=studio_preview.input_sets(ROOT,self.entries)
        name=next(e for e in self.entries if e['id']=='three-cards')['parts'][0]
        changed=next(ROOT/'images/studio'/folder/(name+'.pdf') for folder in ('parts','collection') if (ROOT/'images/studio'/folder/(name+'.pdf')).is_file())
        actual=studio_preview.digest
        with mock.patch('studio_preview.digest',side_effect=lambda path:'edited' if path==changed else actual(path)):
            after=studio_preview.input_sets(ROOT,self.entries)
        expected={e['id'] for e in self.entries if name in e.get('parts',[])}
        self.assertEqual({key for key in before if before[key]!=after[key]},expected)

    def test_single_slide_cache_skips_unchanged_compile_and_thumbnail(self):
        entry=next(e for e in self.entries if e['id']=='three-cards')
        with tempfile.TemporaryDirectory(prefix='BitBeamer review cache ') as directory:
            root=Path(directory)
            def compile_pdf(root,doc,out,backend,image,force=False):
                path=out/'slide.pdf';path.write_bytes(b'pdf');return path
            def render(root,pdf,target,*args):
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(b'png')
            with mock.patch.object(review,'compile_document',side_effect=compile_pdf) as compile_call, mock.patch.object(review,'thumbnail',side_effect=render) as thumbnail_call:
                review.render_slide(root,entry,9,{'source':'one'},'native','test')
                review.render_slide(root,entry,9,{'source':'one'},'native','test')
                self.assertEqual(compile_call.call_count,1)
                self.assertEqual(thumbnail_call.call_count,1)
                review.render_slide(root,entry,9,{'source':'two'},'native','test')
                self.assertEqual(compile_call.call_count,2)
                self.assertEqual(thumbnail_call.call_count,2)
                (root/'build/review/slides/three-cards/slide.pdf').write_bytes(b'corrupted local PDF')
                review.render_slide(root,entry,9,{'source':'two'},'native','test')
                self.assertEqual(compile_call.call_count,3)
                self.assertTrue(compile_call.call_args.kwargs['force'])

    def test_stable_release_stops_before_building_unapproved_selection(self):
        with mock.patch.object(release.build,'main') as compile_call:
            with self.assertRaisesRegex(RuntimeError,'explicit approval'):
                release.release(ROOT,style='studio')
            compile_call.assert_not_called()
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'stable.zip';target.write_bytes(b'old artifact')
            with self.assertRaisesRegex(RuntimeError,'explicit approval'):
                package.package(ROOT,target,style='studio')
            self.assertEqual(target.read_bytes(),b'old artifact')

    def test_explicit_approval_is_required_for_every_selected_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);shutil.copytree(ROOT/'templates',root/'templates')
            data=studio_review.load_review(root)
            for name in [item['id'] for item in studio_review.package_selection(root)]:
                data['templates'][name]['status']='approved'
                for review in data['templates'][name].get('palette_reviews',{}).values():review['status']='approved'
            (root/'templates/review.json').write_text(json.dumps(data), encoding="utf-8")
            studio_review.require_approved(root)
            data['templates'][data['selection'][-1]]['status']='changes requested'
            (root/'templates/review.json').write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,'closing'):
                studio_review.require_approved(root)

    def test_oversized_package_preserves_previous_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'project.zip';target.write_bytes(b'previous')
            with self.assertRaisesRegex(RuntimeError,'budget'):
                package.write_archive(target,{'main.tex':b'x'*1000},budget=100)
            self.assertEqual(target.read_bytes(),b'previous')
            self.assertFalse(target.with_name('project.zip.tmp').exists())

    def test_compact_package_contains_only_selection_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            target=package.package(ROOT,Path(directory)/'studio.zip',style='studio',review=True)
            with ZipFile(target) as archive:
                sources={name for name in archive.namelist() if name.startswith('templates/studio/') and name.endswith('.tex') and not name.endswith('/registry.tex')}
                selected={item['id'] for item in studio_review.package_selection(ROOT)}
                entries=[e for e in studio_templates.inspect_templates(ROOT) if e['id'] in selected]
                expected={e['source'] for e in entries}
                expected.update(name for name in studio_models.dependencies(ROOT,entries) if name.startswith('templates/studio/') and name.endswith('.tex'))
                self.assertEqual(sources,expected)
                self.assertIn('assets/generated/catalogue.tex',archive.namelist())
                self.assertLess(target.stat().st_size,package.BUDGET)
                self.assertNotIn('templates/studio/photo-triptych.tex',archive.namelist())
                self.assertEqual(len([n for n in archive.namelist() if n.startswith('guides/')]),len(studio_review.package_selection(ROOT)))

    def test_parts_gallery_has_no_initial_image_or_article_nodes(self):
        from html.parser import HTMLParser
        class Tags(HTMLParser):
            def __init__(self):super().__init__();self.tags=[]
            def handle_starttag(self,tag,attrs):self.tags.append(tag)
        page=(ROOT/'docs/studio-parts/index.html').read_text(encoding="utf-8")
        parser=Tags();parser.feed(page)
        self.assertNotIn('img',parser.tags)
        self.assertNotIn('article',parser.tags)
        self.assertIn('pageSize=24',page)

    @unittest.skipUnless(shutil.which('node'),'Optional JavaScript runtime is not installed')
    def test_parts_pagination_search_empty_result_and_copy(self):
        import subprocess
        script = r"""
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const parts=JSON.parse(html.split('id="parts-data">')[1].split('</script>')[0]);
function element(tag){return {tag,children:[],dataset:{},value:'',append(...items){this.children.push(...items)},replaceChildren(){this.children=[]},addEventListener(name,fn){this['on'+name]=fn}}}
const main=element('main'),search=element('input'),count=element('p');
const previous={dataset:{page:'-1'}},next={dataset:{page:'1'}};let copied='';
const selectors={'main':main,'#search':search,'#count':count,'#parts-data':{textContent:JSON.stringify(parts)}};
const context={document:{querySelector(s){return selectors[s]},querySelectorAll(){return [previous,next]},createElement:element,createTextNode(s){return s}},window:{scrollTo(){}},navigator:{clipboard:{async writeText(s){copied=s}}}};
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),context);
assert.equal(main.children.length,24);assert.equal(previous.disabled,true);
const first=main.children[0].children[0].alt;
next.onclick();assert.equal(main.children.length,24);assert.notEqual(main.children[0].children[0].alt,first);
search.value='no-such-reference';search.oninput();assert.equal(main.children.length,0);assert.equal(next.disabled,true);
search.value=parts[0].reference;search.oninput();assert.ok(main.children.length>0 && main.children.length<=24);
assert.ok(count.textContent.includes('Page 1 /'));
(async()=>{await main.children[0].children.find(e=>e.tag==='button').onclick();assert.equal(copied,'\\studiopart[width=3cm]{'+main.children[0].children[0].alt+'}')})().catch(e=>{throw e});
"""
        subprocess.run([shutil.which('node'),'-e',script,str(ROOT/'docs/studio-parts/index.html'),str(ROOT/'scripts/studio-parts-gallery.js')],check=True)


if __name__ == '__main__':unittest.main()
