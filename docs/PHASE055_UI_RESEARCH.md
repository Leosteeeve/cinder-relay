# Phase05.5 UI research and layout studies

Date: 2026-11-01. This is a design study and inspection record, not a claim of runtime UMG interaction or owner approval. Implementation contract: [INTERFACE_AUDIO_05_5.md](INTERFACE_AUDIO_05_5.md).

## Method and provenance

Viewed actual screenshot pixels from all four requested games. Reference screenshots and research PDFs are retained only in ignored `.environment-local/phase-05-5/ui-research/`; they are not project assets and must not be staged. The three original layouts use only original vector-like drawing plus Barlow fonts. No source game fonts, icons, textures, exact layouts or screenshot pixels appear in the mockups.

The original screenshots inform the observations below; the CINDER RELAY applications are our own design judgments. Professional reference: EA DICE designer Marcus Andrews's [Game UI Discoveries: What Players Want](https://www.gamedeveloper.com/design/game-ui-discoveries-what-players-want). The article argues for preserving player functionality when choosing diegetic or conventional interfaces and identifies the first-person camera's limited space for physical interface objects. This supports a restrained fiction-grounded style with a readable two-dimensional inventory, rather than introducing a costly physical UI model. The [GDC session entry for Dino Ignacio's Crafting Destruction](https://www.gdcvault.com/play/1017723/Crafting-Destruction-The-Evolution-of) confirms the Dead Space lead designer's focus on the interface's development and diegetic integration; the full talk was not watched in this task.

## Reference observations and original application

### Titanfall 2 — hierarchy under movement

Viewed [Abyss campaign screenshot](https://cdn2.unrealengine.com/titanfall-2-abyss-1-2560x1440-ea4c923e1c18.png), published in [Epic's campaign retrospective](https://store.epicgames.com/en-US/news/five-levels-that-show-why-titanfall-2-is-one-of-the-best-shooters-ever-made). The frame uses a very small crosshair, clustered weapon/ability information and a separately emphasized incoming transmission; large scene areas remain unobstructed. The weapon model's own display supplements the HUD.

Application: make the ROOK-5 magazine number the largest gameplay number; reserve ammo and labels secondary; short-lived feedback near the center; objective and subtitle on separate visual bands. Preserve the already-authored optic instead of placing a second reticle over it. Do not copy Titanfall's arrangement, ability tiles, icons or comms frame.

Professional context: David Shaver's [Invisible Intuition, GDC2018 slides](https://davidshaver.net/DShaver_Invisible_Intuition_GDC2018.pdf), downloaded and text-inspected. The opening describes guiding through level layout while reducing reliance on HUD markers and forced camera movement. It is a level-design talk, not a claim that its author designed the final Titanfall HUD. Our inference is to keep CINDER RELAY's objective concise and let the authored maintenance light/route retain navigational importance.

### Dead Space — a coherent fictional explanation

Viewed the original [Steam promotional inventory image](https://cdn.cloudflare.steamstatic.com/steam/apps/17470/0000006495.jpg). Its projected inventory groups item icons, selection description, suit state and navigation controls, while keeping the character visible. The selected item's textual name/description complements its icon. A strong fiction metaphor does not remove familiar selection and grouping.

Application: use the language of a maintenance record and field equipment, with stable categories, readable item state and a selected-item description. Limit the list to actual chapter equipment. Borrow the idea of coherent framing, not the blue holograms, hexagonal weapon slots, perspective distortion, empty slot grid or vulnerable unpaused interaction. CINDER RELAY explicitly pauses its default Field Pack.

### Metro Exodus — equipment is the subject

Viewed the [crafting screenshot](https://cdn.mos.cms.futurecdn.net/fcLayoUMYBGTqFSok3egeZ.jpg) embedded in [PC Gamer's crafting guide](https://www.pcgamer.com/metro-exodus-crafting-guide/). This is screenshot evidence, not a primary account of 4A's design intent. The visible object occupies the work surface; short resource counts, item description and action prompts frame it. Physical materials and tools create tactility without requiring dense ornament in every label.

Application: give the selected Field Pack item a large original silhouette and clear status; use restrained paper/steel colors. Keep wear on the environment/art. The bag has no crafting action, currency, weight, new resources or economy. Do not infer new Elias equipment/backstory from the reference.

### Black Mesa — sparse, contextual information

Viewed the developer's [Steam announcement HUD image](https://clan.akamai.steamstatic.com/images/8672783/30a66384faaa3f9516ec263e63a8ea824d8c51f1.jpg), from the [Crowbar Collective announcement archive](https://store.steampowered.com/news/posts/?appgroupname=Black+Mesa&appids=362890&enddate=1575675346). Health/suit and weapon counts occupy opposing bottom corners; the center is clear aside from the crosshair. Labels and icon forms communicate compactly without a persistent controls paragraph.

Application: life bottom-left, ammunition bottom-right, contextual interaction near the aiming region, dedicated subtitle space above the bottom status cards. Move the long controls sentence into Help. Do not copy the orange seven-segment treatment or HEV iconography. Keep enough text contrast against both dark and lit locations.

## Original design decisions

1. **Identity:** maintenance records and surviving instrument panels. Warm white, oxidized amber focus, restrained cyan completion, olive-grey secondary text. No neon-blue theme, repeated hexagons or scanline overlay.
2. **Typography:** Barlow Regular/Medium for content and Barlow Condensed SemiBold for title/numbers, SIL Open Font License1.1. Fonts and exact provenance live in `CinderRelay/ArtSource/Interface/Phase055/Fonts/`. Main title remains editable text. Avoid relying on the fonts for unsupported arrow glyphs; use text labels or original drawn icons.
3. **Layout:**48px safe inset at1080p;8px spacing unit;50px menu targets; balanced anchored corners and a centered subtitle panel. The2560x1600 compositions retain the extra vertical space instead of stretching a16:9 image.
4. **States:** focus uses an amber rail and filled steel background; selected equipment uses a cyan rail plus explicit state text. Disabled controls need a reason and differ from unselected controls. Health danger requires both a label and color. No repeated combat flashing.
5. **Navigation:** pointer hit regions plus visible keyboard focus; Enter activates, Escape backs out; I toggles Pack. Arrow navigation must stay legible even when the selected typeface lacks arrow glyphs. Controller-readable selection styling is considered; full gamepad support is not implied.
6. **Motion/audio:** use brief press/hit/confirmation transitions and quiet tactile sounds, triggered by events rather than state refresh. Objective expansion collapses after4seconds; other timing values are in the design contract.

## Mockup deliverables and review

Editable original source: `CinderRelay/ArtSource/Interface/Phase055/Mockups/render_mockups.py`. This uses Pillow; source art is generated from original primitives. `manifest.json` records output dimensions, hashes and provenance. Main-menu/background art here is a schematic blockout, explicitly labeled; it is not the final Blender title render. Inventory quantities and installed state are illustrative UI values, explicitly labeled, not runtime data.

| Layout | 1920x1080 | 2560x1600 | Inspected points |
|---|---|---|---|
| Main Menu | `MainMenu_1920x1080.png` | `MainMenu_2560x1600.png` | Five readable actions, clear active row, unobstructed title, lower save description, environment on right |
| Gameplay HUD | `GameplayHUD_1920x1080.png` | `GameplayHUD_2560x1600.png` | Objective fits, health/ammo separated, center clear, subtitle has contrast and avoids corner status |
| Elias Field Pack | `EliasFieldPack_1920x1080.png` | `EliasFieldPack_2560x1600.png` | Four categories, compact list, readable selected state/quantities/description, modal close/navigation instructions |

Review correction: the original Barlow arrow-character navigation labels rendered missing-glyph boxes. Replaced them with plain UP/DOWN and LEFT/RIGHT text and re-rendered. Changed an overly broad “Inspect & Equip” caption to “Inspection” because this phase does not introduce a new equipment-authority action. No cropped title/body text or overlapping corner/subtitle region was found in the six final layout images.

These observations establish a shared visual language for implementation. They do not verify UMG scaling, keyboard focus, hit targets, authored optic behavior, gameplay state, human aesthetic acceptance or audio. Those require the subsequent native integration and owner review.
