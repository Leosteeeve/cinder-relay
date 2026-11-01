# Phase05.5 audio research and event contract

Research date:2026-11-01. Public repository; license clearance and playable audio quality are separate gates. No purchase, restricted sample, copyrighted music or recorded voice is included.

## Official source review

| Source | Verified license and attribution | Public source permission | Selection |
|---|---|---|---|
| [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds),100 files | Kenney,CC0-1.0; credit optional | CC0 permits redistribution and derivatives | Candidate only |
| [Kenney UI Audio](https://kenney.nl/assets/ui-audio),50 files | Kenney,CC0-1.0; credit optional | Same | Candidate only |
| [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds),130 files | Kenney,CC0-1.0; credit optional | Same | Candidate only |
| [Kenney RPG Audio](https://kenney.nl/assets/rpg-audio),50 files | Kenney,CC0-1.0; credit optional | Same | Candidate only |
| [Sonniss GDC Bundle License](https://sonniss.com/gdc-bundle-license/) | Official v2.0 effective2026-08-27; synchronization use, no attribution requirement | Restriction(c) forbids supplying original, modified or redesigned effects as sound-effect files without permission. Public extractable source assets are excluded | Not downloaded or integrated |
| [Mixkit Sound Effects Free License](https://mixkit.co/license/modal/sfxFree/) | Free use inside a larger end product | Explicitly prohibits redistribution alone, as stock/tool/template or with source files | Not downloaded or integrated |
| [Freesound license FAQ](https://freesound.org/help/faq/#licenses) | Each uploader chooses CC0,CC-BY or CC-BY-NC; no site-wide blanket grant | An exact asset's author/license/source would need verification; no individual sound selected | Not downloaded or integrated |

Kenney's official [support page](https://kenney.nl/support) confirms asset-page CC0 and optional credit. The [CC0 deed](https://creativecommons.org/publicdomain/zero/1.0/) permits copying, modification and distribution, including commercially. These findings do not prove that the retrieved bytes are sounds.

Acquisition diagnosis: indexed Kenney ZIP links redirected to HTML; the current official page uses a public signed-download endpoint, which returned403 in this environment. Two retrieval approaches failed; retries stopped. The responses remain ignored local diagnostic evidence, not admitted audio assets. No candidate file hashes are represented as valid sound hashes. The deliberately selected fallback is original project-authored procedural sound design, already permitted by the owner brief.

## Existing implementation audit

- `CRWeaponViewComponent::Shot`, `ConfirmedImpact`, `Cue`, `Hurt` own the old weapon/damage audio. `DA_Rook5` contains old SoundBase references and remains immutable.
- `CRWeaponHandling::HandleAnimationCue` has montage-instance guards and a consumed shot token; FeedOut/FeedIn already play handling sounds. The old full2.4s ReloadSound overlaps those markers. Replace its playback with a short onset, never stack a full timeline and individual cues.
- `CRCharacter::UpdatePrompt` accumulates grounded displacement at0.1s cadence. It rejects stationary/teleport/dead/presentation/slide movement but selects only X-based yard/interior footsteps. Use actual floor hit/material/physical surface with a documented zone fallback; retain the cadence.
- Slide ownership is `TryStartSlide`/`EndSlide`. An owned AudioComponent can loop only while the accepted slide is active, and stop on pause/cancel/death/travel.
- Existing streamed `CR05_Ambience_<zone>` AmbientSound actors use native attenuation/occlusion. Existing power/ending Level Sequences own their audio; avoid changing story playback authority.
- Installed `UGameplayStatics::PlaySound2D` defaults `bIsUISound=true`. Non-UI weapons/handling/damage should explicitly pass false so world pause freezes them; only UI feedback continues during menus.

## Original source set

Source: `CinderRelay/ArtSource/Audio/Phase055/author_audio.py`. Outputs: `Waves/S_CR055_*.wav`; full per-file manifest with SHA256, author, original-source URL, usage, modifications, public-repository permission, sample format, channel count, peak/RMS and clipping metrics: `manifest.json` beside the script.

The sound set uses deterministic filtered-noise transients, inharmonic material modes, timed handling contacts, controlled early reflections and quiet periodic room tones. No sample or waveform from another game/library is used. The project is the author; publication is authorized original project source, not a new CC0 license granted over the project. All old Phase05/052 audio sources remain unchanged.

| Event/key | Source family | Category/owner |
|---|---|---|
| Accepted shot | RookOutdoor1–3 / RookWorkshop1–3 / RookBunker1–3 | Weapons; one composite mechanical onset/report/tail from existing accepted OnShot |
| Manual cycle | Cycle | Weapons; one consumed montage cycle marker |
| Cosmetic casing | Case | Weapons; one consumed EjectCase token, no ammo/damage |
| Dry fire | Dry | Weapons; existing dry-fire cooldown |
| Reload accepted | ReloadStart | Weapons; short onset from existing Reload cue |
| Feeding component | FeedOut / FeedIn | Weapons; existing montage-instance guards |
| Reload transfer finished | ReloadComplete | Weapons; native CompleteReload after the one transfer |
| Solid impact | Impact | Weapons; native confirmed impact location with attenuation |
| Damage received | Damage | Foley; health damage event, no voiced grunt |
| Footstep | FootConcrete1–3 / FootMetal1–3 / FootGravel1–3 / FootIndustrial1–3 | Foley; grounded distance, one selection per step |
| Slide | SlideStart / SlideLoop / SlideEnd | Foley; owned lifecycle, loop stops on cancellation |
| Menu feedback | UISelect / UIConfirm / UICancel / UIError | UI; focus transitions/action acceptance only, not state refresh |
| Item collection | Collect | UI; actual collection, not merely opening inventory |
| Objective/upgrade/checkpoint | Confirm | UI; actual transition; save cue only on native successful callback |
| Hit / defeat | Hit / Kill | UI; existing confirmed enemy impact |
| Zone ambience | AmbYard / AmbWorkshop / AmbBunker | Ambience; existing zone-local actors,16s loops |

No Music asset exists; hide its slider or explain that no music is present rather than presenting an ineffective control. Voice/Radio remains an independent native class reserved for existing signal/presentation audio; no new voice acting.

## Proposed native integration

`UCRAudioSettingsSubsystem : UGameInstanceSubsystem`: `float GetVolume(FName) const`, `void SetVolume(FName,float)`, `void SavePreferences()`, `void ApplyMix(UWorld*)`, `void PlayUI(FName)`, `void PlayEvent(FName,const UObject*,FVector,bool Spatial)`, `bool IsReady() const`. Config values are finite and clamped0..1; invalid stored values fall back to defaults. Store separately from ChapterSaveGame and do not touch its schema/checksum. A game-instance subsystem survives level travel; apply one mix for the current audio device without repeated Push stacking.

Hierarchy: Master>SFX>Weapons/Foley; Master>Ambience/UI/Voice/Music. Native SoundClass/SoundMix assets. Class overrides use actual installed `SetSoundMixClassOverride` signature; persistent critical SFX/cues async-load once and keep resident pointers. Gameplay playback never calls LoadSynchronous. Native data assets may hold references for authoring; old assets are not rewritten.

Suggested concurrency: accepted shots3 voices, handling3, own steps2, UI2 with35ms retrigger gate, spatial impacts6, ambience3. Short release avoids pops. Each category needs independent assets because an exhausted footstep group must not evict an accepted shot. [Epic concurrency reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/sound-concurrency-reference-guide).

Use mono spatial impacts/room tones with native attenuation and occlusion. First-person own weapon report is stereo2D with restrained baked early reflections; choose environment by authoritative current zone rather than broad world scans. Outdoor is diffuse/open; Workshop has spaced metallic early reflections; Bunker is short and hard. Existing audio zones remain small and streamed. [Epic attenuation reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/sound-attenuation-in-unreal-engine).

## Verification boundary

Validate actual PCM decode, no clipped samples, loop-boundary derivative versus ordinary adjacent samples, bounded voice counts, category routing, pause behavior, same-event deduplication, settings across process restart and native save regression. Capture real audible gameplay if supported and inspect its audio stream/levels. Numerical checks and asset counts are not listening evidence. Stereo-headphone human review remains necessary for harshness, timbre, balance and masking; no claim is made before that review.
