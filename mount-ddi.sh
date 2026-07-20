#!/usr/bin/env bash
# 一键挂载 DDI(macOS / Linux)。用法: ./mount-ddi.sh [--umount|--list]
# 需要 python3;首次会自动 pip 安装 pymobiledevice3。
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "[!] 没找到 python3。macOS: brew install python;Linux: apt install python3 python3-pip"
  exit 1
fi
exec "$PY" "$HERE/mount-ddi.py" "$@"
