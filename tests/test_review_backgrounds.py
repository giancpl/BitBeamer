"""Reject white/light regressions on native PDF canvases before review."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import review_backgrounds as audit
try:
    import pymupdf as fitz
except ImportError:
    fitz = None


@unittest.skipIf(fitz is None, 'Optional PDF maintenance dependency unavailable')
class BackgroundTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root/'templates').mkdir()
        (self.root/'templates/index.json').write_text(json.dumps({'templates': [
            {'id':'light', 'background':'studio-paper', 'native_palette':'light'},
            {'id':'blue', 'background':'bitpolito', 'native_palette':'blue'},
            {'id':'original-white', 'background':'white', 'native_palette':'light'}]}))

    def pdf(self, colour, panel=False):
        path = self.root/'canvas.pdf'
        with fitz.open() as doc:
            page = doc.new_page(width=355.6, height=200)
            if colour is not None:
                page.draw_rect(page.rect, fill=colour, color=None)
            if panel:
                page.draw_rect(fitz.Rect(70,50,280,150), fill=(249/255,)*3, color=(0,28/255,224/255))
            doc.save(path)
        return path

    def test_light_is_f9_and_blue_panel_does_not_replace_canvas(self):
        for name, colour, panel in [('light', (249/255,)*3, False),
                                    ('blue', (0,28/255,224/255), True)]:
            with self.subTest(name=name):
                records = audit.check_pdf(self.root, self.pdf(colour,panel), [(0,name,'')])
                self.assertEqual(records[0]['status'], 'passed')

    def test_wrong_white_and_implicit_white_are_rejected_and_reported(self):
        for colour in [(1,1,1), None]:
            with self.subTest(colour=colour):
                report = self.root/'backgrounds.json'
                with self.assertRaisesRegex(ValueError, 'expected #f9f9f9'):
                    audit.check_pdf(self.root,self.pdf(colour),[(0,'light','')],report)
                self.assertEqual(json.loads(report.read_text())['backgrounds'][0]['status'],'failed')

    def test_original_white_and_explicit_supported_palette(self):
        audit.check_pdf(self.root,self.pdf((1,1,1)),[(0,'original-white','palette=light')])
        audit.check_pdf(self.root,self.pdf((0,28/255,224/255)),[(0,'light','palette={blue}')])

    def test_cached_file_is_rechecked_without_audit_cache(self):
        path = self.pdf((249/255,)*3)
        audit.check_pdf(self.root,path,[(0,'light','')])
        path.unlink()
        self.pdf((1,1,1))
        with self.assertRaisesRegex(ValueError, 'background mismatch'):
            audit.check_pdf(self.root,path,[(0,'light','')])

    def test_later_opaque_canvas_wins_over_initial_viewer_background(self):
        path = self.root/'canvas.pdf'
        with fitz.open() as doc:
            page = doc.new_page(width=355.6,height=200)
            page.draw_rect(page.rect,fill=(1,1,1),color=None)
            page.draw_rect(page.rect,fill=(249/255,)*3,color=None)
            doc.save(path)
        audit.check_pdf(self.root,path,[(0,'light','')])

    def test_full_size_triangle_is_decoration_not_a_canvas_fill(self):
        path = self.root/'triangle.pdf'
        with fitz.open() as doc:
            page = doc.new_page(width=355.6,height=200)
            page.draw_rect(page.rect,fill=(249/255,)*3,color=None)
            page.draw_polyline([fitz.Point(0,0),fitz.Point(355.6,0),fitz.Point(355.6,200)],
                               fill=(0,28/255,224/255),color=None,closePath=True)
            doc.save(path)
        audit.check_pdf(self.root,path,[(0,'light','')])

    def test_palette_words_inside_copy_do_not_change_expected_background(self):
        command = r'\studiotemplate[quote={Explain palette=blue, with \textbf{nested words}.}]{quotation}'
        self.assertEqual(audit.expected_background(self.root,'light',command),'#f9f9f9')
        command = r'\studiotemplate[quote={Explain palette=light.},palette={blue}]{quotation}'
        self.assertEqual(audit.expected_background(self.root,'light',command),'#001ce0')
