param(
    [Parameter(Mandatory = $true)]
    [string]$StockApk,

    [string]$OutputApk = ".\output\LGCameraApp-Candidate24.apk",

    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Builder = Join-Path $Here "tools\build_candidate24.py"
$Patch = Join-Path $Here "patches\EA40g-to-Candidate24.bsdiff"
$Python = Get-Command python -ErrorAction SilentlyContinue

if (-not $Python) {
    throw "Python 3 was not found in PATH. Create the documented virtual environment first."
}

$Arguments = @(
    $Builder,
    "--stock", $StockApk,
    "--patch", $Patch,
    "--output", $OutputApk
)

if ($Force) {
    $Arguments += "--force"
}

& $Python.Source @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Candidate 24 reconstruction failed. Nothing was installed."
}

