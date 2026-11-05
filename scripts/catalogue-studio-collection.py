"""Maintain the offline command gallery for all prepared collection parts."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import json
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def catalogue(root=ROOT,check=False,previews=False):
    parts=[]
    for folder in ('collection','parts'):
        parts += [{**part, '_folder': folder} for part in json.loads((root/('images/studio/'+folder+'/manifest.json')).read_text(encoding='utf-8'))['parts']]
    output=root/'docs/studio-parts';manifest=output/'previews/manifest.json'
    rows=[dict(name=p['name'],reference=p['reference'],folder=p['_folder'],source=p['source']) for p in parts]
    payload=json.dumps(rows,separators=(',',':'),ensure_ascii=True).replace('<','\\u003c')
    script=Path(__file__).with_name('studio-parts-gallery.js').read_text(encoding='utf-8')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Studio reusable graphic parts</title><style>body{font:16px system-ui;background:#eef0ff;color:#001ce0;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}article{padding:20px;background:#fff;border-radius:16px;overflow-wrap:anywhere}img{width:100%;height:170px;object-fit:contain;background:#ddd}code{font-size:12px;display:block}a{color:inherit}input,button{font:inherit;padding:10px;margin:10px 0}.pagination{display:flex;gap:16px}button:disabled{opacity:.4}</style><h1>Studio reusable graphic parts</h1><p>Prepared artwork from measured compositions. Load bitpolitostudiotemplates, then copy a command. Only 24 parts are displayed at once.</p><p><a href="../STUDIO-PARTS.md">Parts guide</a> · <a href="../slides/index.html">Slide models</a></p><input placeholder="Search part or original reference" aria-label="Search parts" id="search"><p id="count" role="status"></p><nav class="pagination"><button data-page="-1">Previous</button><button data-page="1">Next</button></nav><main></main><noscript>Enable JavaScript to browse the offline catalogue.</noscript><script type="application/json" id="parts-data">'''+payload+'</script><script>'+script+'</script></html>\n'
    if check:
        if not (output/'index.html').is_file() or (output/'index.html').read_text(encoding='utf-8')!=page:raise RuntimeError('Stale graphic-part gallery; run catalogue-studio-collection.py')
        data=json.loads(manifest.read_text(encoding='utf-8'))
        if data['inputs']!={p['name']:p['pdf_sha256'] for p in parts}:raise RuntimeError('Stale graphic-part thumbnails')
        for name,value in data['previews'].items():
            if hashlib.sha256((output/'previews'/(name+'.png')).read_bytes()).hexdigest()!=value:raise RuntimeError('Changed part thumbnail: '+name)
        return len(parts)
    output.mkdir(parents=True,exist_ok=True);(output/'index.html').write_text(page, encoding='utf-8')
    if previews:
        (output/'previews').mkdir(exist_ok=True)
        old=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {'inputs':{}}
        def render(p):
            target=output/'previews'/(p['name']+'.png')
            if old['inputs'].get(p['name'])==p['pdf_sha256'] and target.is_file():return
            with tempfile.TemporaryDirectory() as temp:
                prefix=Path(temp)/'part'
                subprocess.run(['pdftocairo','-png','-singlefile','-scale-to','240',str(root/('images/studio/'+p['_folder'])/(p['name']+'.pdf')),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                target.write_bytes(prefix.with_suffix('.png').read_bytes())
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,parts))
        data={'inputs':{p['name']:p['pdf_sha256'] for p in parts},'previews':{p['name']:hashlib.sha256((output/'previews'/(p['name']+'.png')).read_bytes()).hexdigest() for p in parts}}
        manifest.write_text(json.dumps(data,indent=2)+'\n', encoding='utf-8')
    return len(parts)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');parser.add_argument('--previews',action='store_true');args=parser.parse_args()
    if args.check and args.previews:parser.error('--check cannot regenerate previews')
    print('Studio graphic parts:',catalogue(check=args.check,previews=args.previews))
