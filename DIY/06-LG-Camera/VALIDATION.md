# Candidate 24 Validation Matrix

Test in this order. Record ROM/vendor build, Candidate 24 hash, ambient
conditions, battery temperature, available storage and the exact failure time.
Do not publish faces, GPS EXIF or private filenames without consent.

## Stability gates

1. Launch/permission flow once.
2. Force-stop and cold-launch 15 times; require 15 foreground launches and no
   fatal/verifier failure.
3. Switch Photo to Video and back eight times.
4. Open Settings and inspect every row for overlap, clipping or displaced text.
5. Leave the app, lock/unlock, return, rotate where supported and cold-launch
   again.

## Photo gates

| Feature | Test | Expected Candidate 24 result |
|---|---|---|
| Rear main | Daylight focus, capture, open Gallery, inspect dimensions | `4624x3468` maximum compatible binned JPEG; proven |
| Ultrawide | Select 0.5x, capture, inspect | Physical ultrawide `4160x3120`; proven |
| Lens alternation | Main/UW repeated for six captures | Three valid files from each lens; proven |
| Front | Uncover front camera, capture and inspect | Capture/save lifecycle proven at `1920x1440`; visual quality must be judged by tester |
| Portrait | Capture a person/object | Single-camera fallback `4160x3120`; proven, not ToF depth |
| Manual Camera | Change one safe control and capture | UI/telemetry and `4160x3120` save proven |
| Sticker | Choose an effect and capture | ARGear processing and `2460x1080` save proven; face-dependent placement needs a face |
| Story | Complete rear and front stages | Pipeline/save proven; final composition needs unobstructed front camera validation |
| Night | Dark-scene capture | Entry/session stable; final scene-dependent output not yet proven |
| Panorama | Deliberate slow physical sweep | Entry/session stable; stitching/output not yet proven |
| 360 Panorama | Full guided sweep | Entry/session stable; stitching/output not yet proven |
| RAW/DNG | Do not enable | Intentionally disabled for session stability |
| 64 MP | Not present | Proprietary QCFA/remosaic path not restored |

The preview asks for up to 60 fps, but exposure and lighting determine actual
cadence. A 60 fps preview does not itself improve the captured still; judge
quality from files under controlled lighting, not only the live view.

## Video gates

Start at 1080p. For every mode, record 10 seconds, press Stop once, wait for
controls to return, open the exact newest item, play it, then inspect metadata.

| Mode | Expected result |
|---|---|
| 1080p60 | Valid `1920x1080` file; proven |
| 4K60 | Valid `3840x2160`; proven; Gallery opens exact MediaStore item |
| 8K | Valid `7680x4320`; three consecutive stop/finalize cycles proven with same process surviving |
| Sustained 8K | 121.685-second file previously proven; supervise temperature and storage |
| Manual Video | Valid `1920x1080`; proven |
| Slow motion | `1920x1080` constrained-high-speed 240 fps pipeline; proven |
| Time-lapse | Entry/session stable; long output not yet proven |
| Cine Video | Dependency incomplete; no final usable-output proof |

The top resolution badge should expand HD/FHD/FHD60/4K/4K60/8K inside the
camera activity. It should not open the full Settings activity.

Some valid 8K files do not receive a bitmap thumbnail from Android's
MediaStore or file thumbnail extractors. Open the exact MediaStore item to
distinguish a blank thumbnail from a failed recording.

Physical ultrawide Video was not promoted: non-8K camera-2 Video previously
hit provider error `-38`. Keep 8K on camera 0.

## Health/log gate after stress

```powershell
adb -s $Serial shell dumpsys thermalservice
adb -s $Serial shell dumpsys battery
adb -s $Serial shell df -h /sdcard
adb -s $Serial logcat -d -v threadtime > camera-after-stress.log
```

Require no unexplained app/process death, `VerifyError`, camera-provider crash,
KGSL/GMU fault, media-recorder finalization failure or thermal shutdown. Stop
testing if the device becomes uncomfortably hot.

## Proven final baseline

- 15/15 cold launches;
- 8/8 Photo/Video transitions;
- aligned Settings layout;
- main, ultrawide and front capture lifecycles;
- Portrait fallback, Manual Camera, Sticker and Story pipeline;
- 1080p60, 4K60, 8K, Manual Video and 1080p240;
- three consecutive 8K stop/save cycles and one sustained 8K recording;
- quick in-camera resolution strip and exact-item Gallery handoff; and
- final Android thermal status 0 with battery at 37.2 C.

The project owner reported the resulting camera quality as better than the
earlier broken/original comparison state. That is an owner observation, not a
controlled laboratory image-quality measurement.

