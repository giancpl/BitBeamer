"""Check pending-only review PDFs, canonical categories and opening behavior."""
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import review_batch
try:
    import pymupdf as fitz
except ImportError:
    fitz=None


class ReviewBatchOpeningTests(unittest.TestCase):
    def test_open_targets_the_combined_pdf_or_single_comparison(self):
        for batch in ('all', 'closing-01'):
            with self.subTest(batch=batch):
                target = ROOT / 'build/review/batches' / ('comparisons.pdf' if batch == 'all' else 'closing-01/main.pdf')
                with mock.patch.object(review_batch, 'combine', return_value=target), \
                        mock.patch.object(review_batch, 'prepare', return_value=target), \
                        mock.patch.object(review_batch.build, 'open_pdf') as open_pdf:
                    self.assertEqual(review_batch.main([batch, '--compare', '--open']), 0)
                expected = target if batch == 'all' else target.parent / 'comparisons.pdf'
                open_pdf.assert_called_once_with(expected)

    def test_direct_approved_batch_does_not_compile_a_stale_review(self):
        payload={'rows':[{'family':'Covers','choices':[{'id':'cover','status':'approved'}]}]}
        batches=[{'id':'covers','family':'Covers','compositions':['cover']}]
        with mock.patch.object(review_batch,'catalogue',return_value=payload), \
                mock.patch.object(review_batch,'review_batches',return_value=batches), \
                mock.patch.object(review_batch.build,'main') as compiled:
            with self.assertRaisesRegex(ValueError,'No compositions pending review'):
                review_batch.prepare(ROOT,'covers',compare=True)
            compiled.assert_not_called()


@unittest.skipIf(fitz is None,'Optional PDF maintenance dependency is unavailable')
class ReviewBatchTests(unittest.TestCase):
    def test_combined_pdf_excludes_approved_core_and_fixed_compositions(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            batches=[{'id':'first','family':'Covers','compositions':['cover','photo','wordmark']},
                     {'id':'second','family':'Statements','compositions':['four','five']},
                     {'id':'third','family':'Closing','compositions':['closing']}]
            payload={'rows':[
                {'family':'Covers','kind':'studio','choices':[{'id':'cover','status':'approved'},{'id':'photo','status':'in review'}]},
                {'family':'Covers','kind':'fixed','choices':[{'id':'wordmark','status':'approved'}]},
                {'family':'Statements','kind':'studio','choices':[{'id':'four','status':'changes requested'},{'id':'five','status':'approved'}]},
                {'family':'Closing','kind':'studio','choices':[{'id':'closing','status':'approved'}]}]}
            def prepare(root,name,*args):
                folder=root/'build/review/batches'/name;folder.mkdir(parents=True,exist_ok=True)
                with fitz.open() as document:
                    for item in {'first':['photo'],'second':['four']}[name]:
                        page=document.new_page(width=1400,height=460)
                        page.insert_text((20,22),'1 / 1 | '+item,fontsize=13)
                        page.insert_text((710,46),'Current template',fontsize=10)
                    document.save(folder/'comparisons.pdf')
                return folder/'main.pdf'
            with mock.patch.object(review_batch,'catalogue',return_value=payload), \
                    mock.patch.object(review_batch,'review_batches',return_value=batches), \
                    mock.patch.object(review_batch,'prepare',side_effect=prepare) as prepared:
                result=review_batch.combine(root,compare=True)
            self.assertEqual([call.args[1] for call in prepared.call_args_list],['first','second'])
            with fitz.open(result) as document:
                self.assertEqual(len(document),2)
                for number,(page,item,category) in enumerate(zip(document,['photo','four'],['Covers','Statements']),1):
                    text=page.get_text()
                    self.assertIn(item,text)
                    self.assertIn(str(number)+' / 2',text)
                    self.assertIn(category,text)
                    self.assertIn('Current template',text)
                self.assertEqual(document.get_toc(),[[1,'Covers',1],[2,'photo',1],[1,'Statements',2],[2,'four',2]])
            import json
            report=json.loads((root/'build/review/batches/all-report.json').read_text())
            self.assertEqual(report['pending'],[{'id':'photo','category':'Covers','batch':'first'},
                                                {'id':'four','category':'Statements','batch':'second'}])
            (root/'templates').mkdir()
            (root/'templates/review.json').write_text(json.dumps({'active_review_batches':['second']}))
            with mock.patch.object(review_batch,'catalogue',return_value=payload), \
                    mock.patch.object(review_batch,'review_batches',return_value=batches), \
                    mock.patch.object(review_batch,'prepare',side_effect=prepare) as prepared:
                result=review_batch.combine(root,compare=True)
            self.assertEqual([call.args[1] for call in prepared.call_args_list],['second'])
            with fitz.open(result) as document:
                self.assertEqual(len(document),1)
                self.assertIn('four',document[0].get_text())
                self.assertNotIn('photo',document[0].get_text())


    @unittest.skipUnless(shutil.which('pdftocairo'), 'Poppler required for comparison raster checks')
    def test_comparison_prints_the_invocation_used_for_the_reviewed_example(self):
        import json
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'build/review/batches/columns';folder.mkdir(parents=True)
            Image.new('RGB',(16,9),'white').save(root/'original.png')
            (root/'templates').mkdir()
            (root/'templates/figma-inventory.json').write_text(json.dumps({'frames':[{'id':'figma-0021','file':'1900.svg'}]}))
            index=root/'build/checks/slide-guide/comparisons.js';index.parent.mkdir(parents=True)
            index.write_text('window.BITBEAMER_COMPARISONS='+json.dumps({'records':{
                'columns':{'variants':[{'label':'figma-0021','original':'../../original.png'}]}}})+';')
            with fitz.open() as replica:
                page=replica.new_page(width=800,height=450)
                page.draw_rect(page.rect,fill=(249/255,)*3,color=None)
                page.insert_text((20,20),'Current layout')
                replica.save(folder/'main.pdf')
            invocation=r'\studiotemplate[title={Reviewed example},left-title={Left heading},right-title={Right heading}]{two-columns}'
            with mock.patch('guide_comparisons.sync'):
                review_batch.comparisons(root,folder,['columns'],
                    {'columns':{'command':r'\studiotemplate{unreviewed-default}'}},
                    categories={'columns':'Lists'},commands={'columns':invocation})
            with fitz.open(folder/'comparisons.pdf') as document:
                text=document[0].get_text()
                self.assertIn('Lists',text)
                self.assertIn('1900.svg',text)
                self.assertIn('Use: '+invocation,text)
                self.assertNotIn('unreviewed-default',text)
                right=document[0].get_image_info(xrefs=True)[1]
                self.assertEqual(fitz.Pixmap(document,right['xref']).pixel(1,1),(249,249,249))

    @unittest.skipUnless(shutil.which('pdftocairo'), 'Poppler required for comparison raster checks')
    def test_identical_panel_artwork_has_identical_sampling_on_both_sides(self):
        import json
        from PIL import Image, ImageDraw, ImageFilter
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'build/review/batches/panel';folder.mkdir(parents=True)
            # A rounded panel with a soft shadow exposes inconsistent sampling.
            shadow=Image.new('RGB',(1600,900),(249,249,249))
            ImageDraw.Draw(shadow).rounded_rectangle((200,270,1400,670),radius=120,fill=(220,220,220))
            shadow=shadow.filter(ImageFilter.GaussianBlur(30))
            ImageDraw.Draw(shadow).rounded_rectangle((200,230,1400,630),radius=120,fill=(249,249,249))
            shadow.save(root/'panel.png')
            with fitz.open() as replica:
                page=replica.new_page(width=1600,height=900)
                page.draw_rect(page.rect,fill=(249/255,)*3,color=None)
                page.insert_image(page.rect,filename=str(root/'panel.png'))
                replica.save(folder/'main.pdf')
                pixmap=page.get_pixmap(colorspace=fitz.csRGB,alpha=False)
                pixmap.save(root/'original.png')
            (root/'templates').mkdir()
            (root/'templates/figma-inventory.json').write_text(json.dumps({'frames':[{'id':'panel','file':'panel.svg'}]}))
            index=root/'build/checks/slide-guide/comparisons.js';index.parent.mkdir(parents=True)
            index.write_text('window.BITBEAMER_COMPARISONS='+json.dumps({'records':{
                'panel':{'variants':[{'label':'panel','original':'../../original.png'}]}}})+';')
            with mock.patch('guide_comparisons.sync'):
                review_batch.comparisons(root,folder,['panel'],{'panel':{'command':r'\studiotemplate{panel}'}})
            with fitz.open(folder/'comparisons.pdf') as document:
                placements=document[0].get_image_info(xrefs=True)
                self.assertEqual(len(placements),2)
                self.assertEqual(placements[0]['width'],placements[1]['width'])
                self.assertEqual(placements[0]['height'],placements[1]['height'])
                self.assertEqual(placements[0]['digest'],placements[1]['digest'])
                for placement in placements:
                    raster=fitz.Pixmap(document,placement['xref'])
                    self.assertEqual(raster.pixel(10,10),(249,249,249))

    def test_no_pending_compositions_does_not_prepare_or_open_approved_batches(self):
        payload={'rows':[{'family':'Covers','choices':[{'id':'cover','status':'approved'}]}]}
        batches=[{'id':'first','family':'Covers','compositions':['cover']}]
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(review_batch,'catalogue',return_value=payload), \
                mock.patch.object(review_batch,'review_batches',return_value=batches), \
                mock.patch.object(review_batch,'prepare') as prepared:
            with self.assertRaisesRegex(ValueError,'No compositions pending review'):
                review_batch.combine(Path(directory),compare=True)
            prepared.assert_not_called()


if __name__=='__main__':unittest.main()
