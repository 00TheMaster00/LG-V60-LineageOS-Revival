# Final runtime profiles

These are the final profile files extracted from the successful no-reboot deployment.

- `profile.sh`: Daily, Power Save, CPU-MAX, GPU-MAX, and status logic.
- `gpubw.sh`: Qualcomm GPU-bandwidth automatic/max voting.
- `wrapper.sh`: stable public interface used by Termux shortcuts.
- `all-max.sh`: compatibility wrapper for ALL-MAX.
- `capture-baseline.sh`: captures the target's writable CPU/GPU/scheduler
  state before the first profile is applied.
- `install.sh`: root-side, hash-checked installation helper.

Validated modes:

| Mode | CPU | GPU | GPU bandwidth | Android low power |
|---|---|---|---|---|
| Daily | adaptive, normal maxima | adaptive 305–587 MHz | automatic 0–7980 | off |
| Power Save | capped | adaptive up to 400 MHz | automatic | on |
| CPU-MAX | all clusters locked to maxima | Daily/adaptive | automatic | off |
| GPU-MAX | Daily CPU policy | pinned 670 MHz | pinned 7980 | off |
| ALL-MAX | CPU maxima | pinned 670 MHz | pinned 7980 | off |

The Daily mode restores the captured base configuration. A missing, empty,
unsafe or stale baseline is now a hard failure: no mode is promoted and the
script exits nonzero. Failed sysfs writes also prevent promotion. GPU-MAX and
ALL-MAX remain in a pending state until the separate GPU-bandwidth stage
succeeds.

## Install and capture the baseline

From PowerShell on the host, explicitly select the V60 serial. This matters
when a second ADB device is attached:

```powershell
adb devices -l
.\Install-V60Profiles.ps1 -Serial REPLACE_WITH_LG_V60_SERIAL
```

The host installer refuses a non-`timelm` target, requires root, stages only
this profile directory under `/data/local/tmp`, verifies every copied script
by SHA-256, installs to `/data/adb/v60profiles`, and captures the baseline on
first install. An existing baseline is preserved during upgrades.

Inspect the on-device files before using a performance mode:

```powershell
adb -s REPLACE_WITH_LG_V60_SERIAL shell su -c `
  'cat /data/adb/v60profiles/baseline.meta; cat /data/adb/v60profiles/baseline.nodes'
adb -s REPLACE_WITH_LG_V60_SERIAL shell su -c `
  '/data/adb/v60profiles/wrapper.sh status'
```

To recapture intentionally, apply Daily, confirm the phone is truly in the
desired normal state, then run `capture-baseline.sh --force`. Never recapture
while CPU-MAX, GPU-MAX, ALL-MAX or Power Save is active.

Some transient CPU/input-boost nodes may be changed again by Android
immediately after a write, which is why the final validator checks both stable
state and restoration writes.
