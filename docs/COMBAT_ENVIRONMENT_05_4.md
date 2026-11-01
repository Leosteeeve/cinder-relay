# Phase05.4 implementation and acceptance

**Goal:** Improve accepted ROOK-5 combat feedback, add bounded grounded sliding, and curate existing industrial interiors without changing progression or first-person identity.

**Architecture:** A small CharacterMovementComponent specialization changes slide velocity only; native walking, floors, capsule sweeps and crouch remain authoritative. Existing weapon events drive cosmetic recoil and differentiated hit/kill feedback. Zone-owned noncolliding art uses existing original/registered materials. No new persistent identifiers, managers, plugins or movement mode.

**Baseline:** PR9 merge `811aaa5f8921fce4c9bbcc125cfaa2e039693836`; branch `codex/phase-05-4-combat-slide-environment`; UE5.8.4. Schema1, CP00/01/02, combat damage/ammunition, 0.9s cycling, 2.4s reload, ADS65/60 and Phase053 corrected animation remain unchanged.

## Slide contract

- Ctrl Started while Shift is held, grounded and moving at least430cm/s starts one slide. No airborne, dead, paused, disabled, reloading or workbench start. Ineligible Ctrl remains ordinary crouch.
- Duration0.75s; initial speed increased by100cm/s but capped620cm/s. Native floor slope increases uphill deceleration and reduces downhill deceleration without acceleration. No steering acceleration or jump chaining while active.
- End on duration, insufficient speed, obstructing wall, falling, reload, presentation lock, death or cleared input. Cooldown1s from end. Holding Ctrl ends crouched; releasing requests native uncrouch, which still respects overhead clearance.
- Hip fire remains authoritative. ADS exits at start and cannot resume until slide ends. A valid reload ends slide before its existing timer starts. No ammo/cinematic/save state belongs to movement.
- Camera crouch interpolation compensates native capsule height changes; a slight roll and coherent lower weapon/arms pose are cosmetic only. No camera pitch offset that disagrees with hitscan.
- Transient slide state is never serialized. Restored/new pawns start with ordinary movement. Pause clears held actions safely.

## Implementation plan

1. **Baseline and rules.** Preserve old package, take matched Unreal renders and a bounded old-package performance route. Record protected asset hashes and existing actor ownership. Read official APIs and installed headers.
2. **Movement and feedback.** Add `CRCharacterMovementComponent.{h,cpp}` and focused `CRSlideTests.cpp`; integrate `CRCharacter`, `CRWeaponComponent`, `CRWeaponViewComponent`, `CRWeaponAnimInstance`, `CRPlayerController`, `CRHUDWidget`, and `CRAshWarden`. Keep native action montage/notifies and damage authority. Compile Editor target once after this code batch. Add opt-in input-driven slide acceptance to the existing route harness, never assign objectives directly.
3. **Curated art.** Inspect baseline Workshop/entry/yard frames; author only missing original utility pieces if existing kit cannot serve. Save editable source and real imported assets under Phase054. A dedicated idempotent Editor script modifies only Phase054-owned actors and saves the three existing streamable levels. Prove old gameplay transforms, collision, anchors and old source assets are unchanged.
4. **Integration.** Capture identical after views and inspect them. Run focused slide edge cases and existing combat/lifecycle tests; correct actual errors only. One final Windows Development BuildCookRun, bounded cross-process checkpoint route, separate real gameplay video, and lower-overhead performance samples. No repeated packaging for cosmetic iteration.
5. **Delivery.** Update existing technical/milestone/performance/asset docs; review explicit diff and hashes, commit coherent changes, push feature branch and open PR without merge. Human feel/art acceptance remains separate from automation.

## Review focus

- Ctrl release under low ceiling must not expand the capsule through geometry.
- Sprint+ADS ordering, paused release and held Ctrl must not retrigger or leave weapon permanently sprint-locked.
- Firing during slide and reloading immediately after must preserve one native ammo transfer and one cosmetic ejection per accepted shot.
- Checkpoint recovery and workbench interruption must clear movement presentation without changing schema1 or animation completion semantics.
- Decoration must not obstruct interaction traces, checkpoint floor checks, AI navigation or the workbench camera/hand volume.

## Verification ledger

- Implementation complete; Editor builds72.16s and42.01s, both succeeded (second reflects actual final muzzle/input changes). One SlideDecay native automation test passed.
- Native input Editor route:600cm/s entry,0.751s duration,196.7cm/s exit; hip fire one round, ADS denied/resumed, reload conserved ammo, CP01 saved. Editor-game process hung after requesting exit0 and was stopped; that exit is not a pass.
- Blender4.5.11 generated six original meshes/19,772 source triangles; real UE import bounds and post-save ownership checks passed.40 added actors:20 Workshop,11 RailYard,9 RelayBunker.338 original actor snapshots unchanged. Only3 of240 protected old files changed (authorized sublevel maps); no missing files.
- Matched actual UE renders inspected before and after. Corrected the imported front-axis orientation of tool/distribution walls; original source and gameplay actors untouched. No final-art quality claim.
- One Windows Development BuildCookRun139.70s, AutomationTool exit0; six Phase054 meshes confirmed in the staged UFS manifest. Native game menu opened visibly and exited normally.
- One read-only branch review found no critical/important issue. Focused edge fixtures were added to cover identified validation gaps; all six cases passed in the native packaged executable, exit0 (NullRHI physics/input, not visual evidence). Minor: unused SlideBegin test timestamp retained, no runtime effect.
- Three independent packaged processes passed CP01, CP01-to-CP02 and CP02 recovery routes; launcher/native exits0, no forced stops. Normal fire/interaction rules drove progression. Workbench lifecycle fixtures additionally exercised genuine Abort, Skip, death, pause and stream/world cleanup; no direct objective assignment was used for the integrated route.
- Final content-only cook/stage/archive75.29s, AutomationTool0, after rendered inspection found opposite ramp-pipe pitch, incomplete support contact and two recessed bunker placements. No additional C++ build. The primary performance sample predates these noncolliding position edits; counts/materials/code are identical. A fresh recorded native route passed after this cook.
- Final packaged weapon fixture passed, PID51624/exit0: once-only ammo/damage, cosmetic case notifications, partial/empty/limited reload, ADS65/85 recovery, native montage pause, death without reload transfer, Restart. This fixture is separate from natural gameplay and includes explicitly isolated state setup.
- Actual foreground video: native PID31268 and FFmpeg both exit0.23.70s review clip,1920x1080, silent, trimmed startup/exit only. Enhanced Input drives sprint, slide hip fire, reload, real enemy combat, Workshop entry and8s interior camera scan. Direct frame review at raw1.45/1.95/3.7/5/9.6/19s confirms lowered slide view/shared weapon-root pose, retained reload, existing ADS/cycle and imported Workshop decoration. No continuous human feel/motion or sound-mix acceptance is inferred from selected frames.
- Primary performance: combat p95=15.299ms, slide/hip fire20.423ms, reload15.835ms, Workshop assembly18.737ms, Workshop movement20.028ms, Yard movement17.804ms. Five distinct >50ms frames across all routes, none in the active slide/reload/assembly subsets. Not a stable60FPS result. Full p50/p95/p99, GT/RT/GPU and memory in PERFORMANCE_BUDGET.md.
- Owner subjective feel/art acceptance remains pending. No Phase06 work.
- Ruling: reuse original/registered materials and native Blender/UE pipeline. Installed game-dev doctor points at another project's workspace; it was inspected only, not mutated or used to stage CinderRelay assets.
- Ruling: no new arm animation asset for slide. Blend existing idle and lower the shared arms/weapon root; this preserves corrected anatomy/contact and keeps the mobility feature bounded.

Official references (checked2026-11-01): [CalcVelocity](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/UCharacterMovementComponent/CalcVelocity), [OnMovementUpdated](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/UCharacterMovementComponent/OnMovementUpdated), [Camera additive offsets](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/UCameraComponent). Installed headers confirm virtual signatures. Native walking continues to resolve floor and swept movement; additive roll preserves the camera forward sight axis.

## Actual artifacts and ownership

New runtime class: `UCRCharacterMovementComponent`. Modified: `ACRCharacter`, `UCRWeaponComponent`, `UCRWeaponViewComponent`, `UCRWeaponAnimInstance`, `ACRPlayerController`, `UCRHUDWidget`, `ACRAshWarden`. Development-only additions: focused `CRSlideTests.cpp` and existing `ACRCheckpointRoute` extensions. No SaveGame, GameMode, checkpoint, streaming-controller or weapon DataAsset implementation changes.

Editable original source: `CinderRelay/ArtSource/Blender/Phase054/CR054_IndustrialUtilities.blend` plus `author_utility_kit.py`. Native static meshes: `/Game/Generated/Phase054/Meshes/SM_CR054_{ToolWall,ServiceShelf,OverheadServices,ElectricalPanel,PneumaticSkid,TracksideService}`. Total923,732 source `.uasset` bytes; source filesize is not GPU memory.

Changed maps remain `/Game/Generated/Phase01B/Maps/L_CH01_{RailYard,Workshop,RelayBunker}`. Tool boards/shelves define repair storage, original utility detail breaks up ceilings/walls, pneumatic skids/cable details group rail-side maintenance rather than filling paths. Two bounded nonshadow local lights and existing-material grime add local contrast. Three matched1920x1080/FOV85 Editor views plus an additional ramp inspection are actual renders. Yard changes are deliberately modest; the previous accepted skyline is unchanged.

## Local evidence and remaining limits

Compact durable receipt: [PHASE054_VALIDATION.json](PHASE054_VALIDATION.json). Raw files stay ignored under `.environment-local/phase-05-4/`: `editor-build.log`, `editor-final-build.log`, `slide-unit.log`, `environment-import.json`, `final-protection.json`, `package.log`, `package-content-repair.log`, `packaged-acceptance/`, `slide-edges.log`, `weapon-check.log`, `performance-comparison.json`, `before/`, `after/`, `video/`.

Review delivery: `deliverables/CinderRelay_Phase054_Review.zip` contains16 actual images, one23.70s silent game video, a reading note and per-file SHA256 hashes. All17 media entries were verified from the ZIP. It includes no build, save files or raw logs and is not committed to GitHub. The full raw33.60s recording remains local, including exit tail. Capture requests30fps; no locked capture cadence claim is made.

Visual limitations: original hand contact/cuff/material defects remain by scope; this is not a major remodel. Workshop floor/wall surfaces remain comparatively plain, repeated utility motifs and discontinuous modular duct ends remain visible. Rail Yard composition is incrementally detailed, not rebuilt. A visible cursor remains in the recorded sample. Selected frames cannot establish smooth continuous motion or subjective combat satisfaction; human playback and direct playtest are still required. Audio gain/pitch cues were implemented but no audio-balance listening acceptance was performed.

Engineering limits: direct uphill/downhill player traversal was not separately filmed (bounded deceleration has a focused unit test); native wall/ceiling/airborne cases were executed. Sliding-shot case count was not isolated, while the unchanged native notify mechanism passed the separate existing weapon fixture. Editor-game shutdown hung after requesting exit0; all current packaged checks exited0, so the Editor-only observation remains documented rather than called fixed. Dedicated VRAM and exact incremental render cost were not isolated. Do not infer leak freedom or future final-art performance from this bounded sample.
