# Response to the 2026-08 Public Reproducibility Audit

External reviews rated the engineering work highly but identified material
public-release weaknesses in the original and follow-up audits. This file
records the response without pretending that repository changes can replace
independent device testing.

| Finding | Response | Current status |
|---|---|---|
| Backup verifier missed extra files | Verifier now compares the manifest set to every actual backup file and also rejects duplicate rows, invalid sizes/hashes and unsafe paths. A regression test adds an unexpected file. | Fixed and tested |
| Performance V1 build omitted the kernel Image | The full-V2 path now builds `Image.gz`, installs it as the repacked boot kernel and proves its hash. The separate GPU-only-on-existing-V1 path is explicitly distinguished. | Fixed in procedure |
| Runtime profiles had no installer/baseline capture | Added explicit-serial host installer, `timelm`/root gates, hash-checked root install, baseline capture, existing-baseline preservation and fail-closed restore/write behavior. | Fixed and syntax-tested; new-device runtime report requested |
| Camera CI did not perform a successful patch | CI now executes a successful synthetic bsdiff path plus rejection/atomicity tests. The exact proprietary-input reconstruction remains owner-run and is labeled as such. | Test gap narrowed; legal input boundary remains |
| Camera delta was not source-auditable | Added exact 25-entry APK manifest, 106-file semantic Smali manifest, local method-inventory tool, ten project-authored classes3 sources and JNI source. | Materially fixed; proprietary LG bodies remain local-only |
| Decisive evidence was private and single-device | Proof vocabulary and single-device status are explicit; a sanitized reproduction issue form specifies acceptable evidence. | Transparently bounded; independent reports still needed |
| Cross-flash route sounded universal | Renamed it a conversion case-study route and retained the refusal to publish copied sector coordinates. | Fixed in claims; intentionally not a universal flasher |
| Repository governance was immature | Added Code Owners, Dependabot configuration, immutable Action SHAs, read-only workflow permissions, security/supply-chain guidance and a pinning regression test. An active `Protect main` ruleset now requires pull requests and the current `validate` check while blocking force pushes and deletion. | Materially fixed; a signed future release remains pending |
| Privacy CI skipped `private`/`logs`/`input`/`output` | Audit and manifest now use Git's publishable file set, which includes force-added ignored files. Source-archive fallback scans those directory names too. Regression test proves a force-added ignored file is scanned. | Fixed and tested |
| Daily mode could restore a 670 MHz baseline despite claiming a 587 MHz cap | Daily and CPU-MAX now explicitly select the highest exposed GPU frequency at or below 587 MHz, reset forced KGSL votes and restore automatic GPU-bandwidth scaling. A regression test guards both mode paths. | Fixed and tested |
| Published JNI C++ lacked a reproducible native build | Added exact AOSP Clang/libnativehelper pins, deterministic link stubs, compile/link commands, object/library hashes and ELF-interface checks. The documented owner-run rebuild reproduces the 3,872-byte Candidate 24 entry exactly. | Fixed; exact rebuild proven owner-side |
| Backup manifest generator could follow a symbolic link before the verifier rejected it | The generator now rejects a symlink root, output or nested entry before reading any linked bytes; a regression test covers the nested-file case. | Fixed and tested |
| PowerShell installer parsing was owner-run only | The same parser gate now runs in the public `validate` GitHub Actions job. | Fixed in public CI |
| Charging language overstated causality | Claims now say battery replacement resolved the observed behavior and that this is consistent with aging, without asserting a uniquely isolated cause. | Fixed in documentation |

## Validation performed after the response

- camera builder/audit tests: 7 passing;
- recovery verifier tests: 3 passing where symlink creation is available;
- public-file/governance tests: 2 passing;
- performance shell/Python syntax and functional tests: passing;
- exact owner-run Candidate 24 APK-entry audit: 25/25 changes matched;
- exact owner-run Candidate 24 semantic Smali audit: 106/106 files matched;
- exact owner-run JNI rebuild: object and 3,872-byte library hashes matched;
- PowerShell installer parser: passing locally and enforced in public CI;
- public release/privacy audit: passing;
- local Markdown links: passing; and
- deterministic release manifest: passing.

## Still required for a mature community release

1. Publish the next release from a reviewed CI-passing commit with a signed
   tag when the maintainer has configured a signing identity.
2. Obtain at least two independent A001LG/V60 reproduction reports, including
   one clean camera reconstruction and one performance-profile installation.
3. Promote compatibility claims only after those reports identify ROM/vendor
   combinations and real output or physical behavior, not just UI entry.
