# Chapter 01 — Streaming Strategy

## 决定与概念区域

第一章是手工线性章节，含少量探索支路。采用 **非 World Partition 的 persistent level + 原生 Level Streaming**作为实施默认，不实现自定义流送框架。本轮只规划，不创建三个玩法区。

| 概念区域 | 作用 | 驻留边界建议 |
| --- | --- | --- |
| Railway Yard／铁路场 | 开场、探索、建立方向 | 接近工坊前预载工坊；确认玩家离开与回访规则后再卸载 |
| Maintenance Workshop／维修工坊 | 维修师身份、回收与武器恢复 | 可作为遮挡、预载地下站和 checkpoint 的过渡空间 |
| Underground Relay Station／地下中继站 | 设施任务、MERIDIAN 线索与章节结尾 | 进入前确认几何、碰撞和玩法资源就绪；结束后可受控章节 travel |

建议 persistent level 保持精简：必要的世界级设置、转换触发与极少共享对象。大体积环境、遭遇、声音和章节视觉内容属于相应区域。地图名称和触发位置在灰盒里程碑确定，不创建占位二进制文件。

区域边界由遮挡、玩家速度、可回访范围和加载测量决定，不能机械地按建筑名拆分。铁路场虽在室外，规模有限并不因此要求 WP。[原生 Level Streaming](https://dev.epicgames.com/documentation/en-us/unreal-engine/level-streaming-overview-in-unreal-engine)。

## 其他世界结构的适用范围

| 结构 | 方案 | 使用理由／代价 |
| --- | --- | --- |
| 独立线性章节 | 独立 map + 受控 travel；章节内部按需 streaming | 简单且驻留明确；OpenLevel 不承诺无阻塞／真正无缝 |
| 连续室内／本章三个区 | persistent + 原生 sublevels | 门厅、拐角和竖向连接便于控制边界，须测重叠峰值 |
| 枢纽 | 小枢纽 + 相邻 sublevels，远任务独立 map | 根据回访和同时驻留成本决定；不常驻全部任务 |
| 大型连续室外 | 评估 WP、streaming sources、HLOD／OFPA | 空间单元管理适合大世界，附加内容与调试成本高；不是本章默认 |

[World Partition](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine) 由 streaming sources 和空间单元控制驻留。若后续规模改变，先更新决策再采用；不得擅自转换已工作的章节。Runtime Data Layers 可表达 WP 内任务阶段，Editor Data Layers 用于编辑组织；二者不能替代资产生命周期。[Data Layers](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---data-layers-in-unreal-engine)。

## 地图与资产的不同职责

Level Streaming 负责世界内容、Actor 和 visibility；Asset Manager／StreamableManager 负责内容引用与请求。加载 `UWorld` 资产本身不等于地图激活、碰撞／导航就绪或玩家可以传送。

小型明确常驻依赖可用硬引用；跨区大资源、角色库、音频／动画采用 `TSoftObjectPtr`／`TSoftClassPtr`，需要 ID／bundle 才使用 Primary Asset。软引用不是自动异步加载，也不是自动 cook 保证；用明确引用／Asset Manager scan与 cook 规则覆盖目标资产，并在 packaged build 实测。[Async Loading](https://dev.epicgames.com/documentation/en-us/unreal-engine/asynchronous-asset-loading-in-unreal-engine)、[Asset Manager](https://dev.epicgames.com/documentation/en-us/unreal-engine/asset-management-in-unreal-engine)。

不得让常驻 Blueprint、GameInstance 或 class defaults 硬引用整个章节。使用 Reference Viewer／Size Map 查依赖；跨区保存稳定 ID 或弱引用，不让已离开的区域 Actor 被持久对象留住。

## 最小转换协议

1. 进入提前触发范围，发起一次原生异步加载请求，记录 owner／目标 ID／请求序号，禁止重复堆积。
2. 预载下一段必需资源；提前距离依据“实测 load latency × 最大移动速度 + 余量”，考虑回头与快速移动。正常只预载一个目标区。
3. 等待 load、visibility 和必需内容就绪，检查入口碰撞、导航及任务依赖；不以固定 Delay 代替完成条件。资源注册、渲染资源和 PSO 仍可能产生游戏线程卡顿。
4. 安全放行玩家，激活遭遇／叙事，仅触发一次；若失败，留在安全区域，显示可恢复反馈，不让玩家进入空世界。
5. 玩家离开安全缓冲区且无需旧区后，停止其 AI／声音／latent 操作、解绑事件、失效旧回调，原生卸载 level，释放 load handles／bundles 和硬引用。
6. 检查正常 GC 与渲染资源回收后的驻留。卸载完成不等于专用显存即时下降；不在交火中反复强制 GC，异常残留先查引用／缓存。

支持取消、返回、重复 trigger、checkpoint 恢复、owner EndPlay 和超时；回调必须确认 owner 与当前请求仍有效。checkpoint 存储区域／对象稳定 ID 和值，不保存 Actor 指针。

## 预算与验收

峰值包括基础系统、共享资源、当前区、下一段和切换过程；不能用单区静止值宣称通过。暂定 VRAM／RAM 与采样协议见 [PERFORMANCE_BUDGET](PERFORMANCE_BUDGET.md)。预算不够时调整资产密度、遮挡和预载时机，不默认扩大纹理池或常驻全部区域。

| 环境 | 能证明什么 | 不能证明什么 |
| --- | --- | --- |
| Editor／PIE | 引用、加载事件顺序、关卡设置、碰撞、基础交互 | 已在内存／DDC 内的资产不证明首启或真实 I/O；Editor 能找到资产不证明 cook 完整 |
| Packaged Development | 实际 cook 内容、软引用解析、首次进入、往返、卸载与真实内存峰值 | 没有固定设备／设置的单次 FPS 不能作为可靠 benchmark |
| 人工完整试玩 | 空间可读性、遮挡是否自然、过渡节奏、叙事连续性 | 感觉流畅不能替代 trace 和内存测量 |

P04 接受测试：首次进入三个区域、反向返回、同一 trigger 重入、checkpoint 跨区恢复、一次失败注入以及 3 次往返驻留检查。无穿地、不可见碰撞、重复叙事或缺 cook 资源；所有性能数字必须带原始证据。此时才正式接受流送方案。
