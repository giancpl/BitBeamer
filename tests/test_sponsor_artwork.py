"""Sponsor groups must inherit the slide paper rather than paint a rectangle."""
from pathlib import Path
import unittest

try:
    import pymupdf as fitz
except ImportError:
    fitz = None

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(fitz is None, 'Optional PDF maintenance dependency is unavailable')
class SponsorArtworkTests(unittest.TestCase):
    def test_sponsor_groups_have_transparent_paper_and_visible_artwork(self):
        for name in ('partner-column-one', 'partner-column-two', 'media-logos'):
            with self.subTest(group=name), fitz.open(
                    ROOT / 'library/parts/bitpolito' / (name + '.pdf')) as document:
                pixmap = document[0].get_pixmap(alpha=True)
                # The empty border is part of the layout, not a logo or a white badge.
                for x, y in ((0, 0), (pixmap.width - 1, 0),
                             (0, pixmap.height - 1),
                             (pixmap.width - 1, pixmap.height - 1)):
                    self.assertEqual(pixmap.pixel(x, y)[3], 0)
                self.assertTrue(any(pixmap.samples[3::4]), 'Artwork must remain visible')
                self.assertEqual(len(document[0].get_images()), 3)


if __name__ == '__main__':
    unittest.main()
