#!/system/bin/sh
set -eu
MODE="${1:-status}"
ROOT="/data/adb/v60profiles"
PROFILE="$ROOT/profile.sh"
BUS="$ROOT/gpubw.sh"
MODE_FILE="$ROOT/active-profile"

case "$MODE" in
    gpu) "$PROFILE" gpu; "$BUS" max; echo gpu-max-670 > "$MODE_FILE" ;;
    all) "$PROFILE" all; "$BUS" max; echo all-max-670 > "$MODE_FILE" ;;
    cpu) "$PROFILE" cpu; "$BUS" auto; echo cpu-max > "$MODE_FILE" ;;
    daily) "$PROFILE" daily; "$BUS" auto; echo daily > "$MODE_FILE" ;;
    power) "$PROFILE" power; "$BUS" auto; echo power-save > "$MODE_FILE" ;;
    status) "$PROFILE" status; "$BUS" status ;;
    *) echo "Usage: $0 gpu|all|cpu|daily|power|status"; exit 2 ;;
esac
