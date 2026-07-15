#!/usr/bin/env bash
# 快速创建 MM-DD-<topic> 任务目录及 scratch/ 子目录。

set -e

topic="${1:-}"
if [[ -z "$topic" ]]; then
  echo "用法：$0 <topic>" >&2
  echo "示例：$0 source-grounding" >&2
  exit 1
fi

if [[ ! "$topic" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "错误：topic 必须是 kebab-case（小写字母、数字、横杠）" >&2
  echo "  你输入：$topic" >&2
  exit 1
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
today=$(date +%m-%d)
task_dir="$project_root/.cairn/tasks/${today}-${topic}"
scratch_dir="$task_dir/scratch"

if [[ -d "$task_dir" ]]; then
  mkdir -p "$scratch_dir"
  echo "[mktmp] 任务目录已存在，复用：$task_dir" >&2
else
  mkdir -p "$scratch_dir"
  echo "[mktmp] 已创建：$task_dir/" >&2
  echo "[mktmp]   - scratch/（本地临时产物）" >&2
  echo "[mktmp]   收尾时在 .cairn/tasks/INDEX.md 顶部垒一行" >&2
fi

echo "$scratch_dir"
