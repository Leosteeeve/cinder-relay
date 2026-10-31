# 决策日志

更新：2026-10-31（America/Los_Angeles）。Confirmed 为用户批准或直接核验事实；Provisional 为工程建议；Open 尚未决定。历史代号阶段的选择以本表为准，不继续自动执行旧计划。

| ID | 状态 | 决定／证据 | 影响与边界 |
| --- | --- | --- | --- |
| CR-001 | Confirmed | 正式游戏名 CINDER RELAY；repo cinder-relay；private | 用户允许 public 或 private，本轮沿用明确要求的 Private；不再询问、不公开资源 |
| CR-002 | Confirmed | Elias Venn，男，28 岁，机械维修技师；2118；The Quieting；MERIDIAN 主线 | 以 STORY.md 为 canon，不杜撰原因、敌人或结局 |
| CR-003 | Confirmed | 手工线性章节与小探索空间；Dead Station 12–16 分钟 | 替代旧 10–15 分钟目标和开放的世界结构选择 |
| CR-004 | Confirmed | UE 5.8、Windows、C++ 核心／Blueprint 内容编排 | 本机 Build.version 为 5.8.4 / CL 58902052；不升级引擎 |
| CR-005 | Confirmed fact | 初始目录无 .uproject／旧 ThresholdFPS 模块 | 本轮通过正式 Editor 创建 CinderRelay，不是模块迁移或手造二进制 |
| CR-006 | Implemented | Blank C++ 工程在 CinderRelay/，一个 Runtime 模块 | 现有 Git 根保留；仅 native boilerplate，未实现游戏系统 |
| CR-007 | Confirmed direction | 第一章 persistent + 原生 Level Streaming 三个概念区 | 不默认 WP；本轮未生成三个区；地图名、回访规则 Open |
| CR-008 | Provisional | CharacterMovement、Enhanced Input、AnimBP／Montage、USaveGame、默认 Asset Manager | 按里程碑实施，不预建管理器／GAS／插件体系 |
| CR-009 | Provisional | 1080p／60 FPS 与显存／内存预算 | 均为待测门槛，不能引用为已取得性能 |
| CR-010 | Confirmed policy | 优先可靠性、玩法质量、维护性、性能、视觉 | 一次 baseline、定向验证；同一故障两次失败先诊断 |
| CR-011 | Implemented | 保留现有 Git/LFS；忽略 machine-local environment-setup.json 与生成缓存 | 没有删除原文件；没有将 credentials 或 raw packs 纳入范围 |
| CR-012 | Confirmed fact | 原生 UBT baseline Succeeded，55.91 秒，7 actions | 原始日志保存在本地；Editor 自动子进程 OS exit code 未直接捕获 |
| CR-013 | Open risk | Editor 启动出现 13 条 Condition failed | 邻接 UnifiedError 测试，源文件有英文文本断言，中文本地化关联仅为假设；不静默忽略或改引擎 |
| CR-014 | Preserved | 模板 EngineAssociation 为 GUID；默认 Engine OpenWorld、DX12／SM6、Lumen／RT／Substrate 等设置原样保留 | GUID 在常见注册表项未解析，采用明确引擎路径可启动；需在其他机器确认关联；模板不是第一章或最终性能配置 |
| CR-015 | Implemented | Windows-only 工程停用 AndroidFileServer，删除自动生成且含 SecurityToken 的配置段 | 本机源码确认 Editor 初始化自动写配置；发现于提交前，没有上传；保留其他模板功能设置，descriptor 变化后定向编译一次 |

## 后续决策触发

P01 前收敛移动动作／镜头约束，P02 前定武器与敌人，P03 前定修复流程／叙事，P04 前定回访与加载边界。大幅引擎／模块／架构变更先提交影响、替代方案和迁移计划，不以清理草稿为理由重写工作系统。
