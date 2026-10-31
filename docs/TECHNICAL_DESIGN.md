# CINDER RELAY — Technical Design

## 确认基线与实施边界

用户确定 UE 5.8、Windows／Visual Studio、C++ 核心和 Blueprint 支持层。本机安装 UE **5.8.4 / CL 58902052**。本轮初始审计没有任何 `.uproject` 或旧 `ThresholdFPS` C++ 模块；新工程采用 `CinderRelay`，并通过 Unreal Editor 原生 Blank C++ 流程创建，具体结果见 [Phase 00 验证记录](PHASE00_VALIDATION.md)。没有进行模块重命名。

保留已安装引擎，不修改引擎源码。工程／模块改名、引擎升级和架构替换需先有迁移计划及授权。Phase 00 不包含第一人称移动、射击、任务、修复、存档或流送系统实现。

## 工程与模块

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
