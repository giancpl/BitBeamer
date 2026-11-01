/* Offline, bounded rendering: no archive-wide image nodes. */
(() => {
  const parts=JSON.parse(document.querySelector('#parts-data').textContent);
  const search=document.querySelector('#search'),main=document.querySelector('main');
  let page=0;const pageSize=24;
  function render(){
    const query=search.value.trim().toLowerCase();
    const rows=parts.filter(p=>(p.name+' '+p.reference).toLowerCase().includes(query));
    const pages=Math.max(1,Math.ceil(rows.length/pageSize));page=Math.min(page,pages-1);
    main.replaceChildren();
    for(const p of rows.slice(page*pageSize,(page+1)*pageSize)){
      const article=document.createElement('article');
      const image=document.createElement('img');image.src='previews/'+p.name+'.png';image.alt=p.name;image.loading='lazy';article.append(image);
      const ref=document.createElement('p');ref.textContent=p.reference;article.append(ref);
      const command='\\studiopart[width=3cm]{'+p.name+'}';
      const code=document.createElement('code');code.textContent=command;article.append(code);
      const button=document.createElement('button');button.textContent='Copy';button.onclick=async()=>{
        try{await navigator.clipboard.writeText(command)}catch(e){const t=document.createElement('textarea');t.value=command;document.body.append(t);t.select();document.execCommand('copy');t.remove()}button.textContent='Copied';};article.append(button);
      const links=document.createElement('p');
      for(const [label,url] of [['Prepared PDF','../../images/studio/'+p.folder+'/'+p.name+'.pdf'],['Derived SVG','../../'+p.source]]){
        const link=document.createElement('a');link.textContent=label;link.href=url;links.append(link,document.createTextNode(' '));
      }
      article.append(links);main.append(article);
    }
    document.querySelector('#count').textContent=rows.length+' / '+parts.length+' parts · Page '+(page+1)+' / '+pages;
    document.querySelectorAll('[data-page]').forEach(b=>b.disabled=Number(b.dataset.page)<0?page===0:page===pages-1);
  }
  search.addEventListener('input',()=>{page=0;render()});
  document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>{page+=Number(b.dataset.page);render();window.scrollTo(0,0)});
  render();
})();
