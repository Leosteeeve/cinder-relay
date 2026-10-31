# 官方技术研究与本地证据

查询日期：2026-10-31（America/Los_Angeles）。优先 Epic 官方 UE 5.8 文档；网页可能随时间变更。下表是机制依据，项目采用与否以 decision-log 为准，不把文档描述当作本项目测试结果。

| 主题／官方来源 | 核验结论与本项目处理 |
| --- | --- |
| [UE 5.8 Release Notes](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5-8-release-notes) | 5.8 官方文档可访问；Lumen Lite 标 Beta、部分新特性标 Experimental。保留现有稳定引擎，不因发布说明就启用新特性 |
| [Visual Studio setup](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine) | 5.8 表列 VS 2026 18.0+，推荐 MSVC 14.50、SDK 26100+；实际选择还受本机 UBT SDK 配置和构建日志约束 |
| [Modules](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-modules) | Build.cs／Target.cs 定义编译关系，IDE solution 不是构建事实来源；先一个模块，依赖按需 |
| [C++ vs Blueprint](https://dev.epicgames.com/documentation/en-us/unreal-engine/coding-in-unreal-engine-blueprint-vs-cplusplus) | 两者混用；性能差异取决于上下文。以 C++ 定义规则、Blueprint 编排，先 profile 后改写 |
| [First Person Template](https://dev.epicgames.com/documentation/en-us/unreal-engine/first-person-template-in-unreal-engine) | 原生移动／镜头和可选玩法变体可作为参考；具体 C++ 内容需查安装模板，不假定选择 None 就完全轻量 |
| [Level Streaming](https://dev.epicgames.com/documentation/en-us/unreal-engine/level-streaming-overview-in-unreal-engine) | persistent level 与可动态加载／显示的 sublevels；适用于可控空间边界。页面直开仅返回标题，机制正文通过该官方 URL 的搜索索引获得 |
| [World Partition](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine) | 空间单元及 streaming sources 支持大世界；并非所有项目最优。地图上启用 WP 和启用 streaming 是不同状态 |
| [Data Layers](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---data-layers-in-unreal-engine) | 区分 Editor 与 Runtime、资产与世界实例；任务分层不取代空间驻留和内存预算 |
| [Asset Manager](https://dev.epicgames.com/documentation/en-us/unreal-engine/asset-management-in-unreal-engine) | 原生 Primary Asset／bundle 管理可按需求使用；不必先做自定义 manager |
| [Async Asset Loading](https://dev.epicgames.com/documentation/en-us/unreal-engine/asynchronous-asset-loading-in-unreal-engine) | soft references 解耦资产引用和驻留，发起异步请求仍需显式生命周期处理 |
| [Enhanced Input](https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine) | Input Actions、Mapping Contexts、modifiers 和 triggers 支持上下文输入；原生优先 |
| [Animation Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprints-in-unreal-engine) | 现成骨骼动画图作为基础；高级动画方案由内容与测量驱动 |
| [Gameplay Tags](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-gameplay-tags-in-unreal-engine) | 注册的层级语义标签，可配置或 native 定义；按需求使用，不自动引入 GAS |
| [Unreal Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine) | 原生 trace、分析器、文件输出可用于查瓶颈；本机有 UnrealInsights.exe，但本轮未生成游戏 trace |
| [Memory Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/memory-insights-in-unreal-engine) | 从进程启动追踪 allocation；与专用显存／OS private commit 区分口径 |
| [Automation Framework](https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-test-framework-in-unreal-engine) | 选择相关功能／规则测试；不以空测试列表或启动成功替代测试结果 |
| [Functional Testing](https://dev.epicgames.com/documentation/en-us/unreal-engine/functional-testing-in-unreal-engine) | 使用真实地图的准备、就绪、运行和清理阶段；用于未来转换和检查点恢复 |
| [Saving and Loading](https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine) | 以原生 SaveGame 为基础；网页为动态示例，异步签名另由本机 5.8.4 头文件核验 |
| [Fab License](https://www.fab.com/eula) | 区分 Standard／其他许可、项目整合分发与 standalone 资产再分发；逐项完整条款仍是资产准入证据 |

## 安装版本的直接证据

- `D:\Engines\Unreal\UE_5.8\Engine\Build\Build.version`：5.8.4、CL 58902052。
- `Engine\Config\Windows\Windows_SDK.json`：14.50 preferred family；禁止 14.50.0–14.50.35722。安装目录名为 `14.50.35717`，但 `cl.exe` 产品版本是 **14.50.35739**；不能仅凭文件夹名判定编译器落入禁用区间。
- `Templates\TP_FirstPerson\Config\TemplateDefs.ini`、其 `.uproject`／Build.cs：C++ 版本包含全部变体，依赖包括 AI、StateTree、UI。它们不在本项目源码内。
- `Templates\TP_Blank\Source\TP_Blank\TP_Blank.Build.cs` 与 Editor target：较小原生依赖，V7／Unreal5_8 设置。生成工程后仍应重新核验。
- `Engine\Source\Runtime\Engine\Classes\Kismet\GameplayStatics.h`：存在 `AsyncSaveGameToSlot`；通过代码检查并不等于执行过存档。

本轮没有依赖论坛传闻决定架构；后续 CINDER RELAY bootstrap 通过已安装 Editor 的 Blank C++ 模板正式生成工程，没有下载外部资源包。具体本机审计、命令与执行边界见 [Phase 00](../PHASE00_VALIDATION.md)。

## Phase 01A 补充依据

- [Unreal MCP in Unreal Editor](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)：5.8 官方编辑器 MCP；请求在 game thread 串行执行。本机 ModelContextProtocol 插件存在且标 Experimental。本阶段原生 Python 已能生成与验证资产，未启用 MCP 或接入第三方 server。
- [Unreal MCP plugin index](https://dev.epicgames.com/documentation/unreal-engine/API/PluginIndex/ModelContextProtocol)：官方路径为 Engine/Plugins/Experimental/ModelContextProtocol。
- [Editor Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python?application_version=5.8)：只用于 Editor 资产作者流程；不能把 Python 管线当成 packaged runtime 逻辑。
- 实际 5.8.4 反射核验：Rotator(1,2,3) 为 pitch=2、yaw=3、roll=1；所有生成旋转改为关键字轴。Key 使用 key_name 属性；DirectionalLight 用 get_component_by_class；BlueprintInternalUseOnly getter 未导出 Python，用一次性 class-filtered ObjectIterator 找 local-player input subsystem，仅测试设置时调用。
