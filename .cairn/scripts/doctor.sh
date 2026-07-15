#!/usr/bin/env bash
# Cairn 漂移自检：检查陈旧或悬空的在途任务标记。

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base_dir="$(dirname "$script_dir")"
index="$base_dir/tasks/INDEX.md"
tasks_dir="$base_dir/tasks"

STALE_DAYS="${STALE_DAYS:-14}"
SHOW_ORPHANS="${SHOW_ORPHANS:-0}"
for a in "$@"; do
  case "$a" in
    --orphans|-v) SHOW_ORPHANS=1 ;;
    *[!0-9]*|'') : ;;
    *) STALE_DAYS="$a" ;;
  esac
done
now="$(date +%s)"

if [[ ! -f "$index" ]]; then
  echo "cairn doctor: 找不到 $index" >&2
  exit 2
fi

last_activity() {
  local slug="$1" p
  if [[ -d "$tasks_dir/$slug" ]]; then
    p="$tasks_dir/$slug"
    find "$p" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -1 | cut -d. -f1
  elif [[ -f "$tasks_dir/$slug.md" ]]; then
    stat -c %Y "$tasks_dir/$slug.md" 2>/dev/null
  else
    echo "MISSING"
  fi
}

inflight="$(grep -nE '^- [^[:alnum:] ]' "$index" 2>/dev/null || true)"
echo "cairn doctor — .cairn/（陈旧阈值 ${STALE_DAYS} 天）"

if [[ -z "$inflight" ]]; then
  echo "在途标记：无"
else
  echo "在途标记：$(printf '%s\n' "$inflight" | grep -c .) 个"
fi

stale=()
dangling=()
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  slug="$(printf '%s' "$line" | grep -oE '([0-9]{4}-)?[0-9]{2}-[0-9]{2}-[A-Za-z0-9][A-Za-z0-9-]*' | head -1)"
  [[ -z "$slug" ]] && continue
  marker="$(printf '%s' "$line" | awk '{print $2}')"
  act="$(last_activity "$slug")"
  if [[ "$act" == "MISSING" ]]; then
    dangling+=("$marker $slug")
  else
    age=$(( (now - act) / 86400 ))
    if (( age > STALE_DAYS )); then
      stale+=("$marker $slug（最后活动 ${age} 天前）")
    fi
  fi
done <<< "$inflight"

rc=0
if (( ${#stale[@]} > 0 )); then
  printf '陈旧：%s\n' "${stale[@]}"
  rc=1
fi
if (( ${#dangling[@]} > 0 )); then
  printf '悬空：%s\n' "${dangling[@]}"
  rc=1
fi

if [[ "$SHOW_ORPHANS" == "1" ]] && [[ -d "$tasks_dir" ]]; then
  orphan=0
  while IFS= read -r d; do
    [[ -z "$d" ]] && continue
    name="$(basename "$d")"
    grep -qF "$name" "$index" 2>/dev/null || orphan=$((orphan+1))
  done < <(find "$tasks_dir" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/([0-9]{4}-)?[0-9]{2}-[0-9]{2}-.*' 2>/dev/null)
  echo "游离任务目录：${orphan} 个"
fi

if (( rc == 0 )); then
  echo "检查通过：INDEX 与磁盘一致。"
fi
exit "$rc"
