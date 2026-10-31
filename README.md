# CINDER RELAY

A narrative-driven single-player post-apocalyptic FPS, built with Unreal Engine 5.8, C++ and Unreal Blueprints.

**Active milestone: Phase03 — The Mechanic's Hands.** Optional Survey Optic salvage and a 22-second Workshop calibration presentation extend the existing ROOK-5. Editable Blender source, imported skeletal animation and a native Level Sequence live under Phase03. Segmented gloves and industrial geometry remain prototype art. Actual validation and unresolved issues are recorded in MILESTONES; Phase04 is not authorized.

- 游戏名：CINDER RELAY。
- 仓库：[Leosteeeve/cinder-relay](https://github.com/Leosteeeve/cinder-relay)，当前 **Public**（2026-10-31 远端查询；Phase 01A 未修改可见性）。
- 工作目录：`D:\Projects\FPS Game`；工程：`CinderRelay/CinderRelay.uproject`。
- 实际 Runtime 模块：`CinderRelay`；targets：`CinderRelay`、`CinderRelayEditor`。
- 引擎基线：UE **5.8.4 / CL 58902052**；Windows PC／Visual Studio。
- 目标硬件：RTX 5070 Laptop 8 GB VRAM、32 GB RAM。

## 打开原型

打开 `D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject`，默认地图为 `/Game/Generated/Phase01B/Maps/L_CH01_Persistent`。Play 下拉选择 **Standalone Game**：普通 PIE 的 Esc 默认会结束 Editor 试玩，Standalone 中 Esc 才作为游戏暂停键。原图 `/Game/Generated/Phase01A/Maps/L_CH01_Greybox` 保留为回滚参考，不由新地图加载。

WASD 移动、鼠标看、Shift 跑、Ctrl 蹲、Space 跳、E 交互、Esc 暂停；**LMB 射击、RMB 瞄准、R 装填，流送重试改为 F5**。铁路场可交战、退回或沿北侧铁路线绕行；侦察兵死亡不作为主线门槛。工坊前有一份有限弹药。进入工坊，在左侧工作台拿青色电力模块，沿后门坡道下行，在橙色 Relay Nine 终端安装，再调查青色信号台；死亡和结束菜单均支持重新开始。

Phase02 的精确生成、编译、打包和验收命令见 [WINDOWS_SETUP](docs/WINDOWS_SETUP.md#phase02-first-contact)，实际结果见 [MILESTONES](docs/MILESTONES.md)。不要运行 Phase01A generator 或 Phase01B migration 重建当前地图。

Phase03: recover the amber/teal Survey Optic from the cache near the Rail Yard starting area, or from the backup on the Workshop calibration bench. Press E at that bench, positioned separately from the original power module. Tab skips and applies the upgrade; Esc pauses. Completing or skipping adds the visible optic and changes ADS from65 to60degrees. The weapon works before the optional upgrade. Main objectives and `MERIDIAN NETWORK / CONNECTION RESTORED` are unchanged. Restart clears the upgrade and salvage session state.

Phase03 local delivery: Windows Development package and bounded functional acceptance passed after one documented test-harness readiness correction. Human animation/pacing acceptance remains pending; segmented hands are prototype art, and assembly p95=22.108ms does not meet the60FPS target. Play the local package at `.environment-local/phase-03/package/Windows/CinderRelay.exe`; omit all test flags for normal play. See [validation and limits](docs/MILESTONES.md#phase03-final-local-delivery-evidence).

Editable source: `CinderRelay/ArtSource/Blender/Phase03/CR03_RookRestoration.blend`. Unreal sequence: `/Game/Generated/Phase03/Sequences/LS_CR03_RookRestoration`. Use the existing persistent map; do not rerun older level generators. See [Phase03 setup](docs/WINDOWS_SETUP.md#phase03-restoration) for exact authoring, build and test commands.

## 游戏方向

2118 年，全球基础设施灾难性停摆 **The Quieting** 已过去数十年。28 岁的男性机械维修技师 **Elias Venn** 在恢复废弃设施、重新发现技术的过程中，逐渐揭开 **MERIDIAN** 网络的真相。

五个支柱：电影感环境叙事、第一人称射击、探索与回收、动画化武器修复／装配、从旧式机械装备向现代与未来技术成长。

首个垂直切片为 **Chapter 01 — The Dead Station**，目标 **12–16 分钟**，覆盖废弃铁路场、维修工坊和地下中继站。手工线性章节带小探索空间，优先原生 Level Streaming，而不是默认开放世界／World Partition。

## 文档入口

| 内容 | 文档 |
| --- | --- |
| 稳定开发规则 | [AGENTS.md](AGENTS.md) |
| 游戏设计 | [GAME_DESIGN.md](docs/GAME_DESIGN.md) |
| 故事事实与未定内容 | [STORY.md](docs/STORY.md) |
| 技术架构 | [TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) |
| 三分区流送 | [STREAMING_STRATEGY.md](docs/STREAMING_STRATEGY.md) |
| 性能预算／benchmark 协议 | [PERFORMANCE_BUDGET.md](docs/PERFORMANCE_BUDGET.md) |
| 来源与许可登记 | [ASSET_SOURCES.md](docs/ASSET_SOURCES.md) |
| 阶段计划、实际验证与后续门槛 | [MILESTONES.md](docs/MILESTONES.md) |
| 精确 Editor 步骤／PowerShell 命令 | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| 审计、构建证据与限制 | [PHASE00_VALIDATION.md](docs/PHASE00_VALIDATION.md) |
| 官方资料／决策记录 | [研究依据](docs/engineering/research-notes.md)、[决策日志](docs/engineering/decision-log.md) |

## 仓库与验证边界

源码、Config、descriptor 和真实 Editor 生成内容纳入版本控制，二进制沿用 Git LFS。Phase02 增加20个真实资产，修改原生流送的 persistent 与 RailYard 地图：铁路场新增两名侦察兵、一份弹药、导航边界和警示文字，共5个 Actor；persistent 增加原生 Recast 数据。155个原 Actor 的类别、世界/组件变换、碰撞、材质和交互设置比较无差异；原图和工坊/地堡地图保留。Binaries、Intermediate、Saved、DDC、打包输出、本机日志和 `environment-setup.json` 被忽略。没有外部素材包、凭据或手造二进制文件入库。

Phase 01A 已由用户接受。01B 的 Editor 路线已验证三轮回访、门保护、模块/终端防重复、结束和重开；NullRHI 结果不证明渲染或性能。Editor 启动仍有 Phase 00 已知的引擎自测条件错误，不能声称 clean log。packaged 结果、性能口径与剩余限制统一记录在 [MILESTONES](docs/MILESTONES.md) 和 [PERFORMANCE_BUDGET](docs/PERFORMANCE_BUDGET.md)。

保留 CinderRelay 模块、EngineAssociation GUID 和模板渲染设置；未改引擎源码。01B 在功能验证后将默认地图改到 persistent，Packaging 明确包含四图。Python/EditorScriptingUtilities 仍仅 Editor target；AndroidFileServer 继续停用。

Phase02 的武器、AI、资产生成与验证记录见现有 TECHNICAL_DESIGN / MILESTONES。用户短试玩负责枪感、瞄准遮挡和遭遇节奏；自动路线与截图不能代替这些判断。不会自动开始 Phase03。
