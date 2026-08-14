#!/system/bin/sh
set -eu
MODE="${1:-status}"
ROOT="/data/adb/v60profiles"
PROFILE="$ROOT/profile.sh"
BUS="$ROOT/gpubw.sh"

case "$MODE" in
    gpu) "$PROFILE" gpu; "$BUS" max ;;
    all) "$PROFILE" all; "$BUS" max ;;
    cpu) "$PROFILE" cpu; "$BUS" auto ;;
    daily) "$PROFILE" daily; "$BUS" auto ;;
    power) "$PROFILE" power; "$BUS" auto ;;
    status) "$PROFILE" status; "$BUS" status ;;
    *) echo "Usage: $0 gpu|all|cpu|daily|power|status"; exit 2 ;;
esac
