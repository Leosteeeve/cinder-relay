param(
    [Parameter(Mandatory=$true)][string]$PackageRoot,
    [Parameter(Mandatory=$true)][string]$EvidenceRoot,
    [Parameter(Mandatory=$true)][ValidatePattern('^Phase055[A-Za-z0-9_]{1,32}$')][string]$TestPrefix,
    [Parameter(Mandatory=$true)][string]$FFmpeg
)
$ErrorActionPreference='Stop'
$crPackage=(Resolve-Path -LiteralPath $PackageRoot).Path
$crEvidence=[IO.Path]::GetFullPath($EvidenceRoot)
$crNative=Join-Path $crPackage 'CinderRelay/Binaries/Win64/CinderRelay.exe'
$crSaved=Join-Path $crPackage 'CinderRelay/Saved'
$crArtifacts=Join-Path $crSaved "Phase055/$TestPrefix/Write"
if(!(Test-Path -LiteralPath $crNative)){throw 'Normal Windows Development executable is required.'}
if(Test-Path -LiteralPath $crEvidence){throw 'Use a fresh evidence directory.'}
foreach($crPath in @($crArtifacts,(Join-Path $crSaved "SaveGames/CR04_TEST_${TestPrefix}_A.sav"),(Join-Path $crSaved "SaveGames/CR04_TEST_${TestPrefix}_B.sav"),(Join-Path $crSaved "Config/CR04_TEST_Audio_$TestPrefix.ini"))){
    if(Test-Path -LiteralPath $crPath){throw 'Use a fresh test prefix; existing saves/evidence are never removed.'}
}
New-Item -ItemType Directory -Path $crEvidence | Out-Null
$crInfo=[Diagnostics.ProcessStartInfo]::new()
$crInfo.FileName=(Resolve-Path -LiteralPath $FFmpeg).Path
$crInfo.Arguments="-hide_banner -n -f gdigrab -framerate 30 -draw_mouse 0 -offset_x 0 -offset_y 0 -video_size 1920x1080 -i desktop -t 100 -c:v libx264 -threads 4 -preset veryfast -crf 19 -pix_fmt yuv420p `"$crEvidence/RawDesktop.mp4`""
$crInfo.UseShellExecute=$false
$crInfo.CreateNoWindow=$true
$crInfo.RedirectStandardInput=$true
$crInfo.RedirectStandardError=$true
$crCapture=[Diagnostics.Process]::new()
$crCapture.StartInfo=$crInfo
$crCaptureStart=[DateTime]::UtcNow
$null=$crCapture.Start()
$crCaptureErrors=$crCapture.StandardError.ReadToEndAsync()
$crQuality='au.DisableAppVolume 1,r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3'
# A bounded window avoids the observed native Slate screenshot failure during a
# fullscreen desktop-resolution transition. The final movie crops its client area.
# Full-resolution1080p/1600p validation remains in run_interface_acceptance.ps1.
$crArgs="-CR055InterfaceCheck=Write -CRCheckpointTest=$TestPrefix -CR055AudioTest=$TestPrefix -windowed -WinX=0 -WinY=0 -ResX=1280 -ResY=720 -ForceRes -NoVSync -ExecCmds=`"$crQuality`" -abslog=`"$crEvidence/recorded-game.log`""
$crGameStart=[DateTime]::UtcNow
$crGame=Start-Process -FilePath $crNative -ArgumentList $crArgs -WindowStyle Normal -PassThru
$null=$crGame.Handle
$crForced=$false
while(!$crGame.HasExited){
    if(([DateTime]::UtcNow-$crGameStart).TotalSeconds -gt 90){$crForced=$true;Stop-Process -Id $crGame.Id -Force;break}
    Start-Sleep -Milliseconds 100
}
$crGame.WaitForExit()
$crGameEnd=[DateTime]::UtcNow
if(!$crCapture.HasExited){$crCapture.StandardInput.WriteLine('q');$crCapture.StandardInput.Flush()}
if(!$crCapture.WaitForExit(10000)){Stop-Process -Id $crCapture.Id -Force;throw 'Recorder did not finalize within the bound.'}
$crCaptureErrors.GetAwaiter().GetResult() | Set-Content -LiteralPath (Join-Path $crEvidence 'ffmpeg.log')
$crReceipt=$null
$crMarker=$null
if(Test-Path -LiteralPath $crArtifacts){
    Copy-Item -LiteralPath $crArtifacts -Destination (Join-Path $crEvidence 'Write') -Recurse
    $crReceipt=Get-Content -LiteralPath (Join-Path $crArtifacts 'acceptance.json') -Raw | ConvertFrom-Json
    $crMarkerPath=Join-Path $crArtifacts 'Recording.ready'
    if(Test-Path -LiteralPath $crMarkerPath){$crMarker=(Get-Item -LiteralPath $crMarkerPath).LastWriteTimeUtc}
}
$crResult=[ordered]@{executable=$crNative;arguments=$crArgs;game_pid=$crGame.Id;game_exit=$crGame.ExitCode;capture_exit=$crCapture.ExitCode;forced_stop=$crForced;capture_start_utc=$crCaptureStart.ToString('o');game_start_utc=$crGameStart.ToString('o');game_end_utc=$crGameEnd.ToString('o');audio_marker_utc=if($crMarker){$crMarker.ToString('o')}else{$null};audio_offset_seconds=if($crMarker){($crMarker-$crCaptureStart).TotalSeconds}else{$null};acceptance=$crReceipt;capture='Actual 1920x1080 desktop capture, 30 fps; inspect and trim private/loading/exit frames before delivery. Native GameplayMix.wav is from this same process. Wall-clock audio alignment is approximate; no performance or human acceptance claim.'}
$crResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $crEvidence 'result.json') -Encoding utf8
$crResult | ConvertTo-Json -Depth 8
if($crForced -or $crGame.ExitCode -ne 0 -or $crCapture.ExitCode -ne 0 -or !$crReceipt.passed){throw 'Recording route failed; inspect evidence before any repair.'}
