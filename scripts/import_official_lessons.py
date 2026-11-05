"""Build editable source-page reconstructions from reviewed extraction records."""
import sys,io,re,json,hashlib,base64,collections,argparse,xml.etree.ElementTree as ET
from pathlib import Path
import pymupdf as fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('analysis',type=Path,help='Explicit local extraction records and pinned PDF references')
parser.add_argument('--replace-drafts',action='store_true',help='Replace generated drafts; back up all manual curation first')
args=parser.parse_args()
BASE=args.analysis.resolve();EX=BASE/'extracted-v3';LIB=ROOT/'library'
NS='{http://www.w3.org/2000/svg}';HREF='{http://www.w3.org/1999/xlink}href';REV=json.load(open(BASE/'inventory.json', encoding='utf-8'))['revision']
WORDS=['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty']
SPEC={
'bitgeneration-1':('bitgeneration-economics','BitGeneration 1: Economics and culture','Intermediate learners','money'),
'bitgeneration-2':('bitgeneration-cryptography','BitGeneration 2: Cryptography','Technical beginners','cryptography'),
'bitgeneration-3':('bitgeneration-computer-science','BitGeneration 3: Computer science','Technical beginners','network'),
'bitgeneration-4':('bitgeneration-game-theory','BitGeneration 4: Game theory','Intermediate learners','incentives'),
'bitgeneration-5':('bitgeneration-mining','BitGeneration 5: Mining','Technical beginners','mining'),
'bitgeneration-6':('bitgeneration-lightning','BitGeneration 6: Lightning Network','Intermediate learners','lightning'),
'introduzione-bitcoin-breve-en':('bitcoin-introduction-short','Introduction to Bitcoin: short','Beginners','bitcoin-basics'),
'introduzione-bitcoin-breve-it':('bitcoin-introduction-short-it-source','Introduction to Bitcoin: source translation','Beginners','bitcoin-basics'),
'introduzione-bitcoin-completa':('bitcoin-introduction-full','Introduction to Bitcoin: complete','Beginners and workshop participants','bitcoin-basics'),
'bitpolito-presentazione-bitcoin-crypto':('bitcoin-and-crypto','Bitcoin and cryptocurrency distinctions','Beginners','bitcoin-basics'),
'bitpolito-presentazione-fondamenti-tecnici-compressa':('bitcoin-technical-foundations','Technical foundations of Bitcoin','Technical beginners','transactions'),
'bitpolito-workshop-acquisto':('buying-bitcoin','Buying Bitcoin workshop','Beginners','getting-started'),
'bitpolito-workshop-decentralizzazione':('decentralization','The power of decentralization','Beginners','network'),
'bitpolito-workshop-funzionamento-mining':('how-mining-works','How mining works','Technical beginners','mining'),
'bitpolito-workshop-intro-ln-compressa':('lightning-introduction','Introduction to Lightning Network','Beginners','lightning'),
'bitpolito-workshop-intro-mining-breve':('mining-introduction-short','Introduction to mining: short','Beginners','mining'),
'bitpolito-workshop-intro-mining-lunga':('mining-introduction-long','Introduction to mining: long','Technical beginners','mining'),
'bitpolito-workshop-miner':('inside-a-miner','Inside a Bitcoin miner','Technical beginners','mining'),
'bitpolito-workshop-rete':('participating-in-bitcoin','Participating in the Bitcoin network','Technical beginners','network')}
TOPICS={
'hashing':('Hashing',['hash','digest','avalanche','collision','sha-256'],['Bitcoin basics']),
'keys-and-signatures':('Keys and signatures',['private key','public key','signature','cryptography','encryption','symmetric','asymmetric'],['Hashing']),
'wallets-and-custody':('Wallets and self-custody',['wallet','seed','custody','mnemonic','backup','passphrase','multisig'],['Bitcoin basics']),
'lightning':('Lightning payments',['lightning','channel','htlc','routing','liquidity'],['Transactions']),
'mining':('Mining and proof of work',['mining','miner','proof of work','nonce','asic','difficulty','hashrate'],['Bitcoin basics']),
'network':('Networks and decentralization',['network','node','decentral','distributed','peer','p2p','server'],['Bitcoin basics']),
'money':('Money and economics',['money','monetary','inflation','fiat','gold','barter','purchasing','cantillon','debt','reserve'],[]),
'privacy':('Privacy and censorship resistance',['privacy','censorship','kyc','surveillance','anonymous','coinjoin'],['Bitcoin basics']),
'incentives':('Incentives and game theory',['game','incentive','nash','prisoner','payoff','strategy','rational'],['Bitcoin basics']),
'getting-started':('Getting started',['buy','purchase','exchange','regtest','install','download','setup'],[]),
'payments':('Bitcoin payments',['payment','pay','merchant','invoice','btcpay','remittance'],['Wallets']),
'bitcoin-basics':('Bitcoin basics',['bitcoin','satoshi','21 million','properties','freedom'],[]),
'bitcoin-history':('Bitcoin history',['history','cypherpunk','nakamoto','genesis','199','2008','2009'],[]),
'resources':('Further resources',['resources','references','github.com','bitcoin.org','books','thank you','questions'],[]),
 'transactions':('Transactions and blocks',['transaction','utxo','block','merkle','input','output','fee','double spend'],['Bitcoin basics'])}
REFS={
'lesson-bitcoin-faq':('Bitcoin FAQ','https://bitcoin.org/en/faq'),
'lesson-bitcoin-developer':('Bitcoin Developer Guides','https://developer.bitcoin.org/devguide/'),
'lesson-bitcoin-bips':('Bitcoin Improvement Proposals','https://github.com/bitcoin/bips'),
'lesson-lightning-bolts':('Basis of Lightning Technology','https://github.com/lightning/bolts'),
'lesson-btcpay-docs':('BTCPay Server Documentation','https://docs.btcpayserver.org/'),
'lesson-official-decks':('BitPolito educational presentation sources','https://github.com/BitPolito/decks/tree/'+REV)}

def digest(x):return hashlib.sha256(x).hexdigest()
def tex(text):
 replacements={'\\':r'\textbackslash{}','{':r'\{','}':r'\}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\u00a0':' ','\ufeff':'','\u200b':'','\u200e':'','\u200f':'','\u2060':'','\u00ad':'','→':r'$\to$','←':r'$\leftarrow$','↔':r'$\leftrightarrow$','⇒':r'$\Rightarrow$','≥':r'$\geq$','≤':r'$\leq$','≈':r'$\approx$','≠':r'$\neq$','∞':r'$\infty$','∑':r'$\sum$','∈':r'$\in$','∉':r'$\notin$','×':r'$\times$','✓':r'$\checkmark$','₿':r'\textsf{B}','₁':r'$_1$','₂':r'$_2$','²':r'$^2$','³':r'$^3$','Δ':r'$\Delta$','λ':r'$\lambda$','σ':r'$\sigma$','π':r'$\pi$','α':r'$\alpha$','β':r'$\beta$','θ':r'$\theta$','μ':r'$\mu$','₀':r'$_0$','₃':r'$_3$','₄':r'$_4$','₅':r'$_5$','₆':r'$_6$','₇':r'$_7$','₈':r'$_8$','₉':r'$_9$','−':'-','‐':'-','‑':'-','…':r'\ldots{}','\n':r'\\','\r':'','\t':' '}
 return ''.join(replacements.get(c,c if ord(c)>=32 else '') for c in text)

def rgba_key(data):
 with Image.open(io.BytesIO(data)) as im:
  if im.mode=='RGBA' and im.getextrema()[3]!=(255,255):return None
  rgb=im.convert('RGB');return (rgb.size,digest(rgb.tobytes()))

def canonical_svg(page,source):
 tree=ET.fromstring(source);dependencies={};jpg={}
 for item in page.get_images():
  try:
   img=page.parent.extract_image(item[0])
   if img['ext'] in ('jpg','jpeg'):
    key=rgba_key(img['image'])
    if key:jpg[key]=img['image']
  except Exception:pass
 for n in tree.iter():
  for key in (HREF,'href'):
   value=n.get(key,'')
   if not value.startswith('data:image/'):continue
   header,payload=value.split(',',1);raw=base64.b64decode(payload);ext='.jpg' if 'jpeg' in header else '.png'
   try:
    k=rgba_key(raw)
    if k in jpg:raw=jpg[k];ext='.jpg'
   except Exception:pass
   name=digest(raw)+ext;target=LIB/'parts/resources'/name
   if not target.exists():target.write_bytes(raw)
   n.set(key,'resources/'+name);dependencies['library/parts/resources/'+name]=digest(raw)
 # Canonical definition identifiers make repeated graphics independent of PDF object IDs.
 ids={n.get('id'):'part-'+str(i) for i,n in enumerate(tree.iter()) if n.get('id')}
 for n in tree.iter():
  for key,value in list(n.attrib.items()):
   if key=='id':n.set(key,ids[value]);continue
   value=re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+ids.get(m[1],m[1])+')',value)
   if key in (HREF,'href') and value.startswith('#'):value='#'+ids.get(value[1:],value[1:])
   n.set(key,value)
 return ET.tostring(tree,encoding='utf-8')+b'\n',dependencies

def point(p):return '('+f'{p.x:.4f},{p.y:.4f}'+')'
def native_geometry(page,removed):
 drawings=page.get_drawings();kept=[d for n,d in enumerate(drawings) if n not in removed]
 if page.get_image_info() or any(t[0]=='fill-shade' for t in page.get_bboxlog()) or sum(len(d['items']) for d in kept)>180 or any(d.get('dashes') not in ('[] 0','[]0',None) for d in kept):return None
 result=[]
 for i,d in enumerate(kept):
  options=[]
  for prop,color in [('fill',d.get('fill')),('draw',d.get('color'))]:
   if color is None:options.append(prop+'=none')
   else:
    options.append(prop+'={rgb,1:red,'+f'{color[0]:.6f}'+';green,'+f'{color[1]:.6f}'+';blue,'+f'{color[2]:.6f}'+'}')
  options+=['line width='+f'{(d.get("width") or 1):.5f}'+r'\studiounit']
  if d.get('fill_opacity') not in (None,1):options.append('fill opacity='+str(d['fill_opacity']))
  if d.get('stroke_opacity') not in (None,1):options.append('draw opacity='+str(d['stroke_opacity']))
  if d.get('even_odd'):options.append('even odd rule')
  chunks=[];last=None
  for item in d['items']:
   if item[0]=='re':
    r=item[1];chunks.append(f'({r.x0:.4f},{r.y0:.4f}) rectangle ({r.x1:.4f},{r.y1:.4f})');last=None
   elif item[0]=='l':
    if last!=item[1]:chunks.append(point(item[1]))
    chunks.append('--'+point(item[2]));last=item[2]
   elif item[0]=='c':
    if last!=item[1]:chunks.append(point(item[1]))
    chunks.append('.. controls '+point(item[2])+' and '+point(item[3])+' .. '+point(item[4]));last=item[4]
   elif item[0]=='qu':
    q=item[1];chunks.append(point(q.ul)+'--'+point(q.ur)+'--'+point(q.lr)+'--'+point(q.ll)+'--cycle');last=None
   else:return None
  if d.get('closePath') and chunks:chunks.append('--cycle')
  result.append(r'\path['+','.join(options)+'] '+' '.join(chunks)+';')
 return '\n'.join(result)

def role(page,values):
 joined=' '.join(values).lower()
 if page['page']==1:return 'cover'
 if sum(k in joined for k in ('members','alumni','followers','industry members'))>=2:return 'team'
 if any(v.strip().lower() in ('contents','agenda','index') for v in values) and page['page']<=4:return 'contents'
 if len(values)<14 and any(k in joined for k in ('@bitpolito','thank you','questions?','bitpolito.it')) and page['page']>4:return 'closing'
 return 'content'

def topic(values,fallback):
 text=' '.join(values).lower();scores={k:sum(text.count(word) for word in spec[1]) for k,spec in TOPICS.items()}
 best=max(scores,key=scores.get)
 return best if scores[best]>1 else fallback

def get_fields(record,translations):
 raw=record['fields']
 if raw and all('trace_index' not in f for f in raw):raise ValueError('Unreconstructed raster text: '+record['source']+':'+str(record['page']))
 result=[];counts=collections.Counter();largest=max((f['size'] for f in raw if any(c.isalpha() for c in f['text'])),default=0)
 for n,f in enumerate(raw):
  original=f['text'].strip();value=translations.get(original,original).strip()
  if original in ('nen','GtR'):continue
  if not value:continue
  x,y=f['origin'];w=record['canvas'][0];h=record['canvas'][1];size=f['size'];actual=max(1,f['bbox'][2]-f['bbox'][0])
  next_x=min([o['bbox'][0] for o in raw if o is not f and abs(o['origin'][1]-y)<size*.4 and o['bbox'][0]>f['bbox'][2]+size*.05]+[w-60])
  slot=max(actual,min(actual*1.18+size*.35,next_x-x-size*.15,w-x-40))
  is_numeric=not any(c.isalpha() for c in value) or re.fullmatch(r'[\d\s$€£.,:%+−–-]+[BKM]?',value)
  kind='value' if is_numeric else ('title' if abs(size-largest)<1 and size>=95 else ('body' if len(value)>28 else 'caption'))
  counts[kind]+=1;number=counts[kind]
  name='title' if kind=='title' and number==1 else kind+'-'+(WORDS[number-1] if number<=len(WORDS) else str(number))
  color=''.join(f'{min(255,max(0,round(c*255))):02X}' for c in f.get('color',[0,28/255,224/255])[:3])
  alignment='center' if abs((f['bbox'][0]+f['bbox'][2])/2-w/2)<50 and actual<w*.85 else 'left'
  if alignment=='center':x=(f['bbox'][0]+f['bbox'][2])/2-slot/2
  default='0' if is_numeric else ('Title' if kind=='title' else 'Text')
  if len(default)*size*.6>slot:default='A' if not is_numeric else '0'
  result.append({'name':name,'value':value,'default':default,'origin':[round(x,4),round(y,4)],'width':round(slot,4),'height':round(size*1.45,4),'font_size':round(size,4),'leading':round(size*1.15,4),'color':color,'alignment':alignment,'type':'text','source_field':n,'translation_changed':value!=original,'text_recovery':f.get('recovered_by')})
 return result

def main():
 if (LIB/'index.json').exists() and not args.replace_drafts:raise SystemExit('The curated collection exists. This bootstrap importer will not overwrite it without --replace-drafts. Normal refinement edits current sources; see library/MAINTENANCE.md.')
 for sub in ('slides','layouts','parts','parts/resources','references','previews'):(LIB/sub).mkdir(parents=True,exist_ok=True)
 data={'schema':1,'upstream':{'repository':'BitPolito/decks','revision':REV},'sources':[],'references':{},'layouts':{},'slides':{},'decks':{},'blocks':{},'aliases':{}}
 for key,(title,url) in REFS.items():
  source='library/references/'+key+'.bib';(ROOT/source).write_text('@online{'+key+',\n title={'+title+'},\n url={'+url+'},\n urldate={2026-11-04}\n}\n', encoding="utf-8");data['references'][key]={'source':source,'title':title,'url':url,'checked':'2026-11-04'}
 (LIB/'references.bib').write_text('\n'.join((ROOT/r['source']).read_text(encoding="utf-8") for r in data['references'].values()), encoding="utf-8")
 pages=json.load(open(EX/'pages.json', encoding='utf-8'));translations=json.load(open(EX/'translations-opus.json', encoding='utf-8'))
 overrides=BASE/'english-overrides.json'
 if overrides.exists():translations.update(json.load(open(overrides, encoding='utf-8')))
 original_sources=json.load(open(BASE/'inventory.json', encoding='utf-8'))['sources'];source_records={r['path']:r for r in original_sources}
 documents={};parts={};sequences={};layout_sigs={};slide_sigs={};all_values={}
 for count,page in enumerate(pages,1):
  stem=Path(page['source']).stem;deck_id,title,audience,fallback=SPEC[stem]
  if stem not in documents:documents[stem]=fitz.open(BASE/Path(page['source']).name)
  original=documents[stem][page['page']-1]
  vector_doc=fitz.open(ROOT/page['graphic_source_pdf']) if page.get('graphic_source_pdf') else None
  if vector_doc:original=vector_doc[0]
  fields=get_fields(page,translations);values=[f['value'] for f in fields];page_role=role(page,values);page_topic=topic(values,fallback)
  geometry=native_geometry(original,page['removed_paths'])
  if page.get('native_override')=='infinity':
   ink='white' if page['page']==43 else 'bitpolito'
   geometry=r'\node[text='+ink+r',font=\fontsize{600\studiounit}{600\studiounit}\selectfont] at (1778,650) {$\infty$};'
  if page.get('native_override')=='flaring':
   crop=page['photo_crop'];raw=(EX/crop['file']).read_bytes();name=digest(raw)+'.png';(LIB/'parts/resources'/name).write_bytes(raw);x,y,x1,y1=crop['box']
   geometry=r'\node[anchor=north west] at ('+str(x)+','+str(y)+r') {\includegraphics[width='+str(x1-x)+r'\studiounit]{library/resources/'+name+'}};'
  resources={};part_source=None;part_pdf=None
  if geometry is None:
   svg,deps=canonical_svg(original,(EX/page['svg']).read_bytes());part_id=digest(svg)[:24];part_source='library/parts/'+part_id+'.svg';part_pdf='library/parts/'+part_id+'.pdf'
   if not (ROOT/part_source).exists():(ROOT/part_source).write_bytes(svg)
   parts[part_id]={'source':part_source,'source_sha256':digest(svg),'pdf':part_pdf,'dependencies':deps,'origins':[{'source':deck_id,'page':page['page']}]}
   plate=part_pdf
  else:
   part_id=digest(geometry.encode())[:24];part_source='library/parts/'+part_id+'.tex'
   if not (ROOT/part_source).exists():(ROOT/part_source).write_text('% Native editable source-coordinate diagram.\n'+geometry+'\n', encoding="utf-8")
   plate=part_source
   resources[plate]=digest((ROOT/plate).read_bytes())
   if page.get('native_override')=='flaring':resources['library/parts/resources/'+name]=digest(raw)
  field_contract=[{k:f[k] for k in ('name','default','origin','width','height','font_size','leading','color','alignment','type')} for f in fields]
  descriptor={'canvas':[round(v,4) for v in page['canvas']],'fields':field_contract,'graphic':plate}
  signature=digest(json.dumps(descriptor,sort_keys=True).encode());layout_id='official-layout-'+signature[:12]
  if layout_id not in data['layouts']:
   canvas=descriptor['canvas'];bg='blue' if fields and sum(f['color']=='FFFFFF' for f in fields)>len(fields)/2 else 'light'
   layout_source='library/layouts/'+layout_id+'.tex'
   layout=['% Measured source-coordinate layout. Text defaults are neutral; lesson content is separate.',r'\studiolibrarypalette{'+bg+'}']
   for number,f in enumerate(fields,1):layout.append(r'\studiolibraryfield{'+f['name']+'}{'+str(number)+'}{'+tex(f['default'])+'}')
   if geometry is None:
    layout += [r'\studiodeclarefield{graphic-one}{\includegraphics[width='+str(canvas[0])+r'\studiounit]{'+part_pdf+'}}']
   layout += [r'\studioapplyfields',r'\studiolibrarycanvas{'+str(canvas[0])+'}{'+str(canvas[1])+'}{'+layout_id+'}{'+('bitpolito' if bg=='blue' else 'studio-paper')+'}{']
   if geometry is None:layout.append(r'\node[anchor=north west] at (0,0) {\studiofield{graphic-one}};')
   else:layout.append(r'\input{'+part_source+'}')
   for f in fields:
    fmt=r'\bfseries'+(r'\centering' if f['alignment']=='center' else '')
    layout.append(r'\studiolibrarytext{'+f['name']+'}{'+str(f['origin'][0])+'}{'+str(f['origin'][1])+'}{'+str(f['width'])+'}{'+str(f['height'])+'}{'+str(f['font_size'])+'}{'+str(f['leading'])+'}{'+f['color']+'}{'+fmt+'}')
   layout+=['}',''];(ROOT/layout_source).write_text('\n'.join(layout), encoding="utf-8")
   data['layouts'][layout_id]={'title':' / '.join(values[:2])[:100] or 'Visual composition','source':layout_source,'palette':bg,'canvas':canvas,'fields':field_contract,'graphic':plate,'status':'in review','topic':page_topic,'representation':'native TikZ' if geometry is not None else 'prepared vector parts'}
  layout_source=data['layouts'][layout_id]['source'];resources[layout_source]=digest((ROOT/layout_source).read_bytes())
  if part_pdf:resources[part_pdf]='pending preparation'
  content_signature=digest((layout_id+json.dumps(values,ensure_ascii=False)).encode());slide_id='official-slide-'+content_signature[:12]
  if slide_id not in data['slides']:
   slide_source='library/slides/'+slide_id+'.tex'
   ref=['lesson-official-decks','lesson-bitcoin-faq']
   if page_topic in ('hashing','keys-and-signatures','transactions','network','mining'):ref+=['lesson-bitcoin-developer','lesson-bitcoin-bips']
   if page_topic=='lightning':ref+=['lesson-lightning-bolts']
   if page_topic=='payments':ref+=['lesson-btcpay-docs']
   command=r'\studiotemplate['+'\n'+',\n'.join('  '+f['name']+'={'+tex(f['value'])+'}' for f in fields)+'\n]{'+layout_id+'}' if fields else r'\studiotemplate{'+layout_id+'}'
   (ROOT/slide_source).write_text('% Editable English lesson content. Layout geometry is shared.\n'+command+'\n'+r'\nocite{'+','.join(ref)+'}\n', encoding="utf-8")
   top=sorted(fields,key=lambda f:-f['font_size']);display=' '.join(f['value'] for f in top[:2])[:110] if top else 'Visual example'
   changes=['Inter replaces the original typeface.','English text replaces the original; source sequence and graphic proportions are retained. Typography and translation remain in review.']
   notes=[]
   if any(f.get('text_recovery') for f in fields):notes.append('Text recovered from a corrupt source font; verify spelling and diagram labels against the original.')
   if not fields:notes.append('Graphical document or collage: embedded image text remains artwork; replace the graphic to change it.')
   if any(re.search(r'\b(?:19|20)\d{2}\b',v) for v in values):notes.append('Dated figures and screenshots are historical examples, not current live statistics; verify their reference period before reuse.')
   if any(re.search(r'\d',v) for v in values) and page_topic in ('transactions','incentives','hashing'):notes.append('Transaction, payoff and diagram values are illustrative unless a dated source is explicitly stated.')
   data['slides'][slide_id]={'title':display,'source':slide_source,'layout':layout_id,'layout_source':layout_source,'role':page_role,'topic':page_topic,'resources':resources,'references':ref,'fields':{f['name']:f['value'] for f in fields},'origins':[],'changes':changes,'review_notes':notes,'status':'in review'}
  data['slides'][slide_id]['origins'].append({'source':deck_id,'path':page['source'],'page':page['page'],'figma':page.get('vector_reference'),'reference_status':'composition checked' if page.get('vector_reference') else 'PDF measured'})
  data['layouts'][layout_id].setdefault('example_slide',slide_id)
  sequences.setdefault(deck_id,[]).append(slide_id);all_values[slide_id]=values
  if count%60==0:print('Prepared source pages',count,'/',len(pages),flush=True)
 for src,record in source_records.items():
  stem=Path(src).stem;deck_id,title,audience,fallback=SPEC[stem];sequence=sequences[deck_id]
  source={'id':deck_id,'path':src,'sha256':record['sha256'],'revision':REV,'url':'https://raw.githubusercontent.com/BitPolito/decks/'+REV+'/'+src,'page_count':len(sequence),'pages':[{'page':n,'slide':sid,'disposition':'reconstruction'} for n,sid in enumerate(sequence,1)]}
  if stem.endswith('breve-it'):
   english=sequences['bitcoin-introduction-short']
   source['pages']=[{'page':n,'slide':sid,'disposition':'language variant of the official English short introduction'} for n,sid in enumerate(english,1)]
   data['aliases'][deck_id]='bitcoin-introduction-short'
  else:data['decks'][deck_id]={'title':title,'audience':audience,'topics':[fallback],'summary':'Editable English reconstruction of the official '+title.lower()+'. Preserve source order or copy individual topic blocks.','slides':sequence,'status':'in review','source':deck_id,'verified':'2026-11-04','content_review':'Translation and factual updates require final editorial review.'}
  data['sources'].append(source)
 # Drop the duplicate Italian translation content, retaining complete page coverage through the official English counterpart.
 used={p['slide'] for s in data['sources'] for p in s['pages']};data['slides']={k:v for k,v in data['slides'].items() if k in used};used_layouts={s['layout'] for s in data['slides'].values()};data['layouts']={k:v for k,v in data['layouts'].items() if k in used_layouts}
 for deck_id,lesson in data['decks'].items():
  pending=[];current=None
  def emit():
   if not pending:return
   group=list(pending);sig=digest('|'.join(group).encode())[:8];key=current+'-'+sig
   if key not in data['blocks']:
    title,words,prereq=TOPICS.get(current,TOPICS['bitcoin-basics'])
    data['blocks'][key]={'title':title,'audience':lesson['audience'],'topics':[current],'prerequisites':prereq,'slides':group,'status':'in review','source_decks':[]}
   data['blocks'][key]['source_decks'].append(deck_id)
   data['blocks'][key]['summary']=' / '.join(data['slides'][s]['title'] for s in group)[:240]
   data['blocks'][key]['verified']='2026-11-04'
  for sid in lesson['slides']:
   s=data['slides'][sid]
   if s['role']!='content':emit();pending=[];current=None;continue
   t=s['topic']
   if current!=t or len(pending)>=8:emit();pending=[];current=t
   pending.append(sid)
  emit()
 # Stable friendly entries for the initial author/agent examples.
 hashing=[(k,b) for k,b in data['blocks'].items() if k.startswith('hashing-')]
 if hashing:
  selected=max(hashing,key=lambda item:len(item[1]['slides']))[0];data['blocks']['hashing']=data['blocks'].pop(selected)
 basic=[(k,b) for k,b in data['blocks'].items() if k.startswith('bitcoin-basics-')]
 if basic:
  selected=max(basic,key=lambda item:len(item[1]['slides']))[0];data['blocks']['bitcoin-basics']=data['blocks'].pop(selected)
 # Remove obsolete generated source files, never user content or release artifacts.
 active_sources={s['source'] for s in data['slides'].values()}|{l['source'] for l in data['layouts'].values()}
 for folder in ('slides','layouts'):
  for obsolete in (LIB/folder).glob('official-*.tex'):
   if obsolete.relative_to(ROOT).as_posix() not in active_sources:obsolete.unlink()
 (LIB/'index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n', encoding="utf-8")
 (LIB/'parts/manifest.json').write_text(json.dumps({'schema':1,'parts':parts},indent=2)+'\n', encoding="utf-8")
 registry='\n'.join(r'\DeclareStudioLibraryLayout{'+k+'}{'+v['source']+'}' for k,v in data['layouts'].items())+'\n';(LIB/'layouts/registry.tex').write_text(registry, encoding="utf-8")
 print('Library:',len(data['sources']),'sources,',len(data['slides']),'slides,',len(data['layouts']),'layouts,',len(data['blocks']),'blocks,',len(data['decks']),'decks',flush=True)
if __name__=='__main__':main()
