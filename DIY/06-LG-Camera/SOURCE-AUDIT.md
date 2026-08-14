# Audit Candidate 24 at APK, DEX and Smali Level

The binary delta is the installation/reconstruction mechanism, not the only
technical evidence. This path lets a reviewer inspect the exact changed APK
entries, classes and methods locally after reconstructing Candidate 24. No LG
source, APK entry or decompiled tree is uploaded by the tools.

## What is public

- `audit/expected-apk-entry-changes.csv` pins every added, changed and deleted
  uncompressed APK entry by name, size and SHA-256.
- `audit/expected-smali-changes.csv` pins every semantically added or changed
  Smali file by normalized SHA-256.
- `tools/audit_apk_entries.py` verifies the exact package-level inventory.
- `tools/audit_smali_changes.py` ignores only non-executable debug directives
  such as `.line`/`.local`, verifies the exact semantic inventory, and can
  print every changed method signature.
- `source/classes3/` contains the ten project-authored compatibility shims
  added as `classes3.dex`.
- `source/native/` contains the project-authored JNI source plus a pinned
  byte-exact build and ELF/hash verification recipe for
  `liblgcamera_surface_usage.so`.

The repository still does not publish LG's decompiled application or the
proprietary `libmpbase.so` dependency. The exact `libmpbase.so` entry identity
is nevertheless pinned in the APK-entry manifest and can be examined locally
inside the reconstructed APK.

## 1. Reconstruct and verify both APKs

Follow [the Candidate 24 builder](README.md). Require these exact identities:

```text
stock:     65D69A9E0DB652F43E232EC4AE86DCFC11AC688E324C5103CAAB1FECB27807E8
candidate: E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71
```

Then run the package-level audit:

```powershell
python .\tools\audit_apk_entries.py `
  --stock .\input\LGCameraApp-EA40g-stock.apk `
  --candidate .\output\LGCameraApp-Candidate24.apk
```

Expected result:

```text
APK ENTRY AUDIT: PASS (25 entries: 5 added, 18 changed, 2 deleted)
```

This comparison hashes uncompressed ZIP-entry bytes, so changes in ZIP order,
timestamps or compression alone do not masquerade as application changes.

## 2. Disassemble the DEX files locally

Use the official Smali/Baksmali 3.0.9 release or build that exact tag from
<https://github.com/baksmali/smali/releases/tag/3.0.9>. Record the JAR hash.
Extract the APKs into private work directories; `python -m zipfile` is enough:

```powershell
python -m zipfile -e .\input\LGCameraApp-EA40g-stock.apk .\audit-work\stock-dex
python -m zipfile -e .\output\LGCameraApp-Candidate24.apk .\audit-work\candidate-dex
```

Disassemble every `classes*.dex` into a directory named after the DEX. In a
Linux/macOS shell, with `BAKSMALI_JAR` set to the verified 3.0.9 JAR:

```bash
mkdir -p audit-work/stock-smali audit-work/candidate-smali
for dex in audit-work/stock-dex/classes*.dex; do
  name="$(basename "$dex" .dex)"
  java -jar "$BAKSMALI_JAR" disassemble "$dex" \
    --output "audit-work/stock-smali/$name"
done
for dex in audit-work/candidate-dex/classes*.dex; do
  name="$(basename "$dex" .dex)"
  java -jar "$BAKSMALI_JAR" disassemble "$dex" \
    --output "audit-work/candidate-smali/$name"
done
```

The resulting roots must contain `classes/`, `classes2/` and, for Candidate
24, `classes3/`. Keep these trees private: the stock tree is proprietary.

## 3. Verify the exact semantic change inventory

```powershell
python .\tools\audit_smali_changes.py `
  --stock .\audit-work\stock-smali `
  --candidate .\audit-work\candidate-smali
```

Expected result:

```text
SMALI SOURCE AUDIT: PASS (106 semantic files: 10 added, 96 changed, 0 deleted)
```

To print the affected method signatures without printing method bodies:

```powershell
python .\tools\audit_smali_changes.py `
  --stock .\audit-work\stock-smali `
  --candidate .\audit-work\candidate-smali `
  --show-methods
```

After the manifest passes, use a local directory diff on the specific classes
you want to review. Do not paste or commit the proprietary output. The public
[engineering notebook](../../Research/04-Camera-Restoration/ENGINEERING-NOTEBOOK.md)
maps the important classes and candidates to their runtime reason and proof.

## 4. Rebuild the project-authored native library

Follow [`source/native/NATIVE-BUILD.md`](source/native/NATIVE-BUILD.md) with
the exact pinned AOSP Clang and `libnativehelper` commits. The script must
produce:

```text
surface_usage_shim.o:
  750DB38B0124A43143F142144B768AF73CC8FE0031FD6D58356C2C7EBD9812DC
liblgcamera_surface_usage.so (3,872 bytes):
  6C10BF25D9CFE3C719851D0F2951F02F06B2A47BE90E0A498509E2B9826CA5D1
```

The second hash is the exact Candidate 24 APK-entry identity. The recipe also
checks the SONAME, dependencies, exported JNI symbol, versioned loader imports
and immediate-binding flag. This proves the published C++ source can produce
the shipped native entry; it does not prove runtime compatibility on every
ROM/vendor combination.

## What CI can and cannot prove

Public CI runs successful synthetic patching, rejection gates, audit-tool
tests, native-recipe pin/syntax checks, manifest checks and privacy checks. It
cannot legally conjure the proprietary 106 MB stock APK or economically fetch
the large pinned AOSP toolchain, so exact APK reconstruction and native binary
rebuild remain owner-run gates. An independent reproduction report is still
required before this is called multi-device validated.
