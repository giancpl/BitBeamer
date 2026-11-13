"""Verify native slide backgrounds before publishing maintenance previews.

Inspect the PDF canvas, never the surrounding white comparison sheet. Compare
vector colours before rasterisation (MuPDF can quantise 249 to 248).
"""
import json
import re

COLOURS = {'studio-paper': '#f9f9f9', 'white': '#ffffff', 'bitpolito': '#001ce0'}


def explicit_palette(command):
    """Read a top-level option, never a palette name inside quotation text."""
    tail = command.partition('[')[2] if '[' in command else command
    chunks, current, depth, position = [], [], 0, 0
    while position < len(tail):
        char = tail[position]
        if char == '\\' and position + 1 < len(tail):
            current.extend(tail[position:position + 2]); position += 2; continue
        if char == '{': depth += 1
        elif char == '}': depth -= 1
        if depth == 0 and char in ',]':
            chunks.append(''.join(current)); current = []
            if char == ']': break
        else: current.append(char)
        position += 1
    if current: chunks.append(''.join(current))
    result = None
    for chunk in chunks:
        match = re.fullmatch(r'\s*palette\s*=\s*(?:\{\s*(light|blue)\s*\}|(light|blue))\s*', chunk)
        if match: result = match[1] or match[2]
    return result


def expected_background(root, name, command=''):
    entries = json.loads((root / 'templates/index.json').read_text())['templates']
    entry = next((item for item in entries if item['id'] == name), None)
    if entry is None:
        return None  # Lesson presets may contain photographs or full-slide artwork.
    override = explicit_palette(command)
    if override and override != entry.get('native_palette'):
        return '#f9f9f9' if override == 'light' else '#001ce0'
    return COLOURS.get(entry.get('background'),
                       '#001ce0' if entry.get('native_palette') == 'blue' else '#f9f9f9')


def rectangle_path(shape):
    items = shape['items']
    if len(items) == 1 and items[0][0] == 're':
        return True
    if len(items) != 4 or any(item[0] != 'l' for item in items):
        return False
    # A full bounding box alone also matches triangles, circles and decoration.
    points = [(item[1], item[2]) for item in items]
    return all((abs(a.x-b.x) < .01) != (abs(a.y-b.y) < .01) for a,b in points) and all(
        abs(points[i][1].x-points[(i+1)%4][0].x) < .01 and
        abs(points[i][1].y-points[(i+1)%4][0].y) < .01 for i in range(4))


def canvas_colour(page):
    """Last opaque full-page fill is the effective canvas under the artwork."""
    fills = [shape for shape in page.get_drawings()
             if shape.get('fill') is not None and shape.get('fill_opacity', 1) >= .999
             and shape['rect'].contains(page.rect + (1, 1, -1, -1)) and rectangle_path(shape)]
    if not fills:
        return None
    colour = fills[-1]['fill']
    return '#' + ''.join(f'{round(channel * 255):02x}' for channel in colour)


def check_pdf(root, pdf, pages, report=None):
    """pages contains (zero-based page, canonical composition ID, invocation)."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz  # Ubuntu's maintained python3-fitz package uses this name.
    records = []
    with fitz.open(pdf) as document:
        for number, name, command in pages:
            expected = expected_background(root, name, command)
            if expected is None:
                records.append(dict(page=number + 1, composition=name,
                                    status='not applicable: non-core artwork'))
                continue
            actual = canvas_colour(document[number])
            if actual is None:
                # A PDF without an explicit fill has the viewer's white canvas.
                actual = '#ffffff'
            records.append(dict(page=number + 1, composition=name, expected=expected,
                                actual=actual, status='passed' if actual == expected else 'failed'))
    if report:
        report.write_text(json.dumps({'pdf': str(pdf), 'backgrounds': records}, indent=2) + '\n')
    failed = [row for row in records if row['status'] == 'failed']
    if failed:
        raise ValueError('Slide background mismatch: ' + '; '.join(
            f"page {row['page']} {row['composition']}: {row['actual']}, expected {row['expected']}"
            for row in failed))
    return records
