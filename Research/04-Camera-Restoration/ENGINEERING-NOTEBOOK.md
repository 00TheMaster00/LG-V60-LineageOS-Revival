# LG Camera Compatibility Engineering Notebook

This is the sanitized, public version of the application-engineering record
behind Candidate 24. It explains what changed below the APK level, why a stock
APK alone is insufficient on LineageOS, which candidates failed, and what the
final validation actually proves. Private APKs, decompiled proprietary trees,
device identifiers, raw logs and user media are not published.

## System boundary

Candidate 24 is an APK-only compatibility layer for LG Camera 9.91.3 from the
documented EA40g firmware. It keeps the package name `com.lge.camera` and uses
the V60's installed vendor camera provider, codecs, sensors and metadata.

No camera, vendor, ODM, modem, DRM, boot, DTBO, recovery, kernel or ROM
partition was changed during camera restoration. This matters because the
result is not “all camera firmware inside one APK.” The runtime stack is:

```text
LG Camera application and resources
        |
Android framework / Camera2 / MediaRecorder / MediaStore
        |
LG and Qualcomm vendor camera provider and codecs
        |
V60 physical sensors, actuator, flash and ISP path
```

The port replaces or guards missing framework/services at the top two layers.
It cannot recreate every proprietary provider graph or companion package.

## Why the untouched stock APK failed

The EA40g application assumed an LG stock framework environment. On LineageOS
the first failures came from several independent classes of dependency:

- LG-only framework classes such as `android.media.AudioManagerEx`;
- optional services exposed through `LGContext`;
- private camera operation modes and multi-output graphs;
- stock resource identifiers and task-description drawables;
- writable vendor paths unavailable to a normal user application;
- mode/lens conversion policies tied to LG's stock logical-camera model;
- separate main/sub-camera preference keys;
- callback paths normally completed by stock depth/outfocus services; and
- companion packages used by Food/Cine and other external modes.

This is why merely installing the APK produced launch crashes, missing or
misleading lens controls, unusable More modes, broken settings layout and
poor main-camera output sizing.

## Engineering and packaging model

Development was performed as bounded Smali/DEX and resource changes against a
known stock base. Every promoted candidate passed:

1. bytecode assembly;
2. disassembly/round-trip inspection;
3. APK ZIP consistency and alignment;
4. APK Signature Scheme v3 verification;
5. the established project-certificate hash;
6. installed/local APK hash equality; and
7. a candidate-specific physical runtime gate.

The public repository does not require another developer to reproduce the
private decompile/rebuild environment. It supplies a verified binary
transformation from one exact lawful stock input to the exact promoted output,
plus a local [source-audit workflow](../../DIY/06-LG-Camera/SOURCE-AUDIT.md)
that pins every changed APK entry and semantic Smali file. The ten added
compatibility classes and the project-authored SurfaceTexture JNI shim are
published as source; LG's decompiled application and the proprietary
`libmpbase.so` dependency are not. The [DIY builder](../../DIY/06-LG-Camera/README.md)
rejects every near match.

## Phase history

### V1 through V37: make the process survive AOSP

The early work established basic application/framework compatibility, camera
opening, still/video session lifecycles, media saving and physical-lens
mapping. Optional LG dependencies were guarded or replaced rather than
restoring broad proprietary framework packages.

### V38 through V45: restore visible V60 behavior

This phase added V60-specific picture/video choices, settings layout, lens
controls, Gallery handoff, 4K60 and 8K exposure in the interface. UI exposure
was not treated as proof until real files were recorded and inspected.

### V46 through V52: output metadata and high-resolution stability

The port corrected output metadata and front defaults, translated relevant LG
camcorder profiles, stabilized 4K60 and produced real 8K output. V52 retained
evidence for:

- rear HDR JPEG at `4160x3120`;
- front lifecycle at `1920x1440`;
- 4K60 AVC/AAC at `3840x2160`, approximately 59.9 samples/s; and
- 8K HEVC/AAC at `7680x4320` using the vendor 105 Mbps profile.

### V53 through V55: Manual and Portrait compatibility

V53 changed one-shot preview callback ordering in `ManualCameraMode` and
`ManualVideoMode`; the experiment was reverted in V54.

V54 changed the following areas:

| Class/area | Compatibility behavior |
|---|---|
| `CmdAddRequestersManualCamera` | Use the compatible JPEG request path rather than a stock RAW-coupled path |
| `ManualCameraMode` | Constrain preview behavior to a stable range and use a regular Lineage session |
| `ManualVideoMode` | Restore original callback order while preparing a compatible recording route |
| `ConfigurationUtil` / `ZoomMgr` | Remove incompatible dual-outfocus assumptions and accept the active physical optic camera |
| `CameraOperationMode` | Map Manual still and Portrait private operations to regular Camera2 sessions |

V55 updated `CmdPictureCallbackAfter` and `CameraOps` so single-camera
Portrait resets snapshot state after the JPEG callback. Stock dual-outfocus
would normally complete that state transition, but its proprietary callback
does not arrive on the Lineage fallback path.

## V56 More-mode candidate ledger

The V55 More audit first separated application exceptions from provider-graph
failures. The focused fixes were then built cumulatively:

| Candidate | Change | Result |
|---|---|---|
| 1 | Guard null Story `app-shot_mode` and null Slo-mo `videoSize` | Both modes progressed beyond their immediate crashes |
| 2-3 | Translate LG high-speed profile identifiers to Android 1080p/720p high-speed profiles | A real 1080p240 graph was identified; private operation still failed |
| 4 | Replace `AudioManagerEx` references with standard `AudioManager` | Manual Video UI opened; private operation remained incompatible |
| 5 | Map Manual Video to regular session 0 and Slo-mo to constrained-high-speed session 1 | Both sessions configured without provider error 4 |
| 6 | Make unsupported optional LG vibration mute a no-op | Real Manual Video and 1080p240 clips recorded, stopped and saved |
| 7 | Stop decoding missing `lg_iconframe_camera` for task description | Direct camera activity launch became stable |
| 8 | Move Story crop from `/data/vendor/LGCamera/crop.jpg` to app-private storage | Both stages could read/write the intermediate image |
| 9-10 | Attempt to remove Story ultrawide through angle-mask changes | Failed: the earlier camera-ID conversion had already selected camera 2 |
| 11 | Exempt `mode_storyshot` from incompatible `CamCtx.convertCameraId()` conversion | Story opened at x1, completed rear/front stages and saved |

Candidates 9 and 10 are important negative evidence: changing a visible lens
mask did not repair state that had already been converted earlier in the
initialization path.

## Mode-specific provider compatibility

The V55 audit found different root causes:

| Mode | Original failure | Promoted treatment/status |
|---|---|---|
| Manual Video | Missing LG audio class, private operation, optional LG service | Standard audio API, regular session 0; real 1080p output proven |
| Slo-mo | Null size, private profile and operation | Profile translation plus constrained-high-speed session 1; 1080p240 proven |
| Story | Null mode state, stock-only crop path, premature ultrawide conversion | Guards, app-private crop and compatible main-camera state; pipeline/save proven |
| Night | Private operation plus wrong physical conversion | Regular-session compatibility; entry/session stable, final processing unproven |
| Panorama | Private operation graph | Regular-session compatibility; entry/session stable, stitching unproven |
| Time-lapse | Private recording operation plus camera conversion | Regular-session compatibility; entry/session stable, long output unproven |
| 360 Panorama | Private operation and multi-camera assumptions | Entry/session stable, stitching unproven |
| Food/Cine | Missing companion package/proprietary components | Not restored |

## 8K and physical-lens state

The application keeps separate video-size keys:

```text
camera 0 main:       key_video_recordsize
camera 2 ultrawide:  key_video_recordsize_sub
```

When Photo was left on physical ultrawide while the main key held 8K, Video
could initialize from camera 2's FHD `_sub` value while parts of the interface
still displayed 8K. The resulting mixed state produced a grey or rejected
camera-2 recording session.

Candidate 12 forced camera 0 after size initialization; it was safe but too
late. Candidate 13 guarded `CamCtx.convertCameraId()`; it was still too late
because the sub-camera preference had already been read. Candidate 14 moved
the normalization before Video-size initialization and read the main key
directly. Candidates 17-19 refined that path and stopped menu restoration from
overwriting the validated 8K selection.

The final policy is:

- 8K always uses physical camera 0/x1;
- an ultrawide-Photo to 8K-Video transition normalizes before Video reads its
  size state;
- lower-resolution physical-ultrawide Video was not promoted after provider
  `Function not implemented (-38)` evidence; and
- the UI label is never accepted as proof without a real `7680x4320` file.

## Main-photo quality and output dimensions

Live provider metadata identified:

- main camera 0: Samsung `s5kgw1`, real active array `9248x6936`, normal
  binned sensor mode and advertised JPEG output `4624x3468`;
- ultrawide camera 2: maximum corresponding JPEG output `4160x3120`.

Earlier candidates translated the stored Japanese size to `4160x3120` for
both rear sensors. That unnecessarily capped the main output at 12,979,200
pixels instead of 16,036,032—23.6% fewer output pixels.

Candidate 20 proved main `4624x3468` but its optic list broke ultrawide
compatibility. Candidate 21 kept the compatible optic list and moved the
per-sensor mapping to request time. Candidate 22 attempted to limit the
mapping to normal Photo but reused a register as both integer and object; ART
rejected the method with an immediate `VerifyError`. Candidate 23 corrected
the register use and promoted this policy:

| Request | Output policy |
|---|---|
| Normal main 4:3 | `4624x3468` |
| Normal main 16:9 | `4624x2600` |
| Ultrawide 4:3 | `4160x3120` |
| Ultrawide 16:9 | `4160x2340` |
| Portrait, Manual and specialized modes | Compatible 4160-size family |

`CmdAddRequesters` applies the final request-time mapping. `OpticCameraMgr`
retains a stock-compatible optic list so changing the main maximum does not
make camera 2 reject the graph.

The active array is not a proven 64 MP JPEG mode. Full resolution needs the
missing QCFA/remosaic path and compatible vendor processing.

## Candidate 24: final two user-visible defects

Candidate 23 produced valid 8K but left normal Video controls in recording
state after Stop. Recorder and MediaStore logs proved finalization succeeded;
the compatibility stop branch simply did not run all UI restoration normally
completed by the proprietary callback.

Candidate 24 changes two classes:

- `RearVideoMode` runs a narrow compatibility-stop restoration before
  `notifyRecStopDone()`, restoring timer, shutter/recording controls,
  quick-function controls, zoom, focus, angle, progress, screen-on and related
  normal Video state.
- `QFLBtns` no longer remaps resolution quick-function type `0x27` to full
  Settings type `0x20`, so the in-camera resolution group expands directly.

Candidates 25 and 26 explored fallback 8K thumbnails. Candidate 25 was
rejected for an ART register-type conflict. Candidate 26 launched, but the
file-based extractor also returned no 8K bitmap. Neither improved the result,
so Candidate 24 remained promoted.

## Final evidence matrix

| Capability | Final classification |
|---|---|
| 15 cold launches | Proven, 15/15 foreground launches |
| Photo/Video transitions | Proven, 8/8 each direction |
| Main Photo | Proven at `4624x3468` |
| Ultrawide Photo | Proven at `4160x3120` with repeated alternation |
| Front camera | Capture/save lifecycle proven at `1920x1440`; retained final scene was obstructed |
| Portrait | Proven single-camera fallback, not ToF depth |
| Manual Camera | Proven JPEG at `4160x3120` |
| Sticker | Rendering/capture proven at `2460x1080`; face placement needs a visible face |
| Story | Two-stage pipeline/save proven; final visual composition needs unobstructed front-camera proof |
| 1080p60 / 4K60 | Real files proven |
| 8K | Real `7680x4320` files, three consecutive stop/save cycles and sustained 121.685-second recording proven |
| Manual Video | Real `1920x1080` output proven |
| Slo-mo | Real 1080p240 constrained-high-speed output proven |
| Night/Panorama/Time-lapse/360 | Entry/session stable; scene/motion-dependent final output unproven |
| RAW/DNG / 64 MP | Not restored |
| Cine/Food | Missing dependencies; not restored |

Final Candidate 24 identity:

```text
APK SHA-256: E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71
Certificate: 1E08A903AEF9C3A721510B64EC764D01D3D094EB954161B62544EA8F187B5953
```

The retained final stress state reported Android thermal status 0 and battery
temperature 37.2 C. The owner's quality assessment was better than the earlier
broken state, but no controlled stock-versus-Lineage laboratory image-quality
study was completed.

## Reproduction and debugging rule

Start from the exact promoted APK hash, reproduce one mode, and record:

- physical camera ID and requested size;
- session type and first provider error;
- output MediaStore dimensions/duration when a file exists;
- whether the same app process survives; and
- whether the result proves entry, session, capture, save or visual quality.

Do not publish the APK, private Smali tree, raw logs or test media. Use the
public binary transformation and share only sanitized failure signatures.
