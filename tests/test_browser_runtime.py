"""Exercise Chromium process failures without requiring an installed browser."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BrowserRuntimeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Optional browser maintenance tests need Node')
    def test_browser_process_lifecycle(self):
        result = subprocess.run([shutil.which('node'), '--test',
                                 str(ROOT / 'tests/browser_runtime.test.mjs')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
