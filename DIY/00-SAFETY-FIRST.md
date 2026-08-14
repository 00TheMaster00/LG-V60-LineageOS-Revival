# Safety First

LG V60 recovery work can cross three different risk levels. Know which one you
are entering.

## Level 1: application-only

Camera APK reconstruction and installation do not write a phone partition.
They can still cause app crashes or data loss if the existing app is
uninstalled without a backup.

## Level 2: boot/kernel

Kernel and DTB work writes a boot slot. A bad image can stop that slot from
booting. Keep the other slot untouched, back up the target slot, and know how
to select the rollback slot before proceeding.

## Level 3: EDL, cross-flash and calibration

QFIL/Firehose can write almost any UFS partition, including the boot chain,
radio identity and calibration. A wrong programmer, LUN, sector range or
foreign partition image can hard-brick the phone or destroy functionality
that a KDZ cannot recreate.

## Mandatory stop conditions

Stop immediately if any of these is true:

- the target is not positively identified as the intended LG V60;
- more than one ADB/Fastboot device is visible and the command lacks an
  explicit serial;
- the live QFIL partition map does not match the map used to prepare a write;
- a source file has the wrong size or SHA-256;
- a pre-write readback cannot be completed;
- the Qualcomm programmer is not known to support LG SM8250 UFS;
- the requested procedure asks for someone else's FTM, persist, DRM, QCN,
  modem-EFS or identity data;
- the active slot, AVB state, anti-rollback implications or rollback route are
  unknown;
- power, cable or USB connectivity is unreliable.

## Never publish or exchange

Keep these private even when asking for help:

- QCN/NV exports and IMEI-bearing diagnostics;
- `ftm`, `mpt`, `persist`, `p_persist_lg`, `drm`, `sid_*`;
- `fsg`, `fsc`, `modemst1`, `modemst2`, `mdm1m9kefs*`;
- raw userdata, QFIL session directories and unredacted property/log dumps;
- private boot images containing a personal Magisk installation.

## Recovery is not the same as substitution

Restoring your own bytes to the same partition is recovery. Copying another
phone's secure or identity state is substitution and can break calibration,
radio identity, Widevine, fingerprints or legal network operation. This
project supports only owner-derived recovery data.

