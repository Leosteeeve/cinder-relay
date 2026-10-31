# CINDER RELAY — Milestones

按验收门槛推进，不在需求／工作量未明时承诺日期。最终切片为 **Chapter 01 — The Dead Station，12–16 分钟**。Phase 00 不自动授权 Phase 01。

## Phase 01A — 当前批准的实施计划（2026-10-31）

本节以用户的新规格替代下表旧 P01／英文提示的范围：这次允许三个相连灰盒区域、基础交互、四步目标和结束画面；不做战斗、武器装配、AI、存档、流送或最终美术。指定分支 `phase-01a-greybox`，保留 CinderRelay 模块。已检查工作区干净，在同一工作目录切到指定 feature branch，避免重复 Unreal 缓存；不在 main 实施。

**架构：** 一个非 WP 地图；CharacterMovement + Enhanced Input；角色内 10 Hz 短距离 visibility trace 与按键时重新校验；一个 Blueprint interface、一个可配置交互 Actor；GameMode 内单一枚举目标状态；原生 UMG widget 与 PlayerController 管暂停／重新开始。Blueprint 负责角色参数、交互类型和 GameMode 资产配置。Editor Python 仅生成资产，不参与运行时。

**执行与验证：** 按当前用户限制，实施后一次 CinderRelayEditor 编译，实际错误才定向修正；一次连续 gameplay smoke。不追加逐任务全量构建或为制造 red/green 而重复启动引擎；同一问题两次修复失败即停止诊断。后续独立只读代码审查；不自动进入 01B 或打包完整游戏。

- [x] 环境审计：clean main、实际 CinderRelay、5.8.4、无既有 gameplay／map；Python commandlet 成功，所需 asset／actor／level API 可用。
- [x] C++：CRCharacter（动作／trace）、CRInteractable（接口）、CRInteractionActor（module／relay／signal）、CRWorkshopTrigger（到达工坊）、CRGameMode（单目标状态）、CRPlayerController（UI／暂停）、CRHUDWidget（原生 UMG）。Build.cs 仅增加 UMG／Slate 需要的依赖。
- [x] 编辑器生成：`CinderRelay/Scripts/generate_greybox.py`，专属 `/Game/Generated/Phase01A` 路径；带所有权标记的材质、Input Actions／Context、Blueprint defaults 与 L_CH01_Greybox。重跑复用稳定名称；不删除非本脚本对象，冲突时拒绝覆盖。保留生成 receipt。
- [x] 自动验证：两次相关编译成功；真实地图保存；Enhanced Input 驱动碰撞／坡道／暂停与四目标流程，早用／越距／重复交互拒绝，结束及重开通过。人工键鼠、额外遮挡布置／低顶站起边界和主观手感仍待验收，详见实际记录。
- [x] 更新现有 README／技术／流送／资产／验证与决策文档；审查代码、暂存内容和 25 个 LFS 资产。交付分支为 `phase-01a-greybox`，提交／推送结果以最终报告及 Git 远端 SHA 核对为准。

工程默认（可在 Blueprint 调整）：walk 300 cm/s、sprint 500、crouch 160；capsule 半高 96／蹲姿 60 cm，交互距离 250 cm；镜头无 head bob。WASD／鼠标、Shift 按住跑、Ctrl 按住蹲、Space 跳、E 交互、Esc 暂停与释放鼠标。四个目标文本遵循用户原文，结束为 MERIDIAN NETWORK / CONNECTION RESTORED。

实现时关注：暂停释放按键不留 sprint 状态；低顶阻止站起；trace 遮挡；module 重复领取；生成器重跑保留用户添加内容。02 阶段以后不由这次授权启动。

| 阶段 | 交付物 | 依赖 | 接受标准 | 验证方式 | 非目标 |
| --- | --- | --- | --- | --- | --- |
| P00 已完成 | 原生 Blank C++ 工程、Git/LFS、GitHub、八份核心文档、审计记录 | 已安装 UE 5.8、GitHub 可用授权 | 真正 `.uproject`／模块；基线编译证据；main 与远端 SHA 一致；无秘密／生成缓存入库 | 文件／配置检查、一次 baseline 与实际配置变更所需的定向编译、staged diff、远端查询 | 不实现玩法或第一章地图 |
| P01A 当前 | 三连通灰盒、第一人称控制、交互／四目标、UMG、真实生成资产 | P00；本轮用户批准规格 | 见本节合同与实际验证记录，不用编译代替玩法验收 | 一次初始编译、实际发现的定向修正、一次有界地图流程 | 无战斗、AI、装配、存档、streaming、最终美术 |
| P01B 待批准 | 按既定边界拆分原生 Level Streaming、预载／卸载与 packaged 验证 | P01A 人工接受、回访规则、代表性资源预算 | 初入／返回／反复触发不穿地或重复叙事；cook 引用完整；测量重叠峰值 | 定向编译／Functional 检查、一次短人工转换、规定内存采样 | 无 WP、自制框架、combat 或章节扩展 |
| P02 完整战斗遭遇 | 一个主要武器、一种敌人行为、命中／死亡／重试及基本动画音频 | P01；确认敌人／武器／伤害规则、合规资产 | 单次 3–5 分钟遭遇可完成和失败重试；射击、换弹等批准动作反馈一致；无状态卡死 | 定向规则测试、一次短人工遭遇验收、代表性 combat trace | 无多人、武器海、复杂技能树／潜行体系 |
| P03 回收、修复与叙事 | 少量回收点、一条武器恢复／装配流程、一次可读叙事、一项环境交互 | P02；明确修复步骤／动画资源及本章目标 | 缺材料／完成／取消状态正确；动画结束恢复控制；同一事件不重复发奖；字幕可读 | 针对状态的检查、一次短人工完整流程 | 无完整背包经济、任意零件物理拼装、完整科技树 |
| P04 checkpoint 与整合 | 复用 P01B 流送，增加 SaveGame 恢复与跨区状态整合 | P03、P01B；回访规则、资产预算 | packaged 三分区连通；首次／回头／恢复／失败注入可靠；重叠峰值达批准预算 | 一次相关编译、定向 Functional Tests、一次短人工转换、规定的 3 往返内存采样 | 无 WP 迁移、自制 streaming 框架、多章节扩展 |
| P05 精修垂直切片 | 12–16 分钟可玩开始与结尾、叙事／战斗／维修一致性、基本设置／credits、可复现 benchmark | P04；确认节拍和资产权利；所有关键阻断关闭 | 一次完整人工流程通过；checkpoint 重开可恢复；关键音画缺陷关闭；预算测量及来源清单可追溯 | 定向回归、打包验证、一次完整人工验收、固定路线 3 轮性能记录 | 不扩张游戏规模或以加功能替代打磨 |

## Phase 01A 实际验证记录 — 2026-10-31

实现及自动流程通过；人工体验接受仍待用户试玩。不是 12–16 分钟垂直切片完成，也不是 packaged 或性能验收。

| 检查 | 实际结果与本地证据 |
| --- | --- |
| 环境 | `D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject`；保留 CinderRelay 模块；clean main `4abe9c5a0a0c187832314eb06802ff0066f90438` 起分支 `phase-01a-greybox`；UE 5.8.4 CL 58902052 |
| 初始实现编译 | CinderRelayEditor / Win64 / Development；UBT exit 0，Succeeded，87.44 s；`.environment-local/phase-01a/build-01.log` |
| 定向修正编译 | 审查发现输入 context 需要覆盖 possession 生命周期；增加 PawnClientRestart；exit 0，Succeeded，20.95 s；`build-02-input-lifecycle.log`。两次均 MSVC 14.50.35739，UBT 选择 SDK 10.0.22621.0；没有引擎全量编译 |
| Editor 资产生成 | 真实 `.umap` + 24 `.uasset`：8 材质、10 actions、1 context、5 Blueprints。155 个稳定命名 Actor、10 个 mappings、非 WP。首次成功及专门幂等重跑的 commandlet 均 exit 0；之后修正旋转并由当前 Editor 保存，仍为 155，`new_assets=[]` |
| 运行验收 | 最终 rendering PIE smoke **PASS / 11 checks**，66.41 s（含约 20 s 结束截图停留，不是体验时长或性能数字）；`Saved/Phase01A/smoke.json` 与 `.environment-local/phase-01a/gameplay-smoke_2.log` 的 `CR_SMOKE_PASS` |
| 实际可玩闭环 | 原生 CharacterMovement 从 yard 走到 workshop，E 取 module，走坡道下降约 600 cm，E 激活 relay／signal，目标按序 0→1→2→3→4，结束暂停菜单，Restart 后重新可移动。没有 teleport 或直接设置目标状态 |
| 输入／防护 | action yaw、蹲下 capsule 60 cm／站回 96 cm、跳跃上升 81.6 cm、暂停不移动／释放鼠标／清除 sprint、后墙阻挡、过早／越距与重复交互拒绝。通过注入 Enhanced Input，非物理键盘全键位验收 |
| 画面 | 实际查看 yard／workshop／bunker 原生截图与 Editor HUD；`.environment-local/phase-01a/ending-ui.png` 确认 MERIDIAN NETWORK / CONNECTION RESTORED 和 Restart／Exit 按钮；`yard-ui.png` 确认重开后的目标。截图不替代连续人工验收 |

最终地图 SHA256：`C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733`。PASS receipt SHA256：`E9BDD6AF687E49992DB2C09A09A580203B52592A4D14B24D338776255073703C`。原始日志、receipt 和截图保留本地并被 Git 忽略；本表为入库摘要。

Git 交付：实现提交 `37326ff1ab96d30559f7a942c6fe62571ca3dd5c` 已推送 `origin/phase-01a-greybox`，25/25 LFS 对象上传成功，远端 SHA 与本地一致。最终 `gh repo view` 显示仓库为 **PUBLIC**，与 Phase 00 历史记录不同；本轮未更改可见性或其他设置，只补充文档纠正当前状态。最终文档补充提交以该分支 HEAD 为准，main 未合并。

实际调试记录（不是声称所有步骤一次通过）：

- Editor Python 的 Key 初始化、DirectionalLight 组件访问与 internal-only subsystem getter 不同于假设；按本机反射／源码修正具体 API。初次中断创建的空 map 按已记录 hash 和空内容恢复 ownership，此后立即保存 ownership checkpoint。
- 后台首帧晚于动作处理，造成测试的蹲姿计时误判；改成游戏时间加最少帧数。临时关闭后台 throttle 并在 finish 恢复，不保存全局配置。
- 第一次走动流程超时后读取真实 `Rotator(1,2,3)` 得到 pitch=2／yaw=3／roll=1，确认 Python 位置参数顺序问题；生成器和导航改为命名轴，修正坡道与标牌。原生截图会泵 Slate，增加测试回调重入保护。随后上述完整流程通过。
- 同工程的重复测试 Editor 导致资产保存 Error 32；确认命令行后正常关闭本轮多余实例，保存成功。不要在同工程多个 Editor 中同时生成资产。
- 没有通过反复全量构建、清缓存或架构改写处理这些问题。修正后的有界流程通过后停止测试。

已知限制与一次人工接受清单：

- 工坊入口偏亮，标牌、曝光及移动手感尚需人工调整验收；仅灰盒功能美术，没有动画、音效、战斗、存档或最终叙事演出。
- 普通 PIE 的物理 Esc 会被 Editor StopPlaySession 截获，已实际观察；在 Standalone Game 中确认 Esc 暂停／恢复、鼠标、WASD／Shift／Ctrl／Space／E 和按钮点击。自动测试调用暂停／重开处理器，不能代替这些物理输入检查。
- 按 README 路线做一次短完整试玩，再检查贴墙镜头、低顶站起、遮挡／回访和路线可读性。尚未对每个灰盒碰撞面或所有分辨率进行人工验收。
- Phase 00 已有的 13 条 UnifiedError 附近 `LogAutomationTest: Error: Condition failed` 仍出现在 Editor 启动；未修改引擎，也未声称 clean log。这不等于本项目 smoke 失败，但仍是独立未解决的引擎诊断。
- 未 cook/package，未测 FPS／VRAM／冷加载，当前 shader／PSO 编译日志不能作为稳态性能报告。Phase 01B 前先人工接受，再做原生 Level Streaming 与 packaged 验证。

## Phase 01A 试玩修正：鼠标纵轴（2026-10-31）

用户在 Standalone 试玩发现上下视角反转。根因是 `FSceneViewport::OnMouseMove` 已通过 `MouseDelta.Y -= CursorDelta.Y` 转换屏幕坐标，而 `ACRCharacter::LookPitch` 又取反；当前配置关闭 legacy input scales，生成的 MouseY mapping 没有反向 modifier。仅去掉角色代码中的多余负号，保留灵敏度、水平输入、地图和二进制资产。

在既有 smoke 中补充真实 camera forward Z 的正／负方向检查，`-CRLookOnly` 运行 30 秒以内的专用检查并退出其自身 Editor，支持 NullRHI；不重跑完整路线。

- 修复前，原 DLL 在 `pitch_up` 正确复现失败：camera forward Z = **-0.125333**。
- 修改后一次 CinderRelayEditor 定向编译 **Succeeded / exit 0 / 15.74 s / 4 actions**，记录在 `.environment-local/pitch-fix/build.log`。
- 同一检查 **PASS**：向上 Z = **+0.125333**、向下 Z = **-0.125333**，正 MouseX yaw 增量 **+7.56°**；5 项记录（3 项方向检查，另有初始化和既有无效交互检查），动作阶段 1.31 s，不含 Editor 启动。
- 证据：`.environment-local/pitch-fix/look-before.json`、`look-after.json` 和对应 logs；当前 receipt 为 `CinderRelay/Saved/Phase01A/look-smoke.json`。测试结果以 receipt 的 passed 字段为准，不能仅以 Editor 退出码判断。
- 这是无渲染的 Enhanced Input／相机方向验证，未替用户再次操作物理鼠标或重新进行完整手感验收。现有完整路线证据保持为上文先前 revision 的结果。

## 单任务合同

每个 Codex task 必须列出：目标、允许文件／系统、依赖、交付物、可测接受条件、具体验证、非目标、停止条件。阶段过大则切成仍可运行的子任务，避免一次生成所有类。

C++ 修改后运行相关 target 编译；数据／Blueprint 变化运行对应资源检查。规则测试只覆盖真实风险，地图恢复用 Functional Testing。没有相应测试就诚实说明，不运行不存在的测试前缀后报告通过。

每个里程碑一次短人工玩法验收，P05 为完整 12–16 分钟。定义性能 checkpoint：P01 灰盒、P02 战斗、P04 转换内存、P05 最终包；遵守 [性能协议](PERFORMANCE_BUDGET.md)，不是每次编辑都测全程。

## 调试次数规则

复现→根据日志／trace定位→最小修改→相关测试→记录结果。同一故障两次修复均失败：停止编辑，提供根因证据、已排除项和下一项诊断；不要反复重建、清 DDC、安装插件或改架构猜测。通过相关检查后停止扩大测试，除非新证据要求。

## Phase 01B 执行合同（2026-10-31）

用户已接受 Phase 01A，并明确授权 Phase 01B。基线为已合并的 main `96524c9`，工作分支 `phase-01b-streaming`。

1. **迁移与安全门**：保存原图不变，以 Editor 复制世界、原生 MoveActorsToLevel 迁移 155 个 Actor；每个 Actor 的类别、世界变换、组件、碰撞、材质与交互配置必须相等。共享 Actor、PlayerStart、必要入口遮挡留 persistent。产出 4 个真实地图，无 WP、无 streaming volumes。
2. **运行时流送与状态**：一个控制器使用 ULevelStreaming 的原生 desired flags、加载/显示委托和低频超时看守；门只在双方真实就绪时开放。初始 A 就绪前不生成角色；GameMode 仍是唯一目标状态，流送 Actor 从目标进度恢复已使用状态。返回与重试是接受条件。
3. **有界验证**：实现前确认原基线没有四地图/流送控制器；完成后一次 Editor target 编译、实际 Editor 功能检查、一次 Windows Development BuildCookRun。Development 专用验收路线通过原生移动/交互，先回访三轮，再结束及 Restart；包含就绪抑制和恢复。记录真实结果，不能用文件存在代替可玩性。
4. **交付**：复核整分支，修复有证据的重要问题；更新现有文档，显式暂存相关资产/代码，提交、推送并创建 PR，不合并。

依赖：现有输入/角色/GM/HUD、可用 Editor Python、UE 5.8.4 和 VS 工具链。迁移只依赖已有资产和新类；运行时 readiness 验证必须与迁移后的区域归属一致；验收器只通过公开游戏行为驱动，不直接改变章节状态。

验证预算以用户本次指令为准：不为逐类 TDD 重复编译完整 Unreal target；同一故障两次修复失败后停止并诊断。非目标：战斗、AI、最终美术、磁盘存档、自制异步资源框架、模块重命名、性能重写。

## Phase01B 当时的任务边界（历史记录）

Phase01B 交付时 Phase02 尚未授权；本页后面的 Phase02 contract 记录了后续明确授权。不得将本章转换为 World Partition，也不得在尚未验证 packaged 加载时声称无缝。

## Phase 01B 实际交付与验证 — 2026-10-31

**状态：原生流送与 packaged 功能验收通过；60 FPS 性能目标未通过，人工门口/手感接受仍待用户。** 没有进入 Phase 02。

| 检查 | 结果与证据 |
| --- | --- |
| Git 基线 | Phase01A PR #1 已合并，main 快进至 `96524c9`；分支 `phase-01b-streaming`。切换时旧 Editor 锁住资产，正常关闭后逐一核对25个LFS对象哈希，把本地旧副本保存在 ignored backup，再 fast-forward；没有 reset、删除用户文件或 force-push |
| 首次 C++ 编译 | CinderRelayEditor/Win64/Development **Succeeded / exit0 / 53.04s**；`build-editor.log`。随后仅定向修正 BeginPlay 初始化顺序/当前API（22.58s），工坊事件绑定（见下），PIE退出（8.45s）；没有全引擎重建 |
| 原生迁移 | `migration-editor.log` 的 `CR_MIGRATION_PASS`；四张地图保存成功；155个原Actor：persistent15/A86/B22/C32，另外3个persistentActor。`Saved/Phase01B/migration-comparison.json` differences=[]，真实类别/世界和组件变换/碰撞/材质/交互设置相等；原图SHA未变 |
| 重开资产 | 新Editor进程 `CR_ASSET_REOPEN_PASS`，155原Actor归属正确；不是只检查磁盘文件名 |
| Editor 功能 | `editor-acceptance-entryfix.log`：3轮分别62.655/98.152/133.627s完成，模块/终端恢复、目标0→1→2→3→4、结尾和Restart PASS。完整receipt保存在 `editor-accepted/acceptance.json`；NullRHI不证明画面/性能 |
| Editor 退出修复 | 完整路线原先在活跃PIE直接退出触发Slate清理异常；现在由Python监督本轮新receipt，先停止PIE再关闭Editor。只重测退出路径，`editor-exit-check.log` **exit0**；该短检查明确不是玩法验收 |
| Windows 包 | 唯一 BuildCookRun **BUILD SUCCESSFUL / exit0 / 258.73s**；`package.log`。CinderRelay game target编译、cook、pak/IoStore、stage/archive均完成；Cook ReferencedSet明确列出四图 |
| Packaged 初始加载 | 真正的 `package/Windows/CinderRelay/Binaries/Win64/CinderRelay.exe`，PID35188；默认进入 `L_CH01_Persistent`；A Ready之前没有生成玩家，不在空世界落下 |
| Packaged 流程 | 一次完整路线PASS，151.286s记录、6476行；3次 C→B→A→B→C，回访前完成模块/relay，最终signal最后执行。旧模块不重现、终端不重复推进、Workshop entry不重复触发。Restart恢复0目标、初始区和UI；同一pawn在正常跨区中保持 |
| 门/失败 | 目标已loaded/visible但测试veto阻止Ready时，角色向门行走仍被真实碰撞挡住；反向离开取消需求并卸载；注入controller Failed后门关闭，公开R处理器Retry恢复。没有制造磁盘/缺cook包的实际I/O故障 |
| packaged退出/画面 | 真实游戏日志 `RequestExitWithStatus(0,0)`、正常LogExit，无fatal；启动器exit0没有被单独拿来证明成功。已查看原生1920×1080 ending.png，MERIDIAN NETWORK/CONNECTION RESTORED及两个按钮存在；没有声称人工检查全部转换遮挡或物理键鼠 |
| 内存与性能 | 三轮frame p95 71.453ms、GT15.529ms、GPU15.704ms；commit峰值4.68GiB、同C点首末+138.79MiB；真实卸载A4/B8/C3。完整条件、trace分析、预算差距和限制见 PERFORMANCE_BUDGET |

真实文件：`/Game/Generated/Phase01B/Maps/L_CH01_Persistent`、`L_CH01_RailYard`、`L_CH01_Workshop`、`L_CH01_RelayBunker`。原图 `/Game/Generated/Phase01A/Maps/L_CH01_Greybox` SHA256仍为 `C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733`。

本次打包输入清单（Source/Config/Content/uproject）保存于 `validated-inputs.json`，SHA256 `E9939D7F4733DE06158399EF6D4057AE89D55F04423E10E2CB163F47564AC47E`；实际game exe SHA256 `E1C74DDE2C0ABAB85217452DEF087C3F921FF4B8D14838BC3382449BD7F61A42`；packaged PASS receipt SHA256 `49CA82D0BC95532855FACA4592A6CC12E809B29264B4CC9849085A7FAF02C5E5`。文档/统计脚本后续修改不改变该编译包。

代表性真实日志（省略日志系统的时间前缀；完整 timeline 在 packaged-summary.json）：

```text
CR_STREAM StartupPlayerHeld
CR_ACCEPT 2.827 cycle=0 PASS Initial A floor ready before spawn
CR_STREAM C LoadRequested t=19.781 request=1 state=0 loaded=0 visible=0 wanted=1 player=B witness_valid=0
CR_STREAM C Ready t=20.121 request=1 state=3 loaded=1 visible=1 wanted=1 player=B witness_valid=1
CR_STREAM B Unloaded t=25.273 request=5 state=0 loaded=0 visible=0 wanted=0 player=C witness_valid=1
CR_INTERACTION Reconciled kind=0 objective=3
CR_ACCEPT 140.842 cycle=3 PASS Completed one C-B-A-B-C cycle
CR_ACCEPT_FINISH {"passed":true,"restart_verified":true,"message":"Restart verified after three backtracking cycles and ending","stage":"startup","map":"L_CH01_Persistent"}
```

以上均来自本次 packaged 日志，不是预设示例事件。

实际修复记录与限制：

- Python预检发现 overlap getter未导出，改用反射属性；颜色repr含内存地址，改比RGBA值。复制World的Python强引用曾阻止LoadLevel GC，释放wrapper后继续。commandlet MoveActorsToLevel返回0，改完整Editor后实际迁移全部成功。首次迁移保存/receipt成功后Python关闭阶段发生异常，随后新进程重开和真实packaged运行证明资产可用；不宣称首次迁移进程exit0。
- 最初Editor路线在module阶段失败；诊断证明角色在X1772/1889与entry重叠、Pawn响应为Overlap，但目标仍0。迁移后sparse delegate丢失constructor绑定；BeginPlay日志previous_binding=0确认，改每次BeginPlay AddUniqueDynamic、EndPlay解绑后通过完整路线。诊断日志曾误用普通delegate GetAllObjects导致一次编译失败（8.20s）；按sparse API改IsBound后定向编译通过（5.82s）。没有同一错误两次失败后继续猜测。
- 一次独立只读审查未发现生产流送架构Critical问题；Important退出路径已用短检查修复验证；旧receipt误读风险由本轮mtime监督消除。没有再派二次review，也没有以review代替运行证据。
- 审查未覆盖真实I/O坏包恢复、任意运行时删除地板/交互Actor。前者明确未注入；后者本阶段没有这样的玩法路径，未来加入破坏内容时须重新定义Ready失效。final-art、全部碰撞面、手感与自然遮挡仍需人工接受。
- 60FPS目标未通过；trace指出渲染/同步等待值得进一步定位，不能归因为“C++慢”或用重写/降画质解决。先处理有界性能对照与用户短试玩，再决定Phase02单次战斗遭遇；不会自动开始。

所有原始日志、trace、包和备份位于ignored `.environment-local/phase-01b/`；入库的是此可追溯摘要、源码、四图和现有文档更新。

## Phase 02 First Contact — implementation contract (2026-10-31)

Approved specification: owner's attached “CINDER RELAY — PHASE 02”, all sections 0–21. Baseline verified: PR #2 merged at `0da035de78f642e12f4a71aef3a6442e9276eac0`. Clean main fast-forwarded; branch `phase-02-first-contact`, same local project. This section is the plan and execution ledger; raw evidence remains under `.environment-local/phase-02/`.

Goal: one playable, bypassable Rail Yard encounter, with ROOK-5 gunplay and two Ash Warden scouts, preserving the original chapter and native streaming.

Architecture: small health and weapon components; gameplay timers/damage separated from cosmetic viewmodel motion/audio. Existing Character/Controller/UMG receive input and event-driven feedback. One humanoid enemy class and AIController use native Perception/Navigation; inspect actual Editor bindings for authored Behavior Tree/Blackboard assets. Dynamic Recast is confined to the small yard; enemies wait for local navigation and unload with their zone. GameMode stores defeated enemy and collected pickup IDs separately from ECRObjective.

Ruling: implement in the specified existing checkout/feature branch, without an extra worktree or another design approval — the owner explicitly requests implementation on this baseline. Follow the owner's bounded checkpoint validation instead of repeated per-class full Unreal RED/GREEN builds. Existing material primitives and original synthesized prototype audio avoid new licensing/download dependencies. R becomes Reload; streaming Retry moves to F5.

- [x] Preflight: verify real assets/Editor APIs and original map hash; reuse the unchanged Phase01B executable once at 1080p/Epic/100%, without allocation tracing. Record frame/GT/RT/GPU and load observations before rendering additions.
- [x] 02A: implement `UCRHealthComponent`, `UCRWeaponData`, `UCRWeaponComponent`, `UCRWeaponViewComponent`; integrate Character, Controller and HUD. Editor creates 3 input actions, IMC_Combat, one tuning asset, prototype audio/materials and configured player Blueprint. Acceptance: one shot/one ammo/one damage, cooldown spam rejection, cover blocking, partial/empty/zero-reserve reload, pause/death/restart cancellation, reversible ADS/recoil. Compile Editor once at the checkpoint and run focused native checks; integrate the coherent foundation. No AI or multiple weapons in this checkpoint.
- [x] 02B: one `ACRAshWarden`, `ACRAshWardenController`, minimal inspectable BT/Blackboard if supported, session defeated-ID record. Perception drives visible target/last-known location; native moves have bounded retries, and expired target memory stops pursuit/attacks. Acceptance: sight gain/loss behind geometry, no through-wall damage, actual nav path around cover, bounded failure recovery, dead/unloaded actors stop behavior. No EQS/GAS/custom nav framework.
- [x] 02C: Editor adds exactly two yard scouts, one ammo pickup and small navigation bounds; preserve all original actor transforms/components and map registrations. Add bounded opt-in combat acceptance and performance recording, then one integrated Editor route and one Windows Development package. Verify actual combat damage, death/restart, bypass, old objective flow, unloading/revisit dead-state persistence, final signal, reset and cooked assets. No final art, skeletal-animation claims, weapon assembly or Phase03.
- Delivery procedure: one fresh whole-branch review before final packaging where practical; evidence-supported corrections only; review explicit diff/staging, commit coherent tasks, push feature and create PR to main without merging. Document exact settings, known failures, manual acceptance limits and next task.

Shared interfaces: weapon uses native ApplyPointDamage -> health OnTakeAnyDamage; health OnHealthChanged/OnDeath drives both UI and AI cleanup. Weapon presentation subscribes to accepted-shot/reload/hit events, never determines ammo. GameMode session IDs survive zone unload but reset on Restart. AI consumes health and stable IDs; encounter assets consume these classes. Story objective code remains independent of kills.

Review focus: pause/death while reload timer is pending; R reload versus streaming retry conflict; perception stale targets after unload/death; NavMesh unavailable during streamed startup; level unload/reload while defeated IDs are recorded. Targeted tests belong to 02A/02B and one integrated route, not repeated full chapter tests after tuning.

Preflight complete: existing Phase01B game executable SHA matched the accepted package; one same-settings run passed three cycles and Restart. Only frame/bookmark trace channels; no allocation/CPU/GPU scope tracing. Three-cycle p95 frame/GT/RT/GPU = 14.998/2.5315/14.9679/13.512 ms; no >50 ms frame in the cycle segment. Startup/early maximum RT 374.200 ms remains. Settings unchanged (1080p,100%,Epic,RT/Lumen). The read-only NullRHI Editor audit briefly overlapped this run, so it is a bounded diagnostic rather than a controlled final benchmark. Heavy-run persistent RT hitch did not reproduce; no architecture rewrite justified.

Editor baseline verified 155 original actors and absence of weapon/health/enemy classes before implementation. Native BT root editing is supported; CubeBuilder is not exported, so navigation will use the Editor's native volume actor factory and verify real bounds. 02A initial compile failed only on two `auto*` deductions from TObjectPtr; `.Get()` correction passed in 7.74s. Actual gunplay assets generated and saved, Editor exit0. First focused weapon check passed damage/ammo/cooldown but exposed same-tick camera rotation in the test harness; log showed the old direction hit the target. Split aim and fire into separate stages. Ruling: fold that focused correction into the pending 02B compile, not an extra full build. No gameplay aim rewrite was made for a test timing issue.

02A focused check now PASS (`weapon-check-fixed.log`, saved receipt under `weapon-check-evidence`): single damage/ammo, cooldown spam, miss, real collision cover, partial/empty/full/zero-reserve reload, no duplicate transfer, sprint, paused reload, ADS reversal, death cancellation and Restart reset. The original failed receipt remains in the prior log; Editor exit0 alone was not treated as a pass.

02B compile corrected three reported API/type issues once (static lambda capture, inherited Pawn name shadow, native navigation dynamic-delegate pointer signature), then passed in22.17s. 02C route compiled in27.93s. Editor key-type aliases required `load_class` by the verified reflection path; this fixed asset creation. Native NavBounds registration queues until the navigation tick, so generation now observes real Recast data with a30s bound rather than asserting synchronously. Actual asset generation then PASS/exit0; fresh Editor audit found zero property differences for all155 originals, two distinct scout IDs in RailYard, unchanged original map hash and unchanged streaming registrations.

First integrated route proved nav readiness, real path around train cover and visible-player perception but timed out waiting for enemy damage. Engine BaseEngine.ini proves Pawn defaults ignore Visibility, so enemy hitscan could not hit the player body. Corrected the Character capsule response to Block; no damage bypass or test health manipulation was used. Also corrected double counting of one failed MoveTo request when the native completion callback fires synchronously. These are evidence-supported functional fixes, not tuning to hide failures.

Collision repair then passed actual enemy damage, real train occlusion, finite memory expiry and recovery movement. The harness subsequently stopped at(-1154,-997,98): its diagonal return waypoint crossed the train. Replaced it with the reverse flank waypoints; no teleport or geometry modification. Independent read-only whole-branch review found no new Critical/Important production defect, identified this known acceptance blocker, and flagged miss feedback as Minor. Ruling: promote false impact feedback to a correctness fix because the approved combat-feedback contract requires distinguishing a surface hit from empty space; OnShot now carries native bBlockingHit and cosmetics suppress miss impacts. This is the one review fix pass, no re-review. Remaining unjudged areas are packaged/integrated outcomes and manual feel, which must be evidenced separately; arbitrary destruction of nav/floors and live tuning changes remain outside current gameplay.

### Phase02 actual acceptance — 2026-10-31

**Engineering functionality PASS in Editor and a real Windows Development package. Human gunfeel/audio acceptance and clean 60FPS performance acceptance remain open.** This supersedes the pending items in the execution ledger above; it does not turn placeholders into final art.

| Check | Actual result / local evidence under `.environment-local/phase-02/` |
| --- | --- |
| Final Editor target | `build-route-feedback.log`: Succeeded,63.93s,exit0. Earlier checkpoint failures and focused repairs are retained above. No engine rebuild. |
| Real asset preservation | `asset-audit.json`: passed=true,preserved_originals=155,differences=[]; fresh Editor load, not a filename-only check. Original Phase01A SHA unchanged. Only Persistent/RailYard maps modified; Workshop/RelayBunker bytes unchanged. |
| Editor integrated route | `editor-combat-routefix.log`, `editor-combat-pass/acceptance.json`: passed=true,scenario2; real damage, death/restart, two enemy kills, ammo, original objectives and return traversal. NullRHI; no visual/GPU claim. |
| One final packaging pass | `package.log`: BuildCookRun261.30s, BUILD SUCCESSFUL, AutomationTool ExitCode=0. Game target compile108.54s; cook reports0errors/0warnings. ReferencedSet includes all four maps and all20 Phase02 assets. |
| Actual packaged gameplay | `packaged-combat.log` and `package/Windows/CinderRelay/Saved/Phase02/acceptance.json`: passed=true,scenario2. Route completion98.206s; frame-recorded window97.547s/5876rows. Enhanced Input moves/fires/reloads/interacts; no teleport, synthetic combat damage or direct objective progress. |
| AI / damage | Actual enemy fire damages and kills player. Real train geometry blocks sight/damage; memory expires. Native unreachable MoveTo fails, then AI actually moves after legitimate perception. Four accepted player shots defeat two scouts; real reload and player damage verified. |
| State / streaming | A unloads after leaving yard; return A reconciles both defeated IDs and consumed ammo. B/C genuinely unload on return. Old module stays collected, relay progression remains3, final signal completes4; Restart restores health100,ammo5+25,two scouts,empty defeated set. Same player persists through normal transitions. |
| Discrete visual evidence | Actually viewed1920x1080 `combat.png`, `combat-after.png`, `defeat.png`, `ending.png`: visible greybox weapon/enemy, hit/ammo/health feedback, defeat and ending menus. Not continuous manual input/audio/animation acceptance. |
| Exit evidence / limitation | Game logs `RequestExitWithStatus(0,0)`, normal subsystem teardown and `LogExit: Exiting`, no Fatal/Error/Ensure. The bootstrap process returned777003 to PowerShell; its source is absent from the installed SDK and the code remains unexplained. Do not claim an OS process exit0 for this run. The fresh gameplay receipt and normal game log support functional PASS independently. |
| Offline profiling | `combat-summary.json`, `insights-*.csv`, `combat.utrace`; Insights exit0. Conditions, actual deficits and analyzer warnings are in PERFORMANCE_BUDGET. No repeated playtest/package to improve numbers. |

Map inventory after creation: Persistent19 / RailYard91 / Workshop22 / RelayBunker32, total164 named level actors (155 originals + three Phase01B shared actors + five new yard actors + native Recast). New20 assets: six original synthesized SoundWaves, four materials, three Blueprints, three Input Actions plus context, one weapon DataAsset, BT and Blackboard. No downloaded raw packs, fabricated skeletons or new map hierarchy.

Reproducibility hashes:
- validated98 Source/Config/Content/uproject inputs: manifest SHA256 `5F525C76D03EAC31BF57E36F11D4485FC284DEB86A1941DF686964DEF7571036`; rechecked after packaging,0changed.
- actual game executable: `EB6F3111B25CD1605DDD54BBFDB816ABBFF02B5C5FEA16EBB855D88445FD2A9E`.
- packaged acceptance receipt: `DF1143AEE1E1EAFC2CA34561D3E82E139BF723CF2E3E4ED01AD67DD752D8EEF2`.

Representative actual packaged events (world time resets on Restart):

```text
CR02_ROUTE PASS Native perception acquired visible player; enemy inflicted real damage
CR02_ROUTE PASS Real train geometry blocks sight and enemy damage
CR02_ROUTE PASS Lost-target memory expires; no omniscient pursuit
CR02_ROUTE PASS Two scouts defeated by accepted player shots; player also received damage
CR_STREAM A Unloaded t=18.945 request=2 state=0 loaded=0 visible=0 wanted=0 player=B witness_valid=1
CR_ENEMY ReconciledDefeated id=CR02_Scout_1
CR_ENEMY ReconciledDefeated id=CR02_Scout_2
CR_STREAM A Ready t=36.201 request=3 state=3 loaded=1 visible=1 wanted=1 player=B witness_valid=1
CR02_FINISH {"passed":true,"mode":"combat","scenario":2,"message":"Real combat, native AI/nav, death/restart and streamed chapter route passed"}
```

Remaining limits: prototype primitive humanoids and weapon transforms, no skeletal animation; synthesized temporary audio, not human-listened acceptance. HUD/readability checked in still frames; physical mouse feel, ADS obstruction, close-wall transitions and full bypass-to-ending route need one short user playtest (retreat/flank and unrestricted objective code are verified; the packaged route chose combat). No observed functional blocker in the completed route. Restart/exit logs have native CrowdManager/Recast teardown warnings; intentional navigation failure emits a warning and VSync command priority warnings keep0. These are recorded, not called a clean runtime log. The unexplained bootstrap exit code and instrumented frame spikes remain follow-up items, not reasons for an unrelated architecture rewrite.

Next proposed task: short manual acceptance of aim/recoil/reload/audio, cover and retreat/bypass, then bounded tuning only for observed problems. A separately authorized clean performance sample should disable screenshots and detailed scope tracing to isolate their overhead, at the same quality. Do not start Phase03, weapon assembly, more weapons, final art or checkpoint work automatically.

### Packaged desktop DPI correction — owner playtest follow-up

The owner reported clipped bottom controls/right-hand health-ammo in the packaged executable. The physical display is2560x1600; their actual `-windowed -ResX=1920 -ResY=1080` run logged a1707x1067 desktop/workarea1707x1019. The installed engine's default `bAllowHighDPIInGameMode=False` and SlateApplication::InitHighDPI explain the DPI-virtualized coordinates. This is a desktop window sizing issue, not evidence that16:10 cannot display the HUD.

Reproduced visually using the existing package, paused at spawn: right-hand combat text fell beyond the desktop. One controlled rerun changed only `-ini:Engine:[/Script/Engine.UserInterfaceSettings]:bAllowHighDPIInGameMode=True`; the log then reported2560x1600/workarea2560x1528, and the actual window showed both complete bottom control text and `HEALTH100 ROOK-5 5/25`. No HUD/gameplay rewrite, OS scale change, compile, cook or combat regression route. Raw before/after logs are under `.environment-local/phase-02/dpi-check/`.

Persist the verified engine setting in DefaultEngine.ini for future packages. The already delivered local package uses the same key in its ignored Saved/Config/Windows/Engine.ini; its executable/content bytes remain unchanged. This configuration correction does not update the earlier benchmark or establish human combat-feel acceptance. Official setting: [UUserInterfaceSettings, UE5.8](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UUserInterfaceSettings).

Persistence verification: a final ordinary launch with no command-line DPI override logged2560x1600 and showed complete controls/health/ammo with the weapon visible. The same existing executable SHA remains EB6F3111B25CD1605DDD54BBFDB816ABBFF02B5C5FEA16EBB855D88445FD2A9E. The game was left open for the owner; no movement/fire input or gameplay automation was injected. Evidence: dpi-check/persisted.log.
