# Exact Build, DTB Replacement and Boot Repack Procedure

This is the portable form of the recorded private workflow. It intentionally
does not contain a runnable flash command with somebody else's serial, slot or
hash. Every placeholder must be derived from the target phone.

## 1. Create a native Linux/WSL workspace

Build on a native Linux filesystem rather than `/mnt/c` or another Windows
mount; the source tree contains hundreds of symlinks.

```bash
mkdir -p "$HOME/v60-work"/{source,toolchains,build,backup,logs}
cd "$HOME/v60-work/source"
git clone https://github.com/LineageOS/android_kernel_lge_sm8250.git
git clone https://github.com/LineageOS/android_device_lge_timelm.git
```

Pin the exact revisions:

```bash
git -C android_kernel_lge_sm8250 checkout --detach \
  29902cf733dcb4d0558ad5bd8c2eb8ba6e2077d2
git -C android_device_lge_timelm checkout --detach \
  21d4520b4dc69025b46baa6eeead3249b4f5e6a6
git -C android_kernel_lge_sm8250 status --short
```

The recorded compiler was AOSP Clang r563880c:

```text
Android (14054515, +pgo, +bolt, +lto, +mlgo, based on r563880c) clang 21.0.0
LLVM revision 5e96669f06077099aa41290cdb4c5e6fa0f59349
```

Obtain that toolchain from official/AOSP infrastructure, verify it, and place
it outside the source tree. Confirm `clang --version` exactly.

## 2. Capture the current boot/config without ambiguity

List devices and set the LG V60 serial explicitly:

```bash
adb devices -l
export V60_SERIAL='REPLACE_WITH_LG_V60_SERIAL'
adb -s "$V60_SERIAL" shell getprop ro.product.device
adb -s "$V60_SERIAL" shell getprop ro.boot.slot_suffix
```

Set `V60_SLOT` from the returned `_a` or `_b`, then derive the partition name:

```bash
export V60_SLOT='_b'                         # example only
export V60_BOOT="boot${V60_SLOT}"           # becomes boot_b in this example
```

Require root and confirm the by-name target resolves:

```bash
adb -s "$V60_SERIAL" shell su -c id
adb -s "$V60_SERIAL" shell su -c \
  "readlink -f /dev/block/by-name/$V60_BOOT; stat -c %s /dev/block/by-name/$V60_BOOT"
```

Create a device-side read, hash it, pull it, then compare host size/hash:

```bash
adb -s "$V60_SERIAL" shell su -c \
  "dd if=/dev/block/by-name/$V60_BOOT of=/data/local/tmp/v60-boot-before.img bs=4M && sync && sha256sum /data/local/tmp/v60-boot-before.img"
adb -s "$V60_SERIAL" pull /data/local/tmp/v60-boot-before.img \
  "$HOME/v60-work/backup/$V60_BOOT-before.img"
sha256sum "$HOME/v60-work/backup/$V60_BOOT-before.img"
stat -c %s "$HOME/v60-work/backup/$V60_BOOT-before.img"
adb -s "$V60_SERIAL" shell rm -f /data/local/tmp/v60-boot-before.img
```

Store the measured hash in a private variable. Do not use a hash from this
repository. Extract `/proc/config.gz` when available:

```bash
adb -s "$V60_SERIAL" shell su -c 'cat /proc/config.gz' > running-config.gz
gzip -dc running-config.gz > running.config
sha256sum running.config
```

If `/proc/config.gz` is disabled, extract the config from the exact current
kernel using a trusted `extract-ikconfig` tool and verify semantic equivalence.

## 3. Apply only the two release patches

```bash
cd "$HOME/v60-work/source/android_kernel_lge_sm8250"
git apply --check /path/to/patches/0001-V60-performance-v1.patch
git am /path/to/patches/0001-V60-performance-v1.patch
git apply --check /path/to/patches/0002-arm64-dts-kona-enable-existing-670MHz-GPU-OPP-for-sp.patch
git am /path/to/patches/0002-arm64-dts-kona-enable-existing-670MHz-GPU-OPP-for-sp.patch
git log --oneline -3
```

Do not apply fingerprint experiment patches 0003-0008.

## 4. Build with the recorded identity

```bash
export KERNEL_SOURCE="$HOME/v60-work/source/android_kernel_lge_sm8250"
export TOOLCHAIN="$HOME/v60-work/toolchains/clang-r563880c"
export BUILD_OUT="$HOME/v60-work/build/gpu670"
mkdir -p "$BUILD_OUT"
cp running.config "$BUILD_OUT/.config"
export PATH="$TOOLCHAIN/bin:$PATH"

make -C "$KERNEL_SOURCE" O="$BUILD_OUT" \
  ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  CC=clang LD=ld.lld AR=llvm-ar NM=llvm-nm \
  OBJCOPY=llvm-objcopy OBJDUMP=llvm-objdump \
  READELF=llvm-readelf STRIP=llvm-strip \
  HOSTCC=clang HOSTCXX=clang++ \
  KBUILD_BUILD_USER=root KBUILD_BUILD_HOST=77ba96dd40aa \
  KBUILD_BUILD_VERSION=1 \
  KBUILD_BUILD_TIMESTAMP='Sun Jul 26 00:43:22 UTC 2026' \
  olddefconfig

make -s -C "$KERNEL_SOURCE" O="$BUILD_OUT" \
  ARCH=arm64 LLVM=1 LLVM_IAS=1 kernelrelease
```

The recorded baseline release was
`4.19.325-cip133-st17-perf-g29902cf733dc`. A local ELF/Image may still differ
byte-for-byte because absolute build paths can enter debug data; source,
semantic config, compiler, release and metadata identity remain required.

Build the two Kona-v2 DTBs:

```bash
make -C "$KERNEL_SOURCE" O="$BUILD_OUT" -j"$(nproc)" \
  ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  CC=clang LD=ld.lld AR=llvm-ar NM=llvm-nm \
  OBJCOPY=llvm-objcopy OBJDUMP=llvm-objdump \
  READELF=llvm-readelf STRIP=llvm-strip \
  qcom/kona-v2.dtb qcom/kona-v2.1.dtb

find "$BUILD_OUT/arch/arm64/boot/dts" -type f \
  \( -name 'kona-v2.dtb' -o -name 'kona-v2.1.dtb' \) \
  -print0 | xargs -0 sha256sum
```

Decompile each candidate with `dtc -I dtb -O dts` and verify speed-bin 0 has
the exact 670/587/525/490/441600/400/305/0 ladder and unchanged vendor voltage
corners/bandwidth votes.

## 5. Unpack the current boot image without flashing

Use the `magiskboot` belonging to the running Magisk installation so its
repack behavior matches the rooted boot image. Push the verified backup, copy
it to a temporary directory, then run:

```sh
magiskboot unpack -h boot-before.img
sha256sum header kernel ramdisk.cpio dtb
```

Pull `header`, `kernel`, `ramdisk.cpio` and `dtb` back to the host. Keep all
component hashes. The project preserved kernel and ramdisk byte-for-byte and
replaced one indexed FDT entry only.

## 6. Identify the active FDT entry

From this repository's performance workflow directory:

```bash
python3 workflow/tools/fdt-bundle.py list /path/to/unpacked/dtb
python3 workflow/tools/fdt-bundle.py split \
  /path/to/unpacked/dtb /path/to/dtb-entries
```

Compare every entry's model, compatible string and Qualcomm IDs to the live
tree:

```bash
adb -s "$V60_SERIAL" shell su -c \
  'tr -d "\000" < /proc/device-tree/model; echo; tr "\000" " " < /proc/device-tree/compatible; echo'
```

Never assume the documented entry index. Select the unique entry matching the
live handset and save the evidence.

Replace that 1-based entry only:

```bash
python3 workflow/tools/fdt-bundle.py replace \
  /path/to/unpacked/dtb MATCHED_INDEX /path/to/kona-v2.dtb \
  /path/to/new-dtb-bundle
```

Split the new bundle and require every non-target entry hash to match the old
bundle.

## 7. Repack and prove component preservation

Inside a copy of the unpack directory, replace only the file named `dtb`, then:

```sh
magiskboot repack boot-before.img boot-gpu670.img
```

Unpack `boot-gpu670.img` into a second empty directory. Require:

- output size equals the live boot partition size;
- header hash unchanged;
- kernel hash unchanged;
- ramdisk hash unchanged;
- DTB hash equals `new-dtb-bundle`;
- output SHA-256 recorded; and
- the rollback image remains the untouched pre-write boot backup.

## 8. Flash gate and rollback design

Flashing is intentionally not a copyable command in this public workflow.
Before any write, a reviewer must confirm the exact serial, active/test slot,
by-name partition, current boot hash, input size/hash and recovery route.

The private proven operation used an explicit confirmation token, wrote only
the isolated boot slot, synced, re-hashed the live partition, and immediately
restored the verified old image if the new hash differed. Reproduce those
semantics with your own measured values; do not substitute a hardcoded slot.

After boot, verify boot partition hash, kernel release, available GPU
frequencies, Wi-Fi/LTE/audio/camera/fingerprint, thermal health and logs before
installing runtime profiles.

