# Reproducibility Contract

This file answers the practical question: "Does another person have enough to
recreate the result?" The answer differs by subsystem because some inputs are
open source, some are user-supplied proprietary files, and some must be read
from the exact handset being repaired.

## Proof vocabulary

| Label | Meaning |
|---|---|
| Proven | Exact output or physical behavior was observed and retained with matching evidence. |
| Observed | A real behavior was seen, but the test did not prove the complete output or cause. |
| Inferred | Source/log evidence supports the explanation, but a decisive physical test is absent. |
| Untested | The route is documented as future work and must not be advertised as working. |

## Required inputs and public outputs

| Track | User must supply | Repository supplies | Reproduction gate |
|---|---|---|---|
| Camera Candidate 24 | Exact EA40g stock APK, compatible `timelm` vendor stack, ADB target | Hash-pinned builder, binary delta, project-authored shim source, exact APK/Smali audit manifests, install/rollback procedure, test matrix | Stock/output hashes, signature/alignment, 25 APK-entry changes and 106 semantic Smali files verify |
| Performance V1 | Pinned Lineage source, exact running config/toolchain, own boot backup | Exact source patch, build/repack method, runtime profiles | Patch applies to pinned base; build identity and functional boot tests pass |
| GPU 670 | Same as kernel plus matching live DTB entry | Exact OPP patch, before/after fragments, FDT split/replace tools and tests | Only matching DTB entry changes; final ladder and unaffected-entry hashes verify |
| Fingerprint DRMV2 | Credited community DRMV2 file, live GPT, own immediate backups | Successful file identity, diagnosis, one-target QFIL transaction and validation | Source size/hash match; full `drm` readback matches; physical enrollment/authentication pass |
| Radio | Target handset's own original `modem_a`/`modem_b`, live GPT | Narrow diagnostic and read/write/readback workflow | Same-handset provenance; both full readbacks match; baseband/SIM/LTE survive reboot |
| Recovery backup | Target phone, compatible programmer/tooling and storage | Critical list, hashing/verifier tools, acceptance criteria | Every read size matches live extent; all hashes verify on two copies |
| Cross-flash/Lineage | Lawfully obtained firmware, exact device state, current official Lineage packages | Proven checkpoints, bridge hash, failure isolation and rollback model | Each checkpoint passes independently; no copied device coordinates are used |

## Immutable public identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| EA40g stock `LGCameraApp.apk` input | 106,673,076 | `65D69A9E0DB652F43E232EC4AE86DCFC11AC688E324C5103CAAB1FECB27807E8` |
| Camera reconstruction delta | 13,676,109 | `4FB8A5D55E8E048AF737851D19CF98ABF1E2FC55F5AC119415E24746B3DCF485` |
| Candidate 24 output | 101,512,334 | `E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71` |
| Candidate 24 signing certificate | n/a | `1E08A903AEF9C3A721510B64EC764D01D3D094EB954161B62544EA8F187B5953` |
| Tested EA40g KDZ | user-supplied | `0121958707A73152503769913C1B724317A9CC013164361D469339CA40C3ACDE` |
| Successful DRMV2 image | 14,680,064 | `C0FF080DA7CA569BCA190558DB444F33004D8BA58245942496495C9EDBDDF24C` |

Kernel source identities:

```text
Lineage base:              29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2
Performance V1 state:      175901fa8aa5614cc50a695cdaa783a1bbfbba41
Performance V2 / GPU 670:  00d8f9c3262c90159d7bc9ea65fa6dd45797895e
```

These hashes identify bytes or source states. They do not make an untrusted
download safe, grant a license to proprietary material, or prove compatibility
with a different phone.

## Camera compatibility is deeper than one APK

The APK contains the application logic and the Candidate 24 compatibility
changes, but it still calls into the phone's installed Android framework,
Camera2 API, LG/Qualcomm vendor camera provider, media codecs, sensors and
device-specific metadata. Therefore:

- the public transformation is sufficient to recreate the tested APK;
- the target still needs a compatible V60 vendor stack and camera HAL;
- missing stock-only services are guarded, translated or replaced in the app;
- true ToF Portrait, 64 MP remosaic, RAW/DNG and some Cine/Food dependencies
  remain outside the promoted compatibility layer; and
- an exact APK hash on an incompatible ROM/vendor combination does not prove
  that every feature will work.

The implementation and failure history are documented in the
[camera engineering notebook](Research/04-Camera-Restoration/ENGINEERING-NOTEBOOK.md).
The [local source audit](DIY/06-LG-Camera/SOURCE-AUDIT.md) lets an owner verify
the exact package/class/method inventory without publishing LG's source.

Public CI proves builder success/failure logic with non-proprietary fixtures;
it cannot run the exact Candidate 24 delta because the proprietary stock APK
is deliberately absent. That final output proof is owner-run and is not an
independent multi-device validation until another owner reports it.

## Why some binaries are absent

The repository does not need another handset's modem, DRM, persist, FTM, EFS,
QCN, super, userdata or boot image to teach the method. Publishing those files
would create privacy, identity, calibration, licensing and bricking risks.

The same boundary applies to:

- the complete LG APK and KDZ;
- firehose programmers and commercial QPST/QFIL installers;
- a prebuilt Magisk boot image;
- raw private logs, test media and EXIF; and
- scripts with one handset's serial, slot, coordinates and approved hashes.

Absence is not a documentation gap when the correct input must come from the
user's own phone. In those cases, the public deliverable is the validator,
transaction design, exact decision rule and test procedure.

## Independent-validation status

The complete end-to-end result is currently documented on one A001LG. There
are no accepted independent reproduction reports yet. A report becomes
accepted only when it provides the public model/ROM/vendor identity, exact
public hashes, checkpoint results, real physical/output proof and rollback
result without private partitions, identifiers or proprietary files.

## Minimum report from a new reproduction

Publish only sanitized information:

1. exact public model/variant;
2. ROM and vendor build;
3. public input/output artifact hash where applicable;
4. which documented checkpoint was followed;
5. whether UI entry, session creation, real output, readback or physical
   authentication was proven;
6. expected versus actual result;
7. smallest sanitized error signature; and
8. rollback result.

Never attach a proprietary APK/firmware file, partition image, QCN/EFS,
device serial, IMEI, phone number, face, GPS EXIF or raw private log.
