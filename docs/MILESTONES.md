# CINDER RELAY — Milestones

按验收门槛推进，不在需求／工作量未明时承诺日期。最终切片为 **Chapter 01 — The Dead Station，12–16 分钟**。Phase 00 不自动授权 Phase 01。

| 阶段 | 交付物 | 依赖 | 接受标准 | 验证方式 | 非目标 |
| --- | --- | --- | --- | --- | --- |
| P00 当前 | 原生 Blank C++ 工程、Git/LFS、私有 GitHub、八份核心文档、审计记录 | 已安装 UE 5.8、GitHub 可用授权 | 真正 `.uproject`／模块；基线编译证据；main 与远端 SHA 一致；无秘密／生成缓存入库 | 文件／配置检查、一次 baseline 与实际配置变更所需的定向编译、staged diff、远端查询 | 不实现玩法或第一章地图 |
| P01 原生可行走基础 | 第一人称角色／镜头、Enhanced Input、一个非 WP 灰盒测试地图、最小输入说明 | P00；确认移动动作和相机限制 | WASD／鼠标正常；碰撞、斜坡／台阶、暂停后输入恢复；运行时无新 error；一次 Win64 Development 包能启动 | 一次相关编译、一次短 Editor／人工走动、包启动 smoke；灰盒性能基线 | 无枪械、敌人、回收、剧情、修复或三分区实现 |
| P02 完整战斗遭遇 | 一个主要武器、一种敌人行为、命中／死亡／重试及基本动画音频 | P01；确认敌人／武器／伤害规则、合规资产 | 单次 3–5 分钟遭遇可完成和失败重试；射击、换弹等批准动作反馈一致；无状态卡死 | 定向规则测试、一次短人工遭遇验收、代表性 combat trace | 无多人、武器海、复杂技能树／潜行体系 |
| P03 回收、修复与叙事 | 少量回收点、一条武器恢复／装配流程、一次可读叙事、一项环境交互 | P02；明确修复步骤／动画资源及本章目标 | 缺材料／完成／取消状态正确；动画结束恢复控制；同一事件不重复发奖；字幕可读 | 针对状态的检查、一次短人工完整流程 | 无完整背包经济、任意零件物理拼装、完整科技树 |
| P04 三分区与 checkpoint | persistent + 铁路场／工坊／地下站子关卡，异步预载、卸载、SaveGame 恢复 | P03；灰盒空间拓扑、回访规则、资产预算 | packaged 三分区连通；首次／回头／恢复／失败注入可靠；重叠峰值达批准预算 | 一次相关编译、定向 Functional Tests、一次短人工转换、规定的 3 往返内存采样 | 无 WP 迁移、自制 streaming 框架、多章节扩展 |
| P05 精修垂直切片 | 12–16 分钟可玩开始与结尾、叙事／战斗／维修一致性、基本设置／credits、可复现 benchmark | P04；确认节拍和资产权利；所有关键阻断关闭 | 一次完整人工流程通过；checkpoint 重开可恢复；关键音画缺陷关闭；预算测量及来源清单可追溯 | 定向回归、打包验证、一次完整人工验收、固定路线 3 轮性能记录 | 不扩张游戏规模或以加功能替代打磨 |

## 单任务合同

每个 Codex task 必须列出：目标、允许文件／系统、依赖、交付物、可测接受条件、具体验证、非目标、停止条件。阶段过大则切成仍可运行的子任务，避免一次生成所有类。

C++ 修改后运行相关 target 编译；数据／Blueprint 变化运行对应资源检查。规则测试只覆盖真实风险，地图恢复用 Functional Testing。没有相应测试就诚实说明，不运行不存在的测试前缀后报告通过。

每个里程碑一次短人工玩法验收，P05 为完整 12–16 分钟。定义性能 checkpoint：P01 灰盒、P02 战斗、P04 转换内存、P05 最终包；遵守 [性能协议](PERFORMANCE_BUDGET.md)，不是每次编辑都测全程。

## 调试次数规则

复现→根据日志／trace定位→最小修改→相关测试→记录结果。同一故障两次修复均失败：停止编辑，提供根因证据、已排除项和下一项诊断；不要反复重建、清 DDC、安装插件或改架构猜测。通过相关检查后停止扩大测试，除非新证据要求。

## 下一阶段英文任务提示（供以后明确启动时使用）

```text
Implement CINDER RELAY Phase 01 only after the owner explicitly starts it.
Read AGENTS.md, docs/GAME_DESIGN.md, docs/TECHNICAL_DESIGN.md,
docs/STREAMING_STRATEGY.md, and docs/PHASE00_VALIDATION.md first.
Audit the actual CinderRelay.uproject, module, targets, and working tree.
Preserve the CinderRelay module name and all working template configuration.

Objective: a reliable, walkable first-person foundation in one non-World-Partition
graybox map. Use ACharacter/CharacterMovement, the native camera facilities,
and Enhanced Input. Establish only the agreed movement actions and camera
settings; clarify material unanswered requirements before implementing them.
Use C++ for core input/control rules and real Editor-created assets for authoring.
Do not fabricate .uasset or .umap files. If Editor automation is unavailable,
provide exact manual steps and clearly mark the dependent acceptance as pending.

Acceptance: WASD and mouse look work; collision, slopes/steps, and input recovery
after pause work; no new runtime errors; one Development Win64 package starts
at the intended map; one short manual movement acceptance pass is recorded.
Record exact build/package commands, exit codes, logs, and unresolved findings.
Run only a baseline and checks justified by the change. After two failed repairs
of the same issue, stop editing and diagnose before continuing.

Non-goals: weapons, enemies, combat, salvage, weapon restoration, story scenes,
save systems, three-zone streaming, new plugins/frameworks, engine upgrades,
module renaming, art polish, and Phase 02. Do not claim gameplay or performance
acceptance from compilation or screenshots alone. End with a reviewable diff
and evidence-based milestone report.
```
