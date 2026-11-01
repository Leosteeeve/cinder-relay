# Phase05.2 visual comparison

Actual Unreal renders and packaged gameplay recording, published for owner review. These are unchanged capture bytes, tracked by Git LFS; [manifest.json](manifest.json) records SHA256 and provenance. No AI-generated replacement frames or composited fake gameplay. See the [visual report](../../PRESENTATION_05_2.md) and [performance conditions](../../PERFORMANCE_BUDGET.md#phase052-packaged-observations).

## Matched environment views

All pairs use1920x1080, FOV85 and the same position/rotation within each pair. Native Editor renders show the streamed levels together; this is an art comparison, not runtime streaming acceptance. The black entrance panel is the existing streaming gate in its Editor closed state, not an unlit Workshop interior. Runtime readiness opens it. The prior Phase051 black railcar shot was inside collision and is excluded from these valid-route comparisons.

| View / camera cm; pitch,yaw | Before | After |
|---|---|---|
| Initial composition;(-1710,-60,165);-2,7 | ![Before spawn](before-spawn.png) | ![After spawn](after-spawn.png) |
| Accessible railcar route;(-650,430,165);-2,38 | ![Before railcar](before-train-route.png) | ![After railcar](after-train-route.png) |
| Entrance frame;(1120,0,165);-2,0 | ![Before entrance](before-workshop-entrance.png) | ![After entrance](after-workshop-entrance.png) |
| Workshop interior;(1950,100,165);-3,-15 | ![Before interior](before-workshop-interior.png) | ![After interior](after-workshop-interior.png) |
| Shadow flank;(-950,1150,165);-3,-5 | ![Before flank](before-shadow-flank.png) | ![After flank](after-shadow-flank.png) |
| Wall/midground;(700,500,165);10,65 | ![Before midground](before-midground.png) | ![After midground](after-midground.png) |

## Contact poses

Five selected frames from nine actual UE skeletal-animation samples. A fixed settled camera is used here; these do not prove temporal smoothness or evaluate the animated camera track. Native track evaluation and packaged runtime acceptance are separate evidence.

| Inspect6.4s | Micro-adjust9.8s | Seat11.55s |
|---|---|---|
| ![Inspect](contact-2.png) | ![Align](contact-4.png) | ![Seat](contact-5.png) |

| Secure13.8s | Retrieve20.5s |
|---|---|
| ![Secure](contact-6.png) | ![Retrieve](contact-8.png) |

## Actual gameplay recording

[Watch/download the28-second gameplay recording](assembly-gameplay.mp4?raw=true). Actual Windows Development game client,1280x720,30fps,H.264, silent. It includes the retry after the deliberate Stop test, the full22-second presentation with its short pause check, successful upgrade, and return to gameplay. This is sequential desktop capture cropped to the verified game client, not assembled pose screenshots. Use **View raw** or **Download** if GitHub does not preview the LFS video.

After the owner manually dismissed the firewall prompt, the replacement captured only the intended game in ten sampled frames spanning0–27s. All840frames decoded successfully; native game and capture exits0, dedicated test route passed. Recording ran separately from performance sampling and is not an audio-mix or continuous human motion-quality acceptance. The first obstructed capture remains ignored and excluded. The [Phase051 recording](../phase-05-1/README.md#actual-assembly-playback) is retained for historical comparison.

Limitations: the gun, glove/cuff proportions and some straight sleeve segments remain prototype art. Ground/wall material repetition and sparse central-floor detail are still visible. Human motion, sound mix and final aesthetic acceptance remain open; these captures do not establish AAA quality or a measured12–16minute playthrough.
