"""Private deck scaffolding, isolation and diagnostics without a TeX dependency."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build
import deck
import doc_checks


class DeckTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='bitbeamer deck project ')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for name in ('start-studio.tex', 'start-academic.tex'):
            shutil.copyfile(ROOT / name, self.root / name)
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def create(self, name='first-talk', style='studio'):
        with contextlib.redirect_stdout(self.stdout):
            return deck.create_deck(self.root, name, style)

    def test_scaffold_preserves_starters_and_refuses_overwrite(self):
        original = (self.root / 'start-studio.tex').read_bytes()
        project = self.create()
        self.assertEqual((self.root / 'start-studio.tex').read_bytes(), original)
        self.assertTrue((project / 'assets').is_dir())
        self.assertIn('presentations/first-talk/assets/', (project / 'main.tex').read_text(encoding="utf-8"))
        self.assertIn('presentations/first-talk/references.bib', (project / 'main.tex').read_text(encoding="utf-8"))
        self.assertIn('## Sources', (project / 'brief.md').read_text(encoding="utf-8"))
        self.assertIn('bitpolito-studio', (project / 'main.tex').read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, 'Already exists'):
            self.create()
        self.assertEqual(deck.main(['new', 'first-talk'], root=self.root), 1)
        academic = self.create('second-talk', 'academic')
        self.assertIn('bitpolito-academic', (academic / 'main.tex').read_text(encoding="utf-8"))

    def test_names_are_portable_and_cannot_traverse(self):
        for name in ('../elsewhere', '/tmp/talk', 'has space', 'MixedCase', 'two--dashes', 'trailing-', 'con', 'com1', 'nul', ''):
            with self.subTest(name=name), self.assertRaises(ValueError):
                deck.project_path(self.root, name, existing=False)
        self.assertEqual(deck.validate_name('my-talk-2026'), 'my-talk-2026')

    def test_missing_project_fails_without_compiler(self):
        with mock.patch.object(build, 'main') as compile:
            with contextlib.redirect_stderr(self.stderr):
                self.assertEqual(deck.main(['build', 'missing'], root=self.root), 1)
            compile.assert_not_called()

    def test_decks_have_independent_outputs_and_cache_paths(self):
        self.create()
        self.create('second-talk')
        with mock.patch.object(build, 'main', return_value=0) as compile:
            deck.build_deck(self.root, 'first-talk')
            first = compile.call_args.args[0]
            deck.build_deck(self.root, 'second-talk', 'native', open_pdf=True, force=True)
            second = compile.call_args.args[0]
        self.assertNotEqual(first[1], second[1])
        self.assertEqual(first[1], str(self.root / 'build/presentations/first-talk'))
        self.assertIn('docker', first)
        self.assertIn('native', second)
        self.assertIn('--open', second)
        self.assertIn('--force', second)

    def test_layout_discovery_matches_authoritative_metadata(self):
        featured = deck.layout_catalogue(ROOT)
        all_models = deck.layout_catalogue(ROOT, all_models=True)
        self.assertGreater(len(all_models), len(featured))
        self.assertTrue(all(m['featured'] for m in featured))
        cover = deck.layout_catalogue(ROOT, model_id='cover')[0]
        self.assertEqual(cover['default_variant'], 'pattern')
        pattern = next(v for v in cover['variants'] if v['id'] == 'pattern')['choices'][0]
        self.assertEqual(pattern['palettes'], ['blue'])
        self.assertEqual({f['semantic_name'] for f in pattern['fields']}, {'title', 'author', 'institute'})
        self.assertIn('qrcode', deck.layout_catalogue(ROOT, model_id='closing')[0]['variants'][0]['choices'][0]['options'])
        with self.assertRaisesRegex(ValueError, 'Unknown model'):
            deck.layout_catalogue(ROOT, model_id='not-a-model')

    def test_final_log_reports_layout_glyph_reference_and_tex_errors(self):
        log = '''Overfull \\hbox (10.0pt too wide) in paragraph
Overfull \\vbox (2.0pt too high)
Missing character: There is no X in font
LaTeX Warning: Reference `fig:no' on page 1 undefined on input line 8.
LaTeX Warning: There were undefined references.
Package biblatex Warning: Please (re)run Biber on the file:
Package biblatex Warning: Citation 'missing' on page 1 undefined on input line 8.
! Package bitpolitostudiomeasured Error: Text overflow in three-cards/title.
'''
        kinds = {x['kind'] for x in deck.log_issues(log)}
        self.assertTrue({'overflow', 'layout overflow', 'missing glyph', 'unresolved citation', 'unresolved reference', 'bibliography rerun', 'TeX error'} <= kinds)
        self.assertEqual(deck.log_issues('Underfull \\hbox (badness 10000)\nOutput written on main.pdf.'), [])

    def test_checks_mark_failed_build_without_trusting_stale_pdf(self):
        self.create()
        output = deck.output_path(self.root, 'first-talk')
        output.mkdir(parents=True)
        (output / 'main.pdf').write_bytes(b'old PDF')
        with mock.patch.object(deck, 'build_deck', return_value=1), mock.patch.object(deck, 'pdf_tool') as tool, contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            self.assertEqual(deck.check_deck(self.root, 'first-talk', preview=True), 1)
            tool.assert_not_called()
        report = json.loads((output / 'check.json').read_text(encoding="utf-8"))
        self.assertEqual(report['technical_status'], 'failed')
        self.assertFalse(report['preview'])
        self.assertIn('not performed', report['visual_review'])

    def test_preview_is_numbered_and_old_pages_are_removed(self):
        project = self.create()
        output = deck.output_path(self.root, 'first-talk')
        output.mkdir(parents=True)
        (output / 'main.log').write_text('Output written on main.pdf.', encoding="utf-8")
        (output / 'main.pdf').write_bytes(b'PDF')
        (output / 'preview').mkdir()
        (output / 'preview/page-999.png').write_bytes(b'stale')
        (output / 'preview/keep.txt').write_text('keep', encoding="utf-8")
        def render(root, pdf, target, *args, **kwargs):
            self.assertEqual(kwargs['width'], 1600)
            target.write_bytes(b'PNG')
        with mock.patch.object(deck, 'build_deck', return_value=0), mock.patch.object(deck, 'pdf_tool', side_effect=['Pages: 2\n', 'name type encoding emb sub uni object ID\n---\nInter Type1 Custom yes yes yes 1 0']), mock.patch.object(deck, 'thumbnail', side_effect=render), contextlib.redirect_stdout(self.stdout):
            self.assertEqual(deck.check_deck(self.root, 'first-talk', preview=True), 0)
        report = json.loads((output / 'check.json').read_text(encoding="utf-8"))
        self.assertEqual(len(report['preview']), 2)
        self.assertFalse((output / 'preview/page-999.png').exists())
        self.assertTrue((output / 'preview/keep.txt').exists())
        self.assertTrue(any('placeholder' in w for w in report['warnings']))

    def test_local_inputs_and_private_document_links_are_scoped(self):
        project = self.create()
        (project / 'section.tex').write_text('Author name', encoding="utf-8")
        with (project / 'main.tex').open('a', encoding='utf-8') as stream:
            stream.write('\n\\input{presentations/first-talk/section}\n')
        self.assertEqual(len(list(deck.personal_sources(self.root, project))), 2)
        (project / 'brief.md').write_text('[private source](missing-file.pdf)', encoding="utf-8")
        (self.root / 'presentations/README.md').write_text('Entry guide', encoding="utf-8")
        self.assertEqual(doc_checks.check_docs(self.root), 1)

    def test_missing_pdf_tools_are_optional_unless_previews_requested(self):
        self.create()
        output = deck.output_path(self.root, 'first-talk')
        output.mkdir(parents=True)
        (output / 'main.log').write_text('Output written on main.pdf.', encoding="utf-8")
        (output / 'main.pdf').write_bytes(b'PDF')
        with mock.patch.object(deck, 'build_deck', return_value=0), mock.patch.object(deck, 'pdf_tool', side_effect=RuntimeError('Install Poppler')), contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            self.assertEqual(deck.check_deck(self.root, 'first-talk', backend='native'), 0)
            self.assertEqual(deck.check_deck(self.root, 'first-talk', backend='native', preview=True), 1)

    def test_unembedded_fonts_fail_inspection(self):
        self.create()
        output = deck.output_path(self.root, 'first-talk')
        output.mkdir(parents=True)
        (output / 'main.log').write_text('Output written on main.pdf.', encoding="utf-8")
        (output / 'main.pdf').write_bytes(b'PDF')
        with mock.patch.object(deck, 'build_deck', return_value=0), mock.patch.object(deck, 'pdf_tool', side_effect=['Pages: 1\n', 'name type encoding emb sub uni object ID\n---\nHelvetica Type 1 WinAnsi no no no 1 0']), contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            self.assertEqual(deck.check_deck(self.root, 'first-talk'), 1)


if __name__ == '__main__':
    unittest.main()
