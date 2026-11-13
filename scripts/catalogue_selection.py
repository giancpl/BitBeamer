"""Track human selection of original Studio candidates separately from graphical approval."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from asset_library import write_if_changed

ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'templates/catalogue-selection.json'
REPORT = 'docs/CATALOGUE-REVIEW.md'
DECISIONS = {'pending', 'keep', 'merge', 'preset', 'discard', 'exclude'}
PHASES = ['Texts and statements', 'Comparisons and callouts', 'Images and resources',
          'Data and charts', 'General diagrams', 'Technical compositions',
          'Contacts and closing', 'Resources and unclassified originals']


def read(root, name):
    return json.loads((root / name).read_text(encoding='utf-8'))


def family_phase(family, slide_format='slide'):
    if slide_format != 'slide':
        return PHASES[-1]
    return {'Opening': PHASES[0], 'Statements': PHASES[0], 'Comparisons': PHASES[1],
            'Cards': PHASES[1], 'Lists': PHASES[1], 'Images': PHASES[2],
            'Data': PHASES[3], 'Diagrams': PHASES[4], 'Technical': PHASES[5],
            'Closing': PHASES[6]}.get(family, PHASES[-1])


def expected_records(root):
    inventory = read(root, 'templates/figma-inventory.json')
    entries = read(root, 'templates/index.json')['templates']
    reviews = read(root, 'templates/review.json')['templates']
    by_id = {e['id']: e for e in entries}
    direct, duplicate_groups = defaultdict(list), defaultdict(list)
    for entry in entries:
        for reference in entry.get('references', []):
            direct[reference].append(entry['id'])
    for frame in inventory['frames']:
        duplicate_groups[frame['sha256']].append(frame['id'])
    records = {}
    for frame in inventory['frames']:
        group = duplicate_groups[frame['sha256']]
        canonical = sorted({name for member in group for name in direct[member]})
        suggestion = frame.get('assignment', {}).get('template')
        proposed = sorted(set(canonical + ([suggestion] if suggestion in by_id else [])))
        family = by_id[proposed[0]]['category'] if proposed else 'Needs classification'
        approved = [n for n in canonical if reviews[n]['status'] == 'approved']
        excluded = 'glow-statement' in canonical and not approved
        decision = 'keep' if approved else 'exclude' if excluded else 'pending'
        records[frame['id']] = {
            'file': frame['file'], 'sha256': frame['sha256'],
            'representative': min(group), 'format': frame['format'],
            'family_proposal': family, 'phase': family_phase(family, frame['format']),
            'canonical_compositions': canonical, 'suggested_compositions': proposed,
            'decision': decision, 'targets': approved if approved else canonical if excluded else [],
            'basis': 'existing graphical approval' if approved else 'edition exclusion' if excluded else 'awaiting user selection',
            'reason': ('Retain the existing explicit graphical approval; exact source duplicates share this decision.' if approved else
                       'Unresolved gradient excluded from this edition by the user; source and graphical review history are retained.' if excluded else '')}
    return records


def synchronize(root=ROOT):
    inventory = read(root, 'templates/figma-inventory.json')
    index = read(root, 'templates/index.json')
    counts = inventory.setdefault('counts', {})
    counts.update(canonical_models=len(index['templates']),
                  grouped_models=len(read(root, 'templates/models.json')['models']),
                  compatibility_aliases=len(index.get('aliases', [])),
                  templates=len(index['templates']) + len(index.get('aliases', [])))
    write_if_changed(root/'templates/figma-inventory.json',
                     (json.dumps(inventory, ensure_ascii=False, indent=2) + '\n').encode())
    path = root / LEDGER
    old = read(root, LEDGER) if path.exists() else {}
    records = expected_records(root)
    if set(old.get('sources', {})) - records.keys():
        raise ValueError('Originals disappeared from the inventory; reconcile their decisions explicitly.')
    for name, previous in old.get('sources', {}).items():
        if previous['sha256'] != records[name]['sha256']:
            raise ValueError('Original changed after selection: ' + name)
        # New graphical approvals do not override an explicit human exclusion.
        if previous['basis'] == 'user decision' or previous['decision'] != 'pending':
            for field in ('decision', 'targets', 'basis', 'reason'):
                records[name][field] = previous[field]
    reviews = read(root, 'templates/review.json')['templates']
    compositions = {}
    for entry in read(root, 'templates/index.json')['templates']:
        name = entry['id']
        approved = reviews[name]['status'] == 'approved'
        excluded = name == 'glow-statement' and not approved
        record = {'decision': 'keep' if approved else 'exclude' if excluded else 'pending',
                  'targets': [name] if approved else [],
                  'basis': 'existing graphical approval' if approved else 'edition exclusion' if excluded else 'awaiting user selection',
                  'reason': 'Existing explicit graphical approval is preserved.' if approved else
                            'Unresolved gradient excluded from this edition by the user.' if excluded else ''}
        previous = old.get('compositions', {}).get(name)
        if previous and (previous['basis'] == 'user decision' or previous['decision'] != 'pending'):
            record = previous
        compositions[name] = record
    retired = dict(old.get('retired_compositions', {}))
    retired.update({n: r for n, r in old.get('compositions', {}).items() if n not in compositions})
    data = {'schema': 1, 'policy': {
        'scope': 'Current catalogue and all supplied original exports; no full lesson editorial review.',
        'selection': 'Compact catalogue; each distinct candidate is selected with the user before reconstruction.',
        'approved_designs': 'Preserve existing approvals, including deferred card-shadow polish.',
        'unresolved_designs': 'Exclude unapproved unresolved designs from the final edition.',
        'delivery': 'Validated lightweight core plus optional family packages; no release publication.',
        'phase_order': PHASES},
        'sources': records, 'compositions': compositions, 'retired_compositions': retired,
        'composition_exclusions': old.get('composition_exclusions', {'glow-statement': 'Unresolved gradient; excluded from this edition by explicit user instruction.'}),
        'candidate_batches': old.get('candidate_batches', []),
        'active_candidate_batch': old.get('active_candidate_batch', None)}
    write_if_changed(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())
    write_report(root, data)
    return data


def load(root=ROOT):
    return read(root, LEDGER)


def summary(root, data):
    index = read(root, 'templates/index.json')
    reviews = read(root, 'templates/review.json')['templates']
    return {'exports': len(data['sources']),
            'distinct_source_groups': len({s['sha256'] for s in data['sources'].values()}),
            'models': len(read(root, 'templates/models.json')['models']),
            'compositions': len(index['templates']), 'aliases': len(index.get('aliases', [])),
            'graphical_statuses': dict(Counter(r['status'] for r in reviews.values())),
            'composition_decisions': dict(Counter(c['decision'] for c in data['compositions'].values())),
            'source_decisions': dict(Counter(s['decision'] for s in data['sources'].values())),
            'distinct_group_decisions': dict(Counter(s['decision'] for name, s in data['sources'].items() if name == s['representative']))}


def original_path(root, record):
    folder = (root / 'design-references/figma/exports').resolve()
    source = (folder / record['file']).resolve()
    if not source.is_relative_to(folder):
        raise ValueError('Changed or unsafe original: ' + record['file'])
    return source


def check(root=ROOT, complete=False, sources=False):
    data = load(root)
    expected = expected_records(root)
    if data.get('schema') != 1 or set(data['sources']) != set(expected):
        raise ValueError('Selection ledger must cover every original exactly once; run catalogue_selection.py sync.')
    entries = {e['id']: e for e in read(root, 'templates/index.json')['templates']}
    reviews = read(root, 'templates/review.json')['templates']
    if set(data.get('compositions', {})) != set(entries):
        raise ValueError('Selection ledger must cover every current composition; run catalogue_selection.py sync.')
    for name, record in {**data.get('retired_compositions', {}), **data['compositions']}.items():
        if record['decision'] not in DECISIONS or any(not re.fullmatch(r'[a-z][a-z0-9-]*', target) for target in record['targets']) or (record['decision'] != 'pending' and not record['reason'].strip()):
            raise ValueError('Invalid composition decision: ' + name)
        if complete and record['decision'] == 'pending':
            raise ValueError('Composition selection is incomplete: ' + name)
        if complete and record['decision'] in {'keep', 'merge', 'preset'}:
            if not record['targets']:
                raise ValueError('Retained composition needs a target: ' + name)
            for target in record['targets']:
                if target not in entries or reviews[target]['status'] != 'approved':
                    raise ValueError('Selected composition needs explicit graphical approval: ' + target)
                if target in data['composition_exclusions']:
                    raise ValueError('Selected target is excluded: ' + target)
                for palette in entries[target].get('palettes', []):
                    if reviews[target].get('palette_reviews', {}).get(palette, {}).get('status') != 'approved':
                        raise ValueError('Selected palette needs explicit graphical approval: ' + target + '/' + palette)
    grouped = {}
    checked = set()
    for name, record in data['sources'].items():
        for field in ('file', 'sha256', 'representative', 'format', 'canonical_compositions', 'suggested_compositions', 'family_proposal', 'phase'):
            if record[field] != expected[name][field]:
                raise ValueError('Stale source selection metadata: ' + name + '/' + field)
        if record['decision'] not in DECISIONS or record['basis'] not in {'user decision', 'existing graphical approval', 'edition exclusion', 'awaiting user selection'}:
            raise ValueError('Invalid source selection: ' + name)
        if record['decision'] != 'pending' and not record['reason'].strip():
            raise ValueError('A final source decision needs a reason: ' + name)
        if record['decision'] in {'keep', 'merge', 'preset'} and not record['targets']:
            raise ValueError('Retained sources need a target composition: ' + name)
        if any(not re.fullmatch(r'[a-z][a-z0-9-]*', target) for target in record['targets']):
            raise ValueError('Invalid selection target: ' + name)
        value = (record['decision'], record['targets'], record['basis'], record['reason'])
        if record['sha256'] in grouped and grouped[record['sha256']] != value:
            raise ValueError('Exact source duplicates have conflicting decisions: ' + name)
        grouped[record['sha256']] = value
        if sources and record['file'] not in checked:
            source = original_path(root, record)
            if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
                raise ValueError('Changed or unsafe original: ' + name)
            checked.add(record['file'])
        if complete and record['decision'] == 'pending':
            raise ValueError('Selection is incomplete: ' + name)
        if complete and record['decision'] in {'keep', 'merge', 'preset'}:
            for target in record['targets']:
                if target not in entries or reviews[target]['status'] != 'approved':
                    raise ValueError('Selected composition needs explicit graphical approval: ' + target)
                if target in data['composition_exclusions']:
                    raise ValueError('Selected target is excluded: ' + target)
                for palette in entries[target].get('palettes', []):
                    if reviews[target].get('palette_reviews', {}).get(palette, {}).get('status') != 'approved':
                        raise ValueError('Selected palette needs explicit graphical approval: ' + target + '/' + palette)
    if set(data['composition_exclusions']) - (entries.keys() | data.get('retired_compositions', {}).keys()):
        raise ValueError('Unknown excluded composition')
    batch_ids = set()
    for batch in data['candidate_batches']:
        names = batch['candidates']
        if batch['id'] in batch_ids or not re.fullmatch(r'[a-z][a-z0-9-]*', batch['id']):
            raise ValueError('Invalid or duplicate candidate batch')
        batch_ids.add(batch['id'])
        if not 1 <= len(names) <= 5 or len(set(names)) != len(names) or set(names) - data['sources'].keys():
            raise ValueError('Candidate batches need one to five distinct known originals')
        if len({data['sources'][n]['sha256'] for n in names}) != len(names):
            raise ValueError('Show each exact source group only once')
        if not batch.get('family') or set(batch.get('proposals', {})) != set(names):
            raise ValueError('Candidate batches need a category and a proposal for each original')
    if data['active_candidate_batch'] is not None and data['active_candidate_batch'] not in batch_ids:
        raise ValueError('Unknown active candidate batch')
    if (root / REPORT).read_text(encoding='utf-8') != report(root, data):
        raise ValueError('Stale catalogue progress report; run catalogue_selection.py sync.')
    result = summary(root, data)
    counts = read(root, 'templates/figma-inventory.json').get('counts', {})
    for name, expected in {'canonical_models': result['compositions'], 'grouped_models': result['models'],
                           'compatibility_aliases': result['aliases'],
                           'templates': result['compositions'] + result['aliases']}.items():
        if counts.get(name) != expected:
            raise ValueError('Stale catalogue inventory count: ' + name)
    return result


def decide(root, names, decision, targets, reason, compositions=False):
    if any(not re.fullmatch(r'[a-z][a-z0-9-]*', target) for target in targets):
        raise ValueError('Invalid selection target')
    if decision not in DECISIONS - {'pending'} or not reason.strip():
        raise ValueError('A selection decision needs an explicit outcome and reason')
    data = load(root)
    section = 'compositions' if compositions else 'sources'
    if set(names) - data[section].keys():
        raise ValueError('Unknown original selection')
    hashes = {data['sources'][n]['sha256'] for n in names} if not compositions else set()
    for name, record in data[section].items():
        if (compositions and name in names) or (not compositions and record['sha256'] in hashes):
            record.update(decision=decision, targets=targets, reason=reason, basis='user decision')
            if compositions and decision in {'exclude', 'discard'}:
                data['composition_exclusions'][name] = reason
            elif compositions:
                data['composition_exclusions'].pop(name, None)
    if decision in {'keep', 'merge', 'preset'} and not targets:
        raise ValueError('Retained candidates need target composition IDs')
    write_if_changed(root / LEDGER, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())
    write_report(root, data)
    # Selection does not touch templates/review.json or grant graphical approval.


def active_batch(root):
    if not (root / LEDGER).exists():
        return None
    data = load(root)
    return next((b for b in data['candidate_batches'] if b['id'] == data['active_candidate_batch']), None)


def render_candidates(root=ROOT):
    import pymupdf as fitz
    from asset_library import render_svg
    batch = active_batch(root)
    if not batch:
        raise ValueError('No active original selection batch')
    data = load(root)
    names = [n for n in batch['candidates'] if data['sources'][n]['decision'] == 'pending']
    if not names:
        raise ValueError('All active originals have a selection decision; proceed to design or select the next batch')
    folder = root / 'build/review/batches' / batch['id']
    folder.mkdir(parents=True, exist_ok=True)
    commands = {}
    from studio_models import membership
    from studio_guides import command
    members = membership(root)
    temporary = folder / 'candidates.tmp.pdf'
    with fitz.open() as output:
        for number, name in enumerate(names, 1):
            record = data['sources'][name]
            source = original_path(root, record)
            if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
                raise ValueError('Changed original: ' + name)
            prepared = folder / (name + '.pdf')
            render_svg(source, prepared, crop=False)
            page = output.new_page(width=1400, height=980)
            page.insert_text((25,30), f'{number}/{len(names)} | SELECTION | {batch["family"]} | {name}', fontsize=16)
            page.insert_text((25,53), record['file'], fontsize=10)
            with fitz.open(prepared) as original:
                page.show_pdf_page(fitz.Rect(25,75,1375,835), original, 0)
            page.insert_textbox(fitz.Rect(25,850,1375,888), 'Proposal: ' + batch['proposals'][name], fontsize=12)
            duplicates = [n for n, r in data['sources'].items() if r['sha256'] == record['sha256']]
            page.insert_text((25,905), 'Exact source group: ' + ', '.join(duplicates), fontsize=9)
            existing = record['canonical_compositions']
            if existing and existing[0] in members:
                model, variant, composition = members[existing[0]]
                invocation = command(model['id'], {'variant': variant['id'], 'palette': composition['native_palette']})
                commands[name] = invocation
                page.insert_text((25,930), 'Existing API (not yet selected): ' + ' '.join(invocation.split()), fontsize=9, fontname='cour')
            else:
                page.insert_text((25,930), 'No public command yet: selection and design must precede reconstruction.', fontsize=10)
        output.set_metadata({'title': batch['title'] + ' - original candidates, no approval inferred'})
        output.save(temporary, garbage=4, deflate=True)
    target = folder / 'candidates.pdf'
    temporary.replace(target)
    # One stable editor tab for either selection or reconstruction, never both.
    write_if_changed(root / 'build/review/batches/comparisons.pdf', target.read_bytes())
    (folder / 'report.json').write_text(json.dumps({'stage': 'selection', 'batch': batch['id'], 'candidates': names,
        'family': batch['family'], 'commands': commands, 'approval': 'none inferred'}, indent=2) + '\n')
    return root / 'build/review/batches/comparisons.pdf'


def report(root, data):
    counts = summary(root, data)
    lines = ['<!-- Generated by scripts/catalogue_selection.py sync; decisions live in templates/catalogue-selection.json. -->',
        '# Studio catalogue completion', '',
        'Human selection is separate from graphical approval. Original similarity assignments remain proposals.', '',
        f'Current catalogue: **{counts["models"]} models / {counts["compositions"]} compositions**; '
        f'**{counts["graphical_statuses"].get("approved",0)} compositions graphically approved**.',
        f'Original coverage: **{counts["exports"]} exports / {counts["distinct_source_groups"]} exact-source groups**.', '',
        '## Source selection progress', '', '| Decision | Exports | Distinct source groups |', '| --- | ---: | ---: |']
    for decision in sorted(DECISIONS):
        lines.append(f'| {decision} | {counts["source_decisions"].get(decision,0)} | {counts["distinct_group_decisions"].get(decision,0)} |')
    lines += ['', 'Composition decisions: ' + ', '.join(f'{k}: {v}' for k, v in sorted(counts['composition_decisions'].items())) + '.', '', '## Ordered work', '', *[f'{i}. {phase}' for i, phase in enumerate(PHASES,1)], '',
        'Every family follows selection → design → reconstruction → original comparison → explicit approval.',
        'Review at most five distinct original candidates together. Show exact duplicates once with their IDs.',
        'Preserve approved designs; reopen only those visibly changed by a shared correction.', '',
        '## Excluded from this edition', '']
    lines += ['- `' + name + '`: ' + reason for name, reason in data['composition_exclusions'].items()]
    lines += ['', 'Excluded implementations remain in the maintenance archive for provenance and existing consumers;',
        'they must not enter the final usable selection or its packages. No graphical approval is revoked by selection.', '',
        '## Current original selection', '']
    batch = next((b for b in data['candidate_batches'] if b['id'] == data['active_candidate_batch']), None)
    if batch:
        lines += [f'**{batch["title"]} — {batch["family"]}**', '', '| Original | Current composition | Proposal |', '| --- | --- | --- |']
        for name in batch['candidates']:
            lines.append('| ' + name + ' | ' + ', '.join(data['sources'][name]['canonical_compositions']) + ' | ' + batch['proposals'][name] + ' |')
    else:
        lines += ['No original selection batch is active.']
    active = read(root, 'templates/review.json').get('active_review_batches', [])
    if active:
        batches = {b['id']: b for b in read(root, 'templates/review.json').get('review_batches', [])}
        lines += ['', '## Current reconstruction review', '']
        for name in active:
            batch = batches[name]
            lines += ['- ' + batch['title'] + ' (' + batch['family'] + '): ' + ', '.join('`'+c+'`' for c in batch['compositions']) + '. Graphical approval pending.']
    lines += ['', '## Maintainer commands', '', '```sh',
        'python3 scripts/catalogue_selection.py sync', 'python3 scripts/catalogue_selection.py check',
        'python3 scripts/catalogue_selection.py check --sources',
        'python3 scripts/review_batch.py all --compare --open',
        'python3 scripts/catalogue_selection.py check --complete', '```', '',
        '`check` is read-only. `--sources` verifies local SVG hashes; originals are optional outside maintenance.',
        '`--complete` rejects pending source decisions, missing targets and targets/palettes without explicit approval.',
        'Use `decide --ids ... --decision keep|merge|preset|discard|exclude --targets ... --reason ...` only to record an actual user decision.',
        'It updates exact duplicates together and never modifies graphical approvals.',
        'Use `--compositions` instead of `--ids` to record the selection of an existing composition, including supplementary layouts without an original.', '',
        '## Delivery gates', '',
        '- Resolve every original source group and every selected composition, including supplementary entries without an original.',
        '- Rebuild affected lesson consumers, long-copy and replacement examples; keep fonts fixed and test overflow.',
        '- Validate the lightweight core and optional family packages independently with pdfLaTeX and the existing size limits.',
        '- Run the complete test suite, catalogue/library/guide checks and verify green CI on the final commit.',
        '- Commit/push approved family checkpoints; no stable release tag or publication is implicit.', '',
        '**Completion remains pending until the human decisions and all delivery gates are satisfied.**', '']
    return '\n'.join(lines)


def write_report(root, data):
    write_if_changed(root / REPORT, report(root, data).encode())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['sync', 'check', 'status', 'candidates', 'decide'])
    parser.add_argument('--sources', action='store_true')
    parser.add_argument('--complete', action='store_true')
    parser.add_argument('--open', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--ids', nargs='+', default=[])
    group.add_argument('--compositions', nargs='+', default=[])
    parser.add_argument('--decision', choices=sorted(DECISIONS - {'pending'}))
    parser.add_argument('--targets', nargs='*', default=[])
    parser.add_argument('--reason', default='')
    args = parser.parse_args(argv)
    try:
        if args.action == 'sync':
            data = synchronize(); print(json.dumps(summary(ROOT, data), indent=2))
        elif args.action == 'check':
            print(json.dumps(check(ROOT, args.complete, args.sources), indent=2))
        elif args.action == 'status':
            print(json.dumps(summary(ROOT, load()), indent=2))
        elif args.action == 'decide':
            if not (args.ids or args.compositions) or not args.decision:
                raise ValueError('decide needs --ids, --decision, optional --targets and --reason')
            decide(ROOT, args.ids or args.compositions, args.decision, args.targets, args.reason, bool(args.compositions))
        else:
            target = render_candidates()
            if args.open:
                from build import open_pdf
                open_pdf(target)
            print(target)
        return 0
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print('Catalogue selection failed:', error)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
