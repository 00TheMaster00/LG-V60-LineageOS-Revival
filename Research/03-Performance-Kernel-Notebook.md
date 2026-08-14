# Performance Kernel Engineering Notebook

This notebook expands the compact performance summary into the source,
build-failure, DTB-selection, boot-repack and validation reasoning used by the
project. Private boot images, device identifiers and handset-bound flash
scripts are not published. The public patches and portable tools are under
[DIY/05-Performance-Kernel](../DIY/05-Performance-Kernel/README.md).

## Goal and final boundary

The project produced two independent changes:

1. **Performance V1:** keep all CPUs available to core control and change
   schedutil's default rate limits to 0 microseconds up / 10,000 microseconds
   down.
2. **Performance V2:** expose an already vendor-defined 670 MHz GPU operating
   point for speed bin 0 while retaining 587 MHz as the immediate fallback.

Qualcomm LMH/DCVSH and thermal protections were not disabled. The resulting
recommendation is intentionally conservative:

- 587 MHz for daily use and gaming;
- 670 MHz for benchmarks and supervised short bursts; and
- return to Daily after every MAX-profile run.

## Pinned source and build identity

```text
Kernel repository: https://github.com/LineageOS/android_kernel_lge_sm8250
Kernel base:       29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2
Device tree:       21d4520b4dc69025b46baa6eeead3249b4f5e6a6
Performance V1:    175901fa8aa5614cc50a695cdaa783a1bbfbba41
GPU 670 state:     00d8f9c3262c90159d7bc9ea65fa6dd45797895e
```

Recorded compiler:

```text
Android (14054515, +pgo, +bolt, +lto, +mlgo, based on r563880c) clang 21.0.0
LLVM project revision 5e96669f06077099aa41290cdb4c5e6fa0f59349
```

Recorded build metadata:

```text
KBUILD_BUILD_USER=root
KBUILD_BUILD_HOST=77ba96dd40aa
KBUILD_BUILD_VERSION=1
KBUILD_BUILD_TIMESTAMP=Sun Jul 26 00:43:22 UTC 2026
Expected kernelrelease=4.19.325-cip133-st17-perf-g29902cf733dc
Semantic config SHA-256=0bbf27c434e0959c1e06e15b8743392663ba9fd022da4ff4dae862549d587acf
```

The source was built on a native Linux/WSL filesystem. The audit found 503
expected and 503 correct symlinks with `core.symlinks=true`; Windows-mounted
source trees can materialize symlinks incorrectly and embed different paths.

## Why byte-identical full-kernel reproduction was not required for V2

Two local builds with the same semantic configuration and metadata had the
same size as the extracted reference kernel but differed in many byte ranges.
String/path analysis showed local absolute source paths in debug data. This
established that matching source, configuration, compiler, release and build
metadata does not guarantee a byte-identical kernel when build paths enter
debug sections.

Performance V2 avoided that uncertainty: it preserved the already working V1
header, kernel and Magisk ramdisk byte-for-byte and rebuilt only the selected
DTB entry.

## Build failures and reusable lessons

### Unrelated overlay failure

The first combined `Image.gz dtbs` build ended in the LG DCM Japan overlay:

```text
DTC arch/arm64/boot/dts/vendor/lge/kona-timelm_dcm_jp_rev-0.0-overlay.dtbo
ERROR: Input tree has errors, aborting
make ... dtbs Error 2
```

The needed V2 outputs were `kona-v2.dtb` and `kona-v2.1.dtb`, not every carrier
overlay. Building those explicit targets isolated the relevant Qualcomm DTBs
without pretending the unrelated overlay error was fixed.

### Orchestration mistakes

The project retained these failures because they generalize:

- long interactive PowerShell/WSL heredocs were truncated or mixed with
  prompts; final work used standalone scripts plus syntax checks;
- command substitution `$()` was accidentally used where arithmetic `$(( ))`
  was required for DTB-bundle size;
- an in-place Python rewrite truncated the only host copy before throwing;
  later edits use a temporary sibling, validation and atomic rename;
- Windows `adb.exe` added carriage returns, breaking exact shell comparisons
  and anchored PASS markers until `\r` normalization was added;
- `set -euo pipefail` in an interactive WSL shell caused an unexpected exit
  back to PowerShell; strict mode belongs inside the script;
- a silent 90-second retry hid the mismatched value; final checks print every
  mismatch immediately;
- a validator overfit 52 transient sysfs nodes even though Android legitimately
  changes CPU minimum and schedtune state; stable invariants are the real gate;
- requiring the GPU governor string `performance` was wrong because the proven
  lock kept `msm-adreno-tz` while min/max/current/pwrlevel/force/bandwidth state
  all demonstrated 670 MHz.

## CPU LMH/DCVSH investigation

The tracing experiment enabled:

- `events/lmh/lmh_dcvs_freq`;
- `events/dcvsh/dcvsh_freq`; and
- `events/power/cpu_frequency`.

A CPU7-pinned load reported 2.8416 GHz through cpufreq while DCVSH repeatedly
reported a 1.632 GHz maximum. CPU4 also saw temporary DCVSH ceilings such as
1.3824 GHz before returning to 2.4192 GHz. Source mapping in
`drivers/cpufreq/qcom-cpufreq-hw.c` showed how hardware-domain state updates
`dcvsh_freq_limit` and emits the tracepoint.

Therefore CPU-MAX and ALL-MAX request maximum exposed policy values; they do
not and cannot honestly claim that the hardware limiter is bypassed. The
project kept LMH/DCVSH because it is part of Qualcomm's voltage/current/thermal
protection design.

## GPU source finding

The decisive file is:

```text
arch/arm64/boot/dts/vendor/qcom/kona-v2-gpu.dtsi
```

The common OPP table already contained:

| Frequency | Vendor voltage level |
|---:|---|
| 670 MHz | `RPMH_REGULATOR_LEVEL_NOM_L1` |
| 587 MHz | `RPMH_REGULATOR_LEVEL_NOM` |
| 525 MHz | `RPMH_REGULATOR_LEVEL_SVS_L2` |
| 490 MHz | `RPMH_REGULATOR_LEVEL_SVS_L1` |
| 441.6 MHz | `RPMH_REGULATOR_LEVEL_SVS_L0` |
| 400 MHz | `RPMH_REGULATOR_LEVEL_SVS` |
| 305 MHz | `RPMH_REGULATOR_LEVEL_LOW_SVS` |

Speed bin 0 originally began at 587 MHz. Speed bin 1 already carried the
complete 670/587/525/490/441.6/400/305/0 MHz ladder, DDR7/DDR8 votes and ACD
values. The release patch clones that complete vendor ladder into the speed
bin 0 node and changes the speed-bin identifier back to 0.

This avoids unsafe partial changes such as inventing a voltage, adding only a
frequency, omitting bus votes, reusing the wrong `reg` indices or removing the
587 MHz fallback. The top entry remains vendor-authored:

```dts
qcom,gpu-pwrlevel@0 {
    reg = <0>;
    qcom,gpu-freq = <670000000>;
    qcom,bus-freq-ddr7 = <11>;
    qcom,bus-min-ddr7 = <11>;
    qcom,bus-max-ddr7 = <11>;
    qcom,bus-freq-ddr8 = <11>;
    qcom,bus-min-ddr8 = <11>;
    qcom,bus-max-ddr8 = <11>;
    qcom,acd-level = <0x802b5ffd>;
};
```

670 MHz was the stopping point because it was the highest complete OPP in the
captured vendor source. Higher clocks would be a new experimental
clock/voltage decision rather than this evidence-backed promotion.

## Targeted DTB build

The recorded patched outputs were:

| File | Bytes | SHA-256 |
|---|---:|---|
| `kona-v2.1.dtb` | 537,971 | `7174DC52374E9076F8E61DAF5FA4C92D2ED5AFDBE6AF2404DA952E677D034BC` |
| `kona-v2.dtb` | 537,967 | `929844DFE833CA379D81CB0F769299370D32F254CE1472935EE3174162373159` |

The documented handset matched the v2.1 candidate and the first entry in its
three-DTB boot bundle. That index is not portable. Every reproduction must:

1. split its own current boot bundle from FDT headers;
2. hash every entry;
3. compare live `/proc/device-tree` model/compatible/Qualcomm identifiers;
4. select one unique matching entry;
5. replace only that entry; and
6. prove every unaffected entry remains byte-identical.

The supplied `fdt-bundle.py` implements list, split and exact indexed
replacement with functional tests.

## Magisk-preserving boot repack

The boot image construction gate is:

1. read and hash the current target boot partition;
2. unpack with the MagiskBoot matching the installed Magisk state;
3. preserve header, kernel and ramdisk;
4. replace the one selected DTB entry;
5. repack to the full live partition size;
6. unpack the output again; and
7. compare component hashes before any write.

The documented development manifest was:

```text
V1 rollback image:
  bytes=100663296
  sha256=3BFD26A6D0F55FBB202EDB4AAC3E4ECE220D6603607A7C0BD4726277F722F205

V2 image:
  bytes=100663296
  sha256=545CE4882F39A93F9A48B276D1C412E1B8A4B150039B9D548E093C04184FA805

Unchanged components:
  header=A557F843395EE1479BC91C8583408ACF24228C3DE41770230004FD6F6859D3F7
  kernel=8E2A74C227B4B1040145BF5BA3E6C9A4C8BDEB963DEBAA0BB412BA20C319F0A9
  ramdisk=B93F53C49CDECC90EFFB7170B1C329EC5CAEF0EE7D3E04940FE28343CCA7D50B
```

Those values document the tested handset's result. They are not authorization
to flash a downloaded boot image and the images themselves are not public.

## Slot isolation and rollback semantics

The proven operation used slot B while retaining the other slot as part of
the recovery design. The write wrapper verified root, active slot, input size
and hash, and current full-block hash; wrote only the intended boot slot;
synced; hashed the complete live block; and restored V1 automatically if the
write/readback did not match.

After boot, success required all of:

```text
intended active slot
full live boot hash equals the locally approved V2 image
Android boot completed
available_frequencies includes 670000000 then 587000000
no immediate KGSL/GMU fault
core radio/camera/fingerprint functionality survives
```

A successful boot alone cannot prove that the intended image or DTB entry was
used.

## Runtime profiles

The public profiles capture a clean baseline and restore it before applying
overrides. This fixed an older “Daily” script that restored GPU min/max but
left scheduler boost enabled and changed `force_no_nap` from the clean state.

| Profile | Main behavior |
|---|---|
| Daily | Restore captured stable baseline; adaptive GPU, 305-587 MHz |
| Power Save | Lower CPU caps, adaptive 305-400 MHz GPU, Android saver state |
| CPU-MAX | Maximum exposed CPU policy request; GPU restored to Daily |
| GPU-MAX | CPU restored to Daily; GPU min=max=670 MHz; force and bandwidth state applied |
| ALL-MAX | CPU-MAX plus GPU-MAX |
| Status | Print slot, kernel, CPU/GPU/bandwidth/scheduler and temperature state |

Android can legitimately change transient nodes after restoration. Validation
checks stable invariants and actual writes rather than requiring every sampled
value to remain frozen.

## Benchmark and stability evidence

At 587 MHz with GPU bandwidth pinned at 7980, the documented Wild Life score
was 3876 versus an observed reference median of 3855.

The first 670 MHz short test stayed at 670 for all 30 samples and returned no
matching KGSL/Adreno/GMU fault, hang, timeout, page fault or snapshot message.
After a real Wild Life pass, status still showed:

```text
profile=gpu-max-670
cur_freq=670000000
min_freq=670000000
max_freq=670000000
GPU bandwidth current/minimum/maximum=7980
battery temperature=35.4 C
```

The final numeric 670 MHz benchmark score was not retained. Later owner use
found 670 MHz good for benchmarks but mildly unstable in gaming, which is why
587 MHz remains the daily recommendation.

## Reproduction acceptance checklist

- Exact source/device-tree commits and compiler identity recorded.
- Running semantic config captured from the target.
- Only the two public release patches applied.
- Targeted DTBs build and decompile to the expected frequency ladder.
- Unique live DTB entry selected from the target's own boot bundle.
- Header, kernel, ramdisk and unaffected DTB hashes remain identical.
- Output equals the live partition size and has an independently recorded
  hash.
- Rollback is verified and usable without Android reaching the home screen.
- Ten cold boots, ten warm reboots, deep sleep/wake, radio, Wi-Fi, Bluetooth,
  GPS, audio, camera and fingerprint pass.
- 587 MHz extended GPU/gaming tests pass before supervised 670 MHz work.
- No KGSL/GMU fault, thermal shutdown, visual corruption or unexplained reboot.
- Device is returned to Daily after testing.

