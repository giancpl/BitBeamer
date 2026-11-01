"""Prepare Studio-specific white artwork; ordinary compilation needs no converters."""
import argparse
from pathlib import Path
import sys
from studio_assets import prepare_studio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = prepare_studio(Path(__file__).resolve().parents[1], check=args.check)
        print(f'Studio assets ready: {count}.')
    except (OSError, RuntimeError, ValueError) as error:
        print(f'Studio artwork failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
