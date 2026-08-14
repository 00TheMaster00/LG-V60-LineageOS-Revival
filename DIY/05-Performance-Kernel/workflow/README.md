# Portable Performance Workflow Files

- `tools/fdt-bundle.py`: list, split and replace one concatenated FDT entry.
- `tools/clone-vendor-gpu-bin.py`: balanced-brace source transformation helper.
- `tests/test_tools.py`: functional tests for both tools.
- `profiles/`: Daily, Power Save, CPU-MAX, GPU-MAX and ALL-MAX root scripts.
- `termux-shortcuts/`: launchers for the installed profile wrapper.

The original host launchers were purpose-built for one handset and contained
its serial, slot-B assumption, exact boot hashes and private filesystem paths.
They are intentionally excluded from the public repository. Their logic is
fully rewritten with placeholders in
[../BUILD-AND-REPACK.md](../BUILD-AND-REPACK.md).

Run:

```bash
bash tests/syntax-check.sh
```

Before installing profiles, read every sysfs write and compare its node and
available values to the running kernel. Daily caps GPU at 587 MHz; the MAX
profiles use 670 MHz and are not daily defaults.

