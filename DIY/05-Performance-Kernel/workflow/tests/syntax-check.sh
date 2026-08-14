#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

while IFS= read -r file; do
    sh -n "$file"
done < <({ find "$ROOT/profiles" -type f -name '*.sh' -print; find "$ROOT/termux-shortcuts" -type f -print; } | sort)

while IFS= read -r file; do
    python3 - "$file" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done < <(find "$ROOT/tools" "$ROOT/tests" -type f -name '*.py' -print | sort)

PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/tests/test_tools.py"
printf 'Repository syntax and functional tests: PASS\n'
