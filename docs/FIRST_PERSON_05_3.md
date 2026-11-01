# Phase05.3 first-person character and handling

Status: Owner approved the proportions, skin tone and fingerless work-glove direction on 2026-11-01 and authorized refinement/action integration. This does not accept existing cuff, atlas or grip defects. B refinement and C/D implementation are integrated. Focused runtime checks passed; final packaged evidence is recorded below. Human temporal/aesthetic acceptance is not implied.

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
- [ ] B acceptance: owner direction approved and source/held-weapon/active IK integration completed; final cuff/material/contact aesthetic acceptance remains pending.
- [x] C: extend `CRWeaponViewComponent` with a narrow skeletal presentation adapter using the existing `OnShot`, `OnCue`, `OnChanged`. Preload sequences/materials. Preserve missing-asset fallback, native first-person clipping settings and sight-anchor authority. Create actual Idle/Walk/Sprint/ADS/FireCycle/Reload/Dry assets and event markers.
- [x] C: focused regression covers accepted/rejected shots, one casing per shot token, missing/replayed notify, interrupted reload, pause, death, restoration, partial/empty/zero-reserve reload. Cues never change ammo or damage.
- [x] D: create `CR053_RookRestoration.blend` and separate imported animation/sequence derivative. Reuse the accepted human anatomy. Preserve CR03_Hands binding, successful OnFinished/Skip versus Stop/Abort, safe deferred MovieScene cleanup and weak streamed references. Activate only after targeted tests.
- [x] E engineering: Windows Development package, dedicated test saves, three-process genuine-input route, cross-process CP restores, low-overhead comparison and separate1080p continuous recording. Actual results below; performance target and human visual acceptance remain open. Deliver through the existing draft PR; no auto-merge.

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

## Approved-direction continuation ledger (2026-11-01, historical implementation notes)

The owner explicitly approved the anatomical proportions, skin and fingerless-glove direction and authorized refinement/action integration. That approval does not certify existing cuff, contact or material defects. The old playtest ended; no old game/editor process remained in the current process audit. Work continues on the existing Phase053 branch and draft PR9; the prior checkpoint is `382cb559d5c7ec6238485e4bc21d8e29cb654cc4`.

Created separate editable `CR053_FirstPerson.blend` and `CR053_RookRestoration.blend`; `CR053_EliasArms.blend` and all earlier sources remain intact. `author_first_person.py` unwraps the final decimated topology and bakes two new2K atlases, then authors Idle4s/Walk1s/Sprint0.8s/ADS1s/FireCycle0.9s/Reload2.4s/Dry0.25s. The rig retains real weighted fingers and a native Blender two-bone editing IK chain. `rig_contact.py` calibrates each pole's rest-roll offset against an explicit elbow hint. Runtime uses baked animation, no new Control Rig. Small separate exterior feeding-unit, cycling-handle and cosmetic-case meshes have real FBX exports. Their capacity indicators are provisional visual ammunition representation, not simulation of weapon internals.

Actual UE import paths: `/Game/Generated/Phase053/Gameplay/Animation/SK_CR053_FirstPersonArms`, seven `AN_CR053_*` clips, `Gameplay/Meshes/SM_CR053_Feed`, `SM_CR053_CycleHandle`, `SM_CR053_Case`; three arm materials/two textures in Gameplay. Native imported rig has56 bones including the FBX wrapper and `hand_R/L` compatibility aliases. The isolated workbench derivative is `/Game/Generated/Phase053/Assembly/Animation/SK_CR053_Restoration`, `AN_CR053_RookRestoration` and `Assembly/Sequences/LS_CR053_RookRestoration`,22s. Its old camera/audio/tag binding and RestoreState contract are copied; the new camera pitch looks12degrees further downward for the nearer human-reachable presentation. **Workshop actor activation is still pending visual acceptance in this ledger entry.** The existing sequence/source are unchanged.

Implemented narrow runtime presentation additions: `UCRWeaponAnimInstance` composes native sequence players, TwoWayBlend nodes and one WeaponAction montage slot; `UCRWeaponCueNotify` dispatches cosmetic markers; `CRWeaponHandling.cpp` extends the existing view component. Async loading precedes activation; three native montage wrappers and eight collisionless cases are allocated once. Static weapon/optic/feed/handle attachments remove the actual imported reference bone transform. The existing component still owns damage, ammo,0.9s cycling,2.4s reload and checkpoint reset. Cues never mutate them. A montage instance identity is consumed once per accepted shot; stale/duplicate notifications cannot emit a case for a subsequent shot. Pause uses native game time; death, presentation hiding, Ready reconciliation and EndPlay clear transient animation/cues. FeedOut/FeedIn reuse original licensed/project-owned Phase052 sound cues. Missing appearance assets preserve the established fallback.

Ruling: use a small native AnimInstance graph with Engine/AnimGraphRuntime nodes because a scripted Animation Blueprint graph is not available through the supported Python authoring surface. This is native animation-node composition, not a new animation engine. No UnrealEd runtime dependency or replacement WeaponComponent. Hip composition moves from(38,14,-15) to(48,10,-10) to reveal actual hands; ADS still uses the existing sight anchors/28cm Blueprint eye relief/65 and60degree FOV.

Executed so far:

- First Editor build succeeded (12actions,87.80s; fresh intermediate/PCH after prior cleanup). Focused diagnostic build succeeded in6.48s; a hip-framing build and a subsequent integration build also succeeded. These later invocations followed actual C++ changes, not unchanged rebuild loops. Logs: `handling-editor-build.log`, `handling-diagnostic-build.log`, `handling-framing-build.log`, `handling-integration-build.log`.
- Native import initially rejected direct Python access to an editor-only FBX property. Corrected to the installed `set_editor_property` API; import receipt and `CR053_HANDLING_IMPORT_PASS` then confirmed all seven real durations. Native restoration import returned `CR053_HUMAN_RESTORATION_IMPORT_PASS active=False`.
- First actual sight fixture: iron axis error0.00000cm/FOV65 passed; upgraded optic failed at7.15704cm/FOV60. Its process exit was0 despite a failed acceptance receipt, so it is **not a pass**. Source diagnosis found a14degree optic child offset on ADS frame0: Blender's child matrix setter had read an unevaluated parent. Flush parent evaluation before child keying; subsequent animation imports are pending runtime recheck.
- Runtime graph diagnostic confirmed `idle=AN_CR053_Idle`, `ads=AN_CR053_ADS`, advancing idle time1.139s and wrist(-20,5,1.117)cm. A native AnimInstance in an editor-only non-game preview remained in reference pose; that preview is not evidence of a game-runtime evaluation failure. Use actual game fixtures for the graph.
- Workbench retarget initially had41.36cm wrist error. A saved-bone audit found connected endpoints translated twice, changing control-bone lengths. Snapshot/disconnect/translate/reconnect fixed it. Moving the presentation to the near half of the bench keeps real limb lengths and shoulder cuts outside the intended view; measured pre-pole worst error0.425cm. No checkpoint/map boundaries moved.
- Twelve actual native workbench poses were captured under `workbench-review/f3a4f218c6/` with an error-free receipt. They exposed forearm occlusion of the optic; author-time pole calibration now bends elbows below that action. This is a further source refinement awaiting refreshed native visual inspection, not completed aesthetic acceptance. Source renders support the diagnosis but are not Unreal acceptance.
- Focused cases added to existing CRWeaponAcceptance: nine accepted shots; eight normal case events plus one deliberately suppressed cosmetic cue; rejected spam/dry/reload cannot add cases; pause freezes montage position; a missing cue cannot block Ready. ShotCueIdentity automation covers stale, duplicate and canceled montage identities. **These new assertions have not yet executed at this ledger point.**

Next: verify corrected sights and normal handling in the real game; inspect refreshed native workbench poses/playback; activate only the accepted derivative; run focused automation/weapon checks; then one final Windows Development package and bounded cross-process route, separate continuous video and low-overhead comparison. Update this ledger with actual results before delivery. No new package, final regression, performance improvement or human motion-quality acceptance is claimed yet.


## Integrated candidate and executed checks (2026-11-01)

This section supersedes the earlier pending statements; earlier failures remain recorded for diagnosis. Owner direction approval is recorded above. Final human continuous-motion and aesthetic acceptance remain pending.

- Gameplay arms:33,121 source triangles after removing878 skin faces entirely covered by the glove; three material slots, two2K atlases,56 imported bones. Workbench joined hands/weapon/optic:92,165 source triangles. Both editable derivatives pack seven available source images; no missing unpacked image dependencies were found. No whole kit rebuild was needed for this surface correction.
- Seven actual imported handling clips and three native Montage wrappers now run through the existing view component. FireCycle has one EjectCase notify at20/60s; Reload has FeedOut at30/60s and FeedIn at111/60s. These are actual native markers, not only proposed storyboard timings. Eight reusable cosmetic cases expire after1.15s. No synchronous loads or damage/ammo writes occur in these cues.
- Source wrist/contact IK is baked; native skeleton56 bones verified. Blender.R maps to positive UE Y after FBX conversion. This is calibrated source-to-project retargeting, not a verified Manny animation compatibility claim. Imported reference transforms, not name assumptions, align weapon/feed/optic attachments.
- Corrected actual game sight fixture passed: iron/optic/standing/crouched/post-shot/post-reload alignment0.00000cm, post-cover0.00009cm; cover lowering remained active. Native process exit0. Four hip/ADS images plus five regression poses are in Saved/Phase051/Phase053-corrected-*.png. This isolated fixture invokes existing upgrade APIs; it is not normal chapter completion evidence.
- Native weapon fixture passed with9 accepted shots:8 normal case cues and1 intentionally suppressed cue. Rejected spam/dry/reload produce no extra cases; partial/empty/zero-reserve reload, pause, death, restart and missing-cue Ready reconciliation passed. This isolated fixture prepares ammo state; packaged routes exercise ordinary interactions separately. Native process exit0.
- Native Automation CinderRelay.Presentation:3 succeeded,0 failed (ShotCueIdentity, SightAlignment, SightFallback),0.048s, process exit0. Known installed-engine startup self-test condition messages are outside these three results; no clean-log claim.
- Twelve native workbench pose images (ab4afdac10) and two targeted corrected contact images (5da8d6aa1a) were inspected. Pole calibration prevents forearm occlusion; corrected palm target supports the optic beneath its shell. Remaining limits: finger contact is approximate, thumb/opposition and cuff edges need human review, materials look flat under the existing bright task light. Screenshots do not establish natural continuous motion.
- The existing Workshop actor now references Phase053 Assembly SK/LS assets. No other chapter gameplay actor, checkpoint, objective or collision was relocated. Native sequence evaluation at6s and19.2s changed the actual camera, and Stop restored its exact starting transform at both times; Editor exit0. Original Phase052 source/sequence remain rollback.
- Surface reimport saved successfully and wrote a valid receipt, but that commandlet exited0xC0000005 after its normal shutdown log. A fresh native rendered reopen then passed and exited0, as did activation/track validation. Record the abnormal import-process exit separately; it is not a clean OS exit or an asset-import failure inferred solely from the code.
- One Blender replace failed after writing a complete .blend@ recovery file. Reopened both derivatives with Blender, checked owner/revision/actions/packed dependencies, exported the affected meshes, preserved the previous owned source in ignored save-recovery, then restored the validated bytes. No protected earlier source was replaced.

Evidence under ignored .environment-local/phase-05-3: handling-sight-corrected.log, handling-weapon-acceptance.json, handling-weapon-checks.txt, presentation-automation/index.json, handling-exports/surface-refinement.json, contact-track-validation.json, activation-track.log, workbench-review/. Final package/performance/video results are recorded below when actually executed.


### Whole-branch review correction

One fresh-context reviewer identified three P2 issues: first input could precede async appearance residency; a missing base appearance could enable handling while disabling old fallback motion; and wrist orientation snapped at the workbench acquire/release boundaries. One focused correction adds separate appearance/handling settled flags, gates only Character Fire/Reload/AimStart until native completion, and permits both successful and failed/fallback completion. Invalid/null requests resolve without a permanent input lock. Native handling activates only with the valid original sight pair. WeaponComponent authority is unchanged.

A targeted Blender edit of only the existing right wrist/finger keys now quaternion-blends acquire/release/regrip; smoothstep curl changes accompany grasp/release. The saved source measured a worst90.000deg change per30fps frame before,10.562deg after; geometry and existing prop trajectories are unchanged. This metric proves removal of the identified discontinuity, not human-natural motion. Reproduction is in restoration_orientation.py and smooth_restoration_release.py. The latter refuses an already-applied finger revision.

Initial integrated BuildCookRun passed in157.04s/exit0. These concrete review findings justified a subsequent focused Editor build(36.33s/exit0), animation-only reimport and an incremental corrected archive before acceptance. The initial archive is not mislabeled as the final validated build. No repeated unchanged route or shader-cache clearing is used.

## Final engineering delivery and visual-review boundary

This is an integrated playable **review candidate**, not final artistic acceptance. Human anatomy direction was approved before implementation; close-up glove/cuff deformation, hand-to-prop precision, surface realism and continuous human motion acceptance remain open. Do not label the whole visual milestone complete based on the functional results below.

### Native assets and source preservation

Actual active assets are the seven `Gameplay/Animation/AN_CR053_*` clips, `SK_CR053_FirstPersonArms`, three separate exterior props, two2K atlases/three materials, and the separate22s `Assembly/Sequences/LS_CR053_RookRestoration` with imported joined skeletal source. `CR053_FirstPerson.blend` and `CR053_RookRestoration.blend` are editable; original Review, Phase03/05/051/052 sources remain rollback. Only the existing Workshop map's bench soft appearance references changed. No saved ID, checkpoint anchor, gameplay collision, NavMesh, objective or streaming boundary was moved.

Native read-only map audit:302 preserved baseline actors plus36 **pre-existing Phase052** cosmetic actors=338; no new Phase053 chapter actors. Camera track/Stop evaluated at6s and19.2s with exact restore. Original CP00(-1450,0,110), CP01(2050,0,110), CP02(4050,0,-40.18861) anchors remain. The native audit originally checked225 protected file hashes with six exact authorized source exceptions. Later Development recording additions to `CRCheckpointRoute.cpp` are a seventh explicit exception; final static recheck covers224 unchanged protected files. No blanket folder exclusion.

Added runtime sources: `CRWeaponAnimInstance.{h,cpp}`, `CRWeaponCueNotify.{h,cpp}`, `CRWeaponHandling.cpp`, `CRWeaponPresentationTests.cpp`. Modified `CRWeaponViewComponent.{h,cpp}`, `CRCharacter.cpp`, `CRCombatAcceptance.{h,cpp}`, `CRCheckpointRoute.cpp`, `CinderRelay.Build.cs` and explicit Gameplay/Assembly cook directories. Existing `UCRWeaponComponent`, GameMode, SaveGame schema1 and workbench transaction implementation remain unchanged.

### Executed functional acceptance

- Corrected integrated Windows Development BuildCookRun:118.94s, AutomationTool0. Editor review-fix build36.33s/0. Focused weapon fixture, sight fixture and all3 Presentation automation tests passed; the known unrelated engine startup self-test message remains documented.
- Fresh `CR04_TEST_Phase053Final` three-process suite: route1 native19260/bootstrap19092 savedCP01; route2 native30852 restoredCP01 and savedCP02; route3 native33448 restoredCP02, recovered/backtracked and reached both endings. Every fresh receipt passed; all native/bootstrap exits0; no forced stop. This is actual process-restart disk persistence, not same-process OpenLevel proof.
- Route2 exercised explicit Skip, exactly-once upgrade, death, presentation actor destruction, Restart/world EndPlay, controller destruction, genuine SequencePlayer Stop without upgrade, rejected checkpoint requests during assembly, pause/freeze/resume and natural22s completion. Normal upgraded fire/reload then remained usable.
- Route3 exercised saved enemy/pickup/salvage/upgrade reconciliation, real sublevel unload/reload, death Retry, three repeated recovery cycles, full Restart initial state and optional workbench-bypass ending. Inputs/interactions drive the chapter route; isolated unit fixtures' direct setup is not misrepresented as this acceptance.
- Primary raw output was archived to `packaged-acceptance/SavedPhase04` before diagnostics could reuse route-number output folders. Game saves use only dedicated test slots; player saves and the previous local media ZIP remain untouched.

### Recording-driven correction and real media

Initial window-capture/lifetime attempts were rejected as insufficient recording proof. Diagnosis found stale occluded-window frames and unsynchronized recorder lifetime; an opt-in Development `-CRHandlingVideo` path now waits for a foreground/recording-ready file in an existing dedicated-test-slot route. No normal gameplay wait or shipping behavior is added. It drives real Enhanced Input, then the existing workbench route. One recording exposed an early rejected reload (appearance not resident yet) and low feed framing; it is retained only as local diagnostic evidence, not a three-shot acceptance video.

One focused correction waits for `IsPresentationResident` and verifies each accepted shot's actual magazine decrement. `refine_reload_framing.py` edits **only the existing Reload action**: raise/roll the presentation and turn the replacement's five fictional ammunition indicators toward the camera. No geometry/texture regeneration, combat timing, cue times or balance change. Import uses `-CR053ReimportReload`; native import exited0. Game-target recording repair21.34s/0; incremental cook/archive25.93s/AutomationTool0. The earlier recording-adapter Game build34.46s and cook-skipped stage38.19s are separate from full cook evidence. Editor's last compile precedes the opt-in recording helper; Game compiled the final helper.

Final separate recorded route: `CR04_TEST_Phase053Recorded2`, native70292/capture exits0, no forced stop, CP02 success. Native checks confirm three actual accepted shots consumed exactly three rounds after a completed full reload. The continuous recording includes those shots/cycling, an entire visible reload, module/salvage interaction, an explicit Stop/retry, full workbench with a deliberate1s pause, normal upgraded handling and return to gameplay. Trimmed local delivery: `.environment-local/phase-05-3/CR053_Gameplay_Review.mp4`,46.03s,1920×1080,H.264,silent,1238 decoded frames. Capture requested30fps; actual timestamp-average26.89fps, so **not a locked30FPS recording**. No synthetic/interpolated frames or composited animation. Only the trailing shutdown/desktop interval was removed, with stream copy; no action interval was cut or retimed. Successful full decode is not aesthetic acceptance.

Review inspected sequential4fps handling sheets,2fps workbench sheets spanning the entire action, full-resolution replacement/casing frames and the nine actual sight fixture views. Actual replacement ammunition indicators and the rightward ejected case are visible. Iron/optic views live in `CinderRelay/Saved/Phase051/Phase053-corrected-*.png`; selected12 proof categories are indexed in the local media manifest. This review identified and corrected framing, but it is still sampled-frame visual review of a genuine continuous file, not a human real-time motion sign-off.

Remaining observed defects: sleeve/cuff bands and glove edges are conspicuous when the right arm is raised; some grips/thumb contact are approximate and fingers do not fully wrap all surfaces; material/weathering lacks close-up realism; the broad wrist motion and short2.4s reload remain visibly authored prototype motion. A brief fallback appears during cold appearance residency. Workbench placement/retrieval has near-camera blur and approximately posed contact. No claim of professional mocap, flawless clipping or production-quality human animation. The final draft PR remains open for owner play/visual review.

### Performance and reproducibility limits

Same-session assembly frame p50/p95/p99 changed15.844/17.057/17.639ms to16.592/17.678/18.138ms. GT/RT/GPU p95=1.854/17.647/16.218ms after integration. Peak private commit across primary routes4,435,148,800 bytes; this is not VRAM. Nine recorded>50ms rows and one previous-GT2214.954ms observation remain unresolved. Bounded warm Insights did not reproduce the initial stall; named animation/presentation scopes are small but cannot establish the missing cause. Diagnostic native exit777003 recurred although its gameplay receipt passed; primary route exits all0. No claim of performance stabilization to60FPS.

See [performance conditions and actual evidence](PERFORMANCE_BUDGET.md#phase053-integrated-packaged-comparison-2026-11-01). The final Reload-only framing correction was validated in the recorded packaged route; primary performance is the immediately prior candidate, identified by executable hash. Recording overhead is excluded from performance comparisons. No whole-route repeat followed the isolated visual edit. Further aesthetic refinement and one reproducible first-use hitch investigation are appropriate within05.3; Phase06 remains unauthorized.
