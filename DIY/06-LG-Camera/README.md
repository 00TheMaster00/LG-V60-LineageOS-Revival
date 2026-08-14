# Reconstruct and Install LG Camera Candidate 24

Candidate 24 is the tested LG Camera 9.91.3 adaptation for the documented LG
V60 LineageOS 23.2/Android 16 baseline. The complete APK is not distributed.
This directory supplies a verified binary transformation: you provide the
exact EA40g stock APK you are entitled to use, and the builder reconstructs
the byte-exact tested output locally.

Reviewers are not limited to trusting a binary delta. The
[source-audit path](SOURCE-AUDIT.md) verifies every changed APK entry, 106
semantic Smali files and affected method signatures locally. The ten
project-authored `classes3.dex` shims and JNI source are published under
[`source/`](source/); LG's proprietary decompiled tree is not.

## Exact artifact identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| EA40g stock `LGCameraApp.apk` | 106,673,076 | `65D69A9E0DB652F43E232EC4AE86DCFC11AC688E324C5103CAAB1FECB27807E8` |
| Supplied bsdiff delta | 13,676,109 | `4FB8A5D55E8E048AF737851D19CF98ABF1E2FC55F5AC119415E24746B3DCF485` |
| Candidate 24 output | 101,512,334 | `E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71` |

No near match is accepted. A different region, app version, repack, alignment
or signature produces a different hash and the builder stops before writing
an output.

## Part 1: obtain the exact stock APK

### Route A: pull it from an EA40g stock installation

This is the simplest route if you own an LG V60 currently running the tested
EA40g firmware.

1. Install current Android platform tools from Google.
2. Enable Developer options and USB debugging.
3. Connect the phone, unlock it and approve the RSA prompt.
4. List all attached devices:

```powershell
adb devices -l
```

5. Copy the LG V60's exact serial into `$Serial`. Do not use `adb -d` when a
   second device is connected.
6. Confirm identity and find the package path:

```powershell
$Serial = "REPLACE_WITH_LG_V60_ADB_SERIAL"
adb -s $Serial shell getprop ro.product.manufacturer
adb -s $Serial shell getprop ro.product.model
adb -s $Serial shell getprop ro.product.device
adb -s $Serial shell getprop ro.build.fingerprint
adb -s $Serial shell pm path com.lge.camera
```

7. The final command returns a line beginning `package:`. Copy only the path
   after that prefix and pull it:

```powershell
$RemoteApk = "/product/priv-app/LGCameraApp/LGCameraApp.apk"
New-Item -ItemType Directory -Force .\input | Out-Null
adb -s $Serial pull $RemoteApk .\input\LGCameraApp-EA40g-stock.apk
```

8. Verify it before continuing:

```powershell
(Get-Item .\input\LGCameraApp-EA40g-stock.apk).Length
(Get-FileHash -Algorithm SHA256 .\input\LGCameraApp-EA40g-stock.apk).Hash
```

Require the exact input size/hash in the table above. If `adb pull` is denied,
use Route B; do not change permissions on the stock partition merely to read
one APK.

### Route B: extract it from an owned EA40g KDZ

The tested KDZ input had SHA-256:

```text
0121958707A73152503769913C1B724317A9CC013164361D469339CA40C3ACDE
```

1. Obtain the EA40g KDZ through a lawful source and verify its full SHA-256.
2. Work on a copy. Keep at least 30 GiB free.
3. Use an auditable LG KDZ extractor. One maintained open-source route is
   SRLabs Extractor: <https://github.com/srlabs/extractor>.
4. Follow that project's current Docker/setup instructions, including its
   submodules, and extract the KDZ to a new empty folder. Record the extractor
   commit used.
5. Locate the dynamic `super` image in the output. If the extractor already
   expands dynamic partitions, skip to step 9.
6. Convert Android sparse `super` to raw only when `lpunpack` reports a sparse
   input. AOSP supplies `simg2img` and `lpunpack` in its dynamic-partition
   tools: <https://android.googlesource.com/platform/system/extras/+/refs/heads/master/partition_tools/>.
7. Unpack the raw image into an empty folder:

```bash
mkdir -p super-unpacked
lpunpack super.raw.img super-unpacked
find super-unpacked -maxdepth 1 -type f -printf '%f\n'
```

8. Locate `product.img` or `product_a.img`. Mount it read-only if the host
   supports its filesystem. For ext4:

```bash
mkdir -p product-ro
sudo mount -o ro,loop super-unpacked/product_a.img product-ro
```

   For EROFS, use a current `erofs-utils` read-only mount or extraction method.
9. Copy only this file from the product filesystem:

```text
/priv-app/LGCameraApp/LGCameraApp.apk
```

10. Unmount the image and hash the copied APK. Require the exact input
    size/hash above.

Extraction tools evolve, so their current README is authoritative for setup.
The immutable acceptance gate is the APK hash, not a folder name or screenshot.

## Part 2: create an isolated Python environment

Open PowerShell in `DIY/06-LG-Camera`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --no-binary=bsdiff4 --require-hashes `
  -r requirements-camera-hashed.txt
```

If PowerShell blocks only the activation script, use the interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-binary=bsdiff4 --require-hashes `
  -r requirements-camera-hashed.txt
```

Do not install a similarly named package from an arbitrary site.

## Part 3: reconstruct Candidate 24

```powershell
.\Build-Candidate24.ps1 `
  -StockApk .\input\LGCameraApp-EA40g-stock.apk `
  -OutputApk .\output\LGCameraApp-Candidate24.apk
```

Or invoke Python directly:

```powershell
python .\tools\build_candidate24.py `
  --stock .\input\LGCameraApp-EA40g-stock.apk `
  --patch .\patches\EA40g-to-Candidate24.bsdiff `
  --output .\output\LGCameraApp-Candidate24.apk
```

The builder performs these gates in order:

1. stock APK exists;
2. stock byte count matches;
3. stock SHA-256 matches;
4. delta byte count and SHA-256 match;
5. patching occurs into a temporary file beside the output;
6. generated byte count and SHA-256 match Candidate 24; and
7. only then is the temporary file atomically renamed to the requested output.

An existing output is not overwritten unless `--force`/`-Force` is explicit.

## Part 4: verify Android compatibility and signature

Candidate 24 is ZIP-aligned and APK Signature Scheme v3 signed. Its signing
certificate SHA-256 is:

```text
1E08A903AEF9C3A721510B64EC764D01D3D094EB954161B62544EA8F187B5953
```

With Android SDK Build Tools installed:

```powershell
apksigner verify --verbose --print-certs .\output\LGCameraApp-Candidate24.apk
zipalign -c -v 4 .\output\LGCameraApp-Candidate24.apk
```

Require v3 verification, successful alignment, the certificate hash above and
the Candidate 24 file hash. The certificate is a project/debug certificate,
not LG's production certificate. This is why an LG-signed installed package
cannot be updated in place.

## Part 5: inspect and back up the current installation

1. Back up all photos/videos through normal file copy first.
2. List devices again and bind every command to the LG serial.
3. Confirm the target is `timelm`/LG V60 and record the ROM/vendor build:

```powershell
$Serial = "REPLACE_WITH_LG_V60_ADB_SERIAL"
adb -s $Serial shell getprop ro.product.manufacturer
adb -s $Serial shell getprop ro.product.model
adb -s $Serial shell getprop ro.product.device
adb -s $Serial shell getprop ro.lineage.version
adb -s $Serial shell getprop ro.vendor.build.fingerprint
adb -s $Serial shell pm path com.lge.camera
```

4. If the package exists, pull its installed base APK before uninstalling:

```powershell
New-Item -ItemType Directory -Force .\private-backup | Out-Null
$PackageLine = adb -s $Serial shell pm path com.lge.camera
$InstalledPath = ($PackageLine | Select-String '^package:').Line.Substring(8).Trim()
if ($InstalledPath) {
  adb -s $Serial pull $InstalledPath .\private-backup\camera-before.apk
  Get-FileHash -Algorithm SHA256 .\private-backup\camera-before.apk
}
```

Keep that backup private if its provenance/license is uncertain. Copy it away
from the Git checkout; `*.apk` is ignored but should not be trusted as the only
safeguard.

## Part 6: install

First try a non-destructive update:

```powershell
adb -s $Serial install -r -g .\output\LGCameraApp-Candidate24.apk
```

If Android reports `INSTALL_FAILED_UPDATE_INCOMPATIBLE`, the existing package
uses LG's or another build's signature. After confirming the backup above,
uninstall only this package and install Candidate 24:

```powershell
adb -s $Serial uninstall com.lge.camera
adb -s $Serial install -r -g .\output\LGCameraApp-Candidate24.apk
```

Uninstalling clears LG Camera's app settings/data. It does not delete normal
DCIM media, but the independent media backup remains mandatory.

Do not copy the APK into `/system`, `/product` or `/vendor`. The proven
Lineage result is a normal user-installed package. Do not disable SELinux or
flash a camera partition.

## Part 7: first-launch checks

```powershell
adb -s $Serial shell pm clear com.lge.camera
adb -s $Serial logcat -c
adb -s $Serial shell monkey -p com.lge.camera -c android.intent.category.LAUNCHER 1
Start-Sleep -Seconds 10
adb -s $Serial shell dumpsys activity activities | Select-String 'mResumedActivity|com.lge.camera'
adb -s $Serial logcat -d -v threadtime > .\camera-first-launch.log
```

Grant Camera, Microphone, Photos/Videos and Location only as desired. `pm
clear` is optional after a completely fresh install and destructive to app
settings, so do not repeat it during ordinary updates.

Inspect the log for `FATAL EXCEPTION`, `AndroidRuntime`, `VerifyError`,
`SecurityException`, camera-provider death and media-recorder failures. Logs
can include local filenames and location metadata; sanitize before sharing.

## Part 8: validate every feature

Use [VALIDATION.md](VALIDATION.md) exactly. Test basic photo and 1080p video
before 4K60 or 8K. Keep the phone cool, ensure tens of gigabytes are free, and
do not stress 8K while using the 670 MHz GPU profile.

For engineering or security review, run [SOURCE-AUDIT.md](SOURCE-AUDIT.md)
against the exact stock and reconstructed APKs before installation.

## Rollback

If Candidate 24 is unstable:

```powershell
adb -s $Serial uninstall com.lge.camera
adb -s $Serial install -r -g .\private-backup\camera-before.apk
```

If the prior app was a package baked into the current ROM instead of a pulled
user APK, re-enable its existing system package after uninstalling the update:

```powershell
adb -s $Serial shell cmd package install-existing --user 0 com.lge.camera
```

Never use a rollback APK from another phone when you can recover the exact
one you backed up.

## What remains outside Candidate 24

Candidate 24 does not claim true ToF Portrait, RAW/DNG, 64 MP remosaic,
physical-ultrawide Video, a guaranteed 8K thumbnail, or the missing proprietary
dependencies behind Food/Cine modes. See the exact matrix in
[VALIDATION.md](VALIDATION.md) and the engineering narrative in
`Research/04-Camera-Restoration/`.
