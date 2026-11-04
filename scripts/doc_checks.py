"""Check repository Markdown links offline, without altering any files."""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', 'build', 'dist', '__pycache__', '.venv', 'node_modules'}
INLINE = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*["\'])?\s*\)')
REFERENCE = re.compile(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)')


def check_docs(root=ROOT):
    root = root.resolve()
    issues = []
    count = 0
    for path in sorted(root.rglob('*.md')):
        if any(part in IGNORED for part in path.relative_to(root).parts):
            continue
        if path.relative_to(root).parts[0] == 'presentations' and path.relative_to(root).as_posix() != 'presentations/README.md':
            continue
        count += 1
        fence = None
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            marker = re.match(r'^\s*(`{3,}|~{3,})', line)
            if marker:
                delimiter = marker.group(1)[0]
                if fence is None:
                    fence = delimiter
                elif fence == delimiter:
                    fence = None
                continue
            if fence is not None:
                continue
            # Inline code may contain illustrative links that are not document navigation.
            line = re.sub(r'`+[^`]*`+', '', line)
            targets = [match.group(1) for match in INLINE.finditer(line)]
            reference = REFERENCE.match(line)
            if reference:
                targets.append(reference.group(1))
            for target in targets:
                target = target.strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                relative = unquote(parsed.path)
                destination = (path.parent / relative).resolve()
                if relative.startswith('/') or not destination.is_relative_to(root) or not destination.exists():
                    issues.append(f'{path.relative_to(root).as_posix()}:{number}: missing local target {target}')
    if issues:
        raise RuntimeError('Documentation links failed:\n' + '\n'.join(issues))
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        print(f'Documentation links ready: {check_docs(args.root)} Markdown files; no network access needed.')
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
