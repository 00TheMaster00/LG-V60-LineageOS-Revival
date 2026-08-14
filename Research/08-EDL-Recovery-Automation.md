# EDL Recovery Automation Findings

The 2026-08-14 private engineering handoff preserved several historical
PowerShell recovery scripts. They were not imported into this public
repository because they contain one-handset paths, serial selection, COM-port
assumptions, hashes, partition positions, and incident-specific write logic.
The portable result is their transaction architecture.

## Strongest reusable pattern

The best scripts separated an EDL repair into five proof domains:

1. **Identity proof:** select one intended handset/session and verify the
   programmer bytes.
2. **Layout proof:** parse the live GPT, validate its structure/CRCs, and
   derive the target extent by label.
3. **Rollback proof:** read and hash the complete current target before any
   write.
4. **Write proof:** generate a narrow plan, require explicit approval, and
   reject suspicious Firehose output.
5. **Containment proof:** read the target back byte-for-byte and show that GPT
   and unrelated witness partitions did not change.

This is materially stronger than a script that merely sends a rawprogram XML
and checks an exit code. It distinguishes "the tool returned" from "the
intended bytes reached the intended extent and nothing else changed."

## Why the original scripts remain private

Sanitizing a dangerous script is not just replacing a username or serial.
Hard-coded coordinates can look generic after identifiers are removed while
still targeting one historical GPT. Similarly, a known programmer hash or
source-image hash proves identity only for the documented case; it does not
prove compatibility with another V60 variant or storage state.

The preserved scripts also include incident-repair paths for engineering ABL,
AVB/slot state, modem firmware, fingerprint-related partitions, and Lineage
recovery. Publishing them as ready-to-run tools would erase the preconditions
that made their original use defensible.

## Narrow writes produced the clearest conclusions

Two project outcomes illustrate the value of containment:

- Radio service returned after restoring only the same handset's original
  modem firmware slots while identity/calibration witnesses remained
  unchanged.
- Fingerprint recovery ultimately required a specific DRM calibration image,
  written to the live `drm` target with immediate backup and exact readback;
  broad persist/modem/GPT writes were unnecessary.

Because the writes were narrow and independently verified, the result can be
attributed to the changed component rather than to an uncontrolled full-device
flash.

## What future tooling should implement

A reusable recovery framework should keep live case data outside its code and
provide separate commands for:

- discover and record the connected session;
- read and validate GPT structures;
- resolve a unique partition label;
- collect the pre-write target and witnesses;
- validate the proposed source and generate a reviewable plan;
- execute only the approved plan;
- read back and compare; and
- generate a private evidence report.

Its automated tests should use synthetic GPT images and mocked Firehose
output. Tests should cover corrupted CRCs, duplicate labels, out-of-range
extents, wrong block sizes, short reads, unexpected XML operations, misleading
zero exit codes, readback mismatches, and changed witnesses. Real device maps,
partition images, serials, and credentials do not belong in test fixtures.

## Public conclusion

The historical scripts are valuable evidence, but the public artifact should
be a safe transaction model rather than a universal flasher. The actionable
version is the [Safe EDL Write Transaction](../DIY/01-Recovery-Backup/EDL-WRITE-TRANSACTION.md).
