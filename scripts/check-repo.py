"""Check tracked and prospective sources, excluding ignored local outputs."""

import argparse
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FOLDERS = {'build', 'dist', '__pycache__', '.venv', '.pytest_cache'}
TEX_OUTPUTS = {'.aux', '.bbl', '.bcf', '.blg', '.fdb_latexmk', '.fls', '.log',
               '.nav', '.out', '.snm', '.toc', '.vrb', '.synctex.gz', '.run.xml'}
LOCAL_FILES = {'.DS_Store', 'Thumbs.db'}


def unwanted_paths(paths):
    """Return tracked outputs; PDF sources and prepared artwork remain allowed."""
    unwanted = []
    paths = set(paths)
    for name in sorted(paths):
        path = PurePosixPath(name)
        output = (any(part in OUTPUT_FOLDERS for part in path.parts)
                  or path.name in LOCAL_FILES
                  or path.is_relative_to(PurePosixPath('design-references/figma'))
                  or any(path.name.endswith(suffix) for suffix in TEX_OUTPUTS)
                  or path.suffix in {'.pyc', '.tmp', '.swp', '.swo', '.zip', '.7z'}
                  or path.name.endswith(('~', '.tar.gz'))
                  or (path.suffix == '.pdf' and (len(path.parts) == 1 or path.parts[0] == 'examples')))
        redundant = path.name == '.gitkeep' and any(
            other != name and PurePosixPath(other).is_relative_to(path.parent) for other in paths)
        if output or redundant:
            unwanted.append(name)
    return unwanted


def check_repository(root=ROOT):
    git = shutil.which('git')
    if not git:
        raise RuntimeError('This check needs Git and a working checkout.')
    result = subprocess.run([git, '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    paths = result.stdout.decode('utf-8').split('\0')
    paths = [name for name in paths if name]
    unwanted = unwanted_paths(paths)
    if unwanted:
        raise RuntimeError('Tracked or prospective files include local outputs or redundant placeholders:\n'
                           + '\n'.join(unwanted)
                           + '\nRemove them from Git; keep compiled documents in build/ or dist/.')
    return len(set(paths))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        print(f'Repository ready: {check_repository(args.root.resolve())} tracked/prospective files; no local outputs.')
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Repository check failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
