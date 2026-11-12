// Shared lifecycle for the optional offline Chromium maintenance check.
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {setTimeout as sleep} from 'node:timers/promises';

export async function startBrowser(executable, args, {profile, timeoutMs=30000, spawnBrowser=spawn}={}) {
  const child=spawnBrowser(executable,args,{stdio:['ignore','ignore','pipe']});
  let stderr='', failure;
  child.stderr?.on('data',chunk=>{stderr=(stderr+chunk).slice(-12000);});
  child.once('error',error=>{failure=error.message;});
  child.once('exit',(code,signal)=>{failure=`exited (${signal || code})`;});
  const deadline=Date.now()+timeoutMs, portFile=path.join(profile,'DevToolsActivePort');
  try {
    while(Date.now()<deadline) {
      if(failure)throw Error(`Browser ${failure}`);
      try {
        const port=fs.readFileSync(portFile,'utf8').split('\n')[0];
        if(/^\d+$/.test(port))return {child,port,diagnostics:()=>stderr};
      } catch(error) {if(error.code!=='ENOENT')throw error;}
      await sleep(100);
    }
    throw Error(`Browser startup timeout after ${timeoutMs} ms`);
  } catch(error) {
    child.kill();
    throw Error(`${executable}: ${error.message}${stderr ? '\n'+stderr : ''}`);
  }
}
