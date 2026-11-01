# CINDER RELAY — Technical Design

## 确认基线与实施边界

用户确定 UE 5.8、Windows／Visual Studio、C++ 核心和 Blueprint 支持层。本机安装 UE **5.8.4 / CL 58902052**。Phase 00 初始审计没有任何 `.uproject` 或旧 `ThresholdFPS` C++ 模块；工程采用 `CinderRelay`，通过 Unreal Editor 原生 Blank C++ 流程创建，具体结果见 [Phase 00 验证记录](PHASE00_VALIDATION.md)。Phase 01A 审计确认该工程、clean main 和既有 origin，并在其上增量实施，没有进行模块重命名。

保留已安装引擎，不修改引擎源码。工程／模块改名、引擎升级和架构替换需先有迁移计划及授权。Phase 00 不包含第一人称移动、射击、任务、修复、存档或流送系统实现。

## 工程与模块

### Phase 01A 已实施的增量

保留 `CinderRelay` 单 Runtime 模块；增加 UMG 公共依赖及 Slate／SlateCore 私有依赖。没有新 runtime plugin、manager、移动／物理框架。`PythonScriptPlugin` 与 `EditorScriptingUtilities` 仅在 Editor target 启用：Epic 将其列为实验／Beta 编辑工具，本阶段用其生成标准资产，运行游戏不依赖 Python。已核实 UE 5.8 官方 Unreal MCP 及本机插件存在，但未连接或启用：当前原生 Python 已满足资产生产，避免增加实验性接入路径。

| 新类 | 职责与编辑方式 |
| --- | --- |
| ACRCharacter | 原生 CharacterMovement／capsule／第一人称 camera；Enhanced Input；10 Hz 相机 trace，E 时再次校验；Blueprint 可调速度、灵敏度、距离和输入资产 |
| ICRInteractable / UCRInteractable | CanInteract、GetInteractionPrompt、Interact 三个 BlueprintNativeEvent；不查找全场景 |
| ACRInteractionActor | Blueprint 可配置 PowerModule／Relay／Signal；检查当前目标、距离和视线；本地 used guard 防重复；模块拾取后隐藏并关闭碰撞 |
| ACRWorkshopTrigger | 仅 Pawn overlap 驱动到达工坊，重复进入不重复推进 |
| ACRGameMode | 章节局部 ECRObjective 单枚举、期望状态检查和事件广播；没有任务框架／GameInstance 世界引用 |
| ACRPlayerController | 订阅 HUD 更新，Esc 暂停、释放鼠标、恢复、重新开始与退出 |
| UCRHUDWidget | 原生 UMG WidgetTree：目标、提示、准星、控制说明、暂停和结束菜单；无每帧 UI binding |

生成 Blueprint：BP_CRCharacter、BP_CRGameMode、BP_PowerModule、BP_RelayTerminal、BP_SignalConsole。真实 Input Actions／IMC 在 `/Game/Generated/Phase01A/Input`；W/S/A/D 使用四个 Boolean actions，以原生 AddMovementInput 合成方向，鼠标两条 Axis1D，Shift／Ctrl／Space／E 为动作。Esc 使用可在暂停时执行的 Controller key binding，UI 焦点收到 Esc 时由 UMG 处理。关闭旧输入平滑、FOV 缩放和 legacy scales，灵敏度由角色显式参数控制。

本地输入 context 在 BeginPlay 及 PawnClientRestart 幂等安装；保存所属 subsystem 弱引用，EndPlay 只移除本角色 context。暂停清理 sprint／jump／crouch 请求并 flush keys。镜头位于 capsule 内，85° FOV、pitch 限制 ±80°，无 head bob；蹲姿仍由原生站起空间检查控制。默认 walk/sprint/crouch 为 300/500/160 cm/s，交互距离 250 cm。

目标序列：到工坊 → 找模块 → 在 Relay Nine 安装 → 查看恢复信号 →结束菜单。结束只暂停当前世界，Restart 使用原生 map travel 重置本章；这是显式菜单转换，不在交互路径同步加载大资源。尚无 combat、AI、磁盘 save 或动画装配。

### Phase 01B 增量

保留全部 Phase 01A 类型、Blueprint 和输入资产。新增 `ACRChapterStreamingController`（三个原生 sublevel 的需求/就绪/失败/卸载）、`ACRStreamingGate`（遮挡门和预载/保留/门口 overlap）；详见 [STREAMING_STRATEGY](STREAMING_STRATEGY.md)。没有新增 runtime plugin、UnrealEd 依赖或自制资源流送框架。

`ACRGameMode` 增加 A 就绪前暂缓初始角色生成；正常跨区保留同一角色、Controller、GameMode。`ACRInteractionActor::BeginPlay` 从 GameMode 恢复 bUsed 和已取模块的隐藏/碰撞状态，不重播完成事件。`ACRPlayerController` 增加流送重试，UMG 增加轻量状态文本；原目标/暂停/结束逻辑保留。Phase02 为装填保留 R，重试现为 F5。

`ACRStreamingAcceptance` 是显式 `-CRStreamAcceptance` 开关的非 Shipping 验收器，不放置进地图，正常游戏不生成。它只驱动原生移动/输入和公开交互，记录 frame CSV、进程内存及通过/失败 receipt。非 Shipping 的 RenderCore/RHI 私有依赖仅用于读取引擎原生线程和 GPU frame 计数器；不是渲染系统改写。

Editor 脚本 `migrate_streaming.py` 用复制世界及 MoveActorsToLevel，验证 155 个 Actor 无丢失/重复/属性改变。`smoke_streaming.py` 在新进程重开四图验证归属再 PIE。命令行窗口退出码、资产 receipt、实际玩法 receipt 三者分别报告；Editor Python 清理错误不能被吞掉或当作玩法成功。

项目实际路径：`CinderRelay/CinderRelay.uproject`；源码：`CinderRelay/Source/CinderRelay/`；与根目录文档共用一个 Git 仓库，不嵌套 Git。

Windows 项目显式停用未使用的内置 AndroidFileServer 插件。其 Editor 设置初始化会自动将 SecurityToken 写入默认配置；本轮在提交前删除该生成配置段并关闭插件，避免重新生成凭据。其他模板功能／渲染设置保留；未来确需 Android 部署时单独评估，不将开发服务器凭据提交到 Git。

先保留原生 Blank 模板的单一 Runtime 模块和 Game／Editor targets。沿用生成的 Build.cs／Target.cs；只为实际使用添加依赖，公共头使用的依赖才列 Public，其余优先 Private。Runtime 不依赖 `UnrealEd`；确有独立编辑器工具时才拆 Editor 模块。不要为潜在未来系统创建空 manager、plugin 或 interface。[Epic Modules](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-modules)。

选择 Blank 的依据：本机 First Person C++ 模板的 TemplateDefs 写明包含所有变体，Build.cs 带 AI、StateTree 和 UI 依赖；Blank 更适合本轮最小 bootstrap。后续复用引擎能力，不重新实现 CharacterMovement 或物理。这个选择不要求以后复制全部模板或清理工作中的系统。

## 按需实施的职责

| 能力 | 原生能力／C++ 责任 | Blueprint／Editor 责任 |
| --- | --- | --- |
| 第一人称控制 | `ACharacter`、CharacterMovement、PlayerController、原生相机；动作状态与输入绑定 | 角色派生、相机位置、输入资产、碰撞／镜头检查 |
| 输入 | Enhanced Input action/context 生命周期，处理取消／完成与输入模式恢复 | Input Actions、Mapping Contexts、灵敏度与参数；不沿用自定义输入轮询框架 |
| 射击／交互 | 必需状态、UE collision trace／damage、交互校验；复用需求出现再抽 component | 武器参数、反馈、遭遇编排、可交互 Actor 派生 |
| 回收／修复 | 少量稳定物品 ID、数量／条件与交互状态 | 修复顺序、Montage／Sequencer、工具和部件摆位；不先做全物理装配模拟 |
| 叙事／UI | 必需任务事件与持久值；不每帧搜索全世界 | 小型 Blueprint 编排、Sequencer、UMG 字幕／提示；跳过／结束均恢复控制 |
| AI | AIController、Navigation、Perception；一个合适的原生状态方案 | Behavior Tree 或 StateTree 按具体遭遇选择一个，不预置两套 |
| 动画／音频 | SkeletalMesh、AnimInstance、AudioComponent 的原生生命周期 | Animation Blueprint、Blend Space、Montage／Notify、必要的 IK／retarget；声音衰减和并发 |
| 存档 | `USaveGame`、版本号、稳定 ID，异步 slot 读写和失败结果 | 检查点布置、提示、恢复后的表现 |
| 世界／内容 | 原生 Level Streaming、默认 Asset Manager／StreamableManager、load handles | persistent level、三个区域、软引用与依赖审核 |

这是职责分配，不是本轮的类生成清单。C++ 定义规则和所有权，Blueprint 编排内容；只暴露需调节的属性，使用合理类别／范围／默认值。普通配置先用 Data Asset，确需 ID／bundle 管理才用 Primary Data Asset。[C++ 与 Blueprint](https://dev.epicgames.com/documentation/en-us/unreal-engine/coding-in-unreal-engine-blueprint-vs-cplusplus)、[Enhanced Input](https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine)。

## 生命周期与可调试性

### Phase02 combat increment

`UCRHealthComponent` owns clamped health and native OnTakeAnyDamage subscription; death fires once. `UCRWeaponData`/DA_Rook5 owns tunable balance and small required audio/material references. `UCRWeaponComponent` owns ammo, accepted shots, native camera/muzzle collision traces, ApplyPointDamage, cycling/reload timers and aim/sprint flags. `UCRWeaponViewComponent` subscribes to presentation events and interpolates first-person primitives/FOV independently; only cosmetic interpolation uses Tick. It checks nearby cover at 10Hz, without per-frame asset discovery. Timers pause with the world; EndPlay/death cancel them. UMG updates ammo/health from events, with short native visual pulses for hits/damage.

`ACRAshWarden` is one Character class with health and an abstract humanoid silhouette. `ACRAshWardenController` uses AI Perception sight/hearing, weak target reference, last-known position and bounded memory. Native BT_AshWarden executes one C++ `UCRBTTaskWarden` followed by a 0.25s native Wait; BB_AshWarden exposes State/HasSight/LastKnown. Decisions are Idle → Investigate/Combat → Search → Return, with WaitingNavigation and Dead states. Attack requires perceived sight plus a fresh collision trace; hearing alone cannot authorize a shot. Move requests coalesce, failed requests back off and stop after two failures until a new legitimate stimulus/state reset. No EQS/GAS/networking.

Native dynamic Recast covers the small yard only. The bounds and two scouts belong to L_CH01_RailYard; the native navigation-data actor is shared infrastructure. AI waits for projection onto a usable NavMesh and for active generation to settle, with a 12s bounded readiness watch and native navigation-generation event recovery. Destruction/unload stops brain/perception/movement, clears timers/delegates and weak targets. DefeatedEnemies and CollectedPickups are small FName sets in the existing GameMode, independent of ECRObjective; restarted actors reconcile those IDs. They are not disk saves.

`ACRAmmoPickup` uses the existing interactable interface and a stable session ID. `ACRCombatAcceptance` is the opt-in focused weapon fixture (`-CRWeaponCheck`); `ACRCombatRoute` is the opt-in actual-input encounter/story route (`-CRCombatCheck`). Neither is placed in a map or spawned normally/in Shipping. The focused fixture intentionally sets zero reserve to test that edge case and applies native damage for the death boundary; the integrated route must obtain combat damage from the actual gun and enemies. Editor NullRHI checks do not establish visual or GPU quality.

`Scripts/generate_combat.py` creates only owned Phase02 assets and makes explicit additions to the existing yard/persistent maps. It never reruns original generation/migration; `audit_combat.py` imports only pure snapshot definitions through AST filtering to compare all155 original actors without executing migration code. `smoke_combat.py` supervises a fresh receipt, ends PIE, then closes Editor. Binary assets are produced and saved by Editor APIs.

Future Blender attachment contract: replace temporary components at RookViewRoot; author viewmodel/arms with consistent centimetre scale, forward +X, aim/sight anchor and muzzle/cue attachment points. Bind shot/cycle/reload presentation to existing weapon events, with AnimBP/Montages/Notifies when a real skeleton exists. Gameplay state retains authoritative timers; visual duration cannot duplicate ammo transfers. Scout hit/death tilts are placeholders, not skeletal animation or ragdolls.

Official references checked for UE5.8: [AI Perception](https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine), [Behavior Trees](https://dev.epicgames.com/documentation/unreal-engine/behavior-trees-in-unreal-engine), [Navigation System](https://dev.epicgames.com/documentation/unreal-engine/navigation-system-in-unreal-engine), [Dynamic navigation](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-how-to-modify-the-navigation-mesh-in-unreal-engine). Current installed headers verified dynamic navigation delegate signatures, Pawn controller level ownership, BT Wait's FValueOrBBKey_Float and native damage APIs.

- GameMode 管当前世界规则；PlayerController 管玩家控制。跨地图保留少量数据可用 GameInstance／有明确职责的 subsystem，不把世界 Actor 或整章资源长久挂在其中。
- 保存稳定 ID 与值，不保存运行中的 Actor 指针。恢复顺序为读取数据→准备区域→等待对象就绪→幂等恢复→交还控制。考虑坏存档、旧版本、失败写入与重复触发。
- 谁发起异步请求，谁负责 handle、取消和失效检查。EndPlay 后旧回调不访问已销毁对象；释放硬引用之后才有机会回收资源。
- 优先 delegates、overlaps、timers；不禁止必要的引擎移动／动画逐帧更新，也不将所有游戏逻辑放 Tick。
- Gameplay Tags 在确有跨系统语义时登记使用，不替代全部枚举／数值，不因此自动引入 GAS。
- Output Log、Editor Details 可见状态、必要的 Insights bookmarks 让程序与关卡人员能定位故障；不建设自定义遥测平台。

存档异步 API 在本机 `GameplayStatics.h` 中已核验签名，尚未实施；异步磁盘写入仍可能有游戏线程序列化成本。动画基线为原生 AnimBP／Montage；Motion Matching、复杂 Control Rig 或整套能力框架须由实际内容证明需要。

## 流送与渲染

第一章明确采用 **persistent level + 原生 Level Streaming 三个概念区**作为规划默认，见 [STREAMING_STRATEGY](STREAMING_STRATEGY.md)。不强制 World Partition，不实现自定义框架。独立章节可用受控 map travel，具体是否无缝由体验／预算决定。

Blank 模板生成的渲染设置是 bootstrap 起点，不是性能已验收的画质承诺。Lumen、Nanite、光追和第一人称身体方案在代表性场景实测后确定；Beta／Experimental 功能不作为默认依赖。8 GB VRAM 要同时计算当前区与预载区，见 [PERFORMANCE_BUDGET](PERFORMANCE_BUDGET.md)。

## 验证与人工边界

Codex 可审计文本、修改 C++、运行 UBT／定向测试、分析日志和 profile、核验 Git 推送。通过可用 Editor UI／脚本可创建真实资产；没有该路径时只提供精确手动步骤，绝不伪造二进制文件。

Unreal Editor 中必须检查资产编译、引用、地图世界设置、碰撞、动画和输入。人工试玩负责手感、叙事清晰度与视听节奏；截图不是全流程通过。Editor／PIE 会受缓存影响，最终流送、soft-reference cook 覆盖、冷启动及内存释放以 packaged Development 游戏验证。

Automation Framework 用于关键确定性规则；Functional Testing 用于真实地图的准备／就绪／恢复顺序，设置超时与清理。零测试不是通过。不为文档变化写镜像测试。一次 baseline、相关验证、里程碑人工验收；同一故障两次修复失败后先诊断。[Automation](https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-test-framework-in-unreal-engine)、[Functional Testing](https://dev.epicgames.com/documentation/en-us/unreal-engine/functional-testing-in-unreal-engine)。

## Phase03 restoration architecture

`ACRGameMode` owns the logical salvage flag, first accepted source ID, applied Survey Optic flag and one-time subtitle flags. These values are independent of ECRObjective. `ACRSalvagePickup` implements the existing camera-trace interface, subscribes to OnRestorationChanged and reconciles on BeginPlay. Both sources hide when either is collected. There is no cross-level actor inventory.

`ACRWorkbench` owns its surface, skeletal presentation component, camera, async soft-asset handle and a native LevelSequenceActor spawned into its own Workshop ULevel. The PlayerController stores only a weak workbench reference. Assets preload in BeginPlay; an unavailable asset cannot capture input. State follows Idle -> Preparing -> Playing -> Finalizing -> Completed, with Aborting -> Idle for genuine cancellation. Native SequencePlayer OnFinished or explicit Tab Skip commits the upgrade once. An unexpected native Stop, death, Restart and EndPlay abort without a reward. UE5.8 broadcasts OnStop before OnFinished on natural completion, so stop resolution and resource destruction defer to the next game tick; only OnFinished/explicit Skip enter Finalizing. This avoids reentrant MovieScene teardown and is not a delay used to infer success. Cleanup removes sequence delegates/timers, destroys the temporary sequence actor, restores balanced move/look input ignores and weapon presentation, and restores movement only if alive. The controller's normal pause menu freezes world/sequence time. A20Hz cue timer samples actual sequence position only while playing; it does not decide successful completion.

The original weapon component gains only a presentation lock and session-resolved ADS FOV. DA_Rook5 is never mutated. Imported meshes use the existing cosmetic root and shot/reload/recoil/cover behavior; absent imported appearance retains the original cube silhouette. Regular weapon presentation is hidden while the bench's skinned weapon is visible. No separate combat actor or AnimBP framework is needed for a single native skeletal-animation Sequencer track. A future multi-action first-person rig may justify AnimBP/Montages, but is outside this milestone.

Source: `ArtSource/Blender/Phase03/CR03_RookRestoration.blend`, created by create_restoration.py and reopened by validate_source.py. Units are numeric centimeters, Blender scene scale0.01, +X gameplay forward/+Z up. FBX uses -Y forward/Z up conversion; actual imported ROOK bounds are79.5cm long. Skeleton: root, weapon, optic, left/right upperarm/forearm/hand plus five three-segment fingers per hand,39authored bones; the actual Unreal import has40 including the FBX armature-object root CR03_RestorationRig. Prop bones rigidly own the coherent exterior models;192vertices blend weights at palm/cuff transitions. The22s/30fps action is editable in Blender and imported as AN_CR03_RookRestoration. Native LS_CR03_RookRestoration binds the Workshop actor with tag CR03_Hands and one skeletal animation track. The benchmark/render review, not the source receipt, determines runtime quality.

`Scripts/generate_restoration.py` uses real Editor import, material, collision, actor placement and sequence APIs. It checks CR.GeneratedBy metadata and CR_Phase03_Generated actor tags, refuses unowned collisions and compares every original164actor snapshot. It adds six actors, not a replacement map. Interchange did not honor legacy FBX auto-collision settings: the script explicitly adds/validates native simple collision for the optic pickup, with a UBoxComponent ending at the actual98cm tabletop for the bench (the rear rail must not seal empty air). Python Rotator uses explicit yaw keywords. Skeletal material usage is explicitly saved. Phase03 is an explicit small cook directory, covering native soft appearance defaults and imported sequence/audio dependencies.

Official UE5.8 references: [FBX skeletal pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine), [FBX animation pipeline](https://dev.epicgames.com/documentation/unreal-engine/fbx-animation-pipeline-in-unreal-engine?lang=en-US), [Sequencer Python](https://dev.epicgames.com/documentation/unreal-engine/python-scripting-in-sequencer-in-unreal-engine?lang=en-US), [Animation Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprints-in-unreal-engine), [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine). Installed headers, source and DLL exports were also checked; SetSequence is supported in the installed5.8.4 binary whereas InitializePlayerWithSequence is declared but not implemented/exported. No engine modification or runtime UnrealEd dependency was added.

## Phase04 checkpoint architecture

`UCRChapterSaveGame` schema1 contains CH01_DeadStation, a stable checkpoint/zone pair, monotonically increasing generation, ECRObjective, health, magazine/reserve, defeated enemy IDs, collected ammo IDs, Survey Optic/source/upgrade flags, claimed story IDs and a CRC of the bounded value payload. Supported IDs are explicitly whitelisted. Unsupported versions, invalid prerequisites, duplicate/unknown IDs, nonfinite/dead/excess health, invalid ammo and checksum mismatches are rejected. There are no serialized world objects or running timer/sequence positions. `CaptureSession` / `RestoreSession` are narrow GameMode interfaces; restoration replaces sets and flags without broadcasting objective progression.

`UCRChapterSaveSubsystem` has GameInstance lifetime. Native AsyncLoadGameFromSlot scans CinderRelay_CH01_A/B; the highest validated generation wins. An unreadable newer slot does not hide the earlier valid slot. Native AsyncSaveGameToSlot serializes on the game thread and writes asynchronously; success is announced only from its actual completion callback. One immutable write and at most one latest coalesced snapshot exist. Run epochs discard queued previous-session requests and prevent stale-world success feedback; an already accepted old-run write may finish normally. No disk save is deleted by New Game, Restart, or a failed read. CP00 writes only if both slots are genuinely missing. Files reside in native ProjectSavedDir/SaveGames (the actual writable location depends on the build/platform); not in Git.

`ACRCheckpoint` owns only an overlap box and facing marker in the persistent map. Entering starts a bounded 0.25s stable-state check; leaving, acceptance, or 10s timeout stops it. The player must be alive, grounded, outside assembly/pause/reload/shot cycle, and at least2s after last damage. Required objective, native region readiness and safe floor/capsule clearance must all pass. Failed writes retain the previous checkpoint and allow leaving/re-entering to retry. Only a newer checkpoint rank can advance within a run. Unsaved progression after a checkpoint intentionally rolls back on recovery; no automatic save at every pickup.

CP00 uses the same bounded check explicitly armed after safe possession: native SpawnActor overlap occurs before Possess and is not sufficient to trigger the initial save. BeginRun clears prior operation feedback, and a late accepted write from an older run reports neutral checkpoint availability rather than CHECKPOINT SAVED in the new world. These two integration fixes have focused regression/packaged evidence in MILESTONES. Conflicting equal-generation snapshots are rejected rather than arbitrarily chosen; unsupported future versions are retained, with no speculative migration.

Cold launch uses the existing UMG menu. New Game and Restart Chapter set a new-session travel intent. Continue and death Retry re-scan disk, then prepare a validated value-only restore intent. Controlled OpenLevel reloads only the persistent map. GameMode InitGame consumes and applies the snapshot before streamed actors BeginPlay. The streaming controller initializes the saved target zone and ignores pawn-based zone movement until the real player is released. Native GetPlayerPawn includes spectator pawns; the controller suppresses temporary spectator creation while bootstrap is held. Only loaded/visible/prerequisite-ready target geometry plus a unique valid checkpoint anchor permits RestartPlayerAtTransform. Health/ammo then restore before gameplay; reload/cycle timers are cleared and weapon state is Ready. GameMode's restored upgrade is consumed by existing soft-loaded appearance/ADS logic.

Existing workbench Stop/OnFinished/Skip ownership and next-tick MovieScene cleanup remain unchanged. No snapshot is accepted during presentation. PlayerController EndPlay aborts presentation and removes persistence delegates; only weak streamable actor references are retained. Existing enemy, ammo, module, salvage and bench BeginPlay reconciliation reads restored GameMode state.

Official references: [native saving/loading](https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine?lang=en-US), [AsyncSaveGameToSlot](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/UGameplayStatics/AsyncSaveGameToSlot), [subsystem lifetimes](https://dev.epicgames.com/documentation/unreal-engine/programming-subsystems-in-unreal-engine). Installed5.8.4 GameplayStatics.h/.cpp and PlayerController source verify actual signatures and spectator behavior. Python5.8 web API pages were unavailable; the installed binding probe exposed no HitResult fields, so a small runtime-class CallInEditor operation uses native collision without UnrealEd dependencies.
# Phase05 presentation integration

- `ACRZonePresentation` is owned by RelayBunker. It asynchronously loads two soft Level Sequences, rebinds the native tagged actor/component tracks, and uses OnFinished or explicit Skip to release the end screen. Deferred MovieScene cleanup carries a generation token so a superseded power sequence cannot finish a later ending. Weak player/controller references, owned input-lock release and EndPlay cancellation bound its lifetime. It never changes objectives, saves, upgrade rewards or chapter IDs.
- `ACRPlayerController` retains all UI/pause/recovery authority. Complete attempts the local ending; unavailable assets fall back to the existing end screen. Movement/fire lock only during the short ending; look input remains available. Esc pauses native playback and Tab skips. Death/Restart/Exit/EndPlay remove presentation ownership. No second UI manager.
- `ACRAshWarden` keeps native CharacterMovement, AI/perception and all existing hit components. An optional skeletal mesh plus Idle/Walk/Alert/Attack/Hit/Death clips provide cosmetic presentation. AI decision cadence selects locomotion; native skeletal evaluation interpolates animation. Attack damage still originates solely in the old controller trace. Primitive visual fallback remains. Current clips use native single-node playback; they do not have an Animation Blueprint blend graph, so clip transitions require human review.
- `ACRInteractionActor::PresentationMesh` adds only a no-collision/non-nav visual child. The original Mesh remains the trace/collision root. Actor-hidden reconciliation automatically hides the new appearance after collecting a power module. No pickup/objective persistence change.
- `UCRWeaponViewComponent` switches to soft Phase05 ROOK/optic meshes, preserves the primitive fallback, adds bounded locomotion bob and reload/close-wall smoothing. Damage/ammo/ADS authority remains `UCRWeaponComponent`; DA_Rook5 balance values are unchanged. Editor asset audio assignments are intentional, never runtime mutation.
- `ACRCharacter` samples displacement within its existing0.1s interaction cadence for grounded footsteps. It rejects teleport-sized displacement and assembly/dead states. Zone-local AmbientSound owns native attenuation/occlusion; no new audio engine or persistent cross-zone references.
- UMG prompt and controls use anchored width/wrapping instead of unbounded auto-size. Combat readout has a larger bottom inset. Actual packaged1080p windowed and2560x1600 fullscreen inspection passed for bottom controls, health/ammo, objectives and menus; the1600p opening subtitle also fit. Evidence and coverage limits are in MILESTONES.

Actual asset roots: `/Game/Generated/Phase05/{Meshes,Animation,Materials,Textures,Audio,Sequences}`. `LS_CR05_RookRestoration` remains660 frames at30fps. `LS_CR05_RelayPower`120 frames and `LS_CR05_RelayEnding`240 frames contain native child PointLight Intensity and bound audio tracks. Original Phase03 sequence/source remain available. Packaging explicitly includes the small original Phase05 directory because native C++ soft appearance defaults must not depend on editor discovery.


Phase05 import conventions: Blender centimeters, +X forward/+Z up, FBX -Y forward/+Z up, no leaf bones. The imported armature adds one root (Warden18->19, restoration39->40). Actual Editor inspection found the cabinet front's authored -Y becomes imported +Y; final Workshop cabinet yaw180 and Bunker rack yaw90 face the walkways. Mesh bounds were compared against exported source dimensions; no global model-scale assumption substitutes for that check. Animated meshes use UV-based shared materials, avoiding world-aligned texture swimming on hands/weapon; environment modules use180cm world-aligned surfaces. All new decoration uses the saved NoCollision profile, not only a transient enabled flag.

The final calibrated hand derivative preserves original prop curves and22s length, adds7cm approach for holding wrists and a4cm forward/-7cm right-hand correction around the optic beat. Contact is improved at inspected3/7/13/18s poses but remains a coarse prototype grasp. Exact editable curves and source changes are in tune_restoration_contact.py/CR05_RookRestoration.blend; they are not claimed as production anatomical animation. The existing native sequence owns completion, pause, Skip and Abort, never a timed reward delay.

## Phase05.1 visual integration

The runtime module, schema1, stable gameplay IDs, damage/ammo balance and streaming architecture remain unchanged. New content is isolated under `/Game/Generated/Phase051`; Phase03/05 meshes/actions/sequences remain rollback assets.

`UCRWeaponViewComponent::SolveSightRoot` computes the imported mesh-root transform from a native `SightAnchor_Iron` or `SightAnchor_Optic` socket and a28cm visual eye relief. Blueprint-configurable hip location remains separate. The selected sight axis matches camera+X; camera-oriented hitscan remains authoritative. ADS retains65/60degree FOV. ADS locomotion bob is suppressed and visual recoil is axial, returning to the authored alignment. Reload/sprint/close-cover lowering remain intentional interruptions of the sight picture. UMG's generic crosshair is hidden during ADS so the actual notch/post or lens-bound reticle supplies the aiming cue.

Native first-person primitives use conservative camera-depth scale0.65 with viewmodel FOV equal to the world FOV. No secondary scope camera, scene capture, rendering plugin, or project renderer switch was added. Missing imported assets/anchors retain the old cube/legacy transform path. Appearance loads are existing asynchronous soft references. First-person scale is a visual clipping aid, not a gameplay collision or damage change.

`CR051_RookRestoration.blend` retains the22s/30fps runtime contract. Editable `IK_Hand_L/R`, `IK_ElbowPole_L/R`, `CONTACT_weapon_*` and `CONTACT_optic_*` controls drive the same named hand/finger/prop bone hierarchy. Copy Transforms influences explicitly acquire/hold/release a prop-relative contact; FBX export evaluates native IK. The FBX convention is centimeters, -Y forward/+Z up; imported UE Y handedness is verified in rendered poses rather than assumed. Joined meshes share UV0 (`SurfaceUV`) to preserve the hero material coordinates. The new action is not an anatomical realism or motion-capture claim.

`import_quality_animation.py` creates separate SK/AnimSequence/LevelSequence assets; `-CR051Activate` changes only the existing workbench's appearance/sequence after review. Its CR03_Hands binding, OnFinished/Skip/Stop/Abort authority, pause, safe next-tick MovieScene cleanup, input/camera restoration and GameMode upgrade commit remain native and unchanged. Render-only preview scripts do not save temporary pose/camera actors.

`place_quality.py` compares all280 original actor snapshots and level ownership before/after additive placement. Decorative components use NoCollision and cannot affect navigation. A small combined distant exterior mesh is persistent to avoid an empty skyline when the Rail Yard unloads; other large additions belong to their corresponding streamable zones. Checkpoint anchors, gates, floor geometry and gameplay actor transforms are unchanged. No new persisted IDs are introduced.

Development-only `CRCombatRoute -CRSightReview` is a disclosed visual fixture: it applies existing upgrade APIs and samples cover positions directly; it is not the gameplay acceptance route. Normal Chapter01 acceptance uses the existing Enhanced Input/interaction route and dedicated CR04_TEST_ save slots. Both route receipts now record actual viewport dimensions, not merely requested command-line resolution. `run_checkpoint_acceptance.ps1 -Fullscreen` prevents Windows DPI window-size clamping for the1080p comparison.
## Phase05.1 final review correction

The imported view is an atomic pair: both meshes and `SightAnchor_Iron` / `SightAnchor_Optic` must exist before it replaces the original primitive fallback. `CanUseAuthoredSights` validates the pair once in `RefreshAppearance`; the cached validity controls native first-person flags, mesh visibility, camera depth scaling and HUD reticle suppression. Missing meshes/sockets retain the primitive view and accurate HUD crosshair. Normal fully loaded ADS remains socket-aligned at65/60degrees; no gameplay weapon logic changes. The native `CinderRelay.Presentation.SightFallback` test covers missing gun, missing optic, missing sockets and the valid pair.

## Phase05.2 presentation and contact

No runtime C++ classes, state IDs, schema, gameplay collision, checkpoint transforms or streaming rules changed. Cosmetic content lives under `/Game/Generated/Phase052`; explicit cook inclusion supplements the bench's soft references. The persistent map only changes local exposure contrast (shadow0.8/highlight0.9); existing EV0..3/bias1 remains. RailYard owns34 added decorations/lights, Workshop owns2 non-shadowed fill lights. The two existing cosmetic railcar actors use the new model; their separate blocking shell is untouched. Thirty-six added actors use the ownership tag `CR_Phase052_Generated`; metadata `CR.GeneratedBy=CinderRelay.Phase052.v1` protects imported asset names. Native authoring scripts refuse unowned name collisions and do not delete user content.

The active workbench now soft-references `Animation/SK_CR052_Restoration` and `Sequences/LS_CR052_RookRestoration`; `AN_CR052_RookRestoration` is22s/30fps with the preserved40-bone imported hierarchy. Phase03/05/051 sources/assets are unchanged. Prop-relative contact targets, animated elbow poles/shoulder offsets, wrist rotations and staggered digit closure bake to the existing skeleton. No new runtime IK or animation framework was introduced.

The native sequence binds the bench through existing `CR03_Hands` and its `AssemblyCamera` child component. One transform track supplies a small head settle/final reveal and explicitly restores state. Two native audio sections supply original seat/secure cues at frames347/400; the existing15s confirmation cue and GameMode upgrade authority remain unchanged. UE5.8 audio sections cache completion intent: `set_completion_mode` alone was not serialized as intended. The importer updates the `eval_options` editor property, invoking native PostEditChangeProperty; a fresh asset load verified all sections RestoreState. No arbitrary timer grants the upgrade.

`validate_contact_tracks.py` evaluated the actual sequence at6s and19.2s: the camera moved, then Stop restored location(-62,0,166) and pitch-48 each time. This proves native component binding/restoration in Editor, not player-input acceptance. Packaged lifecycle evidence is recorded separately in MILESTONES. `validate_presentation_polish.py` compared302 original actors and231 protected hashes, plus native sphere overlaps for valid review cameras. Preview scripts never save camera/pose state.
