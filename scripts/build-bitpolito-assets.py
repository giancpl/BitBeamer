"""Prepare theme logo PDFs from source SVGs and supplied transparent PNGs.

Only needed when updating brand assets. Requires PyGObject, librsvg and pycairo.
Compiling the theme uses the supplied PDFs and needs none of these tools.
"""

from pathlib import Path

import cairo
import gi

gi.require_version("Rsvg", "2.0")
gi.require_foreign("cairo")
from gi.repository import Rsvg


def render(source, output, white=False):
    data = source.read_bytes()
    if white:
        data = data.replace(b"#001CE0", b"#FFFFFF")
    handle = Rsvg.Handle.new_from_data(data)
    _, width, height = handle.get_intrinsic_size_in_pixels()
    viewport = Rsvg.Rectangle()
    viewport.x, viewport.y = 0, 0
    viewport.width, viewport.height = width, height
    _, ink, _ = handle.get_geometry_for_layer(None, viewport)
    with cairo.PDFSurface(str(output), ink.width, ink.height) as surface:
        surface.restrict_to_version(cairo.PDF_VERSION_1_5)
        context = cairo.Context(surface)
        context.translate(-ink.x, -ink.y)
        handle.render_document(context, viewport)


def render_png(source, output, crop=None):
    """Wrap the supplied transparent PNG in a PDF without resampling it."""
    image = cairo.ImageSurface.create_from_png(str(source))
    x, y, width, height = crop or (0, 0, image.get_width(), image.get_height())
    with cairo.PDFSurface(str(output), width, height) as surface:
        context = cairo.Context(surface)
        context.set_source_surface(image, -x, -y)
        context.paint()


def render_crypto_cover(primary, wordmark, output):
    """Pair the supplied symbol and wordmark, omitting the source's Italian subtitle."""
    symbol = cairo.ImageSurface.create_from_png(str(primary))
    name = cairo.ImageSurface.create_from_png(str(wordmark))
    # Same symbol crop as the header; embed the supplied pixels at native scale.
    symbol_width, height, gap = 405, 290, 35
    width = symbol_width + gap + name.get_width()
    with cairo.PDFSurface(str(output), width, height) as surface:
        context = cairo.Context(surface)
        context.save()
        context.rectangle(0, 0, symbol_width, height)
        context.clip()
        context.set_source_surface(symbol, 0, -40)
        context.paint()
        context.restore()
        context.set_source_surface(name, symbol_width + gap, (height - name.get_height()) / 2)
        context.paint()


if __name__ == "__main__":
    assets = Path(__file__).resolve().parents[1] / "images" / "bitpolito"
    for name, source in (("logo", "logo-blue.svg"), ("bull", "bull.svg"),
                         ("monogram", "monogram.svg")):
        for white in (False, True):
            suffix = "white" if white else "blue"
            render(assets / "source" / source, assets / f"{name}-{suffix}.pdf", white)
    render(assets.parents[1] / "assets/logos/polito-coat-of-arms.svg",
           assets / "polito-coat-of-arms-white.pdf", white=True)
    render_png(assets / "source/crypto-secondary-white.png",
               assets / "crypto-secondary-white.pdf")
    render_crypto_cover(assets / "source/crypto-primary-white.png",
                        assets / "source/crypto-secondary-white.png",
                        assets / "crypto-primary-white.pdf")
    # The primary logo's left-hand symbol, excluding the wordmark and subtitle.
    render_png(assets / "source/crypto-primary-white.png",
               assets / "crypto-symbol-white.pdf", crop=(0, 40, 405, 290))
    render(assets.parents[1] / "assets/symbols/bitcoin/bitcoin.svg",
           assets / "bitcoin-white.pdf", white=True)
