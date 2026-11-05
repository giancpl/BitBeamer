/* One offline interface; optional collections and local comparisons load on demand. */
(function () {
  'use strict';
  const PAGE_SIZE = 12;
  function matches(rows, query = '', kind = 'all', family = '') {
    const q = query.toLowerCase().trim();
    return rows.filter(row => (kind === 'all' || (kind === 'featured' ? row.featured : row.kind === kind)) &&
      (!family || row.family === family) && (!q || [row.id, row.title, row.family,
        ...(row.choices || []).flatMap(c => [c.id, c.label, ...(c.fields || []).flatMap(f => [f.name, f.native || ''])]),
        ...(row.topics || []), ...(row.prerequisites || [])].join(' ').toLowerCase().includes(q)));
  }
  function pageRows(rows, page) { return rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE); }
  function resolveChoice(data, requested, variant, palette) {
    requested = data.aliases?.[requested] || requested;
    const alias = (data.variant_aliases || []).find(a => a.model === requested && a.variant === variant);
    if (alias) { requested = alias.target_model; variant = alias.target_variant; }
    const row = data.rows.find(r => r.id === requested || r.choices.some(c => c.id === requested));
    if (!row) return null;
    let index = row.choices.findIndex(c => c.id === requested);
    if (variant || palette) index = row.choices.findIndex(c => (!variant || c.variant === variant) && (!palette || c.palette === palette));
    return {row, index:index < 0 ? row.default : index};
  }
  if (typeof module !== 'undefined') module.exports = {matches, pageRows, PAGE_SIZE, resolveChoice};
  if (typeof document === 'undefined') return;
  const data = window.BITBEAMER_SLIDES; if (!data) return;
  const $ = id => document.getElementById(id), choices = new Map(), pending = new Map();
  const params = new URLSearchParams(location.search);
  let page = 0, singleId = null, view = params.get('view') || params.get('kind') || 'templates', request = 0;
  const maintenance = params.get('maintenance') === '1';
  if (!['templates','decks','blocks'].includes(view)) view = 'templates';
  function element(tag, text, cls) { const node=document.createElement(tag); if (text !== undefined) node.textContent=text; if(cls)node.className=cls;return node; }
  function link(text,href) {const a=element('a',text);a.href=href;return a;}
  function load(name, variable) {
    if (window[variable]) return Promise.resolve(window[variable]);
    if (!pending.has(name)) pending.set(name,new Promise((resolve,reject) => {const script=element('script');script.src=name;script.onload=()=>resolve(window[variable]);script.onerror=()=>reject(new Error('Cannot load '+name+'. Check that the complete clone is available.'));document.head.append(script);}));
    return pending.get(name);
  }
  function button(text,callback) {const b=element('button',text);b.type='button';b.onclick=callback;return b;}
  function copyButton(text,pre) {return button('Copy command',async event=>{const target=event.currentTarget;try{await navigator.clipboard.writeText(text);target.textContent='Copied';}catch{const range=document.createRange();range.selectNodeContents(pre);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);target.textContent='Selected — copy with Ctrl/Cmd+C';}});}
  function previewImage(record,title) {const image=element('img');image.loading='lazy';image.decoding='async';image.width=640;image.height=360;image.src=record.url;image.alt=title;return image;}
  function close() {$('inspector').close();$('inspect-image').removeAttribute('src');$('inspect-comparison').replaceChildren();}
  $('inspect-close').onclick=close;
  function showHD(title,choice) {
    $('inspect-title').textContent=title;$('inspect-tools').replaceChildren();$('inspect-sequence').replaceChildren();$('inspect-fields').replaceChildren();$('inspect-comparison').replaceChildren();$('field-map').replaceChildren();$('field-map').setAttribute('hidden','');
    $('inspect-image').src=choice.preview.hd || choice.preview.url;$('inspect-image').alt=title;$('inspect-caption').textContent=choice.id+' · '+choice.status;
    if(choice.fields?.length) {
      const toggle=button('Show editable areas',()=>{$('field-map').toggleAttribute('hidden');});$('inspect-tools').append(toggle);
      const focus=element('select');focus.setAttribute('aria-label','Focus an editable field');focus.append(element('option','All fields'));
      choice.fields.forEach(field=>{const o=element('option',field.name);o.value=field.name;focus.append(o);});
      function areas() {
        const svg=$('field-map');svg.replaceChildren();svg.setAttribute('viewBox','0 0 '+(choice.canvas || [3556,2000]).join(' '));
        choice.fields.filter(f=>f.box&&(!focus.selectedIndex||f.name===focus.value)).forEach(f=>{const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');['x','y','width','height'].forEach((key,i)=>rect.setAttribute(key,f.box[i]));rect.setAttribute('fill','#ff287014');rect.setAttribute('stroke','#e51160');rect.setAttribute('stroke-width','5');const title=document.createElementNS('http://www.w3.org/2000/svg','title');title.textContent=f.name;rect.append(title);svg.append(rect);});
      }
      focus.onchange=()=>{areas();$('field-map').removeAttribute('hidden');};areas();$('inspect-tools').append(focus);
      const list=element('ul');choice.fields.forEach(f=>{const item=element('li');item.append(element('code',f.name),document.createTextNode(' · '+f.type+(f.box?' · '+f.box.slice(2).map(n=>Math.round(n)).join(' × ')+' source units':'')));list.append(item);});$('inspect-fields').append(list);
    }
    if(maintenance) $('inspect-tools').append(button('Original comparison',()=>showComparison(choice)));
    if(!$('inspector').open)$('inspector').showModal();
  }
  async function showComparison(choice) {
    const target=$('inspect-comparison');target.replaceChildren(element('p','Loading local reference…'));
    try {
      const local=await load('../../build/checks/slide-guide/comparisons.js','BITBEAMER_COMPARISONS');const record=local.records[choice.id];
      if(!record)throw new Error('No prepared local comparison for this slide. Run the documented comparison maintenance command.');
      const variants=record.variants || [record];
      const select=element('select');select.setAttribute('aria-label','Original reference');
      variants.forEach((v,i)=>{const option=element('option',v.label || 'Reference');option.value=i;select.append(option);});
      const content=element('div');
      function compare(){const reference=variants[Number(select.value)];content.replaceChildren();
        const pair=element('div',undefined,'comparison-pair');
        for(const [url,label] of [[reference.original,'Original reference'],[choice.preview.hd || choice.preview.url,'Current reconstruction']]){const image=element('img');image.src=url;image.alt=label;image.loading='lazy';pair.append(image);}content.append(pair);
        const links=element('p');if(reference.overlay)links.append(link('50% overlay',reference.overlay));if(reference.difference)links.append(document.createTextNode(' · '),link('Graphic difference',reference.difference));content.append(links,element('p',reference.note || 'Inter and English text are intentional adaptations. Metrics do not approve a design.'));
      }
      select.onchange=compare;target.replaceChildren(element('h3','Original / current reconstruction'),select,content);compare();
    } catch(error){target.replaceChildren(element('p',error.message));}
  }
  function template(row) {
    const index=choices.get(row.id) ?? row.default,choice=row.choices[index],article=element('article');article.id=row.id;
    const visual=element('div',undefined,'visual');
    if(choice.preview.available){const open=button('',()=>showHD(row.title,choice));open.className='image-button';open.setAttribute('aria-label','Open HD preview: '+row.title);open.append(previewImage(choice.preview,row.title));visual.append(open,element('small','Open the preview for HD and editable areas.'));}else visual.append(element('p','Preview preparation pending.','missing'));
    const body=element('div',undefined,'body');body.append(element('h2',row.title),element('div',row.id,'identity'));
    const badge=element('p');badge.append(element('span',row.kind==='studio'?'Studio model':row.kind==='fixed'?'Fixed content':'Lesson layout','badge'),element('small',row.family+' · '+choice.status));body.append(badge);
    if(row.choices.length>1){const label=element('label','Composition and original palette'),select=element('select',undefined,'choice');select.setAttribute('aria-label',row.title+' composition');row.choices.forEach((item,i)=>{const o=element('option',item.label);o.value=i;o.selected=i===index;select.append(o);});select.onchange=()=>{choices.set(row.id,Number(select.value));article.replaceWith(template(row));};label.append(select);body.append(label);}
    if(choice.preamble)body.append(element('p','Additional preamble: '+choice.preamble));
    const pre=element('pre',choice.command);body.append(pre);
    const actions=element('div',undefined,'actions');actions.append(copyButton(choice.command,pre),link('Source',choice.source),link('Field guide',choice.guide),link('Permalink','?template='+encodeURIComponent(choice.id)+(maintenance?'&maintenance=1':'')));if(choice.content_source)actions.append(link('Example content',choice.content_source));body.append(actions);
    const details=element('details');details.append(element('summary',row.kind==='fixed'?'Fixed slide: no editable fields':'Customize text and graphics ('+choice.fields.length+' fields)'));
    const list=element('ul');choice.fields.forEach(f=>{const li=element('li');li.append(element('code',f.name),document.createTextNode(' · '+f.type));list.append(li);});details.append(list,element('p','Replace text values with your own LaTeX. Empty values keep their space; oversized content is reported.'));
    const graphic=choice.fields.find(f=>f.type==='graphic');
    if(graphic){const example=element('pre','% Replace the '+graphic.name+' field in the command above:\n'+graphic.name+'={\\asset[width=1cm,height=1cm,keepaspectratio]{alice}}');details.append(example,element('small','Use dimensions within the slot bounds shown in the HD inspector. Graphics keep their proportions.'));}
    body.append(details);article.append(visual,body);return article;
  }
  function collectionCard(row) {
    const library=window.BITBEAMER_LIBRARY,first=library.slides[row.slides[0]],article=element('article'),visual=element('div',undefined,'visual');
    const open=button('',()=>sequence(row));open.className='image-button';open.setAttribute('aria-label','Inspect '+row.title);open.append(previewImage(first.preview,row.title));visual.append(open);
    const body=element('div',undefined,'body');body.append(element('h2',row.title),element('div',row.id,'identity'),element('p',row.summary || ''),element('p',row.slides.length+' slides · '+(row.audience || '')+' · '+row.status));
    body.append(element('p','Prerequisites: '+((row.prerequisites || []).join(', ') || 'None')));
    const command='python3 scripts/deck.py '+(view==='decks'?'new my-talk --from ':'add my-talk --block ')+row.id,pre=element('pre',command);body.append(pre);
    const actions=element('div',undefined,'actions');actions.append(copyButton(command,pre),button('Inspect slide sequence',()=>sequence(row)),link('Permalink','?view='+view+'&item='+encodeURIComponent(row.id)));body.append(actions);article.append(visual,body);return article;
  }
  function sequence(row) {
    const library=window.BITBEAMER_LIBRARY;let position=0;
    function update(){const slide=library.slides[row.slides[position]];showHD(row.title,slide);$('inspect-caption').textContent=(position+1)+' / '+row.slides.length+' · '+slide.title+' · '+slide.status;
      const nav=element('div',undefined,'pager'),previous=button('Previous slide',()=>{position--;update();}),next=button('Next slide',()=>{position++;update();});previous.disabled=position===0;next.disabled=position===row.slides.length-1;nav.append(previous,next,link('Editable source',slide.source));$('inspect-sequence').append(nav);
      const details=element('details');details.append(element('summary','Slide sequence'));const list=element('ol');row.slides.forEach((sid,i)=>{const li=element('li');li.append(button(library.slides[sid].title,()=>{position=i;update();}));list.append(li);});details.append(list);$('inspect-sequence').append(details);
    }update();
  }
  function families(){const current=$('family').value;$('family').replaceChildren(element('option','All families'));$('family').firstChild.value='';for(const name of [...new Set(data.rows.map(r=>r.family))].sort()){const o=element('option',name);o.value=name;$('family').append(o);}$('family').value=current;}
  function render() {
    let rows;
    if(view==='templates'){rows=singleId?data.rows.filter(r=>r.id===singleId):matches(data.rows,$('search').value,$('collection').value,$('family').value);if(params.get('roles')==='pages')rows=rows.filter(r=>['cover','agenda','closing'].includes(r.id));}
    else rows=matches(Object.entries(window.BITBEAMER_LIBRARY[view]).map(([id,item])=>({...item,id,kind:'all',family:'',choices:[]})),$('search').value);
    const pages=Math.max(1,Math.ceil(rows.length/PAGE_SIZE));page=Math.max(0,Math.min(page,pages-1));$('slides').replaceChildren(...pageRows(rows,page).map(view==='templates'?template:collectionCard));
    $('count').textContent=rows.length+' '+(view==='templates'?'templates':view==='decks'?'presentations':'blocks')+' · '+(page+1)+' / '+pages+'. Only this page loads thumbnails.';$('page').textContent=(page+1)+' / '+pages;
    document.querySelectorAll('[data-step]').forEach(b=>b.disabled=Number(b.dataset.step)<0?page===0:page===pages-1);
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
    $('collection-label').hidden=$('family-label').hidden=view!=='templates';
  }
  async function update() {
    const token=++request;
    try {
      if(view!=='templates')await load('catalogue-library.js','BITBEAMER_LIBRARY');
      else if(['all','lesson','fixed'].includes($('collection').value)||singleId&&!data.rows.some(r=>r.id===singleId)){
        const extra=await load('catalogue-lessons.js','BITBEAMER_EXTRA_SLIDES');if(!data.extraLoaded){data.rows.push(...extra.rows);data.extraLoaded=true;families();}
      }
      if(token===request)render();
    }catch(error){$('count').textContent=error.message;}
  }
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{view=b.dataset.view;singleId=null;page=0;$('search').value='';update();});
  $('filters').onsubmit=e=>e.preventDefault();$('search').oninput=$('collection').onchange=$('family').onchange=()=>{singleId=null;page=0;update();};
  document.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>{page+=Number(b.dataset.step);render();$('count').scrollIntoView({block:'nearest'});});
  async function start(){families();if([...$('collection').options].some(o=>o.value===params.get('collection')))$('collection').value=params.get('collection');const requested=params.get('template') || location.hash.slice(1);if(requested){if(!resolveChoice(data,requested,params.get('variant'),params.get('palette'))){$('collection').value='all';await update();}const selected=resolveChoice(data,requested,params.get('variant'),params.get('palette'));if(selected){singleId=selected.row.id;choices.set(singleId,selected.index);$('search').value=singleId;}}
    if(params.get('scope')==='all')$('collection').value='all';if(params.get('scope')==='models')$('collection').value='studio';if(params.get('roles'))$('collection').value='studio';
    await update();if(params.get('item')&&view!=='templates'){const key=window.BITBEAMER_LIBRARY.aliases?.[params.get('item')] || params.get('item');const item=window.BITBEAMER_LIBRARY[view][key];if(item)sequence({...item,id:key});}
    if(params.get('content')==='example'){$('notice').hidden=false;$('notice').textContent='Retained teaching content is available in Presentations and Reusable blocks. Core single-slide English examples remain available through the documented PDF export command.';}
  }start();
})();
