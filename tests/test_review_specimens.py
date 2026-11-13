import json
"""Review content stress cases must follow the active, unapproved compositions."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from review_specimens import invocations, validate_specimen, append_specimens
try:
    import pymupdf as fitz
except ImportError:
    fitz = None


class ReviewSpecimenTests(unittest.TestCase):
    def test_commands_allow_nested_options_and_ignore_comments(self):
        source = r'''% \studiotemplate{ignored}
\studiotemplate[title={Nested {text} and [brackets]}]{paragraphs}
\studiotemplate[variant=plain,title={}]{statement}'''
        calls = invocations(source)
        self.assertEqual(len(calls), 2)
        self.assertIn('[brackets]', calls[0])
        self.assertIn('title={}', calls[1])

    def test_unknown_dynamic_commands_fail_instead_of_printing_a_wrong_command(self):
        with self.assertRaisesRegex(ValueError, 'literal public'):
            invocations(r'\studiotemplate[title={Text}]{\dynamic}')

    def test_specimens_cannot_read_personal_or_external_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'examples').mkdir()
            path = root / 'private.tex'
            path.write_text('private')
            batch = {'id': 'fixture', 'compositions': ['body'], 'specimen':
                     {'source': 'examples/../private.tex', 'samples': []}}
            with self.assertRaisesRegex(ValueError, 'official examples'):
                validate_specimen(root, batch)

    @unittest.skipIf(fitz is None, 'Optional PDF maintenance dependency is unavailable')
    def test_approved_samples_are_not_shown_and_pages_are_uniform(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'examples').mkdir()
            (root / 'templates').mkdir()
            (root / 'templates/index.json').write_text(json.dumps({'templates':[{'id':'body','background':'white'}]}))
            (root / 'examples/source.tex').write_text(r'\studiotemplate{approved}' + '\n' + r'\studiotemplate{body}')
            target = root / 'comparison.pdf'
            specimen = root / 'specimen.pdf'
            with fitz.open() as pdf:
                page = pdf.new_page(width=1400, height=460)
                page.insert_text((30,100), 'Current pending comparison')
                pdf.save(target)
            with fitz.open() as pdf:
                for text in ['Approved specimen must remain hidden', 'Longer body']:
                    page = pdf.new_page()
                    page.insert_text((30,100), text)
                pdf.save(specimen)
            batch = {'id': 'fixture', 'family': 'Statements', 'compositions': ['body'],
                     'specimen': {'source': 'examples/source.tex', 'samples': [
                         {'page': 1, 'composition': 'approved', 'label': 'Hidden'},
                         {'page': 2, 'composition': 'body', 'label': 'Longer copy'}]}}
            with mock.patch('review.compile_document', return_value=specimen):
                count = append_specimens(root, target, [batch], 'docker', 'fixture')
            self.assertEqual(count, 2)
            with fitz.open(target) as pdf:
                self.assertEqual([tuple(p.rect) for p in pdf], [(0,0,1400,1000)] * 2)
                text = '\n'.join(p.get_text() for p in pdf)
                self.assertIn('Longer body', text)
                self.assertIn(r'\studiotemplate{body}', text)
                self.assertNotIn('Approved specimen', text)


if __name__ == '__main__':
    unittest.main()
