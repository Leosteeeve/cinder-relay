param(
    [Parameter(Mandatory)][string]$PackageRoot,
    [Parameter(Mandatory)][string]$EvidenceRoot,
    [Parameter(Mandatory)][ValidateSet('Opening','Select','Handoff','Write','Read')][string]$Check,
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9_]{1,30}$')][string]$TestPrefix,
    [switch]$CaptureFilm
)
$ErrorActionPreference = 'Stop'
$crPackage = (Resolve-Path -LiteralPath $PackageRoot).Path
$crBin = Join-Path $crPackage 'CinderRelay/Binaries/Win64/CinderRelay.exe'
$crSaved = Join-Path $crPackage 'CinderRelay/Saved'
$crEvidence = [IO.Path]::GetFullPath($EvidenceRoot)
$crLog = Join-Path $crEvidence "$Check.log"
if (!(Test-Path -LiteralPath $crBin) -or (Test-Path -LiteralPath $crLog)) { throw 'Choose a packaged game and a new log path.' }
[void](New-Item -ItemType Directory -Force -Path $crEvidence)
$crArgs = "-CRCheckpointTest=$TestPrefix -CR055AudioTest=Phase055Campaign -windowed -ResX=1280 -ResY=720 -ForceRes -NoVSync -unattended -ExecCmds=`"au.DisableAppVolume 1`" -abslog=`"$crLog`""
if ($Check -in @('Write','Read')) {
    $crArgs = if ($Check -eq 'Write') { "/Game/Generated/Chapter02/Maps/L_CH02_EchoCrossing -CREchoCheck=Write " + $crArgs }
              else { "-CRCampaignCheck=Resume -CREchoCheck=Read " + $crArgs }
    $crReceipt = Join-Path $crSaved "EchoCheck/$Check/acceptance.json"
} else {
    $crArgs += " -CRCampaignCheck=$Check"
    if ($Check -eq 'Handoff') { $crArgs += ' -CRCheckpointRoute=3' }
    if ($CaptureFilm) { $crArgs += ' -CRFilmCapture' }
    $crReceipt = Join-Path $crSaved "Campaign/$Check/result.txt"
}
if (Test-Path -LiteralPath $crReceipt) { throw 'A receipt from this scenario already exists. Archive its evidence before repeating.' }
$crProc = Start-Process -FilePath $crBin -ArgumentList $crArgs -WorkingDirectory (Split-Path $crBin) -WindowStyle Hidden -PassThru
if (!$crProc.WaitForExit(360000)) {
    if (!$crProc.HasExited) { $crProc.Kill() }
    throw "$Check exceeded the six-minute deadline. See $crLog."
}
$crProc.Refresh()
if ($crProc.ExitCode -ne 0 -or !(Test-Path -LiteralPath $crReceipt)) { throw "$Check exited $($crProc.ExitCode) with no successful process result. See $crLog." }
$crResult = Get-Content -Raw -LiteralPath $crReceipt
if ($Check -in @('Write','Read')) { $crPass = ($crResult | ConvertFrom-Json).passed -eq $true }
else { $crPass = $crResult -match '(?m)^pass=1\s*$' }
if (!$crPass) { throw "$Check failed: $crResult" }
[pscustomobject]@{check=$Check;native_exit=$crProc.ExitCode;receipt=$crReceipt;result=$crResult} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $crEvidence "$Check-result.json")
"$Check passed with native exit $($crProc.ExitCode)."
