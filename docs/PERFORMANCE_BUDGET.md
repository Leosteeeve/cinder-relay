# CINDER RELAY — Performance Budget

**以下全部是项目暂定目标，不是基准测试结果，也不是 Epic 或 GPU 厂商的性能保证。** Phase 00 只有原生基础工程，没有已实现的玩法、性能 trace 或可报告 FPS。

## 测试档与预算提案

基线设备由用户指定：RTX 5070 Laptop GPU，8 GB VRAM，32 GB RAM。CPU、GPU TGP、驱动、插电／电源模式、温度和散热状态均须在真正测试时记录；笔记本同名 GPU 不代表同样性能。

| 项目 | 暂定目标 | 测量口径 |
| --- | --- | --- |
| 分辨率／渲染 | 1920×1080，100% screen percentage，动态分辨率关闭；高画质作为待验证起点 | 固定实际 scalability、AA、Lumen／阴影／RT 设置并保存；不从 preset 名称推导具体值 |
| 原生响应 | 60 FPS 目标；帧生成关闭；基准时关闭 VSync／帧率上限 | 超分另列档位，不能以插帧结果替代原生性能 |
| 帧耗时 | 稳态 p95 ≤16.67 ms，p99 ≤25 ms | 使用相同路线的逐帧数据；报告中位数、p95、p99 和 >50 ms 帧数 |
| CPU／GPU 余量 | Game Thread p95 ≤12 ms，GPU p95 ≤14 ms，Render Thread 同时观察 | CPU／GPU 可重叠，不把线程耗时简单相加；缺失 GPU 数据标明未测 |
| 卡顿 | 交互／战斗测量段没有非预期 >50 ms 帧 | 将明确加载界面分段统计，不能删掉区域转换卡顿来美化数据 |
| 专用显存 | 稳态 ≤6.5 GiB，转换峰值 ≤7.0 GiB | 包含渲染目标、纹理、几何等整包成本；确认系统提供的实际预算并取更严格限制；监测 eviction／共享内存回退 |
| 进程内存 | 稳态 Private Bytes ≤10 GiB，峰值 ≤12 GiB | OS 进程 private commit 与 UE allocation/LLM 分开记录；不能用 Working Set 冒充总分配 |
| 重复转换 | 3 次往返后稳定驻留无持续上升；首末同位置稳定采样差值 ≤256 MiB，超出则诊断 | 区分预热缓存与泄漏；保留回收时间、存活对象和引用证据 |
| 预加载 | 常态仅预载一个必要目标区域 | 当前区 + 目标区 + 引擎／共享资源同时计入峰值；加载提前量依据实测决定 |

这些数字必须在 Phase 1／2 得到真实基线后修订并记录理由；不得为了宣称通过而在同一验收中悄悄降低质量或改门槛。若目标不合理，先报告差距和取舍，待确认后更新。

## 有界 benchmark

在路线图的 P01（灰盒基线）、P02（战斗）、P04（转换与存档）、P05（最终切片）设测量点。普通文档／参数修改不触发完整性能轮次。

1. 使用 **packaged Development build**；记录 commit 或未提交源码／内容清单哈希、引擎 CL、目标、cook 日志、设备与所有渲染设置。PIE 数据仅作开发诊断。
2. 指定地图、起始检查点、相机路线、动作与遭遇条件；可复现随机数种子，不强求物理完全确定性。P01 起冻结一条包含代表性停留点的 120 秒路线，后续变更路线需记录版本。
3. 每个正式 checkpoint 一次新进程首轮记录启动／首次转换；不删除用户缓存来假装冷机。明确标注“进程冷启动，OS／驱动缓存状态未清空”。
4. 预热 60 秒后，进行 3 次同条件 120 秒测量。保留每轮原始数据和分位数；只有数据丢失、明显外部干扰或新修复才重测，不反复刷最好成绩。
5. 使用 Unreal Insights 分析 CPU／GPU frame、loading／bookmark，观察最差区间；`stat unit` 等仅作快速定位。保存截图之外的原始 `.utrace` 和指标表。
6. 内存追踪单独从进程启动打开 `-trace=default,memory`；开销较高的 allocation/callstack capture 不混作纯帧率对比。Memory Insights 主要看分配与归因，不能独自证明专用 VRAM 使用；显存结合 RHI／GPU 工具与 OS 数值，并记录各工具口径。
7. 在 P04 合并一次 3 往返驻留测试，P05 全流程体验只做一次 12–16 分钟人工验收；不是每次编辑都跑这些检查。

依据 [Unreal Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine) 和 [Memory Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/memory-insights-in-unreal-engine)。内存 channel 必须在进程开始启用，packaged memory trace 使用 Development 配置。

## 先定位，再优化

保留一个复现→定位 trace 中最大成本→提出单一假设→做最小修改→运行对应片段→比较同条件数据。每次只改变可归因的变量；保留正确性与画面检查。C++ 重写、降低画质、扩内存池和增加 streaming cell 都不是默认修复。

同一故障两次修复失败后，停止试错，交付：复现步骤、原始错误／trace、两次假设及结果、最可能根因与可区分它们的下一项检查。诊断完成后再决定继续；不要无限 rebuild、清 DDC、重装或扩大改动范围。

## 当前结果

无 benchmark、GPU／VRAM 实测、视觉验收或手感结论。原生 CinderRelayEditor baseline 编译成功与上述目标无因果保证。尚需确认实际画质档、GPU TGP、输出分辨率和是否接受超分。
