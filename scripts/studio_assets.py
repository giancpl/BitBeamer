"""Maintain the small white illustration set used by Studio blue panels."""

import hashlib
import json
import xml.etree.ElementTree as ET
from asset_library import render_svg, write_if_changed

SOURCES = {'alice': 'assets/characters/alice.svg',
           'bob': 'assets/characters/bob.svg',
           'pig': 'assets/objects/animals/pig.svg',
           'cover-pattern': 'images/bitpolito/source/first-page-background.svg'}


def prepare_studio(root, check=False):
    folder = root / 'images/studio'
    manifest = folder / 'manifest.json'
    previous = json.loads(manifest.read_text()) if manifest.exists() else {}
    records = {}
    for name, relative in SOURCES.items():
        original = (root / relative).read_bytes().replace(b'\r\n', b'\n')
        canvas = name == 'cover-pattern'
        if canvas:
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            artwork = ET.fromstring(original)
            for element in artwork.iter():
                if element.get('fill') not in (None, 'none'):
                    element.set('fill', '#FFFFFF')
            derived = ET.tostring(artwork, encoding='utf-8') + b'\n'
        else:
            derived = original.replace(b'#001CE0', b'#FFFFFF')
        source = folder / 'source' / (name + '-white.svg')
        target = folder / (name + '-white.pdf')
        record = {'source': relative, 'sha256': hashlib.sha256(original).hexdigest()}
        if canvas:
            record['canvas'] = True
        old_source = {k: v for k, v in previous.get(name, {}).items() if k != 'pdf_sha256'}
        current = (old_source == record and source.is_file() and source.read_bytes().replace(b'\r\n', b'\n') == derived
                   and target.is_file() and previous.get(name, {}).get('pdf_sha256') == hashlib.sha256(target.read_bytes()).hexdigest())
        if not current:
            if check:
                raise RuntimeError('Studio artwork is missing or stale. Run python3 scripts/prepare-studio-assets.py.')
            source.parent.mkdir(parents=True, exist_ok=True)
            write_if_changed(source, derived)
            render_svg(source, target, crop=not canvas)
        record['pdf_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        records[name] = record
    if not check:
        write_if_changed(manifest, (json.dumps(records, indent=2) + '\n').encode())
    return len(records)
