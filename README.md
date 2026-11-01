# CINDER RELAY

A narrative-driven single-player post-apocalyptic FPS, built with Unreal Engine 5.8, C++ and Unreal Blueprints.

**Active milestone: Phase05.3 — First-Person Arms and Weapon Handling.** Owner-approved anatomy is integrated into seven native weapon clips and the separate22s workbench derivative. Gameplay authority, schema1, native streaming and earlier rollback sources are retained. See [implementation, verification and art-review limits](docs/FIRST_PERSON_05_3.md). Final human continuous-motion acceptance remains pending. Phase06 is not authorized.

Reload follow-up: corrected the authored right wrist frame and left feeding-component grip in `CR053_FirstPerson_ReloadCorrected.blend`. Original sources and seven rollback actions remain intact. The seven shared-grip clips were reimported into the unchanged Skeleton; a fresh packaged recording and focused weapon fixture passed. The right hand now retains the primary grip while the left handles the component. Local fingertip/near-camera clipping remains; see the [diagnosis and evidence](docs/FIRST_PERSON_05_3.md#reload-rig-correction--2026-11-01).

[View the Phase 05.1 screenshots and actual assembly recording](docs/media/phase-05-1/README.md).

[View the earlier Phase05.2 matched environment/contact review](docs/media/phase-05-2/README.md). Current Phase05.3 local package: `.environment-local/phase-05-3/package/Windows/CinderRelay.exe`; launch without test flags for normal play. Three independent checkpoint/combat/restoration processes passed, all native/bootstrap exits0. Assembly p95=17.678ms at1080p/Epic versus17.057ms in the same-session unchanged Phase052 baseline; this does not meet a clean60FPS budget. First-use/recovery hitches and human motion-quality acceptance remain open. [Actual results and limitations](docs/PERFORMANCE_BUDGET.md#phase053-integrated-packaged-comparison-2026-11-01).

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

Phase03 historical delivery: Windows Development package and bounded functional acceptance passed after one documented test-harness readiness correction. Human animation/pacing acceptance remains pending; segmented hands are prototype art, and the Phase03 assembly p95=22.108ms was not a clean60FPS result. See [historical validation and limits](docs/MILESTONES.md#phase03-final-local-delivery-evidence). Phase05 uses an editable derivative, preserving the original source.

Preserved original source: `CinderRelay/ArtSource/Blender/Phase03/CR03_RookRestoration.blend`. Active derivative: `ArtSource/Blender/Phase052/CR052_RookRestoration.blend`, using `/Game/Generated/Phase052/Sequences/LS_CR052_RookRestoration`. Phase03/05/051 sequences and source remain available for rollback. Use the existing persistent map; do not rerun older level generators. See [Phase05.2 setup](docs/WINDOWS_SETUP.md#phase052-presentation-and-contact).

Phase04: New Game starts in the Rail Yard; Continue resumes the latest validated checkpoint. CP00 is created for a genuinely new save, CP01 activates inside the Workshop, and CP02 activates on the relay ramp after collecting the original power module. Saves contain health/ammo, objectives, enemy/pickup IDs, salvage/upgrade and one-time story flags. Progress after the latest successful checkpoint rolls back when recovered. Restart Chapter resets the session and preserves the stored checkpoint until a later natural checkpoint succeeds. A damaged/incompatible newer slot can fall back to the earlier valid generation; files are retained on failure. See [checkpoint setup](docs/WINDOWS_SETUP.md#phase04-persistent-checkpoints) and [validation ledger](docs/MILESTONES.md#phase04-persistent-world--implementation-plan-and-ledger).

Historical Phase04 package: `.environment-local/phase-04/package/Windows/CinderRelay.exe`; omit test flags for normal play. One Windows Development BuildCookRun and three separate packaged processes passed the bounded checkpoint acceptance route. Native Automation schema and disk-fallback groups passed. All three game processes closed themselves, but Windows returned777003 even when launching the native executable directly; engine exit logs requested0. This unresolved automated-run exit status is separate from gameplay receipts. A separate interactive native run exited0 through Exit Game. Actual New Game/pause/Continue clicks and current-window HUD fit were visually checked after the owner dismissed the firewall prompt; broader human playtest acceptance remains pending. Startup/recovery hitches remain; see [measured results](docs/PERFORMANCE_BUDGET.md#phase04-packaged-checkpoint-observations--2026-10-31).

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

Phase02 的武器、AI、资产生成与验证记录见现有 TECHNICAL_DESIGN / MILESTONES。用户短试玩负责枪感、瞄准遮挡和遭遇节奏；自动路线与截图不能代替这些判断。Phase05 delivery stops before Phase06.

## Phase05 presentation and local review

The map remains `/Game/Generated/Phase01B/Maps/L_CH01_Persistent`, with the same three streamed zones and checkpoint anchors. Original models/animations live in `CinderRelay/ArtSource/Blender/Phase05/`; imported content lives in `/Game/Generated/Phase05/`. No third-party packs or new saved IDs were introduced. See [art direction](docs/ART_DIRECTION.md), [source register](docs/ASSET_SOURCES.md) and [reproduction commands](docs/WINDOWS_SETUP.md#phase05-vertical-slice-presentation).

The opening is a player-controlled environmental reveal. Relay activation and the ending use actual4s/8s native light/audio Level Sequences; Tab skips the ending safely, Esc pauses. The22s workbench sequence keeps its existing Skip/Stop/Abort behavior. The original ending text remains unchanged. The enemy visuals use six imported skeletal clips driven by existing combat/AI events.

Phase05 is an original prototype art pass. Segmented hands, coarse cloth/metal surfaces, simple clip transitions and portions of the original architectural shell remain visible. A complete owner visual/pacing review is still required;12–16minutes is a design target, not a measured human playthrough. Do not treat automation or static frames as final animation-quality acceptance.


Historical Phase05 package: `.environment-local/phase-05/package/Windows/CinderRelay.exe`. One BuildCookRun passed; all three independent checkpoint/combat/restoration routes passed and exited0. Run without test flags for normal play.70 original Unreal assets and107 cosmetic/presentation actors supplement the173 preserved original actors. No claim of final human art acceptance or a measured12–16minute route. Assembly p95=15.891ms, route3 p95=17.694ms at1080p/Epic in the low-overhead sample; controlled recovery travel still takes38.685–99.894ms outside the gameplay frame table. See PERFORMANCE_BUDGET for exact conditions and measurement limits.

Packaged HUD follow-up passed at1920x1080 windowed and2560x1600 fullscreen: bottom controls, health/ammo, objectives and menus fit; actual New Game, Continue, Restart and normal Exit were inspected. Native exit0. Full human art/animation/audio and natural pacing acceptance remain pending.


## Phase05.3 candidate

Human first-person hands now accompany the existing ROOK-5: authored idle/walk/sprint/ADS/fire-cycle/reload/dry clips, a bounded once-per-shot cosmetic case effect and a22-second workbench derivative using the same anatomy. Combat balance, SaveGame schema1 and checkpoint/streaming architecture are unchanged. Current controls remain LMB fire, RMB aim, R reload, Tab assembly Skip and Esc pause. See [Phase05.3 implementation and evidence](docs/FIRST_PERSON_05_3.md); final human animation-quality acceptance remains pending.
