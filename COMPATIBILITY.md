# Compatibility

## Fully documented baseline

| Component | Proven baseline |
|---|---|
| Original handset | SoftBank A001LG, original build family A001LG20s |
| Bridge firmware | LM-V600EA / V600EA40g Android 13 |
| Custom ROM | LineageOS 23.2, Android 16, `timelm` |
| Root during development | Magisk |
| Camera input | EA40g `LGCameraApp.apk`, SHA-256 `65D69A9E0DB652F43E232EC4AE86DCFC11AC688E324C5103CAAB1FECB27807E8` |
| Camera output | Candidate 24, SHA-256 `E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71` |
| Kernel base | `29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2` |

## What is likely portable

- The backup/verification discipline applies to every V60 variant.
- The camera patch may work on another `timelm` ROM exposing a sufficiently
  similar LG/Qualcomm vendor camera stack, but only the baseline above is
  proven.
- The kernel patch can be reviewed and rebased onto related SM8250 Lineage
  trees, but the recorded commit is the only exact application base.
- DRMV2 is a community V60 method, but partition coordinates must always come
  from the target's live map.

## What is not assumed portable

- A001LG sector coordinates, GPT attributes and slot state;
- the A001LG original modem images;
- an AT&T/T-Mobile/Verizon erase list applied to a Japanese model;
- a boot image built for another ROM version or Magisk state;
- foreign DRM, persist, FTM, EFS or QCN data;
- stock-only camera graphs such as true ToF Portrait, RAW/DNG and 64 MP
  remosaic.

Open an issue with sanitized model, ROM build, vendor build and observed
result when testing another configuration. Do not attach partitions or QCNs.

