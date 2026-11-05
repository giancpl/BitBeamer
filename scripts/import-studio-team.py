"""Maintenance-only extraction of measured PDF parts for the Studio team slide."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Operation ranges identify vector panel outlines in the measured reference only.
FRAME_BLOCKS = ((2787,2989),(3504,3707),(4542,4744),(5266,5468),
                (5469,5672),(5673,5875),(5876,6078),(6079,6280),
                (6281,6480),(6481,6679),(6680,6880),(6881,7080),
                (7081,7285),(7286,7490),(7491,7695),(7701,7901))


def extract(source, root=ROOT):
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import ContentStream, DictionaryObject, NameObject, RectangleObject
    except ImportError as error:
        raise RuntimeError('Maintenance only: install pypdf in a temporary virtual environment. Normal builds need no PDF library.') from error
    folder = root / 'images/studio/team'
    record = json.loads((folder / 'manifest.json').read_text(encoding="utf-8"))
    if hashlib.sha256(source.read_bytes()).hexdigest() != record['reference_sha256']:
        raise RuntimeError('Unmeasured reference PDF. Measure a new export before changing its extraction recipe.')
    prepared = {}
    for kind, box in [('collage',[0,0,988,1080]),('panels',[1048,0,1920,1080])]:
        reader = PdfReader(source)
        if len(reader.pages) != 1:
            raise RuntimeError('Expected the measured single-page team reference.')
        page = reader.pages[0]
        if list(map(float,page.mediabox)) != [0,0,1920,1080]:
            raise RuntimeError('Unexpected team reference canvas.')
        contents = page.get_contents()
        # Retain the visual artifact only, without invisible accessibility duplicates.
        contents.operations = contents.operations[:9]
        page[NameObject('/Contents')] = contents
        outer = page['/Resources']['/XObject']['/X1']
        if kind == 'panels':
            inner = outer['/Resources']['/XObject']['/X1']
            stream = ContentStream(inner,reader)
            operations = stream.operations
            if len(operations) != 7902:
                raise RuntimeError('Unexpected measured form structure.')
            stream.operations = operations[:12] + [op for start,end in FRAME_BLOCKS for op in operations[start:end+1]]
            inner.set_data(stream.get_data())
            outer_stream = ContentStream(outer,reader)
            outer_stream.operations = outer_stream.operations[:15]
            outer.set_data(outer_stream.get_data())
        # Prune unused image/font resources, preserving linked masks and colour spaces.
        visited = set()
        def prune(form):
            key = id(form)
            if key in visited:
                return
            visited.add(key)
            operations = (form.get_contents() if hasattr(form, 'get_contents') else ContentStream(form,reader)).operations
            resources = form.get('/Resources',{})
            if hasattr(resources, 'get_object'):
                resources = resources.get_object()
            for category, operator in [('/XObject',b'Do'),('/Font',b'Tf'),('/ExtGState',b'gs')]:
                if category not in resources:
                    continue
                used = {str(args[0]) for args,op in operations if op == operator}
                resources[NameObject(category)] = DictionaryObject({name:value for name,value in resources[category].items() if str(name) in used})
            for value in resources.get('/XObject',{}).values():
                child = value.get_object()
                if child.get('/Subtype') == '/Form':
                    prune(child)
        prune(page)
        page.mediabox = RectangleObject(box)
        page.cropbox = RectangleObject(box)
        writer = PdfWriter()
        writer.pdf_header = '%PDF-1.5'
        writer.add_page(page)
        writer.add_metadata({'/Title':'BitPolito team: '+kind,
                             '/Subject':'Prepared vector part extracted from the measured team reference.'})
        # Content and image streams are copied without rasterization or recompression.
        writer.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
        with (folder/(kind+'.pdf')).open('wb') as output:
            writer.write(output)
        relative = 'images/studio/team/'+kind+'.pdf'
        prepared[relative] = hashlib.sha256((root/relative).read_bytes()).hexdigest()
    record['resources'] = prepared
    (folder/'manifest.json').write_text(json.dumps(record,indent=2)+'\n', encoding="utf-8")
    path = root/'templates/index.json'
    metadata = json.loads(path.read_text(encoding="utf-8"))
    entry = next(e for e in metadata['templates'] if e['id']=='team-presentation')
    entry['prepared_resources'] = prepared
    path.write_text(json.dumps(metadata,indent=2)+'\n', encoding="utf-8")
    return prepared


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference',type=Path)
    arguments = parser.parse_args()
    for name in extract(arguments.reference):
        print('Prepared '+name)
