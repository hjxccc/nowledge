#!/usr/bin/env bash
# Nowledge 一键安装（macOS / Linux / Git-Bash）
# 用法：curl -fsSL https://raw.githubusercontent.com/hjxccc/nowledge/main/install.sh | bash
set -e

REPO="https://github.com/hjxccc/nowledge.git"
TARGET="${NOWLEDGE_TARGET:-claude}"
if [ -n "${NOWLEDGE_DIR:-}" ]; then
  DEST="$NOWLEDGE_DIR"
else
  case "$TARGET" in
    claude) DEST="$HOME/.claude/skills/nowledge" ;;
    codex)  DEST="$HOME/.codex/skills/nowledge" ;;
    agents) DEST="$HOME/.agents/skills/nowledge" ;;
    *) echo "未知 NOWLEDGE_TARGET '$TARGET'；支持 claude、codex、agents，或设置 NOWLEDGE_DIR。" >&2; exit 2 ;;
  esac
fi

echo "→ 安装 Nowledge 到 $DEST"
if [ -d "$DEST/.git" ]; then
  echo "  已存在，拉取更新…"
  git -C "$DEST" pull --ff-only
else
  mkdir -p "$(dirname "$DEST")"
  git clone --depth 1 "$REPO" "$DEST"
fi

# 自检：Python 是否可用（脚本零 pip 依赖，纯标准库）
if command -v python3 >/dev/null 2>&1; then PY=python3; elif command -v python >/dev/null 2>&1; then PY=python; else PY=""; fi
if [ -n "$PY" ]; then
  "$PY" -c "import sys; assert sys.version_info>=(3,8)" 2>/dev/null \
    && echo "  ✓ Python $($PY -V 2>&1 | awk '{print $2}')（满足 3.8+）" \
    || echo "  ⚠ Python < 3.8，请升级"
else
  echo "  ⚠ 未检测到 Python，脚本类功能需 Python 3.8+"
fi

echo ""
echo "✓ 安装完成。重启你的 agent（Claude Code / Cursor / …），然后直接说人话："
echo '    "介绍下最近火的 XX"      → 快答现查现纠'
echo '    "用 Nowledge 带我学 XX"  → 深学学习包'
echo ""
echo "文档：$DEST/README.md"
