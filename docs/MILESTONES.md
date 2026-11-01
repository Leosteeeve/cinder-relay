# CINDER RELAY — Milestones

## Phase05.5 identity, interface, audio and Field Pack — integration ledger

Authorized by the owner's2026-11-01 Phase05.5 brief. Baseline `09eaa5fe39beb1c4365220e09fde311e0d3b10fe`; branch `phase-05-5-ui-audio-inventory`; UE5.8.4 CL58902052. [Design, behavior and evidence](INTERFACE_AUDIO_05_5.md). No Phase06 work.

Delivered source includes four-reference UI research, six original dual-resolution mockups, original Blender key art/cover/mark, OFL fonts, real Designer UMG, event-driven HUD, independent audio settings and a read-only Field Pack. Native import produced85new assets. An independent Editor reload passed590asset/reference/sequence-keyframe checks.307protected old file hashes retain304unchanged files; only the three intended audio-reference sublevels differ. Schema/checksum/weapon/animation source assets remain unchanged.

Validation: Editor target builds exit0 after compiler-diagnosed type/name fixes;11focused Automation tests have0failures (one expected-warning case). A native UI route initially exposed a test-state waiting bug; the corrected route passed at1080p and an independent1600p process restored CP00 and all five audio preferences. Actual Slate/input interactions, reload freeze/exactly-once completion, aim/slide cancellation, screenshots and native mixed WAV are recorded locally. Captures prompted bounded title/health/Pack readability corrections.

One final Windows Development BuildCookRun completed in169.31s, exit0. Three fresh candidate checkpoint processes and both normal packaged UI processes returned0 with successful native receipts and no forced stop. A separate real mouse session verified Continue, carried Power Module, category/close, Settings slider/save, Credits and Exit confirmation, exit0. A17.5s1280x720 gameplay video contains the same process's native stereo mix; capture/game/decode exits0. Original failed fullscreen capture and traced shutdown777003 remain explicitly excluded from successful process counts. Fullscreen Slate screenshot size mismatch was avoided with a bounded recording window; no second package was made.307final protected hashes still differ only in the three authorized audio-reference maps.

Performance remains open: primary combat p95 changed15.063→28.762ms; a bounded quiet repeat changed20.427→16.877ms. These variable samples do not isolate a causal regression, prove no first-use hitch or establish60FPS. Slide/movement tails remain. Human artistic, continuous gameplay-feel and stereo-headphone acceptance are pending. No Phase06 work or automatic merge.

Review delivery: implementation commit `149beca`; [Draft PR11](https://github.com/Leosteeeve/cinder-relay/pull/11), feature branch `phase-05-5-ui-audio-inventory` to `main`. LFS upload succeeded; raw local evidence, saves and packages are excluded. Draft status preserves the explicit open acceptance items.

## Phase05.4 — combat feel, slide and curated environment (integrated candidate)

Base PR9 merge811aaa5; scope excludes Phase06 and weapon/arm remodeling. Implementation and exact slide contract are in [COMBAT_ENVIRONMENT_05_4.md](COMBAT_ENVIRONMENT_05_4.md). Initial native Editor compilation72.16s succeeded; focused slide decay automation succeeded; real input route reached CP01 with a0.751s slide, one accepted hip-fire round and conserved reload. A standalone Editor-game shutdown stalled after its successful receipt and requested exit0; the owned process was stopped and is not counted as a successful process exit. The Windows package passed three independent native processes: CP01 acquisition, CP01-to-CP02 restoration/assembly lifecycle, and CP02 recovery/backtracking/death/restart/optional ending. Launcher/native exits were all0. Additional six slide physics/input edge fixtures passed; they used NullRHI and are not visual or performance evidence.

Six original utility meshes (19,772 source triangles), one editable Blender source and40 zone-owned cosmetic actors were created through Blender4.5.11 and UE5.8.4. Wrong-facing tool walls and an opposite ramp-pipe slope found in actual renders were corrected and re-inspected. The final noncolliding support-position correction passed one75.29s content-only cook, then a fresh recorded native route and focused weapon fixture (all exit0).237 of240 protected prior binary/source assets are byte-identical; only the three authorized sublevel map files changed.338 old actor snapshots remained identical after reopening. No source asset deletion, story/schema/ID changes or global quality reduction.


## Phase053 human arms and weapon handling — integrated candidate

Base `6f9dd59100222ecab6e2bdeeaed60c937389ea60`; branch `phase-05-3-first-person-animation`. Owner approved anatomical direction and continuation. Actual CC0-derived human rig, original glove/sleeve atlas, seven handling clips, once-only cosmetic case cues and22s workbench derivative are integrated. The original combat authority, SaveGame schema1, checkpoint IDs and native streaming remain unchanged. Current scoped weapon/sight/native automation checks passed; final packaged/runtime/performance results are maintained in [FIRST_PERSON_05_3.md](FIRST_PERSON_05_3.md).

Actual source quality remains prototype: calibrated baked IK/contact, human finger chains and continuous release rotations are present, while thumb/contact/material/cuff finesse and continuous human aesthetic acceptance remain open. No commercial pack was acquired. The optional game-dev GLB package builder's Windows fsync issue does not block the independent native UE import pipeline. No Phase06 work.

Engineering delivery:3/3 native presentation automation, focused weapon/sight fixtures, real Editor import/evaluation, and all three fresh packaged checkpoint processes passed. Actual native/bootstrap exits0. Final recording-driven Reload-only correction received its own native import and25.93s incremental cook, followed by a genuine-input recorded CP01-to-CP02 route (native/capture0). The46.03s1080p silent local file shows three accepted shots, a full visible reload and the22s workbench; actual capture-average26.89fps, not locked30. Selected12 proof categories remain local. [Compact validation receipt](PHASE053_VALIDATION.json) excludes raw media, save files and traces.

Art/performance acceptance stays open: glove/cuff seams, approximate contact and prototype material quality remain visible. Assembly p95 changed17.057 ->17.678ms in the paired sample; first-use/recovery hitches remain. A separate warm diagnostic trace passed the gameplay receipt but returned native777003; primary routes returned0. No whole-phase artistic completion, clean60FPS or human pacing acceptance is claimed. PR remains draft for review.

## Phase052 presentation and contact polish

Authorized focused revision of Phase05.1, not Phase06. Base merged PR7 `e5d0ef641e99a71b59012e18e5d56880988cdb4b`; branch `phase-05-2-presentation-contact`. Detailed audit/plan/visual comparison: [PRESENTATION_05_2](PRESENTATION_05_2.md). No runtime C++ changes, saved-ID/schema changes or new mechanics.

Delivered assets: two editable Phase052 Blender sources; eleven original static meshes; SK/AN/skeleton derivative; native22s Level Sequence with camera and two original audio tracks; shared PBR instances/decal. Twenty-nine new Unreal assets. Persistent map changes only local exposure settings; RailYard changes cosmetic car assignments and34 added owned actors; Workshop adds2 local fill lights and changes existing bench soft appearance references. Bunker and original Phase01A rollback map untouched. Read-only native audit preserved302 original actors and231 protected-file hashes, all CP00/01/02 transforms and gameplay collisions. New static decorations have no collision/navigation.

Validation performed:

- Real UE5.8.4 FBX import with bounds/bones/duration checks; nine actual skeletal poses and six matched environment views inspected. Native sequence component binding evaluated at6s/19.2s; actual Stop restored original camera transform twice. Audio completion-cache issue fixed through native editor property notification and verified after fresh load.
- One Windows Development BuildCookRun99.57s, AutomationTool0. The game target compiled/linked successfully as part of that pass; no separate Editor-target rebuild was performed because runtime source was unchanged. Explicit Phase052 cook directory included.
- One bounded three-process actual-input acceptance, fresh `CR04_TEST_Phase052Final` slots. Route1 native31440/bootstrap20572 savedCP01; route2 native13768 restoredCP01 and savedCP02; route3 native71388 restoredCP02, recovered/backtracked and reached both endings. All fresh receipts passed, every native/bootstrap exit0, no forced stop. Raw evidence is ignored locally; [compact public receipt](media/phase-05-2/validation.json) records selected results.
- CP01 restores health68/ammo1+35 and prior enemy/pickup/objective state. CP02 restores health68/ammo5+30/SurveyUpgrade1/objectiveRestorePower. Three additional warm CP02 recoveries retain those values. Native loaded/visible readiness veto holds the pawn; old zones actually unload (route3 A/B/C1/5/1).
- Workbench route exercises explicit Skip/exactly-once upgrade, lethal interruption, presentation actor destruction, Restart/world EndPlay, controller destruction, real SequencePlayer Stop without upgrade, rejection of checkpoint requests during playback, pause/freeze/resume and natural completion. Real imported upgraded view and reload remain functional. Reverse streaming preserves collected salvage/upgrade; death Retry and optional-bypass MERIDIAN ending pass. Repeated assertions are not counted as independent gameplay cases.
- Lower-overhead1080p/Epic sample: yard p95=17.077ms, assembly19.538ms, traversal17.133ms; not sustained60FPS. Detailed ranges, memory and startup/travel limitations: [performance report](PERFORMANCE_BUDGET.md#phase052-packaged-observations).

Actual source/assets, static visual review, native runtime tests and human artistic acceptance are distinct. The first diagnostic video was blocked by Windows firewall UI and excluded. After owner dismissal, a separate dedicated test process produced the published28s1280x720/30fps silent gameplay recording:840frames decoded, ten sampled frames inspected, native/capture exits0 and route passed. It includes full assembly and return to gameplay, without changing the measured performance run. No claim of final hand anatomy, natural continuous motion, polished hero surfaces or measured12–16minute pacing. No Phase06 work started.

## Phase05.1 Asset Quality Overhaul — active plan and ledger

**Goal:** materially improve the fictional ROOK-5, actual sight picture, Rail Yard depth and first-person contact animation while retaining Chapter01 gameplay. **Spec:** owner's Phase05.1 sections0–19, especially visual feedbackA–H. **Baseline:** merged PR6 `fd257fbe56768abb7eea007aa547473919ed4b3a`; clean workspace, branch `phase-05-1-asset-quality`; UE5.8.4/CL58902052. No game/Editor process remained at audit.

**Architecture:** new project-owned Phase051 Blender/Unreal derivatives, narrow appearance-only WeaponView changes using native static mesh sight sockets, CC0 surface maps, original zone-owned noncolliding architecture and a small persistent skyline for exterior continuity. Existing weapon component, maps, native streaming, save schema1 and sequence completion authority remain. No new persisted IDs, weapon balance, functional firearm internals, renderer framework, paid provider or Phase06.

**Review focus:** socket import axes/reticle optical center; recoil/cover/reload return-to-aim; cosmetic collision/NavMesh/checkpoint floors; contact/ownership transitions without prop jumps; completion/Skip versus Abort plus cross-process restored appearance. Each is validated by the task below, not by compile success alone.

- [x] A — read source/docs, verify merge/clean branch, inspect prior actual rendered weapon and7s assembly frame; research owner candidates and native UE first-person rendering. `ASSET_SELECTION_05_1.md` records unknown prices/licenses, rejection of unverified marketplace sources, and limited CC0 selections. No marketplace bytes acquired.
- [x] B — `ArtSource/Blender/Phase051/` original hero model and2K PBR input; `Scripts/import_quality.py`; `CRWeaponViewComponent.{h,cpp}` native socket transform solution with fallback; meaningful native alignment test. Verify source/import bounds, UVs, material/triangle cost, both sight axes and four same-location real rendered views at1080p/1600p, standing/crouching, firing/reload/cover. One relevant C++ build after implementation, no gameplay balance change.
- [x] C — `ArtSource/Blender/Phase051/` original architecture kit; `Scripts/place_quality.py` additive owned cosmetic placement with before/after actor snapshots. First improve spawn/railcar view, inspect actual Unreal render, then extend perimeter/trusses/recessed facades. Four matched views use `Scripts/audit_quality.py`; collision/no-nav/ownership audit before map save. No gate/anchor moves or world partition.
- [x] D — separate `CR051_RookRestoration.blend`, connected shaped gloves, thumb/finger proportions, editable IK targets and baked contact/prop ownership. New skeletal import and Level Sequence derivative, preserve22s baseline until justified otherwise. Eight meaningful frames plus actual playback/video if supported. No old-source overwrite or arbitrary timer-based reward.
- [x] E — integrated appearance/assembly/checkpoint/streaming regressions using existing actual-input routes and test slots. One final Windows Development BuildCookRun, bounded multi-process recovery route, separate representative timing samples (ADS/skyline/assembly/transition/CP01/CP02), measured texture/mesh cost. Report p50/p95/p99 and >50ms spikes without lowering Epic/native settings. Review staging/hashes/LFS, coherent commits, push/PR main, no merge.

Ruling: the owner's detailed implementation contract authorizes local authoring/import and bounded tests; implement inline without a redundant design approval round. Keep plan/evidence in existing milestone system. Asset production capability check found Blender4.5.11; paid-provider credentials unavailable and no paid generation requested. Use existing native Blender/UE pipeline rather than changing the project to fit a generic GLB package layout. CC0 downloads are limited, hash-recorded source dependencies; no unknown-license exception.

Ruling: retain22s runtime duration initially so Phase03/04 cue/lifecycle invariants stay intact; improve contact and pose timing within it. A shorter accepted performance remains optional, not a reason to rewrite the sequence state machine.

Evidence root: ignored `.environment-local/phase-05-1/`. Before-image camera transforms/FOV and protected baseline SHA256 roster are captured before mutation. Human artistic acceptance remains open; do not mark this phase complete from asset counts or passing tests.

Owner-authorized media publication follow-up: six selected screenshots and the valid 28-second recording from the delivery report are now copied without alteration into [docs/media/phase-05-1](media/phase-05-1/README.md), with SHA-256 manifest and Git LFS tracking. This explicitly authorized selection supersedes the earlier local-only policy for these seven files. Raw logs, failed captures, packages and test saves remain ignored locally; publication does not close human artistic acceptance.

Git delivery: implementation commits `e8f2f3682e3e7dcf111441d2ada522c4776990c5` and `a1926ca54ca092be45839f4375a7b8376a602c30` pushed to `origin/phase-05-1-asset-quality`;47/47 LFS objects uploaded (52MB). [PR7](https://github.com/Leosteeeve/cinder-relay/pull/7) targets main, OPEN/non-draft; GitHub reported MERGEABLE/CLEAN with no configured status-check results at inspection. No merge or visibility change. Engineering delivery is recorded separately from the outstanding owner visual/motion acceptance.

### Phase05.1 actual implementation and validation

Engineering/content delivery is implemented; owner visual acceptance remains open. The original Chapter01 state, damage/ammo balance and schema1 IDs are unchanged. No Phase06 work.

| Work | Actual output / evidence |
|---|---|
| Research | All owner Fab candidates plus an editable-source FPS animation candidate compared in `ASSET_SELECTION_05_1.md`. Unavailable prices/licenses explicitly unknown. No Fab purchase/download. Six2K Poly Haven JPEG maps acquired under CC0-1.0, publisher size/MD5 and local SHA256 checked; voluntarily credited. |
| Hero source | `ArtSource/Blender/Phase051/CR051_Rook5.blend`: shaped/subdivided stock and fore-end, rounded receiver/barrel, curved guard, exterior fasteners/marking, four practical weapon material slots. 53,240 weapon +4,820 optic =58,060triangles. Actual imported static mesh bounds117.45x6.93x18.57cm; source UVs and2K material channels verified. No functional internals. |
| Sight contract | Native `SightAnchor_Iron`=(-16,0,8.2), `SightAnchor_Optic`=(-13,0,11.6), +X forward; camera-relative inverse transform, authored28cm eye relief on the existing player BP. Native first-person depth scale0.65, FOV follows existing65/60camera. Single camera; no damage/hitscan compensation. Optical reticle is geometry at the lens, not floating HUD. |
| Environment | Eight new original source meshes in `CR051_IndustrialDepth.blend`: curved vault, sawtooth clerestory, damaged varying-height perimeter, silo pair, water tower, chimney, factory hall and combined eight-tower distant district. 22 additive cosmetics:20Yard,1Workshop,1persistent skyline. Corrected actual roof underside visibility before expansion. No collision/nav/interior city. |
| Preservation | `asset-validation.json`:280original actors retain snapshot transforms/collision/tags/materials/zone ownership;29protected old sources/rollback assets retain hashes. Only3existing maps and the existing player BP changed; RelayBunker map untouched. Bench skeletal appearance is an intentional separate soft-reference change. No original binary deletion. |
| Assembly source | `CR051_RookRestoration.blend`, connected rounded gloves/sleeves, deliberate grip poses, two-bone arm IK, editable hand targets/poles, prop-local contact constraints and baked FBX motion.39author bones/40imported bones,106,828triangles. New `SK_CR051_Restoration`, `AN_CR051_RookRestoration`, `LS_CR051_RookRestoration`, actual22s. Original Phase03/05 source and sequence intact. |
| Visual inspections | Four matched environment cameras saved before modification and after expansion. Eight real native bench-camera poses at1.5/3.2/5.6/7.2/10.5/13.7/16.6/20.2s inspected. Final packaged1080p/1600p captures include base/upgraded hip/ADS, crouch, fire recovery, reload recovery, close cover and return-to-ADS. First four share a fixed player location. Actual viewport dimensions verified in native settings/logs. |
| Runtime sights | All nine states passed in both final packaged resolutions; settled lateral socket error0–0.00010cm, base65/upgraded60FOV. Existing wall probe lowers the selected socket8.641cm near cover, then returns to camera center. These fixtures directly invoke the existing upgrade API and reposition for the wall probe; they are visual checks, not normal chapter completion evidence. |
| Compilation | Relevant Editor target success; initial unity C2086 static-name collision fixed by locally renaming the Development combat fixture strings. Final pre-review Editor build39.29s. One review correction build39.61s; no full engine build. Logs retain original failures. |
| Native tests | Initial4native groups passed: Checkpoints.Schema, Checkpoints.DiskFallback, Presentation.SightAlignment, Restoration.Session. After review, Presentation.SightAlignment and newSightFallback passed, exit0. NullRHI tests are not visual/gameplay proof. Existing engine startup self-test diagnostics remain separate. |
| Package | One full BuildCookRun133.53s, AutomationTool0. After the reviewed error-path fix, one targeted `-skipcook` game rebuild/restage85.38s, AutomationTool0; no animation re-cook or repeated full-route loop. Final package path `.environment-local/phase-05-1/package/Windows/`. |
| Normal-input acceptance | Three separate packaged processes using fresh `CR04_TEST_Phase051Final` slots passed. Real Enhanced Input/trace interactions tested combat, CP01/CP02 save+cross-process Continue, module, salvage, full assembly, Pause, Skip, actual Stop, death/actor EndPlay/controller destruction/restart interruptions, duplicate prevention, backtracking, reload, death retry, repeated recovery, both upgraded and optional bypass endings. Native exits0, bootstrap0, no forced stops. Raw receipts/CSV archived under `packaged-acceptance/SavedPhase04/`. |
| Performance |1080p/Epic lower-overhead results and historical comparison in PERFORMANCE_BUDGET. Assembly p95=18.737ms; not stable60FPS. Screenshots/recording are separate diagnostic runs. No texture-pool/renderer downgrade. |

Debugging evidence and bounded corrections:

- Genuine rendered sight screenshots initially raced the next fixture pose; hold the pose through screenshot completion time, then recapture. Earlier windowed1423x889 images were rejected as1080p evidence. Final native viewport is1920x1080/2560x1600.
- Real posed animation inspection found a frozen preview, a right-elbow pole inversion and mixed joined UV layer names. Corrected the actual preview update, authored pole direction/arm reach and commonSurfaceUV respectively. Follow-up contact adjustment modified the derivative poses only, not every asset. The latest support-hand contact height correction was checked in the actual native frame.
- First additional perimeter camera was too close to a wall and yielded unusable comparisons, not proof of world depth. One corrected camera at(700,500,165), pitch15/yaw60/FOV85 produced the inspected `after-perimeter-before.png` / `after-perimeter-after.png`: old wall with empty sky versus broken parapets, water tower and two distant towers. It hides/shows only tagged new cosmetics in memory; no gameplay geometry was moved or saved.
- Diagnostic recording preparation initially selected a later CP01 generation from the final bypass session, which correctly failed the route's expected defeated-enemy state. Replaced that preparation with a fresh actual-input CP01 run in a new Development-only test prefix. No player save was corrupted or modified.

Final independent review found one Important issue: a partial appearance load could leave the new gun on legacy offsets and hide the HUD crosshair. Fixed once: require the complete authored sight pair before replacing the primitive fallback; keep the crosshair for fallback. Added native missing-mesh/socket regression coverage and verified both tests. No additional reviewer pass, architecture rewrite or full chapter rerun. Ruling: focused source diagnosis plus native regression/build is appropriate here; do not incur another full Editor build solely to manufacture a test-first red run. Cost: no recorded native RED run for this isolated guard; the original invalid selection condition is preserved in Git diff/review evidence.

Final review rulings: continuous motion aesthetics and owner taste remain human acceptance items; static frames do not close them. Packaged acceptance and newly added cover stages required their own actual logs, supplied above. No deferred code minors were raised. Keep raw evidence locally rather than deleting this phase's existing evidence directory; it is the reproducibility record, not a temporary skill worktree.

Remaining artistic limits: the new receiver is rounded but still visually simple; iron-sight supports and the optic mount remain stylized, surface wear is relatively uniform, glove/thumb anatomy and rigid cuffs need owner review. The distant district is deliberately low-detail and repeats facade motifs. Existing train cars/ground/facades remain partly Phase05 prototype art. The Workshop clerestory is owned by B and appears with B streaming; skyline continuity is persistent. Neither screenshots nor the automated route establish production quality, natural animation, final pacing or a12–16minute human playthrough.

Actual video evidence: `.environment-local/phase-05-1/assembly-gameplay.mp4`,28s/1280x720, requested30fps silent desktop-compositor recording cropped to the verified game client rectangle. Native game and FFmpeg exited0; fresh CP01 Continue/Stop/full completion/reload/CP02 route passed on the final corrected package. Nine decoded samples inspected across placement, optic handling, release and return to gameplay. This is real sequential game capture, not interpolated screenshots; continuous human aesthetic acceptance is still pending. Hidden-window capture initially lacked a main-window handle; direct GDI window capture then returned a stale frame despite native playback. That rejected clip is retained as `rejected-stale-window-capture.mp4`, never used as animation evidence. One final compositor-capture correction produced the moving frames above. No further capture/test iteration is scheduled.

按验收门槛推进，不在需求／工作量未明时承诺日期。最终切片为 **Chapter 01 — The Dead Station，12–16 分钟**。Phase 00 不自动授权 Phase 01。

## Phase 01A — 当前批准的实施计划（2026-10-31）

本节以用户的新规格替代下表旧 P01／英文提示的范围：这次允许三个相连灰盒区域、基础交互、四步目标和结束画面；不做战斗、武器装配、AI、存档、流送或最终美术。指定分支 `phase-01a-greybox`，保留 CinderRelay 模块。已检查工作区干净，在同一工作目录切到指定 feature branch，避免重复 Unreal 缓存；不在 main 实施。

**架构：** 一个非 WP 地图；CharacterMovement + Enhanced Input；角色内 10 Hz 短距离 visibility trace 与按键时重新校验；一个 Blueprint interface、一个可配置交互 Actor；GameMode 内单一枚举目标状态；原生 UMG widget 与 PlayerController 管暂停／重新开始。Blueprint 负责角色参数、交互类型和 GameMode 资产配置。Editor Python 仅生成资产，不参与运行时。

**执行与验证：** 按当前用户限制，实施后一次 CinderRelayEditor 编译，实际错误才定向修正；一次连续 gameplay smoke。不追加逐任务全量构建或为制造 red/green 而重复启动引擎；同一问题两次修复失败即停止诊断。后续独立只读代码审查；不自动进入 01B 或打包完整游戏。

- [x] 环境审计：clean main、实际 CinderRelay、5.8.4、无既有 gameplay／map；Python commandlet 成功，所需 asset／actor／level API 可用。
- [x] C++：CRCharacter（动作／trace）、CRInteractable（接口）、CRInteractionActor（module／relay／signal）、CRWorkshopTrigger（到达工坊）、CRGameMode（单目标状态）、CRPlayerController（UI／暂停）、CRHUDWidget（原生 UMG）。Build.cs 仅增加 UMG／Slate 需要的依赖。
- [x] 编辑器生成：`CinderRelay/Scripts/generate_greybox.py`，专属 `/Game/Generated/Phase01A` 路径；带所有权标记的材质、Input Actions／Context、Blueprint defaults 与 L_CH01_Greybox。重跑复用稳定名称；不删除非本脚本对象，冲突时拒绝覆盖。保留生成 receipt。
- [x] 自动验证：两次相关编译成功；真实地图保存；Enhanced Input 驱动碰撞／坡道／暂停与四目标流程，早用／越距／重复交互拒绝，结束及重开通过。人工键鼠、额外遮挡布置／低顶站起边界和主观手感仍待验收，详见实际记录。
- [x] 更新现有 README／技术／流送／资产／验证与决策文档；审查代码、暂存内容和 25 个 LFS 资产。交付分支为 `phase-01a-greybox`，提交／推送结果以最终报告及 Git 远端 SHA 核对为准。

工程默认（可在 Blueprint 调整）：walk 300 cm/s、sprint 500、crouch 160；capsule 半高 96／蹲姿 60 cm，交互距离 250 cm；镜头无 head bob。WASD／鼠标、Shift 按住跑、Ctrl 按住蹲、Space 跳、E 交互、Esc 暂停与释放鼠标。四个目标文本遵循用户原文，结束为 MERIDIAN NETWORK / CONNECTION RESTORED。

实现时关注：暂停释放按键不留 sprint 状态；低顶阻止站起；trace 遮挡；module 重复领取；生成器重跑保留用户添加内容。02 阶段以后不由这次授权启动。

| 阶段 | 交付物 | 依赖 | 接受标准 | 验证方式 | 非目标 |
| --- | --- | --- | --- | --- | --- |
| P00 已完成 | 原生 Blank C++ 工程、Git/LFS、GitHub、八份核心文档、审计记录 | 已安装 UE 5.8、GitHub 可用授权 | 真正 `.uproject`／模块；基线编译证据；main 与远端 SHA 一致；无秘密／生成缓存入库 | 文件／配置检查、一次 baseline 与实际配置变更所需的定向编译、staged diff、远端查询 | 不实现玩法或第一章地图 |
| P01A 当前 | 三连通灰盒、第一人称控制、交互／四目标、UMG、真实生成资产 | P00；本轮用户批准规格 | 见本节合同与实际验证记录，不用编译代替玩法验收 | 一次初始编译、实际发现的定向修正、一次有界地图流程 | 无战斗、AI、装配、存档、streaming、最终美术 |
| P01B 待批准 | 按既定边界拆分原生 Level Streaming、预载／卸载与 packaged 验证 | P01A 人工接受、回访规则、代表性资源预算 | 初入／返回／反复触发不穿地或重复叙事；cook 引用完整；测量重叠峰值 | 定向编译／Functional 检查、一次短人工转换、规定内存采样 | 无 WP、自制框架、combat 或章节扩展 |
| P02 完整战斗遭遇 | 一个主要武器、一种敌人行为、命中／死亡／重试及基本动画音频 | P01；确认敌人／武器／伤害规则、合规资产 | 单次 3–5 分钟遭遇可完成和失败重试；射击、换弹等批准动作反馈一致；无状态卡死 | 定向规则测试、一次短人工遭遇验收、代表性 combat trace | 无多人、武器海、复杂技能树／潜行体系 |
| P03 回收、修复与叙事 | 少量回收点、一条武器恢复／装配流程、一次可读叙事、一项环境交互 | P02；明确修复步骤／动画资源及本章目标 | 缺材料／完成／取消状态正确；动画结束恢复控制；同一事件不重复发奖；字幕可读 | 针对状态的检查、一次短人工完整流程 | 无完整背包经济、任意零件物理拼装、完整科技树 |
| P04 checkpoint 与整合 | 复用 P01B 流送，增加 SaveGame 恢复与跨区状态整合 | P03、P01B；回访规则、资产预算 | packaged 三分区连通；首次／回头／恢复／失败注入可靠；重叠峰值达批准预算 | 一次相关编译、定向 Functional Tests、一次短人工转换、规定的 3 往返内存采样 | 无 WP 迁移、自制 streaming 框架、多章节扩展 |
| P05 精修垂直切片 | 12–16 分钟可玩开始与结尾、叙事／战斗／维修一致性、基本设置／credits、可复现 benchmark | P04；确认节拍和资产权利；所有关键阻断关闭 | 一次完整人工流程通过；checkpoint 重开可恢复；关键音画缺陷关闭；预算测量及来源清单可追溯 | 定向回归、打包验证、一次完整人工验收、固定路线 3 轮性能记录 | 不扩张游戏规模或以加功能替代打磨 |

## Phase 01A 实际验证记录 — 2026-10-31

实现及自动流程通过；人工体验接受仍待用户试玩。不是 12–16 分钟垂直切片完成，也不是 packaged 或性能验收。

| 检查 | 实际结果与本地证据 |
| --- | --- |
| 环境 | `D:\Projects\FPS Game\CinderRelay\CinderRelay.uproject`；保留 CinderRelay 模块；clean main `4abe9c5a0a0c187832314eb06802ff0066f90438` 起分支 `phase-01a-greybox`；UE 5.8.4 CL 58902052 |
| 初始实现编译 | CinderRelayEditor / Win64 / Development；UBT exit 0，Succeeded，87.44 s；`.environment-local/phase-01a/build-01.log` |
| 定向修正编译 | 审查发现输入 context 需要覆盖 possession 生命周期；增加 PawnClientRestart；exit 0，Succeeded，20.95 s；`build-02-input-lifecycle.log`。两次均 MSVC 14.50.35739，UBT 选择 SDK 10.0.22621.0；没有引擎全量编译 |
| Editor 资产生成 | 真实 `.umap` + 24 `.uasset`：8 材质、10 actions、1 context、5 Blueprints。155 个稳定命名 Actor、10 个 mappings、非 WP。首次成功及专门幂等重跑的 commandlet 均 exit 0；之后修正旋转并由当前 Editor 保存，仍为 155，`new_assets=[]` |
| 运行验收 | 最终 rendering PIE smoke **PASS / 11 checks**，66.41 s（含约 20 s 结束截图停留，不是体验时长或性能数字）；`Saved/Phase01A/smoke.json` 与 `.environment-local/phase-01a/gameplay-smoke_2.log` 的 `CR_SMOKE_PASS` |
| 实际可玩闭环 | 原生 CharacterMovement 从 yard 走到 workshop，E 取 module，走坡道下降约 600 cm，E 激活 relay／signal，目标按序 0→1→2→3→4，结束暂停菜单，Restart 后重新可移动。没有 teleport 或直接设置目标状态 |
| 输入／防护 | action yaw、蹲下 capsule 60 cm／站回 96 cm、跳跃上升 81.6 cm、暂停不移动／释放鼠标／清除 sprint、后墙阻挡、过早／越距与重复交互拒绝。通过注入 Enhanced Input，非物理键盘全键位验收 |
| 画面 | 实际查看 yard／workshop／bunker 原生截图与 Editor HUD；`.environment-local/phase-01a/ending-ui.png` 确认 MERIDIAN NETWORK / CONNECTION RESTORED 和 Restart／Exit 按钮；`yard-ui.png` 确认重开后的目标。截图不替代连续人工验收 |

最终地图 SHA256：`C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733`。PASS receipt SHA256：`E9BDD6AF687E49992DB2C09A09A580203B52592A4D14B24D338776255073703C`。原始日志、receipt 和截图保留本地并被 Git 忽略；本表为入库摘要。

Git 交付：实现提交 `37326ff1ab96d30559f7a942c6fe62571ca3dd5c` 已推送 `origin/phase-01a-greybox`，25/25 LFS 对象上传成功，远端 SHA 与本地一致。最终 `gh repo view` 显示仓库为 **PUBLIC**，与 Phase 00 历史记录不同；本轮未更改可见性或其他设置，只补充文档纠正当前状态。最终文档补充提交以该分支 HEAD 为准，main 未合并。

实际调试记录（不是声称所有步骤一次通过）：

- Editor Python 的 Key 初始化、DirectionalLight 组件访问与 internal-only subsystem getter 不同于假设；按本机反射／源码修正具体 API。初次中断创建的空 map 按已记录 hash 和空内容恢复 ownership，此后立即保存 ownership checkpoint。
- 后台首帧晚于动作处理，造成测试的蹲姿计时误判；改成游戏时间加最少帧数。临时关闭后台 throttle 并在 finish 恢复，不保存全局配置。
- 第一次走动流程超时后读取真实 `Rotator(1,2,3)` 得到 pitch=2／yaw=3／roll=1，确认 Python 位置参数顺序问题；生成器和导航改为命名轴，修正坡道与标牌。原生截图会泵 Slate，增加测试回调重入保护。随后上述完整流程通过。
- 同工程的重复测试 Editor 导致资产保存 Error 32；确认命令行后正常关闭本轮多余实例，保存成功。不要在同工程多个 Editor 中同时生成资产。
- 没有通过反复全量构建、清缓存或架构改写处理这些问题。修正后的有界流程通过后停止测试。

已知限制与一次人工接受清单：

- 工坊入口偏亮，标牌、曝光及移动手感尚需人工调整验收；仅灰盒功能美术，没有动画、音效、战斗、存档或最终叙事演出。
- 普通 PIE 的物理 Esc 会被 Editor StopPlaySession 截获，已实际观察；在 Standalone Game 中确认 Esc 暂停／恢复、鼠标、WASD／Shift／Ctrl／Space／E 和按钮点击。自动测试调用暂停／重开处理器，不能代替这些物理输入检查。
- 按 README 路线做一次短完整试玩，再检查贴墙镜头、低顶站起、遮挡／回访和路线可读性。尚未对每个灰盒碰撞面或所有分辨率进行人工验收。
- Phase 00 已有的 13 条 UnifiedError 附近 `LogAutomationTest: Error: Condition failed` 仍出现在 Editor 启动；未修改引擎，也未声称 clean log。这不等于本项目 smoke 失败，但仍是独立未解决的引擎诊断。
- 未 cook/package，未测 FPS／VRAM／冷加载，当前 shader／PSO 编译日志不能作为稳态性能报告。Phase 01B 前先人工接受，再做原生 Level Streaming 与 packaged 验证。

## Phase 01A 试玩修正：鼠标纵轴（2026-10-31）

用户在 Standalone 试玩发现上下视角反转。根因是 `FSceneViewport::OnMouseMove` 已通过 `MouseDelta.Y -= CursorDelta.Y` 转换屏幕坐标，而 `ACRCharacter::LookPitch` 又取反；当前配置关闭 legacy input scales，生成的 MouseY mapping 没有反向 modifier。仅去掉角色代码中的多余负号，保留灵敏度、水平输入、地图和二进制资产。

在既有 smoke 中补充真实 camera forward Z 的正／负方向检查，`-CRLookOnly` 运行 30 秒以内的专用检查并退出其自身 Editor，支持 NullRHI；不重跑完整路线。

- 修复前，原 DLL 在 `pitch_up` 正确复现失败：camera forward Z = **-0.125333**。
- 修改后一次 CinderRelayEditor 定向编译 **Succeeded / exit 0 / 15.74 s / 4 actions**，记录在 `.environment-local/pitch-fix/build.log`。
- 同一检查 **PASS**：向上 Z = **+0.125333**、向下 Z = **-0.125333**，正 MouseX yaw 增量 **+7.56°**；5 项记录（3 项方向检查，另有初始化和既有无效交互检查），动作阶段 1.31 s，不含 Editor 启动。
- 证据：`.environment-local/pitch-fix/look-before.json`、`look-after.json` 和对应 logs；当前 receipt 为 `CinderRelay/Saved/Phase01A/look-smoke.json`。测试结果以 receipt 的 passed 字段为准，不能仅以 Editor 退出码判断。
- 这是无渲染的 Enhanced Input／相机方向验证，未替用户再次操作物理鼠标或重新进行完整手感验收。现有完整路线证据保持为上文先前 revision 的结果。

## 单任务合同

每个 Codex task 必须列出：目标、允许文件／系统、依赖、交付物、可测接受条件、具体验证、非目标、停止条件。阶段过大则切成仍可运行的子任务，避免一次生成所有类。

C++ 修改后运行相关 target 编译；数据／Blueprint 变化运行对应资源检查。规则测试只覆盖真实风险，地图恢复用 Functional Testing。没有相应测试就诚实说明，不运行不存在的测试前缀后报告通过。

每个里程碑一次短人工玩法验收，P05 为完整 12–16 分钟。定义性能 checkpoint：P01 灰盒、P02 战斗、P04 转换内存、P05 最终包；遵守 [性能协议](PERFORMANCE_BUDGET.md)，不是每次编辑都测全程。

## 调试次数规则

复现→根据日志／trace定位→最小修改→相关测试→记录结果。同一故障两次修复均失败：停止编辑，提供根因证据、已排除项和下一项诊断；不要反复重建、清 DDC、安装插件或改架构猜测。通过相关检查后停止扩大测试，除非新证据要求。

## Phase 01B 执行合同（2026-10-31）

用户已接受 Phase 01A，并明确授权 Phase 01B。基线为已合并的 main `96524c9`，工作分支 `phase-01b-streaming`。

1. **迁移与安全门**：保存原图不变，以 Editor 复制世界、原生 MoveActorsToLevel 迁移 155 个 Actor；每个 Actor 的类别、世界变换、组件、碰撞、材质与交互配置必须相等。共享 Actor、PlayerStart、必要入口遮挡留 persistent。产出 4 个真实地图，无 WP、无 streaming volumes。
2. **运行时流送与状态**：一个控制器使用 ULevelStreaming 的原生 desired flags、加载/显示委托和低频超时看守；门只在双方真实就绪时开放。初始 A 就绪前不生成角色；GameMode 仍是唯一目标状态，流送 Actor 从目标进度恢复已使用状态。返回与重试是接受条件。
3. **有界验证**：实现前确认原基线没有四地图/流送控制器；完成后一次 Editor target 编译、实际 Editor 功能检查、一次 Windows Development BuildCookRun。Development 专用验收路线通过原生移动/交互，先回访三轮，再结束及 Restart；包含就绪抑制和恢复。记录真实结果，不能用文件存在代替可玩性。
4. **交付**：复核整分支，修复有证据的重要问题；更新现有文档，显式暂存相关资产/代码，提交、推送并创建 PR，不合并。

依赖：现有输入/角色/GM/HUD、可用 Editor Python、UE 5.8.4 和 VS 工具链。迁移只依赖已有资产和新类；运行时 readiness 验证必须与迁移后的区域归属一致；验收器只通过公开游戏行为驱动，不直接改变章节状态。

验证预算以用户本次指令为准：不为逐类 TDD 重复编译完整 Unreal target；同一故障两次修复失败后停止并诊断。非目标：战斗、AI、最终美术、磁盘存档、自制异步资源框架、模块重命名、性能重写。

## Phase01B 当时的任务边界（历史记录）

Phase01B 交付时 Phase02 尚未授权；本页后面的 Phase02 contract 记录了后续明确授权。不得将本章转换为 World Partition，也不得在尚未验证 packaged 加载时声称无缝。

## Phase 01B 实际交付与验证 — 2026-10-31

**状态：原生流送与 packaged 功能验收通过；60 FPS 性能目标未通过，人工门口/手感接受仍待用户。** 没有进入 Phase 02。

| 检查 | 结果与证据 |
| --- | --- |
| Git 基线 | Phase01A PR #1 已合并，main 快进至 `96524c9`；分支 `phase-01b-streaming`。切换时旧 Editor 锁住资产，正常关闭后逐一核对25个LFS对象哈希，把本地旧副本保存在 ignored backup，再 fast-forward；没有 reset、删除用户文件或 force-push |
| 首次 C++ 编译 | CinderRelayEditor/Win64/Development **Succeeded / exit0 / 53.04s**；`build-editor.log`。随后仅定向修正 BeginPlay 初始化顺序/当前API（22.58s），工坊事件绑定（见下），PIE退出（8.45s）；没有全引擎重建 |
| 原生迁移 | `migration-editor.log` 的 `CR_MIGRATION_PASS`；四张地图保存成功；155个原Actor：persistent15/A86/B22/C32，另外3个persistentActor。`Saved/Phase01B/migration-comparison.json` differences=[]，真实类别/世界和组件变换/碰撞/材质/交互设置相等；原图SHA未变 |
| 重开资产 | 新Editor进程 `CR_ASSET_REOPEN_PASS`，155原Actor归属正确；不是只检查磁盘文件名 |
| Editor 功能 | `editor-acceptance-entryfix.log`：3轮分别62.655/98.152/133.627s完成，模块/终端恢复、目标0→1→2→3→4、结尾和Restart PASS。完整receipt保存在 `editor-accepted/acceptance.json`；NullRHI不证明画面/性能 |
| Editor 退出修复 | 完整路线原先在活跃PIE直接退出触发Slate清理异常；现在由Python监督本轮新receipt，先停止PIE再关闭Editor。只重测退出路径，`editor-exit-check.log` **exit0**；该短检查明确不是玩法验收 |
| Windows 包 | 唯一 BuildCookRun **BUILD SUCCESSFUL / exit0 / 258.73s**；`package.log`。CinderRelay game target编译、cook、pak/IoStore、stage/archive均完成；Cook ReferencedSet明确列出四图 |
| Packaged 初始加载 | 真正的 `package/Windows/CinderRelay/Binaries/Win64/CinderRelay.exe`，PID35188；默认进入 `L_CH01_Persistent`；A Ready之前没有生成玩家，不在空世界落下 |
| Packaged 流程 | 一次完整路线PASS，151.286s记录、6476行；3次 C→B→A→B→C，回访前完成模块/relay，最终signal最后执行。旧模块不重现、终端不重复推进、Workshop entry不重复触发。Restart恢复0目标、初始区和UI；同一pawn在正常跨区中保持 |
| 门/失败 | 目标已loaded/visible但测试veto阻止Ready时，角色向门行走仍被真实碰撞挡住；反向离开取消需求并卸载；注入controller Failed后门关闭，公开R处理器Retry恢复。没有制造磁盘/缺cook包的实际I/O故障 |
| packaged退出/画面 | 真实游戏日志 `RequestExitWithStatus(0,0)`、正常LogExit，无fatal；启动器exit0没有被单独拿来证明成功。已查看原生1920×1080 ending.png，MERIDIAN NETWORK/CONNECTION RESTORED及两个按钮存在；没有声称人工检查全部转换遮挡或物理键鼠 |
| 内存与性能 | 三轮frame p95 71.453ms、GT15.529ms、GPU15.704ms；commit峰值4.68GiB、同C点首末+138.79MiB；真实卸载A4/B8/C3。完整条件、trace分析、预算差距和限制见 PERFORMANCE_BUDGET |

真实文件：`/Game/Generated/Phase01B/Maps/L_CH01_Persistent`、`L_CH01_RailYard`、`L_CH01_Workshop`、`L_CH01_RelayBunker`。原图 `/Game/Generated/Phase01A/Maps/L_CH01_Greybox` SHA256仍为 `C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733`。

本次打包输入清单（Source/Config/Content/uproject）保存于 `validated-inputs.json`，SHA256 `E9939D7F4733DE06158399EF6D4057AE89D55F04423E10E2CB163F47564AC47E`；实际game exe SHA256 `E1C74DDE2C0ABAB85217452DEF087C3F921FF4B8D14838BC3382449BD7F61A42`；packaged PASS receipt SHA256 `49CA82D0BC95532855FACA4592A6CC12E809B29264B4CC9849085A7FAF02C5E5`。文档/统计脚本后续修改不改变该编译包。

代表性真实日志（省略日志系统的时间前缀；完整 timeline 在 packaged-summary.json）：

```text
CR_STREAM StartupPlayerHeld
CR_ACCEPT 2.827 cycle=0 PASS Initial A floor ready before spawn
CR_STREAM C LoadRequested t=19.781 request=1 state=0 loaded=0 visible=0 wanted=1 player=B witness_valid=0
CR_STREAM C Ready t=20.121 request=1 state=3 loaded=1 visible=1 wanted=1 player=B witness_valid=1
CR_STREAM B Unloaded t=25.273 request=5 state=0 loaded=0 visible=0 wanted=0 player=C witness_valid=1
CR_INTERACTION Reconciled kind=0 objective=3
CR_ACCEPT 140.842 cycle=3 PASS Completed one C-B-A-B-C cycle
CR_ACCEPT_FINISH {"passed":true,"restart_verified":true,"message":"Restart verified after three backtracking cycles and ending","stage":"startup","map":"L_CH01_Persistent"}
```

以上均来自本次 packaged 日志，不是预设示例事件。

实际修复记录与限制：

- Python预检发现 overlap getter未导出，改用反射属性；颜色repr含内存地址，改比RGBA值。复制World的Python强引用曾阻止LoadLevel GC，释放wrapper后继续。commandlet MoveActorsToLevel返回0，改完整Editor后实际迁移全部成功。首次迁移保存/receipt成功后Python关闭阶段发生异常，随后新进程重开和真实packaged运行证明资产可用；不宣称首次迁移进程exit0。
- 最初Editor路线在module阶段失败；诊断证明角色在X1772/1889与entry重叠、Pawn响应为Overlap，但目标仍0。迁移后sparse delegate丢失constructor绑定；BeginPlay日志previous_binding=0确认，改每次BeginPlay AddUniqueDynamic、EndPlay解绑后通过完整路线。诊断日志曾误用普通delegate GetAllObjects导致一次编译失败（8.20s）；按sparse API改IsBound后定向编译通过（5.82s）。没有同一错误两次失败后继续猜测。
- 一次独立只读审查未发现生产流送架构Critical问题；Important退出路径已用短检查修复验证；旧receipt误读风险由本轮mtime监督消除。没有再派二次review，也没有以review代替运行证据。
- 审查未覆盖真实I/O坏包恢复、任意运行时删除地板/交互Actor。前者明确未注入；后者本阶段没有这样的玩法路径，未来加入破坏内容时须重新定义Ready失效。final-art、全部碰撞面、手感与自然遮挡仍需人工接受。
- 60FPS目标未通过；trace指出渲染/同步等待值得进一步定位，不能归因为“C++慢”或用重写/降画质解决。先处理有界性能对照与用户短试玩，再决定Phase02单次战斗遭遇；不会自动开始。

所有原始日志、trace、包和备份位于ignored `.environment-local/phase-01b/`；入库的是此可追溯摘要、源码、四图和现有文档更新。

## Phase 02 First Contact — implementation contract (2026-10-31)

Approved specification: owner's attached “CINDER RELAY — PHASE 02”, all sections 0–21. Baseline verified: PR #2 merged at `0da035de78f642e12f4a71aef3a6442e9276eac0`. Clean main fast-forwarded; branch `phase-02-first-contact`, same local project. This section is the plan and execution ledger; raw evidence remains under `.environment-local/phase-02/`.

Goal: one playable, bypassable Rail Yard encounter, with ROOK-5 gunplay and two Ash Warden scouts, preserving the original chapter and native streaming.

Architecture: small health and weapon components; gameplay timers/damage separated from cosmetic viewmodel motion/audio. Existing Character/Controller/UMG receive input and event-driven feedback. One humanoid enemy class and AIController use native Perception/Navigation; inspect actual Editor bindings for authored Behavior Tree/Blackboard assets. Dynamic Recast is confined to the small yard; enemies wait for local navigation and unload with their zone. GameMode stores defeated enemy and collected pickup IDs separately from ECRObjective.

Ruling: implement in the specified existing checkout/feature branch, without an extra worktree or another design approval — the owner explicitly requests implementation on this baseline. Follow the owner's bounded checkpoint validation instead of repeated per-class full Unreal RED/GREEN builds. Existing material primitives and original synthesized prototype audio avoid new licensing/download dependencies. R becomes Reload; streaming Retry moves to F5.

- [x] Preflight: verify real assets/Editor APIs and original map hash; reuse the unchanged Phase01B executable once at 1080p/Epic/100%, without allocation tracing. Record frame/GT/RT/GPU and load observations before rendering additions.
- [x] 02A: implement `UCRHealthComponent`, `UCRWeaponData`, `UCRWeaponComponent`, `UCRWeaponViewComponent`; integrate Character, Controller and HUD. Editor creates 3 input actions, IMC_Combat, one tuning asset, prototype audio/materials and configured player Blueprint. Acceptance: one shot/one ammo/one damage, cooldown spam rejection, cover blocking, partial/empty/zero-reserve reload, pause/death/restart cancellation, reversible ADS/recoil. Compile Editor once at the checkpoint and run focused native checks; integrate the coherent foundation. No AI or multiple weapons in this checkpoint.
- [x] 02B: one `ACRAshWarden`, `ACRAshWardenController`, minimal inspectable BT/Blackboard if supported, session defeated-ID record. Perception drives visible target/last-known location; native moves have bounded retries, and expired target memory stops pursuit/attacks. Acceptance: sight gain/loss behind geometry, no through-wall damage, actual nav path around cover, bounded failure recovery, dead/unloaded actors stop behavior. No EQS/GAS/custom nav framework.
- [x] 02C: Editor adds exactly two yard scouts, one ammo pickup and small navigation bounds; preserve all original actor transforms/components and map registrations. Add bounded opt-in combat acceptance and performance recording, then one integrated Editor route and one Windows Development package. Verify actual combat damage, death/restart, bypass, old objective flow, unloading/revisit dead-state persistence, final signal, reset and cooked assets. No final art, skeletal-animation claims, weapon assembly or Phase03.
- Delivery procedure: one fresh whole-branch review before final packaging where practical; evidence-supported corrections only; review explicit diff/staging, commit coherent tasks, push feature and create PR to main without merging. Document exact settings, known failures, manual acceptance limits and next task.

Shared interfaces: weapon uses native ApplyPointDamage -> health OnTakeAnyDamage; health OnHealthChanged/OnDeath drives both UI and AI cleanup. Weapon presentation subscribes to accepted-shot/reload/hit events, never determines ammo. GameMode session IDs survive zone unload but reset on Restart. AI consumes health and stable IDs; encounter assets consume these classes. Story objective code remains independent of kills.

Review focus: pause/death while reload timer is pending; R reload versus streaming retry conflict; perception stale targets after unload/death; NavMesh unavailable during streamed startup; level unload/reload while defeated IDs are recorded. Targeted tests belong to 02A/02B and one integrated route, not repeated full chapter tests after tuning.

Preflight complete: existing Phase01B game executable SHA matched the accepted package; one same-settings run passed three cycles and Restart. Only frame/bookmark trace channels; no allocation/CPU/GPU scope tracing. Three-cycle p95 frame/GT/RT/GPU = 14.998/2.5315/14.9679/13.512 ms; no >50 ms frame in the cycle segment. Startup/early maximum RT 374.200 ms remains. Settings unchanged (1080p,100%,Epic,RT/Lumen). The read-only NullRHI Editor audit briefly overlapped this run, so it is a bounded diagnostic rather than a controlled final benchmark. Heavy-run persistent RT hitch did not reproduce; no architecture rewrite justified.

Editor baseline verified 155 original actors and absence of weapon/health/enemy classes before implementation. Native BT root editing is supported; CubeBuilder is not exported, so navigation will use the Editor's native volume actor factory and verify real bounds. 02A initial compile failed only on two `auto*` deductions from TObjectPtr; `.Get()` correction passed in 7.74s. Actual gunplay assets generated and saved, Editor exit0. First focused weapon check passed damage/ammo/cooldown but exposed same-tick camera rotation in the test harness; log showed the old direction hit the target. Split aim and fire into separate stages. Ruling: fold that focused correction into the pending 02B compile, not an extra full build. No gameplay aim rewrite was made for a test timing issue.

02A focused check now PASS (`weapon-check-fixed.log`, saved receipt under `weapon-check-evidence`): single damage/ammo, cooldown spam, miss, real collision cover, partial/empty/full/zero-reserve reload, no duplicate transfer, sprint, paused reload, ADS reversal, death cancellation and Restart reset. The original failed receipt remains in the prior log; Editor exit0 alone was not treated as a pass.

02B compile corrected three reported API/type issues once (static lambda capture, inherited Pawn name shadow, native navigation dynamic-delegate pointer signature), then passed in22.17s. 02C route compiled in27.93s. Editor key-type aliases required `load_class` by the verified reflection path; this fixed asset creation. Native NavBounds registration queues until the navigation tick, so generation now observes real Recast data with a30s bound rather than asserting synchronously. Actual asset generation then PASS/exit0; fresh Editor audit found zero property differences for all155 originals, two distinct scout IDs in RailYard, unchanged original map hash and unchanged streaming registrations.

First integrated route proved nav readiness, real path around train cover and visible-player perception but timed out waiting for enemy damage. Engine BaseEngine.ini proves Pawn defaults ignore Visibility, so enemy hitscan could not hit the player body. Corrected the Character capsule response to Block; no damage bypass or test health manipulation was used. Also corrected double counting of one failed MoveTo request when the native completion callback fires synchronously. These are evidence-supported functional fixes, not tuning to hide failures.

Collision repair then passed actual enemy damage, real train occlusion, finite memory expiry and recovery movement. The harness subsequently stopped at(-1154,-997,98): its diagonal return waypoint crossed the train. Replaced it with the reverse flank waypoints; no teleport or geometry modification. Independent read-only whole-branch review found no new Critical/Important production defect, identified this known acceptance blocker, and flagged miss feedback as Minor. Ruling: promote false impact feedback to a correctness fix because the approved combat-feedback contract requires distinguishing a surface hit from empty space; OnShot now carries native bBlockingHit and cosmetics suppress miss impacts. This is the one review fix pass, no re-review. Remaining unjudged areas are packaged/integrated outcomes and manual feel, which must be evidenced separately; arbitrary destruction of nav/floors and live tuning changes remain outside current gameplay.

### Phase02 actual acceptance — 2026-10-31

**Engineering functionality PASS in Editor and a real Windows Development package. Human gunfeel/audio acceptance and clean 60FPS performance acceptance remain open.** This supersedes the pending items in the execution ledger above; it does not turn placeholders into final art.

| Check | Actual result / local evidence under `.environment-local/phase-02/` |
| --- | --- |
| Final Editor target | `build-route-feedback.log`: Succeeded,63.93s,exit0. Earlier checkpoint failures and focused repairs are retained above. No engine rebuild. |
| Real asset preservation | `asset-audit.json`: passed=true,preserved_originals=155,differences=[]; fresh Editor load, not a filename-only check. Original Phase01A SHA unchanged. Only Persistent/RailYard maps modified; Workshop/RelayBunker bytes unchanged. |
| Editor integrated route | `editor-combat-routefix.log`, `editor-combat-pass/acceptance.json`: passed=true,scenario2; real damage, death/restart, two enemy kills, ammo, original objectives and return traversal. NullRHI; no visual/GPU claim. |
| One final packaging pass | `package.log`: BuildCookRun261.30s, BUILD SUCCESSFUL, AutomationTool ExitCode=0. Game target compile108.54s; cook reports0errors/0warnings. ReferencedSet includes all four maps and all20 Phase02 assets. |
| Actual packaged gameplay | `packaged-combat.log` and `package/Windows/CinderRelay/Saved/Phase02/acceptance.json`: passed=true,scenario2. Route completion98.206s; frame-recorded window97.547s/5876rows. Enhanced Input moves/fires/reloads/interacts; no teleport, synthetic combat damage or direct objective progress. |
| AI / damage | Actual enemy fire damages and kills player. Real train geometry blocks sight/damage; memory expires. Native unreachable MoveTo fails, then AI actually moves after legitimate perception. Four accepted player shots defeat two scouts; real reload and player damage verified. |
| State / streaming | A unloads after leaving yard; return A reconciles both defeated IDs and consumed ammo. B/C genuinely unload on return. Old module stays collected, relay progression remains3, final signal completes4; Restart restores health100,ammo5+25,two scouts,empty defeated set. Same player persists through normal transitions. |
| Discrete visual evidence | Actually viewed1920x1080 `combat.png`, `combat-after.png`, `defeat.png`, `ending.png`: visible greybox weapon/enemy, hit/ammo/health feedback, defeat and ending menus. Not continuous manual input/audio/animation acceptance. |
| Exit evidence / limitation | Game logs `RequestExitWithStatus(0,0)`, normal subsystem teardown and `LogExit: Exiting`, no Fatal/Error/Ensure. The bootstrap process returned777003 to PowerShell; its source is absent from the installed SDK and the code remains unexplained. Do not claim an OS process exit0 for this run. The fresh gameplay receipt and normal game log support functional PASS independently. |
| Offline profiling | `combat-summary.json`, `insights-*.csv`, `combat.utrace`; Insights exit0. Conditions, actual deficits and analyzer warnings are in PERFORMANCE_BUDGET. No repeated playtest/package to improve numbers. |

Map inventory after creation: Persistent19 / RailYard91 / Workshop22 / RelayBunker32, total164 named level actors (155 originals + three Phase01B shared actors + five new yard actors + native Recast). New20 assets: six original synthesized SoundWaves, four materials, three Blueprints, three Input Actions plus context, one weapon DataAsset, BT and Blackboard. No downloaded raw packs, fabricated skeletons or new map hierarchy.

Reproducibility hashes:
- validated98 Source/Config/Content/uproject inputs: manifest SHA256 `5F525C76D03EAC31BF57E36F11D4485FC284DEB86A1941DF686964DEF7571036`; rechecked after packaging,0changed.
- actual game executable: `EB6F3111B25CD1605DDD54BBFDB816ABBFF02B5C5FEA16EBB855D88445FD2A9E`.
- packaged acceptance receipt: `DF1143AEE1E1EAFC2CA34561D3E82E139BF723CF2E3E4ED01AD67DD752D8EEF2`.

Representative actual packaged events (world time resets on Restart):

```text
CR02_ROUTE PASS Native perception acquired visible player; enemy inflicted real damage
CR02_ROUTE PASS Real train geometry blocks sight and enemy damage
CR02_ROUTE PASS Lost-target memory expires; no omniscient pursuit
CR02_ROUTE PASS Two scouts defeated by accepted player shots; player also received damage
CR_STREAM A Unloaded t=18.945 request=2 state=0 loaded=0 visible=0 wanted=0 player=B witness_valid=1
CR_ENEMY ReconciledDefeated id=CR02_Scout_1
CR_ENEMY ReconciledDefeated id=CR02_Scout_2
CR_STREAM A Ready t=36.201 request=3 state=3 loaded=1 visible=1 wanted=1 player=B witness_valid=1
CR02_FINISH {"passed":true,"mode":"combat","scenario":2,"message":"Real combat, native AI/nav, death/restart and streamed chapter route passed"}
```

Remaining limits: prototype primitive humanoids and weapon transforms, no skeletal animation; synthesized temporary audio, not human-listened acceptance. HUD/readability checked in still frames; physical mouse feel, ADS obstruction, close-wall transitions and full bypass-to-ending route need one short user playtest (retreat/flank and unrestricted objective code are verified; the packaged route chose combat). No observed functional blocker in the completed route. Restart/exit logs have native CrowdManager/Recast teardown warnings; intentional navigation failure emits a warning and VSync command priority warnings keep0. These are recorded, not called a clean runtime log. The unexplained bootstrap exit code and instrumented frame spikes remain follow-up items, not reasons for an unrelated architecture rewrite.

Next proposed task: short manual acceptance of aim/recoil/reload/audio, cover and retreat/bypass, then bounded tuning only for observed problems. A separately authorized clean performance sample should disable screenshots and detailed scope tracing to isolate their overhead, at the same quality. Do not start Phase03, weapon assembly, more weapons, final art or checkpoint work automatically.

### Packaged desktop DPI correction — owner playtest follow-up

The owner reported clipped bottom controls/right-hand health-ammo in the packaged executable. The physical display is2560x1600; their actual `-windowed -ResX=1920 -ResY=1080` run logged a1707x1067 desktop/workarea1707x1019. The installed engine's default `bAllowHighDPIInGameMode=False` and SlateApplication::InitHighDPI explain the DPI-virtualized coordinates. This is a desktop window sizing issue, not evidence that16:10 cannot display the HUD.

Reproduced visually using the existing package, paused at spawn: right-hand combat text fell beyond the desktop. One controlled rerun changed only `-ini:Engine:[/Script/Engine.UserInterfaceSettings]:bAllowHighDPIInGameMode=True`; the log then reported2560x1600/workarea2560x1528, and the actual window showed both complete bottom control text and `HEALTH100 ROOK-5 5/25`. No HUD/gameplay rewrite, OS scale change, compile, cook or combat regression route. Raw before/after logs are under `.environment-local/phase-02/dpi-check/`.

Persist the verified engine setting in DefaultEngine.ini for future packages. The already delivered local package uses the same key in its ignored Saved/Config/Windows/Engine.ini; its executable/content bytes remain unchanged. This configuration correction does not update the earlier benchmark or establish human combat-feel acceptance. Official setting: [UUserInterfaceSettings, UE5.8](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UUserInterfaceSettings).

Persistence verification: a final ordinary launch with no command-line DPI override logged2560x1600 and showed complete controls/health/ammo with the weapon visible. The same existing executable SHA remains EB6F3111B25CD1605DDD54BBFDB816ABBFF02B5C5FEA16EBB855D88445FD2A9E. The game was left open for the owner; no movement/fire input or gameplay automation was injected. Evidence: dpi-check/persisted.log.

## Phase03 The Mechanic's Hands — authorized implementation plan

Spec: owner's Phase03 instructions0–20 in this chat, baseline PR3 merge7e1002d7fba96c7c0ed7478793772de9c55890c8 verified. Worktree clean; main fast-forwarded; branch phase-03-weapon-reclamation. Existing engine5.8.4/module unchanged. Goal: collect one logical Survey Optic at either location, play an optional22second authored first-person restoration, retain a visible60degreeADS upgrade through streaming, preserve original combat/objectives/ending.

Execution: inline using executing-plans; this existing milestone file is the plan/ledger, not a parallel documentation system. User-authorized checkpoint builds/verification override repetitive per-class RED/GREEN builds. The user has already authorized asset creation, source exports and implementation; no extra generic design/write approval is required. Use the requested existing checkout/branch. Raw evidence/exports under ignored `.environment-local/phase-03/`; intentional .blend and its reproducible authoring/export script under ArtSource/Blender/Phase03. No paid provider, external pack or license substitution. game-dev doctor verifies installed Blender4.5.11LTS; its default workspace belongs to another project and will not be used for writes. Unreal consumes FBX, so use native bpy/FBX/Editor import directly, not an unnecessary GLB vendoring package.

Architecture and interfaces:
- ACRGameMode: explicit HasSurveyOptic/TryCollectSurveyOptic/HasSurveyUpgrade/TryApplySurveyUpgrade, collected source IDs and narrative flags. Stable logical IDs CR03_SurveyOptic and CR03_Rook5_SurveyOptic. Objective enum unchanged.
- ACRSalvagePickup: existing ICRInteractable pattern; both sources reconcile from logical component ownership and update from the chapter event, no strong cross-level actor references.
- ACRWorkbench: one Workshop actor owns static bench, skinned animated rig, camera, soft asset preload handle and local LevelSequencePlayer. Preparing/Playing/Finalizing/Completed/Aborting; natural sequence completion or explicit Skip commits once, genuine Abort never commits. EndPlay/death/restart restore input/camera and release delegates/load/sequence references. Player remains stationary within Workshop so ordinary streaming needs no controller rewrite.
- UCRWeaponComponent: minimal presentation-lock gate and GetAimFOV resolving immutable base data plus session upgrade. No new weapon class/ammo rewrite. UCRWeaponViewComponent adds optional imported static appearance and optic plus hide/restore; old cubes remain fallback.
- ACRPlayerController/HUD: weak ActiveWorkbench, Tab Skip, existing Esc pause, subtitle with bounded lifetime; first workshop entry, assembly reflection and relay restoration claim distinct one-time flags.
- Editor: generate_restoration.py imports authored FBX, creates real22s LevelSequence/skeletal track and owned assets, places two salvage actors and one bench beside existing content. Snapshot all existing actors before/after; Phase01A map remains byte-identical. Runtime modules may add LevelSequence/MovieScene only; SequencerScripting is Editor-only.

Review focus: input state after skip/pause/death/EndPlay; incomplete async load; duplicate pickup/upgrade while actors reload; animation unit/axis/contact continuity; ordinary firearm/ammo state and optional mission bypass.

- [x] 03A: minimal state/salvage/upgrade and workbench lifecycle foundations, focused state fixture first. One Editor compile and focused state check, with only evidence-supported repairs. No global inventory, live DataAsset mutation, save system or cinematic claims before assets exist.
- [x] 03B: real Blender source with arm/hand deformation plus coherent weapon/optic/bench exports; native import, actual bone/duration/scale validation and authored sequence. Inspect meaningful Unreal frames; use actual capture if available. No fabricated skeleton, contact/temporal quality claims from still frames, or external copyrighted content.
- [x] 03C: integrate provisional subtitles, real movement/interaction test route and interruption handling; one integrated Editor smoke. Final independent read-only review per execution skill, one focused correction pass. No new streaming framework or long story sequence.
- [x] Final local validation: one Development package, one full-start route plus the documented focused native-readiness repair/resume; normal completion, skip, cancel, streaming/reset, firearm regression and optional bypass covered.1080p/Epic evidence and limitations recorded below. Git delivery uses only intentional assets/source/docs, three coherent commits, push/PR without merge. Stop before Phase04.

03A evidence: read-only Editor preflight captured the complete existing actor inventory and verified FBX/Sequencer scripting APIs. Original bench/module at (2800,-365,95/127); new bench planned at (2300,-350,0), preserving the old actors. Blender4.5.11LTS CLI and FBX exporter verified. Initial Editor compile failed on TObjectPtr range-loop deduction; its focused repair exposed a separate link failure. Installed LevelSequence headers declare InitializePlayerWithSequence without a source definition/DLL export; dumpbin and local SetSequence implementation verified the supported replacement. Final affected-target compile succeeded, exit0,8.47s,4actions. Focused CinderRelay.Restoration.Session automation passed, exit0,1test: prerequisite rejection, either source, duplicate rejection, objective isolation, exactly-once upgrade, story claim, fresh chapter reset. Logs: build-03a*.log and session-tests/index.json. Animation import/playback and cinematic control acceptance remain pending; this code foundation does not claim those checks passed.

03B evidence: Blender4.5.11LTS wrote a real editable .blend (~6MB),39authored bones and a22s/30fps action. A separate reopen found192multi-weight cuff/palm vertices. FBX import created three static meshes, skeletal mesh, skeleton, AnimSequence, six materials, one original SoundWave and one native LevelSequence (14assets). Actual ROOK length79.5cm; sequence/animation length22.0s. Native Editor reimport preserves asset IDs. Existing164actors compare unchanged; six owned additions; only Yard/Workshop maps changed and the original rollback map remains untouched. First Editor rendered frames at3/7/13/18s were inspected, proving actual skeletal playback but not temporal smoothness. These revealed finger/receiver clipping; a targeted curve correction moved contact poses outside the weapon, without regenerating geometry. Corrected-frame review was completed during03C and final packaged inspection below.

Observed integration failures and bounded repairs: initial FBX import produced no simple collision (native subsystem count0); explicit native collision fixed that. The initial saved pickup pitch placed it inside its stand; runtime hit logs named the stand, and map timestamps showed transform edits had not dirtied/saved existing actors. Actor Modify plus reload assertions corrected this. Yard collection, duplicate rejection and the original death/restart route then passed. Workshop backup was blocked by the bench's full bounding box including its raised rear rail; a native tabletop-height box replaces that overly broad collision. The real backup interaction then passed. A saved-source pose audit detected stale parent-matrix evaluation; explicit per-frame local-basis solving corrected it, followed by targeted Interchange reimport. Native OnStop/OnFinished ordering then caused natural completion to abort and a MovieScene TickManager ensure; local engine source confirmed StopInternal precedes OnFinished. Cleanup now leaves the delegate stack, and the existing route injects a real premature SequencePlayer Stop to distinguish cancellation from successful completion. Its latest focused regression is recorded separately below; packaging had not yet been performed at that checkpoint.

Ruling: use the owner's bounded checkpoint/build policy instead of per-class repeated full RED/GREEN engine builds; deterministic state checks and concrete failing runtime routes supply regression evidence. Cost if wrong: narrower coverage than a complete gameplay test suite; unexecuted lifecycle/aesthetic cases must be named.
Ruling: use native Blender/FBX/Unreal asset tooling directly rather than the asset skill's generic GLB vendoring package or repeated write confirmations. The owner explicitly authorized these assets and imports. Cost if wrong: no cross-engine canonical package, which this Unreal-only milestone does not require.

03C Editor acceptance: latest CinderRelayEditor targeted compile passed(exit0,10.70s). `editor-lifecycle-regression.log` / fresh Saved/Phase03/acceptance.json passed scenario4, resuming at scenario1 after the separately validated Yard/death scenario. This run exercised actual Workshop backup E interaction, missing-prerequisite rejection, duplicate suppression, a native SequencePlayer Stop with no grant/input lock, full22s playback, frozen sequence time during pause, exact-once completion, imported appearance, actual60degreeADS, post-upgrade fire/reload, real Workshop unload/reload, skip, restart reset and a full ending without salvage/upgrade. The earlier natural-finish TickManager ensure did not recur in this run. Actual imported skeleton count40 includes the FBX armature root above39authored bones. Corrected3/7/13/18s Unreal frames were inspected; the optic aperture is open and ADS reticle is centered. Raised-hand framing was widened to74degrees in the Workshop camera after inspecting the13s pose; final packaged frames will verify that presentation-only adjustment. No video was captured: no existing encoder was found in the available toolchains. Still frames and moving-bone checks do not establish continuous animation smoothness. Glove anatomy, mirrored thumb quality, gripping finesse and final sound/animation aesthetics remain prototype limitations requiring owner review.

Final independent review: phase03_final_review inspected7e1002d..b4c6823, lifecycle/source/diff/evidence/actual frames, read-only. No Critical or Important runtime findings; no behaviors declined to judge. It identified one Minor missing reimport-documentation path. Final: Ruling: treat that documentation gap as an acceptance requirement because the owner explicitly requested a documented editable animation/export workflow; added the already executed targeted export/reimport commands and distinguished procedural re-authoring from manual-keyframe export. Cost if wrong: following regeneration commands could otherwise silently retain stale Unreal animation or overwrite manual keys. This documentation-only fix needs no repeated engine/gameplay test. Review limits: mid-presentation death/unload/Restart and missing-resource injection have static review but no separate runtime cases; video continuity and human aesthetic acceptance remain unproven. No further code review or broad test cycle was requested.


Packaged validation repair (first attempt): the single final BuildCookRun succeeded, exit0,109.54s; the first full-start route then failed the post-assembly reload assertion. The log records input injection at22:43:34.469, screenshot-delayed accepted shot at22:43:34.832, and reload injection at22:43:35.471. Only0.639s of the unchanged0.9s native weapon cycle had elapsed. The harness incorrectly equated wall time since injection with native readiness; the weapon correctly rejected early reload. The focused fix waits for ECRWeaponState::Ready before injecting reload. No production weapon logic, assets, cook settings or quality changed. Preserve failed-first-route/, packaged-first-failed.log and first-failed.utrace. Rebuild only the Development game target, refresh its packaged binary, and resume scenario1; scenario0 Yard/cache/death had already passed. This is a corrective validation of an observed harness error, not another full cook or performance-tuning cycle.


### Phase03 final local delivery evidence

- Compilation: CinderRelayEditor passed after lifecycle integration(exit0,10.70s); final BuildCookRun built/cooked/staged/archived Windows Development(exit0,109.54s). The evidence-led harness fix then rebuilt only CinderRelay Win64 Development(exit0,32.77s,4actions). Copied the resulting native exe/PDB into the existing archived package; content containers were not recooked or regenerated. Source/package executable hashes match. Normal play code/assets are unchanged by that corrective build.
- Packaged acceptance: corrected scenario1–4 route PASS,182.782s, fresh receipt and engine RequestExitWithStatus(0,0). Scenario0 Yard-cache/no-combat access, duplicates, native AI/damage/death/restart passed in the preserved first run. The machine's bootstrap again returned777003, so that code is not called a successful game exit by itself. The real engine status, log and receipt establish the result. Do not call this one uninterrupted full-start pass.
- Functional coverage: missing salvage rejected; both sources tested; duplicates rejected; actual camera-trace E interactions; genuine SequencePlayer Stop abort without upgrade or input lock; native22s completion; pause freezes playback; Skip grants once; actual60degreeADS; imported optic visible; fire consumes one round and native reload reaches5; real Workshop unload/reload reconciles consumed salvage/completed bench/upgrade; Restart resets flags; original enemy combat/objectives/final signal; full ending with no salvage or workbench. Stable IDs and ECRObjective remain unchanged.
- Asset evidence:14real imported/generated Phase03 assets, including22.0s AN_CR03_RookRestoration and LS_CR03_RookRestoration. The cook manifest contains all14 and all four existing Phase01B maps. Original164actors retained, six owned additions =>170; RailYard+3/Workshop+3, no Persistent/Bunker changes. The rollback Phase01A map is byte-identical. Editable .blend is Git LFS,39source/40imported bones,6720skin vertices,192multi-weight vertices. No downloaded resources.
- Visual inspection: actual packaged1920x1080 frames at3/7/13/18s and upgraded ADS were inspected, in addition to Editor frames. Camera74degrees keeps the raised fingertips inside the13s frame. The regular weapon is absent during bench presentation; one upgraded appearance returns, aperture/reticle and bottom/right HUD are visible. Subtitle/controls stay outside the central action. These discrete frames do not prove temporal smoothness or zero clipping between samples. No video recorded. Segmented glove anatomy, mirrored-thumb orientation, exposed elbow/segment join at the raised pose, gripping/contact finesse and audio/pacing remain prototype-quality limitations requiring human review; do not call them production animation.
- Runtime logs: no Error/Fatal/Ensure in the final run. Deliberate `CR03_ASSEMBLY Aborted without upgrade`, startup console-command timing, and existing CrowdManager/Recast teardown warnings are recorded, not suppressed. Actual mid-presentation death/unload/Restart and missing-asset fault injection were not separately executed; those cleanup paths were reviewed in code. The completed normal/skip/cancel route has no observed remaining functional blocker.
- Performance: assembly frame p95=22.108ms, GT1.771ms, RT22.013ms, GPU21.145ms; above60FPS budget. Peak working set1.735GiB/private commit4.219GiB. Captures/tracing/pause affect the sample; no clean60FPS or leak-free certification. Full conditions, failed first attempt, scoped CPU evidence and memory samples are in PERFORMANCE_BUDGET.

Actual representative packaged events (world time resets across Restart):

```text
CR03_ASSEMBLY Playing duration=22.000
CR03_ASSEMBLY Aborted without upgrade
CR03_UPGRADE CR03_Rook5_SurveyOptic applied
CR03_ASSEMBLY Finalized applied=1
CR02_ROUTE PASS Upgraded weapon completes original reload
CR_STREAM B Unloaded t=71.394 request=4 state=0 loaded=0 visible=0 wanted=0 player=A witness_valid=1
CR02_ROUTE PASS Upgrade survives actual Workshop unload and return
CR02_ROUTE PASS Reloaded workbench reconciles completion without replay
CR02_ROUTE PASS Reloaded salvage remains consumed
CR03_ASSEMBLY Skip
CR02_ROUTE PASS Chapter ending reached without salvage or optional workbench
CR02_FINISH {"passed":true,"mode":"combat","scenario":4,"message":"Combat, restoration, skip, cancel, streaming and optional ending route passed"}
```

`CR02_`/mode=combat is the retained existing harness prefix, not evidence of testing the wrong milestone. Phase03 uses its own explicit flag, receipt directory and stages. Repeated PASS assertions in a polling stage are not distinct test cases.

Reproducibility SHA256:

- Final archived game executable: `2DDF8C75C8E9541CBE6A18601B3E1D731F1F60F836834934D9E86DFF4C163A5D`.
- Corrected packaged acceptance.json: `D0031B20247F22123E63CBAAAE683656BDCBC571F5C752DB09BB7F951CF4DEB4`.
- 117validated Source/Config/Content/uproject input manifest: `0704743D434F84A7E8C88700A12F7E5B06575F1850A4FE70F553A21ABFEBBA1E`.
- Phase01A rollback map: `C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733`.

Evidence root: `.environment-local/phase-03/`; final executable `package/Windows/CinderRelay.exe`; raw receipt/frames/memory/settings/captures under `package/Windows/CinderRelay/Saved/Phase03/`. Build logs, packaged-restoration.log, failed-first-route/, packaged-first-failed.log, packaged-summary.json, validated-inputs.json and Insights exports remain local/ignored. No full package, trace, temporary export, Blender backup or cache is committed.

Local implementation and bounded validation are complete. Deliver branch phase-03-weapon-reclamation as a PR to main; no automatic merge. Next recommendation is one short owner playtest of the optional flow and22s visual pacing, then a narrowly scoped Phase03 presentation polish for observed hand/contact/framing issues. A separate same-quality, capture-free performance comparison may follow authorization. Phase04/checkpoints/new weapons remain out of scope.


## Phase04 Persistent World — implementation plan and ledger

Goal: resume Chapter01 across real process exits with stable checkpoint/session/player state and collision-safe native streaming bootstrap. Spec: owner's Phase04 sections0–17 in this chat; verified merge d53c6d065b6d1980b3628d06cb4b7075c513e7ee. Clean checkout, main fast-forwarded, branch phase-04-persistent-world. Engine5.8.4/module unchanged. Inline execution using executing-plans; this existing document is the plan/ledger.

Architecture: UCRChapterSaveGame is a flat version1 native SaveGame with validated IDs, bounded values and a payload checksum. UCRChapterSaveSubsystem (GameInstance lifetime) owns two alternating native slots, async scan/write callbacks, one coalesced pending snapshot and a value-only pending travel intent. GameMode remains session authority and restores flags in InitGame before any streamed BeginPlay. Three persistent ACRCheckpoint anchors define safe transforms; the existing streaming controller starts the requested native zone. Existing controller/UMG supplies New Game, Continue, death Retry and explicit Restart Chapter.

Decisions: controlled persistent-map reload for Continue/Retry; never OpenLevel between normal zones. Cold launch holds gameplay at a small existing UMG menu until New Game/Continue. Restart Chapter starts fresh session state and preserves disk checkpoint. CP00 is the new-game anchor; create its initial save only when both slots are genuinely missing, never overwrite corrupt/existing saves on startup. CP01/CP02 advance once per run after their prerequisites and stable player state. Progress since the latest successful checkpoint rolls back on recovery. Two slots protect the last valid generation; no generic inventory/save framework or animation rework.

Review focus and owning tests:
- Async completion across Restart/Exit and coalesced writes: immutable snapshots, no stale-world UI success;04A callback/queue and04C interrupted-request cases.
- Corrupt newer slot, unsupported schema and inconsistent IDs/values: reject explicitly, retain earlier valid slot;04A serialization/selection tests.
- Restored B/C before actor BeginPlay or before collision readiness:04B held-player and real actor reconciliation checks.
- Cinematic Stop/Skip/death/unload/controller destruction:04C lifecycle cases, no checkpoint of partial presentation and no reentrant MovieScene destruction.
- Restart/New Game versus Continue semantics, saved health/ammo and old story flags:04C cross-process route and UI inspection.

- [x] 04A — CRChapterSaveGame.{h,cpp}, CRChapterSaveSubsystem.{h,cpp}, CRCheckpointTests.cpp; narrow CaptureSession/RestoreSession methods in CRGameMode and explicit stable restore methods in health/weapon. Schema round-trip, ID/version/health/ammo rejection, sets/flags, checksum, actual failed async write, earlier-slot fallback and duplicate application passed focused native Automation. Commit c988695: feat: add versioned chapter save snapshots.
- [x] 04B — CRCheckpoint.{h,cpp}, GameMode InitGame/starting-player gate, minimal CRChapterStreamingController initial-zone support. Editor script added three owned persistent anchors after backup/hash/inventory audit; no old generator. Safe floor/capsule, held startup, B/C reconciliation and original actor preservation verified. Commit39197b8 includes streaming and recovery UI.
- [x] 04C — CRPlayerController/CRHUDWidget plus CRCheckpointRoute, Scripts/run_checkpoint_acceptance.ps1 and summarize_checkpoints.py. Focused build/tests, one independent final review, one final Windows Development BuildCookRun and three packaged processes completed. Details and explicit remaining visual/lifecycle/exit-code limits follow. Deliver PR to main without merge; stop before Phase05.

Interfaces: SaveGame.Validate(FString&) / Seal() and CheckpointZone(FName) define the shared snapshot contract. SaveSubsystem.RequestWrite(snapshot,runEpoch), ScanSlots(), PrepareNewChapter(), PrepareContinue() and ConsumeTravelIntent() provide bounded persistence; it never owns actors. GameMode.CaptureSession(UCRChapterSaveGame&) / RestoreSession(const UCRChapterSaveGame&) preserve ECRObjective; RequestCheckpoint validates the anchor/player before snapshotting. GameMode.GetStartingZone()/CanBootstrap()/IsCheckpointReady()/ReleaseStartingPlayer() control streaming bootstrap. Checkpoint callbacks update the current run only; queued snapshots from an old run are discarded.

Pre-flight:04A schema IDs/zone/prerequisites are consumed by04B anchors and04C tests; one shared mapping prevents drift.04A GI travel intent is consumed in04B InitGame, before streaming.04C UI waits for scan/write state and does not infer save completion from a timer.

Ruling: follow the owner's detailed implementation authorization and bounded checkpoint verification in the existing checkout, rather than adding approval pauses, another worktree or repeated per-class engine RED/GREEN builds — the scope and branch are explicit — cost: less exhaustive runtime coverage, with unexecuted cases named and focused tests retained. Raw evidence stays under ignored .environment-local/phase-04; no deletion of prior evidence.

04A evidence (2026-10-31): CinderRelayEditor incremental build succeeded (5.92s after correcting a test-only numeric-limits API; I/O fixture repair build 5.75s). Native Automation Schema passed; DiskFallback passed after one focused fixture repair. An invalid filename containing a colon produced a successful NTFS alternate-stream write, so the dedicated fault fixture now creates a directory at the exact test save filename. Actual native async callback returned false and preserved generation 1. Corrupt/future-version newer slots fell back to generation 1; coalescing and interrupted queued requests passed. Logs: `.environment-local/phase-04/{build-04a-repair,build-04a-io-repair,state-tests,io-repair-tests}.log`. These are data/I/O tests, not gameplay or cross-process acceptance.

04B/04C integration evidence: three real persistent anchors saved/reopened;170 original actor snapshots unchanged. Native SnapToSafeFloor derives actual collision height and validates capsule clearance; CP02 corrected from a trace initially inside the ramp ceiling to(4050,0,-40.18861). Python HitResult field bindings are absent in this installed binary; read-only binding probe justified the small CallInEditor bridge. Final asset Editor exit0; one earlier Editor shutdown returned access violation after its receipt (not treated as clean success).

Editor target compilation passed after focused UHT parameter-name and TObjectPtr inference repairs; integration build37.10s passed. Route1 actual movement/fire/ammo/CP01 native save passed. First CP01 restoration requested A because native GetPlayerPawn returned SpectatorPawn_0; initial-zone policy now ignores pre-release pawns and PlayerController suppresses the loading spectator. Logs confirm BootstrapTarget=1 existing_pawn=None. Corrected route2 passed delayed-readiness pawn hold, exact health68/magazine1/reserve35 restoration, consumed enemy/ammo flags, alternative salvage rejection, explicit Skip, injected assembly death, presentation actor destruction, Restart/world EndPlay, controller destruction, native Stop, pause, natural22s completion, original reload, and successful upgraded CP02 generation2. Repeated assembly checkpoint assertions are one case, not three independent cases. Evidence: editor-route1.log, editor-route2.log(first failure), editor-route2-repair.log(spectator assertion), editor-route2-final.log, CinderRelay/Saved/Phase04/{1,2}. CP02 restore/backtracking and final package remain pending.

Editor-game test processes requested native exit0 but remained alive after receipts; they were identified by exact command line and stopped explicitly. This is not successful clean process-exit evidence. No user save files were modified; all routes use CR04_TEST_Editor04. Use the packaged process handles and fresh receipts for final disk persistence and exit-code investigation.

Final review (fresh gpt-6-astra reviewer, whole branch d53c6d0..39197b8): two Important findings, no Critical/minor findings. CP00 overlap occurs during SpawnActor before native Possess; the original Editor route proved the first write was CP01 generation1. Fix: explicitly arm the existing bounded stable-state retry after safe possession; route1 now waits for a real CP00 success callback before combat. Second finding: old-run completion leaked CHECKPOINT SAVED through the menu availability status despite the toast epoch guard. Fix: BeginRun clears previous operation feedback and stale callbacks publish neutral retained-checkpoint availability only. Added native disk regression assertions for both already-completed and late old-run feedback. These source/runtime failures are recorded evidence; no fabricated RED test run is claimed. One focused final build/test pass follows, per owner's bounded validation policy.

Editor route3 already verified CP02 safe C bootstrap, restored health/ammo/upgrade, Workshop/yard reconciliation and real unload, no replayed saved story flags, explicit Restart preserving disk generation, death from native enemies, three CP02 recovery cycles, and upgraded ending. Its last optional-workbench-bypass walk timed out at(243,-1150.2,98.2), blocked by existing yard geometry. Corrective route uses the previously validated combat path, then skips only the optional workbench; it does not modify level geometry or weaken the bypass criterion. Earlier successful route cases are retained, not counted twice.

Final review fixes: Editor target build succeeded,32.16s. Focused native Automation groups Schema and DiskFallback both succeeded (final-state-tests.log); regression assertions verify new-run status reset and late old-run callback neutrality. No second reviewer or repeated full-suite loop. Corrected Editor route3 passed all required CP02 recovery/backtracking/retry/restart and optional-workbench ending cases (editor-route3-repair.log). These are automated runtime checks, not owner aesthetic acceptance. Original70asset hash audit found only the intended persistent-map change; Phase01A rollback SHA256 remains c22ac1dafe74f3006ca8f2498e7ad81ba8ac827890c44b3554f31d0d13d3e733.

One final Windows Development BuildCookRun succeeded:101.94s, AutomationTool exit0 (package.log); no second packaging pass. Final three-process acceptance is recorded separately below after completion.

### Phase04 final packaged evidence — 2026-10-31

The final archive was tested in three genuinely separate Windows processes using dedicated CR04_TEST_Packaged04Final slots. The runner retained native process handles, waited for actual exit, and checked fresh receipts. No packaged process was force-stopped. Native gameplay movement/fire/reload/trace interactions used existing Enhanced Input and menu handlers; explicitly injected lifecycle faults are identified below. This is automated runtime acceptance, not a human playthrough or UI aesthetic approval.

| Process | UTC start / end | IDs | Actual result |
| --- | --- | --- | --- |
| 1 |23:56:33.498 /23:56:51.451|bootstrap35772, native46016|Cold menu holds pawn; New Game safely starts A; actual CP00 generation1 callback; fight both Wardens, collect ammo, walk to Workshop; CP01 generation2 succeeds; exit.|
| 2 |23:56:51.481 /23:58:05.266|native44696|Read disk from process1, Continue at CP01 with health76/magazine1/reserve35, saved enemy/pickup state; readiness veto holds pawn despite loaded+visible level; all lifecycle cases below; native22s assembly, gunfire/reload and upgraded CP02 generation3; exit.|
| 3 |23:58:05.269 /23:59:12.860|native9760|Read disk from process2, Continue CP02 with health76/magazine5/reserve30, RestorePower objective and upgrade; backtrack C/B/A, reconcile consumed actors/story; Restart preserves disk; real enemy death and three CP02 recovery cycles; upgraded ending; fresh Restart and ending without optional workbench.|

All three fresh acceptance.json receipts report passed=true. Native executable SHA256 is2e1ac14d9c217a122a117e199937e14f920f73288dfbb9ad3338078450688bdc. Route1/2/3 receipts have distinct files under package/Windows/CinderRelay/Saved/Phase04/{1,2,3}. CP02's saved marker is(4050,0,-40.18861); CharacterMovement settles safely to(4050,0,-49.767), as recorded at release. Neither arbitrary free-position restoration nor teleporting before collision readiness is used.

Lifecycle coverage in process2: no checkpoint during active assembly; explicit Skip grants once; injected lethal damage aborts; destroying the presentation actor aborts; Restart causes world EndPlay cleanup; destroying the player controller releases ownership; native SequencePlayer Stop aborts without upgrade; pause freezes playback; natural OnFinished grants once and returns controls. The sequence assets and its Stop/Skip/OnFinished distinction were preserved. Each fault starts from restored CP01; repeated assertions within a stage are not additional cases.

Data/failure coverage: two native Automation groups (Schema and DiskFallback) passed after the final review fixes, exit0. Tests exercise real native serialization/async disk I/O and dedicated test slots: missing files, malformed values, unknown/duplicate IDs, unsupported version, bad checkpoint/zone pairs, corrupted newer slot with earlier valid fallback, native failed write with no false success, bounded coalescing, interrupted queued request, stale callback feedback, and idempotent restored sets/flags. No player save was corrupted/deleted. Rejected files remain available for diagnosis; Continue is unavailable if neither slot validates. A failed write cannot promote Latest, and new-game CP00 does not overwrite existing/corrupt slots.

Representative actual logs (timestamps retained in raw logs):

```text
CR04_SAVE WriteCompleted success=1 generation=1 checkpoint=CP00_START_YARD epoch=2 latency_ms=9.160
CR04_SAVE WriteCompleted success=1 generation=2 checkpoint=CP01_WORKSHOP_ENTRY epoch=2 latency_ms=13.244
CR04_ROUTE PASS Loaded and visible alone cannot release pawn while readiness is vetoed
CR04_RESTORE SafeControl checkpoint=CP01_WORKSHOP_ENTRY zone=1 objective=1 health=76.0 magazine=1 reserve=35 upgrade=0 reconstruction_ms=37.199 position=X=2050.000 Y=0.000 Z=98.150
CR04_SAVE WriteCompleted success=1 generation=3 checkpoint=CP02_RELAY_ACCESS epoch=8 latency_ms=12.083
CR04_RESTORE SafeControl checkpoint=CP02_RELAY_ACCESS zone=2 objective=2 health=76.0 magazine=5 reserve=30 upgrade=1 reconstruction_ms=25.158 position=X=4050.000 Y=0.000 Z=-49.767
CR04_FINISH {"passed":true,"route":3,"journey":4,"message":"Checkpoint recovery, backtracking, death retry, restart and optional ending passed"}
```

Exit-code investigation was bounded within these launches: route1 bootstrap and native both returned777003; direct native launches2/3 also returned777003. All native logs requested RequestExitWithStatus(0) and reached LogExit/closed logs. Thus777003 is not explained solely by the bootstrap wrapper. A targeted installed Launch/Windows source search did not find the numeric code; bootstrap program sources are not included in this installation. A later separate interactive UI check, without route automation/unattended/trace flags, exited0 through the actual Exit Game button. These conditions differ, so the specific cause of the automated runs'777003 remains unresolved. AutomationTool exit0, automated native/bootstrap exit777003, interactive native exit0, and gameplay receipt PASS are separate facts. No renderer changes or engine reinstallation were attempted. Earlier Editor-game receipt-bearing processes hung on exit and were explicitly stopped; they are not clean process-exit evidence.

Asset/source audit: exactly3 checkpoint actors were added via real Editor APIs; all170 earlier actor snapshots match. Of70 baseline Content/ArtSource files, only the intended L_CH01_Persistent.umap changed. Original Phase01A rollback map, all three streamable maps, Phase02 assets and Phase03 .blend/animation/sequence bytes remain unchanged. No new binary asset other than the updated persistent map, no new external resources, no config/engine/module rename. Compiled runtime additions are CRChapterSaveGame, CRChapterSaveSubsystem, CRCheckpoint and the Development-only CRCheckpointRoute; CRCheckpointTests contains focused Automation. Existing GameMode, streaming controller, PlayerController/HUD, health and weapon receive narrow integration changes.

Reproducibility manifest:126 Source/Config/Content/uproject inputs, SHA256 of validated-inputs.json=68b02fe9b10019c84bbe67a63cc62c27842625be5a9f89fe94fa19da94a98d44. Bootstrap executable SHA256=7a5dd7bf366ea691cdd22b56033da87b77477cb4338a8c677e9444f7fb792de1. Original Phase01A map SHA256=c22ac1dafe74f3006ca8f2498e7ad81ba8ac827890c44b3554f31d0d13d3e733. Full artifact/receipt hashes are in ignored delivery-hashes.json, and process-results.json SHA256=17d7a8c4be1e261705c8d72a5c34dd86ede3e9cca46db812d28257ca3f96a39f.

Evidence root: .environment-local/phase-04/. Final build-review-fixes.log, final-state-tests.log, package.log, packaged-route{1,2,3}.log, process-results.json, packaged-summary.json, route3.utrace, insights-game-thread.csv, insights-frames.csv, asset-hash-audit.json and validated-inputs.json remain local/ignored. Scripts/run_checkpoint_acceptance.ps1 orchestrates the bounded fresh-prefix route; summarize_checkpoints.py reads existing evidence without running the game. See PERFORMANCE_BUDGET for actual timings, startup/recovery hitches and memory limits.

Remaining limits:
- After the owner dismissed the Windows firewall prompt, a separate Visual04 native process was visually inspected with real mouse clicks: missing-save Continue disabled; New Game starts safely; Esc exposes Resume/Continue/Restart Chapter/Exit; Continue restores CP00 with visible CHECKPOINT RESTORED. Bottom controls and health/ammo fit the observed window. Screenshots ui-restored.jpg and ui-paused.jpg are actual1283x751 window captures, not substituted renders. Native save callback and restore logs agree; Exit Game returned0. This UI check is separate from measured routes. Death-menu layout, other display sizes and the full human playtest remain unreviewed; no security setting was changed by automation.
- Direct forced native sublevel unload during active assembly was not separately injected. Actual actor/controller destruction and world EndPlay were tested; normal streaming cannot unload occupied Workshop while locomotion is locked. Source cleanup is not proof of every forced whole-level teardown path.
- Mid-reload process termination was not a separate runtime scenario. Restored Ready state/timer absence and subsequent normal reload were checked; snapshots reject active reload. No endurance, physical power-loss or arbitrary corruption fuzz test was performed.
- Startup/controlled-recovery stalls remain. Three fast recovery cycles and1Hz memory sampling cannot prove leak freedom. The previous Phase03 animation quality limits remain; no new claim of polished realistic hands or clean60FPS.

Recommended next scope, subject to owner authorization: a short manual checkpoint/menu/death-recovery playtest, then Phase05 focused on observed presentation issues and a same-quality investigation of controlled-load hitches and abnormal exit status. No new chapter, weapons, save framework or automatic Phase05 implementation.


## Phase05 Vertical Slice Polish — implementation plan and ledger

Goal: an original, coherent Dead Station art/presentation pass with preserved Chapter01 gameplay and schema1 persistence. Spec: owner's Phase05 brief sections0–24, plus ART_DIRECTION.md. Baseline PR5 is merged at67a559bf0f573f9b86bfa1b401569cc8530de75e; clean main fast-forwarded; branch phase-05-vertical-slice-polish. UE5.8.4/module unchanged. Owner confirmed the previous playtest ended and authorized closing the old game; no old game window remained.

Architecture: original editable Blender kit -> verified FBX imports and shared native UE materials -> decorative actors in their existing native sublevels. Old collision/anchors/gates remain authoritative. Existing cosmetic weapon/enemy hooks receive presentation changes only. One localized zone-presentation actor supplies native audio/Sequencer/objective reactions; existing PlayerController/UMG owns subtitles and end-screen behavior. No schema change/new persisted IDs, generic narrative framework, new renderer or streaming replacement.

Review focus: (1) cosmetic geometry must not invalidate checkpoint floor traces, interactable LOS, flank routes or NavMesh; baseline structural snapshots plus real packaged route own this check; (2) cosmetic callbacks must not alter damage/ammo or grant an upgrade on Abort; existing checkpoint/lifecycle routes own it; (3) restored state must settle environmental effects without replaying story/cinematics; CP01/CP02 process restart owns it; (4) native sequence/audio teardown on ending, pause, Restart and EndPlay must not lock controls or retain streamed actors; focused lifecycle validation owns it; (5) new references must be cooked and stay zone-local; packaged appearance/ownership checks own it.

- [x] 05A: docs/ART_DIRECTION.md; Scripts/audit_polish.py; ArtSource/Blender/Phase05/create_environment.py and CR05_IndustrialKit.blend; Scripts/generate_polish.py. Produce the Rail Yard entrance first, stable original mesh/material paths under /Game/Generated/Phase05, then real Unreal render inspection. No full chapter population before this check. Verify authored dimensions/triangle/material counts and imported bounds, old actor/gameplay snapshot, source hashes. No gameplay C++ build for color/mesh-only changes.
- [x] 05B: extend the same original kit/owned placement script to Workshop and RelayBunker. Preserve all original transforms/collision/IDs and ensure new decoration is no-collision/non-nav. Place warm practicals, service props/cables/records, readable original interactables and consistent bunker equipment. Audit zone ownership and focused floor/navigation/streaming checks. No new world layout or checkpoint moves.
- [ ] 05C: ArtSource/Blender/Phase05/create_warden.py, refine_restoration.py and separate editable .blend sources; native import script for skeletal clips and improved22s restoration. Modify CRAshWarden cosmetic event responses and CRWeaponViewComponent appearance/motion/audio only. Keep collision/head-hit components and UCRWeaponComponent authority; retain fallback mesh. Inspect continuous playback plus meaningful frames; no old-source rewrite or full-kit regeneration for pose edits.
- [ ] 05D: localized CRZonePresentation.{h,cpp}, actual native light/audio sequence tracks, original synthesized audio sources/register, existing controller/HUD integration. Opening is a player-controlled reveal; Relay objective triggers real staged lights/audio; end-screen remains original text and waits for successful presentation completion/Skip safely. Nonpersistent visual/clue events only, no new saved IDs. Check UMG at1920x1080 and2560x1600 and minimal settings only if practical. No new story canon.
- [ ] 05E: extend existing actual-input route/evidence scripts narrowly; one relevant Editor build after C++ integration, focused schema/lifecycle checks, one integrated Windows Development BuildCookRun and bounded actual-input route including real process restart. Separate low-overhead representative views/transition and diagnostic trace. Preserve actual p50/p95/p99/hitches/memory/settings. One final independent whole-branch reviewer; fix important issues with targeted checks, no review loop. Inspect hashes/LFS/staging, coherent commits, push and PR main; no merge/Phase06.

Ruling: execute the owner's detailed production brief inline in the existing authorized checkout, using writing-plans/executing-plans with this established ledger. The brief already authorizes native asset/source creation and PR delivery; do not add redundant design/individual-write approval pauses or a parallel plan/package system. Use original project-authored Blender/FBX/UE sources with provenance manifests rather than paid generation or third-party packs. Cost: original procedural assets may remain visibly prototype-quality, which must be inspected/reported and subjected to owner visual acceptance.

Ruling: preserve the accepted22s duration and Phase03 original bytes. Create a targeted Phase05 derivative for hand/weapon edits and point the existing workbench at validated replacement assets. Cost: both versions remain in source/cook references until explicit later cleanup; no destructive cleanup in this milestone.

05A preflight: game-dev1.0.2 doctor found local Blender4.5.11LTS and no configured paid providers. Its default catalog points to another project, so no catalog/provider writes are used; explicit local Phase05 paths drive Blender and real Unreal APIs. No external downloads or paid invocations. Baseline hashes and four original map backups are in ignored .environment-local/phase-05.

Phase05 work ledger (2026-10-31, in progress; not final acceptance):

- 05A actual Unreal renders inspected at1920x1080. First pass was too sunny/empty; targeted roof winding, steel gantry and palette changes followed. Second pass revealed overexposed entrance lights; explicit420 lumen units removed the blown facade. Third pass established the overcast/cold-vs-warm direction; final whole-scene brightness and human aesthetics remain pending. Local comparison: yard-v1.png, yard-v2.png, yard-representative.png. Images are real Editor renders, not gameplay/performance proof.
- 05B native placement saved102 owned cosmetic/environment actors and preserved all173 original actor structural snapshots. Imported mesh bounds match authored centimeters. Wardens and workbench presentation changes are audited separately; no native gameplay floor/gate/checkpoint moved. Original14-mesh environment kit includes a18516-triangle maintenance railcar. Small512px original surface textures replace flat primitive materials.
- 05C Blender actually wrote CR05_AshWarden.blend (18 authored bones,11696 triangles, six clips) and CR05_RookRestoration.blend (targeted derivative,39 authored bones,22s action). Imported native rigs have19/40 bones including the FBX armature root. Actions imported with lengths3/1/1.1/.4/.4/1.8s plus22s restoration. Left thumb is mirrored inward; elbow solve preserves limb lengths with an off-camera shoulder reach; stable grip curves replace sinusoidal curl. This remains segmented prototype anatomy, not final anatomical animation. Native import warnings about bind-pose fallback and smoothing require visual review.
- 05D actual LS_CR05_RelayPower4s and LS_CR05_RelayEnding8s contain native light intensity/audio tracks. Eleven original deterministic sound files were synthesized/imported. No downloaded audio, voice acting or new persisted IDs. Existing22s workbench lifecycle remains authoritative. A generation token prevents stale deferred MovieScene callbacks from finalizing a newer presentation. Opening is a player-controlled environment reveal with provisional subtitles.
- First CinderRelayEditor compile: Succeeded,55.29s,12 actions. A narrow legacy-route adaptation compiled successfully in24.03s; it now waits for the actual ending instead of asserting completion after1s. No engine rebuild. Further C++ generation-token correction requires one affected-target check before runtime testing.
- Editor API corrections were evidence-based and isolated: use set_editor_property for editor-only sample-rate setting, and read StaticMeshComponent.static_mesh rather than a nonexistent get_static_mesh. Native asset creation receipt: presentation-assets.json. Editor process exit0 alone was not accepted as evidence when Python failed.

Ruling: the owner's explicit bounded validation plan takes precedence over a generic repeated red/green rebuild loop for cosmetic content. Use actual import/ownership/collision checks, one integrated route and focused lifecycle assertions; no test scaffold that mirrors Blender geometry or repeated full builds for material edits. Final human aesthetics/pacing remain a separate acceptance gate.

### Phase05 final local evidence and review boundary

Asset audit:173 original actors retained with no differences in protected class/world transform/collision/component structure/zone ownership.107 added actors: Persistent1 (atmospheric haze), RailYard36, Workshop39, RelayBunker31. All95 new StaticMeshActor decorations reopen with NoCollision and navigation disabled. CP00(-1450,0,110), CP01(2050,0,110), CP02(4050,0,-40.18861) remain unchanged. Original Phase03 source, Phase01A rollback and schema1 implementation hashes match the pre-edit inventory. Seventy actual new Unreal assets occupy12,354,801bytes before cook; three editable .blend sources total13,899,143bytes. Final receipts: asset-validation.json, contact-render-review.json, presentation-assets.json.

Native Editor compilation:55.29s initial,24.03s legacy-route ending-wait adaptation,41.82s presentation lifetime/visual-shell integration,45.74s final review fixes; all succeeded. These were justified project-target checks after distinct C++ changes, not engine rebuilds. Final native Automation3/3 passed: Checkpoints.Schema, Checkpoints.DiskFallback, Restoration.Session (final-state-tests.log, process exit0). Installed engine startup still prints previously documented automation condition errors outside these tests; this is not a clean-log claim.

One integrated real PIE route passed: optional yard salvage, actual combat/damage/death, duplicate component prevention, prerequisite rejection, Stop/Abort, Skip, natural22s assembly with pause, upgraded ADS/fire/reload, unloading/backtracking reconciliation, chapter Restart, and both upgraded/bypass objective endings. Fresh editor-smoke/acceptance.json reports passed scenario4; actual light samples recorded264 values from0 to692.0085 with84 distinct rounded intensities. Both native relay sequences played with real tracks, not a synthetic completion delay. PIE evidence is separate from packaged persistence and human art acceptance.

The fresh whole-branch reviewer found two P2 issues and no P0/P1: ending presentation could still accept Jump; ambient loop endpoints had a discontinuity. StartJump now honors the existing weapon presentation lock. Three loop files were regenerated with a short tail/prefix blend and reimported alone. Boundary step/RMS ratios are0.351/0.393/0.681 for Yard/Workshop/Bunker, compared with the earlier Bunker6.9. This digital seam check does not substitute for a listening review.

A saved collision audit caught BlockAll profiles overriding transient NoCollision settings on reopen. The focused repair sets the native profile, enabled state and navigation flag;95/95 decorative meshes passed after actual reload. Other isolated Editor binding corrections used installed APIs rather than repeated whole builds. Final contact screenshots initially failed only in an optional bone-metadata query after a valid render; removing the unsupported diagnostic allowed all four actual Unreal frames (3/7/13/18s) to complete, exit0. No animation regeneration/rebuild was performed for that metadata repair.

Visual review: actual1920x1080 Rail Yard, Workshop, Bunker and four contact poses were inspected. Corrected roof winding, light units, cabinet/rack facing after observed FBX Y handedness, oversized glowing terminal primitives, duplicate billboard labels, hand reach/contact keys and a320lumen workbench task light. The final hand poses are clearer and the props continuous in authored keys, but gloves remain segmented, grasp silhouettes and cloth/metal surfaces coarse, Warden transitions use direct clips, and original room shells remain evident. Static images do not prove natural temporal motion. Native full playback ran; no genuine video recording or complete human motion/pacing acceptance is claimed.

Remaining aesthetic gate: owner review at normal gameplay speed, weapon feel, audio mix, continuous hand/enemy motion, route readability and naturally timed12–16minute pacing. The compact chapter has not been demonstrated to meet that duration; no artificial waits/movement slowdown were added. No new settings framework, voice acting, story canon, persisted IDs, weapons or Phase06 content was introduced.


Final packaged acceptance: one BuildCookRun141.84s, exit0. Three separate processes, fresh `CR04_TEST_Phase05_20261031Final` slots; route1 pid57400 (bootstrap60496), route2 pid46732, route3 pid63440. All fresh receipts passed, all native and bootstrap exits0, no forced stops. CP01 restored health68/ammo1+35/objectiveFindModule/enemy and pickup IDs; CP02 restored health68/ammo5+30/SurveyUpgrade/objectiveRestorePower. Actual readiness veto held the pawn, three recovery cycles and native reverse unload passed. Route2 explicitly exercised Skip, lethal interruption, presentation actor destruction, Restart/world EndPlay, controller destruction, genuine Stop, pause and natural completion. Route3 used real combat death/Retry and reached both upgraded and optional-bypass endings through ordinary interaction rules. No objective assignment shortcut. Fresh process results and logs are under packaged-acceptance; user slots were never touched.

Native A->B initial preload request-to-ready17ms; initial B->C20ms. Cold initial A196ms, cross-process B156ms; readiness derives from actual native loaded/visible/collision state. Later backtracking/unload events are in load-latencies.json and polish-summary.json. The transient gate and persistent player architecture were not rewritten.

Packaged relay Power4s and Ending8s ran naturally on both ending paths. New ending-specific Tab/pause/restart interruption remains source-reviewed but not individually injected in this acceptance route; do not conflate the thoroughly tested workbench lifecycle with those new cosmetic-ending cases. Final human visual/pacing/audio review remains pending. No next milestone begins automatically.


Interactive HUD follow-up completed on2026-10-31 after the owner dismissed the Windows firewall prompt. No security/network settings were changed by automation. The same packaged executable was inspected at native1920x1080 windowed and2560x1600 fullscreen (native RHI resize logs confirm both). Actual New Game, Esc/pause, Continue toCP02, Restart Chapter and Exit Game clicks worked. Bottom controls, health/ammo, objectives and menu labels fit at both resolutions; the1600p opening subtitle also fit without covering critical HUD. Windows150% scaling explains logical screenshot sizes1283x751 with window chrome and1707x1067 fullscreen. This is a bounded layout/menu check, not a new performance or full-route run. No rebuild or repackaging occurred.

Evidence: `.environment-local/phase-05/ui1080-visible.log`, `ui1080-visible-exit.txt` (native exit0), `ui-validation.json`, `ui1080-newgame.jpg`, `ui1080-pause.jpg`, `ui1080-continued.jpg`, `ui1600-gameplay.jpg`, `ui1600-pause.jpg`, `ui1600-opening.jpg`. The test used only the existing dedicated CR04_TEST_Phase05_20261031Final slots; the latest generation5 was the prior bypass route's CP02 (health76/ammo1+25/upgrade0), not the earlier upgraded generation. No player save was touched. New Game/Restart preserved that stored generation. The initial hidden UI-only process had been explicitly stopped before the visible session; it is not counted as a clean exit. Final visible session exited0 through Exit Game and is now closed. Death-menu/long-interaction-prompt variants and complete human visual/pacing/audio acceptance remain separate unverified coverage.


## Phase05.3 — human arms and handling (active candidate)

Owner approved anatomical/skin/fingerless-glove direction and continuation. Research and licensing, actual human-rig import, seven handling clips, once-only cosmetic case cues, visible feeding-unit reload, workbench retarget and native camera Stop restoration are implemented. UCRWeaponComponent, schema1, checkpoint IDs, native streaming and previous rollback assets remain unchanged. Current scoped native weapon fixture, corrected sight fixture and Presentation3/3 automation pass. Full executed evidence and limitations are maintained in FIRST_PERSON_05_3.md. Final package, continuous video and human motion-quality acceptance are separate gates, not implied by these checks.
