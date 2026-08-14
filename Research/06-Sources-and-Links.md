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

## Android host and APK tools

- Android SDK Platform Tools (`adb` and `fastboot`):
  <https://developer.android.com/tools/releases/platform-tools>
- Android `apksigner` reference:
  <https://developer.android.com/tools/apksigner>
- Android `zipalign` reference:
  <https://developer.android.com/tools/zipalign>

Use current official Platform Tools and bind every ADB/Fastboot command to the
intended device when more than one device is connected. For APK work, align
before signing and verify the final signature/certificate after every byte
change.

## Camera and media APIs

- Android Camera2 constrained-high-speed session API:
  <https://developer.android.com/reference/android/hardware/camera2/CameraConstrainedHighSpeedCaptureSession>
- Android MediaStore reference:
  <https://developer.android.com/reference/android/provider/MediaStore>
- Android shared-media guidance:
  <https://developer.android.com/training/data-storage/shared/media>
- AOSP camera documentation index:
  <https://source.android.com/docs/core/camera>

These references explain the standard Android paths used by the compatibility
port. They do not document LG's proprietary operation modes or vendor tags.

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

## Boot image, device tree and partition structure

- Magisk source and MagiskBoot provenance:
  <https://github.com/topjohnwu/Magisk>
- Devicetree specification:
  <https://devicetree-specification.readthedocs.io/en/stable/>
- UEFI GUID Partition Table format:
  <https://uefi.org/specs/UEFI/2.10/05_GUID_Partition_Table_Format.html>

The project's DTB tools operate on flattened-device-tree boundaries. GPT
validation and target resolution must still use the live handset map; a
specification explains the structure but does not make copied coordinates
portable.

## Project navigation and verification

- [Getting started by goal](../GETTING-STARTED.md)
- [Reproducibility contract](../REPRODUCIBILITY.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
- [Supply-chain verification](../SUPPLY-CHAIN.md)
- [Camera engineering notebook](04-Camera-Restoration/ENGINEERING-NOTEBOOK.md)
- [Performance engineering notebook](03-Performance-Kernel-Notebook.md)

## Tool/license note

Links identify upstream projects, not bundled proprietary binaries. Review
current upstream licenses and instructions. Never re-upload firmware, LG APKs,
firehose programmers or private phone partitions merely because a guide links
to an extraction method.
