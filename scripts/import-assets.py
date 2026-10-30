"""Copy the reviewed SVG collection using the names in assets/index.json."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Folder containing the original SVG exports')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    records = json.loads((root / 'assets/index.json').read_text(encoding='utf-8'))
    expected = {record['original'] for record in records}
    exclusions = root / 'assets/excluded.json'
    excluded = {record['original'] for record in json.loads(exclusions.read_text(encoding='utf-8'))} if exclusions.exists() else set()
    actual = {path.name for path in args.source.glob('*.svg')}
    if expected - actual or actual - expected - excluded:
        parser.error(f'Collection differs from the reviewed index. Missing: {sorted(expected-actual)}; extra: {sorted(actual-expected-excluded)}')
    for record in records:
        source = args.source / record['original']
        target = root / 'assets' / record['category'] / (record['name'] + '.svg')
        if target.exists() and target.read_bytes() != source.read_bytes():
            parser.error(f'Will not overwrite modified artwork: {target}')
    for record in records:
        source = args.source / record['original']
        target = root / 'assets' / record['category'] / (record['name'] + '.svg')
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        record['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    (root / 'assets/index.json').write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Imported {len(records)} SVGs; originals unchanged.')


if __name__ == '__main__':
    main()
