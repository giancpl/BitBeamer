"""Index named artwork and prepare pdfLaTeX-compatible files.

PDF/PNG/JPEG need only Python's standard library. SVG rendering additionally
uses librsvg with PyGObject/pycairo, or the Inkscape CLI. Compilation needs no converter.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

FORMATS = {'.svg', '.pdf', '.png', '.jpg', '.jpeg'}
NAME = re.compile(r'[a-z][a-z0-9_-]*\Z')


def write_if_changed(path, data):
    if path.exists() and path.read_bytes() == data:
        return
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)


def rsvg_modules():
    try:
        import cairo
        import gi
        gi.require_version('Rsvg', '2.0')
        gi.require_foreign('cairo')
        from gi.repository import Rsvg
    except (ImportError, ValueError) as error:
        raise RuntimeError('librsvg requires PyGObject and pycairo') from error
    return cairo, Rsvg


def inkscape_executable():
    candidates = [os.environ.get('INKSCAPE'), shutil.which('inkscape'),
                  '/Applications/Inkscape.app/Contents/MacOS/inkscape']
    for variable in ('ProgramFiles', 'ProgramFiles(x86)'):
        if os.environ.get(variable):
            candidates.append(str(Path(os.environ[variable]) / 'Inkscape/bin/inkscape.exe'))
    return next((str(path) for path in candidates if path and Path(path).is_file()), None)


def converter_available():
    try:
        rsvg_modules()
        return True
    except RuntimeError:
        return inkscape_executable() is not None


def render_svg(source, target, converter='auto', *, crop=True):
    modules = None
    if converter != 'inkscape':
        try:
            modules = rsvg_modules()
        except RuntimeError:
            if converter == 'rsvg':
                raise
    if modules is None:
        executable = inkscape_executable()
        if not executable:
            raise RuntimeError(
                'SVG conversion needs Inkscape, or PyGObject + pycairo + librsvg. '
                'Install Inkscape or set INKSCAPE to its executable; see docs/ASSETS.md.'
            )
        temporary = target.with_name(target.stem + '.tmp.pdf')
        try:
            subprocess.run([
                executable, str(source.resolve()), '--export-type=pdf',
                '--export-area-drawing' if crop else '--export-area-page', '--export-text-to-path',
                '--export-filename=' + str(temporary.resolve()),
            ], check=True, capture_output=True, text=True)
            if not temporary.is_file() or not temporary.read_bytes().startswith(b'%PDF-'):
                raise RuntimeError(f'Inkscape did not produce a PDF for {source}')
            temporary.replace(target)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f'Inkscape failed for {source}: {error.stderr}') from error
        finally:
            temporary.unlink(missing_ok=True)
        return
    cairo, Rsvg = modules

    handle = Rsvg.Handle.new_from_file(str(source))
    sized, width, height = handle.get_intrinsic_size_in_pixels()
    if not sized:
        *_, has_viewbox, viewbox = handle.get_intrinsic_dimensions()
        if not has_viewbox:
            raise ValueError(f'{source}: SVG needs dimensions or a viewBox')
        width, height = viewbox.width, viewbox.height
    if width <= 0 or height <= 0:
        raise ValueError(f'{source}: SVG dimensions must be positive')
    viewport = Rsvg.Rectangle()
    viewport.x, viewport.y = 0, 0
    viewport.width, viewport.height = width, height
    _, ink, _ = handle.get_geometry_for_layer(None, viewport)
    if ink.width <= 0 or ink.height <= 0:
        raise ValueError(f'{source}: SVG contains no visible artwork')
    temporary = target.with_name(target.name + '.tmp')
    try:
        with cairo.PDFSurface(str(temporary), ink.width if crop else width, ink.height if crop else height) as surface:
            surface.restrict_to_version(cairo.PDF_VERSION_1_5)
            context = cairo.Context(surface)
            if crop:
                context.translate(-ink.x, -ink.y)
            else:
                context.rectangle(0, 0, width, height)
                context.clip()
            handle.render_document(context, viewport)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def inspect_library(root):
    assets = root / 'assets'
    output = assets / 'generated'
    sources = {}
    # Validate the whole input set before changing the catalogue.
    for source in sorted(assets.rglob('*')):
        if output in source.parents or not source.is_file():
            continue
        if source.suffix.lower() not in FORMATS:
            continue
        name = source.stem
        if not NAME.fullmatch(name):
            raise ValueError(
                f'{source}: use a lowercase filename starting with a letter, '
                'followed by letters, digits, hyphens, or underscores'
            )
        if name in sources:
            raise ValueError(
                f'Duplicate asset name "{name}": {sources[name]} and {source}. '
                'Give each asset a unique filename.'
            )
        sources[name] = source

    manifest_path = output / 'manifest.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    records = {}
    catalogue = ['% Generated by scripts/prepare-assets.py; edit the source artwork instead.']
    for name, source in sources.items():
        extension = source.suffix.lower()
        destination = name + ('.pdf' if extension == '.svg' else extension)
        target = output / destination
        data = source.read_bytes()
        # Git stores SVG text with LF; Windows editors may save CRLF before commit.
        fingerprint = data.replace(b'\r\n', b'\n') if extension == '.svg' else data
        record = {
            'source': source.relative_to(root).as_posix(),
            'output': destination,
            'sha256': hashlib.sha256(fingerprint).hexdigest(),
            'conversion': 'svg-ink-v1' if extension == '.svg' else 'copy-v1',
        }
        records[name] = record
        catalogue.append(r'\DeclareBitPolitoAsset{' + name + '}{' + destination + '}')
    catalogue_data = ('\n'.join(catalogue) + '\n').encode('utf-8')
    return sources, records, previous, catalogue_data


def check_prepared(root):
    """Read-only check; compilation must not convert or rewrite artwork."""
    _, records, previous, catalogue = inspect_library(root)
    output = root / 'assets/generated'
    issues = [name for name, record in records.items()
              if previous.get(name) != record or not (output / record['output']).is_file()]
    issues += sorted(set(previous) - set(records))
    index = output / 'catalogue.tex'
    if not index.is_file() or index.read_bytes() != catalogue:
        issues.append('command catalogue')
    if issues:
        raise RuntimeError(
            'Prepared artwork is stale or missing: ' + ', '.join(issues[:8]) + '. '
            'Run python scripts/prepare-assets.py (or py -3 on Windows). '
            'For SVG changes, install Inkscape or the librsvg Python libraries; see docs/ASSETS.md.'
        )
    return len(records)


def prepare(root, converter='auto', force=False):
    sources, records, previous, catalogue = inspect_library(root)
    output = root / 'assets/generated'
    output.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        record = records[name]
        target = output / record['output']
        if force or previous.get(name) != record or not target.exists():
            extension = source.suffix.lower()
            if extension == '.svg':
                render_svg(source, target, converter)
            else:
                write_if_changed(target, source.read_bytes())

    write_if_changed(output / 'catalogue.tex', catalogue)
    write_if_changed(output / 'manifest.json', (json.dumps(records, indent=2) + '\n').encode('utf-8'))
    # Remove only outputs previously tracked by this script, never source files.
    active = {record['output'] for record in records.values()}
    for record in previous.values():
        filename = record['output']
        if filename not in active and Path(filename).name == filename:
            (output / filename).unlink(missing_ok=True)
    return len(records)
