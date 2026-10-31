"""Check release sequencing and failure handling without a TeX toolchain."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import release
from package import DOCUMENT_SOURCES


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='bitbeamer release ')
        self.addCleanup(directory.cleanup)
        # macOS aliases /var and Windows may expose short temporary paths.
        self.root = Path(directory.name).resolve()
        (self.root / 'build').mkdir()
        (self.root / 'dist').mkdir()
        for source in release.PREVIEWS:
            (self.root / 'build' / source).write_bytes(b'%PDF-1.5 preview')
        self.archive = self.root / 'dist/bitbeamer-overleaf.zip'
        for name in ('check_docs', 'check_prepared', 'check_catalogue'):
            checker = mock.patch.object(release, name)
            checker.start()
            self.addCleanup(checker.stop)

    def prepared_archive(self, root, target):
        target.write_bytes(b'new validated archive')
        return target

    def previous_release(self):
        previous = {self.archive.name: b'previous archive'}
        previous.update({name: b'previous preview' for name in release.PREVIEWS.values()})
        for name, content in previous.items():
            (self.root / 'dist' / name).write_bytes(content)
        return previous

    def test_failed_preflight_stops_before_any_compilation(self):
        with mock.patch.object(release, 'check_catalogue', side_effect=RuntimeError('stale catalogue')), \
                mock.patch.object(release.build, 'main') as build:
            with self.assertRaisesRegex(RuntimeError, 'stale catalogue'):
                release.release(self.root)
            build.assert_not_called()

    def test_compile_failure_stops_before_packaging(self):
        with mock.patch.object(release.build, 'main', return_value=1), \
                mock.patch.object(release, 'package') as package, \
                mock.patch.object(release.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'did not compile'):
                release.release(self.root)
            package.assert_not_called()
            run.assert_not_called()

    def test_invalid_archive_does_not_export_previews(self):
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'validate')):
            with self.assertRaises(subprocess.CalledProcessError):
                release.release(self.root)
        self.assertEqual(list((self.root / 'dist').iterdir()), [])

    def test_failed_validation_preserves_previous_release_and_removes_staging(self):
        previous = self.previous_release()
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'validate')):
            with self.assertRaises(subprocess.CalledProcessError):
                release.release(self.root)
        self.assertEqual({p.name: p.read_bytes() for p in (self.root / 'dist').iterdir()}, previous)

    def test_missing_preview_preserves_previous_release(self):
        previous = self.previous_release()
        (self.root / 'build' / next(iter(release.PREVIEWS))).unlink()
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run'):
            with self.assertRaises(FileNotFoundError):
                release.release(self.root)
        self.assertEqual({p.name: p.read_bytes() for p in (self.root / 'dist').iterdir()}, previous)

    def test_explicit_backend_and_image_reach_builds_and_validation(self):
        with mock.patch.object(release.build, 'main', return_value=0) as build, \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run') as run:
            self.assertEqual(release.release(self.root, 'docker', 'local-image'), self.archive)
        self.assertEqual(self.archive.read_bytes(), b'new validated archive')
        self.assertEqual(set(p.name for p in (self.root / 'dist').iterdir()),
                         {self.archive.name, *release.PREVIEWS.values()})
        self.assertEqual(len(build.call_args_list), len(DOCUMENT_SOURCES))
        self.assertEqual([call.args[0][0] for call in build.call_args_list],
                         list(DOCUMENT_SOURCES.values()))
        for call in build.call_args_list:
            self.assertEqual(call.args[0][-4:], ['--backend', 'docker', '--image', 'local-image'])
            self.assertEqual(call.kwargs['root'], self.root)
        self.assertEqual(run.call_args.args[0][-4:], ['--backend', 'docker', '--image', 'local-image'])
        for source, target in release.PREVIEWS.items():
            self.assertEqual((self.root / 'dist' / target).read_bytes(),
                             (self.root / 'build' / source).read_bytes())


if __name__ == '__main__':
    unittest.main()
