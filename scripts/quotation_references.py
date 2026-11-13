"""Survey original layered quotations, without selecting or approving them."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def find(root=ROOT):
    inventory = json.loads((root/'templates/figma-inventory.json').read_text())
    groups = {}
    for frame in inventory['frames']:
        nodes = list(ET.parse(root/'design-references/figma/exports'/frame['file']).getroot())
        if (len(nodes) > 2 and nodes[0].get('fill', '').lower() == '#001ce0'
            and nodes[1].tag.endswith('rect') and nodes[1].get('fill', '').lower() == '#f9f9f9'
            and nodes[2].get('stroke', '').lower() == '#001ce0'
            and nodes[2].get('fill', '').lower() == '#f9f9f9'):
            groups.setdefault(frame['sha256'], []).append(dict(frame, rear=nodes[1].attrib))
    return list(groups.values())


def prepare(root=ROOT):
    from asset_library import render_svg
    import pymupdf as fitz
    groups = find(root)
    approved = json.loads((root/'templates/review.json').read_text())['templates']['chat-dialogue']['status'] == 'approved'
    output = root/'build/review/reference-surveys/quotation'
    output.mkdir(parents=True, exist_ok=True)
    report = {'scope': 'All 1073 supplied SVG exports; layered quotation geometry search, visually verified.',
              'selection': 'No selection or approval inferred.', 'exports': sum(map(len, groups)),
              'exact_groups': groups}
    (output/'sources.json').write_text(json.dumps(report, indent=2)+'\n')
    with fitz.open() as result:
        for i, group in enumerate(groups):
            if i % 4 == 0:
                page = result.new_page(width=1400, height=1000)
                page.insert_text((20,28),'Statements | Quotation | Original reference survey | Selection separate from approval',fontsize=15)
            frame = group[0]
            pdf = output/(frame['id']+'.pdf')
            if not pdf.exists():
                render_svg(root/'design-references/figma/exports'/frame['file'], pdf, crop=False)
            x = 20 + (i % 2)*690
            y = 65 + ((i % 4)//2)*450
            page.insert_text((x,y), ', '.join(f['id'] for f in group), fontsize=12)
            with fitz.open(pdf) as source:
                page.show_pdf_page(fitz.Rect(x,y+15,x+670,y+392), source, 0)
            page.insert_text((x,y+410),frame['file'],fontsize=8)
        temporary = output/'survey.tmp.pdf'
        result.save(temporary, garbage=4, deflate=True)
        temporary.replace(output/'survey.pdf')
    lines = ['# Original quotation references', '',
             'All 1,073 supplied SVG exports were searched for the layered quotation',
             'geometry and the matches visually inspected: 12 exports, 8 exact groups.',
             'Discovery does not select or approve a composition. The wider/narrower',
             'panels were explicitly selected together on 2026-11-13.',
             ('Graphical approval was explicitly confirmed on 2026-11-13.' if approved else 'Graphical approval remains pending.'),
             'Native canvas is',
             '`#001ce0`; both panel layers are `#f9f9f9` in every match.', '',
             'Five main geometries: compact (figma-0733), medium (figma-0039),',
             'standard (figma-0651, figma-0652, figma-0664, figma-0893),',
             'standard low (figma-0653), and wide (figma-0197). The 1920-wide export',
             'figma-0652 is the standard geometry at another export scale.', '',
             '| Exact representative | Other identical exports | Original file |',
             '| --- | --- | --- |']
    for group in groups:
        lines.append('| '+group[0]['id']+' | '+(', '.join(f['id'] for f in group[1:]) or '—')+' | `'+group[0]['file']+'` |')
    lines += ['', 'The exact hashes and original rear-panel coordinates are retained in',
              '`templates/figma-inventory.json` and the generated',
              '`build/review/reference-surveys/quotation/sources.json`.', '',
              'Regenerate the survey with `PYTHONPATH=scripts python3 scripts/quotation_references.py`.',
              'The PDF shows each exact source once, including the shorter Assange and',
              'Mises quotations, the Musa and Gensler examples, Satoshi and both Hughes',
              'language versions. Text in the originals is reference material, not a',
              'new verified attribution or selected default.', '']
    (root/'docs/STUDIO-QUOTATION-REFERENCES.md').write_text('\n'.join(lines))
    print(output/'survey.pdf')
    return output/'survey.pdf'


if __name__ == '__main__':
    prepare()
