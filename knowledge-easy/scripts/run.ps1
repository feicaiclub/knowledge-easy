$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$entry = Join-Path $PSScriptRoot 'vibe.py'
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python -c 'import sys;sys.exit(sys.version_info < (3,9))' 2>$null
    if ($LASTEXITCODE -eq 0) { & python $entry @args; exit $LASTEXITCODE }
}
if (Get-Command uv -ErrorAction SilentlyContinue) { & uv run --no-project --python 3.12 python $entry @args; exit $LASTEXITCODE }
$boot = Join-Path $env:LOCALAPPDATA 'FEICAI\bootstrap'
New-Item -ItemType Directory -Force $boot | Out-Null
$installer = Join-Path $boot 'install-uv.ps1'
Invoke-WebRequest 'https://astral.sh/uv/0.11.3/install.ps1' -OutFile $installer
$env:UV_UNMANAGED_INSTALL = Join-Path $boot 'bin'
$env:UV_NO_MODIFY_PATH = '1'
& powershell -NoProfile -ExecutionPolicy Bypass -File $installer
if ($LASTEXITCODE -ne 0) { throw 'uv installation failed' }
Remove-Item $installer
& (Join-Path $boot 'bin\uv.exe') run --no-project --python 3.12 python $entry @args
exit $LASTEXITCODE
