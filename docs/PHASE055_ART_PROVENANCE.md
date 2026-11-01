# Phase05.5 — Original title identity provenance

## Authorship and scope

The title stage, original monogram, typography layout and export scripts were authored for CINDER RELAY in this repository on2026-11-01. This is AI-assisted procedural Blender/vector authoring, not a third-party game screenshot or an image-generation-service poster. No paid provider or external photograph was used. The promotional architecture is an interpretation of the owner's Relay Nine brief; it establishes no new story facts or new playable map.

Editable source: `CinderRelay/ArtSource/Blender/Phase055/CR055_TheLastSignal.blend` and `create_identity.py`. The scene uses meters, deterministic seed55091, procedural materials, two editable cameras and packed station-label typography. It preserves all previous project sources. Four original Phase052 meshes are appended read-only from `CR052_YardDetail.blend`: CableSpool, MaintenanceTrolley, ScrapStack and ServiceCrate. Geometry is converted from the original centimeter authoring scale to meters in this stage. No marketplace geometry or source texture is introduced.

Original vector sources: `ArtSource/Interface/Phase055/CR055_RelayMark.svg`, `CR055_GameIcon.svg`, `CR055_TitleTypography.svg` and per-cover SVG composites. Live text remains editable. `create_identity_graphics.py` reproduces the original paths and typographic exports. The mark is an open C and relay-like R with one amber contact and a small muted-cyan carrier point; it is not an extracted game icon or font glyph.

## Art brief and exclusions

**Brief:** CINDER RELAY — THE LAST SIGNAL. Environment-led rail approach, industrial debris and a damaged signaling fixture in the foreground; Relay Nine with a broken roof and a localized warm maintenance light; abandoned blocks, industrial towers and a distant cyan carrier through depth haze. Isolation, industrial decline and restrained hope. Quiet left-side area for the runtime title/actions.

**Exclusions:** no explanation of MERIDIAN or The Quieting; no copied game art; no generative neon city; no decorative holographic HUD; no character-led poster; no fonts/icons extracted from references; no copyright-restricted audio or images; no purchase.

## Font selection and license

Barlow Regular and Medium provide the body/interface hierarchy. Barlow Condensed SemiBold supplies the title/large numeric hierarchy. Principal upstream project: [The Barlow Project](https://github.com/jpt/barlow). The unmodified TTF files were downloaded from the official Google Fonts repository:

- [Barlow Regular](https://raw.githubusercontent.com/google/fonts/main/ofl/barlow/Barlow-Regular.ttf)
- [Barlow Medium](https://raw.githubusercontent.com/google/fonts/main/ofl/barlow/Barlow-Medium.ttf)
- [Barlow Condensed SemiBold](https://raw.githubusercontent.com/google/fonts/main/ofl/barlowcondensed/BarlowCondensed-SemiBold.ttf)
- [Official included SIL Open Font License1.1](https://raw.githubusercontent.com/google/fonts/main/ofl/barlow/OFL.txt)

Copyright2017 The Barlow Project Authors. License: **SIL Open Font License1.1**. Unmodified fonts may be bundled, embedded and publicly redistributed with the software when their copyright and license remain included; the font itself remains under OFL and may not be sold alone. The license does not apply to the resulting artwork/documents. Original project artwork is not relabeled OFL or CC0. `Fonts/OFL.txt` is preserved. `font-provenance.json` records individual source URLs, author, license, modifications, exact bytes and SHA256. No font renaming/modification is performed.

## Runtime versus promotional exports

The runtime imports only the title-free1920x1080 `CR055_MenuBackground.png` and compact512px mark as needed. UE texture compression/cook/residency is verified by the integration owner, not inferred from PNG size. Promotional landscape2560x1440 and portrait1600x2400 sources remain separate. The runtime does not need to load the portrait, promotional composite or Blender scene.

The promotional composites add separately editable title typography to the same original plate. Per-cover SVG files retain linked plate and live title/tagline text; the PNG composites are presentation exports. Source PNGs contain no title burned into the environment plate.

## Reproduction and evidence

Blender4.5.11 LTS, Cycles with OptiX when available, AgX / Medium High Contrast,8CPUthreads. Initial previews are1280x720/24samples; final output is96samples with native denoising. The installed `game-dev`1.0.2 capabilities/doctor reported local Blender available and no paid-provider credentials; no provider operation was attempted. This is a promotional image source, not a reusable runtime3D asset package, so no GLB vendoring receipt is claimed.

Run `blender.exe --background --factory-startup --threads 8 --python CinderRelay/ArtSource/Blender/Phase055/create_identity.py --` from the repository. This writes only the owned Phase055 stage/artwork. Preview with `--preview`; render an existing stage with `--render-only` after opening its blend. Run `create_identity_graphics.py` with Python/Pillow after the plates exist for the icon and separate title exports.

Local authoring evidence stays under ignored `.environment-local/phase-05-5/art/`. An initial operator-heavy scene build was stopped; direct mesh construction removed the authoring overhead. A preview exposed missing foreground framing and inward cube normals that prevented physical fog; these were corrected in the source, then the cool volume scene was visually inspected. No old generator was executed. Empty directories created by an early corrected output-path typo were verified empty and removed non-recursively.

**Validation status:** final Blender rendering exited0. Landscape plate2560x1440, title-free runtime plate1920x1080, portrait plate1600x2400, both promotional typography composites and the512x512 mark/icon were inspected as actual pixels. An independent native Blender reopen exited0 and verified2cameras,2754objects,15source/export file hashes and0unpacked external dependencies. Exact dimensions, source hashes, camera transforms and color management are recorded in `ArtSource/Interface/Phase055/export-metadata.json`. The new Python authoring/verification files passed `py_compile`.

Local commands/evidence: final render log `.environment-local/phase-05-5/art/final-render.log`; reopen command `blender.exe --background CinderRelay/ArtSource/Blender/Phase055/CR055_TheLastSignal.blend --threads 4 --python CinderRelay/ArtSource/Blender/Phase055/verify_identity.py`; receipt `.environment-local/phase-05-5/art/source-verification.log` contains `CR055_IDENTITY_SOURCE_VERIFIED`. Both native processes exited0. No Blender render remains running.

This evidence establishes original artwork/source persistence and bounded visual inspection, not human artistic acceptance. It does not establish Unreal runtime import, texture residency or packaged menu behavior; those are integration-owner checks. The scene is a deliberately simplified promotional stage and does not claim photoreal architectural reconstruction or final human approval.
