"""Offline lesson discovery and isolated, dependency-scoped personal imports."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MARKER = '% BITBEAMER: INSERT BLOCKS HERE'
IDENTIFIER = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')


def load(root=ROOT):
    path = root / 'library/index.json'
    if not path.is_file():
        raise ValueError('The lesson library is not present in this checkout.')
    return json.loads(path.read_text(encoding='utf-8'))


def safe_file(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative:
        raise ValueError('Invalid library resource path: ' + relative)
    source = root / path
    if source.is_symlink() or not source.resolve().is_relative_to(root.resolve()) or not source.is_file():
        raise ValueError('Missing or unsafe library resource: ' + relative)
    return source


def catalogue(root=ROOT, deck=None, block=None):
    data = load(root)
    if deck and block:
        raise ValueError('Select either a deck or a block.')
    key, name = ('decks', deck) if deck else ('blocks', block)
    if name:
        if key == 'decks':name=data.get('aliases',{}).get(name,name)
        if name not in data[key]:
            raise ValueError('Unknown library ' + key[:-1] + ': ' + name)
        item = dict(id=name, **data[key][name])
        slide_ids = item['slides']
        item['slide_details'] = [dict(id=s, **data['slides'][s]) for s in slide_ids]
        keys={key for sid in slide_ids for key in data['slides'][sid].get('references',[])}
        item['reference_details']={key:data['references'][key] for key in sorted(keys)}
        source_ids={origin['source'] for sid in slide_ids for origin in data['slides'][sid].get('origins',[])}
        item['source_details']=[source for source in data['sources'] if source['id'] in source_ids]
        item['command'] = ('python3 scripts/deck.py new my-talk --from ' + name if deck
                           else 'python3 scripts/deck.py add my-talk --block ' + name)
        return item
    return {kind: [dict(id=name, **{k:v for k,v in item.items() if k != 'slides'},
                       slide_count=len(item['slides'])) for name,item in data[kind].items()]
            for kind in ('decks', 'blocks')}


def tex_source(text):
    """Remove comments before inspecting the documented literal-path source format."""
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def template_calls(text):
    """Read literal template IDs, allowing nested LaTeX in the option values."""
    text = tex_source(text)
    calls = []
    for match in re.finditer(r'\\studiotemplate\b', text):
        tail = text[match.end():].lstrip()
        if tail.startswith('['):
            braces, end = 0, None
            for position, char in enumerate(tail[1:], 1):
                if char == '{': braces += 1
                elif char == '}': braces -= 1
                elif char == ']' and braces == 0:
                    end = position + 1
                    break
            if end is None:
                raise ValueError('Unclosed template options in lesson source.')
            tail = tail[end:].lstrip()
        identifier = re.match(r'\{([a-z][a-z0-9-]*)\}', tail)
        if not identifier:
            raise ValueError('Lesson sources must call a literal public template ID.')
        calls.append(identifier[1])
    return calls


def source_dependencies(root, slide, include_registered=True):
    """Follow retained literal inputs and graphics; never execute TeX or converters."""
    pending = [slide['source']]
    if include_registered: pending.extend(slide.get('resources', {}))
    if slide.get('layout_source'): pending.append(slide['layout_source'])
    found = set()
    while pending:
        relative = pending.pop()
        if relative in found: continue
        path = safe_file(root, relative)
        found.add(relative)
        if path.suffix != '.tex': continue
        text = tex_source(path.read_text(encoding='utf-8'))
        literals = set(re.findall(
            r'(?:library|images|assets|examples)/[A-Za-z0-9_./-]+\.(?:pdf|png|jpe?g|tex|csv|txt)\b', text))
        for command, name in re.findall(r'\\(input|includegraphics)(?:\[[^\]]*\])?\s*\{([^{}\\]+)\}', text):
            if '#' in name: continue  # Parameterized paths belong in resource metadata.
            if not Path(name).suffix:
                suffixes = ('.tex',) if command == 'input' else ('.pdf', '.png', '.jpg', '.jpeg')
                name = next((name+suffix for suffix in suffixes if (root/(name+suffix)).is_file()), name+suffixes[0])
            literals.add(name)
        for name in re.findall(r'\\asset(?:\[[^\]]*\])?\{([a-z0-9-]+)\}', text):
            literals.add('assets/generated/' + name + '.pdf')
        pending.extend(literals - found)
    return found


def core_dependencies(root, slide):
    if not slide.get('core_reuse'): return {}
    from studio_preview import input_sets
    entries = json.loads((root/'templates/index.json').read_text())['templates']
    entry = next((e for e in entries if e['id'] == slide['layout']), None)
    if entry is None: raise ValueError('Unknown shared Studio layout: ' + slide['layout'])
    return input_sets(root, [entry])[entry['id']]


def slide_dependencies(root, slide, data=None):
    paths = source_dependencies(root, slide)
    paths.update(key for key in core_dependencies(root, slide) if not key.startswith('@'))
    paths.update(path.name for path in root.glob('*.sty'))
    data = data if data is not None else load(root)
    paths.update(data['references'][key]['source'] for key in slide.get('references', []))
    return paths


def validate_binding(root, data, name):
    """Reject known duplicate compositions and calls that bypass their shared layout."""
    slide = data['slides'][name]
    layout = data.get('layouts', {}).get(slide['layout'], {})
    if layout.get('replaced_by'):
        raise ValueError(name + ': layout ' + slide['layout'] + ' was replaced by ' + layout['replaced_by'])
    calls = template_calls(safe_file(root, slide['source']).read_text(encoding='utf-8'))
    expected = slide.get('preset', slide['layout'])
    if calls != [expected]:
        raise ValueError(name + ': source must call the canonical template ' + expected)
    if layout.get('registration') == 'shared core' and not slide.get('core_reuse'):
        raise ValueError(name + ': shared Studio layouts require core_reuse dependency tracking.')
    if layout.get('source') and not layout.get('registration') and slide.get('layout_source') != layout['source']:
        raise ValueError(name + ': layout source differs from its canonical registration.')
    for family, rule in data.get('reuse_rules', {}).items():
        if name not in rule['slides'] and slide['layout'] != rule['layout']: continue
        if slide['layout'] != rule['layout']:
            raise ValueError(name + ': composition ' + family + ' must reuse ' + rule['layout'])
        paths = source_dependencies(root, slide, include_registered=False)
        paths.update(key for key in core_dependencies(root, slide) if not key.startswith('@'))
        missing = set(rule.get('required_dependencies', [])) - paths
        if missing:
            raise ValueError(name + ': shared components missing for ' + family + ': ' + ', '.join(sorted(missing)))


def validate(root=ROOT):
    data = load(root)
    if data.get('schema') != 1:
        raise ValueError('Unsupported lesson-library schema.')
    for name,target in data.get('aliases',{}).items():
        if not IDENTIFIER.fullmatch(name) or target not in data['decks']:
            raise ValueError('Invalid library deck alias: '+name)
    for name,preset in data.get('presets',{}).items():
        if not IDENTIFIER.fullmatch(name) or preset['slide'] not in data['slides']:
            raise ValueError('Invalid fixed-content preset: '+name)
        safe_file(root,preset['source'])
        slide=data['slides'][preset['slide']]
        if name==slide['layout'] or slide.get('preset')!=name or preset['source'] not in slide.get('resources',{}):
            raise ValueError('Invalid fixed-content binding: '+name)
    slides = data['slides']
    for family, rule in data.get('reuse_rules', {}).items():
        if rule['layout'] not in data.get('layouts', {}) or set(rule['slides']) - slides.keys():
            raise ValueError('Invalid canonical composition rule: ' + family)
    for kind in ('slides', 'blocks', 'decks'):
        for name in data[kind]:
            if not IDENTIFIER.fullmatch(name):
                raise ValueError('Invalid library identifier: ' + name)
    for name, slide in slides.items():
        validate_binding(root, data, name)
        missing = source_dependencies(root, slide) - {slide['source']} - slide.get('resources', {}).keys()
        if missing:
            raise ValueError(name + ': unregistered dependencies; run scripts/library.py sync: ' + ', '.join(sorted(missing)))
        source = safe_file(root, slide['source'])
        if not source.read_text(encoding='utf-8').strip():
            raise ValueError('Empty slide source: ' + name)
        if slide['status'] not in ('in review', 'changes requested', 'approved'):
            raise ValueError('Invalid review status: ' + name)
        for relative, expected in slide.get('resources', {}).items():
            if hashlib.sha256(safe_file(root, relative).read_bytes()).hexdigest() != expected:
                raise ValueError('Changed library resource: ' + relative)
        for key in slide.get('references', []):
            safe_file(root, data['references'][key]['source'])
    for kind in ('blocks', 'decks'):
        for name, item in data[kind].items():
            if not item['slides'] or set(item['slides']) - slides.keys():
                raise ValueError('Empty or unknown slide sequence: ' + name)
            if kind == 'blocks' and any(slides[s].get('role') in ('cover','team','contents','closing') for s in item['slides']):
                raise ValueError('A reusable content block contains presentation wrapper pages: ' + name)
    sources = {s['id']:s for s in data['sources']}
    mapped = set()
    for source in data['sources']:
        pages = source['pages']
        if len(pages) != source['page_count'] or [p['page'] for p in pages] != list(range(1, source['page_count'] + 1)):
            raise ValueError('Incomplete source-page coverage: ' + source['id'])
        for page in pages:
            if page['slide'] not in slides:
                raise ValueError('Source page points at an unknown slide.')
            mapped.add(page['slide'])
    if set(slides) - mapped:
        raise ValueError('Slides without an official source-page mapping.')
    manifest_path=root/'library/parts/manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for part in manifest['parts'].values():
            expected={part['source']:part['source_sha256'],part['pdf']:part['pdf_sha256'],**part['dependencies']}
            for name,value in expected.items():
                if hashlib.sha256(safe_file(root,name).read_bytes()).hexdigest()!=value:
                    raise ValueError('Changed retained artwork: '+name)
            source=safe_file(root,part['source'])
            for node in ET.parse(source).iter():
                for attribute,value in node.attrib.items():
                    if attribute.rsplit('}',1)[-1]!='href' or value.startswith(('#','data:')):
                        continue
                    parsed=urlsplit(value)
                    dependency=(source.parent/unquote(parsed.path)).resolve()
                    if parsed.scheme or parsed.netloc or not dependency.is_relative_to(root.resolve()):
                        raise ValueError('External retained SVG dependency: '+value)
                    relative=dependency.relative_to(root.resolve()).as_posix()
                    if relative not in part['dependencies']:
                        raise ValueError('Unlisted retained SVG dependency: '+relative)
                    safe_file(root,relative)
    return {'sources': len(sources), 'source_pages': sum(s['page_count'] for s in sources.values()),
            'slides': len(slides), 'blocks': len(data['blocks']), 'decks': len(data['decks'])}


def bundle(root, slide_ids, prefix, data=None):
    """Create a write set; validate every collision before touching a personal project."""
    data = data or load(root)
    files, layouts, citations = {}, {}, set()
    source_map = {}
    for slide_id in dict.fromkeys(slide_ids):
        slide = data['slides'][slide_id]
        validate_binding(root, data, slide_id)
        source_map[slide['source']] = prefix + '/slides/' + slide_id + '.tex'
        for relative in sorted(source_dependencies(root, slide) - {slide['source']}):
            source = safe_file(root, relative)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if source.suffix == '.tex':
                target = prefix + '/layouts/' + source.name
            else:
                target = prefix + '/assets/library-' + digest[:20] + source.suffix
            source_map[relative] = target
        if slide.get('layout_source'):
            source_map[slide['layout_source']] = prefix + '/layouts/' + Path(slide['layout_source']).name
            layouts[slide['layout']] = source_map[slide['layout_source']]
        if slide.get('preset'):
            preset=data['presets'][slide['preset']]
            layouts[slide['preset']]=source_map[preset['source']]
        citations.update(slide.get('references', []))
    for source_name, target_name in source_map.items():
        source = safe_file(root, source_name)
        if source.suffix == '.tex':
            text = source.read_text(encoding='utf-8')
            for old, new in sorted(source_map.items(), key=lambda item: -len(item[0])):
                text = text.replace(old, new)
                if old.endswith('.tex'):
                    text = text.replace(r'\input{' + old[:-4] + '}', r'\input{' + new + '}')
                elif Path(old).suffix in ('.pdf', '.png', '.jpg', '.jpeg'):
                    pattern = r'(\\includegraphics(?:\[[^\]]*\])?\s*\{)' + re.escape(str(Path(old).with_suffix(''))) + r'(\})'
                    text = re.sub(pattern, lambda match: match[1] + new + match[2], text)
            files[target_name] = text.encode('utf-8')
        else:
            files[target_name] = source.read_bytes()
    return files, layouts, citations


def definitions(layouts):
    return ''.join(r'\DeclareStudioLibraryLayout{' + name + '}{' + path + '}\n'
                   for name, path in sorted(layouts.items()))


def bibliography(root, data, citations):
    return '\n'.join(safe_file(root, data['references'][key]['source']).read_text(encoding='utf-8').strip()
                     for key in sorted(citations)) + ('\n' if citations else '')


def commit_files(project, files):
    """Roll back a failed multi-file import, including existing managed files."""
    before = {}
    written = []
    try:
        for path, value in files.items():
            if not path.resolve().is_relative_to(project.resolve()) or path.is_symlink():
                raise ValueError('Import destination escapes the presentation.')
            before[path] = path.read_bytes() if path.exists() else None
        for path, value in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
            written.append(path)
    except BaseException:
        for path in reversed(written):
            if before[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(before[path])
        raise


def create_from_library(root, name, deck_id, project):
    data = load(root)
    deck_id=data.get('aliases',{}).get(deck_id,deck_id)
    if deck_id not in data['decks']:
        raise ValueError('Unknown library deck: ' + deck_id)
    if project.exists():
        raise ValueError('Already exists: ' + str(project))
    lesson = data['decks'][deck_id]
    prefix = 'presentations/' + name
    files, layouts, citations = bundle(root, lesson['slides'], prefix, data)
    sequence=lesson['slides']
    closing=max((i for i,s in enumerate(sequence) if data['slides'][s].get('role')=='closing'),default=len(sequence))
    inputs=[r'\input{' + prefix + '/slides/' + sid + '.tex}' for sid in sequence]
    inputs.insert(closing,MARKER)
    main = '\n'.join([
        '% Personal editable copy. Content is independent of the shared lesson library.',
        r'\documentclass[aspectratio=169]{beamer}', r'\usetheme{bitpolito-studio}',
        r'\usepackage{bitpolitostudiolibrary}', r'\usepackage[backend=biber,style=numeric]{biblatex}',
        r'\addbibresource{' + prefix + '/references.bib}',
        r'\input{' + prefix + '/library-layouts.tex}', r'\begin{document}',
        *inputs,
        r'\end{document}', ''])
    brief = '# ' + lesson['title'] + '\n\n## Goal\nAdapt the supplied English lesson to the intended audience.\n\n## Audience\n' + lesson['audience'] + '\n\n## Language\nEnglish.\n\n## Duration\nSet the speaking time before presenting.\n\n## Metadata\nCheck speaker, organization and historical credits before delivery.\n\n## Sources\nCopied from library deck `' + deck_id + '`. See library-imports.json for slide provenance and references.\n\n## Outline\n' + '\n'.join('- ' + s for s in lesson['slides']) + '\n\n## Assumptions\nOriginal composition/order are retained; Inter and English text are deliberate adaptations. Read update notes and review flags before presenting.\n\n## Verification\nNot yet built or visually reviewed as a personal deck.\n'
    state = {'schema': 1, 'deck': deck_id, 'blocks': [], 'slides': list(lesson['slides']),
             'layouts': layouts, 'references': sorted(citations),
             'provenance': {s: {k:v for k,v in data['slides'][s].items() if k in ('origins','changes','editorial_updates','graphic_differences','review_notes','verification_scope','references','status','preset','content_mode')} for s in lesson['slides']}}
    files.update({prefix + '/main.tex': main.encode(), prefix + '/brief.md': brief.encode(),
                  prefix + '/references.bib': bibliography(root, data, citations).encode(),
                  prefix + '/library-layouts.tex': definitions(layouts).encode(),
                  prefix + '/library-imports.json': (json.dumps(state, indent=2) + '\n').encode()})
    project.mkdir(parents=True)
    (project / 'assets').mkdir()
    try:
        commit_files(project, {root/path:value for path,value in files.items()})
    except BaseException:
        shutil.rmtree(project)
        raise
    return project


def add_block(root, project, block_id):
    data = load(root)
    if block_id not in data['blocks']:
        raise ValueError('Unknown library block: ' + block_id)
    main_path = project / 'main.tex'
    main = main_path.read_text(encoding='utf-8')
    if main.count(MARKER) != 1:
        raise ValueError('No unique block insertion marker. Add ' + MARKER + ' before the closing page, then retry. No files were changed.')
    if r'\usetheme{bitpolito-studio}' not in main:
        raise ValueError('Lesson blocks require a Studio presentation.')
    state_path = project / 'library-imports.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {'schema':1,'blocks':[],'slides':[],'layouts':{},'references':[], 'provenance':{}}
    if block_id in state['blocks']:
        raise ValueError('This block is already imported: ' + block_id)
    sequence = data['blocks'][block_id]['slides']
    if set(sequence) & set(state['slides']):
        raise ValueError('This block repeats slides already imported; choose another block or reuse the existing local sources manually.')
    definitions_path=project/'library-layouts.tex'
    if definitions_path.exists() and definitions_path.read_text(encoding='utf-8')!=definitions(state['layouts']):
        raise ValueError('Layout registration collision: library-layouts.tex was edited. Preserve your custom declarations separately before importing.')
    prefix = project.relative_to(root).as_posix()
    files, layouts, citations = bundle(root, sequence, prefix, data)
    for path, content in list(files.items()):
        destination = root / path
        if destination.exists():
            if destination.read_bytes() != content:
                raise ValueError('Import collision: ' + path)
            del files[path]
    for name, path in layouts.items():
        if name in state['layouts'] and state['layouts'][name] != path:
            raise ValueError('Layout collision: ' + name)
    bib_path = project / 'references.bib'
    old_bib = bib_path.read_text(encoding='utf-8') if bib_path.exists() else ''
    existing_keys = set(re.findall(r'@\w+\s*[{(]\s*([^,\s]+)', old_bib))
    new_refs = citations - set(state['references'])
    if new_refs & existing_keys:
        raise ValueError('Bibliography key collision: ' + ', '.join(sorted(new_refs & existing_keys)))
    state['blocks'].append(block_id)
    state['slides'] += sequence
    state['layouts'].update(layouts)
    state['references'] = sorted(set(state['references']) | citations)
    state['provenance'].update({s:{k:v for k,v in data['slides'][s].items() if k in ('origins','changes','editorial_updates','graphic_differences','review_notes','verification_scope','references','status','preset','content_mode')} for s in sequence})
    if r'\usepackage{bitpolitostudiolibrary}' not in main:
        main = main.replace(r'\begin{document}', r'\usepackage{bitpolitostudiolibrary}' + '\n' + r'\input{' + prefix + '/library-layouts.tex}\n' + r'\begin{document}', 1)
    insert = '\n'.join(r'\input{' + prefix + '/slides/' + s + '.tex}' for s in sequence)
    main = main.replace(MARKER, insert + '\n' + MARKER)
    if new_refs and not re.search(r'(?m)^[^%\n]*\\addbibresource', main):
        if not re.search(r'(?m)^[^%\n]*\\usepackage[^\n]*\{biblatex\}', main):
            main = main.replace(r'\begin{document}', r'\usepackage[backend=biber,style=numeric]{biblatex}' + '\n' + r'\begin{document}', 1)
        main = main.replace(r'\begin{document}', r'\addbibresource{' + prefix + '/references.bib}\n' + r'\begin{document}', 1)
    files.update({prefix + '/main.tex':main.encode(), prefix + '/library-layouts.tex':definitions(state['layouts']).encode(),
                  prefix + '/references.bib':(old_bib + '\n' + bibliography(root,data,new_refs)).encode(),
                  prefix + '/library-imports.json':(json.dumps(state,indent=2)+'\n').encode()})
    commit_files(project,{root/path:value for path,value in files.items()})
    return len(sequence)
