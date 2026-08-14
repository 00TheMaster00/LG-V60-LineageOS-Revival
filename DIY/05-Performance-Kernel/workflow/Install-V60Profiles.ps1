[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [ValidatePattern('^[A-Za-z0-9._:-]+$')]
    [string]$Serial
)

$ErrorActionPreference = 'Stop'
$Adb = (Get-Command adb -ErrorAction Stop).Source
$Profiles = Join-Path $PSScriptRoot 'profiles'
$Stage = '/data/local/tmp/v60profiles-stage-' + [Guid]::NewGuid().ToString('N')

if ($Stage -notmatch '^/data/local/tmp/v60profiles-stage-[0-9a-f]{32}$') {
    throw "Refusing unexpected staging path: $Stage"
}

function Invoke-Adb {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $output = & $Adb -s $Serial @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "adb failed: $($Arguments -join ' ')`n$output"
    }
    return $output
}

$listed = & $Adb devices -l
$matches = @($listed | Where-Object { $_ -match ('^' + [regex]::Escape($Serial) + '\s+device\b') })
if ($matches.Count -ne 1) {
    throw "Serial '$Serial' is not exactly one authorized ADB device. Run 'adb devices -l' and select the LG V60 explicitly."
}

$device = (Invoke-Adb shell getprop ro.product.device | Out-String).Trim()
$vendorDevice = (Invoke-Adb shell getprop ro.product.vendor.device | Out-String).Trim()
if ("$device $vendorDevice" -notmatch 'timelm') {
    throw "Refusing non-timelm target: device='$device', vendor_device='$vendorDevice'."
}

$rootId = (Invoke-Adb shell su -c id | Out-String).Trim()
if ($rootId -notmatch 'uid=0') {
    throw "Root was not granted through ADB for serial '$Serial'."
}

try {
    Invoke-Adb shell mkdir -p $Stage | Out-Null
    Invoke-Adb push "$Profiles\." "$Stage/" | Out-Host
    Invoke-Adb shell su -c "sh '$Stage/install.sh' '$Stage'" | Out-Host
    Invoke-Adb shell su -c /data/adb/v60profiles/wrapper.sh status | Out-Host
}
finally {
    if ($Stage -match '^/data/local/tmp/v60profiles-stage-[0-9a-f]{32}$') {
        & $Adb -s $Serial shell rm -r $Stage 2>$null | Out-Null
    }
}

Write-Host 'PASS: Installed profiles and verified the captured baseline on the selected LG V60.'
