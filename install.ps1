# Nowledge installer for Windows PowerShell.
# Usage: irm https://raw.githubusercontent.com/hjxccc/nowledge/main/install.ps1 | iex
$ErrorActionPreference = "Stop"

$Repo = "https://github.com/hjxccc/nowledge.git"
$Target = if ($env:NOWLEDGE_TARGET) { $env:NOWLEDGE_TARGET.ToLowerInvariant() } else { "claude" }
$Dest = if ($env:NOWLEDGE_DIR) {
  $env:NOWLEDGE_DIR
} else {
  switch ($Target) {
    "claude" { "$HOME\.claude\skills\nowledge" }
    "codex"  { "$HOME\.codex\skills\nowledge" }
    "agents" { "$HOME\.agents\skills\nowledge" }
    default { throw "Unknown NOWLEDGE_TARGET '$Target'. Use claude, codex, agents, or set NOWLEDGE_DIR." }
  }
}

Write-Host "Installing Nowledge to $Dest"
if (Test-Path "$Dest\.git") {
  Write-Host "  Existing checkout found; pulling updates..."
  git -C $Dest pull --ff-only
} else {
  New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null
  git clone --depth 1 $Repo $Dest
}

# Check Python.
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
  $ver = (& python -V) 2>&1
  Write-Host "  $ver (3.8+ required)"
} else {
  Write-Host "  WARNING: Python was not found; script features require Python 3.8+."
}

Write-Host ""
Write-Host "Installation complete. Restart your agent, then try:"
Write-Host '    "Use Nowledge to explain the latest changes in XX"'
Write-Host '    "Use Nowledge to help me learn XX"'
Write-Host ""
Write-Host "Documentation: $Dest\README.md"
