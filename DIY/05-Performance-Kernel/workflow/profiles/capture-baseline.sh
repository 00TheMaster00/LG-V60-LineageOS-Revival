#!/system/bin/sh
set -u

ROOT="${V60_PROFILE_ROOT:-/data/adb/v60profiles}"
OUT="$ROOT/baseline.nodes"
LOW_POWER_OUT="$ROOT/baseline.low_power"
META_OUT="$ROOT/baseline.meta"
FORCE=0

case "${1:-}" in
    "") ;;
    --force) FORCE=1 ;;
    *) echo "Usage: $0 [--force]"; exit 2 ;;
esac

[ "$(id -u)" = "0" ] || { echo "ERROR: Root required."; exit 10; }

DEVICE="$(getprop ro.product.device)"
VENDOR_DEVICE="$(getprop ro.product.vendor.device)"
case "$DEVICE $VENDOR_DEVICE" in
    *timelm*) ;;
    *) echo "ERROR: This profile set is only for LG V60/timelm; got '$DEVICE'/'$VENDOR_DEVICE'."; exit 11 ;;
esac

mkdir -p "$ROOT" || exit 12
chmod 700 "$ROOT" 2>/dev/null || true

if [ -e "$OUT" ] && [ "$FORCE" -ne 1 ]; then
    echo "ERROR: Baseline already exists: $OUT"
    echo "Apply Daily first, inspect the phone, then use --force only when recapturing intentionally."
    exit 13
fi

TMP="$ROOT/.baseline.nodes.$$"
SORTED_TMP="$ROOT/.baseline.nodes.sorted.$$"
LOW_POWER_TMP="$ROOT/.baseline.low_power.$$"
META_TMP="$ROOT/.baseline.meta.$$"
trap 'rm -f "$TMP" "$SORTED_TMP" "$LOW_POWER_TMP" "$META_TMP"' EXIT HUP INT TERM
: > "$TMP"

capture_node() {
    NODE="$1"
    [ -e "$NODE" ] || return 0
    [ -r "$NODE" ] || return 0
    [ -w "$NODE" ] || return 0
    VALUE="$(head -n 1 "$NODE" 2>/dev/null || true)"
    [ -n "$VALUE" ] || return 0
    case "$NODE$VALUE" in *'|'*) echo "SKIP unsafe delimiter: $NODE"; return 0 ;; esac
    printf '%s|%s\n' "$NODE" "$VALUE" >> "$TMP"
}

for NODE in /sys/devices/system/cpu/cpu[1-7]/online; do
    capture_node "$NODE"
done
for NODE in \
    /sys/devices/system/cpu/cpu*/core_ctl/enable \
    /sys/devices/system/cpu/cpu*/core_ctl/min_cpus \
    /sys/devices/system/cpu/cpu*/core_ctl/offline_delay_ms \
    /sys/devices/system/cpu/cpufreq/policy*/scaling_min_freq \
    /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq \
    /sys/devices/system/cpu/cpufreq/policy*/scaling_governor \
    /sys/devices/system/cpu/cpufreq/policy*/schedutil/up_rate_limit_us \
    /sys/devices/system/cpu/cpufreq/policy*/schedutil/down_rate_limit_us \
    /sys/class/kgsl/kgsl-3d0/devfreq/min_freq \
    /sys/class/kgsl/kgsl-3d0/devfreq/max_freq \
    /sys/class/kgsl/kgsl-3d0/devfreq/governor \
    /sys/class/kgsl/kgsl-3d0/max_pwrlevel \
    /sys/class/kgsl/kgsl-3d0/min_pwrlevel \
    /sys/class/kgsl/kgsl-3d0/default_pwrlevel \
    /sys/class/kgsl/kgsl-3d0/idle_timer \
    /sys/class/kgsl/kgsl-3d0/force_bus_on \
    /sys/class/kgsl/kgsl-3d0/force_clk_on \
    /sys/class/kgsl/kgsl-3d0/force_rail_on \
    /sys/class/kgsl/kgsl-3d0/force_no_nap \
    /proc/sys/kernel/sched_boost \
    /dev/stune/top-app/schedtune.boost \
    /dev/stune/top-app/schedtune.prefer_idle \
    /dev/stune/foreground/schedtune.boost \
    /dev/stune/foreground/schedtune.prefer_idle \
    /dev/cpuset/top-app/cpus \
    /dev/cpuset/foreground/cpus; do
    capture_node "$NODE"
done

for DIR in /sys/class/devfreq/*; do
    [ -d "$DIR" ] || continue
    NAME="$(cat "$DIR/name" 2>/dev/null || true)"
    case "$NAME $(basename "$DIR")" in
        *gpubw*)
            capture_node "$DIR/min_freq"
            capture_node "$DIR/max_freq"
            capture_node "$DIR/governor"
            ;;
    esac
done

sort -u "$TMP" > "$SORTED_TMP"
mv "$SORTED_TMP" "$TMP"
[ -s "$TMP" ] || { echo "ERROR: No writable performance nodes were captured."; exit 14; }

LOW_POWER="$(settings get global low_power 2>/dev/null || echo 0)"
case "$LOW_POWER" in 0|1) ;; *) LOW_POWER=0 ;; esac
printf '%s\n' "$LOW_POWER" > "$LOW_POWER_TMP"
{
    printf 'device=%s\n' "$DEVICE"
    printf 'vendor_device=%s\n' "$VENDOR_DEVICE"
    printf 'slot=%s\n' "$(getprop ro.boot.slot_suffix)"
    printf 'kernel=%s\n' "$(uname -r)"
    printf 'captured_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$META_TMP"

mv "$TMP" "$OUT"
mv "$LOW_POWER_TMP" "$LOW_POWER_OUT"
mv "$META_TMP" "$META_OUT"
chmod 600 "$OUT" "$LOW_POWER_OUT" "$META_OUT" 2>/dev/null || true
trap - EXIT HUP INT TERM

echo "PASS: captured $(wc -l < "$OUT") baseline nodes"
echo "Baseline: $OUT"
echo "Review it before applying any profile."
