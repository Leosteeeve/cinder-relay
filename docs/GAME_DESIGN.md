# CINDER RELAY — Game Design

## Phase 01A 可玩探索原型

用户批准三个区域连通的单地图灰盒：铁路场出生、工坊发现电力模块、下行通道进入中继站。模块只承担目标状态，不是背包或武器装配系统。

目标原文依次为：

1. Reach the maintenance workshop.
2. Find a functional power module.
3. Restore power to Relay Nine.
4. Investigate the restored signal.

最后显示 `MERIDIAN NETWORK / CONNECTION RESTORED`，提供重新开始与退出。WASD／鼠标、Shift 跑、Ctrl 蹲、Space 跳、E 交互、Esc 暂停。01A 是短探索闭环，不声称已达到最终 12–16 分钟精修切片目标。

状态：用户于 2026-10-31 批准的制作方向；实施范围以 [MILESTONES](MILESTONES.md) 为准。

## 已确认身份

Phase 02 adds the approved **ROOK-5** fictional, manually cycled early carbine and **Ash Warden** humanoid scouts. First Contact takes place in the Rail Yard before the workshop module is completed. Two scouts search the equipment; the player may fight, retreat or use the north rail flank. Kills never gate the story. One +10 reserve ammunition case is near the workshop approach. Existing greybox cover and train cars provide real collision cover.

ROOK-5 initial tuning: 5-round magazine, 25 reserve, 0.9s cycle, 2.4s reload, 40 body damage, 1.75 head multiplier, 85/65 hip/ADS FOV and approximately 0.18s ADS transition. Parameters live in DA_Rook5. These are game abstractions, not real mechanical instructions. LMB fire, RMB aim, R reload; streaming retry moves to F5. Sprint lowers the weapon and blocks fire/ADS, but a pending reload continues. Pause freezes gameplay timers; death cancels reload without transferring ammunition. Restart resets the whole chapter.

Player/scout initial health is 100. Scouts use 8 damage and 1.8/2.05s shot intervals, configurable accuracy/range and finite target memory. Model poses, viewmodel motion and original synthesized audio are explicitly temporary. There is no skeletal animation or final-art claim.

- 游戏名：**CINDER RELAY**；GitHub 仓库：`cinder-relay`，Phase 01A 最终远端查询为 **Public**；用户允许 public 或 private，本轮未修改仓库设置。
- Windows PC 单人、叙事驱动、末日题材 FPS；UE 5.8，C++ 核心与 Blueprint 编排。
- 主角：**Elias Venn，28 岁，男性，机械维修技师**。
- 时间：**2118 年**。全球基础设施灾难性停摆事件 **The Quieting** 已过去数十年。
- 主线：恢复废弃基础设施、重新发现技术，逐渐揭开 **MERIDIAN** 网络的真相。
- 世界：手工制作的线性章节，带小规模探索空间；不是大型连续开放世界。
- 技术成长方向：从过时机械装备走向现代、未来装备。整个成长跨度属于完整游戏，不要求首个切片全部实现。

## 五个玩法支柱

| 支柱 | 对制作的要求 | 首个切片的范围建议 |
| --- | --- | --- |
| 电影感环境叙事 | 场景中的故障、遗留物与空间组织表达故事 | 一段可读的环境线索链和一段有始终的叙事 |
| 满足感第一人称射击 | 命中、动画、音效、镜头与敌人反馈一致 | 一把主要武器、一次完整战斗遭遇 |
| 探索与回收 | 小空间内寻找有明确用途的物品 | 少量固定回收点、一种修复用途；不先做大背包经济 |
| 动画化武器修复／装配 | 维修师身份通过动作表达 | 一段真实可用的修复／装配交互与动画；参数和步骤另定 |
| 技术进阶 | 新技术改变可用装备与行动能力 | 展示一个恢复技术的节点；不做完整科技树 |

表中切片数量是成本控制提案，不能当作用户已逐项批准。秘密行动是此前方向背景；最新主线优先，是否保留秘密行动动机、是否需要潜行机制仍待确认。

## Chapter 01 — The Dead Station

目标时长 **12–16 分钟**，取代旧代号阶段的 10–15 分钟目标。三个已确认场景：废弃铁路场、维修工坊、地下中继站。

早期节拍建议由 Phase02 的铁路场遭遇取代：铁路场建立目标并发生 First Contact，工坊回收，地下中继站恢复信号。最终各段时长仍待试玩，不能用等待凑时长。Ash Wardens 和 ROOK-5 已批准，武器装配与后续事件仍未实施。

切片需有可玩的开始与结束、明确下一步提示、一次完整遭遇、一段叙事、一个有作用的环境交互、一次区域转换、checkpoint 恢复、基本音频／动画及可复现 benchmark。

## 仍待设计的内容

武器修复零件、后续敌人类别、完整潜行机制、移动动作、主角外观、配音／字幕语言、具体谜题、后续事件顺序、叙事结尾、资产费用与开发排期仍开放。不要据“末日”自动加入丧尸、核战争或生存建造。

Phase 00 只创建原生工程与制作基础，不实现以上系统。多人、广域开放世界、完整制作经济、大型科技树和复杂分支剧情不纳入首个切片计划。
