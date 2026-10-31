# Phase 00 — Audit and Validation

日期：2026-10-31（America/Los_Angeles）。证据分为磁盘／构建、Editor 观察、Git／remote；不把其中一种当成另一种的通过。

## 初始审计

- 工作目录 `D:\Projects\FPS Game` 已有未产生提交的 main 和本地 LFS 配置，无 remote。
- 初始文件：.gitignore、.gitattributes、.vsconfig、environment-setup.json，以及被忽略的本机环境日志；之后有本聊天前半段生成的 Threshold 规划草稿。
- 初始目录没有 `.uproject`、C++ modules、Source、Content、输入或地图配置。没有 ThresholdFPS 模块可迁移。
- 已安装 UE 5.8.4 / CL 58902052，Build.bat、UBT、Editor、UnrealInsights 可见。VS Community 2026 18.11.3、MSVC 14.50.35739、SDK 10.0.26100.0 已核验。Git 2.55.0.windows.2、Git LFS 3.7.1、GitHub CLI 可用。
- GitHub 浏览器与 CLI 账户为 Leosteeeve。CLI 首次在受限网络中报 auth/connection 错误；正常网络权限下 keyring 登录成功，因此没有重新授权、读取 token 或导出 cookies。
- 原 environment-setup.json 内的 UEToolchainCheck 历史成功不是本项目构建。该记录原样保留且不上传。

## 原生工程结果

通过已安装 Unreal Editor 的 Games → Blank → C++ → Desktop → Maximum 创建 `CinderRelay/CinderRelay.uproject`。不是文本伪造项目或二进制资源。完整手动步骤与 PowerShell 命令见 [WINDOWS_SETUP](WINDOWS_SETUP.md)。

| 检查 | 结果 |
| --- | --- |
| 实际模块 | CinderRelay，Runtime／Default；源码只含原生 module bootstrap，未新增 gameplay class |
| Targets | CinderRelay Game、CinderRelayEditor Editor；V7 build settings，Unreal5_8 include order |
| Build.cs | Core、CoreUObject、Engine、InputCore、EnhancedInput；无自制 manager/plugin |
| 插件 | 原生 ModelingToolsEditorMode 保持 Editor-only；显式关闭 Windows 项目未使用的 AndroidFileServer，原因见下文；不表示引擎默认插件全被禁用 |
| Content | 当前为空，用 .gitkeep 保留；没有 .uasset／.umap；没有保存 Editor 展示的 OpenWorld 模板作为第一章 |
| Config | 保留原生 DefaultEngine／Game／Input／Editor，唯一功能调整为移除 AndroidFileServer 自动生成配置段；GameDefaultMap 指向 /Engine/Maps/Templates/OpenWorld，不是本项目章节 |
| Renderer | 保留 Desktop／Maximum 生成设置，包括 DX12／SM6、Lumen、RT、Substrate；未做性能承诺或未经说明的优化 |
| EngineAssociation | Editor 生成 GUID，常见 HKCU／HKLM lookup 未解析；已用确切 5.8.4 引擎启动，跨机器关联仍须核验 |

## 编译证据

Editor 创建流程执行的 UBT command line：

```text
UnrealBuildTool.dll Development Win64 -Project=D:/Projects/FPS Game/CinderRelay/CinderRelay.uproject -TargetType=Editor -Progress -NoEngineChanges -NoHotReloadFromIDE
```

原始调用中带空格的 Project 参数已加引号。日志确认：Parsing headers for CinderRelayEditor；Internal UnrealHeaderTool；7 个 actions，含 C++ 编译和 `UnrealEditor-CinderRelay.dll` 链接；`Result: Succeeded`；**55.91 秒**。后续 descriptor 调整只进行一次有明确理由的定向编译核验，结果另行记录。

- 原始证据保留：`.environment-local/cinder-phase00/unreal-baseline-build.log`（本机忽略，不上传含本机信息的原始日志）。
- SHA256：`FF3B5B2CE8752E5AEC02DEFD7B29A0AE050DB3918ABB8912CA954F497D2CAC56`。
- 产生 DLL：`CinderRelay/Binaries/Win64/UnrealEditor-CinderRelay.dll`，49,664 bytes；为生成物，不提交。
- MSVC：14.50.35739；Windows SDK：10.0.26100.0。
- Editor 拥有该编译子进程，工具没有直接捕获它的 OS exit code；以原始 UBT Succeeded 和实际链接输出为证，**不伪造 exit code 0**。

前半段独立 C++20 smoke 也返回 0，但它仅证明编译工具链；本项目 UBT 证据以上述 CinderRelay 构建为准。

### descriptor 配置调整后的定向核验

关闭 Editor、停用未使用的 AndroidFileServer 并清理生成配置后，执行一次 `Build.bat CinderRelayEditor Win64 Development`，完整参数采用 [WINDOWS_SETUP](WINDOWS_SETUP.md) 的编译命令。UBT 因 `.uproject file is newer` 更新 makefile，执行 4 actions（编译、lib／DLL 链接、metadata），`Result: Succeeded`，**17.83 秒，直接捕获 exit code 0**。这次核验由实际 descriptor 变更触发，不是无理由重复全量测试。

- 本机原始日志：`.environment-local/cinder-phase00/descriptor-build.log`。
- SHA256：`C02C73F189004A1BEA608EC5A4C148DB397F10BA6214597265CAD94916DE9A23`。
- 退出码 receipt：`.environment-local/cinder-phase00/descriptor-build-result.json`。
- 未再次启动 Editor／重跑引擎测试；以下 13 条启动诊断未被修复或重新验证。

## Editor 观察与已知诊断

Editor 窗口为 `CinderRelay - 虚幻编辑器`，实际观察到默认 OpenWorld 场景。日志确认 CinderRelay DLL 被加载、`Engine is initialized`，首次 Editor startup 约 338 秒，伴随初次 shader／RT PSO 编译。这不是游戏 benchmark，不能据此推算切片帧率。

启动日志有 **13 条 `LogAutomationTest: Error: Condition failed`**，没有声称 clean log 或全测试通过。它们邻接 `UE::UnifiedErrorTest` 输出；安装源文件 `Engine/Source/Runtime/Core/Tests/Experimental/UnifiedError/UnifiedErrorTests.cpp` 存在 SmokeFilter 测试及英文文本比较，日志相关输出为中文。**本地化／硬编码文本断言是待验证假设，尚未证明全部 13 条来源或修复。** 本轮没有改引擎、禁用测试、切换全局语言或反复 rebuild。

后续诊断应先按该测试组隔离获取具体断言结果，再判断是否为 engine-side issue；不要将其直接归因到尚未存在的玩法。此项不抹去编译成功，但阻止“Editor 无错误”的结论。

## Git 与分发核验方式

暂存审查发现 Editor 在第一次配置扫描后自动追加 AndroidFileServer 设置与本机 SecurityToken。该文件立即移出暂存区，未提交或上传。安装源码 `Engine/Plugins/Runtime/AndroidFileServer/Source/AndroidFileServerEditor/Private/AndroidFileServerRuntimeSettings.cpp` 确认 `PostInitProperties` 会在 `[AUTO]` 默认值下生成 GUID 并调用 `TryUpdateDefaultConfigFile`。正常关闭本轮 Editor 后，删除整个自动生成段，并在 `.uproject` 显式停用该未使用插件；这是 Windows-only 项目的最小功能配置调整。没有更改凭据账户、放宽权限或修改引擎。检查加入 SecurityToken 模式并以最终暂存内容为准；其余修改仅清除模板行尾／文件末尾多余空白。

已有 Git／LFS 被保留；.uasset／.umap 的 filter=lfs 已查询，生成目录与本机环境文件的 ignore 已查询。浏览器创建的仓库由 `gh repo view` 核验为 **Leosteeeve/cinder-relay，PRIVATE，初始 empty**；未创建 README／license 冲突提交。

本轮仅按用户授权提交与推送明确列出的生产文件；提交前检查 staged diff、凭据模式、体积、所有 local links 与生成文件排除。initial commit SHA 由 Git 本身记录，避免在该提交内嵌自引用 hash。收尾使用下面独立证据，具体结果随最终报告交付：

```powershell
git status --short --branch
git branch -vv
git remote -v
git log -1 --oneline
git rev-list --max-parents=0 HEAD
git rev-parse HEAD
git ls-remote origin refs/heads/main
gh repo view Leosteeeve/cinder-relay --json nameWithOwner,url,visibility,defaultBranchRef
```

只有本地 HEAD 与远端 main 完整 SHA 一致、push 返回成功，才报告推送完成。原始核验 receipt 保存在被忽略的 `.environment-local/cinder-phase00/`；没有 force push。

## 尚未验证与下一步

没有项目 gameplay tests、packaged build、运行时流送、存档、性能 benchmark 或人工玩法验收。跨机器 EngineAssociation 关联与 13 条启动测试错误仍须后续核验。没有新增/修复游戏系统，进入 P01 前按 [MILESTONES](MILESTONES.md) 启动独立任务。
