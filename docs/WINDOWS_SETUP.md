# Windows Setup and Reproduction

## Phase05.5 interface, audio and Field Pack

Normal owner playtest (real player save namespace; no automation flags):

```powershell
Set-Location 'D:\Projects\FPS Game'
Start-Process -FilePath '.\.environment-local\phase-05-5\package\Windows\CinderRelay.exe' -WindowStyle Normal
```

I opens/closes Elias's Field Pack; Escape closes it before the regular pause menu. Opening clears held aim/sprint/crouch, cancels a slide and pauses a reload; closing resumes the existing reload. Pack is unavailable during assembly, ending, death, startup, ordinary pause or checkpoint travel. Tab still skips the existing presentation. Settings contains controls/help and five independent audio sliders. Music has a native category but no misleading slider because this chapter has no music asset.

Reproduce focused packaged integration with fresh test prefixes and fresh evidence folders:

```powershell
./CinderRelay/Scripts/run_interface_acceptance.ps1 -PackageRoot .environment-local/phase-05-5/package/Windows -EvidenceRoot .environment-local/phase-05-5/repro-interface -TestPrefix Phase055Repro01 -Trace
./CinderRelay/Scripts/run_checkpoint_acceptance.ps1 -PackageRoot .environment-local/phase-05-5/package/Windows -EvidenceRoot .environment-local/phase-05-5/repro-checkpoints -TestPrefix Phase055CPRepro01 -LowOverhead -Fullscreen -SlideCheck
```

The first command runs real Slate/input interactions in separate1080p Write and1600p Read processes, exports native ShowUI captures and mixed stereo WAV, and uses independent `CR04_TEST_Audio_*.ini` preferences. The second retains existing CP01/CP02/streaming/workbench/death/ending tests. Neither touches a player save. Process exit codes, fresh acceptance receipts and forced-stop fields must all be inspected. Traced or recorded runs are diagnostics, not the untraced paired frame-time benchmark.

Editable sources live in `CinderRelay/ArtSource/{Blender/Phase055,Interface/Phase055,Audio/Phase055}`. `import_interface.py` and `import_audio055.py` are intentionally bounded to Phase055-owned content and the three explicit streamed-map audio references. Do not rerun historical generators. `verify_interface055.py` reads native assets and checks Designer bindings, source hashes, classes/concurrency/attenuation, protected weapon values and unchanged sequence transform/animation tracks. [Validation ledger](INTERFACE_AUDIO_05_5.md) distinguishes authored assets, automated evidence and pending human acceptance.

## Phase05.4 combat / slide / environment

Normal owner playtest (no test flags; actual player saves remain separate from test slots):

```powershell
Set-Location 'D:\Projects\FPS Game'
Start-Process -FilePath '.\.environment-local\phase-05-4\package\Windows\CinderRelay.exe' -WindowStyle Normal
```

Shift+movement then Ctrl starts a grounded slide above430cm/s. Hold Ctrl to remain crouched; release requests standing with native ceiling clearance. Hip fire is allowed; ADS waits until slide ends. R can end a slide and start the unchanged reload. Esc clears held movement and pauses.

Native reproducible asset production, only for intentional edits to Phase054-owned content:

```powershell
$cr54Blender = 'D:\Dev\Toolchains\Blender\blender-4.5.11-windows-x64\blender.exe'
$cr54Editor = 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$cr54Project = 'D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject'
& $cr54Blender --background --factory-startup --python-exit-code 1 --python './CinderRelay/ArtSource/Blender/Phase054/author_utility_kit.py' -- --export-dir '.environment-local/phase-05-4/exports'
& $cr54Editor $cr54Project -run=pythonscript '-script=D:/Projects/FPS Game/CinderRelay/Scripts/polish_combat_environment.py' -unattended -nosplash -NoLiveCoding
```

The Blender author overwrites only its Phase054 source; preserve any manual edits before intentionally regenerating. The importer creates missing owned meshes, does not silently reimport existing ones, and refuses foreign name collisions. Use native Reimport for intentional mesh changes. Its338-actor baseline, post-save comparison and `CR054_ENVIRONMENT_PASS` receipt are required; exit0 alone is insufficient. Never invoke old greybox/streaming/arm generators.

Existing `run_checkpoint_acceptance.ps1` accepts optional `-SlideCheck` for the route1 native input extension. `-CRSlideEdges` adds six bounded native physics/input fixtures to route1 under dedicated `-CRCheckpointTest=<fresh prefix>` slots; fixture geometry is transient, never saved. NullRHI evidence does not establish visual quality. `record_combat_environment.ps1` waits for an observed foreground handshake before recording real game pixels; it is an operator-assisted capture, not an unattended benchmark. Do not enable any test/recording flags for ordinary play.

Before/after views use `capture_combat_environment.py` and `-cr054after`; the script does not save assets. Output is local `.environment-local/phase-05-4/{before,after}`. Original sources: `ArtSource/Blender/Phase054/CR054_IndustrialUtilities.blend`; imported meshes: `/Game/Generated/Phase054/Meshes`. Existing native persistent map remains the entry map.

## Phase053 anatomy review — no gameplay activation

Open `CinderRelay/ArtSource/Blender/Phase053/CR053_EliasArms.blend` for editable anatomy/garments, fingers and disabled IK edit controls. The source contains packed texture images. For native Unreal review, open `/Game/Generated/Phase053/Review/Maps/L_CR053_ArmsReview` and inspect `AN_CR053_AnatomyReview` in the Animation Editor. This separate3s articulation sample is not a new playable build or weapon animation. Default game remains the existing persistent chapter map.

```powershell
Set-Location 'D:\Projects\FPS Game'
$cr53Blender = 'D:\Dev\Toolchains\Blender\blender-4.5.11-windows-x64\blender.exe'
$cr53Editor = 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$cr53Project = 'D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject'
# Export the existing source, preserving centimeter FBX and meter GLB conventions.
& $cr53Blender --background --factory-startup --python-exit-code 1 --python './CinderRelay/ArtSource/Blender/Phase053/export_elias_review.py' -- --export-dir '.environment-local/phase-05-3/exports'
# First import or complete only this owned review map; existing imported mesh is preserved.
$cr53Args = '"{0}" -ExecutePythonScript="D:/Projects/FPS Game/CinderRelay/Scripts/import_arms_review.py" -CR053CaptureReview -unattended -nosplash -NoLiveCoding' -f $cr53Project
Start-Process -FilePath $cr53Editor -ArgumentList $cr53Args -WindowStyle Hidden -Wait
# Visible human inspection; no game-input automation.
Start-Process -FilePath $cr53Editor -ArgumentList ('"{0}" /Game/Generated/Phase053/Review/Maps/L_CR053_ArmsReview' -f $cr53Project)
```

The importer is idempotent and does not reimport existing geometry automatically. After an intentional saved Blender edit, export then use Unreal's **Reimport** on the owned review Skeletal Mesh/AnimSequence; inspect the actual Interchange result before acceptance. Do not expect exporting alone to update an existing `.uasset`. Do not invoke Phase01A/01B generators or overwrite previous hands. `create_elias_review.py` refuses existing source; `finish_elias_review.py` is one-time only.

For pinned authoring inputs, use the bundled engine Python with UTF-8:

```powershell
$cr53Python = 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
& $cr53Python -X utf8 './CinderRelay/ArtSource/Blender/Phase053/acquire_reference.py' --output-dir '.environment-local/phase-05-3/evaluation/makehuman'
```

Actual review captures/logs and baseline receipts live under `.environment-local/phase-05-3/`. Check `CR053_ARMS_IMPORT_PASS`, the import JSON, `CR053_ARMS_REVIEW PASS`, capture JSON and real files; Unreal can exit0 after Python errors. Initial import diagnostics and successful focused fixes are preserved. No new C++ build/package is necessary for this isolated art review. Final weapon/workbench integration and packaged performance remain pending.

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

## Phase03 restoration

Run commands from the repository root in PowerShell. Do not regenerate Phase01A or rerun Phase01B migration. Close Editor before a C++ build. The generation script preserves an existing ignored preflight inventory; on a fresh checkout it snapshots all non-Phase03 actors before any placement. Native transform changes call Modify before saving and saved rotations are checked after reload.

```powershell
Set-Location 'D:\Projects\FPS Game'
$project = 'D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject'
$engine = 'D:\Engines\Unreal\UE_5.8'
$blender = 'D:\Dev\Toolchains\Blender\blender-4.5.11-windows-x64\blender.exe'

# Optional deliberate re-authoring of the original source; not needed to play.
& $blender --background --factory-startup --python '.\CinderRelay\ArtSource\Blender\Phase03\create_restoration.py' -- --export-dir 'D:\Projects\FPS Game\.environment-local\phase-03\exports'
& $blender --background '.\CinderRelay\ArtSource\Blender\Phase03\CR03_RookRestoration.blend' --python '.\CinderRelay\ArtSource\Blender\Phase03\validate_source.py' -- --receipt 'D:\Projects\FPS Game\.environment-local\phase-03\source-validation.json'

& "$engine\Engine\Build\BatchFiles\Build.bat" CinderRelayEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReloadFromIDE
& "$engine\Engine\Binaries\Win64\UnrealEditor.exe" $project '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/generate_restoration.py' -unattended

# Focused deterministic state check.
& "$engine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project -unattended -nullrhi '-ExecCmds=Automation RunTests CinderRelay.Restoration.Session' '-TestExit=Automation Test Queue Empty'
# Bounded actual PIE acceptance; emits Saved/Phase03/acceptance.json and frame captures.
& "$engine\Engine\Binaries\Win64\UnrealEditor.exe" $project '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/smoke_restoration.py' -CRRestorationCheck -unattended

# One final Development package; inspect the exit code and receipts, not just file existence.
& "$engine\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun "-project=$project" -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive '-archivedirectory=D:\Projects\FPS Game\.environment-local\phase-03\package' -nocompileeditor -installed -unattended -utf8output
# Manual play (omit acceptance flags).
& '.\.environment-local\phase-03\package\Windows\CinderRelay.exe' -windowed -ResX=1920 -ResY=1080
```

Open LS_CR03_RookRestoration in Sequencer with L_CH01_Persistent/Workshop loaded to inspect the actual skeletal track. Open the .blend to edit bones/weights/action and timeline beat markers. Generated export intermediates are local, not third-party source packs. UE GUI executables may detach when invoked directly from PowerShell; automation uses Start-Process -WindowStyle Hidden -Wait -PassThru and a fresh receipt/log to establish completion. Human review remains necessary for glove anatomy, contact quality and pacing.

### Updating an existing Phase03 import

`generate_restoration.py` intentionally reuses existing owned imported assets. It does **not** reimport changed FBX files. For a procedural animation-curve edit in `animate_restoration.py`, use the already verified targeted path below. `export_animation.py` re-authors the procedural action on the existing rig; it does not regenerate geometry. Do not use it to preserve hand-edited keyframes.

```powershell
Set-Location 'D:\Projects\FPS Game'
$blender = 'D:\Dev\Toolchains\Blender\blender-4.5.11-windows-x64\blender.exe'
& $blender --background 'D:/Projects/FPS Game/CinderRelay/ArtSource/Blender/Phase03/CR03_RookRestoration.blend' --python 'D:/Projects/FPS Game/CinderRelay/ArtSource/Blender/Phase03/export_animation.py' -- --export-dir 'D:/Projects/FPS Game/.environment-local/phase-03/exports'
& 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' 'D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject' '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/reimport_restoration.py' -CR03AnimationOnly -unattended
```

For hand-edited animation, save the .blend, select only CR03_RestorationRig and SK_CR03_Restoration, and use Blender File > Export > FBX to the same ignored SK_CR03_Restoration.fbx. Enable Selected Objects, Mesh/Armature and Bake Animation; use frames0–660 at30fps, sample step1, simplify0, -Y Forward/Z Up, Apply Unit Scale, no leaf bones, no NLA strips and no All Actions. Do not run the procedural re-author command over those manual edits. Then run the same Unreal reimport command. Omit -CR03AnimationOnly only when deliberately updating the optic mesh and skeletal geometry as well. Inspect imported bones, duration and actual contact frames after changes; repackage only at the next relevant acceptance checkpoint.

Use forward slashes in ExecutePythonScript paths: the installed Python launcher interprets sequences such as backslash-r in a Windows path as escaped characters. These export/reimport commands were executed successfully for this milestone; this is not an unexecuted pseudo-workflow.


### Phase03 packaged acceptance and evidence

The normal game command above has no acceptance flags. For a deliberate future acceptance checkpoint, use the actual Development package and the same reference conditions (do not rerun merely because this documented checkpoint already passed):

```powershell
Set-Location 'D:\Projects\FPS Game'
$phase03 = 'D:\Projects\FPS Game\.environment-local\phase-03'
$game = Join-Path $phase03 'package\Windows\CinderRelay.exe'
$runArgs = '-CRRestorationCheck -windowed -ResX=1920 -ResY=1080 -ForceRes -NoVSync -ExecCmds="r.ScreenPercentage 100,r.DynamicRes.OperationMode 0,r.VSync 0,t.MaxFPS 0,sg.ViewDistanceQuality 3,sg.AntiAliasingQuality 3,sg.ShadowQuality 3,sg.GlobalIlluminationQuality 3,sg.ReflectionQuality 3,sg.PostProcessQuality 3,sg.TextureQuality 3,sg.EffectsQuality 3,sg.FoliageQuality 3,sg.ShadingQuality 3" -trace=cpu,gpu,frame,bookmark,loadtime -tracefile="D:/Projects/FPS Game/.environment-local/phase-03/restoration.utrace" -abslog="D:/Projects/FPS Game/.environment-local/phase-03/packaged-restoration.log"'
$run = Start-Process -FilePath $game -ArgumentList $runArgs -WindowStyle Hidden -Wait -PassThru
"Bootstrap exit: $($run.ExitCode)"
Get-Content -LiteralPath "$phase03\package\Windows\CinderRelay\Saved\Phase03\acceptance.json"
& 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' '.\CinderRelay\Scripts\summarize_combat.py' "$phase03\package\Windows\CinderRelay\Saved\Phase03" "$phase03\packaged-summary.json"
```

Inspect the fresh receipt, engine RequestExitWithStatus and runtime log together; this machine's bootstrap has returned777003 independently of the engine's result. The route uses actual movement, trace interactions, damage and native state. It is bounded at600s total/65s per stage. `-CRRestorationStart=1` is a Development-only corrective resume after scenario0 was separately proven; it is not a normal play option or a substitute for documenting omitted scenarios. PNG captures, pause and detailed tracing affect performance. Never treat this route as human animation/weapon-feel acceptance.

## Phase04 persistent checkpoints

Normal play opens the existing persistent map and displays New Game / Continue from Checkpoint. Esc exposes Continue and Restart Chapter; death exposes Retry from Last Checkpoint. Restart Chapter always resets session progress and preserves the stored checkpoint until a later natural checkpoint succeeds. Assembly remains optional; Tab skips it, Esc pauses it. A successful async callback displays CHECKPOINT SAVED; failed/incompatible saves remain on disk and show a recoverable message. No key is repurposed.

```powershell
Set-Location 'D:\Projects\FPS Game'
$crProject = 'D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject'
$crEngine = 'D:\Engines\Unreal\UE_5.8'
# Close Editor before compiling changed C++.
& "$crEngine\Engine\Build\BatchFiles\Build.bat" CinderRelayEditor Win64 Development "-Project=$crProject" -WaitMutex -NoHotReloadFromIDE
# Only needed to deliberately recreate/update the three owned checkpoint markers.
& "$crEngine\Engine\Binaries\Win64\UnrealEditor.exe" $crProject '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/generate_checkpoints.py' -unattended
# Dedicated CR04_TEST_Automation slots only; never the player slots.
& "$crEngine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" $crProject -unattended -nullrhi '-ExecCmds=Automation RunTests CinderRelay.Checkpoints' '-TestExit=Automation Test Queue Empty'
# One final Windows Development build/cook/package after integration.
& "$crEngine\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun "-project=$crProject" -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive '-archivedirectory=D:\Projects\FPS Game\.environment-local\phase-04\package' -nocompileeditor -installed -unattended -utf8output
# Normal play: no acceptance/test flags.
& '.\.environment-local\phase-04\package\Windows\CinderRelay.exe' -windowed -ResX=1920 -ResY=1080
```

`-CRCheckpointRoute=1/2/3` is a bounded Development harness using existing Enhanced Input movement/fire/interaction and the same menu handlers. It refuses player slots: supply `-CRCheckpointTest=<unique alphanumeric suffix>`. Route1 requires a fresh test prefix, fights, collects ammo and saves CP01; exit the process. Route2 uses that same prefix to restore CP01, collect salvage/module, validate Stop/pause/natural assembly, reload and save CP02; exit again. Route3 restores CP02, backtracks, checks consumed actors/story, restarts, dies to real enemies, retries/reloads three times, and reaches both upgraded and optional-bypass endings. Route2 `-CRCheckpointLifecycle` additionally exercises Skip, injected lethal damage during assembly, presentation actor destruction, Restart/world EndPlay and controller destruction. These deliberate faults are distinct from normal gameplay input. Receipt/CSV files live under native Saved/Phase04/<route>; inspect fresh timestamps, process IDs and logs, not only exit codes. Do not rerun completed acceptance routes to chase frame times.

For manual anchor repair: open L_CH01_Persistent, select CP00/01/02 in the persistent level, keep its exact checkpoint ID, position its marker inside the corridor above the floor, then click Snap To Safe Floor. It refuses penetration, a wrong CP02 ramp owner, or blocked capsule clearance. Save only that level. Runtime validates readiness and clearance again. Never move recovery onto a sublevel-owned actor or rerun Phase01 generators.

The completed acceptance used one packaged archive and three separate native processes. To reproduce only when a new change or investigation justifies it, use a fresh test prefix and evidence directory; the runner refuses existing test slots and never deletes saves:

```powershell
Set-Location 'D:\Projects\FPS Game'
$crPackage = 'D:\Projects\FPS Game\.environment-local\phase-04\package\Windows'
$crRunId = 'Review04_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$crEvidence = Join-Path 'D:\Projects\FPS Game\.environment-local\phase-04' $crRunId
& '.\CinderRelay\Scripts\run_checkpoint_acceptance.ps1' -PackageRoot $crPackage -EvidenceRoot $crEvidence -TestPrefix $crRunId
Get-Content -LiteralPath (Join-Path $crEvidence 'process-results.json')
& 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' '.\CinderRelay\Scripts\summarize_checkpoints.py' (Join-Path $crPackage 'CinderRelay\Saved') $crEvidence
```

The runner captures actual process handles/IDs and separates gameplay receipts, native exit, bootstrap exit and forced-stop status. It has a540s process bound and30s post-receipt shutdown allowance. Route1 uses the bootstrap executable, routes2/3 the native executable; this also provides a bounded exit-code comparison. The final accepted runs self-exited with777003 even for direct native launch, despite engine RequestExitWithStatus(0). A separate later interactive native UI run exited0 through the real Exit Game button without the route/unattended/trace flags. The automated-run discrepancy remains unresolved; those nonzero codes are not clean OS exits. AutomationTool packaging exited0. Do not hide the discrepancy or repeatedly repackage to investigate it.

Normal packaged saves are native CinderRelay_CH01_A.sav/B.sav. In this tested Development archive they are under package/Windows/CinderRelay/Saved/SaveGames; other build/platform configurations can redirect ProjectSavedDir. Test flags use CR04_TEST_<suffix>_A/B instead. Never delete/corrupt the owner's slots for testing. Restart/New Game preserves them until a subsequent natural checkpoint successfully replaces one generation. CP00 writes only if both slots are missing. Continue is unavailable while scanning/writing or when neither slot validates; recoverable error text retains existing files.

Interactive menu/HUD inspection was completed after the owner dismissed the Windows firewall prompt. Real clicks verified New Game, Esc/pause, Continue and Exit Game in the separate Visual04 process; Continue was disabled with no save, CP00 restored visibly, and bottom control/health/ammo text fit the observed window. Local actual captures are ui-restored.jpg and ui-paused.jpg. No network permission was changed by automation. Death-menu layout, other display configurations and full human playtest acceptance remain pending. This short UI check is not a repeated performance run.

## Phase05 vertical-slice presentation

Current source is the existing project and persistent map. Do not rerun Phase01A/01B/Phase03 generators. All new art is original project-authored content under ArtSource/Blender/Phase05; the old Phase03 source and Phase01A map remain rollback references. Blender4.5.11 and installed UE5.8.4 bindings were used.

Normal launch after the verified package exists:

```powershell
Set-Location 'D:\Projects\FPS Game'
& '.\.environment-local\phase-05\package\Windows\CinderRelay.exe' -windowed -ResX=1920 -ResY=1080
```

Use New Game or Continue, normal input, E interaction, Tab assembly/ending Skip, Esc pause, R reload and F5 streaming retry. Restart Chapter resets the session while retaining the stored checkpoint until a later natural successful save. No test flags are needed for play.

The authoring scripts are intentionally bounded to owned Phase05 assets; they are not required to play. `create_environment.py` writes the original kit; `refine_environment.py` adds the gantry/roof correction; `create_terminals.py` adds the two interactive visual shells. `create_warden.py` writes the six-clip enemy rig. `refine_restoration.py` creates the protected Phase03 derivative; `refine_rook.py` adds matching sight references; `tune_restoration_contact.py` changes only that derivative's hand/arm keys. FBX exports are temporary under ignored `.environment-local/phase-05/exports`. Source .blend files, scripts and the two512px textures are versioned. `create_audio.py` generates eleven original WAVs; `--only-loops` updates only the three ambient loops.

Native import/placement is in `generate_polish.py` and `import_polish_presentation.py`; `refine_polish_visuals.py` applies the final facing/task-light/contact adjustments and renders unsaved review poses. Preserve the order: base environment, presentation import, final refinements. Each writes only tagged/owned assets or explicitly audited visual settings. Do not casually rerun production generators over later hand edits. Read-only `validate_polish_assets.py` compares the local Phase04 baseline receipt; it requires that ignored pre-edit evidence, and correctly refuses to claim preservation without it. `audit_polish.py` can inventory a fresh checkout but must not relabel a post-edit inventory as the original baseline.

Reproduce validation only for a new relevant change, not as a repeated acceptance loop:

```powershell
$crEngine = 'D:\Engines\Unreal\UE_5.8'
$crProject = 'D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject'
# Only if C++ changed; close Editor first.
& "$crEngine\Engine\Build\BatchFiles\Build.bat" CinderRelayEditor Win64 Development "-Project=$crProject" -WaitMutex -NoHotReloadFromIDE
& "$crEngine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" $crProject -unattended -nullrhi '-ExecCmds=Automation RunTests CinderRelay.Checkpoints+CinderRelay.Restoration' '-TestExit=Automation Test Queue Empty'
# Real Editor route, not a replacement for packaged/visual acceptance.
& "$crEngine\Engine\Binaries\Win64\UnrealEditor.exe" $crProject '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/smoke_polish.py' -CRRestorationCheck -unattended
# Forward slashes in ExecutePythonScript avoid accidental Python escape sequences.
& "$crEngine\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun "-project=$crProject" -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive '-archivedirectory=D:\Projects\FPS Game\.environment-local\phase-05\package' -nocompileeditor -installed -unattended -utf8output
$crPackage = 'D:\Projects\FPS Game\.environment-local\phase-05\package\Windows'
$crRunId = 'Review05_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$crEvidence = Join-Path 'D:\Projects\FPS Game\.environment-local\phase-05' $crRunId
& '.\CinderRelay\Scripts\run_checkpoint_acceptance.ps1' -PackageRoot $crPackage -EvidenceRoot $crEvidence -TestPrefix $crRunId -LowOverhead
& "$crEngine\Engine\Binaries\ThirdParty\Python3\Win64\python.exe" '.\CinderRelay\Scripts\summarize_polish.py' (Join-Path $crPackage 'CinderRelay\Saved') $crEvidence
```

`-LowOverhead` omits requested Insights tracing and preserves1080p/Epic/native100% rendering, CSV counters and1Hz memory; default Phase04 tracing remains available. The three-process route uses fresh CR04_TEST slots, never player saves. Native/bootstrap exit, AutomationTool exit and gameplay receipts must be reported separately. Do not clear caches, force GC at transitions or repackage to improve statistics. The actual Phase05 results and unresolved limits are in MILESTONES/PERFORMANCE_BUDGET.

Phase05 interactive follow-up: the owner dismissed the Windows firewall prompt, then actual packaged menus/HUD were checked at1920x1080 windowed and2560x1600 fullscreen on the150%-scaled desktop. Native console `r.SetRes 2560x1600f` changed only the running display mode; no gameplay state was assigned through console. RHI logs confirm the2560x1600 backbuffer. Real New Game, Pause, Continue toCP02, Restart and Exit Game succeeded; visible process exit0. Bottom control/health/ammo layout and menus fit both modes; opening subtitles fit1600p. See MILESTONES for screenshot paths and remaining variants. No rebuild/repackage was needed for this check.
## Phase05.1 asset quality

Use the existing project and persistent map. The local final package is `.environment-local/phase-05-1/package/Windows/CinderRelay.exe`. Launch without Development test flags for owner play:

```powershell
Set-Location 'D:\Projects\FPS Game'
Start-Process -FilePath '.\.environment-local\phase-05-1\package\Windows\CinderRelay.exe' -ArgumentList '-ResX=1920 -ResY=1080 -fullscreen'
```

Editable source files in `CinderRelay/ArtSource/Blender/Phase051/`: `CR051_Rook5.blend`, `CR051_IndustrialDepth.blend`, `CR051_RookRestoration.blend`. Native imports live under `/Game/Generated/Phase051/`. The workbench uses `Animation/SK_CR051_Restoration`, `Animation/AN_CR051_RookRestoration`, and `Sequences/LS_CR051_RookRestoration` (22s). Review it by collecting either Survey Optic and interacting with the Workshop calibration bench; Tab skips, Esc pauses. The old Phase03/05 assets remain intact.

Source/export scripts use real Blender4.5.11 APIs. Do not run all authoring steps for a minor pose or material change. `create_rook.py` authors the hero source; `create_depth.py` authors the decorative kit; `rework_restoration.py` creates the derivative rig; `tune_quality_contact.py` edits its contact poses without rebuilding the kit. FBX export intermediates remain in ignored `.environment-local/phase-05-1/exports/`.

Example native import and read-only validation (close other Editors for this project first):

```powershell
$crEditor = 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$crProject = 'D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject'
# Import only when corresponding FBX files have intentionally changed.
& $crEditor $crProject -unattended '-ExecutePythonScript=D:\Projects\FPS Game\CinderRelay\Scripts\import_quality.py'
& $crEditor $crProject -unattended '-ExecutePythonScript=D:\Projects\FPS Game\CinderRelay\Scripts\import_quality_animation.py' -CR051ReimportAnimation
# This audit compares with this machine's ignored pre-mutation receipt.
& $crEditor $crProject -unattended '-ExecutePythonScript=D:\Projects\FPS Game\CinderRelay\Scripts\validate_quality.py'
```

`place_quality.py` owns only actors tagged `CR_Phase051_Generated`; it checks the original actor inventory before saving. `import_quality_animation.py -CR051Activate` intentionally switches the existing bench to the new soft references; old source/sequence assets are not overwritten. Do not invoke legacy greybox/migration generators. `review_quality_animation.py` and `audit_quality.py -CR051After` require the rendered `UnrealEditor.exe`, not NullRHI; they capture actual native frames and quit without saving temporary review poses/cameras. `-CR051PerimeterPair` compares new decoration hidden/visible from one fixed camera.

Focused native verification after C++ changes:

```powershell
& 'D:\Engines\Unreal\UE_5.8\Engine\Build\BatchFiles\Build.bat' CinderRelayEditor Win64 Development "-Project=$crProject" -WaitMutex -NoHotReloadFromIDE
& $crEditor $crProject -unattended -nullrhi '-ExecCmds=Automation RunTests CinderRelay.Presentation' '-TestExit=Automation Test Queue Empty'
```

Final Windows package and bounded cross-process acceptance:

```powershell
& 'D:\Engines\Unreal\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat' BuildCookRun "-project=$crProject" -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive '-archivedirectory=D:\Projects\FPS Game\.environment-local\phase-05-1\package' -nocompileeditor -installed -unattended -utf8output
& '.\CinderRelay\Scripts\run_checkpoint_acceptance.ps1' -PackageRoot '.environment-local\phase-05-1\package\Windows' -EvidenceRoot '.environment-local\phase-05-1\retest' -TestPrefix Phase051OwnerRetest -LowOverhead -Fullscreen
```

Use a fresh test prefix; the runner refuses to overwrite existing test saves. Do not run this during an owner playtest. Three process launches use only `CR04_TEST_` slots. `-Fullscreen` explicitly verifies1920x1080, avoiding desktop DPI/window-size clamping. Diagnostic sight fixture flags are `-CRCombatCheck -CRSightReview -CRSightLabel=review1080`; it includes nine poses, ending with close-wall lowering and realigned ADS. It directly uses the existing upgrade API and is **not** evidence of normal chapter completion. Add `-CRSightNoCapture` for a separate lower-overhead timing sample. Native chapter acceptance remains the actual-input checkpoint route.

## Phase05.2 presentation and contact

The project/map and player controls are unchanged. Obtain LFS objects, open the persistent map, and use Standalone. The active bench references Phase052; do not run old generators. To play the locally validated package without test automation:

```powershell
Set-Location 'D:\Projects\FPS Game'
Start-Process '.\.environment-local\phase-05-2\package\Windows\CinderRelay.exe' -WindowStyle Normal
```

Editable sources: `CinderRelay/ArtSource/Blender/Phase052/CR052_YardDetail.blend` and `CR052_RookRestoration.blend`. Authoring scripts accept `--export-dir`; run only when intentionally rebuilding these owned derivatives. `polish_presentation.py` and `import_contact_polish.py` use actual Editor operations and protect name ownership. The contact importer requires `-CR052Activate` to switch the existing bench's soft references. Do not mix a new animation source with stale FBX exports.

Read-only visual and camera-track checks (close other Editor/game instances first):

```powershell
$cr52Editor='D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$cr52Project='D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject'
$cr52Args='"{0}" -ExecutePythonScript="D:/Projects/FPS Game/CinderRelay/Scripts/review_presentation.py" -CR052After -unattended -nosplash' -f $cr52Project
Start-Process $cr52Editor -ArgumentList $cr52Args -WindowStyle Hidden -Wait
$cr52Args='"{0}" -ExecutePythonScript="D:/Projects/FPS Game/CinderRelay/Scripts/review_contact_polish.py" -unattended -nosplash' -f $cr52Project
Start-Process $cr52Editor -ArgumentList $cr52Args -WindowStyle Hidden -Wait
$cr52Args='"{0}" -ExecutePythonScript="D:/Projects/FPS Game/CinderRelay/Scripts/validate_contact_tracks.py" -unattended -nosplash -nullrhi' -f $cr52Project
Start-Process $cr52Editor -ArgumentList $cr52Args -WindowStyle Hidden -Wait
```

Forward slashes inside Unreal arguments avoid Python-script path escape problems. Pose captures use a fixed settled review camera and do not evaluate its animated track; the separate track validator performs actual native evaluation/Stop restoration. `validate_presentation_polish.py` requires the original pre-edit `before-inventory.json` and `protected-hashes.json` in the ignored Phase052 evidence directory. Do not recreate those from the changed map and call it an original-preservation test.

Final package / bounded regression commands used:

```powershell
& 'D:/Engines/Unreal/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' BuildCookRun '-project=D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject' -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive '-archivedirectory=D:/Projects/FPS Game/.environment-local/phase-05-2/package' -nocompileeditor -installed -unattended -utf8output
& './CinderRelay/Scripts/run_checkpoint_acceptance.ps1' -PackageRoot '.environment-local/phase-05-2/package/Windows' -EvidenceRoot '.environment-local/phase-05-2/packaged-acceptance' -TestPrefix Phase052Final -LowOverhead -Fullscreen
```

For a later rerun choose a new TestPrefix and evidence directory. Never overwrite player saves. Archive `Saved/Phase04` alongside process receipts before running any diagnostic video route, because the route-number output paths are reused. Do not record video or render Editor screenshots during performance sampling.


## Phase05.3 first-person handling

Active project/map and controls are unchanged. Gameplay arms and all seven handling clips load asynchronously from /Game/Generated/Phase053/Gameplay. The Workshop references the separate Phase05322s assembly sequence. Preserve Phase01A and earlier Blender sources; never rerun old greybox generators.

Editable sources: ArtSource/Blender/Phase053/CR053_FirstPerson.blend and CR053_RookRestoration.blend. author_first_person.py and author_restoration.py write only owned derivatives (explicit --rebuild-owned); rig_contact.py calibrates authoring poles. refine_hand_surfaces.py performs a guarded one-time covered-skin correction. Exports remain ignored under .environment-local/phase-05-3/handling-exports. Do not regenerate all actions for a small mesh correction.

Native import_first_person.py imports missing owned assets; explicit -CR053ReimportHandling reimports clips and -CR053ReimportHandlingMesh reimports the mesh. import_human_restoration.py uses -CR053ReimportAssembly/-CR053ReimportAssemblyMesh for the respective assets; -CR053ActivateAssembly switches only the existing bench's soft references. validate_contact_tracks.py -CR053Human checks actual sequence camera evaluation/Stop restoration without saving maps. review_human_restoration.py captures12 real poses; -CR053ContactOnly limits a targeted check to two contact moments. These captures do not replace continuous playback review.

Current locally packaged candidate and real recording (no test flags for ordinary play):

```powershell
Set-Location 'D:\Projects\FPS Game'
Start-Process '.\.environment-local\phase-05-3\package\Windows\CinderRelay.exe' -WindowStyle Normal
# Actual recorded gameplay, silent; not an animation render or benchmark.
Start-Process '.\.environment-local\phase-05-3\CR053_Gameplay_Review.mp4'
```

The new action-only source correction is reproducible without regenerating mesh/atlas/skeleton:

```powershell
& 'D:\Dev\Toolchains\Blender\blender-4.5.11-windows-x64\blender.exe' -b --python '.\CinderRelay\ArtSource\Blender\Phase053\refine_reload_framing.py' -- --replace-owned-derivative --export-dir 'D:\Projects\FPS Game\.environment-local\phase-05-3\handling-exports'
& 'D:\Dev\Toolchains\Blender\blender-4.5.11-windows-x64\blender.exe' -b --python '.\CinderRelay\ArtSource\Blender\Phase053\verify_reload_correction.py' -- --evidence-dir 'D:\Projects\FPS Game\.environment-local\phase-05-3\reload-fix' --export-dir 'D:\Projects\FPS Game\.environment-local\phase-05-3\handling-exports'
& 'D:\Engines\Unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' 'D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject' '-ExecutePythonScript=D:/Projects/FPS Game/CinderRelay/Scripts/import_first_person.py' -CR053ReimportHandling -unattended -nullrhi
```

Only run the above when intentionally updating the owned `CR053_FirstPerson_ReloadCorrected.blend` derivative. The correction starts from the preserved original and creates seven rollback actions; it updates the shared right grip in all seven clips plus Reload left-hand contact. It does not regenerate meshes, textures, rest poses, original Blender files or maps. The reimport flag updates animations only, not the skeletal mesh. Verification supports `--skip-renders` for a focused data-only rerun. `restoration_orientation.py` defines smooth contact orientation; `smooth_restoration_release.py` is a guarded one-time correction already applied to the saved workbench derivative. Do not reapply that correction to already-corrected fingers.

Full build/reproduction after a clean clone with LFS assets (not needed for a simple playtest):

```powershell
& 'D:/Engines/Unreal/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' BuildCookRun '-project=D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject' -noP4 -platform=Win64 -clientconfig=Development -target=CinderRelay -build -cook -stage -pak -archive '-archivedirectory=D:/Projects/FPS Game/.environment-local/phase-05-3/package' -nocompileeditor -installed -unattended -utf8output
& './CinderRelay/Scripts/run_checkpoint_acceptance.ps1' -PackageRoot '.environment-local/phase-05-3/package/Windows' -EvidenceRoot '.environment-local/phase-05-3/owner-retest' -TestPrefix Phase053OwnerRetest -LowOverhead -Fullscreen
```

The runner refuses existing test-prefix slots; choose a new prefix for an intentional later check. Preserve/inspect user save files independently. Do not run automation while the owner is playing. Archive Saved/Phase04 before a diagnostic route overwrites route-number receipts. The delivered low-overhead measurements precede the final single-clip framing edit; the latter has focused recorded package validation, not a repeated whole-route benchmark. Raw video/frames/trace/build files stay ignored locally; `docs/PHASE053_VALIDATION.json` records selected hashes/results.
