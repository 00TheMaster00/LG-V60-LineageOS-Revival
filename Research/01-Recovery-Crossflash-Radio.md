# Recovery, Cross-flash and Radio Findings

## What made the project recoverable

The most important engineering decision was the full pre-write recovery set.
The project read 96 non-userdata partitions and verified 96/96 hashes before
the global bridge. That supplied three different forms of protection:

- exact rollback inputs;
- provenance for later same-handset radio/secure-state restores; and
- evidence that unrelated partitions stayed unchanged during narrow fixes.

## Cross-flash conclusion

The A001LG could boot the EA40g global family and then `timelm` LineageOS, but
“Android boots” did not mean all regional subsystems were compatible. The
global bridge left the baseband path unusable on this handset. Further full
flashes would have hidden which component mattered.

Restoring only original `modem_a` and `modem_b` recovered cellular service.
That narrow result is stronger than a full-device transplant because:

- the source images came from the same physical handset;
- only the firmware slots changed;
- identity/calibration LUNs were not rewritten; and
- readback/hash verification isolated the action.

## What should not be generalized

- The recorded A001LG partition coordinates are not universal.
- Another phone's FTM, QCN, EFS, modemst, DRM or persist is not a substitute
  for a missing backup.
- A community “erase list” for one carrier model is not automatically safe on
  a SoftBank/global variant.
- Relocking a bootloader across a mixed/cross-flashed state is outside the
  proven result.

The public DIY path therefore documents checkpoints and live-map verification
instead of shipping another handset's raw programmer commands.

