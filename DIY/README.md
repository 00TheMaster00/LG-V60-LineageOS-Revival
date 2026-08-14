# Do It Yourself

This path turns the project into repeatable work for another owner. Follow the
tracks in order when doing a complete conversion; jump directly to Camera or
Kernel only when the required baseline already exists.

If you are unsure which independent track applies, begin with
[Getting Started by Goal](../GETTING-STARTED.md). For exact required inputs and
hashes, see the [Reproducibility Contract](../REPRODUCIBILITY.md).

## Complete order of operations

1. [Safety and stop conditions](00-SAFETY-FIRST.md)
2. [Recovery backup](01-Recovery-Backup/README.md)
3. [A001LG to EA40g to Lineage case study](02-Crossflash-Lineage/README.md)
4. [Radio recovery from your own modem backup](03-Radio-Recovery/README.md)
5. [Fingerprint diagnosis and DRMV2 recovery](04-Fingerprint/README.md)
6. [Performance kernel and runtime profiles](05-Performance-Kernel/README.md)
7. [LG Camera Candidate 24 reconstruction](06-LG-Camera/README.md)
8. [Final validation checklist](07-Final-Validation.md)

## Three rules that prevent most disasters

- Never use another phone's identity/calibration partitions.
- Never use copied sector coordinates without exporting the live partition
  table from the target handset.
- Never flash without a matching pre-write backup, source hash and post-write
  readback plan.

The repository deliberately separates read-only preparation from write steps.
A successful result on one A001LG does not make an unverified command safe on
another V60 variant.
