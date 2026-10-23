"""Validate the payload layout consumed by handoff.c and its limited tar reader."""
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BasebinsTests(unittest.TestCase):
    def test_packaged_helpers_keep_their_bytes_and_install_paths(self):
        payload = subprocess.check_output(["ar", "-p", ROOT / "basebins/tnsv2_updater.deb", "data.tar"])
        expected = {
            "amethyst/jbutil", "amethyst/launchd_hook.dylib",
            "usr/lib/base_hook.dylib", "usr/lib/libjailbreak.dylib",
            "amethyst/dyld_patch_text_12.bin", "amethyst/dyld_patch_text_13.bin",
        }
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "basebins.tar"
            subprocess.run(["python3", ROOT / "scripts/prepare_basebins.py", destination], check=True)
            with tarfile.open(destination) as result, tarfile.open(fileobj=io.BytesIO(payload)) as source:
                members = result.getmembers()
                files = {m.name: m for m in members if m.isfile()}
                originals = {m.name.removeprefix("./"): m for m in source.getmembers()}
                self.assertEqual(set(files), expected)
                self.assertEqual({m.name for m in members if m.isdir()}, {"amethyst", "usr", "usr/lib"})
                for member in members:
                    self.assertIn(member.type, (tarfile.REGTYPE, tarfile.DIRTYPE))
                    self.assertEqual((member.uid, member.gid), (0, 0))
                    self.assertFalse(member.pax_headers)
                for name, member in files.items():
                    self.assertEqual(member.mode, 0o644 if name.endswith(".bin") else 0o755)
                    original = originals["amethyst/update/" + Path(name).name]
                    self.assertEqual(result.extractfile(member).read(), source.extractfile(original).read())
            before = destination.read_bytes()
            subprocess.run(["python3", ROOT / "scripts/prepare_basebins.py", destination], check=True)
            self.assertEqual(destination.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
