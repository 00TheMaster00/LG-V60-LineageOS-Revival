# Recovery Backup: Before You Change Anything

This is the mandatory first stage. The documented A001LG was protected by a
96-partition, non-`userdata` backup. All 96 files were hashed and then
re-hashed before later recovery work.

This guide uses QFIL terminology because that was the proven route. QFIL UI
labels vary slightly by QPST release. Stop if the live partition map does not
match the image you intend to read or write.

## What you need

- Windows with a working Qualcomm HS-USB QDLoader 9008 driver;
- QPST/QFIL obtained from a source you trust;
- a firehose programmer that is already known to communicate with your exact
  LG V60/SM8250 configuration;
- a reliable USB cable, preferably connected directly to the PC;
- at least 40 GiB free for a practical non-userdata set, and much more if you
  also choose to read `userdata`;
- battery above 50%; and
- a second copy destination that is not the phone.

The repository does not redistribute a programmer, KDZ, partition image or
QPST package. Verify the provenance of every binary you obtain.

## Phase A: record the Android state

With the phone booted and USB debugging authorized, replace `SERIAL` with the
serial printed by `adb devices -l`:

```powershell
adb devices -l
adb -s SERIAL shell getprop ro.product.manufacturer
adb -s SERIAL shell getprop ro.product.model
adb -s SERIAL shell getprop ro.product.device
adb -s SERIAL shell getprop ro.boot.slot_suffix
adb -s SERIAL shell getprop ro.build.fingerprint
adb -s SERIAL shell getprop gsm.version.baseband
adb -s SERIAL shell getprop ro.boot.verifiedbootstate
adb -s SERIAL shell getprop ro.boot.flash.locked
```

Save the output outside the repository. Never publish the ADB serial, IMEI,
phone number, IMSI, Wi-Fi MAC, Bluetooth MAC, QCN or NV/EFS contents.

## Phase B: enter EDL and prove read access

1. Close LGUP, ADB shells and any program that might hold the USB interface.
2. Put the handset into EDL manually using the method appropriate to the
   device. ADB reboot commands are not reliable on every boot chain.
3. Open Device Manager and confirm **Qualcomm HS-USB QDLoader 9008** appears.
4. Open QFIL and select **Flat Build**.
5. Set **Storage Type** to **UFS** before opening Partition Manager.
6. Select the known-compatible firehose programmer.
7. Choose **Tools > Partition Manager**. Allow QFIL to read the live table.
8. Export or screenshot every LUN and partition row before reading data.

If QFIL cannot enumerate the live table, stop. Do not try a write to test the
connection.

## Phase C: read and name the images

For every live partition row:

1. Select the row in Partition Manager.
2. Choose **Manage Partition Data**.
3. Choose **Read Data**.
4. Wait for QFIL to report completion.
5. Find the newly created `ReadData_ufs_...bin` file in QFIL's output folder.
6. Immediately copy it to the backup folder and rename it using both the LUN
   and label, for example `lun1_modem_a.img`.
7. Record the live start sector, sector count and logical sector size in your
   private notes.
8. Confirm the file size equals `sector_count * logical_sector_size`.

Repeat one partition at a time. Never rely on QFIL's generated filename after
several reads; it is too easy to associate the wrong file with a label.

## Minimum critical set

A full non-userdata set is preferred. At minimum, preserve every partition in
[critical-partitions.txt](critical-partitions.txt), including both A/B copies
where they exist. Especially important groups are:

- GPT/partition-table copies for every populated LUN;
- boot chain: `xbl`, `xbl_config`, `abl`, `tz`, `hyp`, `devcfg`, `aop`,
  `qupfw`, `keymaster`, `cmnlib`, and `cmnlib64`;
- Android boot: `boot`, `dtbo`, `vbmeta`, `vendor_boot` and `recovery` when
  present;
- radio: `modem_a`, `modem_b`, `fsg`, `fsc`, `modemst1`, `modemst2` and any
  device-specific M9K/EFS partitions;
- calibration/security: `drm`, `persist`, `p_persist_lg`, `ftm` and `mpt`;
- dynamic partitions: `super`;
- LG-specific metadata and misc partitions; and
- `userdata` only if you consciously accept its size and privacy sensitivity.

Never share EFS, QCN, DRM, persist, FTM, MPT or userdata images. They may
contain identity, calibration, account or security data.

## Phase D: create and verify a manifest

From this repository's root:

```powershell
python DIY/01-Recovery-Backup/tools/hash_directory.py `
  --directory "D:\LGV60-private-backup" `
  --output "D:\LGV60-private-backup\SHA256SUMS.csv"

python DIY/01-Recovery-Backup/tools/verify_manifest.py `
  --manifest "D:\LGV60-private-backup\SHA256SUMS.csv"
```

Run the verifier again after copying the backup to a second physical disk.
The manifest contains only file names, sizes and hashes; keep it private when
the names expose device-specific information.

## Recovery-set acceptance checklist

- QFIL enumerated every expected UFS LUN.
- Every read completed without Sahara, Firehose or storage errors.
- Every file size matches the live partition-table size.
- Both slot copies were captured where present.
- GPT/partition maps were saved before any write.
- The manifest verifier reports zero missing, changed or extra files.
- A second offline copy verifies against the same manifest.
- The backup has never been added to Git.

Only after every item passes should you continue to cross-flash or recovery.

