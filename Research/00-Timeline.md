# Complete Project Timeline

## Starting state

- SoftBank Japan LG V60 A001LG, originally from the A001LG20s firmware family.
- Original aging battery produced apparent charge stalls and low input power.
- The owner wanted global firmware features, then LineageOS, while retaining
  cellular service, fingerprint, performance tuning and as much of LG Camera
  as possible.

## 2026-07-29: recovery foundation

- Entered Qualcomm EDL and read all 96 non-userdata partitions.
- Preserved GPT/boot-chain, both slot copies, modem/EFS-related state,
  DRM/persist/calibration, super and LG-specific partitions.
- Generated SHA-256 evidence for all 96 images and verified the copied set.
- This backup later made the radio and secure-state investigations possible.

## Late July 2026: global bridge and LineageOS

- Cross-flashed through the V600EA40g Android 13 global firmware family.
- Restored the intended production bootloader state after the temporary
  engineering-ABL work and repaired slot/AVB/GPT consistency.
- Installed matching Lineage recovery and LineageOS 23.2/Android 16.
- Android booted, but the radio/baseband path was not functional.
- Restored only same-handset A001LG `modem_a` and `modem_b`; baseband, SIM and
  LTE registration returned.

## 2026-08-02: performance kernel

- Pinned Lineage kernel base
  `29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2`.
- Created Performance V1 at
  `175901fa8aa5614cc50a695cdaa783a1bbfbba41`.
- Source audit found the vendor had already defined a 670 MHz `NOM_L1` GPU
  OPP; the speed-bin-0 table simply started at 587 MHz.
- Created GPU 670 revision
  `00d8f9c3262c90159d7bc9ea65fa6dd45797895e` and rebuilt the DTB bundle while
  preserving the working Magisk kernel/ramdisk.
- 670 MHz proved useful for benchmarking but mildly unstable in gaming;
  587 MHz became the daily/gaming recommendation.

## Fingerprint investigation and 2026-08-10 resolution

- Enrollment failed immediately after the global flash and persisted on
  LineageOS.
- Same-device original `p_persist_lg` and `drm` restoration did not solve it.
- Tested matched regional trusted-app files and five guarded QSEE kernel
  approaches. Early secure traffic improved, but a later Egistec command was
  still rejected.
- Community research located the DRMV2 calibration method credited on XDA.
- Read the live map, backed up `drm`, wrote DRMV2 to `drm` only, read it back
  byte-for-byte and confirmed GPT unchanged.
- Physical fingerprint enrollment and authentication immediately worked and
  have remained reliable. Replacement touch glass later required firmer
  pressure, a separate physical behavior.

## Charging closure

- Charging stalls were initially investigated as possible ROM/kernel policy.
- Replacing the old original battery resolved charging behavior.
- That result is consistent with battery aging, not proof that cell aging was
  the only possible cause.
- No charge-current bypass, thermal override or charging-kernel hack was
  accepted.

## 2026-08-10 through 2026-08-13: LG Camera restoration

- Extracted the exact EA40g LG Camera 9.91.3 package from owned firmware.
- Built an APK-only Lineage compatibility port; no camera/vendor/boot
  partition was flashed.
- Iterated through application/framework compatibility, physical lens
  mapping, settings layout, Manual/Portrait/Sticker/Story, video profiles,
  4K60, 8K, photo sizing and regression work.
- Candidate 23 passed the broad release matrix but exposed an apparent 8K
  stop freeze and an unwanted full Settings screen for resolution changes.
- Candidate 24 restored the complete post-stop UI state and the in-camera
  HD/FHD/FHD60/4K/4K60/8K quick strip.
- Candidate 24 passed 15 cold launches, eight Photo/Video cycles, three
  consecutive 8K stop/save cycles, sustained 8K, 4K60, Gallery handoff and
  final thermal checks.

## 2026-08-14: consolidation and public release preparation

- Consolidated LG-related material into one private project master while
  retaining strict recovery/evidence boundaries.
- Replayed all eight kernel patches against the pinned base; final tree match
  passed.
- Created this public repository with no APK, firmware, partition image,
  device serial, IMEI, QCN/EFS, private DRM/persist, user media or raw private
  logs.
- Verified that the public camera delta reconstructs the exact Candidate 24
  APK from the exact stock input.
- Imported and integrity-checked two additional private engineering handoffs.
  Their raw scripts/evidence remained private; the reusable EDL transaction
  design was converted into sanitized public documentation.
