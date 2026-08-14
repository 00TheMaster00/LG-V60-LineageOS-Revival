# Known Limits and Next Research

## Proven project boundaries

- End-to-end conversion was proven on one SoftBank A001LG.
- Camera Candidate 24 was proven on the recorded LineageOS 23.2/Android 16 and
  matching V60 vendor stack.
- GPU 670 was benchmark-capable but not the recommended gaming default.
- Fingerprint DRMV2 success does not make one handset's sector coordinates
  universal.

## Camera research still open

- true ToF/multi-output Portrait graph;
- RAW/DNG session stability;
- 64 MP QCFA/remosaic vendor processing;
- physical ultrawide Video provider compatibility;
- robust 8K thumbnails outside the app;
- full output proof for Night, Panorama, Time-lapse and 360 modes; and
- missing Food/Cine companion dependencies.

## Publication gaps intentionally retained

- no proprietary APK or KDZ;
- no prebuilt boot image;
- no DRM/persist/modem/EFS/FTM/QCN/userdata image;
- no raw logs containing a device serial, network identity or user path;
- no user photo/video evidence; and
- no claim of laboratory image-quality improvement.

Contributions should reproduce one bounded result, include sanitized build
and vendor identity, state whether output or only UI entry was proven, and
never attach private partition data.

