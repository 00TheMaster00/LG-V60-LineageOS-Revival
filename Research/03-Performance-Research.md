# Performance and GPU Research

## CPU finding

Performance V1 made two bounded scheduler changes:

- each core-control cluster's minimum CPU count equals its full CPU count; and
- schedutil defaults to immediate upscaling and a 10 ms downscale delay.

This keeps cores available and increases responsiveness. It does not remove
thermal throttling. Qualcomm LMH/DCVSH remained intact after investigation;
that safety boundary is deliberate.

## GPU finding

The source already contained a complete vendor 670 MHz OPP at the `NOM_L1`
corner. Speed bin 0 began at 587 MHz/NOM. The release patch did not invent a
voltage. It promoted the existing 670 entry, shifted the existing indices and
retained 587 immediately below it.

The final ladder is:

```text
670 / 587 / 525 / 490 / 441.6 / 400 / 305 / 0 MHz
```

Bandwidth votes and ACD values were retained from the vendor source. The
repository includes the exact patch and a balanced-brace source tool so the
transformation can be reviewed and tested.

## Repack finding

Rebuilding the entire kernel was not necessary for the GPU change. The safer
V2 design kept the already working V1 kernel and Magisk ramdisk byte-for-byte,
identified one live matching entry in a concatenated DTB bundle, replaced
only that entry, and proved all unaffected entries stayed identical.

## Practical result

670 MHz was stable enough for benchmark use and short tests. The owner
observed mild instability in gaming, so 587 MHz is the daily/gaming default.
This is a real, measurable extension with an explicit stability boundary—not
a claim that every SM8250 bin will behave identically.

