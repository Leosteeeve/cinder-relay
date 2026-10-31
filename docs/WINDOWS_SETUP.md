# Windows Setup and Reproduction

本机工作目录：`D:\Projects\FPS Game`。已安装引擎：`D:\Engines\Unreal\UE_5.8`，实际版本 5.8.4。VS 2026 Community 18.11.3，MSVC 产品版本 14.50.35739（目录 family 为 14.50.35717），Windows SDK 10.0.26100.0。不要因 family 文件夹名而误判为旧的 banned compiler。

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
