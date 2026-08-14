# Getting Started by Goal

This repository covers several independent LG V60 jobs. Choose the smallest
path that matches your fault. Do not perform a partition write merely because
another project feature uses EDL.

## Before every path

1. Read [Safety First](DIY/00-SAFETY-FIRST.md).
2. Identify the exact V60 variant, current ROM, vendor build and active slot.
3. Run `adb devices -l` and bind every command to the V60's explicit serial.
4. Back up ordinary user data and media.
5. For any boot, firmware, modem or secure-state work, complete and verify the
   [recovery backup](DIY/01-Recovery-Backup/README.md) first.
6. Record hashes before and after each bounded change.

## Camera only

Use this path when LineageOS already boots and the goal is the restored LG
Camera. No EDL, modem, DRM, kernel or boot-partition change is required.

You need:

- a `timelm` LG V60 with a vendor camera stack compatible with the documented
  LineageOS 23.2/Android 16 baseline;
- the exact stock EA40g `LGCameraApp.apk` identified in
  [COMPATIBILITY.md](COMPATIBILITY.md);
- Python 3, the hash-pinned `bsdiff4` dependency, Android platform tools, and
  Android Build Tools for `apksigner`/`zipalign`; and
- a private backup of the currently installed camera package and normal DCIM
  media.

Follow [Reconstruct and Install Candidate 24](DIY/06-LG-Camera/README.md), then
run the complete [camera validation matrix](DIY/06-LG-Camera/VALIDATION.md).
The builder accepts only the exact stock input and promotes an output only
after its size and SHA-256 match Candidate 24.

Read the [camera engineering notebook](Research/04-Camera-Restoration/ENGINEERING-NOTEBOOK.md)
when diagnosing a mode-specific crash, lens-state problem, poor 1x dimensions,
8K stop behavior, settings-layout issue or Gallery/thumbnail confusion.

## Performance kernel only

Use this path only after the current ROM, radio, fingerprint and camera
provider are stable. It does not require a cross-flash, modem restore or DRMV2.

You need:

- the pinned Lineage kernel source and exact base commit;
- the exact running kernel configuration;
- AOSP Clang r563880c as documented;
- your own current boot-partition backup;
- a tested recovery/rollback route independent of Android booting; and
- a separate test slot or an equally strong rollback design.

Start with [Performance Kernel](DIY/05-Performance-Kernel/README.md), follow
[Build and Repack](DIY/05-Performance-Kernel/BUILD-AND-REPACK.md), and run the
portable workflow tests before touching a boot image. Daily/gaming use should
remain at 587 MHz unless the target independently proves long-term 670 MHz
stability.

## Fingerprint repair only

Use this path for immediate enrollment failure after a cross-flash when the
sensor illuminates and the Android biometric stack is present. First eliminate
display glass, protector, touch and sensor hardware issues.

The successful project result used the credited community DRMV2 image and
wrote only the live `drm` partition after:

- verifying the exact DRMV2 size and SHA-256;
- resolving `drm` from the target's current GPT;
- reading the complete immediate pre-write `drm` backup;
- proving source size equals the live target size;
- writing one target only; and
- reading it back byte-for-byte before reboot.

Follow [Fingerprint Recovery](DIY/04-Fingerprint/README.md). The historical
QSEE kernel experiments are research evidence, not prerequisites or fixes.

## Radio repair only

Use this path only when the OS boots but baseband/SIM/LTE broke after the
firmware transition and the handset's own original modem-slot backups exist.
The proven repair restored only same-handset `modem_a` and `modem_b`.

Do not substitute another phone's QCN, EFS, modemst, FSG, FTM, persist or
calibration data. Follow [Radio Recovery](DIY/03-Radio-Recovery/README.md) and
distinguish a missing baseband from an APN, carrier, band or SIM problem first.

## A001LG conversion case-study route

This is the only path that uses the full sequence:

1. [Safety model](DIY/00-SAFETY-FIRST.md)
2. [Full recovery backup](DIY/01-Recovery-Backup/README.md)
3. [A001LG global-bridge and Lineage case study](DIY/02-Crossflash-Lineage/README.md)
4. Baseline Lineage validation before root or custom kernel
5. [Radio recovery](DIY/03-Radio-Recovery/README.md) only if diagnosis matches
6. [Fingerprint recovery](DIY/04-Fingerprint/README.md) only if needed
7. [Performance kernel](DIY/05-Performance-Kernel/README.md) after stability
8. [LG Camera](DIY/06-LG-Camera/README.md) as an independent app-only stage
9. [Final end-to-end validation](DIY/07-Final-Validation.md)

The documented A001LG journey is evidence that the state transition can work,
not a universal sector-level recipe. Partition coordinates, slot state,
bootloader state and rollback inputs must come from the target handset.

## What to record privately

For each stage keep a case folder outside the Git checkout containing:

- model/variant, ROM/vendor fingerprints and active slot;
- source name, provenance, size and SHA-256;
- immediate pre-change backup size and SHA-256;
- exact target selected from the live device;
- post-change readback/hash or installed-artifact hash;
- test result and smallest relevant log excerpt; and
- rollback decision and artifact hash.

Do not publish device serials, telephony identifiers, raw partition maps,
QFIL session folders, APKs, user media or unredacted logs.
