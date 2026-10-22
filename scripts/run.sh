#!/bin/sh
set -eu
VIBE_SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys;sys.exit(sys.version_info < (3,9))'; then
    exec python3 "$VIBE_SCRIPT_DIR/vibe.py" "$@"
fi
if command -v uv >/dev/null 2>&1; then
    exec uv run --no-project --python 3.12 python "$VIBE_SCRIPT_DIR/vibe.py" "$@"
fi
# A machine without Python can bootstrap uv without writing into the Skill.
VIBE_BOOT_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/feicai-bootstrap"
mkdir -p "$VIBE_BOOT_DIR"
curl -fLsS --retry 2 https://astral.sh/uv/0.11.3/install.sh -o "$VIBE_BOOT_DIR/install-uv.sh"
UV_UNMANAGED_INSTALL="$VIBE_BOOT_DIR/bin" UV_NO_MODIFY_PATH=1 sh "$VIBE_BOOT_DIR/install-uv.sh"
rm -f "$VIBE_BOOT_DIR/install-uv.sh"
exec "$VIBE_BOOT_DIR/bin/uv" run --no-project --python 3.12 python "$VIBE_SCRIPT_DIR/vibe.py" "$@"
