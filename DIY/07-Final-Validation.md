# Final End-to-End Validation

Run this after the phone has booted the intended Lineage build and before
calling the conversion complete. Test the unmodified Lineage baseline first,
then radio/fingerprint, then kernel, then Camera.

## Identity and recovery

- [ ] Every ADB command uses the LG V60's explicit serial.
- [ ] Model/device/vendor/ROM fingerprints are recorded privately.
- [ ] Current active slot and boot partition are known.
- [ ] All 96 original non-userdata reads or an equivalent complete set still
      verify against the original manifest.
- [ ] Current GPT maps and immediate pre-write backups are stored offline.
- [ ] EDL, recovery and bootloader access have been rehearsed.

## Core device

- [ ] 10 cold boots and 10 warm reboots.
- [ ] Display, touch, rotation, proximity, vibration and buttons.
- [ ] USB data, charging, file transfer and ADB authorization.
- [ ] Wi-Fi association/roaming and Bluetooth audio.
- [ ] Speaker, earpiece, microphones and headphone path if used.
- [ ] GPS lock and compass/sensor behavior.
- [ ] Screen-off deep sleep, alarm wake and normal idle drain.

## Radio

- [ ] Non-empty baseband property.
- [ ] SIM detected after boot and after airplane-mode cycle.
- [ ] Outgoing/incoming call where lawful, SMS and mobile data.
- [ ] LTE registration survives a reboot.
- [ ] No raw telephony log is added to the public repository.

## Fingerprint

- [ ] One complete new enrollment.
- [ ] At least 10 lock-screen authentications.
- [ ] Authentication after reboot.
- [ ] One Android biometric app prompt.
- [ ] Any replacement-glass pressure difference documented as physical.

## Battery and charging

- [ ] Known-good cable and charger.
- [ ] Charge increases through the previously failing percentage range.
- [ ] No charge/thermal safety override is installed.
- [ ] Battery temperature remains normal during camera and performance tests.

## Performance kernel

- [ ] Running boot partition hash equals the intended locally built image.
- [ ] Kernel release and source/patch provenance are recorded.
- [ ] GPU frequency table includes 670 and 587 in the expected order.
- [ ] Daily profile caps at 587 MHz.
- [ ] CPU/GPU stress shows no reboot, KGSL/GMU fault or thermal runaway.
- [ ] 670 MHz is classified benchmark-only unless the target independently
      passes extended gaming stability.
- [ ] Rollback image/hash and recovery route are still available.

## Camera

- [ ] Installed APK SHA-256 equals Candidate 24.
- [ ] All items in [LG Camera validation](06-LG-Camera/VALIDATION.md) tested.
- [ ] 8K Stop returns the complete UI and saves a playable exact item.
- [ ] Resolution badge expands in-camera instead of opening Settings.
- [ ] Main and ultrawide output dimensions match their physical sensors.
- [ ] Unproven modes are reported as unproven, not “working” from UI entry.

## Privacy/publication

- [ ] No APK, KDZ, partition image, QCN, EFS, DRM, persist, FTM, MPT,
      userdata, private key, device serial, IMEI, phone number or user media.
- [ ] Logs/screenshots are sanitized or omitted.
- [ ] `python tools/audit_public_release.py` passes.
- [ ] `python tools/generate_release_manifest.py --check` passes.
- [ ] Repository CI passes on the public commit.

