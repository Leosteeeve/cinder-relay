param(
    [Parameter(Mandatory=$true)][string]$PackageRoot,
    [Parameter(Mandatory=$true)][string]$EvidenceRoot,
    [Parameter(Mandatory=$true)][ValidatePattern('^Phase055[A-Za-z0-9_]{1,32}$')][string]$TestPrefix,
    [switch]$Trace
)
$ErrorActionPreference='Stop'
$crPackage=(Resolve-Path -LiteralPath $PackageRoot).Path
$crEvidence=[IO.Path]::GetFullPath($EvidenceRoot)
$crNative=Join-Path $crPackage 'CinderRelay\Binaries\Win64\CinderRelay.exe'
$crSaved=Join-Path $crPackage 'CinderRelay\Saved'
if(!(Test-Path -LiteralPath $crNative)) { throw "Missing normal Windows Development executable: $crNative" }
if(Test-Path -LiteralPath $crEvidence) { throw 'Use a fresh evidence directory; existing evidence is never overwritten.' }
foreach($crSlot in @('A','B')) {
    if(Test-Path -LiteralPath (Join-Path $crSaved "SaveGames\CR04_TEST_${TestPrefix}_$crSlot.sav")) { throw 'Choose a fresh prefix; no test or player saves are deleted.' }
}
if(Test-Path -LiteralPath (Join-Path $crSaved "Config\CR04_TEST_Audio_$TestPrefix.ini")) { throw 'Choose a fresh prefix; audio preferences are never overwritten by preflight.' }
if(Test-Path -LiteralPath (Join-Path $crSaved "Phase055\$TestPrefix")) { throw 'Choose a fresh prefix; prior route evidence exists.' }
New-Item -ItemType Directory -Path $crEvidence | Out-Null
$crQuality='au.DisableAppVolume 1,r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3'
$crResults=@()
foreach($crMode in @('Write','Read')) {
    $crWidth=if($crMode -eq 'Write'){1920}else{2560}
    $crHeight=if($crMode -eq 'Write'){1080}else{1600}
    $crLog=Join-Path $crEvidence "$crMode.log"
    $crArtifacts=Join-Path $crSaved "Phase055\$TestPrefix\$crMode"
    $crReceiptPath=Join-Path $crArtifacts 'acceptance.json'
    $crArgs="-CR055InterfaceCheck=$crMode -CRCheckpointTest=$TestPrefix -CR055AudioTest=$TestPrefix -windowed -ResX=$crWidth -ResY=$crHeight -ForceRes -NoVSync -unattended -ExecCmds=`"$crQuality`" -abslog=`"$crLog`""
    if($Trace) { $crArgs+=" -trace=cpu,frame,bookmark -tracefile=`"$(Join-Path $crEvidence "$crMode.utrace")`"" }
    $crStart=[DateTime]::UtcNow
    $crProcess=Start-Process -FilePath $crNative -ArgumentList $crArgs -WindowStyle Hidden -PassThru
    $null=$crProcess.Handle
    $crForced=$false
    while(!$crProcess.HasExited) {
        if(([DateTime]::UtcNow-$crStart).TotalSeconds -gt 90) {
            $crForced=$true
            # This handle belongs only to the exact native process launched above.
            Stop-Process -Id $crProcess.Id -Force
            break
        }
        Start-Sleep -Milliseconds 500
    }
    $crProcess.WaitForExit()
    $crReceipt=$null
    if((Test-Path -LiteralPath $crReceiptPath) -and (Get-Item -LiteralPath $crReceiptPath).LastWriteTimeUtc -ge $crStart) {
        $crReceipt=Get-Content -LiteralPath $crReceiptPath -Raw | ConvertFrom-Json
    }
    $crFiles=@()
    if(Test-Path -LiteralPath $crArtifacts) {
        Copy-Item -LiteralPath $crArtifacts -Destination (Join-Path $crEvidence $crMode) -Recurse
        $crFiles=@(Get-ChildItem -LiteralPath $crArtifacts -File | ForEach-Object {
            [ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}
        })
    }
    $crResult=[ordered]@{mode=$crMode;resolution=@($crWidth,$crHeight);arguments=$crArgs;executable=$crNative;pid=$crProcess.Id;exit_code=$crProcess.ExitCode;forced_stop=$crForced;started_utc=$crStart.ToString('o');finished_utc=[DateTime]::UtcNow.ToString('o');acceptance=$crReceipt;artifacts=$crFiles;human_visual_acceptance=$false;human_auditory_acceptance=$false}
    $crResults+=$crResult
    $crResults | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $crEvidence 'process-results.json') -Encoding utf8
    $crResult | ConvertTo-Json -Depth 10
    if($crForced -or $crProcess.ExitCode -ne 0 -or !$crReceipt -or !$crReceipt.passed) { throw "Interface $crMode failed. Inspect fresh logs and receipt before a bounded repair." }
}
# Captures/WAV/traces remain local evidence, never assets to stage in public Git.
