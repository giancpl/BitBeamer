"""Keep default container validation from trying to start nested Docker."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('validate_release', ROOT / 'scripts/validate-release.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidationBackendTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='bitbeamer validation ')
        self.addCleanup(directory.cleanup)
        self.archive = Path(directory.name).resolve() / 'template.zip'
        self.archive.write_bytes(b'archive placeholder')

    def test_default_docker_uses_native_validation_inside_container(self):
        with mock.patch.object(validator, 'docker_image', return_value='docker'), \
                mock.patch.object(validator.subprocess, 'run') as run, \
                mock.patch.object(validator, 'validate') as native:
            self.assertEqual(validator.main([str(self.archive)]), 0)
            native.assert_not_called()
        self.assertEqual(run.call_args.args[0][-4:],
                         ['scripts/validate-release.py', '/release.zip', '--backend', 'native'])

    def test_explicit_native_validation_does_not_access_docker(self):
        with mock.patch.object(validator, 'docker_image') as docker, \
                mock.patch.object(validator, 'validate') as native:
            self.assertEqual(validator.main([str(self.archive), '--backend', 'native']), 0)
            docker.assert_not_called()
            native.assert_called_once_with(self.archive)


if __name__ == '__main__':
    unittest.main()
