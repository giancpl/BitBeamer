"""Refresh the artwork library, or check it without making changes."""
import argparse
from pathlib import Path
import sys
from asset_library import check_prepared, prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true', help='Read-only check of prepared artwork')
    parser.add_argument('--converter', choices=('auto', 'rsvg', 'inkscape'), default='auto')
    parser.add_argument('--force', action='store_true', help='Regenerate every asset')
    args = parser.parse_args()
    try:
        count = check_prepared(args.root.resolve()) if args.check else prepare(
            args.root.resolve(), converter=args.converter, force=args.force)
    except Exception as error:
        print(f'Asset preparation failed: {error}', file=sys.stderr)
        return 1
    print(f'Assets ready: {count}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
