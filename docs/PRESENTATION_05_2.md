# Phase 05.2 Presentation and Contact Polish

## Intent and current visual audit

The owner's reviewed Phase05.1 images and 28-second recording are the acceptance contract. Improve the existing chapter's near-field believability and contact, with no new mechanics, story, progression or map hierarchy. Base: merged PR7, `e5d0ef641e99a71b59012e18e5d56880988cdb4b`.

Observed: both `CR05_RailCar*` actors have weak wheel/undercarriage contrast and repetitive flat panels; the Workshop opening is a bare rectangular aperture; two gantries lack credible attachment detail; the large yard floor reads as one uniform surface. The skyline is useful but the gap between wall and towers remains empty. Existing assembly poses show nearly straight sleeves, little wrist variation, simultaneous finger motion and a mostly vertical optic placement.

The previous `after-train-route.png` camera at (-600,700,165) lies inside the north railcar's occupied footprint. It is not a valid playable camera position. Audit it explicitly, preserve that evidence, and capture the adjacent accessible route as well as Workshop interior views. Do not brighten the whole world to conceal an invalid camera.

## Approach

Use original editable Blender derivatives and native Unreal materials/lights/Sequencer. Retain prior meshes/source as rollback. Replace only cosmetic railcar mesh assignments; add a bounded detail kit and local fill lighting owned by existing zones. Keep collision and navigation from the established gameplay shell. Use existing CC0 surfaces where appropriate; acquire no external assets or paid generation.

A global exposure lift alone would flatten the yard and still leave missing structure. A replacement environment or new animation system would create unrelated integration risk. The selected scoped asset/contact pass addresses the owner's specific views while preserving runtime authority.

## Implementation plan and ledger

**Goal:** Visible improvement in believable industrial composition, readable playable shadows and deliberate fictional optic calibration.

**Architecture:** `/Game/Generated/Phase052` contains new cosmetic content; `ArtSource/Blender/Phase052` contains editable derivatives. Existing workbench state machine and 22-second contract stay authoritative. Native render-only audits never save preview cameras/poses.

**Review focus:** decoration must not cross walkways or checkpoint floors; a dark invalid camera must not masquerade as a fixed gameplay view; contact must survive FBX conversion; sequence/Skip/Abort must preserve upgrade ownership; extra material/light/mesh costs must be measured at unchanged Epic quality.

- [x] Audit: six matched before views,302-actor inventory,231 protected hashes and prior media inspected. Native overlap confirms the old camera intersects CR_CarBody800; new route/flank/interior cameras do not intersect WorldStatic actors.
- [x] Environment: original11-mesh kit and36 owned actors; actual representative views reviewed before final placement refinement. Corrected reflected-axis wheel/spool winding and reduced the overly bright service fill after inspecting actual renders. Final six matched after views inspected.
- [x] Contact assets: separate editable Blender/SK/AN/LS derivative, preserved22s/40 imported bones. Nine native poses inspected; native camera evaluation/Stop restoration passed. Full runtime playback and lifecycle route passed. Published video review is tracked separately below.
- [x] Integration:302 original actors/231 protected files preserved. One final Development package99.57s, exit0. Existing three-process actual-input route passed, all process exits0. No runtime C++ edits or separate Editor-target compile; BuildCookRun performed three game-target compile/link/metadata actions.
- [x] Documentation/media preparation: existing technical/performance/source/milestone docs updated;17 unchanged1920x1080 screenshots, one28s actual1280x720 gameplay recording and compact validation receipt prepared with SHA256 manifest. Failed desktop capture excluded. The owner dismissed Windows firewall UI before the successful replacement.
- Git delivery target: `phase-05-2-presentation-contact` to `main` by Pull Request, no merge. Asset/script commit: `566979c407a08d8cfbc1cd5ebd03c30b858de946`; accompanying documentation/media commit follows it. GitHub branch/PR status is authoritative for remote publication.

Ruling: the owner's detailed implementation authorization covers the local asset edits, native imports, captures and bounded performance tests. Keep the existing single project workspace on a clean feature branch; duplicating its native asset/cache setup adds no useful isolation here. Use native authoring/import scripts because the optional game-dev validator targets glTF packages rather than the project's FBX/Unreal pipeline. No provider execution.

## Reference checks

- [Epic UE5.8 Auto Exposure](https://dev.epicgames.com/documentation/unreal-engine/auto-exposure-in-unreal-engine): distinguish metering/exposure from actual illumination and geometry occlusion.
- [Blender4.5 IK constraint](https://docs.blender.org/manual/en/4.5/animation/constraints/tracking/ik_solver.html): preserve authored hand target constraints, use elbow poles to control bend, bake evaluated transforms for Unreal import.

## Actual results

See [matched images](media/phase-05-2/README.md), [compact evidence](media/phase-05-2/validation.json), [runtime ledger](MILESTONES.md#phase052-presentation-and-contact-polish), and [performance](PERFORMANCE_BUDGET.md#phase052-packaged-observations).

| Weak point | Actual change | Observed result / remaining limit |
|---|---|---|
| Box-like railcars and dark wheels | Formed roof cross-section, recessed panels/trim, handles, buffer cylinders, dished wheels/hubs/bolts, bogie/coil/axle structure | Wheels and underframe now readable at route distance; still stylized prototype metal and repeated panel language |
| Bare Workshop aperture | Layered guide/frame, base plates, shutter housing/canopy, drain/utility box | Entrance reads as supported industrial equipment. Existing closed Editor gate remains black; runtime opens on native readiness |
| Empty service yard | Three curated maintenance clusters, spools/crates/barrels/trolley, scrap, seven weeds and seven feathered grime decals | Better near-field scale cues, flank and center remain open. Central ground is still visibly uniform |
| Weak near/far connection | Three low-cost roof/tank/vent/stack groups behind perimeter; gantry hangers and pipe supports | Intermediate industrial silhouettes connect existing wall/towers; no playable city added |
| Occluded black view | Correct invalid railcar camera; local flank/interior fill and shadow/highlight local contrast0.8/0.9 | Six sampled views readable. This does not prove every possible camera angle is lit; global EV and quality unchanged |
| Straight/stiff assembly | Animated elbow poles and shoulder offsets, wrist approach/roll, independent finger acquisition/release, prop-relative contact | Grip silhouettes and separate inspection/seat/secure beats are clearer. Long sleeve segments, oversized cuff/glove shapes and intermittent contact penetration remain prototype limitations |
| Optic simply placed | Lift4.4–6.4s, inspect6.4–8.1, align9.1, micro-adjust9.8, seat11.55/settle12.15, secure13.15–14.3, confirm15 | Deliberate staged external calibration with quiet original seat/secure audio; no real firearm internals or procedural construction |
| Weak reveal | Native camera settle and small final reveal, return to exact camera baseline on Stop | Native binding evaluated at6/19.2s and restored each time; packaged return restores normal upgraded weapon/control |

No new story, saved IDs, weapons or runtime frameworks. Phase03/05/051 assets, schema1, checkpoint transforms and gameplay collision remain intact. The existing106,828-triangle hands/weapon presentation was reposed, not rebuilt; the ROOK-5 hero still reads as prototype. Final human aesthetics, continuous-motion satisfaction, audio mix and natural12–16minute pacing remain pending.

Validation caveats: nine static poses cannot prove temporal motion quality. Full native playback ran in the packaged lifecycle test, while the first attempted desktop recording was blocked by Windows firewall UI and excluded from publication. Editor screenshots were redundantly repeated after sandbox process visibility was misread; all three final capture jobs completed, and only the last matched set is published. No Editor/capture job overlapped performance sampling. Known engine-startup self-test condition messages remain separate from Python pass receipts; packaged logs had no Error/Fatal/Ensure matches. Expected teardown streaming Failed messages occurred after successful route receipt/exit request, not during accepted traversal.

Replacement recording follow-up: owner dismissed the firewall prompt on2026-11-01. One dedicated `CR04_TEST_Phase052VideoRetry` process captured the actual client at1280x720/30fps for28s, silent. Native and capture exits0; actual Stop/retry, pause, natural completion, upgraded view and reload checks passed. All840video frames decoded; ten samples across0–27s were visually inspected with no unrelated window/UI obstruction. The clip shows the complete22s presentation and return to gameplay. This adds a genuine continuous artifact for owner review, not a claim that sampled frames establish natural movement or accepted audio. No game code/assets, rebuild, package or benchmark changed.

## Final independent review

One fresh read-only reviewer independently rehashed231 protected files and inspected scripts, raw native receipts and representative before/after images. No gameplay integration blocker found. The reviewer flagged an evidence-overwrite risk as Minor; author regraded it Important because accidentally replacing the original before inventory/images would destroy the audit baseline. Fixed with an early refusal when any before evidence exists. `Scripts/test_capture_guard.py`: observed failing original-preservation case before the fix, then3/3 preflight cases passed after the fix. No native asset, runtime code or package changed for this guard; no repackage required.

Final: fixed before-evidence overwrite — capture-guard RED (1 error of3) to GREEN3/3. No deferred review minors.

Final: Ruling: video/publication bookkeeping is delivery work, completed only when verified files exist; a firewall-obstructed desktop capture is never review media. Cost if wrong: unrelated desktop content could be exposed, so it remains ignored and excluded.

Final: Ruling: human continuous-motion/contact/audio/hero-quality and natural pacing acceptance remain open; native playback/static frames cannot answer them. Cost if wrong: overstating polish. Report these limits and require owner review.

Final: Ruling: universal view readability, long-run memory/VRAM and stable60FPS remain unproven by the bounded samples. Cost if wrong: unsupported performance/safety claims. Preserve measured conditions and remaining gaps.

Final: Ruling: sparse central ground, sleeve shapes and repeated material reads remain explicit art limitations within this focused revision, rather than grounds for an unauthorized level/framework rewrite. Cost if wrong: another focused art pass may be needed after owner review.

Final: Ruling: native Editor receipts, hashes, scripts and rendered/runtime evidence support binary asset integration; the reviewer did not independently parse Unreal binary internals. Cost if wrong: an unsampled asset defect remains possible; do not label review as exhaustive engine-level verification.
