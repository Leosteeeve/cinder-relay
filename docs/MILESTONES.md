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
| P00 已完成 | 原生 Blank C++ 工程、Git/LFS、私有 GitHub、八份核心文档、审计记录 | 已安装 UE 5.8、GitHub 可用授权 | 真正 `.uproject`／模块；基线编译证据；main 与远端 SHA 一致；无秘密／生成缓存入库 | 文件／配置检查、一次 baseline 与实际配置变更所需的定向编译、staged diff、远端查询 | 不实现玩法或第一章地图 |
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

## 单任务合同

每个 Codex task 必须列出：目标、允许文件／系统、依赖、交付物、可测接受条件、具体验证、非目标、停止条件。阶段过大则切成仍可运行的子任务，避免一次生成所有类。

C++ 修改后运行相关 target 编译；数据／Blueprint 变化运行对应资源检查。规则测试只覆盖真实风险，地图恢复用 Functional Testing。没有相应测试就诚实说明，不运行不存在的测试前缀后报告通过。

每个里程碑一次短人工玩法验收，P05 为完整 12–16 分钟。定义性能 checkpoint：P01 灰盒、P02 战斗、P04 转换内存、P05 最终包；遵守 [性能协议](PERFORMANCE_BUDGET.md)，不是每次编辑都测全程。

## 调试次数规则

复现→根据日志／trace定位→最小修改→相关测试→记录结果。同一故障两次修复均失败：停止编辑，提供根因证据、已排除项和下一项诊断；不要反复重建、清 DDC、安装插件或改架构猜测。通过相关检查后停止扩大测试，除非新证据要求。

## 后续任务边界

Phase 01B 需要用户另行启动。先确认回访范围并用现有坐标／tags 制定迁移清单，保留已工作的输入、交互和目标状态。不得直接将本章转换为 World Partition，也不得在尚未验证 packaged 加载时声称无缝。
