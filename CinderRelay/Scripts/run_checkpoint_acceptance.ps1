param(
    [Parameter(Mandatory=$true)][string]$PackageRoot,
    [Parameter(Mandatory=$true)][string]$EvidenceRoot,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]{1,40}$')][string]$TestPrefix
)
$ErrorActionPreference = 'Stop'
$crPackage = (Resolve-Path -LiteralPath $PackageRoot).Path
$crEvidence = [IO.Path]::GetFullPath($EvidenceRoot)
New-Item -ItemType Directory -Path $crEvidence -Force | Out-Null
$crBootstrap = Join-Path $crPackage 'CinderRelay.exe'
$crNative = Join-Path $crPackage 'CinderRelay\Binaries\Win64\CinderRelay.exe'
$crSaved = Join-Path $crPackage 'CinderRelay\Saved'
foreach ($crPath in @($crBootstrap,$crNative)) { if (!(Test-Path -LiteralPath $crPath)) { throw "Missing executable: $crPath" } }
foreach ($crSlot in @('A','B')) {
    if (Test-Path -LiteralPath (Join-Path $crSaved "SaveGames\CR04_TEST_${TestPrefix}_$crSlot.sav")) { throw 'Choose a fresh test prefix; existing save files are never deleted.' }
}
$crQuality = 'r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3'
$crResults = @()
foreach ($crRoute in 1..3) {
    # One bounded bootstrap/native comparison, within the required three process launches.
    $crExecutable = if ($crRoute -eq 1) { $crBootstrap } else { $crNative }
    $crLog = Join-Path $crEvidence "packaged-route$crRoute.log"
    $crTrace = Join-Path $crEvidence "route$crRoute.utrace"
    $crReceiptPath = Join-Path $crSaved "Phase04\$crRoute\acceptance.json"
    $crArgs = "-CRCheckpointTest=$TestPrefix -CRCheckpointRoute=$crRoute -windowed -ResX=1920 -ResY=1080 -ForceRes -NoVSync -unattended -ExecCmds=`"$crQuality`" -trace=cpu,gpu,frame,bookmark,loadtime -tracefile=`"$crTrace`" -abslog=`"$crLog`""
    if ($crRoute -eq 2) { $crArgs += ' -CRCheckpointLifecycle' }
    $crStarted = [DateTime]::UtcNow
    $crRootProcess = Start-Process -FilePath $crExecutable -ArgumentList $crArgs -WindowStyle Hidden -PassThru
    $null = $crRootProcess.Handle # retain OS handle so exit code remains readable
    $crGameProcess = if ($crRoute -eq 1) { $null } else { $crRootProcess }
    $crReceipt = $null; $crReceiptAt = $null; $crForcedStop = $false
    while ($true) {
        if (!$crGameProcess -and !$crRootProcess.HasExited) {
            $crChild = Get-CimInstance Win32_Process -Filter "ParentProcessId=$($crRootProcess.Id)" | Where-Object { $_.ExecutablePath -eq $crNative } | Select-Object -First 1
            if ($crChild) { $crGameProcess = Get-Process -Id $crChild.ProcessId; $null = $crGameProcess.Handle }
        }
        if (!$crReceipt -and (Test-Path -LiteralPath $crReceiptPath) -and (Get-Item -LiteralPath $crReceiptPath).LastWriteTimeUtc -ge $crStarted) {
            try { $crReceipt = Get-Content -LiteralPath $crReceiptPath -Raw | ConvertFrom-Json; $crReceiptAt = [DateTime]::UtcNow } catch { }
        }
        if ($crRootProcess.HasExited -and (!$crGameProcess -or $crGameProcess.HasExited)) { break }
        if (([DateTime]::UtcNow-$crStarted).TotalSeconds -gt 540 -or ($crReceiptAt -and ([DateTime]::UtcNow-$crReceiptAt).TotalSeconds -gt 30)) {
            $crForcedStop = $true
            # Only process handles created/identified by this exact launch; never enumerate/kill user sessions.
            if ($crGameProcess -and !$crGameProcess.HasExited) { Stop-Process -Id $crGameProcess.Id -Force }
            if (!$crRootProcess.HasExited) { Stop-Process -Id $crRootProcess.Id -Force }
            break
        }
        Start-Sleep -Milliseconds 500
    }
    $crRootProcess.WaitForExit()
    if ($crGameProcess) { $crGameProcess.WaitForExit() }
    $crResult = [ordered]@{ route=$crRoute; executable=$crExecutable; arguments=$crArgs; started_utc=$crStarted.ToString('o'); ended_utc=[DateTime]::UtcNow.ToString('o'); launcher_pid=$crRootProcess.Id; launcher_exit=$crRootProcess.ExitCode; native_pid=if($crGameProcess){$crGameProcess.Id}else{$null}; native_exit=if($crGameProcess){$crGameProcess.ExitCode}else{$null}; forced_stop=$crForcedStop; acceptance=$crReceipt }
    $crResults += $crResult
    $crResults | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $crEvidence 'process-results.json') -Encoding utf8
    $crResult | ConvertTo-Json -Depth 8
    if (!$crReceipt -or !$crReceipt.passed) { throw "Route $crRoute acceptance failed; inspect recorded evidence before any repair." }
}
