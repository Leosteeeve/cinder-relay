# Phase05.3 first-person character and handling

Status: Checkpoint A research and Checkpoint B review candidate in progress. No claim of completed runtime integration or human visual acceptance.

## Authorized contract

Owner brief: Phase05.3, received 2026-11-01. Base merge `6f9dd59100222ecab6e2bdeeaed60c937389ea60`; branch `phase-05-3-first-person-animation`. UE5.8.4, CinderRelay runtime module, Windows. This continues the existing workspace; no duplicate project or engine upgrade.

Elias remains a 28-year-old male mechanic. Proposed art treatment: moderate forearm musculature, properly opposed thumbs, fitted faded work sleeves and flexible fingerless work gloves. This is an appearance proposal for the required close-up gate, not added story canon. One mesh/skeleton/material identity must serve gameplay and the workbench. Existing Phase03/05/051/052 sources and active assets remain rollback resources.

The user explicitly requires review of the new human hand model before implementing all five checkpoints. Produce a real editable, deforming asset and real engine samples first. Do not approve anatomy based on vertex counts or a successful import. Runtime C/D integration follows that review.

## Research and legal selection (2026-11-01)

The four supplied marketplace links were read as references only. None was purchased or downloaded. Current extracted Fab pages expose Buy now but hide numeric prices and the selected license; exact cost and acquired license are **unverified**, not assumed free. Their published UE compatibility is a seller claim until actual import testing. All four expose an AI-use restriction field; no source assets from these listings are supplied to generative services.

| Candidate / author | Evidence and suitability | Source / rig / cost | Public repository decision |
|---|---|---|---|
| [FPS Arms 02](https://www.fab.com/listings/dd1e0474-3869-48a8-9a90-6681fa4b7e1c), Davlet | Seller lists animation-focused topology, 13,292 triangles, 4K PBR, dirty-hand texture and forearm twist corrections; claims UE4/UE5 skeleton and UE5.8 support. Good professional anatomical reference; weights and finger deformation not locally tested. | Blender, FBX, UE; two rigs. Seller warns the demonstration FK rig is not the UE animation export rig. Numeric price/license selection unavailable. | Commercial candidate only. Do not put raw meshes/textures/animations in public Git. No purchase/download. |
| [FPS Arms 01](https://www.fab.com/listings/78949782-1f94-43a5-bd64-fc120716a711), Davlet | Similar 13,292-triangle anatomy, 4K maps, twist/retarget updates; UE5.8 claim. Finger/hand quality requires acquired-asset inspection. | Blender, FBX, UE; same FK export caveat. Actual source editing and retarget cost unmeasured; price/license unavailable. | Same restricted-candidate treatment. No purchase/download. |
| [FPS Animation Pack Pro](https://www.fab.com/listings/37b13190-f784-4cf3-9312-922bd263d3d2), KINEMATION | Ten weapon sets, reload/action/movement clips, first-person arms. Useful timing reference, but existing weapon designs and operation differ from fictional ROOK-5. | UE format, Control Rig + Enhanced Input dependencies. Blender source, exact bones/triangles and 5.8.4 compatibility unverified. Price/license unavailable. | No wholesale framework adoption or source redistribution. No purchase/download. |
| [FPS Animation Pack Lite](https://www.fab.com/listings/79752ba2-c659-4375-8fa9-5e6fc8025b62), KINEMATION | Smaller set; listing inconsistently states four and five weapons. Reload/movement source concept useful, exact contents require verification. | UE format; same dependencies; editable Blender data/hand topology/twist weights unverified. Price/license unavailable. | Not presumed free because it is named Lite. No purchase/download. |
| [WRAD ARMS](https://wriks.itch.io/wrad-arms), wriks | CC0, free/name-your-price, 1,200 triangles, 512px textures, IK rig, GLB/FBX/OBJ. Deliberately retro GoldSource style. | Low resource cost; independent rig needs retarget testing. | Redistribution permitted under stated CC0, but rejected for the owner's realistic close-up art target. Not downloaded. |
| [MakeHuman official core assets](https://github.com/makehumancommunity/makehuman), MakeHuman team / Data Collection AB, Joel Palmius, Jonas Hauquier | Connected authored human topology, separate finger chains, published weights, graphical morph targets. A suitable anatomical foundation, not a finished textured FPS kit. | Free, CC0 core graphical data. OBJ + JSON skeleton/weights + morph targets, adapted into editable Blender. Needs source-space, UV, wrist/finger deformation and UE import validation. | Selected **for a review candidate**, not final quality approval. Pin upstream commit and SHA256; copy only explicitly licensed graphical data. |

[Fab's Standard License summary](https://www.fab.com/eula) distinguishes project distribution/private collaborator sharing from standalone asset redistribution. A public source repository is not treated as a licensed private collaboration channel. If the owner later authorizes a commercial pack, keep it in a separately provisioned, ignored private content directory; record exact version/hash and acquisition instructions publicly, provide fallback content, and cook only under the verified acquired license. Do not change repository visibility or publish receipts/account data.

[MakeHuman LICENSE.md](https://raw.githubusercontent.com/makehumancommunity/makehuman/master/LICENSE.md) separates AGPL program logic from CC0 graphical assets, including base mesh, morph targets, textures and poses. The actual base.obj header explicitly declares CC0; default_weights.mhw declares CC0. No MakeHuman application Python code is copied. Attribution is not required by CC0; provenance is retained voluntarily. The selected upstream commit is `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`. Native import/cook/performance remain separate acceptance stages.

## Current implementation audit

`UCRWeaponViewComponent` currently displays two asynchronously loaded static meshes, drives whole-root recoil/sway/reload lowering, and owns flash/audio. There are no gameplay skeletal hands. Sight roots solve the authored socket transform into camera +X; the actual default eye relief is20cm (an older technical paragraph says28cm). Both meshes/sockets must validate before replacing the original fallback.

`UCRWeaponComponent` owns Ready/Cycling/Reloading/Disabled, accepted shots, ammunition and timers. `OnChanged` broadcasts state; `OnShot` fires once after an accepted shot; `OnCue` distinguishes Reload/Dry. Reload transfer is atomic at2.4s. Checkpoint restoration clears timers and resets Ready. No animation notify may duplicate these responsibilities.

The active workbench uses SK/AN/LS_CR052_RookRestoration:22s,30fps,40 imported bones, with authoring IK/contact controls. Its hand/sleeve surfaces originate from procedural unions and rigid sleeve sections, confirming the owner's anatomical criticism. The replacement must use the newly approved human mesh, not another capsule-derived palm. Source assets must be opened and measured rather than assuming their bone names prove retargetability.

## Implementation plan and gate

> For agentic workers: execute the steps in order with the executing-plans workflow. Read the owner's Phase05.3 brief and this contract together. Do not bypass the close-up art gate.

**Goal:** one coherent human first-person arm identity with readable fictional weapon handling and preserved gameplay authority.

**Architecture:** baked skeletal presentation behind existing weapon events; reusable arm source; local cosmetic props and a bounded casing pool. Existing GameMode, SaveGame, workbench ownership and streaming remain authoritative. No replacement combat/animation framework.

**Tech stack:** installed Blender4.5.11, UE5.8.4 native SkeletalMesh/AnimSequence/AnimInstance/Notifies/Sequencer, C++ and Editor Python.

- [x] A: inspect clean branch and expected merged baseline; read current weapon/view/workbench and asset sources.
- [x] A: compare supplied professional references and a redistributable alternative; pin original sources and license scope.
- [x] B candidate: create `CinderRelay/ArtSource/Blender/Phase053/CR053_EliasArms.blend`, connected anatomical mesh, finger/wrist rig and articulation keys; old sources preserved.
- [x] B candidate: actual isolated UE import, dimension/bone verification and nine close-up rendered pose samples.
- [ ] B acceptance: correct cuff/atlas defects, calibrate thumb/contact and active IK editing controls, obtain owner visual review, then test held-weapon poses/retargeting before full C/D integration.
- [ ] C: extend `CRWeaponViewComponent` with a narrow skeletal presentation adapter using the existing `OnShot`, `OnCue`, `OnChanged`. Preload sequences/materials. Preserve missing-asset fallback, native first-person clipping settings and sight-anchor authority. Create actual Idle/Walk/Sprint/ADS/FireCycle/Reload/Dry assets and event markers.
- [ ] C: focused regression covers accepted/rejected shots, one casing per shot token, missing/replayed notify, interrupted reload, pause, death, restoration, partial/empty/zero-reserve reload. Cues never change ammo or damage.
- [ ] D: create `CR053_RookRestoration.blend` and separate imported animation/sequence derivative. Reuse the accepted human anatomy. Preserve CR03_Hands binding, successful OnFinished/Skip versus Stop/Abort, safe deferred MovieScene cleanup and weak streamed references. Activate only after targeted tests.
- [ ] E: one final Windows Development package, dedicated test saves, bounded genuine-input route, one cross-process CP restore, low-overhead benchmark, separate1080p continuous video and12 meaningful visual samples. Commit/push feature branch and PR; no auto-merge.

Non-goals: new weapons, balance changes, schema2, checkpoint relocation, new inventory, renderer rewrite, new chapter, Motion Matching, MetaHuman, paid AI generation, cinematic hand model swap without visual review.

## Fictional handling storyboard and proposed cue contract

ROOK-5 uses a fictional five-round detachable feeding unit and one external cycling handle. Only visible exterior animation is represented; no internal mechanical construction model. Cases are stylized cosmetic props. Source animation is authored at60fps for precise short gestures; these proposed markers must be checked against actual exported/imported playback before becoming implementation evidence.

| Clip / proposed frames at60fps | Visible action | Authority |
|---|---|---|
| FireCycle0–6 (0–0.10s) | Shot recoil while support grip holds | Accepted `OnShot` starts one token; existing flash/sound; existing damage/ammo already applied |
| FireCycle7–18 (0.117–0.30s) | Grip releases to external handle, cycle pull | Cosmetic pose only |
| FireCycle20 (0.333s) | One visible case leaves the cosmetic ejection anchor | Notify spends that shot token at most once; never on idle/dry/reload |
| FireCycle21–44 (0.35–0.733s) | External handle returns; grip reacquires | Cosmetic pose only |
| FireCycle45–54 (0.75–0.90s) | Ease back to unchanged selected sight axis | Gameplay cycle timer owns Ready; missing notify cannot block shooting |
| Reload0–18 (0–0.30s) | Present feed unit within view | Accepted reload state/cue starts presentation |
| Reload19–46 (0.317–0.767s) | Support hand removes old unit | Authored contact/attachment cue; no ammo transfer |
| Reload47–90 (0.783–1.50s) | Replacement with readable round indicators appears and is presented | Cosmetic replica only; no spawned ammo pickup |
| Reload91–113 (1.517–1.883s) | Seat replacement | Animation marker changes cosmetic ownership |
| Reload114–144 (1.90–2.40s) | Brief exterior ready gesture; regrip | Existing2.4s timer transfers ammo once; Ready state repairs any skipped visual marker |

Preserve timing by concise anticipation and overlapping hand travel; if actual readable motion cannot fit2.4s, report a comparison rather than extending gameplay duration silently. Interruption clears shot tokens, attached transient props and pending cosmetic effects; pause follows game time. Preallocated case capacity is bounded (proposed8); no physics authority or per-shot asset load.

## Native technical references

- [UE5.8 first-person rendering](https://dev.epicgames.com/documentation/en-us/unreal-engine/first-person-rendering): tag matching hands/weapon primitives consistently; preserve the current single camera and aligned world FOV.
- [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine): use real animation markers for cosmetic cues, with duplicate/interruption guards.
- [Animation Montages](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine): native slots/blending and lifecycle events; no notify-driven ammo authority.
- [Animation Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-insights-in-unreal-engine): focused diagnostic run only when a measured hitch requires it.

## Actual Checkpoint A / B progress (2026-11-01)

Created `CinderRelay/ArtSource/Blender/Phase053/CR053_EliasArms.blend` from pinned CC0 graphical data, with original fitted sleeves, fingerless gloves and two original baked2K atlases. The final source mesh has33,999 triangles,17,237 vertices, three material slots and at most four normalized skin influences per vertex. The49 deform bones retain split forearm, wrist, metacarpal and individual finger chains. Four non-deforming IK control bones and hand/elbow targets are editable but disabled in the anatomical clip; active contact IK and retarget calibration are not completed.

Actual UE5.8.4 import saved:

- `/Game/Generated/Phase053/Review/Animation/SK_CR053_EliasArms`
- `/Game/Generated/Phase053/Review/Animation/SK_CR053_EliasArms_Skeleton`
- `/Game/Generated/Phase053/Review/Animation/AN_CR053_AnatomyReview`
- `/Game/Generated/Phase053/Review/Maps/L_CR053_ArmsReview`

The imported animation is3 seconds at60fps, showing finger curl and wrist articulation, **not** firearm handling. Imported bounds are40.629 ×109.586 ×49.391cm. There are50 imported bones including the FBX armature wrapper. Blender period suffixes become underscores in Unreal (`wrist.R` -> `wrist_R`); actual bone names are preserved in the import receipt. This custom rig is not interchangeable with Manny/UE mannequin by name. No actual Manny retarget test or gameplay/workbench retarget has yet passed.

Nine genuine1920×1080 Editor renders inspect both hands, relaxed/open/curl shapes, thumb, wrist and release. The first capture exposed excessive review-stage lighting; the revised neutral stage uses fixedEV7 and a dark matte floor. Existing gameplay lighting/settings are unchanged. Static images show continuous anatomical surfaces, nails and articulated fingers; they also expose unfinished glove/cuff edges, atlas color patches, basic cloth shading and a thumb pose that needs contact calibration. These are **candidate-quality** samples, not human approval, finished character art or proof of natural motion. Shoulder cuts lie outside the intended gameplay camera but are visible in the full anatomy overview.

No runtime C++ class, existing weapon mesh, old Blender source, chapter map, default map or SaveGame configuration has changed. New weapon clips, once-only ejection, visible reload, actual weapon contact, workbench retargeting, continuous runtime video and final Phase05.3 packaged acceptance remain pending. Do not describe this checkpoint as complete Phase05.3 delivery.

## Executed verification and bounded failures

- One low-overhead baseline suite ran the retained **Phase05.2** Windows Development package in three separate processes at1080p/Epic/native, using only `CR04_TEST_Phase053Baseline` slots. CP01 save/exit, CP01 continue/CP02 save, CP02 continue/backtracking/recovery/ending acceptance all passed; bootstrap/native exits were0 for all three. This is baseline compatibility evidence, not testing new runtime arms.
- Baseline assembly:1452 frames, frame p50/p95/p99=15.844/17.057/17.639ms; GT/RT/GPU p95=2.689/17.041/15.591ms. This run has lower p95 than the historical19.538ms sample without any asset change; do **not** claim an optimization. Desktop scheduling/thermal state was uncontrolled.
- GLB inspection and12 policy checks pass:33,999 triangles,3 materials,2×2048 textures, UVs/normals/tangents, skinned animation, meter bounds0.406×0.494×1.096. An initial100× export error and then an incorrect node-scale correction were diagnosed; the second focused correction converts geometry/bones/translation keys together in an unsaved export copy. FBX/source remain centimeters.
- Initial native importer completed mesh/animation import but its bounds query used an unavailable component API. Replaced it with installed `SkeletalMesh.GetImportedBounds`. The next run encountered a separate UWorld GC fatal because Python retained a loaded map before `LoadLevel`; removed that reference and verified successful map save, receipt and Editor exit0. Process exit0 alone was not counted as Python success.
- Initial and neutral Editor capture batches each produced nine real images and an error-free capture receipt. The neutral batch is the review evidence; screenshots alone do not prove animation smoothness.
- Optional `game-dev package build` failed twice with `EPERM: operation not permitted, fsync`, including elevated execution. The installed1.0.2 `packages/format.ts::fsyncDirectory` handles EINVAL/ENOTSUP but not Windows EPERM. No further retry, global tool patch, package-verification or canonical vendoring success is claimed. Standalone GLB policy validation and native UE import passed independently. No restricted source is admitted.
- No C++ was changed, so no C++ rebuild or new BuildCookRun was performed for this art-review checkpoint.

Independent checkpoint review found an Important ownership issue: animation recovery selected any sole animation in the generated folder. A focused fake-asset-store test executing the actual recovery branch failed on the old code, then four cases passed after requiring the exact owned FBX animation and valid duration before renaming. Log files: `ownership-red.log`, `ownership-green.log`. This verifies the safety branch, not another native import. The review also identified stale-image risk in repeated capture runs; subsequent captures use a new UUID/timestamp directory and reject directory collisions. Existing nine samples were verified against actual successful capture logs/times; that evidence remains valid. No whole-route rerun or C++ rebuild followed these editor-script-only safeguards.

Local evidence remains ignored under `.environment-local/phase-05-3/`: `source-preflight.json`, `exports/arms-source-receipt.json`, `arms-import.json`, `asset-inspection.json`, `asset-validation.json`, `arms-review-neutral/review.json`, import/capture logs, `baseline/process-results.json`, `baseline/polish-summary.json` and `baseline/SavedPhase04/`. GLB packaging errors remain in `package-build.json`. Raw captures, packages, save games and logs are not intended source assets.
