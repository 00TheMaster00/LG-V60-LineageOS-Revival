# Reproduce the Camera JNI Shim

This is an owner-run byte-for-byte build of the project-authored
`liblgcamera_surface_usage.so`. It does not build or redistribute LG Camera.
The final library is only 3,872 bytes and its identity is also pinned in the
Candidate 24 APK-entry manifest.

## Pinned inputs

| Input | Identity |
|---|---|
| AOSP Clang prebuilt repository | `9916fb51ccb914d62d35ad9a7b9b21d2ef046928` |
| Toolchain directory | `clang-r563880c` |
| `clang++` SHA-256 | `AF0F25CA6818AED54C1CAB03DC591ACD549F385B8447148326A413E3E59C22B7` |
| `ld.lld` SHA-256 | `784146955ED87545385BF5C89B3B920CA7FE3AC83E034C3E6C53783CE544ADF1` |
| AOSP `libnativehelper` repository | `aef2939781fc0b57b4477df7160935cdf5697919` |
| normalized `include_jni/jni.h` SHA-256 | `2A3CEA5E4306872202592406593F6465F07B848D75ED03AD07E2936479867F0A` |
| project C++ source SHA-256 | `3587D81948D2F47BBE95BDDAC7A62F7DFD0195F87EAF2EA3938CEA99F91E0D42` |

The two upstream repositories are the official AOSP sources:

- <https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86>
- <https://android.googlesource.com/platform/libnativehelper>

Check out the exact commits above. Do not substitute a similarly named
third-party toolchain. A clean `libnativehelper` checkout is preferred; the
script normalizes CRLF only for the content check so a Windows checkout does
not fail solely because of line endings.

## Build and verify

From Linux or WSL:

```bash
cd DIY/06-LG-Camera/source/native
AOSP_CLANG_ROOT=/absolute/path/to/clang-r563880c \
JNI_INCLUDE=/absolute/path/to/libnativehelper/include_jni \
./build_surface_usage_shim.sh /tmp/lgcamera-native-output
```

The script builds minimal link-time-only `libandroid.so` and `libdl.so` stubs.
They provide no runtime code and are not packaged; they only make the Android
ELF dependency names and `LIBC` symbol versions deterministic without copying
proprietary device libraries.

The build fails unless all of these match:

| Output | Bytes | SHA-256 |
|---|---:|---|
| `surface_usage_shim.o` | tool-defined | `750DB38B0124A43143F142144B768AF73CC8FE0031FD6D58356C2C7EBD9812DC` |
| `liblgcamera_surface_usage.so` | 3,872 | `6C10BF25D9CFE3C719851D0F2951F02F06B2A47BE90E0A498509E2B9826CA5D1` |

It also verifies the AArch64 shared object's `libandroid.so`/`libdl.so`
dependencies, SONAME, immediate binding, exported JNI entry point and
versioned `dlopen`/`dlsym` imports. The final library hash must match the entry
recorded in `../../audit/expected-apk-entry-changes.csv`.

Public CI syntax-checks this recipe and guards its pinned constants, but does
not download the large AOSP prebuilt toolchain. The exact rebuild remains an
owner-run gate; the checked-in source and script let another reviewer perform
the same gate independently.
