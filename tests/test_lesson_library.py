"""Offline lesson imports must preserve source files and personal work."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import deck
import lesson_library as library


class LessonLibraryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='BitBeamer lessons ');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name).resolve();(self.root/'library/slides').mkdir(parents=True)
        (self.root/'library/layouts').mkdir();(self.root/'library/references').mkdir();(self.root/'library/parts').mkdir()
        (self.root/'start-studio.tex').write_text('\\documentclass{beamer}\n\\usetheme{bitpolito-studio}\n\\begin{document}\n\\closingframe\n\\end{document}\n')
        (self.root/'library/parts/panel.pdf').write_bytes(b'prepared test graphic')
        (self.root/'library/layouts/sample.tex').write_text('\\includegraphics{library/parts/panel.pdf}')
        (self.root/'library/references/lesson-source.bib').write_text('@misc{lesson-source,title={Synthetic source fixture}}\n')
        for name in ('cover','first','second','closing'):
            (self.root/f'library/slides/{name}.tex').write_text('\\studiotemplate{official-layout-sample}')
        resources={p:hashlib.sha256((self.root/p).read_bytes()).hexdigest() for p in ('library/parts/panel.pdf','library/layouts/sample.tex')}
        self.data={'schema':1,'sources':[{'id':'official','page_count':4,'pages':[{'page':i,'slide':s} for i,s in enumerate(('cover','first','second','closing'),1)]}],
          'references':{'lesson-source':{'source':'library/references/lesson-source.bib'}},
          'slides':{s:{'source':f'library/slides/{s}.tex','layout':'official-layout-sample','layout_source':'library/layouts/sample.tex','status':'in review','resources':resources,'references':['lesson-source'],'role':s if s in ('cover','closing') else 'content','origins':[{'source':'official','page':i}]} for i,s in enumerate(('cover','first','second','closing'),1)},
          'decks':{'intro':{'title':'Introduction','audience':'Beginners','status':'in review','slides':['cover','first','closing']}},
          'blocks':{'hashing':{'title':'Hashing','audience':'Beginners','status':'in review','slides':['second']}}}
        self.save()

    def save(self):
        (self.root/'library/index.json').write_text(json.dumps(self.data))

    def create(self,name='my-talk',from_library=None):
        with contextlib.redirect_stdout(io.StringIO()):return deck.create_deck(self.root,name,from_library=from_library)

    def test_full_copy_has_no_content_dependency_on_library(self):
        project=self.create(from_library='intro')
        self.assertIn('presentations/my-talk/slides/first.tex',(project/'main.tex').read_text())
        self.assertNotIn('library/slides/',(project/'main.tex').read_text())
        layout=(project/'layouts/sample.tex').read_text()
        self.assertIn('presentations/my-talk/assets/',layout)
        self.assertNotIn('library/parts/',layout)
        self.assertTrue((project/'references.bib').is_file())
        self.assertTrue((project/'assets').is_dir())
        self.assertIn(library.MARKER,(project/'main.tex').read_text())
        with self.assertRaisesRegex(ValueError,'Already exists'):self.create(from_library='intro')

    def test_block_inserts_before_closing_and_keeps_copies_independent(self):
        project=self.create();original=(self.root/'library/slides/second.tex').read_bytes()
        count=library.add_block(self.root,project,'hashing');self.assertEqual(count,1)
        text=(project/'main.tex').read_text()
        self.assertLess(text.index('slides/second.tex'),text.index('\\closingframe'))
        self.assertIn('bitpolitostudiolibrary',text)
        self.assertIn('biblatex',text)
        self.assertIn('lesson-source',(project/'references.bib').read_text())
        (project/'slides/second.tex').write_text('personal edit')
        self.assertEqual((self.root/'library/slides/second.tex').read_bytes(),original)
        with self.assertRaisesRegex(ValueError,'already imported'):library.add_block(self.root,project,'hashing')

    def test_missing_marker_does_not_copy_any_files(self):
        project=self.create();main=project/'main.tex';main.write_text(main.read_text().replace(library.MARKER,''));before={p.relative_to(project):p.read_bytes() for p in project.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(ValueError,'insertion marker'):library.add_block(self.root,project,'hashing')
        self.assertEqual(before,{p.relative_to(project):p.read_bytes() for p in project.rglob('*') if p.is_file()})

    def test_asset_collision_is_rejected_before_main_or_bibliography_changes(self):
        project=self.create();(project/'layouts').mkdir();(project/'layouts/sample.tex').write_text('my own layout')
        before=(project/'main.tex').read_bytes()
        with self.assertRaisesRegex(ValueError,'collision'):library.add_block(self.root,project,'hashing')
        self.assertEqual((project/'main.tex').read_bytes(),before)
        self.assertFalse((project/'library-imports.json').exists())

    def test_bibliography_collision_is_rejected(self):
        project=self.create();(project/'references.bib').write_text('@misc{lesson-source,title={Personal reference}}')
        with self.assertRaisesRegex(ValueError,'Bibliography key collision'):library.add_block(self.root,project,'hashing')
        self.assertFalse((project/'slides').exists())

    def test_failed_write_rolls_back_existing_files(self):
        project=self.create();main=project/'main.tex';before=main.read_bytes();other=project/'new.tex';write=Path.write_bytes
        def failing(path,content):
            if path==other:raise OSError('simulated failure')
            return write(path,content)
        with mock.patch.object(Path,'write_bytes',failing):
            with self.assertRaises(OSError):library.commit_files(project,{main:b'changed',other:b'new'})
        self.assertEqual(main.read_bytes(),before);self.assertFalse(other.exists())

    def test_traversal_and_changed_prepared_resources_fail_offline(self):
        self.assertEqual(library.validate(self.root)['source_pages'],4)
        with self.assertRaisesRegex(ValueError,'Invalid library resource'):library.safe_file(self.root,'../outside.tex')
        (self.root/'library/parts/panel.pdf').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Changed library resource'):library.validate(self.root)

    def test_wrapper_pages_cannot_enter_content_blocks(self):
        self.data['blocks']['hashing']['slides']=['closing'];self.save()
        with self.assertRaisesRegex(ValueError,'wrapper'):library.validate(self.root)

    def test_all_source_pages_must_have_a_destination(self):
        self.data['sources'][0]['pages'].pop();self.save()
        with self.assertRaisesRegex(ValueError,'Incomplete source-page'):library.validate(self.root)

    def test_language_alias_copies_the_canonical_english_lesson(self):
        self.data['aliases']={'italian-source':'intro'};self.save()
        self.assertEqual(library.catalogue(self.root,deck='italian-source')['id'],'intro')
        project=self.create(from_library='italian-source')
        self.assertEqual(json.loads((project/'library-imports.json').read_text())['deck'],'intro')

    def test_edited_registration_is_not_overwritten_by_a_block_import(self):
        project=self.create(from_library='intro');path=project/'library-layouts.tex'
        path.write_text(path.read_text()+'% Personal registration\n');before=path.read_bytes()
        with self.assertRaisesRegex(ValueError,'registration collision'):library.add_block(self.root,project,'hashing')
        self.assertEqual(path.read_bytes(),before)

    def test_a_lesson_without_a_closing_page_keeps_its_final_content(self):
        self.data['slides']['closing']['role']='content';self.save()
        project=self.create(from_library='intro');text=(project/'main.tex').read_text()
        self.assertLess(text.index('slides/closing.tex'),text.index(library.MARKER))
        self.assertLess(text.index(library.MARKER),text.index(r'\end{document}'))

    def test_discovery_and_unknown_ids(self):
        summary=library.catalogue(self.root);self.assertEqual(summary['decks'][0]['slide_count'],3)
        self.assertEqual(library.catalogue(self.root,block='hashing')['slide_details'][0]['id'],'second')
        with self.assertRaisesRegex(ValueError,'Unknown library'):library.catalogue(self.root,deck='missing')
        with self.assertRaisesRegex(ValueError,'requires Studio'):deck.create_deck(self.root,'academic','academic',from_library='intro')


class LessonCacheTests(unittest.TestCase):
    setUp=LessonLibraryTests.setUp
    save=LessonLibraryTests.save
    def test_fingerprint_ignores_notes_but_tracks_content_and_dependencies(self):
        import library as maintenance
        initial=maintenance.fingerprint(self.root,['first'],self.data)
        self.data['slides']['first']['review_notes']=['Please check alignment.']
        self.data['decks']['intro']['status']='changes requested'
        self.assertEqual(initial,maintenance.fingerprint(self.root,['first'],self.data))
        (self.root/'library/slides/second.tex').write_text('Unrelated block change')
        self.assertEqual(initial,maintenance.fingerprint(self.root,['first'],self.data))
        (self.root/'library/parts/panel.pdf').write_bytes(b'updated shared graphic')
        self.assertNotEqual(initial,maintenance.fingerprint(self.root,['first'],self.data))

    def test_prepare_tracks_changed_retained_sources_without_original_exports(self):
        import library as maintenance
        source=self.root/'library/parts/panel.svg';source.write_text('<svg>old</svg>')
        target=source.with_suffix('.pdf');manifest=self.root/'library/parts/manifest.json'
        manifest.write_text(json.dumps({'parts':{'panel':{'source':'library/parts/panel.svg','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pdf':'library/parts/panel.pdf','pdf_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'dependencies':{}}}}))
        source.write_text('<svg>changed</svg>')
        def convert(name):
            Path(name).with_suffix('.pdf').write_bytes(b'new prepared vector')
            return name
        with mock.patch('concurrent.futures.ProcessPoolExecutor') as executor, mock.patch.object(maintenance,'prepare_part',side_effect=convert) as converter, contextlib.redirect_stdout(io.StringIO()):
            executor.return_value.__enter__.return_value.map.side_effect=lambda worker,items:map(worker,items)
            maintenance.prepare(self.root,backend='native')
            converter.assert_called_once_with(str(source))
            converter.reset_mock()
            maintenance.prepare(self.root,backend='native')
            converter.assert_not_called()
        record=json.loads(manifest.read_text())['parts']['panel']
        self.assertEqual(record['source_sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(record['pdf_sha256'],hashlib.sha256(target.read_bytes()).hexdigest())


class LessonDependencyTests(unittest.TestCase):
    setUp=LessonLibraryTests.setUp
    save=LessonLibraryTests.save

    def test_retained_svg_cannot_depend_on_network_or_unlisted_images(self):
        source=self.root/'library/parts/panel.svg';target=source.with_suffix('.pdf')
        for href,expected in [('https://example.invalid/image.png','External'),('unlisted.png','Unlisted')]:
            with self.subTest(href=href):
                source.write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="'+href+'"/></svg>')
                part={'source':'library/parts/panel.svg','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pdf':'library/parts/panel.pdf','pdf_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'dependencies':{}}
                (self.root/'library/parts/manifest.json').write_text(json.dumps({'parts':{'panel':part}}))
                with self.assertRaisesRegex(ValueError,expected+' retained SVG dependency'):
                    library.validate(self.root)


class FixedLessonTests(unittest.TestCase):
    setUp=LessonLibraryTests.setUp
    save=LessonLibraryTests.save
    create=LessonLibraryTests.create

    def test_fixed_preset_copy_registers_its_underlying_layout_independently(self):
        source='library/layouts/fixed-example.tex'
        (self.root/source).write_text('\\studiotemplate{official-layout-sample}')
        self.data['presets']={'fixed-example':{'source':source,'slide':'first','slides':['first'],'fields':[],'content_mode':'fixed'}}
        slide=self.data['slides']['first'];slide['preset']='fixed-example';slide['resources'][source]=hashlib.sha256((self.root/source).read_bytes()).hexdigest()
        (self.root/slide['source']).write_text('\\studiotemplate{fixed-example}')
        self.save();project=self.create(from_library='intro')
        registrations=(project/'library-layouts.tex').read_text()
        self.assertIn('{fixed-example}',registrations)
        self.assertIn('{official-layout-sample}',registrations)
        self.assertTrue((project/'layouts/fixed-example.tex').is_file())
        self.assertNotIn('library/layouts/',registrations)
        library.validate(self.root)


class SharedTemplatePropagationTests(unittest.TestCase):
    setUp=LessonLibraryTests.setUp
    save=LessonLibraryTests.save
    create=LessonLibraryTests.create

    def shared_component(self):
        component='library/layouts/components.tex'
        (self.root/component).write_text(r'\includegraphics{library/parts/panel.pdf}')
        (self.root/'library/layouts/sample.tex').write_text(r'\input{library/layouts/components}')
        for slide in self.data['slides'].values():
            slide['resources']=dict(slide['resources'])
            slide['resources']['library/layouts/sample.tex']=hashlib.sha256((self.root/'library/layouts/sample.tex').read_bytes()).hexdigest()
        self.save()
        return component

    def test_nested_component_changes_invalidate_every_consumer_only(self):
        import library as maintenance
        component=self.shared_component()
        (self.root/'library/layouts/other.tex').write_text('% Unrelated composition\n')
        self.data['slides']['second'].update(layout='other',layout_source='library/layouts/other.tex',resources={})
        (self.root/'library/slides/second.tex').write_text(r'\studiotemplate{other}')
        before={sid:maintenance.fingerprint(self.root,[sid],self.data) for sid in ('first','cover','second')}
        (self.root/component).write_text((self.root/component).read_text()+'\n% Updated shared panel geometry\n')
        for sid in ('first','cover'):
            self.assertNotEqual(before[sid],maintenance.fingerprint(self.root,[sid],self.data))
        self.assertEqual(before['second'],maintenance.fingerprint(self.root,['second'],self.data))
        self.save()
        report=maintenance.affected(self.root,[component])
        self.assertEqual(set(report['slides']),{'first','cover','closing'})
        self.assertEqual(set(report['decks']),{'intro'})
        self.assertEqual(report['blocks'],{})

    def test_import_copies_new_indirect_dependencies_and_keeps_snapshot(self):
        component=self.shared_component()
        project=self.create(from_library='intro')
        local=project/'layouts/components.tex';before=local.read_bytes()
        self.assertIn('presentations/my-talk/assets/',local.read_text())
        self.assertIn('presentations/my-talk/layouts/components.tex',(project/'layouts/sample.tex').read_text())
        (self.root/component).write_text('% New shared version\n')
        self.assertEqual(local.read_bytes(),before)

    def test_unregistered_nested_component_is_reported_without_modifying_registry(self):
        component=self.shared_component();before=(self.root/'library/index.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'unregistered dependencies.*components.tex'):
            library.validate(self.root)
        self.assertEqual(before,(self.root/'library/index.json').read_bytes())
        self.assertIn(component,library.source_dependencies(self.root,self.data['slides']['first']))

    def test_source_call_cannot_bypass_registered_template_even_with_nested_options(self):
        source=self.root/'library/slides/first.tex'
        source.write_text('% \\studiotemplate{old-example}\n'+r'\studiotemplate[title={A {nested} [value]},graphic-one={\asset[width=1cm]{alice}}]{official-layout-sample}')
        library.validate_binding(self.root,self.data,'first')
        source.write_text(r'\studiotemplate{unreviewed-copy}')
        with self.assertRaisesRegex(ValueError,'canonical template official-layout-sample'):
            self.create(from_library='intro')
        self.assertFalse((self.root/'presentations/my-talk').exists())

    def test_known_replaced_layout_cannot_return_to_a_lesson(self):
        self.data['layouts']={'official-layout-sample':{'replaced_by':'canonical-layout'}}
        with self.assertRaisesRegex(ValueError,'replaced by canonical-layout'):
            library.validate_binding(self.root,self.data,'first')

    def test_declared_family_rejects_a_duplicate_and_missing_shared_component(self):
        self.data['layouts']={'official-layout-sample':{'source':'library/layouts/sample.tex'},'duplicate':{}}
        self.data['reuse_rules']={'two-panels':{'layout':'official-layout-sample','slides':['first'],
                                  'required_dependencies':['library/layouts/components.tex']}}
        with self.assertRaisesRegex(ValueError,'shared components missing'):
            library.validate_binding(self.root,self.data,'first')
        self.data['slides']['first']['layout']='duplicate'
        (self.root/'library/slides/first.tex').write_text(r'\studiotemplate{duplicate}')
        with self.assertRaisesRegex(ValueError,'composition two-panels must reuse'):
            library.validate_binding(self.root,self.data,'first')

    def test_unused_resource_registration_cannot_fake_component_reuse(self):
        component='library/layouts/components.tex'
        (self.root/component).write_text('% Shared helper not actually loaded\n')
        self.data['slides']['first']['resources']=dict(self.data['slides']['first']['resources'])
        self.data['slides']['first']['resources'][component]=hashlib.sha256((self.root/component).read_bytes()).hexdigest()
        self.data['reuse_rules']={'panels':{'layout':'official-layout-sample','slides':['first'],
                                          'required_dependencies':[component]}}
        with self.assertRaisesRegex(ValueError,'shared components missing'):
            library.validate_binding(self.root,self.data,'first')


    def test_extensionless_graphics_are_discovered_and_rewritten_in_personal_copies(self):
        (self.root/'art').mkdir();(self.root/'art/local.pdf').write_bytes(b'prepared local drawing')
        (self.root/'library/layouts/sample.tex').write_text(r'\includegraphics[width=2cm]{art/local}')
        project=self.create(from_library='intro')
        layout=(project/'layouts/sample.tex').read_text()
        self.assertIn('presentations/my-talk/assets/',layout)
        self.assertNotIn('{art/local}',layout)
        self.assertTrue(any(path.read_bytes()==b'prepared local drawing' for path in (project/'assets').glob('*.pdf')))


if __name__=='__main__':unittest.main()
