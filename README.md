# LG V60 LineageOS Revival

[![Validate public release](https://github.com/The1-Master/LG-V60-LineageOS-Revival/actions/workflows/ci.yml/badge.svg)](https://github.com/The1-Master/LG-V60-LineageOS-Revival/actions/workflows/ci.yml)

Canonical repository: <https://github.com/The1-Master/LG-V60-LineageOS-Revival>

An evidence-backed, backup-first project for keeping the LG V60 useful on
LineageOS. It documents one complete A001LG-to-Lineage journey and packages
the reusable work as reproducible tools instead of another phone's private
partition images.

The project has two paths:

| Path | Use it when you want to... |
|---|---|
| [Do It Yourself](DIY/README.md) | back up a V60, understand the cross-flash/Lineage sequence, repair common radio or fingerprint failures from your own backups, build the performance kernel, or reconstruct the tested LG Camera port |
| [Research & Findings](Research/README.md) | understand what was tried, what worked, what failed, why the fixes work, and which limitations remain |

## What this project achieved

On the documented SoftBank A001LG handset, the work:

- captured and hash-verified 96 original partitions before modification;
- bridged through V600EA40g and installed LineageOS while preserving a
  practical rollback route;
- recovered LTE by restoring only the handset's own original `modem_a` and
  `modem_b` images;
- repaired fingerprint enrollment using the community DRMV2 calibration
  method, with a pre-write backup and byte-for-byte readback;
- produced reproducible Performance V1 and GPU 670 MHz kernel changes;
- adapted LG Camera 9.91.3 for LineageOS 23.2/Android 16, including stable
  main/ultrawide/front capture, Manual Camera and Video, Portrait fallback,
  Sticker, Story, 1080p60, 4K60, 1080p240, real 8K stop/save, a quick
  resolution strip, and improved main-camera output dimensions;
- traced the original charging fault to the aged battery rather than a kernel
  charging policy; battery replacement resolved it.

## Start here

1. Read [the safety model](DIY/00-SAFETY-FIRST.md).
2. Check [compatibility](COMPATIBILITY.md).
3. Make and verify [your own recovery set](DIY/01-Recovery-Backup/README.md).
4. Choose only the track you need:
   - [Cross-flash and Lineage case study](DIY/02-Crossflash-Lineage/README.md)
   - [Radio recovery](DIY/03-Radio-Recovery/README.md)
   - [Fingerprint recovery](DIY/04-Fingerprint/README.md)
   - [Performance kernel](DIY/05-Performance-Kernel/README.md)
   - [LG Camera Candidate 24](DIY/06-LG-Camera/README.md)

Do not start with a write command. Start with a complete, verified backup and
a partition map captured from the exact handset being modified.

## Important distribution boundary

This repository intentionally does **not** contain:

- LG Camera APKs or LG firmware/KDZ files;
- boot, modem, DRM, persist, FTM, EFS, super or userdata images;
- QCN/NV exports, IMEI, device serials or private QFIL logs;
- another person's calibration or identity data.

The camera builder requires the user to supply the exact EA40g LG Camera APK
and reconstructs the tested result locally. Recovery instructions require
each user to supply only images read from their own phone.

## Proven versus portable

The complete end-to-end journey was proven on one A001LG. The camera release
was proven on LineageOS 23.2 (Android 16) with the matching V60 vendor stack.
The kernel work is pinned to a recorded Lineage kernel base. That is strong
evidence, not permission to assume that every V60 variant, ROM build, slot or
partition map is identical.

Read [DISCLAIMERS.md](DISCLAIMERS.md), [PRIVACY.md](PRIVACY.md), and
[CREDITS.md](CREDITS.md) before reproducing or redistributing the work.

## Project status

The documented handset is working with charging restored after battery
replacement, cellular service restored, fingerprint enrollment/authentication
working, Candidate 24 camera installed, and the performance work preserved.
For daily gaming, 587 MHz remains the conservative GPU choice; 670 MHz is a
benchmark/short-burst option because mild gaming instability was observed.

This is an independent community project. It is not affiliated with or
endorsed by LG, Qualcomm, LineageOS, XDA, or the cited contributors.
