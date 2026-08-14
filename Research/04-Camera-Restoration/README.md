# LG Camera Restoration Engineering Narrative

For the detailed phase history, class-level compatibility ledger, failed
candidates and complete proof matrix, read the
[Camera Compatibility Engineering Notebook](ENGINEERING-NOTEBOOK.md).
For exact package/class/method verification against locally owned APKs, use
the [Candidate 24 source audit](../../DIY/06-LG-Camera/SOURCE-AUDIT.md).

## Scope

The goal was to run LG Camera 9.91.3 from EA40g on LineageOS 23.2/Android 16
without replacing vendor, ODM, kernel or ROM partitions. Every candidate was
an APK-only change and used the same package name, `com.lge.camera`.

## Why stock crashed

LG Camera expected LG framework classes, privileged services, private camera
operation modes, resource overlays, fixed writable vendor paths and companion
packages that are not present on AOSP/Lineage. Initial symptoms included
launch crashes, missing lens/video controls, broken settings layout, poor
main-camera sizing, and crashes in Portrait, Sticker, Manual and More modes.

## Major development phases

### V1-V37: establish a working AOSP process

- guarded or replaced absent LG framework/service calls;
- restored camera open/session lifecycle and media save behavior;
- mapped physical V60 cameras instead of presenting one generic lens; and
- separated hard dependencies from optional LG enhancements.

### V38-V45: restore visible V60 behavior

- native V60 picture/video choices;
- stable settings layout and physical lens controls;
- Gallery handoff;
- 4K60 and 8K options; and
- stock-style mode navigation where dependencies existed.

### V46-V55: make specialized paths survive Lineage

- corrected output metadata/front-camera defaults;
- translated LG private camcorder profiles;
- used ordinary Camera2 session 0 for Manual Video where the private operation
  mode was unavailable;
- used constrained-high-speed session 1 for 1080p240 Slo-mo;
- replaced unavailable `AudioManagerEx` behavior with standard Android APIs;
- implemented a single-camera Portrait fallback; and
- repaired repeated Portrait capture state and other operation-mode failures.

### V56 Candidates 1-11: More-mode closure

- guarded Story and Slo-mo null state;
- completed Manual Video and 1080p240 output;
- removed the absent LG task-description drawable dependency;
- moved Story's temporary crop from a stock-only vendor path into app-private
  storage; and
- prevented Story from being converted to an incompatible physical lens.

### Candidates 12-23: 8K/lens state, photo quality and broad regression

- found separate main/sub video preference keys and normalized 8K to camera 0;
- added safe regular-session fallbacks for selected More modes;
- inspected live camera metadata and found the main camera advertised
  `4624x3468` while the port forced both rear cameras to the ultrawide
  `4160x3120` ceiling;
- restored `4624x3468` only for normal main Photo while retaining compatible
  4160-family sizes for ultrawide, Portrait and Manual; and
- fixed the Settings row layout and proved broad mode/capture stability.

The main output change raises captured pixels from 12,979,200 to 16,036,032,
23.6% more. It does not claim 64 MP remosaic or prove that dimensions alone
solve every subjective quality issue.

### Candidate 24: final user-visible defects

Recorder/MediaStore logs showed the apparent 8K stop freeze was not a lost
recording: the valid file finalized, but the compatibility branch left normal
Video UI in its recording state. Candidate 24 added a narrow post-stop UI
restoration before completion notification.

It also stopped the top resolution badge from redirecting to full Settings,
allowing the in-camera HD/FHD/FHD60/4K/4K60/8K strip to expand.

## Final proof

- 15/15 cold launches;
- 8/8 Photo/Video cycles;
- main `4624x3468`, ultrawide `4160x3120`, front lifecycle;
- Portrait fallback, Manual Camera, Sticker and Story pipeline;
- 1080p60, 4K60, Manual Video, 1080p240 and real 8K;
- three consecutive 8K stop/save cycles with UI/process survival;
- one sustained 121.685-second 8K recording;
- exact MediaStore Gallery handoff; and
- thermal status 0 after final stress.

## Honest limits

- Portrait is single-camera fallback, not true ToF depth.
- RAW/DNG and 64 MP QCFA/remosaic are not restored.
- Physical ultrawide Video was not promoted after provider `-38` evidence.
- Android may return no bitmap thumbnail for a valid 8K file.
- Night, Panorama, Time-lapse and 360 entry/session are stable, but their
  scene/motion-dependent final outputs remain unproven.
- Food/Cine paths still depend on absent proprietary components.
- Front visual quality was not proven in the retained run because the phone
  was face-down over the front camera.

The public DIY route distributes a verified delta, not an LG APK. The delta
reconstructed the exact promoted Candidate 24 during owner-run release
validation. Public CI validates the transformation engine with synthetic data;
an independent owner reproduction is still pending.
