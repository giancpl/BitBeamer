"""Original selection is complete, traceable, and never a graphical approval."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue_selection as selection


class CatalogueSelectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'templates').mkdir()
        (self.root / 'docs').mkdir()
        (self.root / 'design-references/figma/exports').mkdir(parents=True)
        frames = []
        for number, raw in enumerate((b'approved', b'approved', b'pending', b'gradient'), 1):
            filename = str(number) + '.svg'
            (self.root / 'design-references/figma/exports' / filename).write_bytes(raw)
            frames.append({'id': 'figma-000' + str(number), 'file': filename,
                           'sha256': hashlib.sha256(raw).hexdigest(), 'format': 'slide',
                           'assignment': {'template': 'cover'}})
        entries = [{'id': name, 'category': 'Statements', 'palettes': ['light'], 'references': refs}
                   for name, refs in [('cover', ['figma-0001']), ('body', ['figma-0003']),
                                      ('glow-statement', ['figma-0004']), ('table', [])]]
        reviews = {e['id']: {'status': 'approved' if e['id'] == 'cover' else 'in review',
                             'palette_reviews': {'light': {'status': 'approved' if e['id'] == 'cover' else 'in review'}}}
                   for e in entries}
        self.write('templates/figma-inventory.json', {'frames': frames})
        self.write('templates/index.json', {'templates': entries})
        self.write('templates/models.json', {'models': []})
        self.write('templates/review.json', {'templates': reviews})
        selection.synchronize(self.root)

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data) + '\n')

    def save(self, data):
        self.write(selection.LEDGER, data)
        selection.write_report(self.root, data)

    def test_all_originals_and_compositions_have_separate_decisions(self):
        data = selection.load(self.root)
        self.assertEqual(len(data['sources']), 4)
        self.assertEqual(len(data['compositions']), 4)
        self.assertEqual(data['sources']['figma-0001']['decision'], 'keep')
        self.assertEqual(data['sources']['figma-0002']['decision'], 'keep')
        self.assertEqual(data['sources']['figma-0003']['decision'], 'pending')
        self.assertEqual(data['compositions']['table']['decision'], 'pending')
        self.assertEqual(selection.check(self.root, sources=True)['distinct_source_groups'], 3)

    def test_similarity_is_only_a_proposal_and_never_carries_approval(self):
        record = selection.load(self.root)['sources']['figma-0003']
        self.assertIn('cover', record['suggested_compositions'])
        self.assertNotIn('cover', record['canonical_compositions'])
        self.assertEqual(record['decision'], 'pending')

    def test_decision_updates_exact_duplicates_and_preserves_graphical_ledger(self):
        previous = (self.root / 'templates/review.json').read_bytes()
        selection.decide(self.root, ['figma-0002'], 'merge', ['body'], 'Explicit user selection')
        data = selection.load(self.root)
        for name in ('figma-0001', 'figma-0002'):
            self.assertEqual(data['sources'][name]['targets'], ['body'])
        self.assertEqual((self.root / 'templates/review.json').read_bytes(), previous)
        selection.synchronize(self.root)
        self.assertEqual(selection.load(self.root)['sources']['figma-0001']['decision'], 'merge')

    def test_read_only_check_catches_source_changes_and_conflicting_duplicates(self):
        before = (self.root / selection.LEDGER).read_bytes()
        (self.root / 'design-references/figma/exports/2.svg').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Changed or unsafe original'):
            selection.check(self.root, sources=True)
        self.assertEqual((self.root / selection.LEDGER).read_bytes(), before)
        data = selection.load(self.root)
        data['sources']['figma-0002']['decision'] = 'discard'
        self.save(data)
        with self.assertRaisesRegex(ValueError, 'conflicting decisions'):
            selection.check(self.root)

    def test_completion_requires_selection_and_approved_targets_including_supplementary(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            selection.check(self.root, complete=True)
        selection.decide(self.root, ['figma-0003'], 'preset', ['body'], 'User selected preset')
        selection.decide(self.root, ['body'], 'preset', ['body'], 'User selected preset', compositions=True)
        selection.decide(self.root, ['table'], 'discard', [], 'User rejected supplementary table', compositions=True)
        with self.assertRaisesRegex(ValueError, 'explicit graphical approval'):
            selection.check(self.root, complete=True)
        reviews = selection.read(self.root, 'templates/review.json')
        reviews['templates']['body']['status'] = 'approved'
        self.write('templates/review.json', reviews)
        with self.assertRaisesRegex(ValueError, 'palette.*approval'):
            selection.check(self.root, complete=True)
        reviews['templates']['body']['palette_reviews']['light']['status'] = 'approved'
        self.write('templates/review.json', reviews)
        selection.synchronize(self.root)
        selection.check(self.root, complete=True)

    def test_candidate_batches_reject_duplicates_and_more_than_five(self):
        data = selection.load(self.root)
        data['candidate_batches'] = [{'id': 'texts-01', 'family': 'Statements',
                                     'candidates': ['figma-0001', 'figma-0002'],
                                     'proposals': {'figma-0001': 'Keep', 'figma-0002': 'Keep'}}]
        self.save(data)
        with self.assertRaisesRegex(ValueError, 'only once'):
            selection.check(self.root)
        data['candidate_batches'][0]['candidates'] = ['figma-0003'] * 6
        self.save(data)
        with self.assertRaisesRegex(ValueError, 'one to five'):
            selection.check(self.root)

    def test_invalid_decisions_do_not_write_and_sync_is_idempotent(self):
        previous = (self.root / selection.LEDGER).read_bytes()
        with self.assertRaisesRegex(ValueError, 'target'):
            selection.decide(self.root, ['figma-0003'], 'keep', [], 'Selected')
        self.assertEqual((self.root / selection.LEDGER).read_bytes(), previous)
        selection.synchronize(self.root)
        self.assertEqual((self.root / selection.LEDGER).read_bytes(), previous)

    def test_removed_composition_retains_selection_history(self):
        selection.decide(self.root, ['table'], 'discard', [], 'Explicit rejection', compositions=True)
        data = selection.read(self.root, 'templates/index.json')
        data['templates'] = [e for e in data['templates'] if e['id'] != 'table']
        self.write('templates/index.json', data)
        selection.synchronize(self.root)
        self.assertEqual(selection.load(self.root)['retired_compositions']['table']['decision'], 'discard')

    def test_real_catalogue_approval_snapshot_and_exclusion_are_preserved(self):
        data = selection.load(ROOT)
        self.assertEqual(len(data['sources']), 1073)
        reviews = selection.read(ROOT, 'templates/review.json')['templates']
        self.assertEqual(selection.summary(ROOT, data)['graphical_statuses']['approved'],
                         sum(r['status'] == 'approved' for r in reviews.values()))
        from studio_review import selected, package_selection, load_review
        self.assertNotIn('glow-statement', [e['id'] for e in selected(ROOT)])
        self.assertNotIn('glow-statement', [e['id'] for e in package_selection(ROOT)])

    def test_active_selection_routes_to_original_renderer_not_reconstruction(self):
        import review_batch
        with mock.patch('catalogue_selection.active_batch', return_value={'id': 'selection-01'}), \
             mock.patch('catalogue_selection.render_candidates', return_value=Path('selection.pdf')) as render:
            reviews = selection.read(self.root, 'templates/review.json')
            reviews['active_review_batches'] = []
            self.write('templates/review.json', reviews)
            self.assertEqual(review_batch.combine(self.root), Path('selection.pdf'))
            render.assert_called_once_with(self.root)
            reviews['active_review_batches'] = ['reconstruction-01']
            self.write('templates/review.json', reviews)
            with self.assertRaisesRegex(ValueError, 'never both'):
                review_batch.combine(self.root)


if __name__ == '__main__':
    unittest.main()
