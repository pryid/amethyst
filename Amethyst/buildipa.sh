#!/bin/bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
output_dir="$project_dir/build"
if [[ "$(uname -s)" != Darwin ]]; then
    echo 'Building the IPA requires macOS/Xcode. Use the GitHub Actions workflow from Linux.' >&2
    exit 1
fi
mkdir -p "$output_dir"
rm -f "$output_dir/Amethyst-logging-unsigned.ipa" "$output_dir/SHA256SUMS"
build_dir="$(mktemp -d "${TMPDIR:-/tmp}/amethyst-build.XXXXXX")"
trap 'rm -rf "$build_dir"' EXIT

{
    git -C "$project_dir" rev-parse HEAD
    xcodebuild -version
    xcrun --sdk iphoneos --show-sdk-version
} > "$output_dir/build-info.txt"

if [[ ! -f "$project_dir/../basebins/basebins.tar" ]]; then
    python3 "$project_dir/../scripts/prepare_basebins.py"
fi

xcodebuild \
    -project "$project_dir/Amethyst.xcodeproj" \
    -target Amethyst -configuration Release -sdk iphoneos \
    ARCHS=arm64 ONLY_ACTIVE_ARCH=NO IPHONEOS_DEPLOYMENT_TARGET=12.0 \
    CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= \
    "SYMROOT=$build_dir" "OBJROOT=$build_dir/objects" \
    "CONFIGURATION_BUILD_DIR=$build_dir/products" \
    build 2>&1 | tee "$output_dir/xcodebuild.log"

app="$build_dir/Payload/Amethyst.app"
mkdir -p "$build_dir/Payload"
ditto "$build_dir/products/Amethyst.app" "$app"
xcrun lipo "$app/Amethyst" -verify_arch arm64
python3 - "$app/Info.plist" <<'PY'
import plistlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
info = plistlib.loads(path.read_bytes())
info['CFBundleDisplayName'] = 'Amethyst Logs'
path.write_bytes(plistlib.dumps(info))
PY

(
    cd "$build_dir"
    ditto -c -k --keepParent Payload "$output_dir/Amethyst-logging-unsigned.ipa"
)
(
    cd "$output_dir"
    shasum -a 256 Amethyst-logging-unsigned.ipa > SHA256SUMS
)
echo "Saved $output_dir/Amethyst-logging-unsigned.ipa; sign it before installation."
