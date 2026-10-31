# CINDER RELAY

A narrative-driven single-player post-apocalyptic FPS, built with Unreal Engine 5.8, C++ and Unreal Blueprints.

**当前阶段：Phase 00 — Repository Bootstrap and Production Foundation。** 已通过原生 Unreal Editor 创建 Blank C++ 基础工程；没有实现第一人称角色、战斗、修复、剧情或第一章地图。不要把模板预览场景当作游戏内容。

- 游戏名：CINDER RELAY。
- 仓库：[Leosteeeve/cinder-relay](https://github.com/Leosteeeve/cinder-relay)，**Private**。
- 工作目录：`D:\Projects\FPS Game`；工程：`CinderRelay/CinderRelay.uproject`。
- 实际 Runtime 模块：`CinderRelay`；targets：`CinderRelay`、`CinderRelayEditor`。
- 引擎基线：UE **5.8.4 / CL 58902052**；Windows PC／Visual Studio。
- 目标硬件：RTX 5070 Laptop 8 GB VRAM、32 GB RAM。

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
| 里程碑与英文 Phase 01 提示 | [MILESTONES.md](docs/MILESTONES.md) |
| 精确 Editor 步骤／PowerShell 命令 | [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) |
| 审计、构建证据与限制 | [PHASE00_VALIDATION.md](docs/PHASE00_VALIDATION.md) |
| 官方资料／决策记录 | [研究依据](docs/engineering/research-notes.md)、[决策日志](docs/engineering/decision-log.md) |

## 仓库与验证边界

源码、Config、descriptor 和真实内容纳入版本控制。LFS 已覆盖 `.uasset`、`.umap` 等二进制；当前 Content 为空，仅保留 `.gitkeep`，不伪造资源。Binaries、Intermediate、Saved、DDC、本机日志和 `environment-setup.json` 被忽略；原环境文件仍在本机保留。没有原始第三方素材包或凭据入库。

Editor 创建流程的 UBT baseline 显示 `Result: Succeeded`，包含 UHT、C++ 编译和 DLL 链接；下述插件配置调整后的一次定向编译也成功，直接捕获 exit code 0。Editor 已打开模块并显示默认场景，但启动日志有 13 条引擎自动测试条件错误，尚未逐项归因；不是 clean-log 验收。没有运行项目自动化套件、packaged 验证、性能 benchmark 或人工玩法验收，详见验证记录。

旧代号 ThresholdFPS 从未成为此目录中的实际模块；本轮没有重命名 C++ 模块。旧文档路径只保留兼容链接。原生模板的 EngineAssociation GUID、默认 OpenWorld map、渲染配置和 Editor-only Modeling Tools 插件保持原样；跨机器使用明确的 5.8 安装路径，首个游戏地图在 P01 建立。唯一功能配置收敛是停用 Windows 项目未使用的 AndroidFileServer 插件，并移除其自动生成、含本机 SecurityToken 的配置段，防止凭据入库；没有修改引擎源码。

下一步建议 **Phase 01：原生第一人称控制 + 单个非 WP 灰盒地图 + 一次包启动验收**。本轮不执行。所有实现任务需明确接受条件和非目标，后续不得用“可编译”替代手感、视觉或性能证据。
