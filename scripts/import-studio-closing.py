"""Maintenance-only extraction of the QR and social artwork from the supplied closing PDF."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
 'qrcode':((1860,1875),(277,263,831,817)),
 'telegram':((499,752),(1088,425,1191,523)),
 'instagram':((753,1034),(1216,425,1319,523)),
 'twitter':((1035,1316),(1344,425,1447,523)),
 'youtube':((1317,1544),(1472,425,1575,523))}


def extract(reference,root=ROOT):
    try:
        from pypdf import PdfReader,PdfWriter
        from pypdf.generic import NameObject,DictionaryObject,RectangleObject
    except ImportError as error:
        raise RuntimeError('Maintenance only: install pypdf in a temporary environment. Normal builds need no PDF library.') from error
    folder = root/'images/studio/closing'
    manifest = json.loads((folder/'manifest.json').read_text())
    if hashlib.sha256(reference.read_bytes()).hexdigest()!=manifest['reference_sha256']:
        raise RuntimeError('Unmeasured closing reference. Measure a new export before changing extraction ranges.')
    hashes={}
    for name,((start,end),box) in PARTS.items():
        reader=PdfReader(reference)
        if len(reader.pages)!=1 or list(map(float,reader.pages[0].mediabox))!=[0,0,1920,1080]:
            raise RuntimeError('Unexpected closing reference canvas.')
        page=reader.pages[0];stream=page.get_contents();operations=stream.operations
        if len(operations)!=1901:raise RuntimeError('Unexpected measured closing content structure.')
        stream.operations=operations[:2]+operations[start:end+1]
        page[NameObject('/Contents')]=stream
        resources=page['/Resources']
        resources[NameObject('/Font')]=DictionaryObject()
        # Retain the original JPEG stream and alpha mask only in the QR part.
        if name!='qrcode':resources[NameObject('/XObject')]=DictionaryObject()
        page.mediabox=RectangleObject(box);page.cropbox=RectangleObject(box)
        writer=PdfWriter();writer.add_page(page)
        # Retained paths, JPEG streams, ICC colour and alpha masks use PDF 1.5 features.
        writer.pdf_header='%PDF-1.5'
        writer.add_metadata({'/Title':'BitPolito closing: '+name,'/Subject':'Lossless prepared part from the supplied closing reference.'})
        writer.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
        target=folder/(name+'.pdf')
        with target.open('wb') as output:writer.write(output)
        hashes[target.relative_to(root).as_posix()]=hashlib.sha256(target.read_bytes()).hexdigest()
    manifest['resources']=hashes
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    metadata=root/'templates/index.json';data=json.loads(metadata.read_text())
    next(e for e in data['templates'] if e['id']=='closing')['prepared_resources']=hashes
    metadata.write_text(json.dumps(data,indent=2)+'\n')
    return hashes


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reference',type=Path);args=parser.parse_args()
    for name in extract(args.reference):print('Prepared '+name)
