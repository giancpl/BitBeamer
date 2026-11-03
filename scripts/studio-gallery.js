/* Offline galleries: only the current page creates cards and image requests. */
function selectRows(rows, selection, scope, query, category, status) {
  const selected = new Set(selection);
  const term = query.trim().toLowerCase();
  const result = rows.filter(row => (scope === 'all' || selected.has(row.id)) &&
    (!category || row.category === category) && (!status || row.status === status) &&
    [row.id, row.title, ...row.references, ...(row.aliases || [])].join(' ').toLowerCase().includes(term));
  return scope === 'all' ? result : result.sort((a, b) => selection.indexOf(a.id) - selection.indexOf(b.id));
}
function pageRows(rows, page, size) {
  const pages = Math.max(1, Math.ceil(rows.length / size));
  const current = Math.min(Math.max(0, page), pages - 1);
  return {rows: rows.slice(current * size, (current + 1) * size), page: current, pages};
}
function groupRows(rows, models, selection, scope, choices = {}) {
  if (scope === 'all' || !models?.length) return rows;
  const byId = new Map(rows.map(row => [row.id, row]));
  const selected = new Map((selection || []).map(item => [item.model, item]));
  const ordered = scope === 'selected' ? (selection || []).map(item => models.find(m => m.id === item.model)).filter(Boolean) : models;
  return ordered.map(model => {
    const chosen = choices[model.id] || selected.get(model.id) || {};
    const variant = model.variants.find(v => v.id === chosen.variant) || model.variants.find(v => v.id === model.default_variant);
    const composition = variant.compositions.find(c => c.native_palette === chosen.palette) || variant.compositions.find(c => c.id === chosen.composition) || variant.compositions.find(c => c.id === variant.default_source);
    const row = byId.get(composition.id);
    if (!row) return null;
    const palette = composition.palettes.includes(chosen.palette) ? chosen.palette : composition.native_palette;
    return {...row, model, modelVariant:variant.id, modelPalette:palette, modelComposition:composition,
      title:model.title, status:row.status==='supplementary' ? row.status : (row.paletteReviews?.[palette]?.status || row.status), references:[...new Set(model.variants.flatMap(v => v.compositions.flatMap(c => byId.get(c.id)?.references || [])))]};
  }).filter(Boolean);
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {selectRows, pageRows, groupRows};
} else {
  const config = JSON.parse(document.querySelector('#gallery-data').textContent);
  const rows = config.entries, byId = new Map(rows.map(row => [row.id, row]));
  const main = document.querySelector('main'), search = document.querySelector('#search');
  const scope = document.querySelector('#scope'), category = document.querySelector('#category');
  const status = document.querySelector('#status');
  let page = 0;
  const modelChoices = {};
  const displayById = new Map();
  function visibleRows() {return groupRows(rows, config.models, config.modelSelection, scope.value, modelChoices);}
  const requested = new URLSearchParams(location.search).get('template');
  const singleId = config.aliases?.[requested] || requested;
  const single = requested !== null;
  const queryOptions=new URLSearchParams(location.search);
  const requestedModel=config.models?.find(m=>m.id===requested || m.variants.some(v=>v.compositions.some(c=>c.id===singleId)));
  if(requestedModel){const v=requestedModel.variants.find(v=>v.id===queryOptions.get('variant')) || requestedModel.variants.find(v=>v.compositions.some(c=>c.id===singleId)) || requestedModel.variants.find(v=>v.id===requestedModel.default_variant); const c=v.compositions.find(c=>c.id===singleId) || v.compositions.find(c=>c.id===v.default_source);modelChoices[requestedModel.id]={variant:v.id,composition:c.id,palette:queryOptions.get('palette') || c.native_palette};}
  const escape = value => String(value ?? '').replace(/[&<>"']/g, ch =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const image = (preview, full, label) => '<a href="' + escape(full) + '" target="_blank" rel="noopener">' +
    '<img loading="lazy" decoding="async" width="480" height="270" src="' + escape(preview) +
    '" alt="' + escape(label) + '"></a><small>' + escape(label) + (config.mode === 'comparisons' ? ' · Open 2000px render' : ' · Open preview') + '</small>';
  function mappedImage(row) {
    const markup = image(row.preview, row.full, 'Editable replica');
    const split = markup.indexOf('</a>') + 4;
    if (row.canvas.length !== 2) return markup;
    const [width, height] = row.canvas;
    const mapped = row.fields.filter(field => field.box);
    const boxes = mapped.map(field => {
      const [x, y, w, h] = field.box;
      const labelX = Math.max(0, Math.min(width - 100, x));
      const labelY = Math.max(height * .025, Math.min(height - 10, y + height * .025));
      const color = field.type === 'graphic' ? '#bc3700' : '#001ce0';
      return '<g data-box="' + escape(field.name) + '"><rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h +
        '" fill="' + color + '" fill-opacity=".06" stroke="' + color + '" stroke-width="' + (height * .002) +
        '"></rect><text x="' + labelX + '" y="' + labelY + '" fill="' + color + '" font-size="' + (height * .023) +
        '" paint-order="stroke" stroke="white" stroke-width="' + (height * .003) + '">' + escape(field.slot?.key || field.name) + '</text></g>';
    }).join('');
    return '<div class="slide-image">' + markup.slice(0, split) + '<svg class="field-map" aria-hidden="true" viewBox="0 0 ' + width + ' ' + height + '">' + boxes + '</svg></div>' + markup.slice(split);
  }
  function singleHelp(row) {
    return '<h3>Use this slide</h3><p>Copy the complete example into <code>my-slide.tex</code> in the project root. ' +
      'Compile with <code>python3 scripts/build.py my-slide.tex</code>, or add <code>--backend native</code>. ' +
      'On Windows use <code>py -3</code>. On Overleaf, select the new file as the main document and use pdfLaTeX.</p>' +
      '<details open><summary>Complete one-slide document</summary><pre>' + escape(row.document) + '</pre>' +
      '<button data-copy="' + escape(row.id) + '" data-copy-kind="document">Copy document</button></details>' +
      (row.replacement ? '<h3>Replace a graphic</h3><pre>' + escape(row.replacement) + '</pre><p>This example fits an icon in the first graphic slot. ' +
      'Some slots contain a complete panel or decoration; check the field map before replacing them.</p>' : '') +
      '<h3>Keep the layout</h3><p>Use only the listed fields. Omitted fields retain defaults; an empty value keeps its space. ' +
      'Shorten overflowing text or edit the current source deliberately. Fonts and anchors do not shrink automatically. ' +
      'Original graphic colours remain fixed.</p><p>Status: ' + escape(row.status) + '. Compilation does not approve graphical fidelity.</p>';
  }
  function mapControls(row) {
    const fields = row.fields.filter(field => field.box);
    if (!fields.length) return '<p>This model uses source-defined Beamer areas; inspect its source for placement.</p>';
    return '<div class="map-controls"><button data-areas>Show editable areas</button><select data-field-focus aria-label="Locate an editable field">' +
      '<option value="">All editable fields</option>' + fields.map(field => '<option value="' + escape(field.name) + '">' +
        escape((field.slot?.key || field.name) + ' — ' + field.role) + '</option>').join('') + '</select></div>';
  }
  function card(row) {
    if (row.model) {
      const options = {variant:row.modelVariant, palette:row.modelPalette};
      for (const key of ['title','author','institute']) {
        const native = row.modelComposition.fields[key];
        const field = row.fields.find(f => f.name === native);
        if (field) options[key] = field.default;
      }
      const command = '\\studiotemplate[\n  ' + Object.entries(options).map(([key,value]) => key+'={'+value+'}').join(',\n  ')+'\n]{'+row.model.id+'}';
      row = {...row, guide:(config.mode==='comparisons' ? '../../../docs/templates/models/' : 'models/')+row.model.id+'.md', example:command, document:row.document.replace(row.example,command), single:'index.html?template='+encodeURIComponent(row.model.id)+'&variant='+encodeURIComponent(row.modelVariant)+'&palette='+row.modelPalette};

    }
    displayById.set(row.id,row);
    const variantControls = row.model ? '<div class="map-controls"><label>Variant <select data-model-variant="'+escape(row.model.id)+'">'+row.model.variants.map(v => '<option value="'+escape(v.id)+'"'+(v.id===row.modelVariant?' selected':'')+'>'+escape(v.id)+'</option>').join('')+'</select></label>'+([...new Set(row.model.variants.find(v=>v.id===row.modelVariant).compositions.map(c=>c.native_palette))].length>1 ? '<label>Palette <select data-model-palette="'+escape(row.model.id)+'" data-composition="'+escape(row.id)+'">'+[...new Set(row.model.variants.find(v=>v.id===row.modelVariant).compositions.map(c=>c.native_palette))].map(p => '<option'+(p===row.modelPalette?' selected':'')+'>'+p+'</option>').join('')+'</select></label>' : '')+'</div>' : '';

    const graphics = config.mode === 'comparisons' ? '<div class="pair">' +
      (row.original ? '<div>' + image(row.original.preview, row.original.full, 'Original') + '</div>' :
        '<p>Supplementary: no Figma original.</p>') + '<div>' + (single ? mappedImage(row) : image(row.preview, row.full, 'Editable replica')) + '</div></div>' :
      (single ? mappedImage(row) : image(row.preview, row.full, row.title));
    return '<article id="' + escape(row.id) + '">' + (single ? mapControls(row) : '') + graphics + '<div class="body"><small>' +
      escape(row.category + ' · ' + row.status + ' · Archive page ' + row.page) + '</small><h2>' +
      escape(row.title) + '</h2>' + variantControls + '<p class="purpose">' + escape(row.purpose || '') + '</p><p><code>' +
      escape(row.model ? '\\studiotemplate[variant='+row.modelVariant+',palette='+row.modelPalette+']{'+row.model.id+'}' : '\\studiotemplate{'+row.id+'}') + '</code></p><pre>' + escape(row.example) +
      '</pre><p><button data-copy="' + escape(row.id) + '">Copy example</button> <a href="' + escape(row.source) +
      '">Editable source</a> · <a href="' + escape(row.single + '&scope=' + scope.value) + '">Open slide</a> · <a href="' + escape(row.guide) + '">Usage guide</a> · <a href="#' + escape(row.id) + '">Permalink</a></p><small>' +
      escape(row.references.join(', ') || 'Supplementary') + '</small><details data-fields="' + escape(row.id) +
      '"><summary>Fields (' + row.fields.length + '), dimensions and parts</summary><div></div></details>' +
      (row.overlay ? '<details data-comparison="' + escape(row.id) +
      '"><summary>Load overlay and graphic difference</summary><div></div></details>' : '') + (single ? singleHelp(row) : '') + '</div></article>';
  }
  function render() {
    if (single) {
      document.body.classList.add('single');
      const row = requestedModel ? groupRows(rows,config.models,config.modelSelection,'models',modelChoices).find(r=>r.model.id===requestedModel.id) : byId.get(singleId);
      const context = new URLSearchParams(location.search).get('scope') || (requestedModel ? (config.modelSelection.some(s=>s.model===requestedModel.id) ? 'selected' : 'models') : (config.selection.includes(singleId) ? 'selected' : 'all'));
      const sequence = requestedModel ? (context==='selected' ? config.modelSelection.map(s=>s.model) : config.models.map(m=>m.id)) : (context==='selected' ? config.selection : rows.map(item=>item.id));
      const position = sequence.indexOf(requestedModel ? requestedModel.id : singleId);
      const neighbour = (offset, label) => {
        const id = sequence[position + offset];
        return id ? ' · <a href="index.html?template=' + escape(id) + '&scope=' + context + '">' + label + '</a>' : '';
      };
      main.innerHTML = '<nav><a href="index.html' + (row ? '#' + escape(row.id) : '') + '">Back to gallery</a>' + (row ? neighbour(-1, 'Previous slide') + neighbour(1, 'Next slide') : '') + '</nav>' +
        (row ? '<h1>' + escape(row.title) + '</h1><p><code>' + escape(row.model ? row.model.id+' / '+row.modelVariant+' / '+row.modelPalette : row.id) + '</code></p>' + card(row) : '<h1>Unknown layout</h1><p>Choose a current composition from the gallery.</p>');
      return;
    }
    const matches = selectRows(visibleRows(), [], 'all', search.value, category.value, status.value);
    const result = pageRows(matches, page, config.pageSize); page = result.page;
    main.innerHTML = result.rows.map(card).join('') || '<p>No matching layouts. Try the full archive or clear the filters.</p>';
    document.querySelector('#count').textContent = matches.length + ' layouts · Page ' + (page + 1) + ' of ' + result.pages;
    document.querySelectorAll('[data-page]').forEach(button => {
      button.disabled = Number(button.dataset.page) < 0 ? page === 0 : page === result.pages - 1;
    });
  }
  function followHash() {
    const requested = location.hash.slice(1), id = config.aliases?.[requested] || requested, row = byId.get(id);
    if (!row) return false;
    if (!config.selection.includes(id)) scope.value = 'all';
    search.value = ''; category.value = ''; status.value = '';
    const matches = selectRows(visibleRows(), [], 'all', '', '', '');
    page = Math.floor(matches.findIndex(item => item.id === id) / config.pageSize);
    render(); document.getElementById(id)?.scrollIntoView(); return true;
  }
  for (const control of [search, scope, category, status]) control.addEventListener('input', () => {page = 0; render();});
  document.querySelectorAll('[data-page]').forEach(button => button.addEventListener('click', () => {
    page += Number(button.dataset.page); render(); document.querySelector('#controls').scrollIntoView();
  }));
  main.addEventListener('toggle', event => {
    const details = event.target;
    if (details.tagName !== 'DETAILS' || (!details.dataset.fields && !details.dataset.comparison)) return;
    const body = details.querySelector('div');
    if (!details.open) {body.replaceChildren(); return;}
    const key=details.dataset.fields || details.dataset.comparison;
    const row = displayById.get(key) || byId.get(key);
    if (details.dataset.comparison) {
      body.innerHTML = '<div class="pair"><div>' + image(row.overlay.preview, row.overlay.full, '50% overlay') +
        '</div><div>' + image(row.difference.preview, row.difference.full, 'Graphic difference') + '</div></div>';
    } else {
      body.innerHTML = '<table><tr><th>Field</th><th>Role / position</th><th>Default</th><th>Space; box</th></tr>' +
        row.fields.map(field => '<tr><td><code>' + escape(row.modelComposition ? (Object.entries(row.modelComposition.fields).filter(([,native])=>native===field.name).map(([name])=>name).join(', ') || field.slot?.key || field.name) : field.slot?.key || field.name) + '</code><br><small>' + escape(field.name) + '</small></td><td>' + escape(field.role + ' · ' + field.location) +
        '</td><td><code>' + escape(field.default) + '</code></td><td>' + escape(field.space) + '<br>' + escape(JSON.stringify(field.box || 'file input')) +
        '<br>' + escape(field.font_size || '') + ' / ' + escape(field.leading || '') + '</td></tr>').join('') +
        '</table><p>Compatibility names: ' + escape((row.aliases || []).join(', ') || 'None') + '</p><p>Canvas: ' + escape(JSON.stringify(row.canvas)) + '. ' + escape(row.notes.join(' ')) + '</p><ul>' +
        row.parts.map(part => '<li><a href="' + escape(part.url) + '">' + escape(part.name) + '</a></li>').join('') + '</ul>';
    }
  }, true);
  main.addEventListener('change', event => {
    const target=event.target;
    if (target.matches('[data-model-variant], [data-model-palette]')) {
      const modelId=target.dataset.modelVariant || target.dataset.modelPalette;
      const model=config.models.find(m => m.id===modelId);
      const current=displayById.get(target.closest('article').id) || visibleRows().find(r => r.model?.id===modelId);
      const variant=model.variants.find(v => v.id===(target.dataset.modelVariant ? target.value : current.modelVariant));
      const composition=variant.compositions.find(c => c.id===variant.default_source);
      modelChoices[modelId]={variant:variant.id,composition:composition.id,palette:target.dataset.modelPalette ? target.value : current.modelPalette};
      render();return;
    }
    if (!event.target.matches('[data-field-focus]')) return;
    const name = event.target.value, article = event.target.closest('article');
    article.querySelector('.slide-image')?.classList.add('show-areas');
    article.querySelectorAll('[data-box]').forEach(box => box.classList.toggle('muted', !!name && box.dataset.box !== name));
    const button = article.querySelector('[data-areas]'); if (button) button.textContent = 'Hide editable areas';
  });
  main.addEventListener('click', async event => {
    const areas = event.target.closest('[data-areas]');
    if (areas) {
      const visible = areas.closest('article').querySelector('.slide-image').classList.toggle('show-areas');
      areas.textContent = visible ? 'Hide editable areas' : 'Show editable areas'; return;
    }
    const button = event.target.closest('[data-copy]'); if (!button) return;
    const row = displayById.get(button.dataset.copy) || byId.get(button.dataset.copy);
    const example = button.dataset.copyKind === 'document' ? row.document : row.example;
    try {await navigator.clipboard.writeText(example);} catch {
      const node = document.createElement('textarea'); node.value = example; document.body.append(node);
      node.select(); document.execCommand('copy'); node.remove();
    }
    const label = button.textContent; button.textContent = 'Copied'; setTimeout(() => {button.textContent = label;}, 1500);
  });
  window.addEventListener('hashchange', followHash);
  if (single || !followHash()) render();
}
