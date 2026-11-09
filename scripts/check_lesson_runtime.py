"""Check the optional lesson runtime without changing shared sources."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
import argparse
parser=argparse.ArgumentParser(description='Verify editable lesson fields, empty content, normal-frame isolation and explicit errors.')
parser.add_argument('--backend',choices=('docker','native'),default='docker')
parser.add_argument('--image',default='bitbeamer-latex:local')
args=parser.parse_args()
x=json.load(open(root/'library/index.json', encoding='utf-8'));sid=x['decks']['bitcoin-introduction-short']['slides'][0];s=x['slides'][sid];l=x['layouts'][s['layout']];lid=s['layout'];text_fields=[f for f in l['fields'] if f['type']=='text'];title=next(f['name'] for f in text_fields if f['name']=='title');empty=','.join(f['name']+'={}' for f in text_fields)
cases={
'glow-short-long-empty':(r'\studiotemplate[variant=glow,statement={One shared idea}]{statement}'+ '\n' + r'\studiotemplate[variant=glow,statement={Connecting people through shared ideas}]{statement}'+ '\n' + r'\studiotemplate[variant=glow,statement={}]{statement}',None),
'glow-explicit-two-lines':(r'\studiotemplate[variant=glow,statement={Connecting people\\through shared ideas}]{statement}',None),
'glow-three-lines':(r'\studiotemplate[variant=glow,statement={One\\Two\\Three}]{statement}','Text overflow in glow-statement/statement'),
'section-pair-two-lines':(r'\studiotemplate[title={Understanding\\digital money}]{section-divider}'+ '\n' + r'\studiotemplate[variant=arrow,title={A shared system\\without a central owner.}]{statement}',None),
'section-divider-three-lines':(r'\studiotemplate[title={One\\Two\\Three}]{section-divider}','Text overflow in section-divider/title'),
'standalone-arrow-two-lines':(r'\studiotemplate[variant=arrow,title={An independent idea\\with room for a second line.}]{statement}',None),
'standalone-arrow-three-lines':(r'\studiotemplate[variant=arrow,title={One\\Two\\Three}]{statement}','Text overflow'),
'five-social-closing':(r'\closingframe[title={Custom handle}]',None),
'five-social-no-qr':(r'\closingframe[qrcode=false,title={}]'+ '\n' + r'\closingframe',None),
'pack-closing-fields':(r'\studiotemplate[title={Custom handle},qrcode=false,copyright={}]{bitpolito-contact}',None),
'fixed-brand-cover':(r'\studiotemplate{bitpolito-wordmark-cover}',None),
'fixed-brand-cover-override':(r'\studiotemplate[title={Change}]{bitpolito-wordmark-cover}','accepts no options'),
'closing-removed-four-social':(r'\closingframe[variant=four-socials]',"do not know the key"),
'catalogue-removed-socials':(r'\studiotemplate[socials=4]{closing}',"field 'socials' in closing"),
'closing-invalid-qr':(r'\closingframe[qrcode=maybe]','Invalid boolean'),
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
 folder=root/'build/library/runtime-checks'/name;folder.mkdir(parents=True,exist_ok=True);source=folder/'main.tex';source.write_text(r'\ifdefined\pdfminorversion\pdfminorversion=7\fi'+'\n'+r'\documentclass[aspectratio=169]{beamer}'+'\n'+r'\usetheme{bitpolito-studio}'+'\n'+r'\usepackage{bitpolitostudiolibrary}'+'\n'+r'\begin{document}'+'\n'+content+'\n'+r'\end{document}'+'\n', encoding="utf-8")
 command=[sys.executable,str(root/'scripts/build.py'),str(source),str(folder),'--backend',args.backend,'--image',args.image];result=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(folder/'launcher.log').write_text(result.stdout, encoding="utf-8");log=(folder/'main.log').read_text(errors='replace', encoding="utf-8")
 if expected:
  if result.returncode==0 or expected not in log:raise RuntimeError(name+' did not reject the invalid content as expected')
 else:
  from deck import log_issues
  if result.returncode or log_issues(log):raise RuntimeError(name+' failed: '+str(log_issues(log)))
 reports.append({'case':name,'status':'passed','expected_error':expected})
(root/'build/library/runtime-checks/report.json').write_text(json.dumps(reports,indent=2)+'\n', encoding="utf-8");print(json.dumps(reports,indent=2))
