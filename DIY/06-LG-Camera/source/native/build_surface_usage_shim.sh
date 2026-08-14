#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CLANG_ROOT="${AOSP_CLANG_ROOT:-}"
JNI_ROOT="${JNI_INCLUDE:-}"
OUTPUT="${1:-}"

if [[ -z "$CLANG_ROOT" || -z "$JNI_ROOT" || -z "$OUTPUT" ]]; then
    cat >&2 <<'EOF'
Usage:
  AOSP_CLANG_ROOT=/path/to/clang-r563880c \
  JNI_INCLUDE=/path/to/libnativehelper/include_jni \
  ./build_surface_usage_shim.sh /path/to/output-directory
EOF
    exit 2
fi

CLANG="$CLANG_ROOT/bin/clang++"
LLD="$CLANG_ROOT/bin/ld.lld"
READELF="$CLANG_ROOT/bin/llvm-readelf"
NM="$CLANG_ROOT/bin/llvm-nm"
JNI_HEADER="$JNI_ROOT/jni.h"
SOURCE="$ROOT/surface_usage_shim.cpp"
STUBS="$ROOT/link-stubs"

require_hash() {
    local path="$1" expected="$2" actual
    [[ -f "$path" ]] || { echo "ERROR: missing $path" >&2; exit 10; }
    actual="$(sha256sum "$path" | awk '{print $1}')"
    [[ "$actual" == "$expected" ]] || {
        echo "ERROR: SHA-256 mismatch for $path" >&2
        echo "expected=$expected" >&2
        echo "actual=$actual" >&2
        exit 11
    }
}

require_hash "$CLANG" af0f25ca6818aed54c1cab03dc591acd549f385b8447148326a413e3e59c22b7
require_hash "$LLD" 784146955ed87545385bf5c89b3b920ca7fe3ac83e034c3e6c53783ce544adf1
require_hash "$SOURCE" 3587d81948d2f47bbe95bddac7a62f7dfd0195f87eaf2ea3938cea99f91e0d42

[[ -f "$JNI_HEADER" ]] || { echo "ERROR: missing $JNI_HEADER" >&2; exit 10; }
JNI_HASH="$(tr -d '\r' < "$JNI_HEADER" | sha256sum | awk '{print $1}')"
[[ "$JNI_HASH" == 2a3cea5e4306872202592406593f6465f07b848d75ed03ad07e2936479867f0a ]] || {
    echo "ERROR: jni.h does not match pinned libnativehelper content." >&2
    echo "actual-normalized=$JNI_HASH" >&2
    exit 11
}

for tool in "$READELF" "$NM"; do
    [[ -x "$tool" ]] || { echo "ERROR: missing tool $tool" >&2; exit 10; }
done

WORK="$(mktemp -d "${TMPDIR:-/tmp}/lgcamera-native.XXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT
mkdir -p -- "$OUTPUT"

"$CLANG" --target=aarch64-linux-android35 \
    -shared -nostdlib -fuse-ld=lld \
    -Wl,-soname,libandroid.so \
    "$STUBS/libandroid_stub.S" -o "$WORK/libandroid.so"

"$CLANG" --target=aarch64-linux-android35 \
    -shared -nostdlib -fuse-ld=lld \
    -Wl,-soname,libdl.so \
    -Wl,--version-script,"$STUBS/libdl.map" \
    "$STUBS/libdl_stub.S" -o "$WORK/libdl.so"

"$CLANG" --target=aarch64-linux-android35 \
    -ffreestanding -fPIC -O2 -I"$JNI_ROOT" \
    -c "$SOURCE" -o "$WORK/surface_usage_shim.o"

"$CLANG" --target=aarch64-linux-android35 \
    -shared -nostdlib -fuse-ld=lld \
    -Wl,-soname,liblgcamera_surface_usage.so \
    -Wl,-z,now -Wl,--hash-style=gnu \
    "$WORK/surface_usage_shim.o" -L"$WORK" \
    -Wl,--no-as-needed -landroid -ldl \
    -o "$WORK/liblgcamera_surface_usage.so"

require_hash "$WORK/surface_usage_shim.o" 750db38b0124a43143f142144b768af73cc8fe0031fd6d58356c2c7ebd9812dc
require_hash "$WORK/liblgcamera_surface_usage.so" 6c10bf25d9cfe3c719851d0f2951f02f06b2a47be90e0a498509e2b9826ca5d1
[[ "$(stat -c '%s' "$WORK/liblgcamera_surface_usage.so")" == 3872 ]] || {
    echo "ERROR: unexpected shared-library size." >&2
    exit 12
}

DYNAMIC="$($READELF -d "$WORK/liblgcamera_surface_usage.so")"
SYMBOLS="$($NM -D "$WORK/liblgcamera_surface_usage.so")"
grep -q 'Shared library: \[libandroid.so\]' <<<"$DYNAMIC"
grep -q 'Shared library: \[libdl.so\]' <<<"$DYNAMIC"
grep -q 'Library soname: \[liblgcamera_surface_usage.so\]' <<<"$DYNAMIC"
grep -q 'BIND_NOW' <<<"$DYNAMIC"
grep -q 'Java_com_lge_camera_util_SurfaceUsageShim_nativeSetConsumerUsage' <<<"$SYMBOLS"
grep -q 'U dlopen@LIBC' <<<"$SYMBOLS"
grep -q 'U dlsym@LIBC' <<<"$SYMBOLS"

install -m 0644 "$WORK/surface_usage_shim.o" "$OUTPUT/surface_usage_shim.o"
install -m 0644 "$WORK/liblgcamera_surface_usage.so" "$OUTPUT/liblgcamera_surface_usage.so"

echo "NATIVE REBUILD: PASS"
echo "object_sha256=750DB38B0124A43143F142144B768AF73CC8FE0031FD6D58356C2C7EBD9812DC"
echo "library_sha256=6C10BF25D9CFE3C719851D0F2951F02F06B2A47BE90E0A498509E2B9826CA5D1"
