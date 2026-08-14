# A001LG to Global Firmware to LineageOS

This is a documented case study, not a one-click flasher. It separates the
parts reproduced exactly from the parts that depend on model, current
firmware, bootloader state and live GPT layout.

## Proven outcome

The documented handset started as a SoftBank A001LG on A001LG20s. It booted a
V600EA40g global firmware bridge, then LineageOS 23.2/Android 16 for `timelm`.
The bridge initially had no usable baseband; cellular service was recovered
later from the handset's own A001LG `modem_a` and `modem_b` backups.

## Why this repository does not contain blind flash commands

The original work used a combination of LG tooling, an engineering ABL,
slot/GPT repair and recovery flashing. A raw sector write copied from one
phone can destroy the partition table or boot chain of another. The surviving
evidence proves the state transitions and final images, but it does not prove
that one universal command sequence is safe for every V60 variant.

Use the current official LineageOS `timelm` instructions for the Lineage
installation stage. Use this case study to understand prerequisites,
checkpoints and recovery planning around an A001LG conversion.

## Stage 1: establish the immutable baseline

1. Complete [the recovery backup](../01-Recovery-Backup/README.md).
2. Record model, device, firmware fingerprint, active slot, lock state,
   verified-boot state and baseband.
3. Export the live GPT for every UFS LUN.
4. Confirm you possess and can verify the original A001LG boot-chain and radio
   partitions before introducing global firmware.
5. Hash every input firmware package. Never trust a renamed KDZ.

The EA40g bridge package used in the documented project had SHA-256:

```text
0121958707A73152503769913C1B724317A9CC013164361D469339CA40C3ACDE
```

This hash identifies the tested input; it is not an endorsement of an
untrusted download bearing the same name.

## Stage 2: global-firmware bridge

The proven checkpoint after the global bridge was:

```text
product/device: timelm family
vendor: V600EA40g
Android: 13
active slot: A
bootloader: unlocked
verified boot: orange
```

At this checkpoint, do not proceed merely because Android boots. Test:

- touch, display, storage and USB;
- Wi-Fi and Bluetooth;
- baseband property, SIM detection and cellular registration;
- both slots' boot-chain consistency; and
- the ability to return to EDL and read the live partition map.

The documented handset did **not** have working cellular service here. That
was treated as a separate radio-compatibility problem, not hidden by further
flashing.

## Stage 3: bootloader and slot integrity

Before installing recovery:

1. Re-read `abl_a`, `abl_b`, `boot_a`, `boot_b`, `vbmeta_a`, `vbmeta_b` and
   both GPT copies.
2. Hash and label the reads by slot.
3. Confirm the live active slot with both Android properties and bootloader
   tooling.
4. Restore the intended production ABL after any temporary engineering ABL
   operation.
5. Confirm the device still enumerates in fastboot/fastbootd and EDL.

Do not leave an engineering bootloader in daily use. Do not assume slot B is a
backup unless its contents have been read and verified.

## Stage 4: install LineageOS using the current device guide

Lineage builds and recovery requirements change. Follow the current official
`timelm` page rather than copying the project's July 2026 package names:

- <https://wiki.lineageos.org/devices/timelm/>

At a high level, the proven flow was:

1. download the matching Lineage recovery and ROM from official infrastructure;
2. verify published checksums/signatures;
3. flash the recovery components exactly as the current device guide states;
4. boot recovery immediately, without allowing an incompatible OS to replace it;
5. format data only when the official guide requires it and only after backups;
6. sideload the matching Lineage package;
7. install add-ons in the same recovery session only when their instructions require it;
8. boot Android and finish basic setup before adding Magisk or a custom kernel;
9. record the new active slot and build fingerprint; and
10. test USB, Wi-Fi, Bluetooth, audio, sensors and camera-provider enumeration.

## Stage 5: isolate post-install faults

Fix one subsystem at a time:

- missing baseband/SIM: [Radio Recovery](../03-Radio-Recovery/README.md);
- enrollment fails immediately: [Fingerprint](../04-Fingerprint/README.md);
- stock AOSP camera limitations: [LG Camera](../06-LG-Camera/README.md);
- performance tuning: only after a stable baseline, use
  [Performance Kernel](../05-Performance-Kernel/README.md).

Do not combine radio, DRM, camera and kernel writes into one experiment. A
single-variable workflow is slower for one evening and far faster for finding
the real cause.

## Rollback plan

Before every write, record:

- target LUN, label, start sector, count and byte size from the live map;
- source file name, SHA-256 and provenance;
- pre-write image name and SHA-256;
- expected post-write SHA-256; and
- the exact next boot/recovery test.

If a checkpoint fails, stop and restore only the component changed in that
checkpoint. A complete original backup is the final safety net, not the first
reaction to a local problem.

