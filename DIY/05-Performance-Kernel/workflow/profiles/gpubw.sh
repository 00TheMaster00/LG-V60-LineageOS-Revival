#!/system/bin/sh
set -u
MODE="${1:-status}"

find_gpubw() {
    for DIR in /sys/class/devfreq/*; do
        [ -d "$DIR" ] || continue
        NAME="$(cat "$DIR/name" 2>/dev/null || true)"
        BASE="$(basename "$DIR")"
        case "$NAME $BASE" in *gpubw*) printf '%s' "$DIR"; return 0 ;; esac
    done
    return 1
}

write_node() {
    NODE="$1"; VALUE="$2"
    [ -e "$NODE" ] || { echo "MISSING: $NODE"; return 0; }
    [ -w "$NODE" ] || { echo "READ-ONLY: $NODE"; return 0; }
    if printf '%s\n' "$VALUE" > "$NODE" 2>/dev/null; then
        echo "SET: $NODE=$VALUE"
    else
        echo "REJECTED: $NODE=$VALUE"
    fi
}

GPUBW="$(find_gpubw || true)"
[ -n "$GPUBW" ] || { echo "ERROR: Qualcomm gpubw device not found."; exit 10; }
TOP="$(tr ' ' '\n' < "$GPUBW/available_frequencies" 2>/dev/null | grep -E '^[0-9]+$' | sort -nr | head -n 1)"
LOW="$(tr ' ' '\n' < "$GPUBW/available_frequencies" 2>/dev/null | grep -E '^[0-9]+$' | sort -n | head -n 1)"
case "$TOP $LOW" in *[!0-9\ ]*) echo "ERROR: Invalid gpubw table."; exit 11 ;; esac

case "$MODE" in
    max)
        echo "Applying maximum GPU bandwidth vote..."
        write_node "$GPUBW/max_freq" "$TOP"
        write_node "$GPUBW/min_freq" "$TOP"
        ;;
    auto)
        echo "Restoring automatic GPU bandwidth scaling..."
        write_node "$GPUBW/min_freq" "$LOW"
        write_node "$GPUBW/max_freq" "$TOP"
        ;;
    status) ;;
    *) echo "Usage: $0 max|auto|status"; exit 2 ;;
esac

if grep -qw bw_vbif "$GPUBW/available_governors" 2>/dev/null; then
    write_node "$GPUBW/governor" bw_vbif
fi

echo
echo "=== GPU BANDWIDTH ==="
echo "device=$GPUBW"
echo "available=$(cat "$GPUBW/available_frequencies" 2>/dev/null)"
echo "governor=$(cat "$GPUBW/governor" 2>/dev/null)"
echo "current=$(cat "$GPUBW/cur_freq" 2>/dev/null)"
echo "minimum=$(cat "$GPUBW/min_freq" 2>/dev/null)"
echo "maximum=$(cat "$GPUBW/max_freq" 2>/dev/null)"
