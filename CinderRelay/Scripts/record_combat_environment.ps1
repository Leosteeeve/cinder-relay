param([string]$TestPrefix='Phase054Video')
$ErrorActionPreference='Stop'
if($TestPrefix -notmatch '^[A-Za-z0-9_]{1,40}$'){throw 'Invalid isolated test prefix'}
$crRoot=(Resolve-Path '.environment-local/phase-05-4').Path
$crSaved=Join-Path $crRoot 'package/Windows/CinderRelay/Saved'
$crReady=Join-Path $crSaved 'Phase054/Record.ready'
$crForeground=Join-Path $crRoot 'video/foreground.ready'
foreach($crPath in @($crReady,$crForeground,(Join-Path $crSaved "SaveGames/CR04_TEST_${TestPrefix}_A.sav"),(Join-Path $crSaved "SaveGames/CR04_TEST_${TestPrefix}_B.sav"))) {
    if(Test-Path -LiteralPath $crPath){throw "Fresh recording paths required: $crPath"}
}
New-Item -ItemType Directory -Path (Split-Path $crReady),(Join-Path $crRoot 'video') -Force | Out-Null
$crQuality='r.SetRes 1920x1080f,r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3'
$crArgs="-CRCheckpointTest=$TestPrefix -CRCheckpointRoute=1 -CRSlideCheck -CR054Video -fullscreen -ResX=1920 -ResY=1080 -ForceRes -NoVSync -ExecCmds=`"$crQuality`" -abslog=`"$crRoot/video/recorded-game.log`""
$crGame=Start-Process (Join-Path $crRoot 'package/Windows/CinderRelay/Binaries/Win64/CinderRelay.exe') -ArgumentList $crArgs -WindowStyle Normal -PassThru
$null=$crGame.Handle;$crLimit=[DateTime]::UtcNow.AddSeconds(60)
while(!(Test-Path $crForeground) -and !$crGame.HasExited -and [DateTime]::UtcNow -lt $crLimit){Start-Sleep -Milliseconds 100}
if(!(Test-Path $crForeground) -or $crGame.HasExited){if(!$crGame.HasExited){Stop-Process -Id $crGame.Id};throw 'Observed foreground handshake missing; capture not started'}
$crInfo=[Diagnostics.ProcessStartInfo]::new()
$crInfo.FileName=(Resolve-Path '.environment-local/phase-05-1/tools/imageio-ffmpeg/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe').Path
$crInfo.Arguments="-hide_banner -n -f gdigrab -framerate 30 -draw_mouse 0 -offset_x 0 -offset_y 0 -video_size 1920x1080 -i desktop -t 90 -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p `"$crRoot/video/CR054_Gameplay.mp4`""
$crInfo.UseShellExecute=$false;$crInfo.CreateNoWindow=$true;$crInfo.RedirectStandardInput=$true;$crInfo.RedirectStandardError=$true
$crCapture=[Diagnostics.Process]::new();$crCapture.StartInfo=$crInfo;$null=$crCapture.Start();$crErrorTask=$crCapture.StandardError.ReadToEndAsync()
$crStarted=[DateTime]::UtcNow
Start-Sleep -Milliseconds 500
if($crCapture.HasExited){throw 'Recorder failed before gameplay release'}
Set-Content -LiteralPath $crReady 'Observed foreground and recorder running; Development route only'
if(!$crGame.WaitForExit(90000)){Stop-Process -Id $crGame.Id;$crTimedOut=$true}else{$crTimedOut=$false}
$crEnded=[DateTime]::UtcNow
if(!$crCapture.HasExited){$crCapture.StandardInput.WriteLine('q');$crCapture.StandardInput.Flush()}
if(!$crCapture.WaitForExit(10000)){Stop-Process -Id $crCapture.Id;throw 'Recorder failed to finalize'}
$crErrorTask.GetAwaiter().GetResult() | Set-Content (Join-Path $crRoot 'video/ffmpeg.log')
@{game_pid=$crGame.Id;game_exit=$crGame.ExitCode;capture_exit=$crCapture.ExitCode;forced_stop=$crTimedOut;started_utc=$crStarted.ToString('o');seconds=($crEnded-$crStarted).TotalSeconds;capture='Actual foreground gameplay,1920x1080,30fps,silent,Enhanced Input; not a benchmark'} | ConvertTo-Json | Set-Content (Join-Path $crRoot 'video/result.json')
