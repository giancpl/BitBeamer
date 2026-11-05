"""Create, build and inspect private presentations without changing the library."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import build
from studio_models import load_models
from studio_preview import thumbnail

ROOT = Path(__file__).resolve().parents[1]
RESERVED = {'con', 'prn', 'aux', 'nul', *(f'{p}{i}' for p in ('com', 'lpt') for i in range(1, 10))}
PLACEHOLDERS = re.compile(r'\b(?:Your (?:presentation|name|institute)|Presentation title|Author name|Department or organization|Slide title|Your content|(?:First|Second|Third) concept|Supporting explanation|Label [0-9]+|Value [0-9]+|TODO|TBD)\b', re.I)


def validate_name(name):
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', name) or name in RESERVED:
        raise ValueError('Use a portable lowercase kebab-case name, such as my-talk (no paths or reserved device names).')
    return name


def project_path(root, name, existing=True):
    validate_name(name)
    namespace = root / 'presentations'
    project = namespace / name
    if namespace.is_symlink() or project.is_symlink() or not project.resolve().is_relative_to(root.resolve()):
        raise ValueError('Presentation folders must remain inside this checkout; symlink projects are not supported.')
    if existing and not (project / 'main.tex').is_file():
        raise ValueError(f'Presentation not found: {name}. Run scripts/deck.py new {name} first.')
    return project


def create_deck(root, name, style='studio', from_library=None):
    project = project_path(root, name, existing=False)
    if project.exists():
        raise ValueError(f'Already exists: {project}. Choose another name; existing projects are never overwritten.')
    if from_library:
        if style != 'studio':
            raise ValueError('--from requires Studio; Academic remains a separate workflow.')
        from lesson_library import create_from_library
        return create_from_library(root, name, from_library, project)
    source = (root / f'start-{style}.tex').read_text(encoding='utf-8')
    prefix = f'presentations/{name}'
    setup = ('% Paths are relative to the repository root, where compilation runs.\n'
             + r'\graphicspath{{' + prefix + '/assets/}}\n'
             + '% For local sections: \\input{' + prefix + '/sections/introduction.tex}\n'
             + '% Uncomment both lines when using citations; add real sources to references.bib.\n'
             + '% \\usepackage[backend=biber,style=numeric]{biblatex}\n'
             + '% \\addbibresource{' + prefix + '/references.bib}\n\n')
    source = source.replace(r'\begin{document}', setup + r'\begin{document}', 1)
    if style == 'studio':
        from lesson_library import MARKER
        source = source.replace(r'\closingframe', MARKER + '\n' + r'\closingframe', 1)
    brief = f'''# {name}

## Goal
TODO: describe the outcome the audience should take away.

## Audience
TODO: describe prior knowledge and interests.

## Duration
TODO: state the speaking time or approximate slide count.

## Language
English, unless explicitly requested otherwise.

## Metadata
TODO: provide the presentation title, real author and organization.

## Sources
List supplied files, verified references and any claims needing verification.
Do not invent statistics, names, results or citations.

## Outline
Cover → team introduction → contents → content → closing.
Adapt or omit the team page if it does not fit the brief. Check its example figures.

## Assumptions
Record reasonable decisions and identify illustrative data explicitly.

## Verification
Not yet built or visually reviewed. Record the final check report and inspection of every page here.
'''
    project.mkdir(parents=True)
    (project / 'assets').mkdir()
    (project / 'main.tex').write_text(source, encoding='utf-8')
    (project / 'brief.md').write_text(brief, encoding='utf-8')
    (project / 'references.bib').write_text('% Add verified bibliographic entries for this presentation only.\n', encoding='utf-8')
    print(f'Created {prefix}/main.tex ({style}). Complete brief.md and replace the example content.')
    return project


def layout_catalogue(root, all_models=False, model_id=None):
    data = load_models(root)
    featured = {s['model']: s for s in data['selection']}
    models = {m['id']: m for m in data['models']}
    if model_id and model_id not in models:
        raise ValueError(f'Unknown model: {model_id}. Use layouts --all for available model IDs.')
    chosen = [models[model_id]] if model_id else (list(models.values()) if all_models else [models[s['model']] for s in data['selection']])
    entries = {e['id']: e for e in json.loads((root / 'templates/index.json').read_text(encoding='utf-8'))['templates']}
    result = []
    for model in chosen:
        item = {k: model[k] for k in ('id', 'title', 'category', 'default_variant')}
        item['featured'] = model['id'] in featured
        item['guide'] = f'docs/templates/models/{model["id"]}.md'
        item['variants'] = []
        for variant in model['variants']:
            v = {'id': variant['id'], 'default_source': variant['default_source'], 'choices': []}
            for composition in variant['compositions']:
                choice = {'composition': composition['id'], 'palettes': composition['palettes'], 'default_palette': composition['native_palette']}
                if model_id:
                    entry = entries[composition['id']]
                    inverse = {target: semantic for semantic, target in composition['fields'].items()}
                    choice['fields'] = [dict(field, semantic_name=inverse.get(field['name'], field['name'])) for field in entry['fields']]
                    choice['options'] = entry.get('options', {})
                    choice['source'] = entry['source']
                    choice['guide'] = f'docs/templates/guides/{composition["id"]}.md'
                    choice['example'] = r'\studiotemplate[variant=' + variant['id'] + ',palette=' + composition['native_palette'] + ']{' + model['id'] + '}'
                v['choices'].append(choice)
            item['variants'].append(v)
        if item['featured']:
            item['selected'] = featured[model['id']]
        result.append(item)
    return result


def output_path(root, name):
    output = root / 'build' / 'presentations' / validate_name(name)
    if not output.resolve().is_relative_to((root / 'build').resolve()) or any(p.is_symlink() for p in (root / 'build', root / 'build/presentations', output)):
        raise ValueError('Presentation output must be a local build directory, not a symlink.')
    return output


def build_deck(root, name, backend='docker', image='bitbeamer-latex:local', open_pdf=False, force=False):
    project = project_path(root, name)
    output = output_path(root, name)
    args = [str(project / 'main.tex'), str(output), '--backend', backend, '--image', image]
    if open_pdf:
        args.append('--open')
    if force:
        args.append('--force')
    return build.main(args, root=root)


def log_issues(text):
    """Inspect the final TeX log, not transient warnings from earlier latexmk passes."""
    errors = []
    patterns = [
        ('overflow', r'Overfull \\[hv]box[^\n]*'),
        ('layout overflow', r'[^\n]*(?:Text|Graphic|Field|Content)\s+overflow[^\n]*'),
        ('missing glyph', r'Missing character:[^\n]*'),
        ('unresolved citation', r'(?:LaTeX|Package [^\n]+) Warning:[^\n]*Citation[^\n]*undefined[^\n]*'),
        ('unresolved reference', r'(?:LaTeX|Package [^\n]+) Warning:[^\n]*(?:Reference[^\n]*undefined|(?:undefined|unresolved) (?:references|citations))[^\n]*'),
        ('bibliography rerun', r'[^\n]*(?:Please \(re\)run Biber|Please rerun LaTeX|Rerun to get cross-references right)[^\n]*'),
        ('TeX error', r'^!\s*[^\n]+'),
    ]
    for kind, pattern in patterns:
        for match in re.finditer(pattern,text,re.I|re.M):
            message=match.group(0).strip()
            if kind in ('overflow','layout overflow'):
                fields=list(re.finditer(r'STUDIO-FIELD: ([^\n]+)',text[:match.start()]))
                if fields:message+=' ['+fields[-1][1].strip()+']'
            errors.append({'kind':kind,'message':message})
    return errors


def personal_sources(root, project):
    """Follow literal inputs only within this deck; never inspect another personal project."""
    pending = [project / 'main.tex']
    visited = set()
    while pending:
        source = pending.pop().resolve()
        if source in visited or not source.is_relative_to(project.resolve()) or not source.is_file():
            continue
        visited.add(source)
        text = re.sub(r'(?<!\\)%[^\n]*', '', source.read_text(encoding='utf-8'))
        yield source, text
        for name in re.findall(r'\\(?:input|include)\s*\{([^{}\\#\n]+)\}', text):
            path = Path(name)
            if not path.suffix:
                path = path.with_suffix('.tex')
            pending.append(root / path)  # TeX runs from the checkout root.


def pdf_tool(root, name, pdf, backend, image):
    if shutil.which(name):
        command = [shutil.which(name), str(pdf)]
    elif backend == 'docker':
        docker = build.docker_image(root, image)
        command = [docker, 'run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp',
                   '--mount', f'type=bind,source={pdf.parent.resolve()},target=/input,readonly',
                   '--entrypoint', name, image, '/input/' + pdf.name]
    else:
        raise RuntimeError(f'{name} is missing. Install Poppler (poppler-utils / brew install poppler / conda install -c conda-forge poppler), or use --backend docker.')
    if name == 'pdftotext':command.append('-')
    return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout


def check_deck(root, name, backend='docker', image='bitbeamer-latex:local', preview=False, force=False):
    project = project_path(root, name)
    output = output_path(root, name)
    output.mkdir(parents=True, exist_ok=True)
    report = {'deck': name, 'backend': backend, 'source': str(project / 'main.tex'),
              'pdf': str(output / 'main.pdf'), 'errors': [], 'warnings': [],
              'preview': [], 'visual_review': 'not performed; inspect every rendered page before delivery'}
    status = build_deck(root, name, backend, image, force=force)
    if status:
        report['errors'].append({'kind': 'compilation', 'message': 'Build failed; any previous PDF or preview is stale.'})
    else:
        log = output / 'main.log'
        if not log.is_file():
            report['errors'].append({'kind': 'log', 'message': 'Final TeX log not found.'})
        else:
            report['errors'].extend(log_issues(log.read_text(encoding='utf-8', errors='replace')))
        for source, text in personal_sources(root, project):
            for number, line in enumerate(text.splitlines(), 1):
                matches = sorted(set(m.group(0) for m in PLACEHOLDERS.finditer(line)))
                if matches:
                    report['warnings'].append(f'{source.relative_to(root)}:{number}: placeholder: {", ".join(matches)}')
        if r'\studioteamframe' in (project / 'main.tex').read_text(encoding='utf-8'):
            report['warnings'].append('Team page included: confirm its figures, labels and artwork against the brief; built-in figures are example content.')
        pdf = output / 'main.pdf'
        if not pdf.is_file():
            report['errors'].append({'kind': 'PDF', 'message': 'The compiler produced no PDF.'})
        else:
            try:
                info = pdf_tool(root, 'pdfinfo', pdf, backend, image)
                match = re.search(r'^Pages:\s*(\d+)', info, re.M)
                if not match:
                    raise RuntimeError('Cannot read the PDF page count.')
                report['pages'] = int(match[1])
                fonts = pdf_tool(root, 'pdffonts', pdf, backend, image)
                for line in fonts.splitlines()[2:]:
                    if re.search(r'\sno\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$', line):
                        report['errors'].append({'kind': 'font embedding', 'message': line.strip()})
                if preview:
                    target = output / 'preview'
                    target.mkdir(exist_ok=True)
                    with tempfile.TemporaryDirectory(prefix='pages-', dir=output) as temporary:
                        for page in range(1, report['pages'] + 1):
                            filename = f'page-{page:03d}.png'
                            thumbnail(root, pdf, Path(temporary) / filename, backend, image, page, width=1600)
                        for old in target.glob('page-*.png'):
                            if re.fullmatch(r'page-\d+\.png', old.name):
                                old.unlink()
                        for prepared in sorted(Path(temporary).glob('page-*.png')):
                            destination = target / prepared.name
                            prepared.replace(destination)
                            report['preview'].append(destination.relative_to(root).as_posix())
            except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
                # PDF inspection is optional without --preview; compilation still works without Poppler.
                bucket = 'errors' if preview else 'warnings'
                issue = {'kind': 'PDF inspection', 'message': str(error)} if preview else str(error)
                report[bucket].append(issue)
    report['technical_status'] = 'failed' if report['errors'] else 'passed'
    (output / 'check.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for error in report['errors']:
        print(f'ERROR [{error["kind"]}]: {error["message"]}', file=sys.stderr)
    for warning in report['warnings']:
        print(f'WARNING: {warning}')
    print(f'Checks: {report["technical_status"]}; {len(report["warnings"])} warning(s). Report: {output / "check.json"}')
    return 1 if report['errors'] else 0


def main(argv=None, root=None):
    root = (root or ROOT).resolve()
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    layouts = commands.add_parser('layouts', help='Discover existing Studio models without compiling')
    layouts.add_argument('--all', action='store_true')
    layouts.add_argument('--model')
    layouts.add_argument('--json', action='store_true')
    new = commands.add_parser('new', help='Create an ignored personal project from an editable starter')
    new.add_argument('name')
    new.add_argument('--from', dest='from_library', help='Copy a complete ready-content Studio lesson')
    new.add_argument('--style', choices=('studio', 'academic'), default='studio')
    library = commands.add_parser('library', help='Find complete lessons and reusable topic blocks')
    selection = library.add_mutually_exclusive_group()
    selection.add_argument('--deck')
    selection.add_argument('--block')
    library.add_argument('--json', action='store_true')
    add = commands.add_parser('add', help='Copy a reusable topic block into a personal Studio project')
    add.add_argument('name')
    add.add_argument('--block', required=True)
    for name in ('build', 'check'):
        command = commands.add_parser(name)
        command.add_argument('name')
        command.add_argument('--backend', choices=('docker', 'native'), default='docker')
        command.add_argument('--image', default=os.environ.get('LATEX_IMAGE', 'bitbeamer-latex:local'))
        command.add_argument('--force', action='store_true')
        if name == 'build':
            command.add_argument('--open', action='store_true')
        else:
            command.add_argument('--preview', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'layouts' and args.model and (args.model.startswith('official-layout-') or ((root/'library/index.json').is_file() and args.model not in {m['id'] for m in load_models(root)['models']})):
            from lesson_library import load
            collection=load(root)
            lesson=collection['layouts'].get(args.model) or collection.get('presets',{}).get(args.model)
            if lesson is None:raise ValueError('Unknown lesson layout: '+args.model)
            print(json.dumps(dict(id=args.model,**lesson),indent=2))
            return 0
        if args.command == 'layouts':
            data = layout_catalogue(root, args.all, args.model)
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                for model in data:
                    print(f'{model["id"]}: {model["title"]} ({model["category"]}) — {model["guide"]}')
                    for variant in model['variants']:
                        palettes = sorted({p for c in variant['choices'] for p in c['palettes']})
                        print(f'  variant={variant["id"]}; palette={"|".join(palettes)}')
                        if args.model:
                            for choice in variant['choices']:
                                print('    ' + choice['example'])
                                for field in choice['fields']:
                                    print(f'    {field["semantic_name"]} [{field["type"]}]: {field.get("default", "")}')
                                if choice['options']:
                                    print('    options: ' + json.dumps(choice['options']))
            return 0
        if args.command == 'library':
            from lesson_library import catalogue
            result = catalogue(root, args.deck, args.block)
            if args.json:
                print(json.dumps(result, indent=2))
            elif args.deck or args.block:
                print(json.dumps(result, indent=2))
            else:
                for kind in ('decks', 'blocks'):
                    print(kind.upper())
                    for item in result[kind]:
                        print(f'  {item["id"]}: {item["title"]} ({item["slide_count"]} slides; {item["status"]})')
            return 0
        if args.command == 'add':
            from lesson_library import add_block
            count = add_block(root, project_path(root, args.name), args.block)
            print(f'Imported {count} slides into {args.name}; inspect and adapt the personal copies.')
            return 0
        if args.command == 'new':
            create_deck(root, args.name, args.style, args.from_library)
            return 0
        if args.command == 'build':
            return build_deck(root, args.name, args.backend, args.image, args.open, args.force)
        return check_deck(root, args.name, args.backend, args.image, args.preview, args.force)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Deck failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
