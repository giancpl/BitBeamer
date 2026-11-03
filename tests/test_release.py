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
        for source in (*release.PREVIEWS, *release.STUDIO_PREVIEWS):
            (self.root / 'build' / source).write_bytes(b'%PDF-1.5 preview')
        self.archive = self.root / 'dist/bitbeamer-academic-overleaf.zip'
        approval = mock.patch('studio_review.require_approved')
        approval.start()
        self.addCleanup(approval.stop)
        for name in ('check_docs', 'check_prepared', 'check_catalogue', 'prepare_catalogue'):
            checker = mock.patch.object(release, name)
            checker.start()
            self.addCleanup(checker.stop)

    def prepared_archive(self, root, target, style='academic', review=False):
        target.write_bytes(b'new validated archive')
        return target

    def previous_release(self):
        previous = {self.archive.name: b'previous archive'}
        previous.update({name: b'previous preview' for name in release.PREVIEWS.values()})
        previous.update({release.LEGACY_ARCHIVE: b'previous legacy zip',
                         release.LEGACY_PREVIEW: b'previous legacy preview'})
        for name, content in previous.items():
            (self.root / 'dist' / name).write_bytes(content)
        return previous

    def test_failed_preflight_stops_before_any_compilation(self):
        with mock.patch.object(release, 'check_catalogue', side_effect=RuntimeError('stale catalogue')), \
                mock.patch.object(release.build, 'main') as build:
            with self.assertRaisesRegex(RuntimeError, 'stale catalogue'):
                release.release(self.root, style='academic')
            build.assert_not_called()

    def test_compile_failure_stops_before_packaging(self):
        with mock.patch.object(release.build, 'main', return_value=1), \
                mock.patch.object(release, 'package') as package, \
                mock.patch.object(release.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'did not compile'):
                release.release(self.root, style='academic')
            package.assert_not_called()
            run.assert_not_called()

    def test_invalid_archive_does_not_export_previews(self):
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'validate')):
            with self.assertRaises(subprocess.CalledProcessError):
                release.release(self.root, style='academic')
        self.assertEqual(list((self.root / 'dist').iterdir()), [])

    def test_failed_validation_preserves_previous_release_and_removes_staging(self):
        previous = self.previous_release()
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'validate')):
            with self.assertRaises(subprocess.CalledProcessError):
                release.release(self.root, style='academic')
        self.assertEqual({p.name: p.read_bytes() for p in (self.root / 'dist').iterdir()}, previous)

    def test_missing_preview_preserves_previous_release(self):
        previous = self.previous_release()
        (self.root / 'build' / next(iter(release.PREVIEWS))).unlink()
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run'):
            with self.assertRaises(FileNotFoundError):
                release.release(self.root, style='academic')
        self.assertEqual({p.name: p.read_bytes() for p in (self.root / 'dist').iterdir()}, previous)

    def test_explicit_backend_and_image_reach_builds_and_validation(self):
        with mock.patch.object(release.build, 'main', return_value=0) as build, \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run') as run:
            self.assertEqual(release.release(self.root, style='academic', image='local-image'), self.archive)
        self.assertEqual(self.archive.read_bytes(), b'new validated archive')
        self.assertEqual((self.root / 'dist' / release.LEGACY_ARCHIVE).read_bytes(), self.archive.read_bytes())
        self.assertEqual((self.root / 'dist' / release.LEGACY_PREVIEW).read_bytes(),
                         (self.root / 'dist/bitbeamer-academic-preview.pdf').read_bytes())
        self.assertEqual(set(p.name for p in (self.root / 'dist').iterdir()),
                         {self.archive.name, *release.PREVIEWS.values(), release.LEGACY_ARCHIVE, release.LEGACY_PREVIEW})
        self.assertEqual(len(build.call_args_list), len(set(DOCUMENT_SOURCES.values())))
        self.assertEqual([call.args[0][0] for call in build.call_args_list],
                         list(dict.fromkeys(DOCUMENT_SOURCES.values())))
        for call in build.call_args_list:
            self.assertEqual(call.args[0][-4:], ['--backend', 'docker', '--image', 'local-image'])
            self.assertEqual(call.kwargs['root'], self.root)
        self.assertEqual(run.call_args.args[0][-4:], ['--backend', 'docker', '--image', 'local-image'])
        for source, target in release.PREVIEWS.items():
            self.assertEqual((self.root / 'dist' / target).read_bytes(),
                             (self.root / 'build' / source).read_bytes())

    def test_default_release_checks_both_styles_before_promoting_either(self):
        (self.root / 'build/main-studio.pdf').write_bytes(b'%PDF-studio')
        with mock.patch.object(release.build, 'main', return_value=0) as build, \
                mock.patch.object(release, 'prepare_studio') as assets, \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive) as package, \
                mock.patch.object(release.subprocess, 'run') as validate:
            paths = release.release(self.root)
        self.assertEqual(tuple(path.name for path in paths),
                         ('bitbeamer-academic-overleaf.zip', 'bitbeamer-studio-overleaf.zip'))
        self.assertEqual([call.kwargs['style'] for call in package.call_args_list], ['academic', 'studio'])
        self.assertEqual(validate.call_count, 2)
        for selected, call in zip(('academic', 'studio'), validate.call_args_list):
            self.assertIn(selected, call.args[0])
        self.assertEqual(build.call_args_list[-2].args[0][0], 'main-studio.tex')
        self.assertEqual(build.call_args_list[-1].args[0][0], 'examples/studio-selected-templates.tex')
        self.assertEqual((self.root / 'dist/bitbeamer-studio-templates.pdf').read_bytes(), b'%PDF-1.5 preview')
        assets.assert_called_once_with(self.root, check=True)
        self.assertEqual((self.root / 'dist/bitbeamer-studio-preview.pdf').read_bytes(), b'%PDF-studio')

    def test_second_archive_failure_preserves_both_previous_styles(self):
        previous = self.previous_release()
        previous.update({'bitbeamer-studio-overleaf.zip': b'previous studio archive',
                         'bitbeamer-studio-preview.pdf': b'previous studio preview',
                         'bitbeamer-studio-templates.pdf': b'previous template catalogue'})
        for name, content in previous.items():
            (self.root / 'dist' / name).write_bytes(content)
        (self.root / 'build/main-studio.pdf').write_bytes(b'%PDF-studio')
        with mock.patch.object(release.build, 'main', return_value=0), \
                mock.patch.object(release, 'prepare_studio'), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run',
                                  side_effect=[None, subprocess.CalledProcessError(1, 'studio')]):
            with self.assertRaises(subprocess.CalledProcessError):
                release.release(self.root)
        self.assertEqual({p.name: p.read_bytes() for p in (self.root / 'dist').iterdir()}, previous)

    def test_studio_only_release_leaves_academic_files_untouched(self):
        previous = self.previous_release()
        (self.root / 'build/main-studio.pdf').write_bytes(b'%PDF-studio')
        with mock.patch.object(release.build, 'main', return_value=0) as build, \
                mock.patch.object(release, 'prepare_studio'), \
                mock.patch.object(release, 'package', side_effect=self.prepared_archive), \
                mock.patch.object(release.subprocess, 'run'):
            result = release.release(self.root, style='studio', backend='native')
        self.assertEqual(result.name, 'bitbeamer-studio-overleaf.zip')
        self.assertEqual(build.call_count, 2)
        for name, content in previous.items():
            self.assertEqual((self.root / 'dist' / name).read_bytes(), content)


if __name__ == '__main__':
    unittest.main()
