# CINDER RELAY

A narrative-driven single-player post-apocalyptic FPS, built with Unreal Engine 5.8, C++ and Unreal Blueprints.

**当前阶段：Phase 01A — Playable Greybox: The Dead Station。** 在原生 CinderRelay 工程上增加第一人称控制、三连通区域、模块／终端交互、四步目标和原生 UMG。没有战斗、武器装配、AI、存档或流送；不自动进入 Phase 01B。

- 游戏名：CINDER RELAY。
- 仓库：[Leosteeeve/cinder-relay](https://github.com/Leosteeeve/cinder-relay)，当前 **Public**（2026-10-31 远端查询；Phase 01A 未修改可见性）。
- 工作目录：`D:\Projects\FPS Game`；工程：`CinderRelay/CinderRelay.uproject`。
- 实际 Runtime 模块：`CinderRelay`；targets：`CinderRelay`、`CinderRelayEditor`。
- 引擎基线：UE **5.8.4 / CL 58902052**；Windows PC／Visual Studio。
- 目标硬件：RTX 5070 Laptop 8 GB VRAM、32 GB RAM。

## 打开原型

打开工程后，默认地图为 `/Game/Generated/Phase01A/Maps/L_CH01_Greybox`。Play 下拉选择 **Standalone Game**：普通 PIE 的 Esc 默认会结束 Editor 试玩，Standalone 中 Esc 才作为游戏暂停键。独立启动命令见 [WINDOWS_SETUP](docs/WINDOWS_SETUP.md)。

WASD 移动、鼠标看、Shift 跑、Ctrl 蹲、Space 跳、E 交互、Esc 暂停。进入工坊，在左侧工作台拿青色电力模块，沿后门坡道下行，在橙色 Relay Nine 终端安装，再调查青色信号台；结束菜单支持重新开始。所有推进都通过正常走动和交互，不需要开发者控制台。

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
| Phase 01A 计划、验证与后续门槛 | [MILESTONES.md](docs/MILESTONES.md) |
| 精确 Editor 步骤／PowerShell 命令 | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| 审计、构建证据与限制 | [PHASE00_VALIDATION.md](docs/PHASE00_VALIDATION.md) |
| 官方资料／决策记录 | [研究依据](docs/engineering/research-notes.md)、[决策日志](docs/engineering/decision-log.md) |

## 仓库与验证边界

源码、Config、descriptor 和真实 Editor 生成内容纳入版本控制。25 个生成资产包含 map、8 个纯色材质、11 个输入资产和 5 个配置 Blueprint，二进制使用 Git LFS。地图有 155 个具名生成 Actor，重复生成不增加数量。Binaries、Intermediate、Saved、DDC、本机日志和 `environment-setup.json` 被忽略；原环境文件保留。没有外部素材包、凭据或手造二进制占位文件入库。

Phase 01A 首次 CinderRelayEditor 编译成功（87.44 秒，exit 0）；修正独立审查发现的输入 possession 生命周期后定向编译也成功（20.95 秒，exit 0）。地图生成及幂等检查由真实 Editor 执行；最终 PIE smoke **11 项通过**，实际走动、三次 E 交互、结尾和重开均通过，没有传送。玩法证据、调试记录和剩余限制见 [MILESTONES](docs/MILESTONES.md)。Editor 启动仍有 Phase 00 已知的 13 条引擎自测条件错误，不能声称 clean log。工坊入口偏亮，物理键鼠和手感待人工接受；没有 packaged／正式性能 benchmark。

保留 CinderRelay 模块、EngineAssociation GUID 和模板渲染设置；未改引擎源码。01A 仅将默认地图切到灰盒、关闭旧输入附加缩放／平滑，并启用两个 Editor-only 资产生产插件。AndroidFileServer 继续停用。源码职责与配置变更理由见技术文档。

下一步建议先人工确认移动、光照和空间可读性，再批准 **Phase 01B：原生 Level Streaming 的区域拆分与 packaged 验证**。精确分区边界已记录；本轮不实施流送。
