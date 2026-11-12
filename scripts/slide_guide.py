"""One offline slide reference generated from canonical models and lesson layouts."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
import tempfile
import webbrowser

from lesson_library import collection_status

ROOT = Path(__file__).resolve().parents[1]


def read(root, name):
    return json.loads((root/name).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def command(name, fields):
    from studio_guides import command as format_command
    return format_command(name, fields)


def preview(root, name, key=None, assets=None):
    record=(assets or {}).get(key,{})
    if record.get('images'):
        small=record['images']['thumb'];large=record['images']['hd']
        return {'url':'../../'+small['file']+'?v='+small['sha256'][:12],
                'hd':'../../'+large['file']+'?v='+large['sha256'][:12],
                'available':True,'sha256':small['sha256'],'hd_sha256':large['sha256']}
    checksum=digest(root/name)
    return {'url':'../../'+name+('?v='+checksum[:12] if checksum else ''),
            'available':checksum is not None,'sha256':checksum}


def prepared_assets(root):
    path=root/'docs/slides/previews/manifest.json'
    return read(root,'docs/slides/previews/manifest.json').get('previews',{}) if path.exists() else {}


def lesson_assets(data):
    result={layout['example_slide']:name for name,layout in data.get('layouts',{}).items()
            if not layout.get('registration') and not layout.get('replaced_by')}
    result.update({preset['slide']:name for name,preset in data.get('presets',{}).items()})
    return {sid:result.get(sid,sid) for sid in data['slides']}


def lesson_command(root, slide):
    """Use exactly the editable invocation that produced the retained preview."""
    from lesson_library import tex_source
    text=tex_source((root/slide['source']).read_text(encoding='utf-8'))
    start=text.index(r'\studiotemplate');position=start+len(r'\studiotemplate')
    while text[position].isspace():position+=1
    if text[position]=='[':
        braces=0
        for position in range(position+1,len(text)):
            char=text[position]
            if char=='{':braces+=1
            elif char=='}':braces-=1
            elif char==']' and braces==0:break
        else:raise ValueError('Unclosed lesson options: '+slide['source'])
        position+=1
    while text[position].isspace():position+=1
    if text[position]!='{':raise ValueError('Missing lesson template ID: '+slide['source'])
    end=text.index('}',position)
    return text[start:end+1]


def field_names(fields):
    result=[]
    for field in fields:
        item={key:field[key] for key in ('name','type')}
        if field.get('box'):item['box']=field['box']
        elif field.get('origin'):
            x,y=field['origin'];size=field.get('font_size',0)
            item['box']=[x,y-size,field['width'],field['height']+size]
        result.append(item)
    return result


def semantic_fields(entry,composition):
    reverse={native:semantic for semantic,native in composition['fields'].items()}
    result=[]
    for field in entry['fields']:
        name=reverse.get(field['name'],field['name'])
        if field['type']=='graphic' and field.get('slot'):
            words=['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve']
            number=field['slot']['number']
            if any(key.startswith('card-') for key in composition['fields']):
                names={value:'card-'+key+'/graphic' for key,value in composition.get('graphic_slots',{}).items()}
                if composition.get('title_graphic_slot'):names[composition['title_graphic_slot']]='title-graphic'
                if number not in names:continue
                name=names[number]
            elif 'graphic_slots' in composition:
                names={value:key for key,value in composition['graphic_slots'].items()}
                if number not in names:continue
                name='graphic-'+names[number]
            else:name='graphic-'+(words[number-1] if number<=len(words) else str(number))
        item=field_names([field])[0];item.update(name=name,native=field['name'])
        content=field.get('slot',{}).get('content')
        if field['type']=='graphic' and content and field.get('box'):
            x,y,_,_=field['box'];cx,cy,width,height=content
            item['box']=[x+cx-width/2,y+cy-height/2,width,height]
        result.append(item)
    return result


def catalogue(root=ROOT):
    metadata=read(root,'templates/index.json')
    entries={entry['id']:entry for entry in metadata['templates']}
    ledger=read(root,'templates/review.json')
    featured=ledger['selection'];rows=[];assets=prepared_assets(root)
    for model in read(root,'templates/models.json')['models']:
        choices=[]
        for variant in model['variants']:
            for composition in variant['compositions']:
                entry=entries[composition['id']]
                options={'variant':variant['id'],'palette':composition['native_palette']}
                preferred={native:semantic for semantic,native in composition['fields'].items()}
                for native,semantic in preferred.items():
                    field=next((f for f in entry['fields'] if f['name']==native),None)
                    if field and field['type']=='text':
                        options[semantic]=field.get('default','').replace(r'\\\\',r'\\')
                choices.append({'id':entry['id'],'label':variant['id']+' / '+composition['native_palette'],
                    'command':command(model['id'],options),'fields':semantic_fields(entry,composition),
                    'preview':preview(root,'docs/templates/previews/'+entry['id']+'.png',entry['id'],assets),
                    'variant':variant['id'],'palette':composition['native_palette'],'canvas':entry.get('canvas',[3556,2000]),
                    'source':'../../'+entry['source'],'source_sha256':digest(root/entry['source']),
                    'guide':'../templates/models/'+model['id']+'.md',
                    'status':ledger['templates'][entry['id']]['status'],
                    **({'reference_note':'Related four-item source; current layout adapts it to five items.'} if entry.get('reconstruction')=='adapted' else {})})
        default=next((i for i,c in enumerate(choices) if c['id'] in featured),
                     next((i for i,c in enumerate(choices) if c['label'].split(' / ')[0]==model['default_variant']),0))
        rows.append({'id':model['id'],'title':model['title'],'kind':'studio','family':{'cover':'Covers','team':'Team','agenda':'Contents','closing':'Closing'}.get(model['id'],model['category']),
                     'featured':any(c['id'] in featured for c in choices),'default':default,'choices':choices})
    if (root/'library/index.json').exists():
        data=read(root,'library/index.json')
        preset_layouts={data['slides'][p['slide']]['layout'] for p in data.get('presets',{}).values()}
        editable_layouts={s['layout'] for s in data['slides'].values() if not s.get('preset')}
        for name,layout in data['layouts'].items():
            if layout.get('registration') or layout.get('replaced_by') or name in entries:continue
            if name in preset_layouts and name not in editable_layouts:continue
            slide=data['slides'][layout['example_slide']]
            rows.append({'id':name,'title':layout['title'],'kind':'lesson','family':layout.get('visual_family','Needs classification'),'topics':[layout.get('topic','Lesson')],
                'featured':False,'default':0,'choices':[{'id':name,'label':layout.get('palette','native'),
                'command':lesson_command(root,slide),'fields':field_names(layout.get('fields',[])),'status':slide['status'],'canvas':layout.get('canvas',[3556,2000]),
                'preview':preview(root,'library/previews/'+layout['example_slide']+'.png',name,assets),
                'source':'../../'+layout['source'],'source_sha256':digest(root/layout['source']),
                'guide':'../../library/README.md','content_source':'../../'+slide['source'],
                'content_sha256':digest(root/slide['source']),
                'preamble':r'\usepackage{bitpolitostudiolibrary}'}]})
        for name,preset in data.get('presets',{}).items():
            slide=data['slides'][preset['slide']]
            rows.append({'id':name,'title':preset['title'],'kind':'fixed','family':preset.get('visual_family','Fixed content'),
                'featured':False,'default':0,'choices':[{'id':name,'label':'Fixed content',
                'command':command(name,{}),'fields':[],'status':preset['status'],
                'preview':preview(root,'library/previews/'+preset['slide']+'.png',name,assets),
                'source':'../../'+preset['source'],'source_sha256':digest(root/preset['source']),
                'guide':'../../library/FIXED.md','preamble':r'\usepackage{bitpolitostudiolibrary}'}]})
    if (root/'library/index.json').exists():
        data=read(root,'library/index.json')
        for row in rows:
            for choice in row['choices']:
                users={sid for sid,slide in data['slides'].items() if slide['layout']==choice['id'] or slide.get('preset')==choice['id']}
                choice['consumers']=[name for name,deck in data.get('decks',{}).items() if users.intersection(deck['slides'])]
    from studio_models import suggested_sequences
    choices={choice['id']:choice for row in rows if row['kind']=='studio' for choice in row['choices']}
    for sequence in suggested_sequences(root):
        steps=[{'id':name,'title':entries[name]['title']} for name in sequence['compositions']]
        recommendation=dict(sequence,steps=steps,command='\n\n'.join(choices[name]['command'] for name in sequence['compositions']))
        for name in sequence['compositions']:
            choices[name].setdefault('sequences',[]).append(recommendation)
    rows.sort(key=lambda row:(not row['featured'],{'studio':0,'lesson':1,'fixed':2}[row['kind']]))
    return {'schema':1,'rows':rows,'counts':{'models':len(rows),
            'compositions':sum(len(row['choices']) for row in rows)}}


def lesson_catalogue(root=ROOT):
    if not (root/'library/index.json').exists():return {'decks':{},'blocks':{},'slides':{}}
    data=read(root,'library/index.json');assets=prepared_assets(root);mapping=lesson_assets(data)
    slides={sid:{'id':sid,'title':slide.get('title',sid),'status':slide['status'],
                   'preview':preview(root,'library/previews/'+sid+'.png',mapping[sid],assets),
                   'source':'../../'+slide['source'],'origins':slide.get('origins',[])} for sid,slide in data['slides'].items()}
    return {kind:{name:dict(item,status=collection_status(item,data['slides'])) for name,item in data.get(kind,{}).items()} for kind in ('decks','blocks')} | {'slides':slides,'aliases':data.get('aliases',{})}


def redirect_page(target):
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><title>BitBeamer slide guide</title>'
            '<p>This reference has moved to <a id="destination" href="'+target+'">the unified slide guide</a>.</p>'
            '<script>const target=new URL(document.getElementById("destination").getAttribute("href"),location.href);'
            'new URLSearchParams(location.search).forEach((value,key)=>target.searchParams.set(key,value));'
            'target.hash=location.hash;location.replace(target.href);</script></html>\n')


def review_batches(root, payload=None):
    payload = payload if payload is not None else catalogue(root)
    known = {c['id'] for row in payload['rows'] for c in row['choices']}
    batches = read(root,'templates/review.json').get('review_batches', [])
    names = set()
    for batch in batches:
        ids = batch.get('compositions', [])
        if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',batch['id']) or batch['id'] in names or not batch.get('title') or not batch.get('family'):
            raise ValueError('Invalid review batch: ' + batch['id'])
        if not 1 <= len(ids) <= 5 or len(set(ids)) != len(ids) or set(ids) - known:
            raise ValueError('Review batches need one to five distinct published compositions: ' + batch['id'])
        overrides=batch.get('commands',{})
        if not isinstance(overrides,dict) or set(overrides)-set(ids) or any(not isinstance(command,str) or not command.strip() for command in overrides.values()):
            raise ValueError('Invalid review batch command overrides: '+batch['id'])
        names.add(batch['id'])
    return batches


def sync(root=ROOT,check=False):
    payload=catalogue(root)
    models=read(root,'templates/models.json')
    initial=dict(payload,rows=[r for r in payload['rows'] if r['kind']=='studio'])
    initial['aliases']={a['id']:a['alias_of'] for a in read(root,'templates/index.json').get('aliases',[])}
    initial['variant_aliases']=models.get('variant_aliases',[])
    initial['review_batches']=review_batches(root,payload)
    extra={'rows':[r for r in payload['rows'] if r['kind']!='studio']}
    def script(variable,value):return '// Generated by scripts/slide_guide.py sync; do not edit.\nwindow.'+variable+'='+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';\n'
    first=script('BITBEAMER_SLIDES',initial)
    if len(first.encode())>1024*1024:raise ValueError('Initial guide data exceeds 1 MiB.')
    outputs=[('docs/slides/index.html',(root/'scripts/slide-guide.html').read_text(encoding='utf-8')),
             ('docs/slides/catalogue.js',first),('docs/slides/catalogue-lessons.js',script('BITBEAMER_EXTRA_SLIDES',extra)),
             ('docs/slides/catalogue-library.js',script('BITBEAMER_LIBRARY',lesson_catalogue(root))),
             ('library/index.html',redirect_page('../docs/slides/index.html?view=decks'))]
    for relative,text in outputs:
        path=root/relative;raw=text.encode('utf-8')
        if path.is_file() and path.read_bytes()==raw:continue
        if check:raise ValueError('Stale unified slide guide: '+relative+'. Run python3 scripts/slide_guide.py sync.')
        path.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix=path.name+'.',suffix='.tmp',delete=False) as temporary:
            temporary.write(raw);name=Path(temporary.name)
        try:
            name.chmod(0o644);name.replace(path)
        finally:name.unlink(missing_ok=True)
    return payload['counts']


def refresh_if_present(root,check=False):
    # Partial fixtures and Overleaf subsets do not contain the clone-only guide.
    if (root/'docs/slides/guide.js').is_file():return sync(root,check)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('sync','check'),nargs='?',default='sync')
    parser.add_argument('--open',action='store_true');args=parser.parse_args(argv)
    try:
        print('Slide guide:',sync(ROOT,check=args.action=='check'))
        if args.open:webbrowser.open((ROOT/'docs/slides/index.html').as_uri())
        return 0
    except (ValueError,KeyError,OSError) as error:
        print('Slide guide failed:',error,file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
