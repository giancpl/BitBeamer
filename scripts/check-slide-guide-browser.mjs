// Optional real-browser maintenance check. Node 22+ and Chromium/Chrome; no network service.
import {execFileSync} from 'node:child_process';
import {startBrowser} from './browser_runtime.mjs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'), output=root+'/build/checks/slide-guide/browser';
const candidates=[process.env.CHROMIUM,'google-chrome','chromium','chromium-browser'].filter(Boolean);
let browser;for(const candidate of candidates){try{execFileSync(candidate,['--version'],{stdio:'ignore'});browser=candidate;break;}catch{}}
if(!browser)throw Error('Install Chromium/Chrome or set CHROMIUM to its executable. This is an optional maintenance check.');
fs.mkdirSync(output,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'bitbeamer-guide-browser-'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let ws,chrome;try {
const started=await startBrowser(browser,['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--allow-file-access-from-files','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{profile});
chrome=started.child;
const port=started.port;
const tabs=await (await fetch('http://127.0.0.1:'+port+'/json')).json();
ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let serial=0;const pending=new Map(),errors=[],requests=[];
ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const pair=pending.get(m.id);pending.delete(m.id);m.error?pair.reject(Error(m.error.message)):pair.resolve(m.result);}else{if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(m.method==='Network.requestWillBeSent')requests.push(m.params.request.url);}};
function call(method,params={}){const id=++serial;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending.delete(id);reject(Error('DevTools response timeout: '+method));},30000);pending.set(id,{resolve:value=>{clearTimeout(timer);resolve(value);},reject:error=>{clearTimeout(timer);reject(error);}});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression){for(let i=0;i<150;i++){if(await evaluate(expression))return;await sleep(100);}throw Error('Timeout: '+expression+'; '+JSON.stringify({errors,body:await evaluate("document.body?.innerText.slice(-1500)")}));}
async function goto(path){const url=new URL(path,pathToFileURL(root+'/').href).href; if(await evaluate('location.href')!==url){await evaluate('window.__bitbeamerNavigationPending=true');await call('Page.navigate',{url});await wait("window.__bitbeamerNavigationPending!==true && document.readyState==='complete'");}await wait("document.querySelectorAll('#slides article').length>0");}
async function screenshot(name){const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(output+'/'+name+'.png',Buffer.from(r.data,'base64'));}
await call('Runtime.enable');await call('Network.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await goto('docs/slides/index.html');
assert.ok(await evaluate("document.querySelectorAll('#slides article').length<=12 && document.querySelectorAll('#slides article').length>0"));
assert.equal(requests.some(u=>u.includes('/previews/hd/')),false);
assert.equal(requests.some(u=>u.includes('catalogue-library.js')||u.includes('catalogue-lessons.js')),false);
assert.equal(await evaluate("typeof window.BITBEAMER_LIBRARY"),'undefined');
assert.equal(await evaluate("typeof window.BITBEAMER_EXTRA_SLIDES"),'undefined');
await screenshot('guide-desktop');
await evaluate("document.querySelector('.actions button').click()");await wait("['Copied','Selected — copy with Ctrl/Cmd+C'].includes(document.querySelector('.actions button').textContent)");
await evaluate("document.querySelector('[data-quality=ready]').click()");
await wait("document.querySelector('[data-quality=ready]').getAttribute('aria-pressed')==='true'");
assert.equal(await evaluate("[...document.querySelectorAll('#slides article small')].some(n=>n.textContent.includes('in review'))"),false);
await evaluate("document.querySelector('[data-quality=review]').click()");
await wait("document.querySelectorAll('#slides article').length>0");
await evaluate("document.querySelector('[data-step=\"1\"]').click()");assert.ok(await evaluate("document.querySelectorAll('#slides article').length<=12"));
await evaluate("document.querySelector('[data-step=\"-1\"]').click()");
await evaluate("document.querySelector('.image-button').click()");await wait("document.querySelector('#inspect-image').complete && document.querySelector('#inspect-image').naturalWidth===1600");
assert.equal(await evaluate("document.querySelector('#inspector').open"),true);
await evaluate("document.querySelector('#inspect-tools button').click()");assert.equal(await evaluate("document.querySelector('#field-map').hasAttribute('hidden')"),false);
await evaluate("document.querySelector('#inspect-close').click();document.querySelector('[data-view=decks]').click()");await wait("document.querySelector('#count').textContent.includes('presentations')");
assert.ok(await evaluate("document.querySelectorAll('#slides article').length<=12 && document.querySelectorAll('#slides article').length>0"));
await evaluate("document.querySelector('.image-button').click()");await wait("document.querySelector('#inspect-caption').textContent.includes(' / ')");
await evaluate("document.querySelector('#inspect-sequence button:nth-child(2)').click()");await wait("document.querySelector('#inspect-caption').textContent.startsWith('2 / ')");
await evaluate("document.querySelector('#inspect-close').click();document.querySelector('[data-view=blocks]').click()");await wait("document.querySelector('#count').textContent.includes('blocks')");
assert.ok(await evaluate("document.querySelectorAll('#slides article').length<=12 && document.querySelectorAll('#slides article').length>0"));
await evaluate("document.querySelector('#search').value='hash';document.querySelector('#search').dispatchEvent(new Event('input'))");await wait("document.querySelector('#count').textContent.includes('blocks')");
assert.ok(await evaluate("document.querySelectorAll('#slides article').length>0"));
await goto('docs/templates/index.html?template=cover&variant=script&maintenance=1');await wait("document.querySelector('#slides article').id==='protocol'");
assert.ok(await evaluate("document.querySelector('#slides pre').textContent.includes('message-relay')"));
await evaluate("document.querySelector('.image-button').click()");await wait("document.querySelector('#inspect-tools').textContent.includes('Original comparison')");
if(fs.existsSync(root+'/build/checks/slide-guide/comparisons.js')){
await evaluate("[...document.querySelectorAll('#inspect-tools button')].find(b=>b.textContent==='Original comparison').click()");await wait("document.querySelectorAll('#inspect-comparison img').length===2");
assert.ok(await evaluate("document.querySelector('#inspect-comparison img').src.includes('figma-0545')"));
await screenshot('guide-comparison');
}
await goto('docs/slides/index.html?collection=fixed');await wait("document.querySelector('#slides .badge').textContent==='Fixed content'");assert.ok(await evaluate("document.querySelectorAll('#slides article').length<=12"));
await goto('docs/slides/index.html?template=levels&palette=blue');await wait("document.querySelector('#slides pre').textContent.includes('palette={blue}')");
await evaluate("document.querySelector('.choice').value='0';document.querySelector('.choice').dispatchEvent(new Event('change'))");
assert.ok(await evaluate("document.querySelector('#slides pre').textContent.includes('palette={light}')"));
await goto('docs/slides/index.html?view=decks&item=bitpolito-introduction');
await wait("document.querySelector('#inspect-caption').textContent.startsWith('1 / 11')");
for(let i=0;i<10;i++)await evaluate("document.querySelector('#inspect-sequence button:nth-child(2)').click()");
await wait("document.querySelector('#inspect-caption').textContent.startsWith('11 / 11') && document.querySelector('#inspect-image').complete && document.querySelector('#inspect-image').naturalWidth===1600");
assert.ok(await evaluate("document.querySelector('#inspect-image').src.includes('bitpolito-contact')"));
await goto('docs/slides/index.html?batch=covers-01&maintenance=1');
await wait("document.querySelectorAll('#slides article').length===5");
assert.deepEqual(await evaluate("[...document.querySelectorAll('#slides article')].map(n=>n.id)"),['cover','cover-light','cover-photo','cover-wide-title','bitpolito-wordmark-cover']);
assert.equal(await evaluate("document.querySelectorAll('#slides .choice').length"),0);
assert.ok(await evaluate("document.querySelector('#notice').textContent.includes('Covers')"));
await screenshot('covers-review-batch');
if(fs.existsSync(root+'/build/checks/slide-guide/comparisons.js')){
await evaluate("[...document.querySelectorAll('#slides .actions button')].find(b=>b.textContent==='Compare original / replica').click()");
await wait("document.querySelectorAll('#inspect-comparison img').length===2");
assert.ok(await evaluate("document.querySelector('#inspect-comparison img').src.includes('figma-0175')"));
}
await goto('docs/slides/index.html?template=section-divider');
await wait("document.querySelector('.suggested-sequence')!==null");
await evaluate("document.querySelector('.suggested-sequence').open=true");
assert.ok(await evaluate("document.querySelector('.suggested-sequence pre').textContent.includes(']{section-divider}') && document.querySelector('.suggested-sequence pre').textContent.includes(']{statement}')"));
await evaluate("document.querySelector('.suggested-sequence button').click()");
await wait("['Copied','Selected — copy with Ctrl/Cmd+C'].includes(document.querySelector('.suggested-sequence button').textContent)");
await screenshot('section-sequence');
await evaluate("document.querySelector('.suggested-sequence li:nth-child(2) a').click()");
await wait("document.querySelector('#slides article')?.id==='statement'");
assert.ok(await evaluate("document.querySelector('#slides .body > pre').textContent.includes('variant={arrow}') && (document.querySelector('#slides .body > pre').textContent.match(/studiotemplate/g)||[]).length===1"));
// A variant may move between Ready and In review as graphical approvals evolve.
await evaluate("window.__glowChoice=window.BITBEAMER_SLIDES.rows.find(r=>r.id==='statement').choices.findIndex(c=>c.id==='glow-statement');const choice=window.BITBEAMER_SLIDES.rows.find(r=>r.id==='statement').choices[window.__glowChoice];document.querySelector('[data-quality='+ (choice.status==='approved'?'ready':'review') +']').click()");
await wait("[...document.querySelectorAll('.choice option')].some(o=>Number(o.value)===window.__glowChoice)");
await evaluate("document.querySelector('.choice').value=String(window.__glowChoice);document.querySelector('.choice').dispatchEvent(new Event('change'))");
await wait("document.querySelector('#slides .body > pre').textContent.includes('variant={glow}') && document.querySelector('.suggested-sequence')===null");
await goto('docs/slides/index.html');await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await sleep(400);
assert.ok(await evaluate("document.documentElement.scrollWidth<=window.innerWidth+1"));await screenshot('guide-mobile');
await evaluate("document.querySelector('.image-button').click()");await wait("document.querySelector('#inspect-image').naturalWidth===1600");assert.ok(await evaluate("document.querySelector('#inspector').getBoundingClientRect().width<=innerWidth"));await screenshot('guide-mobile-detail');
const report={status:'passed',browser:execFileSync(browser,['--version'],{encoding:'utf8'}).trim(),offline:true,cases:['12-card pagination and copy command','no eager HD or extra datasets','1600px detail','editable areas','presentation and reusable-block views','sequence navigation','search','legacy URL and variant adapter','local comparison','fixed slides and explicit Ready/In review filtering','palette choice','eleven-page canonical BitPolito pack','five-cover review batch with separate compositions','optional divider/arrow sequence and independent arrow use','390px mobile layout'],javascript_errors:errors,network:requests.filter(u=>/^https?:/.test(u))};
assert.equal(errors.length,0);assert.equal(report.network.length,0);fs.writeFileSync(output+'/browser.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
} catch(error) {console.error(error);process.exitCode=1;} finally {ws?.close();chrome?.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true,maxRetries:5,retryDelay:100});}catch{}}
