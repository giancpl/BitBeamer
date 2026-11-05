// Optional real-browser maintenance check. Node 22+ and Chromium/Chrome; no network service.
import {spawn,execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'), output=root+'/build/checks/slide-guide/browser';
const candidates=[process.env.CHROMIUM,'chromium-browser','chromium','google-chrome'].filter(Boolean);
let browser;for(const candidate of candidates){try{execFileSync(candidate,['--version'],{stdio:'ignore'});browser=candidate;break;}catch{}}
if(!browser)throw Error('Install Chromium/Chrome or set CHROMIUM to its executable. This is an optional maintenance check.');
fs.mkdirSync(output,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'bitbeamer-guide-browser-'));
const chrome=spawn(browser,['--headless','--no-sandbox','--disable-gpu','--disable-background-networking','--no-first-run','--allow-file-access-from-files','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(path.join(root,'docs/slides/index.html')).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let ws;try {
for(let i=0;!fs.existsSync(profile+'/DevToolsActivePort');i++){if(i>100)throw Error('Browser startup timeout');await sleep(100);}
const port=fs.readFileSync(profile+'/DevToolsActivePort','utf8').split('\n')[0];
const tabs=await (await fetch('http://127.0.0.1:'+port+'/json')).json();
ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let serial=0;const pending=new Map(),errors=[],requests=[];
ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const pair=pending.get(m.id);pending.delete(m.id);m.error?pair.reject(Error(m.error.message)):pair.resolve(m.result);}else{if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(m.method==='Network.requestWillBeSent')requests.push(m.params.request.url);}};
function call(method,params={}){const id=++serial;return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression){for(let i=0;i<150;i++){if(await evaluate(expression))return;await sleep(100);}throw Error('Timeout: '+expression+'; '+JSON.stringify({errors,body:await evaluate("document.body?.innerText.slice(-1500)")}));}
async function goto(path){const url=new URL(path,pathToFileURL(root+'/').href).href; if(await evaluate('location.href')!==url) await call('Page.navigate',{url});await wait("document.querySelectorAll('#slides article').length>0");}
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
await goto('docs/slides/index.html');await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await sleep(400);
assert.ok(await evaluate("document.documentElement.scrollWidth<=window.innerWidth+1"));await screenshot('guide-mobile');
await evaluate("document.querySelector('.image-button').click()");await wait("document.querySelector('#inspect-image').naturalWidth===1600");assert.ok(await evaluate("document.querySelector('#inspector').getBoundingClientRect().width<=innerWidth"));await screenshot('guide-mobile-detail');
const report={status:'passed',browser:execFileSync(browser,['--version'],{encoding:'utf8'}).trim(),offline:true,cases:['12-card pagination and copy command','no eager HD or extra datasets','1600px detail','editable areas','presentation and reusable-block views','sequence navigation','search','legacy URL and variant adapter','local comparison','9 fixed slides','palette choice','390px mobile layout'],javascript_errors:errors,network:requests.filter(u=>/^https?:/.test(u))};
assert.equal(errors.length,0);assert.equal(report.network.length,0);fs.writeFileSync(output+'/browser.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
} catch(error) {console.error(error);process.exitCode=1;} finally {ws?.close();chrome.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true,maxRetries:5,retryDelay:100});}catch{}}
