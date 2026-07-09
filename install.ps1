# Nowledge 一键安装（Windows PowerShell）
# 用法：irm https://raw.githubusercontent.com/hjxccc/nowledge/main/install.ps1 | iex
$ErrorActionPreference = "Stop"

$Repo = "https://github.com/hjxccc/nowledge.git"
$Dest = if ($env:NOWLEDGE_DIR) { $env:NOWLEDGE_DIR } else { "$HOME\.claude\skills\nowledge" }

Write-Host "→ 安装 Nowledge 到 $Dest"
if (Test-Path "$Dest\.git") {
  Write-Host "  已存在，拉取更新…"
  git -C $Dest pull --ff-only
} else {
  New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null
  git clone --depth 1 $Repo $Dest
}

# 自检 Python
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
  $ver = (& python -V) 2>&1
  Write-Host "  ✓ $ver（需 3.8+）"
} else {
  Write-Host "  ⚠ 未检测到 Python，脚本类功能需 Python 3.8+"
}

Write-Host ""
Write-Host "✓ 安装完成。重启你的 agent，然后直接说人话："
Write-Host '    "介绍下最近火的 XX"      → 快答现查现纠'
Write-Host '    "用 Nowledge 带我学 XX"  → 深学学习包'
Write-Host ""
Write-Host "文档：$Dest\README.md"
