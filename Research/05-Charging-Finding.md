# Charging Finding: Resolved by Battery Replacement

The initial phone stopped accepting meaningful current at intermediate charge
levels and did not approach the expected original-charger input. Because the
device used LineageOS and custom kernels, charging policy was a plausible
hypothesis.

The original battery was likely unchanged since the phone's early life.
Replacing it resolved charging behavior. That outcome outweighs speculative
kernel current-limit changes and is consistent with battery aging. It does not
isolate cell aging as the sole possible cause, but no kernel override was
needed on this handset.

No public release should disable battery authentication, thermal protection,
charge-voltage limits or Qualcomm safety logic to hide a failing cell. Check
cable/charger, USB-C port, battery temperature/health and a known-good battery
before touching charge policy.
