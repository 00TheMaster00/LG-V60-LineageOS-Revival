# Sources and Community Links

## LineageOS and source

- LineageOS LG V60 (`timelm`) device page:
  <https://wiki.lineageos.org/devices/timelm/>
- Lineage LG V60 device tree:
  <https://github.com/LineageOS/android_device_lge_timelm>
- Lineage LG SM8250 kernel:
  <https://github.com/LineageOS/android_kernel_lge_sm8250>
- Lineage project and downloads:
  <https://lineageos.org/>

Use the current device-page instructions for ROM installation. This project
pins historical commits only for reproducibility.

## Fingerprint and recovery community work

- XDA thread documenting the V60 DRMV2 method and its credits:
  <https://xdaforums.com/t/discontinued-rom-aosp-14-11022025-gapps-unofficial-timelm-evolution-x-9-9.4718320/>
- XDA LG V60 full-flash backup/restore discussion by netmsm and contributors:
  <https://xdaforums.com/t/tutorial-full-flash-backup-and-restore.4362809/>

The DRMV2 thread credits `@Grendly_foo` and `@Astrum_Visconti` for the
factory-level fingerprint work. This repository documents an independently
verified application of that community fix; it does not claim invention of
DRMV2.

## Firmware and dynamic-partition extraction

- AOSP dynamic partition tools (`lpunpack`, `lpmake`, related sources):
  <https://android.googlesource.com/platform/system/extras/+/refs/heads/master/partition_tools/>
- AOSP dynamic partitions overview:
  <https://source.android.com/docs/core/ota/dynamic_partitions>
- SRLabs Android firmware extractor, including KDZ/super support:
  <https://github.com/srlabs/extractor>

## Tool/license note

Links identify upstream projects, not bundled proprietary binaries. Review
current upstream licenses and instructions. Never re-upload firmware, LG APKs,
firehose programmers or private phone partitions merely because a guide links
to an extraction method.

