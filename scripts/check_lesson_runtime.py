"""Check the optional lesson runtime without changing shared sources."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
import argparse
parser=argparse.ArgumentParser(description='Verify editable lesson fields, empty content, normal-frame isolation and explicit errors.')
parser.add_argument('--backend',choices=('docker','native'),default='docker')
parser.add_argument('--image',default='bitbeamer-latex:local')
args=parser.parse_args()
x=json.load(open(root/'library/index.json'));sid=x['decks']['bitcoin-introduction-short']['slides'][0];s=x['slides'][sid];l=x['layouts'][s['layout']];lid=s['layout'];text_fields=[f for f in l['fields'] if f['type']=='text'];title=next(f['name'] for f in text_fields if f['name']=='title');empty=','.join(f['name']+'={}' for f in text_fields)
cases={
'fixed-content':(r'\studiotemplate{bitcoin-supply}',None),
'fixed-content-override':(r'\studiotemplate[value-one={99 M}]{bitcoin-supply}','accepts no options'),
'custom-and-reset':(r'\studiotemplate['+title+r'={Local review}]{'+lid+'}\n'+r'\studiotemplate['+empty+']{'+lid+'}\n'+r'\begin{frame}{Normal frame}Ordinary editable content.\end{frame}',None),
'custom-graphic':(r'\studiotemplate[graphic-one={\cow[height=1cm]},'+title+r'={Custom art}]{'+lid+'}',None),
'unknown-field':(r'\studiotemplate[missing-field={Unknown}]{'+lid+'}','Unknown field'),
'unsupported-palette':(r'\studiotemplate[palette='+('light' if l['palette']=='blue' else 'blue')+']{'+lid+'}','Unsupported palette'),
'overflow':(r'\studiotemplate['+title+r'={One\\Two\\Three\\Four\\Five}]{'+lid+'}','Text overflow'),
'graphic-overflow':(r'\studiotemplate[graphic-one={\rule{30cm}{30cm}}]{'+lid+'}','Graphic overflow')}
reports=[]
for name,(content,expected) in cases.items():
 folder=root/'build/library/runtime-checks'/name;folder.mkdir(parents=True,exist_ok=True);source=folder/'main.tex';source.write_text(r'\documentclass[aspectratio=169]{beamer}'+'\n'+r'\usetheme{bitpolito-studio}'+'\n'+r'\usepackage{bitpolitostudiolibrary}'+'\n'+r'\begin{document}'+'\n'+content+'\n'+r'\end{document}'+'\n')
 command=[sys.executable,str(root/'scripts/build.py'),str(source),str(folder),'--backend',args.backend,'--image',args.image];result=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(folder/'launcher.log').write_text(result.stdout);log=(folder/'main.log').read_text(errors='replace')
 if expected:
  if result.returncode==0 or expected not in log:raise RuntimeError(name+' did not reject the invalid content as expected')
 else:
  from deck import log_issues
  if result.returncode or log_issues(log):raise RuntimeError(name+' failed: '+str(log_issues(log)))
 reports.append({'case':name,'status':'passed','expected_error':expected})
(root/'build/library/runtime-checks/report.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports,indent=2))
