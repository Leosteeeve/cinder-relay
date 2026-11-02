# CINDER RELAY — Asset Sources and Licensing

## Phase05.5 original identity and audio

- Original Blender/Cycles environment-led title artwork, two camera compositions, editable SVG typography, relay mark and four item symbols. Editable source: `ArtSource/Blender/Phase055/CR055_TheLastSignal.blend`; outputs and per-file metadata: `ArtSource/Interface/Phase055/`. Source authoring uses original geometry plus read-only appended project-authored Phase052 props. No reference-game pixels or image-generation-service output is admitted. [Full art provenance](PHASE055_ART_PROVENANCE.md).
- Barlow Regular/Medium and Barlow Condensed SemiBold by Jeremy Tribby, **SIL Open Font License1.1**. Official pinned source URLs, hashes and OFL text are preserved under `ArtSource/Interface/Phase055/Fonts/`. Public source redistribution is permitted under the retained OFL conditions; no font names were changed.
-44original deterministic PCM effects/loops, authored by this project without external samples. `ArtSource/Audio/Phase055/author_audio.py` and `manifest.json` retain source URL, author, usage, modification, SHA256 and public-repository permission for every output. Eight earlier original sounds and three sequences have explicit Phase055 derivatives; historical originals remain unchanged. No separate standalone asset license is granted for project-original work.
- Official Kenney CC0 packs were researched but not acquired as valid audio bytes; no Kenney sounds are represented as integrated. Sonniss and Mixkit source redistribution restrictions exclude them from public extractable assets. No Freesound sample, purchased material, copyrighted music or voice performance is included. [Exact license research and acquisition limits](PHASE055_AUDIO_RESEARCH.md).
- Native UE assets were created with the actual5.8.4 Editor:12interface assets,70audio assets and3sequence derivatives. Only three existing sublevels change their seven audio-owner references. Original art/cleared fonts/audio are intentional source; captured media, tests, SaveGames, packages and raw research references remain ignored local evidence.

## Phase05.4 original utility kit and feedback reuse

No new external acquisition, marketplace pack, paid provider, audio sample or texture download. `ArtSource/Blender/Phase054/author_utility_kit.py` and `CR054_IndustrialUtilities.blend` contain original project-authored ToolWall, ServiceShelf, OverheadServices, ElectricalPanel, PneumaticSkid and TracksideService geometry.19,772 source triangles total, six native static-mesh imports with centimeter bounds checked. Source helper functions are reused from the original Phase052 script without executing that generator or changing its source. UE5.8.4 imported paths are `/Game/Generated/Phase054/Meshes/SM_CR054_*`.

Materials reuse registered Phase052 originals and Phase051 CC0 rusty-metal textures; no new texture residency is requested. Existing original shot/hit/impact audio is reused at bounded gain/pitch. The small muzzle cone is an engine basic shape referencing the existing project lamp material; engine source/raw packs are not redistributed. Intentional project-owned `.blend`/`.uasset` derivatives use Git LFS; FBX intermediates, local media and packaged builds remain ignored. No separate standalone asset license is granted for original project additions. Actual import/placement evidence is in the Phase05.4 report; human art acceptance remains separate.


## Phase053 anatomical review kit

- **Used:** [MakeHuman graphical data](https://github.com/makehumancommunity/makehuman/tree/a8bc2d54ff0ac92e78ff71431b1023eda42bf482), **CC0-1.0**, zero purchase cost. Base geometry, default rig/weights and six morphological targets only. Headers credit Data Collection AB, Joel Palmius, Jonas Hauquier and Manuel Bastioni/MakeHuman contributors. Attribution is not required by CC0; credits are retained. CC0 permits derivative/public-source redistribution. No MakeHuman AGPL application code is copied or executed; no external skin textures are used. Exact pinned URLs/hashes and license references: `CinderRelay/ArtSource/Blender/Phase053/{upstream-manifest.json,PROVENANCE.md}`.
- **Original project edits:** fitted fingerless gloves/sleeves, procedural materials and2K atlas baking, independent authoring/export scripts,3-second anatomical keyframes, native review materials/map. Stored as `CR053_EliasArms.blend`, PNG sources and `/Game/Generated/Phase053/Review/` assets. Project ownership is not a new public reuse license; upstream CC0 rights remain intact. Native UE5.8.4 skeletal/animation import and rendered pose checks succeeded; **cooking, gameplay integration and final artistic acceptance remain unverified**.
- **Not acquired:** Davlet FPS Arms01/02 and KINEMATION Pro/Lite. Price/selected license were hidden in listings; no free status, actual retarget compatibility or purchase is assumed. Fab source is not admitted to this public repository. **Rejected:** CC0 WRAD ARMS retro aesthetic does not meet the intended close-up direction. See [candidate comparison and private-integration proposal](FIRST_PERSON_05_3.md).
- Raw pinned CC0 evaluation inputs and export intermediates stay ignored. The native assets and editable derivative are intentional source assets. No marketplace library, account receipt, paid provider job or credential is included. Standalone GLB validation passed; optional canonical packaging remains blocked by a documented Windows `fsync` tool issue, with no false vendoring receipt.

Phase 00 不下载大型第三方资源包、不购买资产，也不将本机引擎复制进仓库。新游戏素材导入前必须登记来源、作者、license、署名和再分发限制。

## 当前来源登记

| ID／内容 | 来源／作者 | 许可与署名 | 再分发限制 | 兼容与证据 |
| --- | --- | --- | --- | --- |
| EPIC-001：生成的 Blank C++ skeleton 与 template 配置 | Epic Games；本机 UE 5.8.4 `Templates/TP_Blank`，由官方 Editor 创建项目；[官方项目创建说明](https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-a-new-project-in-unreal-engine) | [Unreal Engine EULA](https://www.unrealengine.com/en-US/eula/unreal)；保留原文件 Epic 版权注记；最终 credits 按适用条款审阅 | 不把引擎／Starter Content 原始库上传；生成内容与引用资源按各自适用条款处理，不标为 MIT／CC0 | 在 5.8.4 生成，CinderRelayEditor UBT baseline 有成功记录；打包／shipping 未验 |

当前没有外部 Fab 模型、动画、纹理、声音或 raw pack 入库。`/Engine/` 中被模板引用的内容属于引擎安装依赖，不代表已复制到本仓库或许可可独立再分发。通过 Editor 创建的项目自有地图单独记录生成方式；原始地图中的 Engine asset 引用仍需在最终包审核。

## Phase 01A 来源补充

| ID／内容 | 来源／作者 | 许可／署名／再分发 | 兼容与证据 |
| --- | --- | --- | --- |
| EPIC-002：Cube、Cylinder、默认 TextRender 字体／材质 | 本机官方 UE 5.8.4 `/Engine/BasicShapes` 与引擎默认 TextRender 依赖；Epic Games；[Epic Engine Content](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-content-in-unreal-engine) | 适用 Unreal Engine EULA；保留 Epic 署名义务；只引用安装依赖，不复制引擎资源库或独立再分发素材 | 由真实 Editor 用于灰盒；未验证 packaged cook |
| CR-GEN-001：灰盒 map、8 个纯色材质、11 个输入资产、5 个配置 Blueprint | 本项目 `CinderRelay/Scripts/generate_greybox.py`；由本项目制作流程生成 | 项目自有编排，依赖部分仍遵循 Epic 条款；没有附加第三方素材 license 或对外开源许可 | UE 5.8.4 Editor 实际生成／保存，155 个具名对象；运行证据见 MILESTONES |

Phase 01A 未下载／购买外部资源，无 marketplace 运行依赖。所有 `.uasset`／`.umap` 使用现有 Git LFS；截图与原始运行日志保存在忽略目录。生成资产的精确内容 hash 由 Git LFS pointer 记录。

## 今后的必填记录

### Phase 02 additions

| ID / content | Provenance and author | License / attribution / redistribution | Compatibility and status |
| --- | --- | --- | --- |
| CR-GEN-002: Phase02 inputs, tuning data, configured Blueprints, BT/Blackboard, primitive materials and encounter placement | This repository, `CinderRelay/Scripts/generate_combat.py`; original project-authored content, 2026-10-31 | No external asset license; project has not granted a standalone public asset license. Engine primitive dependencies remain under Epic's EULA, not relabeled CC0/MIT | Generated by the installed UE5.8.4 Editor; exact binary hashes tracked by Git LFS. Actual validation is recorded in MILESTONES |
| CR-AUDIO-001: S_Proto_Shot, Reload, Dry, Hit, Impact, Hurt | Original deterministic mathematical synthesis in the same script; no recordings, samples or external provider | Project-authored prototype cues; no third-party attribution. Raw generated WAV files remain local; the script reproduces them. No external copyrighted samples redistributed | 24kHz mono PCM16 WAV imported as real SoundWave assets by Editor; deliberately placeholder audio, not professional sound design |
| EPIC-003: greybox viewmodel/scout Cube and Sphere references | Epic Games, installed `/Engine/BasicShapes`; [Engine content](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-content-in-unreal-engine) | Unreal Engine EULA; engine source asset library is not copied or independently redistributed | Runtime primitive components, no fabricated skeleton or animations; final cook/runtime evidence is separate |

No Fab download, third-party raw asset pack, purchase or external audio library was used in Phase02. Future Blender work should replace the viewmodel silhouettes through the existing cosmetic component/events; it must have its own provenance record.

每个包记录：资产 ID／本地路径、source URL、作者／提供者、版本和获取日期、原文件 SHA256、完整 license 名称／版本／条款 URL、署名文本／位置、修改记录、redistribution 限制、允许的 repo 可见性、宣称引擎兼容、实际 UE 5.8.4 import／cook／runtime 证据、负责人和状态。

状态：candidate → license-cleared → import-tested → accepted，或 rejected。许可合规不能替代技术兼容，导入成功不能替代使用权。未知许可不下载／不导入；免费与可搜索到不等于可商用。

## 准入与仓库政策

1. 优先原作者／官方发行渠道，验证来源链。禁止游戏拆包、搬运站或无许可 copyrighted 内容。
2. 查骨架、比例／坐标轴、LOD、碰撞、材质、纹理预算、音频格式与插件版本。仅导入当前里程碑需要的资产，隔离每个外部包的目录。
3. 许可与收据存入合适的受控位置；不提交个人／支付信息或账户授权文件。私人 GitHub 也不是无限再分发许可。
4. 不将不必要的 raw asset packs、安装包、模型训练数据或整套第三方库存入 GitHub。必要二进制用 LFS；LFS 不能绕开版权条款。
5. 发布前核验实际 cooked 内容、credits 和 source distribution 范围；未经审查不切换公开仓库。

[Fab 官方许可摘要](https://www.fab.com/eula) 区分 Standard、CC-BY 等。Standard 允许在项目中整合使用，但禁止 standalone 资源再分发；每件商品仍需核对取得时的完整条款与访问级别。不要将某件资产的许可套用到另一件。

Codex 可整理公开证据、文件 hash、依赖和 cook 日志；许可歧义、购买／授权以及实际动画、材质与审美适用性需要相应人工审查。没有证据就标未验证。

## Phase03 original asset register

| ID | Source / authorship | License, attribution and redistribution | Actual compatibility |
| --- | --- | --- | --- |
| CR-ART-003 | Original project-authored `ArtSource/Blender/Phase03/create_restoration.py` and `CR03_RookRestoration.blend`; no external model or generated-provider input | No third-party attribution or asset license. Repository has not granted a separate public asset license; preserve project ownership. Blender's software license is not substituted as the artwork license | Blender4.5.11LTS;39authored bones,6720skinned vertices; baked22s/30fps action. FBX importer and coordinate/collision evidence in MILESTONES |
| CR-ANIM-003 | Same editable source; real weighted segmented gloves, separate weapon/optic bones, original keyframed performance | Same project authorship; not motion-capture, not final anatomical animation; no third-party raw pack | `/Game/Generated/Phase03/Animation/AN_CR03_RookRestoration`, skeletal mesh/skeleton and native Level Sequence |
| CR-AUDIO-003 | Original two-tone mathematical synthesis in `Scripts/generate_restoration.py` | No samples, recordings, music or third-party attribution; no standalone asset-license grant |24kHz monoPCM16, real imported `S_CR03_Calibration` SoundWave |
| CR-MAT-003 | Six original constant-color native materials generated by the same Editor script | Same original project content; Epic engine implementation remains under its own EULA | Explicit skeletal usage flags; no textures or additional rendering features |

Intentional .blend/.uasset/.umap files are Git LFS assets. Reproducible FBX/WAV intermediates, render captures, packaged builds and traces remain under ignored local directories. Exact binary versions/hashes are in Git LFS; do not treat an import receipt as packaged or aesthetic acceptance.
# Phase05 original production register

All Phase05 additions are original project-authored geometry, keyframes, procedural textures and deterministic audio synthesis. No paid providers, marketplace packs, ripped assets, third-party samples, voice recordings or music were acquired. Public-repository compatibility derives from original authorship; engine/editor tools are not redistributed.

| Source / provider | Editable source | Imported assets | License / attribution / restrictions | Verification |
|---|---|---|---|---|
| Cinder Relay Phase05 original industrial kit | `ArtSource/Blender/Phase05/CR05_IndustrialKit.blend`, `create_environment.py`, `refine_environment.py`, `create_terminals.py` | `/Game/Generated/Phase05/Meshes/SM_CR05_*` | Original project work; no external attribution obligation or third-party redistribution condition. Repository license, if any, governs public reuse. | Blender4.5.11 export; real UE5.8.4 import; centimeter bounds checked; Windows Development cook passed. |
| Cinder Relay original surface synthesis | `create_surfaces.py`, `T_CR05_SurfaceMask.png`, `T_CR05_SurfaceNormal.png` | Phase05 Textures, shared environment/actor Materials | Original deterministic texture source, no source photographs or downloaded textures. |512px masks/normal; native material import and actual scene renders inspected. |
| Cinder Relay original Ash Warden | `CR05_AshWarden.blend`, `create_warden.py` | `SK_CR05_AshWarden`, six `AN_CR05_Warden_*` clips | Original cloth/armor/rig/action source. ROOK exterior derives only from this project's preserved Phase03 source. |18 authored/19 imported bones,11696 triangles; actual import. Actual native playback and gameplay route passed; human motion-quality acceptance pending. |
| Cinder Relay original restoration derivative | `CR05_RookRestoration.blend`, `refine_restoration.py`, `refine_rook.py`, `tune_restoration_contact.py` | `SK_CR05_Restoration`, `AN_CR05_RookRestoration`, `SM_CR05_Rook5`, `SM_CR05_SurveyOptic` | Derived from original Phase03 source, whose bytes remain protected. No external motion capture/character assets. |39 authored/40 imported bones;22s real native animation; visual acceptance pending. |
| Cinder Relay original synthesized audio | `create_audio.py` (seed211805) |11 `S_CR05_*` SoundWaves | Original equations/noise; no external samples. No voice acting. |32kHz mono16-bit, normalized peak0.7 before mix, native import. Windows cook and native runtime playback passed; human spatial listening/mix acceptance pending. |

Audio provenance: YardWind(8s), WorkshopHum(8s), BunkerHum(8s), RookShot(.65s), Impact(.35s), Reload(2.4s), FootYard(.24s), FootMetal(.28s), PowerRise(4s), SignalEnding(8s), Calibration(.8s). First three loop through native zone-owned AmbientSound components with attenuation/occlusion; weapon events remain authoritative for gun cues, existing movement cadence drives footsteps, and native Sequencer tracks own relay sounds. Raw exported FBX/WAV files are reproducible ignored intermediates, not source-control payloads.

## Phase05.1 authored assets and limited CC0 inputs

Selection rationale and all owner candidate URLs: [ASSET_SELECTION_05_1.md](ASSET_SELECTION_05_1.md). Fab candidates remain research-only; no purchase, protected download, or marketplace source is included in this public repository.

| Source | Author / exact license | Included content | Public repository / attribution |
|---|---|---|---|
| https://polyhaven.com/a/wood_table_001 | Dimitrios Savva (photography), Rico Cilliers (processing); CC0-1.0 | Only 2K JPEG Diffuse, ARM, DirectX normal | Redistribution allowed by https://polyhaven.com/license; attribution voluntary, retained here |
| https://polyhaven.com/a/rusty_metal_02 | Rob Tuytel; CC0-1.0 | Only 2K JPEG Diffuse, ARM, DirectX normal | Same CC0 treatment; no whole library or unrelated files |
| `ArtSource/Blender/Phase051/CR051_Rook5.blend` | Original project-authored fictional exterior | Contoured stock/receiver, thin-wall optic, lens-bound reticle, native sight anchors | Project-owned source; no functional firearm internals or copied commercial model |
| `ArtSource/Blender/Phase051/CR051_IndustrialDepth.blend` | Original project-authored | Curved/sawtooth roofs, damaged perimeter, silo/water tower/chimney, exterior-only distant district | Project-owned; no high-rise interiors or third-party packs |
| `ArtSource/Blender/Phase051/CR051_RookRestoration.blend` | Original derivative of retained Phase03/05 project source | Connected glove surfaces, two-bone IK, prop-relative contact targets, baked skeletal action | Project-owned; uses the separately registered CC0 hero materials |

`CinderRelay/ArtSource/Textures/Phase051/provenance.json` records each exact publisher download URL, file size, publisher MD5 and independently checked SHA256. Source images total approximately6.1MB. Material texture import is real UE5.8.4 import, with DX normal compression and non-sRGB ARM. Final cook/runtime status is recorded in MILESTONES, not inferred from license or format compatibility.

Local recording tool only: imageio-ffmpeg0.7.0 Windows wheel from the publisher's PyPI metadata, SHA256 checked; wrapper BSD-2-Clause and bundled FFmpeg's own reported build license are separate. Ignored `.environment-local/phase-05-1/tools/provenance.json` retains the download record. No recording executable/wheel is shipped, committed, or treated as a game asset.

## Phase05.2 original derivatives

No new external acquisition, paid provider or marketplace package. Existing Phase051 CC0 rusty_metal_02 maps and original Phase05 mask are reused; their licenses/authorship above are unchanged. All added geometry, poses and synthesized cues are original project work, without a separate public asset-license grant.

| Source | Actual imported content | Authorship / compatibility |
|---|---|---|
| `ArtSource/Blender/Phase052/CR052_YardDetail.blend`, `polish_environment.py` |11 `SM_CR052_*` meshes, original native master/instances/decal | Original modeled railcar, entrance, industrial service props and exterior midground kit;61,004 source triangles total. Blender4.5.11, real UE5.8.4 FBX import and bounds check. No external model pack. |
| `ArtSource/Blender/Phase052/CR052_RookRestoration.blend`, `polish_contact.py` | SK/AN/skeleton and `LS_CR052_RookRestoration` | Editable derivative of project-owned Phase051 source;39 authored/40 imported bones,106,828 triangles,22s. Original weapon/skeleton source retained. Actual poses inspected; human motion-quality acceptance remains pending. |
| `ArtSource/Audio/Phase052/S_CR052_Seat.wav`, `S_CR052_Secure.wav`, `provenance.json`; generator `create_contact_audio.py` | Two SoundWaves and native sequence sections | Original deterministic additive/noise synthesis,48kHz monoPCM,0.26s/0.38s. No samples, music, voice acting or third-party attribution requirements. Quiet fictional calibration sounds, not authentic recorded machinery. |

The29 Phase052 Unreal assets were included in the successful Windows Development cook. Editable .blend sources and intentional tiny original WAV sources use LFS; exported FBX, build outputs and raw local capture directories remain ignored. Selected review media is published separately with provenance and no claim of final artistic acceptance.


### Phase05.3 integrated derivatives

CR053_FirstPerson.blend and CR053_RookRestoration.blend derive from the registered CC0 MakeHuman graphical anatomy and original project clothing/rig/action work, not MakeHuman AGPL program code. No Fab pack or paid service was acquired. Existing Phase051 CC0 wood/metal and original Phase052 sound cues retain their registered provenance. Editable sources pack their available image dependencies; FirstPersonTextures contains two original2K baked atlases. Source-side IK/keyframes and seven native handling clips are original project authoring.

Gameplay meshes/animations/materials/textures live under /Game/Generated/Phase053/Gameplay; the separate22s workbench derivative under Phase053/Assembly. Actual Blender4.5.11 exports and UE5.8.4 imports/bone checks passed. Gameplay arm source33,121tri/3materials; joined workbench92,165tri. Public distribution is limited to these project-owned/CC0 inputs; imported engine runtime code/tools and optional recording executable are not redistributed. No standalone commercial asset license is implied for original project additions.

Reload correction: `ArtSource/Blender/Phase053/CR053_FirstPerson_ReloadCorrected.blend` is an original action-only derivative of the same registered source. It preserves all seven previous actions with `_Rollback_PreReloadFix` suffixes. Mesh topology, UVs, skin weights, materials, rest matrices and bone names are unchanged. No new external assets/licenses or paid resources were used. The original three Phase053 Blender files remain byte-identical; temporary FBX exports and real review media stay in ignored local evidence storage.

## Phase06 original chapter mechanics

`ArtSource/Blender/Phase06/CR06_ChapterMechanics.blend` and `author_chapter_kit.py` are original project geometry authored in Blender4.5.11. Five actual UE5.8.4 StaticMeshes under `/Game/Generated/Phase06/Meshes` provide the roller shutter, isolation door, door frame, diagnostic panel and machinery shuttle: **11,124 source triangles total**. Native import verified centimeter bounds. `provenance.json` records editable-source SHA256, sizes and per-mesh dimensions/triangles. No downloaded model, paid provider, new font, texture or audio sample is included. Original project-owned content is authorized for this public repository; this does not grant a separate standalone asset license.

Materials reuse the registered original Phase052 Steel/Paint/Dark/Amber/Pale instances. Yard cover skins reuse project-original Phase05/052 meshes. Mechanical feedback reuses the already registered original Phase055 resident `FeedIn`, `FeedOut`, `ReloadComplete` and `Dry` cues; no restricted source pack is introduced. Existing font/audio/image provenance remains unchanged. `.blend` and native `.uasset`/`.umap` use existing Git LFS. Temporary FBX exports, captures, profiling traces, saves and packaged builds stay under ignored local storage.

The owner-reported bunker shuttle support correction is original native level assembly in `Scripts/chapter06_access_frame.py`: ten scaled references to `/Engine/BasicShapes/Cube` with the already registered Phase052 materials. It adds guides, a head enclosure and wall connections with a permanent service opening. No engine asset file is copied into project source, no new third-party download or license is introduced, and only the existing RelayBunker map stores the authored placement. Raw before/after captures remain ignored.
