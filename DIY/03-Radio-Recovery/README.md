# Radio Recovery from Your Own A001LG Backup

Use this track only when the global/Lineage installation boots but the
baseband is missing or the SIM cannot register, and only when you possess the
original radio images read from the same handset.

## Proven fix

On the documented A001LG, restoring its own original `modem_a` and `modem_b`
images recovered baseband reporting, SIM detection and LTE registration. No
other person's QCN, EFS, modemst, FSG or identity partition was used. The
unrelated UFS LUN containing identity/calibration data remained unchanged.

## Diagnose before writing

```powershell
adb devices -l
adb -s SERIAL shell getprop gsm.version.baseband
adb -s SERIAL shell getprop persist.radio.multisim.config
adb -s SERIAL shell dumpsys telephony.registry
adb -s SERIAL shell logcat -b radio -d > radio-before.txt
```

Sanitize `radio-before.txt` before sharing it; radio logs can contain phone
numbers, operator identifiers and other private data.

Do not use this procedure for an ordinary APN problem, a disabled SIM, a
network outage or an unsupported carrier band.

## Pre-write checks in QFIL

1. Enter EDL and confirm Qualcomm 9008 enumeration.
2. Open QFIL in Flat Build mode with UFS storage selected.
3. Load the known-compatible firehose and open Partition Manager.
4. Export the live partition map.
5. Locate `modem_a` and `modem_b` by **label**, not by remembered row number.
6. Record each live LUN, start sector, sector count and byte size.
7. Read both current modem partitions and hash them.
8. Verify each original backup size equals its target's live byte size.
9. Verify the original backup hashes against your pre-crossflash manifest.

Stop on any size, label, LUN or hash mismatch.

## Write one slot at a time

For `modem_a`, then separately for `modem_b`:

1. Select the exact live partition row.
2. Open **Manage Partition Data**.
3. Choose **Load Image**.
4. Select only the matching same-handset backup.
5. Wait for a clean completion message.
6. Immediately choose **Read Data** on that same row.
7. Rename the readback and calculate SHA-256.
8. Require the readback hash to equal the source image hash.

Do not write `modemst1`, `modemst2`, `fsg`, `fsc`, QCN or EFS merely because
they are radio-related. The proven repair needed only the two modem firmware
slots. Expanding the write set increases identity and calibration risk.

## Boot validation

1. Exit Partition Manager cleanly and reboot.
2. Wait several minutes for the radio stack to initialize.
3. Re-run the baseband and telephony commands above.
4. Confirm SIM state in Android Settings.
5. Test an outgoing call where lawful, SMS, mobile data and airplane-mode
   recovery.
6. Reboot once and repeat mobile-data registration.

Record the result without publishing IMEI, phone number, IMSI or raw radio
logs.

## Failure handling

- Still no baseband: compare the live vendor/firmware combination with the
  known working bridge and collect sanitized radio logs.
- Baseband exists but no service: check APN, carrier provisioning, bands and
  SIM state before any more partition writes.
- QFIL readback mismatch: do not boot; re-read the live map and investigate
  the programmer/cable/storage path.
- Wrong source phone: stop. Cross-device modem/EFS transplantation is outside
  this project and can corrupt calibration or identity.

