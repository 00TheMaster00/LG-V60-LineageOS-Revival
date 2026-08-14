# Fingerprint Recovery on LineageOS

Use this track when enrollment reaches the sensor screen and then immediately
reports **Can't complete fingerprint setup**, **Something went wrong**, or an
instant timeout after a global cross-flash.

## First separate hardware from provisioning

Before EDL work:

1. Clean the display over the optical sensor.
2. Remove a badly fitted protector for one test.
3. Confirm the fingerprint icon/illumination appears when pressed.
4. Confirm touch works in the same display region.
5. If the screen or touch glass was replaced, test with firm, even pressure.
6. Reboot and delete any partial fingerprint entries.
7. Capture a sanitized log while starting enrollment:

```powershell
adb -s SERIAL logcat -c
adb -s SERIAL shell am start -a android.settings.FINGERPRINT_ENROLL
# Touch once, wait for the failure, then:
adb -s SERIAL logcat -d > fingerprint-enrollment.txt
```

The repaired project handset later received replacement touch glass. Its
fingerprint authentication remains reliable but requires somewhat harder
pressure. That is a physical/display-stack behavior, not evidence that the
software repair failed.

## What was tried before the successful fix

The following were useful diagnostics but were **not** the final repair:

- restoring the handset's own original `p_persist_lg`;
- restoring the handset's own original `drm`;
- testing matched regional fingerprint trusted-app files at runtime; and
- five guarded QSEE transport/buffer kernel experiments.

The experiments proved that the sensor, illumination, HAL startup and early
secure commands were alive. A later Egistec secure command was rejected. The
decisive repair was the community DRMV2 calibration/provisioning image written
to `drm` only.

## Obtain and verify DRMV2

This repository does not redistribute `DRMV2.img`. Obtain it from the original
community/XDA source and preserve that source's credits:

- <https://xdaforums.com/t/discontinued-rom-aosp-14-11022025-gapps-unofficial-timelm-evolution-x-9-9.4718320/>

The exact image used successfully had:

```text
file size: 14,680,064 bytes
SHA-256: C0FF080DA7CA569BCA190558DB444F33004D8BA58245942496495C9EDBDDF24C
```

Verify locally:

```powershell
(Get-Item .\DRMV2.img).Length
(Get-FileHash -Algorithm SHA256 .\DRMV2.img).Hash
```

Stop if either value differs. A matching hash proves byte identity with the
tested community file; it does not prove a download site is trustworthy.

## Mandatory backup and mapping

Before the write, read and hash at least:

- the live `drm` partition through EDL;
- `persist`;
- `p_persist_lg`; and
- both GPT copies for the LUN containing `drm`.

Keep those images private. DRM/persist content can carry device-specific
secure state or calibration.

The documented A001LG had this live mapping:

```text
UFS LUN: 0
partition label: drm
start sector: 8198
sector count: 3584
logical sector size: 4096 bytes
partition bytes: 14,680,064
```

These numbers are **evidence from one handset, not copy-and-paste targets**.
Export the target handset's live GPT and locate `drm` by label. Require its
computed byte size to equal the DRMV2 file size. If the LUN, label, size or
range is uncertain, stop.

## Exact QFIL write workflow

1. Charge the handset above 50% and close software holding ADB/USB.
2. Enter EDL manually and confirm Qualcomm HS-USB QDLoader 9008.
3. Open QFIL, select **Flat Build**, and set storage to **UFS**.
4. Load the already proven compatible firehose programmer.
5. Open **Tools > Partition Manager** and allow a fresh live-table read.
6. Save the table and locate the row whose label is exactly `drm`.
7. Record LUN, start sector, sector count and sector size.
8. Compute `sector_count * sector_size`; require 14,680,064 bytes for the
   tested DRMV2 image.
9. Open **Manage Partition Data** for `drm`.
10. Select **Read Data**. Rename the result
    `drm-edl-immediately-before-drmv2.img` and hash it.
11. Reconfirm the selected row still says `drm`.
12. Select **Load Image** and choose the verified `DRMV2.img`.
13. Wait for a clean completion message. Do not disconnect during the write.
14. Without leaving the row, select **Read Data** again.
15. Rename the result `drm-after-drmv2-readback.img`.
16. Require its file size and SHA-256 to equal the source DRMV2 values above.
17. Re-read or hash the LUN's GPT header and confirm it is unchanged.
18. Exit Partition Manager cleanly and reboot.

No modem, EFS, persist, boot, super or userdata partition is part of this
write. If QFIL highlights anything except `drm`, cancel.

## Android validation

1. Wait for Android to finish booting.
2. Open **Settings > Security and privacy > Device unlock > Fingerprint**.
3. Start a new enrollment and complete a full finger.
4. Lock the device and authenticate at least ten times.
5. Reboot and authenticate again.
6. Test one app that uses Android biometric authentication.

On the documented handset, the post-write EDL readback matched DRMV2 exactly,
the GPT header was unchanged, the HAL started, physical enrollment completed,
and fingerprint continued working on LineageOS.

## Rollback and failures

- Readback mismatch: do not boot; investigate cable/programmer/mapping and
  retain both reads.
- Phone boots but enrollment still fails: restore only your immediate
  pre-write `drm` image after verifying its target map, then collect logs.
- No illumination/touch response: investigate display/sensor hardware before
  more secure-partition writes.
- Another phone's DRM/persist image: never use it.

The ordered experimental kernel patches are retained under
`Research/02-Fingerprint-Investigation/experiments/` for research provenance.
They are not required for the working DRMV2 result.

