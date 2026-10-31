# Windows Setup and Reproduction

## Phase 01A：打开与游玩

工程默认启动地图已设为 `/Game/Generated/Phase01A/Maps/L_CH01_Greybox`。打开 `CinderRelay.uproject` 后可在 Content Browser 找到 Generated → Phase01A → Maps。Play 下拉选择 **Standalone Game**，以便 Esc 交给游戏暂停菜单；普通 PIE 的 Esc 默认会被 Editor 的 StopPlaySession 快捷键截获。PIE 释放鼠标可用 Shift+F1。这是 Editor 快捷键边界，不修改用户的全局快捷键。

也可直接启动未打包的独立游戏窗口（需要本机已编译的 Editor target）：

```powershell
Set-Location -LiteralPath 'D:\Projects\FPS Game'
$ueEditor = 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$projectArg = '"D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject"'
Start-Process -FilePath $ueEditor -ArgumentList @($projectArg, '/Game/Generated/Phase01A/Maps/L_CH01_Greybox', '-game', '-windowed', '-ResX=1280', '-ResY=720')
```

WASD 移动、鼠标看、Shift 按住跑、Ctrl 按住蹲、Space 跳、E 交互、Esc 暂停／释放鼠标。进入蓝色标识工坊，查看左侧工作台拿模块；沿后门坡道下行，在橙色 Relay Nine 终端安装，再到青色信号台交互。结束菜单可以 Restart／Exit，无需控制台。

## Phase 01A：生成资产与有界 smoke

脚本仅支持原生 Editor Python，不能用普通 Python 运行 `import unreal`。启用的两个编辑插件只对 Editor target 生效。下面命令会打开／切换地图，所以先保存个人工作并关闭其他 CinderRelay Editor；不要在已有未保存关卡里直接运行生成器。

```powershell
Set-Location -LiteralPath 'D:\Projects\FPS Game'
$ueCmd = 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = 'D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject'
& $ueCmd $project -run=pythonscript '-script=D:/Projects/FPS Game/CinderRelay/Scripts/generate_greybox.py' -NullRHI -unattended -nosplash
if ($LASTEXITCODE -ne 0) { throw 'Greybox generation failed; inspect the exact Python error before retrying.' }
```

`-script` 值使用正斜杠，避免 UE quoted-string parser 将 `\r` 等解析为转义字符。脚本使用 LevelEditorSubsystem／EditorActorSubsystem／EditorAssetSubsystem，地图通过 `new_level(..., False)` 和 `save_current_level()` 保存。Rotator 必须用 `pitch=...`／`yaw=...`／`roll=...`，Python 位置参数顺序不同于 C++。只处理 `/Game/Generated/Phase01A` 与带 `CR_Phase01A_Generated` tag 的稳定命名 Actor；遇到未拥有资产或同名用户对象就报错，不删除用户内容。第一次保存立即写 ownership checkpoint。自定义资产应放在生成目录外；修改生成对象的脚本控制字段可能被下一次生成覆盖。可读 receipt：`CinderRelay/Saved/Phase01A/generation.json`。

只有里程碑或相关故障才执行一次 smoke：

```powershell
& $ueCmd $project '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/smoke_greybox.py' -nosplash -unattended -windowed -ResX=1280 -ResY=720
```

此命令启动有渲染的 Editor／PIE，以 Enhanced Input 注入驱动真实 CharacterMovement，程序化转向，不传送、不直接设置目标。240 秒有界，输出 `Saved/Phase01A/smoke.json` 与原生截图，完成／失败后注销回调并留下 Editor 供检查，需手动结束 PIE／关闭窗口。它不是人工手感验收，也不证明物理 Esc 键或 packaged cook；任何失败先读 stage／错误，只做针对性修正，不循环刷通过。

只验证鼠标方向时，在关闭本工程游戏／Editor 后使用以下定向命令，不需要走完整关卡：

```powershell
$checkStarted = Get-Date
& $ueCmd $project '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/smoke_greybox.py' -CRLookOnly -NullRHI -unattended -nosplash
if ($LASTEXITCODE -ne 0) { throw 'Editor input check process failed.' }
$receiptPath = 'D:\Projects\FPS Game\CinderRelay\Saved\Phase01A\look-smoke.json'
if ((Get-Item -LiteralPath $receiptPath).LastWriteTime -lt $checkStarted) { throw 'No fresh input check receipt.' }
$result = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json
if (-not $result.passed) { throw $result.error }
$result.checks | Format-Table
```

该模式在真实 PIE 中注入正／负 pitch action，检查 camera forward Z 的方向，并核验正 MouseX 右转；30 秒运行上限，自动关闭自己的测试 Editor。NullRHI 不验证画面／物理鼠标，完整流程仍用上面的有渲染模式。

官方依据：[Editor Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python?application_version=5.8)。实际 API 同时核对本机 5.8.4 headers／反射结果；未引入第三方 MCP 或资产包。

本机工作目录：`D:\Projects\FPS Game`。已安装引擎：`D:\Engines\Unreal\UE_5.8`，实际版本 5.8.4。VS 2026 Community 18.11.3，MSVC 产品版本 14.50.35739（目录 family 为 14.50.35717）。已安装 SDK 包含 10.0.26100.0；Phase 01A 两次 UBT 实际选择 **10.0.22621.0**，以当次日志为准。不要因 family 文件夹名而误判为旧的 banned compiler。

## 原生创建步骤（本轮已执行；不要重复创建）

初始仓库没有 `.uproject`、Source 或 Content。必须先由 Unreal Editor 创建真实工程，不能把模板二进制伪造为文本。

1. 启动已安装的 Unreal Editor，点击 **新建项目 / New Project**。
2. 选择 **游戏 / Games → 空白 / Blank**。
3. 选择 **C++**、**Desktop**；本轮保留模板 **Maximum** 默认预设。它不是性能验收结论。
4. 项目位置填写 `D:\Projects\FPS Game`；名称填写 `CinderRelay`。
5. 核对创建位置为 `D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject`，点击创建，等待原生 UBT 编译及 Editor 启动。
6. 不添加射击变体、不导入 Starter Content／Fab 包、不额外建立 Git。若 UI 或实际生成位置不同，先检查磁盘和项目浏览器，不能覆盖已有工程。

工程 descriptor 的 EngineAssociation 由 Editor 生成。本机生成的是 GUID；没有为规避它修改全局注册表。其他机器可通过 Editor 选择对应 5.8 安装，或对 `.uproject` 使用 Switch Unreal Engine version；不要将此误当作 C++ 模块改名。

## PowerShell：检查与打开

```powershell
Set-Location -LiteralPath 'D:\Projects\FPS Game'
$ueRoot = 'D:\Engines\Unreal\UE_5.8'
$project = Join-Path (Get-Location) 'CinderRelay\CinderRelay.uproject'
if (-not (Test-Path -LiteralPath $project)) { throw 'CinderRelay.uproject missing; use the Editor creation steps first.' }
Get-Content -LiteralPath "$ueRoot\Engine\Build\Build.version"
Get-Content -LiteralPath $project
& "$ueRoot\Engine\Binaries\Win64\UnrealEditor.exe" $project
```

调用可执行文件打开 Editor 是有意可见的交互操作。不要把引擎安装目录或其他用户工程当作当前项目。

## PowerShell：后续确需重新编译时

先关闭 CinderRelay Editor／Live Coding 会话，避免已载入 DLL 干扰。下面是复现命令，本轮 baseline 已由 Editor 创建流程执行；不因阅读本文重复构建。

```powershell
Set-Location -LiteralPath 'D:\Projects\FPS Game'
$ueRoot = 'D:\Engines\Unreal\UE_5.8'
$project = Join-Path (Get-Location) 'CinderRelay\CinderRelay.uproject'
if (-not (Test-Path -LiteralPath $project)) { throw 'Missing Unreal project.' }
$evidence = Join-Path (Get-Location) '.environment-local\build'
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
& "$ueRoot\Engine\Build\BatchFiles\Build.bat" CinderRelayEditor Win64 Development "-Project=$project" -WaitMutex -NoEngineChanges -NoHotReloadFromIDE 2>&1 |
    Tee-Object -FilePath "$evidence\CinderRelayEditor.log"
$buildExit = $LASTEXITCODE
"Exit code: $buildExit"
if ($buildExit -ne 0) { throw "CinderRelayEditor build failed: $buildExit" }
```

只有源码位置／Build.cs／Target.cs 变动需要更新 IDE 文件时再生成，不以反复生成解决不明编译错误：

```powershell
& "$ueRoot\Engine\Build\BatchFiles\Build.bat" -ProjectFiles "-Project=$project" -Game -Engine
if ($LASTEXITCODE -ne 0) { throw 'Project file generation failed.' }
```

## PowerShell：Git 与远端验证

已初始化仓库不要再 `git init`。已有 LFS 本地配置无需每次重装。以下全部为核验：

```powershell
Set-Location -LiteralPath 'D:\Projects\FPS Game'
git status --short --branch
git branch -vv
git remote -v
git log -1 --oneline
git lfs ls-files
gh auth status
gh repo view Leosteeeve/cinder-relay --json nameWithOwner,url,visibility,defaultBranchRef
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

登录凭据只使用现有 keyring／credential manager，不读取或导出 token、浏览器 cookies 或凭据文件。若 CLI 真正未登录，由 `gh auth login --web --hostname github.com` 发起用户授权；网络受限错误不能直接当作凭据失效。

尚未创建远端的其他环境才使用下面的等价 CLI 后备流程，**本轮通过浏览器创建，不再重复执行**：

```powershell
gh repo view Leosteeeve/cinder-relay --json nameWithOwner,url,visibility,isEmpty
# Only after confirming the intended owner's repository truly does not exist:
gh repo create Leosteeeve/cinder-relay --private --description 'CINDER RELAY - narrative-driven single-player post-apocalyptic FPS'
# Only when origin is absent, after verifying the URL and owner:
git remote add origin https://github.com/Leosteeeve/cinder-relay.git
# Review explicit staged paths and diff before a commit. Never force push.
git push -u origin main
```

有已存在 remote／远端提交时先 fetch 并检查历史，不覆盖、不自动换 origin、不强推。源码与文档分阶段提交，不执行无审计的 `git add .`。

## Phase 01B native streaming

以下是已存在工程的命令，不是新建或重命名工程。`$repo`、`$ueRoot`、`$project` 均为任务变量。退出现有同工程 Editor 后再编译/迁移，避免资产或 DLL 文件锁。

```powershell
$repo = 'D:\Projects\FPS Game'
$ueRoot = 'D:\Engines\Unreal\UE_5.8'
$project = Join-Path $repo 'CinderRelay\CinderRelay.uproject'
$evidence = Join-Path $repo '.environment-local\phase-01b'
Set-Location -LiteralPath $repo
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
& "$ueRoot\Engine\Build\BatchFiles\Build.bat" CinderRelayEditor Win64 Development "-Project=$project" -WaitMutex -NoEngineChanges -NoHotReloadFromIDE
if ($LASTEXITCODE -ne 0) { throw 'Editor target compilation failed; diagnose the reported error.' }
```

迁移脚本：已经生成完毕时只审计，不应重生成或替换地图。必须完整 Editor，不能改为 Python commandlet 执行 MoveActorsToLevel（commandlet 选择集不可用）。路径参数使用 `/`，避免 Unreal 对反斜杠转义。

```powershell
& "$ueRoot\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/migrate_streaming.py' -unattended -nosplash
```

Editor 功能检查（NullRHI，无视觉/性能结论）：

```powershell
& "$ueRoot\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/smoke_streaming.py' -CRStreamAcceptance -NullRHI -unattended -nosplash
Get-Content -LiteralPath "$repo\CinderRelay\Saved\Phase01B\acceptance.json"
```

只诊断已复现的退出路径时另加 `-CRStreamExitCheck`；它明确不是玩法验收。完整路线与此短检查的 receipt 必须分开归档。脚本只读取本次写出的 receipt，并先停止 PIE 再退出；不能只看 Editor exit 0 判定路线通过。

Windows Development 一次打包：

```powershell
& "$ueRoot\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun "-project=$project" -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive "-archivedirectory=$evidence\package" -nocompileeditor -installed -unattended -utf8output
if ($LASTEXITCODE -ne 0) { throw 'BuildCookRun failed; preserve package.log and diagnose.' }
$game = Join-Path $evidence 'package\Windows\CinderRelay.exe'
& $game -windowed -ResX=1920 -ResY=1080
```

有界 packaged 验收与 trace（不是日常试玩参数，不输入控制台、不传送）：

```powershell
& $game -CRStreamAcceptance -windowed -ResX=1920 -ResY=1080 -ForceRes -NoVSync '-ExecCmds=r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0' '-trace=cpu,gpu,frame,bookmark,loadtime,memory,metadata,assetmetadata' "-tracefile=$evidence\packaged.utrace" "-abslog=$evidence\packaged-game.log"
```

新进程不清 OS/DDC/驱动缓存。非 Shipping 记录保存到该包 `CinderRelay/Saved/Phase01B`（若平台重定向 Saved，以启动日志的实际目录为准）。`acceptance.json`、`route.txt`、`frames.csv`、`memory.csv`、`settings.txt` 和原生结束截图分别证明不同事项。运行 `Scripts/summarize_streaming.py <Saved/Phase01B> <game-log> <output.json>` 只汇总已有数据，不重复运行游戏。Memory trace 有额外开销，应单独标明，不能充当无追踪的最终美术性能基线。
## Phase02 First Contact

Use the existing checkout and Engine5.8.4. Never run the Phase01A generator or destructive migration against the accepted maps. Phase02 creation only updates its owned content, adds encounter actors and changes the persistent GameMode to a derived combat configuration.

```powershell
$repo = 'D:\Projects\FPS Game'
$ueRoot = 'D:\Engines\Unreal\UE_5.8'
$project = Join-Path $repo 'CinderRelay\CinderRelay.uproject'
$phase02 = Join-Path $repo '.environment-local\phase-02'
& "$ueRoot\Engine\Build\BatchFiles\Build.bat" CinderRelayEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReloadFromIDE
if ($LASTEXITCODE -ne 0) { throw 'Read the actual compile error before repair.' }
$editorArgs = '"{0}" "-ExecutePythonScript={1}\CinderRelay\Scripts\generate_combat.py" -CRCreateEncounter -unattended -nosplash' -f $project,$repo
Start-Process -FilePath "$ueRoot\Engine\Binaries\Win64\UnrealEditor.exe" -ArgumentList $editorArgs -WindowStyle Hidden -Wait
```

Inspect Output Log for `CR02_ENCOUNTER_ASSETS_PASS`, not just a launcher exit code. The Editor creates the real BT/Blackboard, audio, input/data/Blueprint assets and nav bounds. It waits for native navigation data to exist before saving; it does not fabricate brush data. Complete reruns reuse owned labels/assets. Refuse ownership conflicts instead of deleting content.

Focused weapon fixture uses `-CRWeaponCheck`; actual encounter route uses `-CRCombatCheck`. Run the appropriate checkpoint only, not both after every edit:

```powershell
$editorArgs = '"{0}" "-ExecutePythonScript={1}\CinderRelay\Scripts\smoke_combat.py" -CRCombatCheck -NullRHI -unattended -nosplash' -f $project,$repo
Start-Process -FilePath "$ueRoot\Engine\Binaries\Win64\UnrealEditor.exe" -ArgumentList $editorArgs -WindowStyle Hidden -Wait
Get-Content -LiteralPath "$repo\CinderRelay\Saved\Phase02\acceptance.json"
```

NullRHI validates logic/collision/navigation, not visuals or GPU performance. The focused weapon test uses controlled edge-case fixtures; the combat route drives Enhanced Input and actual enemy/player damage, never teleports or directly sets objective progress. The supervisor requires a new receipt, ends PIE and then closes Editor.

Once integrated Editor checks pass, one Windows Development package:

```powershell
& "$ueRoot\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun "-project=$project" -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive "-archivedirectory=$phase02\package" -nocompileeditor -installed -unattended -utf8output
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed; retain the log and diagnose.' }
$game = Join-Path $phase02 'package\Windows\CinderRelay.exe'
& $game -windowed -ResX=1920 -ResY=1080
```

The project enables `bAllowHighDPIInGameMode=True` so Windows desktop scaling does not enlarge the requested game window beyond the visible screen. The existing local Phase02 package also has that same override in `Windows/CinderRelay/Saved/Config/Windows/Engine.ini`; future packages inherit the project setting. Do not change Windows scaling or shrink HUD fonts to mask a desktop-window crop.

Ordinary play uses no automation flags. For the one authorized packaged acceptance/performance sample:

```powershell
$combatArgs = '-CRCombatCheck -windowed -ResX=1920 -ResY=1080 -ForceRes -NoVSync -ExecCmds="r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0" -trace=cpu,gpu,frame,bookmark,loadtime "-tracefile={0}\combat.utrace" "-abslog={0}\packaged-combat.log"' -f $phase02
$run = Start-Process -FilePath $game -ArgumentList $combatArgs -WindowStyle Hidden -Wait -PassThru
"Bootstrap exit code: $($run.ExitCode)"
Get-Content -LiteralPath "$phase02\package\Windows\CinderRelay\Saved\Phase02\acceptance.json"
```

No allocation/callstack memory tracing requested in this combat sample. Native counters still record GT/RT/GPU; process memory is sampled separately. Read the actual game log and a freshly modified `package/Windows/CinderRelay/Saved/Phase02/acceptance.json`; a bootstrap code alone does not prove gameplay success. This run produced a PASS receipt and normal game exit log but bootstrap code777003; see MILESTONES. `summarize_combat.py <Saved/Phase02> <output.json>` only analyzes existing CSVs. Screenshots prove discrete frames, not human gunfeel/audio acceptance. Do not run this command again solely because the documented run has already completed.
