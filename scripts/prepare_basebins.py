#!/usr/bin/env python3
"""Package the already-built helpers from the checked-in updater; run none of them."""
import argparse
import io
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def prepare(destination):
    payload = subprocess.check_output([
        "ar", "-p", str(ROOT / "basebins/tnsv2_updater.deb"), "data.tar",
    ])
    names = {
        "jbutil": "amethyst/jbutil",
        "launchd_hook.dylib": "amethyst/launchd_hook.dylib",
        "base_hook.dylib": "usr/lib/base_hook.dylib",
        "libjailbreak.dylib": "usr/lib/libjailbreak.dylib",
        "dyld_patch_text_12.bin": "amethyst/dyld_patch_text_12.bin",
        "dyld_patch_text_13.bin": "amethyst/dyld_patch_text_13.bin",
    }
    with tarfile.open(fileobj=io.BytesIO(payload)) as source:
        members = {m.name.removeprefix("./"): m for m in source.getmembers()}
        # The app's small tar reader handles regular files and directories, not PAX.
        with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as output:
            for directory in ("amethyst", "usr", "usr/lib"):
                entry = tarfile.TarInfo(directory)
                entry.type = tarfile.DIRTYPE
                entry.mode = 0o755
                output.addfile(entry)
            for name, path in names.items():
                member = members["amethyst/update/" + name]
                if not member.isfile():
                    raise ValueError("Expected a regular helper: " + name)
                entry = tarfile.TarInfo(path)
                entry.size = member.size
                entry.mode = 0o644 if name.endswith(".bin") else 0o755
                output.addfile(entry, source.extractfile(member))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=ROOT / "basebins/basebins.tar")
    prepare(parser.parse_args().output)
