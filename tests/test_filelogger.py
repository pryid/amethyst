"""Exercise the real C file logger with synthetic output, without running Amethyst."""
import os
from pathlib import Path
import shlex
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FileLoggerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = tempfile.TemporaryDirectory(prefix="amethyst-logger-test-")
        cls.executable = Path(cls.build.name) / "fixture"
        command = shlex.split(os.environ.get("CC", "cc")) + [
            "-std=c11", "-D_POSIX_C_SOURCE=200809L", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "Amethyst/Amethyst"), str(ROOT / "tests/filelogger.c"),
            "-o", str(cls.executable),
        ]
        subprocess.run(command, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.build.cleanup()

    def test_capture_with_open_or_closed_streams(self):
        for mode in ("normal", "closed-out", "closed-err", "closed-both", "twice"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                subprocess.run([self.executable, directory, mode], check=True, capture_output=True)
                logs = list((Path(directory) / "AmethystLogs").glob("*.log"))
                self.assertEqual(len(logs), 2 if mode == "twice" else 1)
                contents = [p.read_bytes() for p in logs]
                for path, content in zip(logs, contents):
                    self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                    self.assertIn(b"stdout capture ready\n", content)
                    self.assertIn(b"stderr capture ready\n", content)
                first = next(c for c in contents if b"fixture-out\n" in c)
                self.assertIn(b"fixture-err\n", first)
                self.assertIn(b"\x00\xff\n", first)
                if mode == "twice":
                    self.assertIn(b"first-file-only\n", first)
                    self.assertNotIn(b"second-file-only\n", first)
                    self.assertEqual(sum(b"second-file-only\n" in c for c in contents), 1)

    def test_invalid_destinations_preserve_existing_data(self):
        for mode in ("file", "symlink", "missing", "short-capacity", "relative", "long"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                documents = Path(directory) / "Documents"
                documents.mkdir()
                target = documents / "AmethystLogs"
                outside = Path(directory) / "outside"
                outside.mkdir()
                argument = str(documents)
                if mode == "file":
                    target.write_bytes(b"preserve existing data")
                elif mode == "symlink":
                    target.symlink_to(outside)
                elif mode == "missing":
                    argument = str(documents / "missing")
                elif mode == "relative":
                    argument = "relative-path"
                elif mode == "long":
                    argument = "/" + "x" * 5000
                fixture_mode = "short-capacity" if mode == "short-capacity" else "failure"
                subprocess.run([self.executable, argument, fixture_mode], check=True, capture_output=True)
                self.assertFalse(list(documents.rglob("*.log")))
                self.assertFalse(list(outside.iterdir()))
                if mode == "file":
                    self.assertEqual(target.read_bytes(), b"preserve existing data")


if __name__ == "__main__":
    unittest.main()
