"""Model/variant catalogue above the stable source-composition identifiers."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Explicit editorial groupings, not similarity-based or title-based inference.
GROUPS = [
 ('cover','Presentation cover',[('pattern','cover'),('wide-pattern','cover-light'),('photo','cover-photo'),('script','cover-script-blue'),('wide-title','cover-wide-title')]),
 ('agenda','Agenda',[('panels','contents'),('rail','tabbed-agenda'),('icons','agenda-with-icons'),('schedule','agenda-with-schedule')]),
 ('statement','Statement',[('arrow','statement-arrow'),('glow','glow-statement'),('plain','blue-statement'),('clipped','oversized-word'),('credit','statement-with-credit')]),
 ('icon-spotlight','Icon spotlight',[('compact','icon-spotlight-light'),('large','icon-spotlight-blue')]),
 ('dialogue','Dialogue',[('two-messages','chat-dialogue'),('three-messages','chat-three-messages'),('people','speech-panel'),('cards','people-speech-cards')]),
 ('oversized-number','Oversized number',[('plain','oversized-number-light'),('captioned','oversized-number-blue')]),
 ('paragraphs','Heading and paragraphs',[('left','title-paragraphs'),('centered','title-centered-paragraphs')]),
 ('list-rail','List beside a rail',[('three-items','list-rail-light'),('four-items','list-rail-blue'),('grouped','grouped-rail'),('stepped','stepped-rail-blue')]),
 ('levels','Three levels',[('default','privacy-levels'),('default','privacy-levels-blue')]),
 ('icon-cards','Icon cards',[('two','two-cards'),('three','three-cards'),('two-vertical','two-card-vertical'),('four-pillars','four-pillar-cards'),('summary','three-card-summary')]),
 ('text-cards','Text cards',[('four','four-card-grid'),('six-outline','six-outline-cards'),('six-detailed','six-explanation-cards'),('callout','callout-explanation')]),
 ('icon-process','Icon process',[('two','two-step-process'),('three','three-step-process'),('four','four-step-process'),('milestones','milestone-cards')]),
 ('icon-grid','Labelled icon grid',[('four','square-icon-grid'),('eight','eight-icon-grid'),('twelve','twelve-word-grid'),('row','five-icon-row')]),
 ('options','Options',[('devices','hardware-options'),('applications','software-options')]),
 ('split-comparison','Panel comparison',[('horizontal','horizontal-split'),('vertical','vertical-split'),('outlines','split-outline-cards'),('process','split-process-cards')]),
 ('image-text','Image and text',[('left','image-left'),('right','image-right'),('overlay','image-overlay'),('diagonal','diagonal-photo-title')]),
 ('image-grid','Image grid',[('four','four-images'),('portraits','three-portraits'),('pair','two-image-comparison'),('triptych','photo-triptych'),('title-pair','image-pair-title')]),
 ('collage','Image collage',[('asymmetric','gallery-collage'),('banner','photo-collage-banner'),('grid','photo-collage-grid'),('statistics','photo-statistics-collage')]),
 ('screenshots','Application screenshots',[('callout','screenshot-callout'),('pair','screenshot-pair'),('phone','phone-screenshot')]),
 ('metrics','Metric dashboard',[('four-counters','three-statistics'),('four-panels','metric-dashboard'),('summary','success-dashboard')]),
 ('charts','Charts',[('line','line-chart'),('two','two-charts'),('three','three-charts'),('bars','bar-comparison'),('scatter','scatter-comparison'),('stages','adoption-curve'),('bubbles','bubble-chart'),('series','price-lines')]),
 ('map','Annotated map',[('world','world-map'),('region','europe-map')]),
 ('timeline','Timeline',[('horizontal','horizontal-timeline'),('vertical','vertical-timeline'),('alternating','alternating-timeline'),('milestones','personal-timeline')]),
 ('sets','Set relationships',[('nested','nested-circles'),('separate','separate-circles'),('outlined','nested-outline-circles')]),
 ('radial','Radial diagram',[('goals','radial-goals'),('five','five-spoke-values'),('three','three-spoke-benefits'),('two-groups','two-radial-groups'),('target','bullseye-values')]),
 ('layer-stack','Layered structure',[('purposes','layered-stack'),('overview','layers-overview')]),
 ('binary-tree','Binary tree',[('compact','merkle-tree'),('wide','merkle-tree-wide'),('hierarchy','seed-key-tree')]),
 ('chain','Linked nodes',[('headers','block-chain'),('branches','fork-branches'),('annotated','blockchain-with-list'),('conflict','double-spend-diagram')]),
 ('protocol','Message exchange',[('paired-nodes','protocol-key-pair'),('symmetric','protocol-symmetric'),('public-nodes','protocol-public-keys'),('lock','protocol-key-lock'),('exchange','protocol-key-exchange'),('signed','protocol-signed-message'),('encrypted','protocol-encrypted-message'),('unlock','protocol-unlock-message'),('payload','protocol-signed-payload'),('setup','protocol-key-setup'),('transfer','protocol-token-transfer'),('routing','protocol-token-routing'),('aggregation','protocol-key-aggregation'),('aggregate','protocol-aggregate-signature'),('observer','protocol-eavesdropping'),('channel','protocol-encrypted-channel')]),
 ('transformation','Transformation pipeline',[('symmetric','symmetric-encryption'),('asymmetric','asymmetric-encryption'),('flow','encryption-flow'),('mapping','cipher-mapping')]),
 ('contact','Contact and next steps',[('contact','contact-qr'),('action','apply-qr')]),
]
NEUTRAL_TITLES = {
 'cover-dashboard':'Overview dashboard','network-environments':'Three environments','node-type-grid':'Three node types',
 'onchain-offchain':'Two approaches','coin-comparison':'Two-symbol comparison','whitepaper-blue':'Document spotlight',
 'partner-rail':'Organization rail','partner-media-grid':'Media grid','mission-badges':'Three badges',
 'nine-logo-grid':'Nine-symbol grid','image-logo-pair':'Image and symbol','three-statistics':'Four counters',
 'purchasing-power':'Value over time','currency-equivalence':'Equivalent values','split-currency':'Split value comparison',
 'diagram-annotated-energy':'Annotated system','card-statistics-process':'Cards and counters','large-figure':'Large diagram',
 'table':'Data table','hash-avalanche':'Input and output comparison','key-derivation':'Derivation path',
 'signature-flow':'Input and output flow','protocol-sequence':'Three-lane sequence','transaction-flow':'Two-lane process',
 'payoff-matrix':'Outcome matrix','payment-channel':'Two-way channel','proof-of-work-flow':'Processing flow',
 'cryptographic-assumptions':'Three assumptions','routing-graph':'Routing diagram','diagram-transaction-inputs':'Inputs and outputs',
 'seed-grid-caption':'Word grid and caption','diagram-pool-shares':'Shared work diagram','multi-signature':'Multiple approvals',
 'key-to-addresses':'One-to-many mapping','dual-consensus-diagram':'Two-system comparison','cipher-wheel':'Letter wheel',
 'blue-resources-columns':'Resource columns','genesis-information':'Record information','regtest-instructions':'Practical instructions',
 'block-inspection':'Record inspection','mining-card-grid':'Processing cards','hero-number':'Headline number',
}
SPECIAL = {'horizontal-split','vertical-split','benefits-limits','before-after','photo-split','onchain-offchain',
 'photo-statistics-collage','split-currency','cover-dashboard','partner-media-grid','gallery-collage','photo-collage-banner',
 'photo-collage-grid','image-overlay','diagonal-photo-title','statement-with-credit','purchasing-power','currency-equivalence'}


def native_palette(source):
    m=re.search(r'\\studiomeasuredcanvas\{[^}]+\}\{[^}]+\}\{[^}]+\}\{([^}]+)\}',source)
    if not m:m=re.search(r'\\studiopilotcanvas\{[^}]+\}\{([^}]+)\}',source)
    return 'blue' if m and m[1]=='bitpolito' else 'light'


def load_models(root=ROOT):
    path=root/'templates/models.json'
    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'schema':1,'models':[]}
    member={c['id']:(m,v,c) for m in data['models'] for v in m['variants'] for c in v['compositions']}
    ledger=root/'templates/review.json';selection=[];known={}
    if ledger.exists():
        for name in json.loads(ledger.read_text()).get('selection',[]):
            if name not in member:continue
            m,v,c=member[name]
            if m['id'] not in known:
                item={'model':m['id'],'variant':v['id'],'composition':name,'palette':c['native_palette'],'selected_compositions':[]};selection.append(item);known[m['id']]=item
            known[m['id']]['selected_compositions'].append(name)
    data['selection']=selection
    return data


def validate(root, entries):
    data=load_models(root)
    if not data['models']:return
    known={e['id'] for e in entries}; assigned=[]; ids=set()
    for model in data['models']:
        if model['id'] in ids:raise RuntimeError('Duplicate Studio model '+model['id'])
        ids.add(model['id']);variants=set()
        for variant in model['variants']:
            if variant['id'] in variants:raise RuntimeError('Duplicate model variant '+model['id'])
            variants.add(variant['id'])
            for item in variant['compositions']:
                assigned.append(item['id'])
                if item['palettes'] != [item['native_palette']]:
                    raise RuntimeError('Only original palette choices are supported: '+item['id'])
                if set(item['fields'].values())- {f['name'] for e in entries if e['id']==item['id'] for f in e['fields']}:
                    raise RuntimeError('Unknown semantic field in '+item['id'])
        if model['default_variant'] not in variants:raise RuntimeError('Missing default variant '+model['id'])
    if set(assigned)!=known or len(assigned)!=len(known):raise RuntimeError('Every composition must belong to one model variant')
    return len(ids)


def membership(root=ROOT):
    return {c['id']:(m,v,c) for m in load_models(root)['models'] for v in m['variants'] for c in v['compositions']}


def representatives(root,entries):
    by_id={e['id']:e for e in entries};output=[]
    for m in load_models(root)['models']:
        v=next(v for v in m['variants'] if v['id']==m['default_variant'])
        c=next(c for c in v['compositions'] if c['id']==v['default_source'])
        if c['id'] in by_id:output.append(by_id[c['id']])
        else:
            candidates=[by_id[c['id']] for v in m['variants'] for c in v['compositions'] if c['id'] in by_id]
            if candidates:output.append(candidates[0])
    return output


def dependencies(root, entries):
    """Prepared content and shared geometry required by the included compositions."""
    result = {name: root / name for entry in entries
              for name in entry.get('neutral_parts', []) + entry.get('shared_sources', []) + list(entry.get('prepared_resources', {}))}
    icons = root / 'images/studio/icon-palettes/manifest.json'
    if entries and icons.exists():
        result.update({part['pdf']: root / part['pdf']
                       for part in json.loads(icons.read_text())['parts']})
    return result


def registry(root, entries):
    """Subset registries advertise only included variants and palette resources."""
    included={e['id'] for e in entries};lines=[];member=membership(root)
    for model in load_models(root)['models']:
        vs=[]
        for v in model['variants']:
            cs=[c for c in v['compositions'] if c['id'] in included]
            if not cs:continue
            source=v['default_source'] if v['default_source'] in included else cs[0]['id']
            vs.append((v,cs,source))
        if not vs:continue
        default=model['default_variant'] if any(v['id']==model['default_variant'] for v,_,_ in vs) else vs[0][0]['id']
        lines.append(r'\DeclareStudioModel{'+model['id']+'}{'+default+'}')
        for v,cs,source in vs:
            palettes=sorted(set(p for c in cs for p in c['palettes']))
            native=member[source][2]['native_palette']
            lines.append(r'\DeclareStudioVariant{'+model['id']+'}{'+v['id']+'}{'+source+'}{'+native+'}{'+','.join(palettes)+'}')
            for p in palettes:
                chosen=next((c for c in cs if c['native_palette']==p),next(c for c in cs if p in c['palettes']))
                lines.append(r'\DeclareStudioChoice{'+model['id']+'}{'+v['id']+'}{'+p+'}{'+chosen['id']+'}')
    for name in sorted(included):
        if name not in member:continue
        m,v,c=member[name]
        lines.append(r'\DeclareStudioMembership{'+name+'}{'+m['id']+'}{'+v['id']+'}{'+c['native_palette']+'}{'+','.join(c['palettes'])+'}')
        entry=next(e for e in entries if e['id']==name)
        words=['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve']
        for f in entry['fields']:
            if f['type']=='graphic':
                n=f['slot']['number']; word=words[n-1] if n<=len(words) else str(n)
                lines.append(r'\DeclareStudioGraphicSemantic{'+name+'}{'+word+'}{'+str(n)+'}')
        for semantic,native in c['fields'].items():
            if semantic!=native:lines.append(r'\DeclareStudioSemantic{'+name+'}{'+semantic+'}{'+native+'}')
        if name=='cover-script-blue':lines.append(r'\DeclareStudioMirror{'+name+'}{title}{text-3}')
        for rejected in c.get('rejected_semantic_fields',[]):lines.append(r'\DeclareStudioRejectedSemantic{'+name+'}{'+rejected+'}')
    icons=root/'images/studio/icon-palettes/manifest.json'
    if icons.exists():
        lines.extend(r'\DeclareStudioIconPalette{'+a['name']+'}{'+a['pdf']+'}' for a in json.loads(icons.read_text())['parts'])
    return lines


def model_document(root,entries):
    from studio_templates import catalogue_document
    source=catalogue_document(representatives(root,entries)).replace('Studio\\\\Layout Library','Studio\\\\Model Catalogue')
    source=source.replace(r'\texttt{\string\studiotemplate\{\studiocataloguename\}}',r'\texttt{\studiocataloguename}')
    member=membership(root)
    for entry in representatives(root,entries):
        model,variant,composition=member[entry['id']]
        command=r'\studiotemplate[variant={'+variant['id']+'}]{'+model['id']+'}'
        source=source.replace(r'\studiotemplate{'+entry['id']+'}',command)
        source=source.replace(r'\gdef\studiocataloguename{\detokenize{'+entry['id']+'}}',r'\gdef\studiocataloguename{\detokenize{'+command+'}}')
    return source


def generated(root,entries):
    data=load_models(root)
    if not data['models']:return {}
    from studio_templates import catalogue_document
    lines=['<!-- Generated by scripts/review.py sync; edit templates/models.json. -->','# Studio models','',
           f"{len(data['models'])} models retain {len(entries)} source compositions. Colour choices do not add catalogue pages.",'',
           '| Model | Variants | Default source |','| --- | --- | --- |']
    migration=['<!-- Generated by scripts/review.py sync. -->','# Studio composition migration','',
               'All previous names remain usable. Defaults are neutral; original references remain in technical metadata.','',
               '| Existing name | Model | Variant | Native palette |','| --- | --- | --- | --- |']
    for m in data['models']:
        lines.append('| `'+m['id']+'` | '+', '.join('`'+v['id']+'`' for v in m['variants'])+' | `'+next(v['default_source'] for v in m['variants'] if v['id']==m['default_variant'])+'` |')
        for v in m['variants']:
            for c in v['compositions']:migration.append('| `'+c['id']+'` | `'+m['id']+'` | `'+v['id']+'` | '+c['native_palette']+' |')
    guides=model_guides(root,entries)
    return {**guides, Path('templates/MODELS.md'):'\n'.join(lines)+'\n',Path('templates/MIGRATION.md'):'\n'.join(migration)+'\n',
            Path('examples/studio-model-catalogue.tex'):model_document(root,entries)}


def resolve(root,name,variant=None,palette=None):
    data=load_models(root);member=membership(root);models={m['id']:m for m in data['models']}
    if name in models:
        model=models[name];vid=variant or model['default_variant']
        v=next((v for v in model['variants'] if v['id']==vid),None)
        if v is None:raise ValueError('Unknown variant '+name+'/'+vid)
        c=next(c for c in v['compositions'] if c['id']==v['default_source'])
        if palette:
            c=next((candidate for candidate in v['compositions'] if candidate['native_palette']==palette),c)
    elif name in member:
        model,v,c=member[name]
        if variant:return resolve(root,model['id'],variant,palette)
        if palette:c=next((candidate for candidate in v['compositions'] if candidate['native_palette']==palette),c)
    else:raise ValueError('Unknown Studio model '+name)
    p=palette or c['native_palette']
    if p not in c['palettes']:raise ValueError('Unsupported palette '+p+' in '+model['id']+'/'+v['id'])
    return model,v,c,p


def palette_document(root,entries):
    from studio_templates import catalogue_document
    source=catalogue_document(entries)
    source=source[:source.index(r'\begin{document}')]+r'\begin{document}'+'\n'
    for e in entries:
        for p in e['palettes']:
            source+=r'\gdef\studiocataloguename{'+e['id']+' / '+p+'}\n'+r'\studiotemplate[palette='+p+']{'+e['id']+'}\n'
    return source+r'\end{document}'+'\n'


def model_guides(root,entries):
    by_id={e['id']:e for e in entries};files={}
    for m in load_models(root)['models']:
        variants=[(v,[c for c in v['compositions'] if c['id'] in by_id]) for v in m['variants']]
        variants=[(v,cs) for v,cs in variants if cs]
        if not variants:continue
        lines=['<!-- Generated by scripts/review.py sync; edit templates/models.json and composition metadata. -->','# '+m['title'],'',
               'Model: `'+m['id']+'`. Each call creates a complete slide. Inter, geometry and text sizes are fixed.','',
               '[Model index](../../../templates/MODELS.md) · [Palette and content guide](../../STUDIO-MODELS.md)','',
               '```latex',r'\studiosetup{palette=light}',r'\studiotemplate[variant='+variants[0][0]['id']+']{'+m['id']+'}','```','',
               'Palette switches are available only where the original composition exists in both colours.',
               'Unsupported explicit choices fail. A global palette leaves special compositions in their native treatment.','',
               '## Variants and named fields','']
        for v,cs in variants:
            c=cs[0];e=by_id[c['id']]
            palettes=sorted({p for item in cs for p in item['palettes']})
            lines+=['### '+v['id'],'','Original palettes: '+', '.join(palettes)+'.','',
                    '[Current source](../../../'+e['source']+') · [Full slot guide](../guides/'+c['id']+'.md)','',
                    '| Field | Default | Available space |','| --- | --- | --- |']
            for semantic,native in c['fields'].items():
                f=next(f for f in e['fields'] if f['name']==native)
                value=f['default'].replace('|','&#124;').replace('\n',' ')
                from studio_guides import dimensions
                lines.append('| `'+semantic+'` | <code>'+__import__('html').escape(value[:110])+'</code> | '+dimensions(e,f)+' |')
            if e.get('options'):
                lines += ['', 'Layout options: ' + ', '.join('`'+key+'='+str(option['default']).lower()+'` ('+option['type']+')' for key,option in e['options'].items()) + '. See the full slot guide for both treatments.']
            graphics=[f for f in e['fields'] if f['type']=='graphic']
            if graphics:lines+=['','Graphic slots also accept named `icon-one`, `image-one`, `graphic-one` keys (then two, three, …), following their stable slot numbers. See the full slot guide for position and bounds.']
            lines+=['','Omitted fields retain these descriptive defaults; empty values retain their allocated space. Numbers and charts are illustrative.','']
        from studio_guides import PREAMBLE,END,command
        first_variant,first_compositions=variants[0]
        first=first_compositions[0];first_entry=by_id[first['id']]
        options={'variant':first_variant['id'],'palette':first['native_palette']}
        for key,native in list(first['fields'].items())[:2]:
            f=next(f for f in first_entry['fields'] if f['name']==native)
            if f['type']=='text':options[key]=f['default']
        lines+=['## Complete one-slide example','','```latex',(PREAMBLE+command(m['id'],options)+'\n'+END).rstrip(),'```','']
        files[Path('docs/templates/models/'+m['id']+'.md')]='\n'.join(lines).rstrip()+'\n'
    return files


def choice_inputs(root,entry,palette,base):
    """Fingerprint an existing original, never an invented opposite-colour render."""
    if palette != entry['native_palette']:
        raise ValueError('No original '+palette+' palette for '+entry['id'])
    return dict(base, **{'@palette':palette})


def render_palette_previews(root, pdf):
    """Compatibility entry point: refresh original previews without duplicates."""
    from studio_templates import render_previews
    render_previews(root, pdf)
    return 0


def check_palette_previews(root, entries):
    """Original colour pairs reuse their own composition previews."""
    for entry in entries:
        if entry['palettes'] != [entry['native_palette']]:
            raise RuntimeError('Unexpected synthetic palette for ' + entry['id'])
    obsolete = list((root / 'docs/templates/previews').glob('*--*.png'))
    if obsolete:
        raise RuntimeError('Obsolete duplicate palette thumbnails: ' + ', '.join(p.name for p in obsolete))
    return 0


def selection_document(root,entries,showcase=False):
    from studio_templates import catalogue_document
    by_id={e['id']:e for e in entries};items=[s for s in load_models(root)['selection'] if s['composition'] in by_id]
    source=catalogue_document([by_id[s['composition']] for s in items])
    for s in items:
        old=r'\studiotemplate{'+s['composition']+'}'
        options='variant={'+s['variant']+'},palette={'+s['palette']+'}'
        if showcase and s['model']=='cover':options+=r',title={\inserttitle},author={\insertauthor},institute={\insertinstitute}'
        source=source.replace(old,r'\studiotemplate['+options+']{'+s['model']+'}')
    if showcase:
        source=source.replace(r'\title{Studio\\Layout Library}',r'\title{Presentation\\Slide Layouts}').replace('Editable slide templates','Department or organization')
    return source


def expand_model_names(root,names):
    models=load_models(root)['models'];known={m['id'] for m in models};requested=set(names)
    if requested-known:raise ValueError('Unknown Studio models: '+', '.join(sorted(requested-known)))
    return [c['id'] for m in models if m['id'] in requested for v in m['variants'] for c in v['compositions']]
