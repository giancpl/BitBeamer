"""Restore exact original JPEG streams in prepared lesson graphics (maintenance only)."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def optimize(root=ROOT):
    try:
        import pymupdf as fitz
        from PIL import Image
    except ImportError as error:
        raise RuntimeError('Optional lossless maintenance optimization needs PyMuPDF and Pillow. Ordinary builds need neither.') from error
    path=root/'library/parts/manifest.json';manifest=json.loads(path.read_text());before=after=count=0;cache={}
    for part in manifest['parts'].values():
        target=root/part['pdf'];before+=target.stat().st_size;originals={}
        for name in part['dependencies']:
            if not name.lower().endswith(('.jpg','.jpeg')):continue
            if name not in cache:
                with Image.open(root/name) as image:
                    if image.mode not in ('RGB','L'):continue
                    cache[name]=(image.width,image.height,len(image.getbands()),hashlib.sha256(image.tobytes()).hexdigest())
            originals[cache[name]]=root/name
        with fitz.open(target) as document:
            changed=0
            for xref in {image[0] for page in document for image in page.get_images(full=True)}:
                pixmap=fitz.Pixmap(document,xref)
                key=(pixmap.width,pixmap.height,pixmap.n,hashlib.sha256(pixmap.samples).hexdigest())
                if key not in originals:continue
                encoded=originals[key].read_bytes()
                if document.xref_get_key(xref,'Filter')[1]=='/DCTDecode' and document.xref_stream_raw(xref)==encoded:
                    continue
                document.update_stream(xref,encoded,compress=False)
                document.xref_set_key(xref,'Filter','/DCTDecode')
                document.xref_set_key(xref,'DecodeParms','null')
                changed+=1
            if changed:
                temporary=target.with_suffix('.optimized.pdf')
                document.save(temporary,garbage=4,deflate=True)
                count+=changed
        if changed:temporary.replace(target)
        after+=target.stat().st_size
        part['pdf_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        if changed:part['optimization']='Original JPEG bytes restored only after exact decoded-pixel equality; masks and transforms unchanged.'
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    index=root/'library/index.json';data=json.loads(index.read_text())
    for slide in data['slides'].values():
        for name in slide.get('resources',{}):slide['resources'][name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
    index.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(f'JPEG streams restored: {count}; prepared parts: {before/1048576:.1f} → {after/1048576:.1f} MiB')


if __name__=='__main__':optimize()
