# Troubleshooting by Symptom

Use this page before repeating a flash or broadening a write set. A changed
symptom is evidence; record it before making the next single-variable change.

## Universal triage

1. Stop if device identity, active slot, source hash or live target is unclear.
2. Reproduce once from a cold start with the smallest possible action.
3. Save the pre-action state and the first relevant error—not thousands of
   unrelated log lines.
4. Separate UI entry, session creation, real output and post-reboot survival.
5. Roll back the last bounded change before combining another hypothesis.

## Camera installation or launch

| Symptom | Likely explanation | Next check |
|---|---|---|
| Builder rejects stock APK | Wrong region/version, modified APK, bad extraction or incomplete copy | Compare exact byte count and SHA-256; do not bypass the gate |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Installed LG/system copy has a different signing certificate | Pull/back up the installed base APK, then follow the documented uninstall/install path |
| Camera immediately keeps stopping | Stale incompatible package, missing permission, wrong ROM/vendor baseline, verifier failure or absent dependency | Capture clean launch log; verify installed APK hash, version and certificate; look for the first `FATAL EXCEPTION`/`VerifyError` |
| App opens but no lenses/video control | Wrong build installed or vendor camera enumeration differs | Verify Candidate 24 hash; record `dumpsys media.camera` and package version privately |
| Settings text overlaps or appears scattered | Pre-fix resource/layout state or display/font scaling outside tested baseline | Verify build hash; test default display/font scale; compare with Candidate 24 layout gate |
| Gallery button crashes then opens Gallery | Handoff receives an invalid/stale item or pre-fix compatibility branch | Test the exact newest MediaStore URI and inspect the first camera exception |

Do not copy the app into `/system`, `/product` or `/vendor`, disable SELinux,
or flash a camera partition to fix an application-level crash.

## Camera lenses and photo quality

| Symptom | Explanation from the project | Required distinction |
|---|---|---|
| 1x output is only `4160x3120` | Earlier port forced the main sensor to the ultrawide ceiling | Candidate 24 normal main Photo should save `4624x3468` |
| 0.5x is missing | Physical-camera mapping or selector state did not initialize | Confirm camera 2 exists in provider metadata before changing UI logic |
| 0.5x preview becomes grey after 8K | 8K main-camera preference crossed into the ultrawide `_sub` preference state | Return Video to camera 0; Candidate 24 normalizes 8K before Video initialization |
| Preview appears smoother at 60 fps but still photo is not better | Preview cadence and still-image processing are separate | Judge saved files under matched lighting; exposure may reduce actual preview fps |
| 64 MP option is absent | Full active-array size is not an ordinary JPEG mode; QCFA/remosaic vendor processing is missing | Do not advertise `9248x6936` active-array metadata as a proven 64 MP output path |
| Portrait works without depth separation | Promoted build uses a stable single-camera fallback | True ToF/multi-output Portrait remains unproven |

Compare real file dimensions, EXIF, focus, noise, clipping and detail. A
higher requested output size alone does not prove superior ISP processing.

## Camera video and More modes

| Symptom | What the project found | Action |
|---|---|---|
| 8K records but appears frozen after Stop | Candidate 23 finalized the file but failed to restore normal Video UI state | Use Candidate 24 and wait for controls; verify the exact newest MediaStore item |
| Valid 8K item has a blank thumbnail | Android thumbnail extraction may return no bitmap for the 8K file | Open the exact MediaStore URI; do not confuse thumbnail failure with recording failure |
| Resolution badge opens an ugly full Settings screen | Pre-Candidate-24 quick-function remap redirected the badge | Candidate 24 should expand the in-camera HD/FHD/FHD60/4K/4K60/8K strip |
| 4K60 starts but Gallery fails | Save may be valid while handoff targets the wrong item | Inspect exact recorded dimensions/duration and launch the exact MediaStore URI |
| Manual Video fails during session setup | LG private operation mode is unavailable on the Lineage provider | Promoted path uses ordinary Camera2 session 0 |
| Slo-mo fails with profile/session error | LG private high-speed profile and operation mode are incompatible | Promoted path translates profile and uses constrained-high-speed session 1 for 1080p240 |
| Sticker crashes on entry/capture | Optional LG context/service or ARGear state is unavailable | Verify Candidate 24 and test with a visible face separately from pipeline capture |
| Story fails after first stage | Stock-only crop path or automatic ultrawide conversion | Promoted path uses app-private crop storage and compatible main-camera state |
| Cine/Food still fails | Companion packages or proprietary processing remain absent | Treat as unsupported research, not a reason for a broad vendor transplant |

## Fingerprint enrollment

| Symptom | Interpretation | Next step |
|---|---|---|
| No icon, illumination or touch response | Likely display/sensor/touch-stack issue | Inspect hardware, connector, replacement glass and protector before EDL work |
| Immediate “Can't complete fingerprint setup” after global flash | Secure calibration/provisioning mismatch is plausible | Capture one enrollment log, verify hardware response, then compare with the DRMV2 case |
| Immediate timeout during experiment | Transport changed but enrollment did not complete | Roll back experimental kernel state; timeout was not the final fix |
| Original `drm`/`p_persist_lg` restore changes nothing | Mixed firmware may still reject the secure state | Do not keep widening restores; the successful case used exact DRMV2 on `drm` only |
| DRMV2 write succeeds but enrollment still fails | Wrong target mapping, incompatible baseline, hardware issue or unverified source | Check full readback hash, unchanged GPT and HAL logs; restore the immediate pre-write image if diagnosis no longer matches |
| Authentication works but needs harder pressure | Replacement touch glass/protector can alter optical coupling | Treat as physical behavior when enrollment/authentication remain reliable |

Never use another handset's DRM, persist or calibration partitions.

## Baseband, SIM or LTE

| Symptom | Likely class | Next check |
|---|---|---|
| Empty/unknown baseband after bridge | Modem firmware incompatibility or missing slot image | Verify both modem slots from the same handset before any write |
| Baseband present but SIM absent | SIM hardware, carrier configuration or telephony state | Reseat/test SIM, inspect sanitized telephony state, avoid EFS/QCN writes |
| SIM present but no data | APN, carrier provisioning, bands or network | Check APN and supported bands before firmware changes |
| Service returns then disappears after reboot | Slot asymmetry or incomplete validation | Verify both `modem_a` and `modem_b` readbacks and repeat post-reboot registration |
| QFIL readback differs | Transfer, programmer, mapping or storage-integrity fault | Do not reboot; preserve logs and re-establish read-only access |

The proven repair did not require modemst, FSG, FSC, EFS, QCN or identity
substitution.

## Boot or kernel

| Symptom | Likely explanation | Response |
|---|---|---|
| Patch does not apply | Wrong kernel base or source already differs | Stop and rebase/review; do not force rejected hunks |
| Build release/config differs | Wrong toolchain, config or metadata | Recheck pinned commit, AOSP Clang version and running configuration |
| New slot does not boot | Bad repack, wrong DTB entry, AVB/slot issue or image-size mismatch | Select rollback slot through the preplanned independent route |
| Wi-Fi/camera/fingerprint breaks after DTB change | Wrong bundle entry or unintended component change | Compare unpacked header/kernel/ramdisk and every unaffected DTB hash |
| 670 MHz benchmark passes but games reset/freeze | Silicon/thermal stability boundary | Restore Daily/587 MHz; 670 MHz is not the recommended gaming default |
| Device becomes hot during camera plus MAX profile | Combined sustained load | Stop, cool device, restore Daily and retest subsystems independently |

Do not remove Qualcomm LMH/DCVSH or thermal limits to make a benchmark pass.

## Charging

The documented phone stopped taking meaningful power at intermediate charge
levels. Replacing its old original battery resolved the problem. Before any
kernel charging change, test a known-good cable/charger, USB-C port, battery
temperature/health and known-good battery. Never disable charge-voltage,
battery-authentication or thermal safety logic to hide a failing cell.

## Evidence safe to share

Share the smallest sanitized set:

- public model/variant and ROM/vendor version;
- public artifact hash;
- exact documented step reached;
- first relevant exception/error code;
- output dimensions/duration when applicable; and
- rollback outcome.

Do not share device serials, phone numbers, IMEI/MEID, QCN/EFS, partition
images, DRM/persist/FTM, proprietary APK/firmware, faces, GPS EXIF or raw logs.

