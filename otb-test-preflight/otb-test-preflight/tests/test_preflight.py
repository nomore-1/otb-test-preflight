import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from preflight import inspect


class PreflightTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'install'
        self.bin = self.home / 'bin'
        self.bin.mkdir(parents=True)
        for name in ('postgres', 'pgxc_ctl', 'psql'):
            self.executable(self.bin / name)

    def executable(self, path):
        path.write_bytes(b'fixture binary\n')
        path.chmod(0o755)

    def report(self, source=None, path=None):
        return inspect(str(self.home), str(self.bin) if path is None else path, source)

    def test_valid_environment(self):
        self.assertEqual(self.report()['status'], 'pass')

    def test_missing_home(self):
        self.assertEqual(inspect(None, str(self.bin), None)['status'], 'fail')

    def test_missing_binary(self):
        (self.bin / 'pgxc_ctl').unlink()
        self.assertEqual(self.report()['status'], 'fail')

    def test_non_executable(self):
        (self.bin / 'psql').chmod(0o644)
        self.assertEqual(self.report()['status'], 'fail')

    def test_path_shadow(self):
        other = self.root / 'other'
        other.mkdir()
        self.executable(other / 'postgres')
        self.assertEqual(self.report(path=os.pathsep.join([str(other), str(self.bin)]))['status'], 'fail')

    def test_symlink_path(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.bin, target_is_directory=True)
        self.assertEqual(self.report(path=str(alias))['status'], 'pass')

    def test_binary_match(self):
        source = self.root / 'postgres'
        self.executable(source)
        self.assertEqual(self.report(source)['status'], 'pass')

    def test_binary_mismatch(self):
        source = self.root / 'postgres'
        source.write_bytes(b'different build')
        self.assertEqual(self.report(source)['status'], 'warn')

    def test_missing_source(self):
        self.assertEqual(self.report(self.root / 'missing')['status'], 'fail')

    def test_cli_exit_status(self):
        env = dict(os.environ, PATH=str(self.bin))
        command = [sys.executable, str(ROOT / 'scripts/preflight.py'), '--home', str(self.home)]
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['status'], 'pass')
        (self.bin / 'postgres').unlink()
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['status'], 'fail')


if __name__ == '__main__':
    unittest.main()
