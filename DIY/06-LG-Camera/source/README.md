# Project-Authored Camera Compatibility Source

This directory contains source created for the LineageOS compatibility layer,
not LG's decompiled application tree.

- `classes3/` contains the ten compatibility shims assembled into the added
  `classes3.dex`.
- `native/surface_usage_shim.cpp` contains the JNI bridge used by
  `SurfaceUsageShim.smali`.
- `native/build_surface_usage_shim.sh` and `native/NATIVE-BUILD.md` provide a
  pinned, byte-exact owner-run rebuild and ELF/hash verification path for that
  JNI bridge.

These files are covered by the repository's MIT license. Names and method
signatures intentionally match APIs expected by LG Camera, but the minimal
fallback implementations were created for this project.

Candidate 24 also includes a proprietary `libmpbase.so` dependency. That
binary and its source are not published here; its exact output-entry hash is
recorded in `../audit/expected-apk-entry-changes.csv` and it is reconstructed
only through the exact-input binary delta.

The source directory is for security review and future clean-room maintenance.
The JNI library is independently buildable from this project-authored source;
the complete APK is not, because the proprietary app must be supplied by its
owner and reconstructed through the verified builder.
