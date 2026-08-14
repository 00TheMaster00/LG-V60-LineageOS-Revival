#!/system/bin/sh
set -u

MODE="${1:-status}"
ROOT="/data/adb/v60profiles"
MODE_FILE="$ROOT/active-profile"
BASELINE="$ROOT/baseline.nodes"
BASELINE_LOW_POWER="$ROOT/baseline.low_power"
KGSL="/sys/class/kgsl/kgsl-3d0"
GPU="$KGSL/devfreq"
WRITE_FAILURES=0

write_node() {
    NODE="$1"
    VALUE="$2"
    [ -e "$NODE" ] || return 0
    [ -w "$NODE" ] || {
        echo "READ-ONLY: $NODE"
        WRITE_FAILURES=$((WRITE_FAILURES + 1))
        return 1
    }
    if printf '%s\n' "$VALUE" > "$NODE" 2>/dev/null; then
        echo "SET: $NODE=$VALUE"
    else
        echo "REJECTED: $NODE=$VALUE"
        WRITE_FAILURES=$((WRITE_FAILURES + 1))
        return 1
    fi
}

validate_baseline() {
    [ -s "$BASELINE" ] || {
        echo "ERROR: Missing or empty baseline: $BASELINE"
        echo "Run $ROOT/capture-baseline.sh before applying any profile."
        return 1
    }

    COUNT=0
    while IFS='|' read -r NODE VALUE EXTRA; do
        COUNT=$((COUNT + 1))
        case "$NODE" in
            /sys/*|/proc/*|/dev/*) ;;
            *) echo "ERROR: Unsafe baseline path on line $COUNT: $NODE"; return 1 ;;
        esac
        [ -n "$VALUE" ] || {
            echo "ERROR: Empty baseline value on line $COUNT: $NODE"
            return 1
        }
        [ -z "$EXTRA" ] || {
            echo "ERROR: Invalid baseline record on line $COUNT: $NODE"
            return 1
        }
        [ -e "$NODE" ] || {
            echo "ERROR: Baseline node no longer exists: $NODE"
            return 1
        }
        [ -w "$NODE" ] || {
            echo "ERROR: Baseline node is no longer writable: $NODE"
            return 1
        }
    done < "$BASELINE"

    [ "$COUNT" -gt 0 ] || { echo "ERROR: Baseline contains no nodes."; return 1; }
}

restore_baseline() {
    validate_baseline || return 1
    WRITE_FAILURES=0
    while IFS='|' read -r NODE VALUE; do
        [ -n "$NODE" ] || continue
        write_node "$NODE" "$VALUE" || true
    done < "$BASELINE"
    [ "$WRITE_FAILURES" -eq 0 ] || {
        echo "ERROR: Baseline restoration had $WRITE_FAILURES failed write(s)."
        return 1
    }

    LOW_POWER="$(cat "$BASELINE_LOW_POWER" 2>/dev/null || echo 0)"
    case "$LOW_POWER" in 0|1) ;; *) LOW_POWER=0 ;; esac
    settings put global low_power "$LOW_POWER" 2>/dev/null || true
    if [ "$LOW_POWER" = "1" ]; then
        cmd power set-adaptive-power-saver-enabled true 2>/dev/null || true
    else
        cmd power set-adaptive-power-saver-enabled false 2>/dev/null || true
    fi
}

commit_mode() {
    NAME="$1"
    if [ "$WRITE_FAILURES" -ne 0 ]; then
        echo "ERROR: Profile had $WRITE_FAILURES failed write(s); active state was not promoted."
        return 1
    fi
    printf '%s\n' "$NAME" > "$MODE_FILE"
}

freqs_desc() {
    tr ' ' '\n' < "$GPU/available_frequencies" 2>/dev/null |
        grep -E '^[0-9]+$' | sort -nr
}

highest_gpu_frequency() { freqs_desc | head -n 1; }
lowest_gpu_frequency() { freqs_desc | tail -n 1; }
second_gpu_frequency() { freqs_desc | awk 'NR == 2 {print; exit}'; }

gpu_level_for_frequency() {
    TARGET="$1"
    INDEX=0
    for FREQ in $(freqs_desc); do
        if [ "$FREQ" = "$TARGET" ]; then
            echo "$INDEX"
            return 0
        fi
        INDEX=$((INDEX + 1))
    done
    return 1
}

select_gpu_at_or_below() {
    TARGET="$1"
    for FREQ in $(freqs_desc); do
        [ "$FREQ" -le "$TARGET" ] && { echo "$FREQ"; return 0; }
    done
    lowest_gpu_frequency
}

select_cpu_at_or_below() {
    POLICY="$1"
    TARGET="$2"
    tr ' ' '\n' < "$POLICY/scaling_available_frequencies" 2>/dev/null |
        grep -E '^[0-9]+$' | sort -nr |
        awk -v target="$TARGET" '$1 <= target {print; exit}'
}

set_all_cores_maximum() {
    for CPU in /sys/devices/system/cpu/cpu[1-7]; do
        [ -d "$CPU" ] || continue
        write_node "$CPU/online" 1
    done
    for CORE_CTL in /sys/devices/system/cpu/cpu*/core_ctl; do
        [ -d "$CORE_CTL" ] || continue
        MAX_CPUS="$(cat "$CORE_CTL/max_cpus" 2>/dev/null || true)"
        case "$MAX_CPUS" in
            ''|*[!0-9]*) ;;
            *)
                write_node "$CORE_CTL/enable" 1
                write_node "$CORE_CTL/min_cpus" "$MAX_CPUS"
                write_node "$CORE_CTL/offline_delay_ms" 10000
                ;;
        esac
    done
}

set_cpu_maximum() {
    set_all_cores_maximum
    for POLICY in /sys/devices/system/cpu/cpufreq/policy*; do
        [ -d "$POLICY" ] || continue
        MAXIMUM="$(cat "$POLICY/cpuinfo_max_freq" 2>/dev/null || true)"
        case "$MAXIMUM" in ''|*[!0-9]*) continue ;; esac
        write_node "$POLICY/scaling_max_freq" "$MAXIMUM"
        write_node "$POLICY/scaling_min_freq" "$MAXIMUM"
        if grep -qw performance "$POLICY/scaling_available_governors" 2>/dev/null; then
            write_node "$POLICY/scaling_governor" performance
        else
            write_node "$POLICY/scaling_governor" schedutil
            write_node "$POLICY/schedutil/up_rate_limit_us" 0
            write_node "$POLICY/schedutil/down_rate_limit_us" 100000
        fi
    done
}

set_cpu_power_save() {
    for POLICY in /sys/devices/system/cpu/cpufreq/policy*; do
        [ -d "$POLICY" ] || continue
        NAME="$(basename "$POLICY")"
        case "$NAME" in
            policy0) TARGET=1248000 ;;
            policy4) TARGET=1670400 ;;
            policy7) TARGET=1977600 ;;
            *) TARGET="$(cat "$POLICY/cpuinfo_max_freq" 2>/dev/null || true)" ;;
        esac
        CAP="$(select_cpu_at_or_below "$POLICY" "$TARGET")"
        MINIMUM="$(cat "$POLICY/cpuinfo_min_freq" 2>/dev/null || true)"
        [ -n "$CAP" ] || continue
        [ -n "$MINIMUM" ] || continue
        write_node "$POLICY/scaling_min_freq" "$MINIMUM"
        write_node "$POLICY/scaling_max_freq" "$CAP"
        if grep -qw schedutil "$POLICY/scaling_available_governors" 2>/dev/null; then
            write_node "$POLICY/scaling_governor" schedutil
        fi
        write_node "$POLICY/schedutil/up_rate_limit_us" 5000
        write_node "$POLICY/schedutil/down_rate_limit_us" 40000
    done
}

set_gpu_maximum() {
    GPU_MAX="$(highest_gpu_frequency)"
    case "$GPU_MAX" in ''|*[!0-9]*) echo "ERROR: Cannot determine GPU maximum."; return 1 ;; esac
    echo "Highest exposed GPU frequency: $GPU_MAX Hz"
    write_node "$GPU/max_freq" "$GPU_MAX"
    write_node "$GPU/min_freq" "$GPU_MAX"
    if grep -qw performance "$GPU/available_governors" 2>/dev/null; then
        write_node "$GPU/governor" performance
    fi
    write_node "$KGSL/max_pwrlevel" 0
    write_node "$KGSL/min_pwrlevel" 0
    write_node "$KGSL/default_pwrlevel" 0
    write_node "$KGSL/idle_timer" 10000
    write_node "$KGSL/force_bus_on" 1
    write_node "$KGSL/force_clk_on" 1
    write_node "$KGSL/force_rail_on" 1
    write_node "$KGSL/force_no_nap" 1
}

set_gpu_power_save() {
    CAP="$(select_gpu_at_or_below 400000000)"
    LOW="$(lowest_gpu_frequency)"
    CAP_LEVEL="$(gpu_level_for_frequency "$CAP")"
    LOW_LEVEL="$(gpu_level_for_frequency "$LOW")"
    write_node "$GPU/min_freq" "$LOW"
    write_node "$GPU/max_freq" "$CAP"
    if grep -qw msm-adreno-tz "$GPU/available_governors" 2>/dev/null; then
        write_node "$GPU/governor" msm-adreno-tz
    fi
    write_node "$KGSL/min_pwrlevel" "$LOW_LEVEL"
    write_node "$KGSL/max_pwrlevel" "$CAP_LEVEL"
    write_node "$KGSL/default_pwrlevel" "$CAP_LEVEL"
}

set_benchmark_scheduler() {
    settings put global low_power 0 2>/dev/null || true
    cmd power set-adaptive-power-saver-enabled false 2>/dev/null || true
    write_node /proc/sys/kernel/sched_boost 1
    write_node /dev/stune/top-app/schedtune.boost 100
    write_node /dev/stune/top-app/schedtune.prefer_idle 1
    write_node /dev/stune/foreground/schedtune.boost 50
    write_node /dev/stune/foreground/schedtune.prefer_idle 1
    write_node /dev/cpuset/top-app/cpus 0-7
    write_node /dev/cpuset/foreground/cpus 0-7
}

show_status() {
    echo
    echo "============================================================"
    echo "V60 PERFORMANCE V2 PROFILE STATUS"
    echo "============================================================"
    echo "Active profile: $(cat "$MODE_FILE" 2>/dev/null || echo unknown)"
    echo "Slot: $(getprop ro.boot.slot_suffix)"
    echo "Kernel: $(uname -r)"
    echo
    echo "=== CPU ==="
    for POLICY in /sys/devices/system/cpu/cpufreq/policy*; do
        [ -d "$POLICY" ] || continue
        echo "$(basename "$POLICY")"
        echo "  governor=$(cat "$POLICY/scaling_governor" 2>/dev/null)"
        echo "  current=$(cat "$POLICY/scaling_cur_freq" 2>/dev/null)"
        echo "  minimum=$(cat "$POLICY/scaling_min_freq" 2>/dev/null)"
        echo "  maximum=$(cat "$POLICY/scaling_max_freq" 2>/dev/null)"
    done
    echo
    echo "=== GPU ==="
    for NODE in available_frequencies governor cur_freq min_freq max_freq; do
        echo "$NODE=$(cat "$GPU/$NODE" 2>/dev/null)"
    done
    for NODE in max_pwrlevel min_pwrlevel default_pwrlevel idle_timer force_bus_on force_clk_on force_rail_on force_no_nap; do
        echo "$NODE=$(cat "$KGSL/$NODE" 2>/dev/null)"
    done
    echo
    echo "=== SCHEDULER ==="
    echo "low_power=$(settings get global low_power 2>/dev/null)"
    echo "sched_boost=$(cat /proc/sys/kernel/sched_boost 2>/dev/null)"
    echo "battery_temp=$(cat /sys/class/power_supply/battery/temp 2>/dev/null)"
}

[ "$(id -u)" = "0" ] || { echo "ERROR: Root required."; exit 10; }

case "$MODE" in
    daily)
        echo "Applying V60 DAILY profile..."
        restore_baseline || exit 20
        commit_mode daily || exit 21
        ;;
    cpu)
        echo "Applying V60 CPU MAX profile..."
        restore_baseline || exit 20
        set_cpu_maximum
        set_benchmark_scheduler
        commit_mode cpu-max || exit 21
        ;;
    gpu)
        echo "Applying V60 GPU MAX 670 profile..."
        restore_baseline || exit 20
        set_gpu_maximum
        set_benchmark_scheduler
        commit_mode gpu-max-pending-bandwidth || exit 21
        ;;
    all)
        echo "Applying V60 ALL MAX 670 profile..."
        restore_baseline || exit 20
        set_cpu_maximum
        set_gpu_maximum
        set_benchmark_scheduler
        commit_mode all-max-pending-bandwidth || exit 21
        ;;
    power)
        echo "Applying V60 POWER SAVE profile..."
        restore_baseline || exit 20
        set_cpu_power_save
        set_gpu_power_save
        settings put global low_power 1 2>/dev/null || true
        cmd power set-adaptive-power-saver-enabled true 2>/dev/null || true
        write_node /proc/sys/kernel/sched_boost 0
        write_node /dev/stune/top-app/schedtune.boost 0
        write_node /dev/stune/top-app/schedtune.prefer_idle 0
        write_node /dev/stune/foreground/schedtune.boost 0
        write_node /dev/stune/foreground/schedtune.prefer_idle 0
        commit_mode power-save || exit 21
        ;;
    status) ;;
    *) echo "Usage: $0 daily|cpu|gpu|all|power|status"; exit 2 ;;
esac

show_status
