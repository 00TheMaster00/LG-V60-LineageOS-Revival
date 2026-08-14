# Charging Finding: Hardware, Not a Kernel Override

The initial phone stopped accepting meaningful current at intermediate charge
levels and did not approach the expected original-charger input. Because the
device used LineageOS and custom kernels, charging policy was a plausible
hypothesis.

The original battery was likely unchanged since the phone's early life.
Replacing it resolved charging behavior. That outcome outweighs speculative
kernel current-limit changes: the root cause was the aged battery in this
case.

No public release should disable battery authentication, thermal protection,
charge-voltage limits or Qualcomm safety logic to hide a failing cell. Check
cable/charger, USB-C port, battery temperature/health and a known-good battery
before touching charge policy.

