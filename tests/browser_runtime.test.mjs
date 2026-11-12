import {test} from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {PassThrough} from 'node:stream';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {startBrowser} from '../scripts/browser_runtime.mjs';

function fixture(t) {
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'bitbeamer-browser-test-'));
  t.after(()=>fs.rmSync(profile,{recursive:true,force:true}));
  const child=new EventEmitter();child.stderr=new PassThrough();child.killed=false;
  child.kill=()=>{child.killed=true;};
  return {profile,child,options:{profile,timeoutMs:250,spawnBrowser:()=>child}};
}

test('waits for a complete DevTools port and retains startup diagnostics',async t=>{
  const {profile,child,options}=fixture(t);
  fs.writeFileSync(path.join(profile,'DevToolsActivePort'),'');
  setTimeout(()=>{child.stderr.write('startup note');fs.writeFileSync(path.join(profile,'DevToolsActivePort'),'9222\n/devtools/browser/example');},20);
  const result=await startBrowser('fixture',[],options);
  assert.equal(result.child,child);assert.equal(result.port,'9222');
  assert.equal(result.diagnostics(),'startup note');assert.equal(child.killed,false);
});

test('reports spawn errors and stops the process',async t=>{
  const {child,options}=fixture(t);
  setImmediate(()=>child.emit('error',new Error('executable missing')));
  await assert.rejects(startBrowser('fixture',[],options),/executable missing/);
  assert.equal(child.killed,true);
});

test('reports early exit with actual stderr instead of a startup timeout',async t=>{
  const {child,options}=fixture(t);
  setImmediate(()=>{child.stderr.write('sandbox startup failed');child.emit('exit',1,null);});
  await assert.rejects(startBrowser('fixture',[],options),/exited \(1\)[\s\S]*sandbox startup failed/);
  assert.equal(child.killed,true);
});

test('kills an unresponsive browser and includes its stderr on timeout',async t=>{
  const {child,options}=fixture(t);child.stderr.write('browser stalled');
  await assert.rejects(startBrowser('fixture',[],options),/timeout[\s\S]*browser stalled/);
  assert.equal(child.killed,true);
});
