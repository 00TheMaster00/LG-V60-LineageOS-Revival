# Performance Kernel and Runtime Profiles

This track reproduces two independent changes on a pinned LineageOS LG SM8250
kernel base:

1. **Performance V1** keeps all CPUs available to core control and changes
   schedutil's default transition limits to 0 microseconds up / 10,000
   microseconds down.
2. **GPU 670** promotes an already vendor-defined 670 MHz/NOM_L1 OPP into the
   speed-bin-0 power table while retaining 587 MHz/NOM immediately below it.

The project did not invent a new voltage/frequency pair. It exposed the
vendor-authored 670 MHz operating point and rebuilt the ordered ladder:

```text
670 / 587 / 525 / 490 / 441.6 / 400 / 305 / 0 MHz
```

## Proven revisions

```text
Lineage base: 29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2
Performance V1: 175901fa8aa5614cc50a695cdaa783a1bbfbba41
Performance V2/GPU 670: 00d8f9c3262c90159d7bc9ea65fa6dd45797895e
```

Exact patches are in [patches](patches/). The first two patches are the
performance release. Patches 0003-0008 in the Research path are failed
fingerprint experiments and must not be included in a normal performance
build.

The public patch headers use the project owner's GitHub noreply identity to
avoid exposing a local username. Their leading `From <object-id>` lines retain
the original private commit IDs; replayed tree content is unchanged, but a
new `git am` commit ID can differ because author metadata is part of a commit.

## Host requirements

The recorded workflow used WSL/Linux with:

- Git, Bash, Python 3 and PowerShell on the Windows side where applicable;
- the current Android platform tools;
- the toolchain/config expected by the pinned Lineage kernel branch;
- `dtc`/FDT tooling;
- Magisk boot-image tooling when preserving a rooted ramdisk; and
- enough disk space for the kernel source, output and boot work directories.

The canonical upstream source is:

```text
https://github.com/LineageOS/android_kernel_lge_sm8250.git
```

## Reproduce the source state

```bash
git clone https://github.com/LineageOS/android_kernel_lge_sm8250.git
cd android_kernel_lge_sm8250
git fetch --all --tags --prune
git checkout --detach 29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2
git status --short

git apply --check /path/to/0001-V60-performance-v1.patch
git am /path/to/0001-V60-performance-v1.patch

git apply --check /path/to/0002-arm64-dts-kona-enable-existing-670MHz-GPU-OPP-for-sp.patch
git am /path/to/0002-arm64-dts-kona-enable-existing-670MHz-GPU-OPP-for-sp.patch
```

After patch 2, inspect the modified `kona-v2-gpu.dtsi`. Do not continue if the
speed-bin block, order, voltages or bandwidth votes differ from the patch.

## Use the supplied portable workflow

The [workflow](workflow/README.md) contains the portable FDT tools, functional
tests, root-side runtime profiles and Termux launchers. The old private host
launchers are not public because they were bound to one handset's serial,
slot, boot hashes and local paths. [BUILD-AND-REPACK.md](BUILD-AND-REPACK.md)
documents their full logic with placeholders and explicit gates.

Run the portable tests before using the tools:

```bash
bash workflow/tests/syntax-check.sh
```

Set your own ADB serial, paths, target slot/partition and freshly measured
hashes in private shell variables. Never reuse a documented boot-image hash as
authorization to flash.

## Boot-image construction model

The active boot image can contain a concatenated DTB bundle and a Magisk
ramdisk. The reproducible workflow therefore:

1. reads and hashes the target boot partition;
2. unpacks it without normalizing header fields;
3. splits the concatenated FDT bundle;
4. identifies the exact indexed DTB used by the V60;
5. replaces only that matching entry;
6. proves every unaffected DTB entry is byte-identical;
7. preserves the original ramdisk/Magisk state;
8. rebuilds the boot image to the exact partition size; and
9. re-unpacks the output and checks component hashes before any flash.

The included `fdt-bundle.py` and tests implement the bundle operations. Do not
replace every DTB just because they share a platform ID.

## Flash and automatic rollback

The original process tested an isolated slot and prepared an automatic
rollback before reboot. A safe reproduction requires:

- verified pre-write boot backup;
- exact live target slot;
- new boot image exactly equal to the partition size;
- output hash recorded;
- known-good recovery/EDL access; and
- a rollback mechanism that does not depend on Android reaching the home
  screen.

Only then inspect and run the workflow's flashing stage. If your slot model
does not match the script's assumptions, adapt and review it first.

## Runtime profiles

The host-side build only makes capabilities available. The profile scripts
offer Daily, Power Save, CPU-MAX, GPU-MAX and ALL-MAX modes. Install them only
after the custom boot passes basic stability. Profiles require root and write
to sysfs; verify every node exists on the running kernel. Use the supplied
serial-bound [profile installer](workflow/README.md), which captures the
target's actual baseline and fails closed when restoration is incomplete.

The documented owner's conclusion is the practical default:

- **587 MHz**: daily/gaming recommendation;
- **670 MHz**: good for benchmarks and short bursts;
- **670 MHz gaming**: mildly unstable on the tested handset.

## Stress-test gates

Before calling a build stable:

1. 10 cold boots and 10 warm reboots;
2. screen-off deep sleep and wake cycles;
3. Wi-Fi, Bluetooth, LTE, GPS, audio, camera and fingerprint checks;
4. sustained CPU load while monitoring temperature/frequency;
5. repeated GPU benchmark loops at 587 MHz;
6. short, supervised 670 MHz loops with thermal and KGSL/GMU logs;
7. a real gaming session at the intended daily setting; and
8. successful rollback rehearsal.

Stop on reboot, visual corruption, KGSL/GMU fault, thermal runaway, storage
error, unexplained radio loss or camera-provider failure. This project never
removes Qualcomm thermal LMH/DCVSH protections.
