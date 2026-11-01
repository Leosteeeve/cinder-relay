# CINDER RELAY — Performance Budget

## Phase05.4 measured integration sample, 2026-11-01

Paired unchanged Phase053 and candidate Phase054 packages ran once each through three independent native processes. RTX5070 Laptop8GB,32GB RAM;1920x1080, Epic quality3, ScreenPercentage100, DynamicRes0, VSync0, MaxFPS0. No frame generation, recording, requested allocation trace, Editor or Blender during the primary sample. Enhanced Input route instrumentation, previous-frame engine counters,1Hz process sampler and one final receipt screenshot remain overhead. Desktop activity, temperature and power were not controlled; caches were not cleared. Lower observed numbers are not proof of an optimization caused by this patch.

| Sample | Frames | Before p95 ms | After p50 / p95 / p99 ms | GT / RT / GPU p95 ms | >50ms |
|---|---:|---:|---|---|---:|
| Combat | 239 | 17.138 | 13.105 / 15.299 / 16.260 | 2.354 / 15.301 / 13.812 | 0 |
| Yard traversal | 436 | 18.534 | 14.051 / 17.804 / 19.109 | 2.897 / 17.805 / 16.468 | 0 |
| Slide and hip fire | 60 | n/a | 12.373 / 20.423 / 23.702 | 8.643 / 20.797 / 19.011 | 0 |
| Reload after slide | 208 | n/a | 12.080 / 15.835 / 17.181 | 1.996 / 15.800 / 14.487 | 0 |
| Workshop assembly | 1324 | 23.382 | 17.384 / 18.737 / 19.524 | 2.124 / 18.736 / 17.132 | 0 |
| Workshop movement | 1337 | 21.982 | 16.156 / 20.028 / 28.169 | 6.313 / 19.570 / 16.880 | 0 |
| Bunker | 2405 | 23.828 | 15.596 / 17.651 / 21.047 | 3.696 / 17.614 / 15.918 | 1 |
| Streaming traversal | 2716 | 20.613 | 15.426 / 18.814 / 24.575 | 4.601 / 18.779 / 16.906 | 3 |

The slide sample contains only60 frames. Workshop assembly p95 remains2.070ms above16.667ms and slide p95 exceeds it by3.756ms; this is not a stable60FPS result. RT/GPU intervals are observations, not additive costs or a causal diagnosis. Source code changes did not reduce global quality.

Five distinct >50ms frames in the entire candidate route CSV:79.120ms during initial CP00 readiness,60.123ms in low-speed crouch setup before the actual slide, then57.673/59.864/51.080ms during route3 walking/backtracking. None occurred inside the measured slide/reload/assembly subsets. The latter walking samples show RT58.789/59.964/50.648ms; startup and rendering/travel remain investigation candidates, not established causes. No speculative optimization or repeated cache clearing was performed.

| Process | Peak working set bytes | Peak private commit bytes | Safe-control reconstruction |
|---|---:|---:|---|
| Route1 |1,951,567,872|4,368,359,424|47.021ms,1 event|
| Route2 |1,956,782,080|4,446,035,968|p50 44.247/max99.119ms,7 events|
| Route3 |1,915,146,240|4,414,570,496|p50 44.821/max78.937ms,6 events|

Successful save callback maxima:17.471/15.228/15.443ms by route. Safe-control timings measure in-engine bootstrap/reconstruction, not OS process launch. Native A/B/C unload counts: route1=0/0/0, route2=11/0/6, route3=1/5/1. No leak or VRAM claim follows from these small process-memory samples.

Asset increment: six original meshes,19,772 source triangles total,40 zone-owned decorative actors, two bounded nonshadow local lights and existing-material grime decals. No new texture files or render features. Existing texture residency can still change with added visibility; incremental GPU memory was not isolated. All gameplay collision/navigation and338 old actors remained unchanged.

The primary sample precedes a final noncolliding support-position correction (ramp slope, hanger contact and two bunker placements), with identical mesh/material/actor counts and gameplay code. The final content receives a focused cook and recorded route rather than silently replacing or repeating the entire benchmark. Final video is separate, includes capture overhead and is not performance evidence. Raw receipts: `.environment-local/phase-05-4/{baseline-performance,packaged-acceptance}/SavedPhase04`, `performance-comparison.json`, `performance-table.md`. `Scripts/summarize_combat_environment.py` reproduces the comparison from those sealed CSVs.

## Phase053 integrated packaged comparison, 2026-11-01

One unchanged Phase052 baseline and one integrated Phase053 three-process suite used the same1080p/Epic/native input routes, ScreenPercentage100, DynamicRes0, VSync0 and MaxFPS0. No frame generation, allocation trace, continuous screenshot capture, Editor or Blender ran in the primary samples. Input automation, lifecycle fault checks, one final receipt screenshot and1Hz process-memory sampling remain overhead. OS/driver caches were not cleared; thermal/desktop conditions were not controlled. Frame percentiles are median/nearest-rank, counters are not additive, and held startup/menu/controlled map travel are excluded from CSV. This is a bounded engineering sample, not a guaranteed60FPS benchmark.

| Sample | Before frames | Before frame p50/p95/p99 ms | After frames | After frame p50/p95/p99 ms |
|---|---:|---|---:|---|
| Route1 / CP01 acquisition |915|12.991 /16.733 /19.368|865|13.649 /17.080 /19.879|
| Route2 / CP01 restore, lifecycle, assembly, CP02 |4405|15.248 /17.660 /19.879|4238|15.838 /18.133 /21.811|
| Assembly subset |1452|15.844 /17.057 /17.639|1387|16.592 /17.678 /18.138|
| Route3 / recovery, backtracking, endings |5303|14.337 /16.445 /21.343|4799|15.556 /18.979 /24.402|

Assembly GT/RT/GPU p95 changed from2.689/17.041/15.591ms to1.854/17.647/16.218ms. Frame p95 increased0.620ms (3.64%); it remains1.011ms above16.667ms. This is not an optimization or a clean60FPS result. The assembly source uses92,165 triangles including existing weapon/optic; gameplay arms33,121 triangles,3 slots,2×2K maps,56 imported bones. Seventeen Gameplay assets occupy11,891,373 source uasset bytes and four Assembly assets16,809,475 bytes before the final single-clip framing correction. These file sizes are not runtime texture/VRAM residency.

Primary >50ms frames increased from2 to9: route1 one121.997ms startup-ready frame; route2 three rows400.000/96.671/53.686ms during first Workshop traversal/module approach; route3 five88.793/54.398/55.043/67.896/50.077ms recovery/walk/ending frames. **The route delta caps at400ms; the next route2 row records previous Game Thread2214.954ms. Do not report400ms as the true worst wall-clock stall.** No exact cause is established. A separate warm CPU/GPU/frame/loadtime Insights route failed to reproduce the primary >50ms gameplay interval; no cache was cleared or speculative optimization applied.

Native Insights timer export over3–40s observed `CR_WeaponPresentation`2192 events: average0.006ms/max0.097ms; `CRWeaponAnimInstance`4382: average0.019ms/max0.250ms; all `USkeletalMeshComponent_CompleteParallelAnimationEvaluation`3574: average0.014ms/max0.171ms. These named scopes are not total animation CPU/GPU cost. Trace-wide maxima include ConsoleVariableSinks319.725ms and EngineLoop326.378ms during startup/configuration, not proof of the same primary stall. Inference: the sampled animation scopes alone do not explain the large first-use stall. The one bounded diagnostic game reached its successful CP02 receipt but Windows returned777003 despite native requested exit0; primary three processes all returned0. Keep the unresolved diagnostic exit issue separate.

| After process | Peak working set bytes | Peak private commit bytes | Safe-control reconstruction range/sample |
|---|---:|---:|---|
| Route1 |1,893,761,024|4,377,309,184|58.915ms,1 event|
| Route2 |1,885,470,720|4,382,224,384|p50 34.321ms / max42.323ms,7 events|
| Route3 |1,857,077,248|4,435,148,800|p50 67.802ms / max219.018ms,6 events|

Native successful save callback samples were13.427ms median/15.495ms max(route1),14.134ms(route2),14.279ms median/14.816ms max(route3). Small samples are not population estimates. No increasing-leak conclusion or dedicated-VRAM reading is inferred from process memory. Texture residency was not separately captured. First-shot/cycle/reload/ADS correctness has focused evidence; isolated low-overhead per-action timing attribution remains unmeasured.

Evidence: ignored `.environment-local/phase-05-3/{baseline,packaged-acceptance}/polish-summary.json` and archived SavedPhase04, process receipts, `first-use-diagnostic.utrace`, native `first-use-timers.csv`, `primary-acceptance-exe.json`. The principal accepted executable SHA256 is A3348A46175046EC76E5FFB1D91016794E1B76FFEEC7227469D3732534F35111. A subsequent opt-in Development recording route and one Reload-only framing edit received focused validation; they were not used to silently replace the primary performance sample. Continuous video has recording overhead and is not a benchmark.

### Historical pre-integration baseline

One baseline suite used the unchanged Phase05.2 Development package,1080p/Epic/native, ScreenPercentage100, DynamicRes0, VSync0, MaxFPS0 and dedicated `CR04_TEST_Phase053Baseline` saves. No Editor/Blender/capture ran concurrently; existing input-route and frame-counter instrumentation remain overhead. No requested allocation/Insights trace; one final receipt screenshot per process. Three route acceptances and all launcher/native exits passed0. This is **not** a Phase05.3 arm-runtime benchmark.

| Recorded sample | Frames | Frame p50/p95/p99 ms | GT p95 ms | RT p95 ms | GPU p95 ms |
|---|---:|---|---:|---:|---:|
| Route1 |915|12.991 /16.733 /19.368|5.878|16.681|15.415|
| Route2 |4405|15.248 /17.660 /19.879|2.730|17.544|16.343|
| Route2 assembly subset |1452|15.844 /17.057 /17.639|2.689|17.041|15.591|
| Route3 |5303|14.337 /16.445 /21.343|3.148|16.406|14.890|

Assembly p95 remains0.391ms above16.667ms. Historical Phase05.2 p95 was19.538ms, but identical assets in a later uncontrolled thermal/desktop session cannot prove an optimization. Route1 maximum71.052ms and route3 maximum55.141ms show remaining spikes; route2 maximum39.192ms. CSV excludes menu/held bootstrap/controlled map travel; counters are not additive. Peak process working set/private commit bytes respectively: route1 1,830,137,856/4,332,101,632; route2 1,897,676,800/4,525,187,072; route3 1,861,795,840/4,422,926,336. These are not dedicated VRAM or proof of leak freedom.

At this historical checkpoint the review-only arms had33,999 source triangles,3 slots,49 deform bones and2×2048 atlases; runtime was not integrated yet. The integrated comparison above supersedes that limitation. Preserve the original baseline; do not substitute Editor capture timing. Evidence: `.environment-local/phase-05-3/baseline/{process-results.json,polish-summary.json,SavedPhase04/}`. Full conditions/known failures are recorded in [the active report](FIRST_PERSON_05_3.md).

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

## Phase04 measurement policy

Keep the Phase03 reference unchanged:1920x1080, Epic scalability3, ScreenPercentage100, dynamic resolution0, VSync0 and MaxFPS0 for instrumented comparison. Phase03 assembly p95=22.108ms is a previous traced sample, not a proven60FPS baseline. Phase04 logs native serialize/dispatch duration, actual async save callback latency, two-slot read latency, target-zone readiness, and GameMode safe-control reconstruction time. The Development route records frame/GT/RT/native GPU counters and process working set/private commit; repeated checkpoint reloads are bounded to three cycles. Allocation/asset/VRAM leak freedom is not inferred from process residency. No cache clearing, forced GC per transition, quality reduction or unrelated rendering changes are authorized.

Final Windows results are appended after the real packaged routes. Editor-game data verifies state/control only; it is not the packaged hardware performance result. CPU/GPU/frame/bookmark/loadtime tracing and injected lifecycle faults introduce overhead, and whole-map recovery differs from ordinary gate streaming.

## Phase04 packaged checkpoint observations — 2026-10-31

One final Windows Development BuildCookRun; three fresh processes, dedicated test saves and cpu,gpu,frame,bookmark,loadtime traces. Same RTX5070 Laptop/32GB, NVIDIA616.92, requested1920x1080 window with ForceRes, ScreenPercentage100, DynamicRes0, VSync0, t.MaxFPS0, all ten scalability groups3/Epic. Native settings receipts confirm those console values. No quality reduction, DDC clearing or forced per-transition GC. Desktop background/power/thermal/cache conditions were not controlled as an A/B benchmark. Lifecycle fault injection, pause and automation are part of this acceptance run.

| Recorded gameplay segment | Rows | Frame p95 ms | GT p95 ms | RT p95 ms | GPU p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| Process1: new game/combat/CP01 |1109|14.3535|1.6968|14.3894|13.4004|
| Process2: CP01/lifecycle/assembly/CP02 |4708|16.7568|2.2888|16.6826|15.5326|
| Process3: CP02/recovery/backtracking/endings |4871|15.1928|2.8108|15.1668|13.7416|
| Process2 assembly stage |1497|16.5544|2.1032|16.5328|15.2882|

These CSV counters are previous-frame native measurements; do not sum GT/RT/GPU. CSV recording excludes the cold menu, held bootstrap and portions of map travel. Percentile uses sorted[floor((n-1)*0.95)]; sparse save events are reported as a range rather than a meaningful p95. The smaller assembly p95 compared with Phase03's22.108ms is not an isolated performance improvement: route, lifecycle, cache and capture conditions differ. This is not a clean60FPS or future final-art claim.

Five successful writes: native serialization/dispatch log time0.127–0.176ms; request-to-success callback9.160–13.461ms. Route3's CR04_SerializeCheckpoint CPU scope is2calls,total0.148ms,max0.076ms; that scope covers a narrower interval than the surrounding dispatch log. Menu/save-window samples are sparse; no causal per-write hitch estimate is claimed. Route3 native scan latency median10.643ms across5reads, max426.095ms at initial process startup; async callback timing includes scheduling/startup, not pure device I/O.

InitGame-to-first-safe-control reconstruction is24.629–133.707ms across all releases; it includes required native streaming/readiness and anchor/spawn checks, but excludes earlier persistent-map loading. Process start to first safe player-control log is3959.902ms /3726.958ms /5458.246ms for routes1/2/3, including startup/menu handler selection. Three CP02 recovery cycles measured32.900/25.456/24.629ms, each restored health76/magazine5/reserve30/upgrade1. These short reconstructions must not hide the surrounding travel hitches below.

One offline Unreal Insights analysis of route3 completed, exit0. Game Frames export covers4897frames, p95=15.2415ms, max646.4917ms,8frames>50ms. Largest frame is startup646.492ms; first Continue/persistent-map travel218.041ms; final exit135.959ms. Frames coinciding with Restart/recovery include68.444/60.662/56.163/53.763/52.191ms. Timestamp coincidence is not exclusive causal attribution. These hitches are absent from parts of the gameplay CSV and remain visible in the trace. GT FlushAsyncLoading has96calls,max329.393ms across startup and controlled travel; this does not mean normal zone transitions switched to blocking loads. ConditionalCollectGarbage max23.177ms; engine full-GC scopes12calls,total8.005ms,max3.853ms. No unrelated performance rewrite was attempted.

| Process | Peak working set bytes | Peak private commit bytes |
| --- | ---: | ---: |
| 1 |1808613376|4453691392|
| 2 |1782394880|4454256640|
| 3 |1794392064|4363665408|

Route3 working/private at the earlier death stage=1769803776/4261679104B; first1Hz sample after the three quick recoveries=1765851136/4358971392B; final walk=1781391360/4192153600B. Sampling cannot resolve each sub-second cycle; different active zones and caches affect residency. No unbounded trend was established by this bounded sample, and no leak-free claim follows. Native logs record A/B/C unloading1/5/1 times in route3; these events and restored stable IDs are stronger evidence than unchanged GPU allocation. Working set/commit are not dedicated VRAM or an asset-residency sum. No allocation-level retained-reference analysis is claimed.

Analyzer limits:30675 MemAllocTagTracker errors from the partial-channel trace,4LoadTime warnings, GPU ordering warnings (up to0.099ms) and one pending RHI command list at close. Memory-allocation reconstruction and affected GPU event timing are not used. GPU values above are native RHI frame counters; maximum route3 GPU counter68.0282ms. Runtime packaged logs have no Error/Fatal/Ensure matches; expected abort/teardown warnings remain. Automated OS process exit777003 is unresolved even for direct native launch, independently of successful gameplay receipts and AutomationTool exit0. A separate interactive UI run without route/unattended/trace flags exited0; it is outside these measurements and does not identify which condition caused the discrepancy.

Evidence: .environment-local/phase-04/{packaged-summary.json,process-results.json,packaged-route1.log,packaged-route2.log,packaged-route3.log,route3.utrace,insights-game-thread.csv,insights-frames.csv}; native Saved/Phase04/{1,2,3}/{frames.csv,memory.csv,settings.txt,acceptance.json}. Keep raw traces/packages ignored. Reanalyze existing traces before considering another run; a future same-quality performance experiment requires a concrete question.

## Phase05 packaged observations — 2026-10-31

One Windows Development BuildCookRun141.84s, AutomationTool0. One bounded three-process acceptance at1920x1080, all ten quality groups3/Epic, ScreenPercentage100, DynamicRes0, VSync0, t.MaxFPS0; RTX5070Laptop,32GB RAM, NVIDIA616.92. Existing TSR/Lumen/ray-tracing settings retained; no frame generation or silent quality reduction. No Editor/Blender render ran concurrently. Power/temperature/background desktop applications were not controlled.

`-LowOverhead` omitted requested Insights/allocation tracing. Existing native route counters and1Hz process memory remain; input automation, lifecycle fault injection and pause are overhead. Only one final screenshot per process, after receipt creation. Median p50 and nearest-rank p95/p99 are reported. Engine GT/RT/GPU counters refer to previous frames and are not additive.

| Sample | Frames | Frame p50 ms | p95 ms | p99 ms | GT p95 ms | RT p95 ms | GPU p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rail Yard combat/approach | 945 | 11.585 | 15.625 | 17.372 | 2.352 | 15.622 | 14.469 |
| Workshop full assembly | 1544 | 14.884 | 15.896 | 16.311 | 1.839 | 15.886 | 14.588 |
| Relay Bunker | 2493 | 14.979 | 17.988 | 21.579 | 3.808 | 17.962 | 15.328 |
| Streaming/backtracking traversal | 2905 | 14.473 | 18.242 | 22.377 | 4.114 | 18.117 | 15.475 |
| Route3 all recorded | 5426 | 14.206 | 17.701 | 20.758 | 3.970 | 17.621 | 14.841 |

Route3 p95=17.694ms exceeds the16.667ms goal by1.027ms (~6.2%). This is not a clean60FPS guarantee. Assembly p95=15.891ms is a useful observed sample, but cannot establish an art-only improvement over Phase03's traced22.108ms because trace overhead/content/test conditions differ. No clean same-content A/B or per-feature mesh/material/audio cost isolation was performed. RT/GPU dominate the assembly sample; traversal also has higher GT tails. These observations do not justify a renderer/streaming rewrite.

There were0 recorded gameplay-frame deltas above50ms across11,020 CSV rows; maximum29.782ms. This excludes menu, held bootstrap and controlled map reload. Native LoadMap logs show38.685–99.894ms synchronous travel work; most travel samples exceed50ms and remain visible hitch risk. A bounded log investigation locates this outside the normal streamed traversal CSV, in intentional persistent-map reload during recovery/restart. First safe-control reconstruction: fresh CP00=198.777ms, cross-process CP01=157.211ms, CP02=127.043ms; warm CP02 recoveries79.775/49.619/41.320ms. These timings start at native bootstrap, not OS launch or first rendered input frame; do not add them blindly to LoadMap. Full end-to-end visible hitch attribution remains unverified without a focused trace. No cache clearing or repeated benchmark was used.

Native save dispatch0.126–0.316ms; successful callbacks8.247–16.242ms (five writes). These small samples are not population percentiles. Actual separate processes restored CP01 health68/magazine1/reserve35 and CP02 health68/magazine5/reserve30/upgrade1. Native readiness and collision gating held the pawn before release.

| Process route | Peak working set MiB | Peak private commit MiB | Actual native unloaded events |
|---|---:|---:|---|
| 1 | 1744.6 | 4160.4 | {'A': 0, 'B': 0, 'C': 0} |
| 2 | 1781.1 | 4310.7 | {'A': 11, 'B': 0, 'C': 6} |
| 3 | 1728.7 | 4124.8 | {'A': 1, 'B': 5, 'C': 1} |

One-Hz memory sampling is too coarse to separate the three rapid CP02 recovery cycles; bounded peak residency is reported without a no-leak claim. Native unload status, saved actor reconciliation and absence of persistent strong streamed-actor references support residency behavior; unchanged process/GPU allocation would not disprove unload. Dedicated VRAM residency, detailed texture use and long-run growth were not measured. Logs show native texture pool1000MB after initialization; no pool-over-budget warning was found. The8GB hardware target remains a budget, not proof of all future final-art fit.

Evidence (ignored locally): `.environment-local/phase-05/package.log`, `packaged-acceptance/{process-results.json,polish-summary.json,load-latencies.json,packaged-route1.log,packaged-route2.log,packaged-route3.log}`, and `package/Windows/CinderRelay/Saved/Phase04/{1,2,3}/{frames.csv,memory.csv,settings.txt,route.txt,acceptance.json}`. All three native processes exited0; route1 bootstrap also0, no forced stops. Prior777003 was not reproduced without requested traces in this run, but that is correlation, not a proven root-cause fix.

## Phase05.1 packaged observations

UE5.8.4, Windows Development, RTX5070Laptop/32GB, actual viewport1920x1080, Epic3, ScreenPercentage100, DynamicRes0, VSync0, MaxFPS0. Existing TSR/Lumen/hardware-ray-tracing settings retained; no frame generation. One bounded three-process lower-overhead route; no Editor/Blender/recording concurrently. No requested Insights/allocation trace; previous-frame native counters, input/lifecycle automation and1Hz process sampling remain overhead. Power/temperature/background desktop applications were not controlled. Median p50 and nearest-rank p95/p99.

| Sample | Frames | Frame p50 ms | p95 ms | p99 ms | GT p95 ms | RT p95 ms | GPU p95 ms | Phase05 p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Yard combat/skyline approach | 853 | 12.691 | 16.987 | 18.983 | 2.067 | 16.970 | 15.854 | 15.625 |
| Workshop full assembly | 1386 | 16.445 | 18.737 | 20.383 | 3.331 | 18.645 | 16.228 | 15.896 |
| Relay Bunker | 2414 | 15.570 | 17.477 | 20.948 | 3.107 | 17.447 | 15.832 | 17.988 |
| Streaming/backtracking | 2808 | 15.051 | 17.768 | 22.640 | 3.332 | 17.737 | 15.804 | 18.242 |
| Route3 all recorded | 5196 | 14.851 | 17.214 | 20.044 | 3.107 | 17.176 | 15.539 | 17.701 |

Assembly p95=18.737ms exceeds16.667ms by2.070ms and the corresponding Phase05 sample by2.841ms. Yard p95 increased1.362ms; normal traversal decreased0.474ms. These are observed separate runs, not isolated causal measurements of individual materials/meshes. RT/GPU dominate the assembly sample; do not claim native60FPS or start a renderer rewrite. The denser106,828-triangle skeletal presentation and shared2K materials are plausible contributors, not proven exclusive causes.

One recorded gameplay delta exceeded50ms:150.795ms at route1 `wait_cp00` elapsed0.802s; the other two routes had none. Startup/menu/held bootstrap and controlled map reload are not fully present in gameplay CSV. Native LoadMap timings below describe synchronous travel work, not end-to-end player-visible latency. No diagnostic trace was added to manufacture an attribution.

LoadMap samples: 26.845–186.413ms, 14/17 above50ms. Cross-process safe-control reconstruction: CP01=34.160ms and CP02=40.292ms; repeated warm CP02 recoveries34.770/24.950/24.022ms. These start at native bootstrap, not OS process launch, and are not added to LoadMap durations. Correct saved state was CP01 health68, ammo1/35, upgrade0; CP02 health68, ammo5/30, upgrade1.

| Process | Peak working set MiB | Peak private commit MiB | Native unload counts A/B/C |
|---|---:|---:|---|
| 1 | 1721.2 | 4177.5 | 0/0/0 |
| 2 | 1723.7 | 4252.0 | 11/0/6 |
| 3 | 1782.9 | 4291.5 | 1/5/1 |

New source textures: six2048x2048 images, 6,083,958 compressed JPEG bytes; actual native Texture2D dimensions/compression/sRGB verified. New Phase051 uassets total25,524,302 source bytes. These are disk sizes, not resident VRAM. Hero plus optic58,060triangles; eight-piece environment source32,056triangles including19,140-triangle combined eight-tower skyline; new assembly106,828triangles/40importedbones. All22decorations are noncolliding/non-nav; only the combined skyline stays persistent.

Process peak private commit reached4,291.5MiB in route3 (Phase05 corresponding peak4,124.8MiB); process allocation includes pools/cache and does not isolate added art residency. Texture pool stabilized at1000MB, no pool-over-budget warning found in the three logs. Per-texture current residency, dedicated VRAM delta and long-term leak freedom remain unmeasured; six2K source maps are not a measured VRAM figure. No forced GC per transition or cache clearing.

Evidence: `.environment-local/phase-05-1/packaged-acceptance/{process-results.json,polish-summary.json,packaged-route1.log,packaged-route2.log,packaged-route3.log,SavedPhase04/}`. The archived SavedPhase04 copy preserves this performance run when later diagnostic recording reuses receipt paths. All three native exits0, route1 bootstrap0, no forced stops. The older777003 did not recur; no causal fix is claimed. This full route preceded the narrowly reviewed missing-sight fallback correction; final corrected package uses the same assets/normal appearance path, followed by focused native tests and packaged visual checks. No full route rerun was needed for that error-path-only change.

Final corrected package ADS sample: `sight-performance/summary.json`, 961 frames from six2s settled windows, no capture/recording/trace. Frame p50/p95/p99=12.540/13.542/14.028ms; GT/RT/GPU p95=2.184/13.530/11.970ms. Full nine-pose fixture has2 deltas>50ms. No comparable Phase05 ADS fixture was recorded, so no isolated old-versus-new sight cost is claimed.

Those two sight-fixture spikes were55.992ms and56.841ms at elapsed4.537/4.767s, during initial hip-view settling before the measured ADS windows. Their GT/RT/GPU counters were lower than the frame delta; wall scheduling/initial presentation is a hypothesis, not a proven GPU or streaming cause. The28s animation video and Editor comparison captures ran separately and are not benchmark data.

## Phase052 packaged observations

2026-11-01: one Windows Development BuildCookRun99.57s, AutomationTool0. UE5.8.4, RTX5070Laptop/32GB, actual1920x1080 viewport, Epic groups3, ScreenPercentage100, DynamicRes0, VSync0, MaxFPS0; existing TSR/Lumen/ray-tracing configuration retained. No frame generation or quality reduction. No Editor, Blender render or recording ran during the three-process performance route. No requested Insights/allocation trace; native previous-frame counters,1Hz process memory and input/lifecycle automation remain overhead. Thermal/power/background desktop load was not controlled. Median p50 and nearest-rank p95/p99; thread counters are not additive.

| Sample | Frames | Frame p50 ms | p95 ms | p99 ms | GT p95 ms | RT p95 ms | GPU p95 ms | Phase051 p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Yard combat/approach | 865 | 12.651 | 17.077 | 18.736 | 1.894 | 17.137 | 16.061 | 16.987 |
| Workshop full assembly | 1363 | 16.571 | 19.538 | 21.534 | 3.985 | 19.463 | 16.255 | 18.737 |
| Relay Bunker | 2487 | 15.146 | 16.491 | 19.400 | 1.872 | 16.451 | 15.235 | 17.477 |
| Streaming/backtracking | 2829 | 14.797 | 17.133 | 22.324 | 2.860 | 17.083 | 15.629 | 17.768 |
| Route3 all recorded | 5242 | 14.607 | 16.562 | 19.400 | 2.705 | 16.531 | 15.235 | 17.214 |

Assembly p95 is0.801ms higher than the prior sample and2.871ms above the16.667ms goal. Yard p95 increased0.090ms. RT tails dominate assembly, while GPU p95 is16.255ms. These are separate bounded runs, not a controlled causal cost isolation. Camera framing, added light/material work and scheduling are hypotheses; no renderer rewrite or blanket quality reduction follows. Route3 p95 being below budget does not establish sustained60FPS for the chapter.

One of10,491 recorded gameplay frame deltas exceeded50ms:72.181ms at route1 wait_cp00, elapsed0.445s (RT55.855ms, GPU5.264ms). This is early presentation/startup, not proven normal zone-load GPU cost. Other two routes have no recorded>50ms gameplay deltas. CSV excludes much of menu/held bootstrap/controlled travel. Native LoadMap work24.658–161.278ms,15/17 above50ms, remains a recovery/restart hitch risk; it is not total input-visible latency. CP01/CP02 cross-process safe-control reconstruction107.492/55.096ms; three warm CP02 recoveries28.374/24.724/21.922ms. These start at native bootstrap, not OS launch; do not add them blindly to travel timings.

Five native save dispatches0.116–0.303ms and successful callbacks9.848–15.849ms. Small samples are ranges, not population percentiles. Save restoration retained CP01 health68/ammo1+35/upgrade0 and CP02 health68/ammo5+30/upgrade1. Native readiness held the pawn before release. No user saves were modified.

| Route | Peak working set MiB | Peak private commit MiB | Native unload counts A/B/C |
|---|---:|---:|---|
|1|1796.7|4173.6|0/0/0|
|2|1792.4|4324.4|11/0/6|
|3|1755.5|4217.2|1/5/1|

No new texture images; reuse of existing CC0 2K maps and original mask. Eleven new static meshes total61,004 source triangles before instancing; the106,828-triangle assembly retains the previous geometry/bone budget. Thirty-six added actors include four local non-shadowed lights and seven decals. Source asset bytes and process peaks are not measured dedicated VRAM or per-asset residency. Long-run leaks, exact texture residency and isolated per-feature cost remain unmeasured. No pool-over-budget warning was found; no forced transition GC or cache clearing.

Evidence: `.environment-local/phase-05-2/package.log`, `packaged-acceptance/{process-results.json,polish-summary.json,packaged-route1.log,packaged-route2.log,packaged-route3.log,SavedPhase04/}`. A compact public [validation receipt](media/phase-05-2/validation.json) preserves selected metrics. All native and bootstrap exits0, no forced stops; older777003 did not recur, without a claimed causal fix. The first diagnostic recording was obstructed by Windows firewall UI and is excluded from publication. Its successful28s replacement also ran separately; neither recording is included in these performance metrics.
