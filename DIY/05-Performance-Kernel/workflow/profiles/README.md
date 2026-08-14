# Final runtime profiles

These are the final profile files extracted from the successful no-reboot deployment.

- `profile.sh`: Daily, Power Save, CPU-MAX, GPU-MAX, and status logic.
- `gpubw.sh`: Qualcomm GPU-bandwidth automatic/max voting.
- `wrapper.sh`: stable public interface used by Termux shortcuts.
- `all-max.sh`: compatibility wrapper for ALL-MAX.

Validated modes:

| Mode | CPU | GPU | GPU bandwidth | Android low power |
|---|---|---|---|---|
| Daily | adaptive, normal maxima | adaptive 305–587 MHz | automatic 0–7980 | off |
| Power Save | capped | adaptive up to 400 MHz | automatic | on |
| CPU-MAX | all clusters locked to maxima | Daily/adaptive | automatic | off |
| GPU-MAX | Daily CPU policy | pinned 670 MHz | pinned 7980 | off |
| ALL-MAX | CPU maxima | pinned 670 MHz | pinned 7980 | off |

The Daily mode restores the captured base configuration. Some transient CPU/input-boost nodes may be changed again by Android immediately after the write, which is why the final validator checks both stable state and restoration writes.
