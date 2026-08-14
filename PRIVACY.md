# Privacy and Release Boundary

## Allowed in this repository

- original documentation and scripts;
- GPL-compatible kernel source patches;
- parameterized examples and blank manifest templates;
- sanitized, aggregate test results;
- a transformation that requires the user-owned exact stock Camera APK;
- public checksums and links to original community sources.

## Forbidden in this repository

- `.apk`, `.kdz`, `.dz`, `.tot`, partition `.img/.bin`, QCN/NV and userdata;
- IMEI, MEID, phone numbers, SIM identifiers or ADB serials;
- private email, access tokens, signing keys or personal host paths;
- unredacted QFIL, `getprop`, `dumpsys`, radio or telephony logs;
- another handset's modem, DRM, persist, FTM, calibration or EFS content.

## Sanitizing a bug report

Include model family, ROM/version, vendor build, active slot, exact public
artifact hash, command exit status and the smallest relevant error excerpt.
Replace device serials with `<DEVICE_SERIAL>`, COM ports with `<COM_PORT>`,
user paths with `<WORKSPACE>`, and omit all telephony identifiers.

The CI privacy check is intentionally conservative. A maintainer must review
any exception rather than weakening the filter to make a commit pass.

