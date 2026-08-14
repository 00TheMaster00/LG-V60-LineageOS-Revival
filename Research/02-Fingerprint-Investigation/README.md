# Fingerprint Investigation: What the Failed Kernel Work Proved

## Symptom progression

Enrollment first failed immediately with **Can't complete fingerprint setup**.
During guarded experiments it briefly changed to an immediate timeout, then
returned to the original message. Illumination, touch handling and HAL startup
showed the optical sensor path was not simply dead.

## Original-partition tests

Restoring the same handset's original `p_persist_lg`, then its original `drm`,
did not repair enrollment in the mixed global/Lineage environment. A runtime
overlay test using exact EA40g fingerprint trusted-app files also reached the
same later secure-call rejection. These results ruled out a simple missing
file or simple “restore old DRM” answer.

## Ordered kernel experiments

The six preserved patches correspond to five transport/buffer experiments
plus a kernel label commit:

| Commit | Experiment | Result |
|---|---|---|
| `20744a7e49d965f11992a02be10b77d0d8bcce61` | legacy transport for Egistec modified-buffer commands | did not complete enrollment |
| `d61c4c6c4b9044ad47e9e3823fdc252080e3225b` | registered-buffer path | did not complete enrollment |
| `9a7254d4b0eda13fa413ee5670437afff4db6beb` | shared-memory bridge | allocation could exceed the 32-bit trusted-app range |
| `abb26dbd20378a00a157f15b135b4dca888fd384` | keep whitelist buffers below 4 GiB | early commands improved; later command rejected |
| `39bfb0eecc61ab36f965b82c6438c44ee684a554` | identify fpqsee4 build | provenance only |
| `27f36e7df45014f88d5f2ac51fd0d110669d7da6` | retry rejected command through legacy SCM | both supported routes returned rejection |

The best experiment placed request, response and scatter/gather metadata in
low TrustZone-registered memory. The HAL obtained a real pre-enrollment
challenge, but the later initialization command still returned raw SCM `-2`,
surfaced as QSEECOM `-22`/`EINVAL`.

These patches are under [experiments](experiments/) for research provenance.
They are **not** part of the working performance release and are unnecessary
after DRMV2.

## Decisive community fix

The XDA-linked DRMV2 method changed the handset's DRM calibration/provisioning
state in the form expected by the secure fingerprint stack. The exact source
image was written to `drm` only; full readback matched SHA-256 and the GPT
header remained unchanged. Enrollment then completed.

That result explains why the solution was hard to derive from kernel logs
alone: the failing API boundary was visible, but the accepted secure-state
contents and provenance were opaque/proprietary. Community hardware/firmware
experimentation supplied the missing empirical input.

