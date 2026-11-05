"""Check HD source quality, independent cache updates and legacy routing contracts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import guide_previews
import guide_checks
import slide_guide

class GuidePreviewTests(unittest.TestCase):
    def test_real_lossless_previews_have_requested_dimensions(self):
        records=guide_previews.manifest(ROOT)['previews']
        for name in ('cover','three-cards','chat-dialogue','bitcoin-supply'):
            for kind,size in [('thumb',(640,360)),('hd',(1600,900))]:
                self.assertEqual(guide_previews.webp_size((ROOT/records[name]['images'][kind]['file']).read_bytes()),size)
        with self.assertRaisesRegex(ValueError,'WebP'):guide_previews.webp_size(b'PNG')

    def test_updates_merge_instead_of_overwriting_other_compositions(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            guide_previews.save(root,{'previews':{'first':{'signature':'one'}}})
            guide_previews.save(root,{'previews':{'second':{'signature':'two'}}})
            self.assertEqual(set(guide_previews.manifest(root)['previews']),{'first','second'})
            self.assertFalse((root/'docs/slides/previews/manifest.lock').exists())

    def test_clean_documents_have_no_catalogue_labels(self):
        text=guide_previews.clean_document([r'\studiotemplate{cover}'])
        self.assertIn(r'\studiotemplate{cover}',text)
        self.assertNotIn('studiocatalogue',text)
        self.assertNotIn('catalogue label',text)

    def test_retired_gallery_cannot_be_restored(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir();(root/'docs').mkdir();(root/'library').mkdir()
            (root/'scripts/studio_gallery.py').write_text('obsolete')
            with self.assertRaisesRegex(ValueError,'Retired gallery code'):guide_checks.check_retired_galleries(root)

    def test_public_guide_links_resolve_offline(self):
        self.assertGreater(guide_checks.check_guide_links(ROOT),1000)

    def test_legacy_redirect_preserves_query_and_hash(self):
        page=slide_guide.redirect_page('../slides/index.html?view=templates')
        self.assertIn('target.searchParams.set',page)
        self.assertIn('target.hash=location.hash',page)
        self.assertIn('location.replace',page)

if __name__=='__main__':unittest.main()
