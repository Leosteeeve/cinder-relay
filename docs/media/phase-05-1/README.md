# Phase 05.1 visual review

The owner authorized publication of these six screenshots and one recording after the Phase 05.1 implementation delivery. These are unchanged copies of the actual renders shown in the delivery report, tracked through Git LFS. [manifest.json](manifest.json) records their SHA-256 hashes, sizes and dimensions.

These samples support visual review; they do not establish production quality, continuous human motion acceptance, or benchmark performance. See the [milestone evidence and limitations](../../MILESTONES.md#phase051-actual-implementation-and-validation), [performance measurements](../../PERFORMANCE_BUDGET.md#phase051-packaged-observations), and [asset provenance](../../ASSET_SOURCES.md#phase051-authored-assets-and-limited-cc0-inputs).

## ROOK-5 and sights

Actual Windows Development gameplay captures at 1920x1080 from the same player location. The diagnostic fixture selects the base/upgraded appearances; it is not evidence of earning the upgrade through normal play. Base ADS is 65 degrees; upgraded ADS is 60 degrees.

### Base hip view

![Base ROOK-5 hip view](rook-base-hip.png)

### Iron-sight ADS

![Base ROOK-5 iron-sight ADS](rook-iron-ads.png)

### Upgraded hip view

![Upgraded ROOK-5 hip view](rook-upgraded-hip.png)

### Survey Optic ADS

![Survey Optic ADS](rook-optic-ads.png)

## Rail Yard before and after

Actual Unreal Editor renders, 1920x1080, with streamable zones visible for comparison. Both use camera position (-1710, -60, 165) cm, pitch -2 / yaw 7 / roll 0 degrees and FOV 85. This is a matched art comparison, not proof of runtime streaming readiness.

### Before

![Rail Yard before Phase 05.1](rail-yard-before.png)

### After

![Rail Yard after Phase 05.1](rail-yard-after.png)

## Actual assembly playback

[Open or download the 28-second gameplay recording](assembly-gameplay.mp4?raw=true).

The 1280x720 H.264 recording captures actual sequential packaged gameplay, including the workbench presentation and return to the weapon view. It is silent; recording was requested at 30 fps and was separate from performance sampling. The route includes a short pause check. If GitHub does not preview the Git LFS video, use **View raw** or **Download**.

The source meshes, Blender rig and animation remain editable. The clip is not assembled from screenshots. Earlier failed/stale captures, test saves, logs, packaged executables and recording tools remain local and are not included here.
