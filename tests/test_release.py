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
        self.root = Path(directory.name)
        (self.root / 'build').mkdir()
        (self.root / 'dist').mkdir()
        for source in release.PREVIEWS:
            (self.root / 'build' / source).write_bytes(b'%PDF-1.5 preview')
        self.archive = self.root / 'dist/bitbeamer-overleaf.zip'
        checker = mock.patch.object(release, 'check_docs')
        checker.start()
        self.addCleanup(checker.stop)

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
                mock.patch.object(release, 'package', return_value=self.archive), \
                mock.patch.object(release.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'validate')):
            with self.assertRaises(subprocess.CalledProcessError):
                release.release(self.root)
        self.assertEqual(list((self.root / 'dist').iterdir()), [])

    def test_explicit_backend_and_image_reach_builds_and_validation(self):
        with mock.patch.object(release.build, 'main', return_value=0) as build, \
                mock.patch.object(release, 'package', return_value=self.archive), \
                mock.patch.object(release.subprocess, 'run') as run:
            self.assertEqual(release.release(self.root, 'docker', 'local-image'), self.archive)
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
