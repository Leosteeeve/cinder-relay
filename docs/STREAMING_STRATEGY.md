# Chapter 01 — Native Level Streaming

Phase 01B 在已接受的 Phase 01A 基础上实施。手工线性章节使用一个 persistent world 与三个 `ULevelStreamingDynamic` 子关卡，由脚本请求控制；不使用 World Partition、Level Streaming Volumes 或跨区 OpenLevel。原图保持为回滚参考。

## 地图与 Actor 所有权

地图目录均为 `/Game/Generated/Phase01B/Maps/`。

| 资产 | 原 Actor | 新 Actor | 内容 |
| --- | ---: | ---: | --- |
| L_CH01_Persistent | 15 | 3 | PlayerStart、4 个全局环境 Actor、10 个入口立面/门框/标牌；1 控制器、2 遮挡门 |
| L_CH01_RailYard | 86 | 0 | 铁路、车厢、仓库、场地，X -2000～1600，Y ±1400，地面 Z=0 |
| L_CH01_Workshop | 22 | 0 | 工坊主体、工作台、模块、entry trigger，X 1600～3600，Y ±700，地面 Z=0 |
| L_CH01_RelayBunker | 32 | 0 | 坡道与地下站；X 3600～7200；坡道 X 3600～5400，Z 0→-600 |

原始 155 个具名生成 Actor 全部保留。Persistent 的 10 个 B 区例外：`CR_WorkshopFront-440/440`、`CR_WorkshopLintelFront`、`CR_WorkshopRear-440/440`、`CR_WorkshopLintelRear`、`CR_WorkshopEntrance`、`CR_EntranceStripe-205/205`、`CR_BunkerDirection`。这些小型遮挡立面让关闭的门有完整边框，避免相邻主体卸载后露出空白。

回滚图：`/Game/Generated/Phase01A/Maps/L_CH01_Greybox`，原始 SHA256 `C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733`。新 persistent 不引用或加载此图。引擎自身的 WorldSettings/LevelScriptActor 不计入 155 个内容 Actor。

## 运行时策略

`ACRChapterStreamingController` 只管理本章三个引擎流送对象。软地图引用通过 `GetStreamingLevel` 解析已注册对象，`SetShouldBeLoaded/SetShouldBeVisible` 提交原生目标状态；加载/显示/隐藏/卸载委托触发重算。0.25 s watchdog 只检查三项状态、丢失事件和超时，不做每帧世界搜索。

这里直接使用原生 desired flags，而不叠加 `LoadStreamLevel/UnloadStreamLevel` latent actions：反向请求由引擎自身协调，不存在重复 latent UUID 或 callback owner。每次 desired 改变仍增加 request ID，便于追踪。加载与卸载均不阻塞。

状态：Unloaded → Loading → LoadedOrShowing → Ready；离开时 Unloading → Unloaded；超时或失败进入 Failed。Ready 需要 loaded、visible、所属关卡地板 trace/注册物理组件及已 BeginPlay 的必要交互 Actor；B 还要求 workshop entry，C 要求 access ramp。固定等待时间不是 Ready 条件。

`ACRGameMode` 在 A Ready 前保留 PlayerController、暂缓生成角色。A Ready 后按原 GameMode 流程生成一次角色；跨区不销毁角色/Controller，也不重置 GameMode。BeginPlay 初始化保护避免测试/overlap 在流送对象绑定前误报失败。

## 两道门、预载与回访

`ACRStreamingGate` 位于 X=1600（AB）、3600（BC），门洞 Y ±180、净高 350 cm。关闭时有真实 BlockAll 碰撞与不透明面；双方均需要且 Ready 才开放。卸载请求前先关门。

- 预载 Box：门平面前后 800 cm，Y ±1450，Z ±1100；Pawn 进入时要求两侧区域。
- 保留 Box：前后 1000 cm；离开后取消邻区需求，形成 200 cm 滞回。角色胶囊半径 42 cm 也影响实际 overlap 位置。
- 门口保护：中心距门 <230 cm 强制保留双方，避免在角色穿越时卸载支撑几何。
- CurrentZone 的切换采用 160 cm 滞回：A→B X>1760，B→A X<1440；B→C X>3760，C→B X<3440。
- 通常只有当前区；接近门时保留当前区和必要邻区。极短边界重叠可临时保留三者，不允许卸载当前区。
- 最大 sprint 500 cm/s。800 cm 几何提前量约 1.6 s；最终是否有足够余量以 packaged 实测表为准，不能用 PIE 延迟证明。

失败时门保持关闭，HUD 显示 `Access unavailable. Press F5 to retry.`。Phase02 将重试移到 F5，为 R 装填让出键位；重置请求期限与恢复语义不变。UE 原生 FailedToLoad 状态仅在无 loaded level 时，通过 `SetWorldAsset` 重新设置相同软引用恢复 Unloaded（本机 5.8.4 源码已核对）。缺失地图文件无法靠重试补齐，仍须修复 cook；重试不能打开不满足条件的门。

## 目标与卸载引用

唯一章节状态仍是 `ACRGameMode/ECRObjective`：ReachWorkshop → FindModule → RestorePower → InvestigateSignal → Complete。`ACRInteractionActor::BeginPlay` 从进度恢复 bUsed；已取模块隐藏并关闭碰撞，终端不会重复奖励或播放完成事件。WorkshopTrigger 的 TryAdvance 仍要求旧状态匹配。没有新增库存、任务框架或磁盘存档。

控制器和验收器只持有区域 Actor 的弱引用；门只弱引用控制器。EndPlay 解绑委托、清 timer。日志中的 `witness_valid` 区分隐藏/卸载与旧 Actor 仍被缓存持有；Unloaded 必须同时满足原生状态、loaded=false、visible=false、desired=false。引擎资源缓存、异步删除与显存池不要求立刻归零；不逐区强制 GC。

## 安全迁移与恢复

`Scripts/migrate_streaming.py` 必须在**完整 Editor**以 `-ExecutePythonScript` 运行。先复制原图，再用 `EditorLevelUtils.create_new_streaming_level` 与 `move_actors_to_level` 搬移，保留 Actor 世界变换、类别、组件变换、材质、碰撞、灯光与交互设置。原图文件 hash 前后相同。不是删除并手动重建对象。运行时模块没有 UnrealEd 依赖。

输出 `Saved/Phase01B/migration.json`（逐 Actor 归属）和 `migration-comparison.json`（前后属性）。完成后的再次执行只审计；部分已拆分或未拥有的目标会拒绝自动修复。仅一个尚未拆分、带 ownership 且全部属性等于原图的 persistent 副本允许安全续作。不要再运行 Phase 01A generator。

若自动迁移阻塞：在 Editor 复制原图到 persistent；Window → Levels 创建三个空关卡，Streaming Method 设 Blueprint；先按上表选中 persistent 例外，再按区域 tag 选择剩余 Actor，Levels 中对目标使用 Move Selected Actors to Level。保留世界坐标，保存四图；逐项核对原 155 个 Actor 和门/控制器，再验收。未经 inventory 对比不能宣称迁移成功。

## Cook 与验收边界

三个子图在 persistent 的 Levels 中注册，均非 Always Loaded、初始不载入/不显示、无 Streaming Volumes。Packaging 明确列四图；默认图切换只在功能验证后进行。Editor 能读到资源不代表 packaged cook 完整。

`smoke_streaming.py` 重新打开四图并检查归属，再启动 PIE。`-CRStreamAcceptance` 只在非 Shipping 生成 `ACRStreamingAcceptance`；它注入 Enhanced Input、转向相机、沿固定路径行走，绝不 teleport 或直接设置目标。包括 Ready veto、反向取消、一次失败/重试、三次 C→B→A→B→C、模块/终端防重复、结束及 Restart。生产流程不依赖测试 veto；veto 本身最多 20 s。

完整运行证据见 MILESTONES，设置/数据口径见 PERFORMANCE_BUDGET。自动路线不是人工手感或所有碰撞面的视觉验收。

## 官方依据与其他结构

核对 UE 5.8 官方 [Level Streaming Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/level-streaming-overview-in-unreal-engine)、[C++ loading/unloading](https://dev.epicgames.com/documentation/unreal-engine/loading-and-unloading-levels-using-cplusplus-in-unreal-engine)、[ULevelStreaming](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/ULevelStreaming)、[MoveActorsToLevel](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/UnrealEd/UEditorLevelUtils/MoveActorsToLevel?lang=en-US)、[Packaging](https://dev.epicgames.com/documentation/unreal-engine/packaging-your-project)。官方 C++ 教程示例使用阻塞参数，本章依用户要求使用非阻塞 native flags。

| 世界结构 | 适合方案 |
| --- | --- |
| 独立线性章节 | 独立 map + 明确章节 travel；章内可 streaming |
| 连续室内/本章 | Persistent + 原生 scripted sublevels + 受控遮挡边界 |
| 小枢纽 | 枢纽 + 必要邻区；远任务独立地图，根据回访预算决定 |
| 大连续室外 | 另行评估 World Partition、sources、HLOD；不可据此改写本章 |

## Phase03 Workshop presentation ownership

The four existing maps and boundary policy remain unchanged. Added actors are owned only by L_CH01_RailYard (cache/stand/sign) and L_CH01_Workshop (calibration bench/backup/sign). The bench is at (2300,-350,0)cm, separate from the original power module at (2800,-365,127). Native LevelSequenceActor uses SpawnParameters.OverrideLevel=Workbench.GetLevel(). Its async handle and temporary hard references are released on EndPlay; the persistent controller's active workbench pointer is weak. The player cannot move during calibration, so normal coordinate-based streaming does not unload the occupied Workshop. No persistent streaming-controller changes, level pins or custom streaming framework are introduced.

After Workshop reload, GameMode flags restore hidden salvage and completed workbench state. The pawn retains its own small weapon appearance assets and upgrade lookup. Restart travels to the existing persistent map and starts a fresh GameMode. A PIE asset load is not proof of cooked coverage; see the separate Phase03 Windows package evidence in MILESTONES.
