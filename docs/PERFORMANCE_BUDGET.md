# CINDER RELAY — Performance Budget

**预算表是项目目标，不是 Epic 或 GPU 厂商的性能保证。** 文末记录 Phase 01B 的真实 packaged 诊断测量；功能已通过，但本次数据没有达到 60 FPS 帧耗时目标。灰盒结果不代表最终美术性能。

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

## Phase 01B packaged 诊断记录 — 2026-10-31

一次 Windows Development 包、一次新游戏进程、一次三轮 C→B→A→B→C 回访；不清缓存、不强制逐区 GC。记录 151.286 s / 6476 行 actor tick；三轮回访段 4766 行。此次依 Phase 01B 指令执行有界路线，包含初始安全加载、Ready veto/反向取消/失败重试；不是上述未来正式 60 s 预热 + 3×120 s 的无追踪性能 benchmark。

条件：UE 5.8.4 CL 58902052；AMD Ryzen 9 8945HX；32 GB RAM；RTX 5070 Laptop，驱动 616.92；Windows D3D12 SM6。1920×1080 原生结束截图确认输出分辨率，`r.ScreenPercentage=100`、DynamicRes=0、VSync=0、MaxFPS=0。所有 sg.* 画质项为 **3 / Epic**；AA method=4（TSR，100% 输入分辨率）、Lumen GI/reflection=1、RT=1、Lumen HardwareRayTracing=1、VSM=1。没有启用帧生成或下调质量。`settings.txt` 初次写入早于 ExecCmds 时曾为 ScreenPercentage=0；游戏日志确认移动前设为100，Restart 后最终 settings.txt 也为100。

供电查询 PowerOnline=true、Charging=true；Windows 电源方案为“平衡”。TGP/power.limit 返回 N/A，不猜测额定功率；本次 GPU 监测约 21.77–40.16 W、56–62°C。未固定/锁定时钟，没有人工确认所有期间持续前台。OS/驱动/DDC 缓存未清空；“新进程首启”不是物理冷机。

同时启用 `cpu,gpu,frame,bookmark,loadtime,memory,metadata,assetmetadata`。Memory allocation/callstack 跟踪、自动路线、CSV 缓冲有额外开销；因此这些是带追踪的诊断结果，不能作为无追踪 60 FPS 的最终证明。

| 三轮回访段 | median ms | p95 ms | p99 ms | 最大 ms |
| --- | ---: | ---: | ---: | ---: |
| World tick frame delta | 15.993 | 71.453 | 88.655 | 111.686 |
| Game Thread 原生计数器 | 3.164 | 15.529 | 23.895 | 102.161 |
| Render Thread 原生计数器 | 15.963 | 70.780 | 86.985 | 112.294 |
| GPU 原生 RHI frame 计数器 | 10.800 | 15.704 | 16.217 | 18.810 |

回访段 >50 ms 的 frame delta 有 **615** 行。p95 frame 超出16.67ms目标 **54.78 ms**，GT/GPU p95也分别高于12/14ms目标。本阶段不以“流送功能通过”替代性能目标。world delta 在启动可被引擎截断，整段最大400ms不能当作真正最差帧；Insights 原始 trace 含约1.84s的启动/初期 GameThread frame。线程计数器来自前一个引擎帧，不能简单相加。

| 驻留/加载指标 | 实测 |
| --- | --- |
| 初始 A request→Ready | 2612 ms；角色生成始终延后到地板/碰撞就绪 |
| 正常区域转换 request→Ready | 19–885 ms（剔除明确的 B veto/取消/故障请求）；首进 C 352ms，首次返回 B 301ms、A 885ms |
| 预载余量 | 800cm / 500cm/s ≈1.6s，大于本次最大正常转换0.885s；胶囊 overlap 还略提前。不是所有磁盘/缓存状态的保证 |
| 进程 Working Set 峰值 | 2,629,877,760 B ≈2.45 GiB |
| 进程 commit 峰值 | 5,028,859,904 B ≈4.68 GiB；UE Windows `UsedVirtual=PROCESS_MEMORY_COUNTERS.PagefileUsage`（commit charge），不是虚拟地址范围或显存 |
| 同一 C 停留点 cycle1/2/3 commit 中位数 | 4,440,100,864 / 4,578,897,920 / 4,585,627,648 B |
| cycle3−cycle1 | +145,526,784 B ≈138.79 MiB，小于暂定256MiB；只有三轮观察，不宣称排除所有泄漏 |
| 真实 Unloaded 事件 | A 4、B 8、C 3；均原生 Unloaded、loaded=0、visible=0、desired=0 |
| GPU 监测总已用显存峰值 | nvidia-smi 全适配器4173MiB，包含其他进程；不能当作游戏独占显存预算验收 |

后续加载记录出现旧地板 weak witness 无效（witness_valid=0），证实观察的旧 Actor 没有被控制器强引用留住；不是所有资产的完整 Reference Viewer/引用链审计。显存池保留不等于 level 未卸载。

证据根目录 `.environment-local/phase-01b/`：`packaged-game.log`、`packaged.utrace`（1,674,598,618 B）、`packaged-summary.json`、`os-samples.csv`；包内 `Windows/CinderRelay/Saved/Phase01B` 有原始 CSV、settings、route、receipt 和 ending.png。`summarize_streaming.py` 只汇总这些数据。

Unreal Insights 已实际离线分析 trace，exit 0；解析 76 个 CPU threads、22,103,638 scopes，Memory Insights 收到117,199,686系统内存事件。CPU 导出包含 `Sync_RenderingThread` / `GameThreadWaitForTask` 约119.99/119.86s（含嵌套、整段启动与等待，不相加）。这支持优先调查渲染线程/同步等待，而不是假设控制器加载逻辑耗尽GT。GPU trace有少量时间戳顺序警告；本表GPU数字来自原生RHI计数器。明确区分观察与原因假设，不能把所有开销归咎于memory tracing。

进一步按真实 `RenderThread 0` 导出的22–32s片段显示 Scene scope 可达83.34ms；完整trace有 `WaitForVisibilityTasks`（最大56.23ms）与 `UpdateAllPrimitiveSceneInfos`（启动/初期最大1.805s）。`insights-render-hitch.csv` 含明确ThreadName；统计表默认也带GPU聚合项，不能把整张表当成单线程时间相加。计数器目录和Memory Insights事件均已实际解析。第一次导出线程名/文件引号不符合此版本接口，按真实名称修正后定向导出成功；没有再运行游戏。

下一性能任务应先做与当前场景/设置相同的短定向、关闭高开销 memory trace 的对照，定位渲染/同步尖峰；保留图像质量，不进行架构重写。此次未自动启动该额外 benchmark 或优化。

## Phase02 preflight — existing package, lower-overhead comparison

The owner explicitly authorized one preflight comparison. Reused the exact Phase01B executable (SHA E1C74DDE2C0ABAB85217452DEF087C3F921FF4B8D14838BC3382449BD7F61A42); no new packaging, quality reduction or cache clearing. Same1920×1080/100%/Epic/TSR/Lumen HWRT settings and native frame counters. Only `frame,bookmark` trace channels, no allocation/callstack or CPU/GPU scope trace. Three-cycle route and Restart PASS,143.497s/11714rows.

| Three-cycle segment (8610 rows) | median ms | p95 ms | p99 ms | max ms |
| --- | ---: | ---: | ---: | ---: |
| Frame delta | 12.796 | 14.998 | 17.269 | 36.566 |
| Game Thread | 1.405 | 2.532 | 3.842 | 22.810 |
| Render Thread | 12.784 | 14.968 | 17.035 | 36.535 |
| GPU | 11.857 | 13.512 | 13.897 | 14.574 |

No cycle-segment frame >50ms; the earlier sustained ~71ms p95 RT problem did not recur. Startup/early all-recorded max RT374.200ms and frame120.558ms remain; this is not zero-hitch certification. Peak working set1,777,156,096B and commit4,246,114,304B. Same-C checkpoint commit growth4,063,232B across three cycles. Raw results `.environment-local/phase-02/preflight-*`.

This is evidence against attributing the old sustained hitch to the native streaming controller. It does not isolate one causal variable perfectly: a read-only NullRHI Editor asset audit briefly overlapped the later portion, and OS/driver cache/power conditions were not fully controlled. No render/streaming rewrite was performed. Phase02 combat must be measured separately with its tracing conditions and segment length reported.

## Phase02 packaged combat sample — measured, not a clean benchmark

One actual Windows Development run, same RTX5070Laptop8151MiB /32GB platform, driver616.92. Window1920x1080,ScreenPercentage100,DynamicRes0,VSync0,t.MaxFPS0, all ten scalability groups3(Epic),TSR(4),RayTracing1,LumenHWRT1. No settings lowered or caches cleared. Power/thermal/background desktop conditions were not fully controlled; no concurrent Unreal Editor audit in this run. Trace channels: cpu,gpu,frame,bookmark,loadtime; no requested allocation/callstack tracing. Automated route and PNG captures add overhead. Native thread/GPU counters refer to previous engine frames and must not be summed.

| Segment | Rows / recorded seconds | Frame p95 ms | GT p95 ms | RT p95 ms | GPU p95 ms |
| --- | --- | ---: | ---: | ---: | ---: |
| All recorded, including restart/streaming/capture |5876 /97.547|20.451|6.166|20.007|14.448|
| Actual player combat (`fight`) |477 /7.090|19.261|5.049|19.187|15.185|
| AI/nav/cover diagnostic stages |1130|23.644|15.321|22.277|11.585|
| Post-combat walking / streaming |3029|18.514|3.230|18.441|14.819|

Combat median frame12.671ms,p9921.519ms,max378.478ms;2frames>50ms. All-recorded12frames>50ms,max frame delta400ms (engine-clamped DeltaSeconds, not an upper bound on wall-time pauses),GT341.583ms,RT429.930ms,GPU22.424ms. The instrumented combat p95 exceeds the16.667ms60FPS budget by2.594ms. This does not establish the clean game's FPS, nor final-art performance. Compared with the low-overhead Phase01B preflight, sustained~71msRT p95 still did not recur; scope tracing, route/camera/content and captures differ, so the difference cannot be assigned entirely to combat.

Peak process working set1,691,394,048B(1.575GiB),private commit4,413,399,040B(4.110GiB); these are not dedicated VRAM or an asset-residency total. Two normal A unloads, three B unloads, one C unload occurred, independently of two Restart map travels. Return A logs both `ReconciledDefeated` IDs; no strong combat actor ownership in the session sets. No repeated forced GC or claim that cached GPU memory implies failed unloading. Single combat-return sample does not establish leak freedom.

Offline Insights analyzed191,456,648B trace,75CPUthreads/21,625,437scopes,exit0. Named CPU scopes below are inclusive per invocation, not per frame; nested times must not be added. The export also includes default GPU aggregate rows, so only identified CPU scopes are used here.

| CPU scope | Calls | Total ms | Mean ms | Max ms |
| --- | ---: | ---: | ---: | ---: |
| CR_WeaponPresentation |5789|51.697|0.009|0.588|
| CR_WeaponShot |4|1.787|0.447|0.782|
| CR_WardenDecision |237|23.111|0.098|7.147|
| RecastNavMesh-Default tick |5797|7.465|0.001|0.095|
| UNavigationSystemV1::OnWorldPostActorTick |5799|1.790|<0.001|0.029|

Native path creation/failure/recovery and readiness are functionally proven; this trace does not separately attribute every asynchronous Recast tile-build worker task. These small visible scopes therefore are not a total navigation budget. No optimization inferred merely from using C++.

Evidence for follow-up: GT `Sync_RenderingThread` total76.888s/max394.183ms overlaps its child wait; RT `FDeferredShadingSceneRenderer_Render` max418.584ms and `WaitUntilTasksComplete` max395.648ms show render/synchronization work. PNG compression ran5times (some overwrite the same screenshot path),total961.554ms/max320.160ms. Thus screenshot instrumentation is a plausible contributor to captured GT spikes; the trace does not prove it explains all hitches. Readiness/load transitions and restart also coexist with spikes. Preserve the native architecture; next performance work should isolate these observations under separately authorized same-quality conditions.

Analyzer limits: Insights reports30,663MemAllocTagTracker errors with this partial-channel capture,4LoadTime warnings, and GPU timestamp interleaving/reversal warnings(max~1.171ms). Memory-allocation analysis is not used. GPU table values above come from native RHI frame counters, not reconstructed invalid GPU event durations. Runtime has no Fatal/Error/Ensure, but expected native teardown/VSync/navigation-test warnings are listed in MILESTONES.

Evidence: `.environment-local/phase-02/combat-summary.json`, `packaged-combat.log`, `combat.utrace`, `insights.log`, `insights-game-thread.csv`, `insights-render-thread.csv`, `insights-all-threads.csv`, and `package/Windows/CinderRelay/Saved/Phase02/{frames.csv,memory.csv,settings.txt,route.txt,acceptance.json}`. Raw logs/traces/package remain ignored. This bounded run is complete; no further package, cache clear or quality change was used to chase targets.

## Phase03 measurement boundary

The original1080p/Epic reference remains unchanged. The14asset restoration kit adds one6720vertex skeletal prototype (40imported bones), three static meshes, six constant-color materials, one short original SoundWave and one22s LevelSequence. These counts are content facts, not performance guarantees. The instrumented Phase02 combat p95=19.261ms is not a clean60FPS baseline.

The bounded packaged route records native frame/GT/RT/GPU counters and1Hz process-memory samples, separated by gameplay, assembly, return-to-gameplay and backtracking stages. It includes actual screenshots, native sequence pause and restarts; report those costs/conditions explicitly. Editor frames are not packaged1080p measurements. No DDC clearing, silent quality reduction, speculative optimization or new expensive rendering feature is authorized by these measurements. Actual packaged results and the failed first attempt are reported below.


### Phase03 packaged observations — 2026-10-31

One Windows Development cook/package, followed by one focused game-binary rebuild for the documented acceptance-harness readiness race. No content re-cook, quality reduction or cache clearing. The corrected run resumed at scenario1 and passed scenarios1–4 in182.782s; scenario0 passed in the preserved first attempt. This is not a single uninterrupted full-start pass. Same RTX5070Laptop/32GB system, driver616.92; actual1920x1080 capture, all ten scalability groups3/Epic, ScreenPercentage100, DynamicRes0, VSync0, t.MaxFPS0, TSR4, RayTracing1 and LumenHWRT1. Windows desktop2560x1600/workarea2560x1528 confirms the existing DPI fix remains active. Power, thermal state and background desktop load were not controlled. No Editor or Blender render ran concurrently.

Trace channels cpu,gpu,frame,bookmark,loadtime; no requested allocation/callstack capture. Automated movement, screenshots, one1.5s pause, restart and streaming are included. Native GT/RT/GPU counters refer to prior engine frames; do not add them. Segment seconds below sum recorded engine frame deltas, not independent wall-time measurements.

| Corrected-run segment | Rows / recorded seconds | Frame p95 ms | GT p95 ms | RT p95 ms | GPU p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| All recorded |13765 /180.688|16.663|2.539|16.553|15.402|
| Three actual combat encounters |1844 /20.996|14.865|2.256|14.738|13.876|
| Full assembly, pause and four captures |1429 /23.535|22.108|1.771|22.013|21.145|
| Return: ADS, shot and reload |339 /5.349|20.432|2.142|20.374|19.374|
| Scenario1 walking/backtracking |3766 /47.833|15.309|1.973|15.268|14.124|
| Optional-workbench bypass walking |3637 /47.316|15.404|3.297|15.352|13.847|

Assembly p95 exceeds the16.667ms target by5.441ms. All-recorded max frame delta400ms is engine-clamped, not an upper bound on wall-time stalls;16frames exceed50ms. GT max341.799ms, RT max32.997ms and GPU max27.381ms. Four assembly-capture spikes reached359.670ms frame delta; return-to-gameplay includes the400ms screenshot-associated spike. Therefore this is not clean60FPS acceptance, even though the aggregate p95 happens to be near the target. The failed first sample is retained:80.927s/6434rows, all-recorded p95=17.837ms, assembly p95=21.578ms, return p95=21.976ms. No results were discarded to manufacture a faster benchmark. Phase02 combat p95=19.261ms remains historical evidence; different route duration/cache/conditions prevent claiming a causal improvement from Phase03.

Offline Unreal Insights exit0:437,559,051-byte trace,74CPUthreads,49,872,313CPUscopes. Visible CPU costs attributable to the new presentation are below. These are inclusive per-invocation statistics, not per-frame budgets; nested scopes overlap and must not be summed. The export also includes default GPU aggregate rows; only named CPU scopes are used here.

| CPU scope | Calls | Total ms | Mean ms | Max ms |
| --- | ---: | ---: | ---: | ---: |
| CR_WeaponPresentation |13588|93.831|0.007|0.876|
| USkeletalMeshComponent_TickAnimation |1603|72.743|0.045|0.208|
| AnimSequencerInstance |3178|65.581|0.021|0.202|
| MovieScene GameThread_UpdateSequenceInstances |1590|15.395|0.010|0.182|
| FSkeletalMeshUpdater::ProcessUpload |1594|27.051|0.017|0.070|
| AudioMixerSource::Init (all game sources) |79|2.560|0.032|0.153|

These scopes show actual skeletal/Sequencer execution without a large measured GT cost. Assembly RT/GPU p95 is higher than ordinary traversal. That observation motivates a future same-camera render comparison; it does not isolate the incremental GPU cost of each new mesh/material or the original audio cue. There is no disabled-content A/B measurement, so no separate per-material/audio performance guarantee. PNG compression ran16times,total3366.704ms,max333.501ms; this supports capture instrumentation as a contributor to the large GT spikes. It does not prove every hitch has that cause. No unrelated optimization was performed.

Peak working set1,863,364,608B(1.735GiB), private commit4,530,450,432B(4.219GiB). Samples: bench entry17.128s=1,818,439,680/4,520,050,688B; assembly22.174s=1,824,280,576/4,530,450,432B; post-reload51.390s=1,832,972,288/4,271,542,272B; return to Yard76.572s=1,745,321,984/4,181,856,256B; reloaded Workshop86.644s=1,736,302,592/4,172,029,952B (working set/commit). Final pre-restart182.782s=1,772,470,272/4,228,411,392B. No monotonic memory-growth pattern appears in this bounded sample, but different resident zones/restarts and allocator caching prevent a leak-free claim. These are process measurements, not dedicated VRAM or per-asset residency. Normal scripted unloads: A5/B6/C2, independently of3Restart travels; no forced GC per transition.

Analyzer limits:30,667MemAlloc TagTracker errors with partial trace channels,4LoadTime warnings, GPU interleaved/reversed/negative-duration warnings(max0.252ms). Do not use this capture for allocation or reconstructed GPU-event claims; GPU table uses the native RHI frame counter. Runtime had no Error/Fatal/Ensure; expected deliberate cancellation and existing Recast teardown warnings remain. First-run startup commands also warn about execution time. Full settings, both receipts, CSVs, command lines, first-failed.utrace, restoration.utrace and Insights exports stay under ignored `.environment-local/phase-03/`. No further run was used to chase numbers.
