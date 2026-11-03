"""Keep generated documents out of Git while preserving prepared artwork."""

from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
checks = runpy.run_path(str(ROOT / 'scripts/check-repo.py'))


class RepositoryTests(unittest.TestCase):
    def test_sources_and_prepared_artwork_are_allowed(self):
        paths = ['main.tex', 'scripts/build.py', 'assets/new-icon.pdf',
                 'assets/generated/alice.pdf', 'images/bitpolito/bull-white.pdf',
                 '.vscode/tasks.json', '.github/workflows/build.yml']
        self.assertEqual(checks['unwanted_paths'](paths), [])

    def test_local_outputs_and_redundant_placeholders_are_rejected(self):
        paths = ['build/main.pdf', 'dist/template.zip', 'main.pdf', 'examples/preview.pdf',
                 'main.aux', 'main.run.xml', 'main.synctex.gz', 'scripts/__pycache__/build.pyc',
                 'notes.md~', '.DS_Store', '.coverage', '.ruff_cache/cache', '.mypy_cache/cache',
                 '.pytest_cache/cache', 'htmlcov/index.html', 'assets/characters/.gitkeep', 'assets/characters/alice.svg']
        self.assertEqual(set(checks['unwanted_paths'](paths)), set(paths) - {'assets/characters/alice.svg'})

    @unittest.skipUnless(shutil.which('git'), 'Git is required')
    def test_git_check_includes_new_sources_excludes_ignored_outputs_and_reports_staged_outputs(self):
        with tempfile.TemporaryDirectory(prefix='bitbeamer repository ') as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            (root / 'main.tex').write_text('source', encoding='utf-8')
            (root / '.gitignore').write_text('*.pdf\n', encoding='utf-8')
            (root / 'new-source.tex').write_text('new source', encoding='utf-8')
            (root / 'main.pdf').write_bytes(b'local preview')
            subprocess.run(['git', '-C', str(root), 'add', 'main.tex'], check=True)
            self.assertEqual(checks['check_repository'](root), 3)
            subprocess.run(['git', '-C', str(root), 'add', '--force', 'main.pdf'], check=True)
            with self.assertRaisesRegex(RuntimeError, 'main.pdf'):
                checks['check_repository'](root)

    def test_figma_references_are_local_inputs_not_repository_sources(self):
        self.assertEqual(checks['unwanted_paths'](['design-references/README.md']), [])
        paths = ['design-references/figma/frame.svg', 'design-references/figma/slide.pdf']
        self.assertEqual(checks['unwanted_paths'](paths), sorted(paths))


if __name__ == '__main__':
    unittest.main()
