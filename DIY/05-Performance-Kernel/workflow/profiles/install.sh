#!/system/bin/sh
set -u

SOURCE="${1:-}"
DEST="/data/adb/v60profiles"
FILES="profile.sh gpubw.sh wrapper.sh all-max.sh capture-baseline.sh install.sh"

[ "$(id -u)" = "0" ] || { echo "ERROR: Root required."; exit 10; }
[ -d "$SOURCE" ] || { echo "ERROR: Source directory missing: $SOURCE"; exit 11; }

DEVICE="$(getprop ro.product.device)"
VENDOR_DEVICE="$(getprop ro.product.vendor.device)"
case "$DEVICE $VENDOR_DEVICE" in
    *timelm*) ;;
    *) echo "ERROR: Refusing non-timelm target: '$DEVICE'/'$VENDOR_DEVICE'."; exit 12 ;;
esac

mkdir -p "$DEST" || exit 13
chmod 700 "$DEST" 2>/dev/null || true

for FILE in $FILES; do
    [ -f "$SOURCE/$FILE" ] || { echo "ERROR: Missing installer input: $FILE"; exit 14; }
    cp "$SOURCE/$FILE" "$DEST/$FILE.new" || exit 15
    chmod 700 "$DEST/$FILE.new" || exit 16
    SOURCE_HASH="$(sha256sum "$SOURCE/$FILE" | awk '{print $1}')"
    DEST_HASH="$(sha256sum "$DEST/$FILE.new" | awk '{print $1}')"
    [ "$SOURCE_HASH" = "$DEST_HASH" ] || { echo "ERROR: Copy hash mismatch: $FILE"; exit 17; }
    mv "$DEST/$FILE.new" "$DEST/$FILE" || exit 18
done

if [ ! -s "$DEST/baseline.nodes" ]; then
    "$DEST/capture-baseline.sh" || exit 19
else
    echo "Preserved existing baseline: $DEST/baseline.nodes"
fi

echo "PASS: V60 profiles installed at $DEST"
echo "Run: su -c '$DEST/wrapper.sh status'"
