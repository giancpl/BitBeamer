"""Recolour the cover pattern and prepare its canvas-preserving vector PDF."""

import argparse
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from asset_library import render_svg


def build(color, converter='auto'):
    if not re.fullmatch(r'#?[0-9a-fA-F]{6}', color):
        raise ValueError('Use a six-digit hex colour such as 8090FF or "#001CE0".')
    color = '#' + color.lstrip('#').upper()
    assets = Path(__file__).resolve().parents[1] / 'images/bitpolito'
    source = assets / 'source/first-page-background.svg'
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root = ET.fromstring(source.read_bytes())
    for element in root.iter():
        if element.get('fill') not in (None, 'none'):
            element.set('fill', color)
    temporary_svg = assets / 'first-page-background.tmp.svg'
    temporary_pdf = assets / 'first-page-background.tmp.pdf'
    try:
        temporary_svg.write_bytes(ET.tostring(root, encoding='utf-8') + b'\n')
        # Keep the authored 1260 x 2000 canvas; paths extend beyond its edges.
        render_svg(temporary_svg, temporary_pdf, converter, crop=False)
        temporary_pdf.replace(assets / 'first-page-background.pdf')
        temporary_svg.replace(assets / 'first-page-background.svg')
    finally:
        temporary_svg.unlink(missing_ok=True)
        temporary_pdf.unlink(missing_ok=True)
    print(f'Cover pattern colour: {color}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--color', default='001CE0', help='Six-digit hex colour; default: BitPolito electric blue')
    parser.add_argument('--converter', choices=('auto', 'rsvg', 'inkscape'), default='auto')
    args = parser.parse_args()
    try:
        build(args.color, args.converter)
    except (OSError, ValueError, RuntimeError) as error:
        print(f'Cover generation failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
