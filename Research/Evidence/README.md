# Sanitized Evidence Ledger

| Area | Public claim | Verification retained privately |
|---|---|---|
| Recovery | 96/96 non-userdata partitions read and hash-verified | full images, maps and manifests |
| Radio | same-handset `modem_a/b` restored LTE | pre/post images, readbacks and logs |
| Fingerprint | DRMV2 readback matched; GPT unchanged; enrollment passed | private DRM reads and enrollment logs |
| Kernel | eight patches replayed to exact final Git tree | source repository, build logs and boot images |
| Camera | exact Candidate 24 hash; launch/mode/media/thermal matrix passed | private APK history, logs, screenshots and media |
| Charging | battery replacement resolved behavior | owner observation and device follow-up |

Private evidence is intentionally not a release dependency. Reproducible
public hashes, source patches, tools and test procedures let another owner
generate their own evidence without receiving this handset's data.

