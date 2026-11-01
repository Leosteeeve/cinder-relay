# The Dead Station — Phase05 Art Direction

## Intent and boundaries

Ruined Industrial Realism: a repair technician reads an abandoned railway facility through the things people maintained, repaired and left unfinished. Cold steel and oxidized surfaces lead toward a small warm Workshop, then restrained cyan relay technology. This is an original prototype art pass, not a claim of photorealism or AAA readiness.

The owner's Phase05 brief is the approved scope. Existing gameplay collision, checkpoint transforms/IDs, schema1 whitelists, mission order and native three-zone streaming are constraints. Art must communicate the existing playable space before adding decorative density.

## Reference observations and original translation

The named inspirations are studied as design principles: industrial route readability and contrasting practical light (Black Mesa); readable combat silhouettes and layered industrial depth (Titanfall2); wear concentrated around contact, exposure and past human work (Red Dead Redemption2). No source game model, scene, character, dialogue, texture or sound is copied. These are proposed original translations, not an asset provenance claim.

## Palette, surfaces and light

| Role | sRGB direction | Use |
| --- | --- | --- |
| Cold steel | #526774 | Painted sheet metal, distant structures |
| Oxidation | #754734 | Seams, lower panels, exposed fasteners |
| Workshop amber | #D19A57 | Practical lamps, small wayfinding accents |
| Relay cyan | #60B6BB | Low-area indicators and activation feedback |
| Charcoal | #202A2E | Machinery recesses, rubber, helmet/weapon detail |
| Aged concrete | #77766C | Large structural surfaces, low contrast variation |

Surfaces use shared native material families with restrained macro variation, roughness and fine normal detail; no uniform mirror metal or random high-contrast noise. Wear follows edges, rain streaks, foot traffic and mechanical use. Avoid a unique large texture for each small prop. Lighting remains readable at player eye height: cool diffuse exterior, amber local Workshop practicals, dim concrete bunker with cyan accents. Retain existing renderer/scalability baseline; tune light placement/exposure locally, not a project-wide renderer switch. Minimize overlapping shadowed local lights. Do not use bright emissive strips as the sole source of usable room light.

## Scale, geometry and modular kit

Centimeters, +X along chapter progression, +Z up. Keep all original collision and navigation until a demonstrated replacement passes equivalent traces/path checks. Decorative components have no gameplay collision and cannot affect navigation. Railcar detail fits the original ~900x310cm body envelope; door and central route clearance remain unchanged. Small dressing clusters belong beside existing supports/walls, not uniformly across floors. Workshop camera/hand volume and both interactive work surfaces remain empty of new obstructions.

Original Blender kit: railcar shell/bogies, I-beam/brace modules, corrugated steel panel, service cabinet/control rack, cable/pipe runs, lamp cage, industrial pump, maintenance tools, debris cluster and sparse vegetation. Repeat shared geometry where useful; hero train and service equipment get coherent assembled silhouettes, bevels and functional joints. Preserve Phase03 source bytes; improved restoration source is a separate Phase05 derivative with documented changes.

Provisional per-asset budgets: hero railcar <=35k triangles, modular props generally <=5k, small tools <=2k, Warden <=25k, first-person kit <=25k. Shared surface maps normally512–1024px; at most2K for a justified hero surface. No speculative4K/8K packs. No additional expensive rendering feature by default. Use instancing for repeated detail where supported; enable Nanite only if measured geometry warrants it. Report actual counts/import bounds and memory, not just budgets.

## Composition and environmental story

- Rail Yard: preserve two-scout cover and northern flank. Train side and overhead steel form foreground layers; workshop amber is the destination. Localized discarded maintenance pieces suggest interrupted work. Opening is a player-controlled framed reveal, no prolonged control lock.
- Workshop: lamp pools on distinct calibration and power-module surfaces, tools organized by recent use, shelves at room edges. Provisional maintenance records explain local equipment, not the cause of The Quieting.
- Relay Bunker: conduits converge on Relay Nine, layered control cabinets behind a clear walkway. Native Sequencer animates existing objective-driven local lights/audio. Final MERIDIAN text and mission authority stay unchanged.

All additional clue text is provisional. New aesthetic events do not add persisted IDs. Restore reads existing objective/upgrade state and presents the appropriate settled appearance without replaying completed story beats.

## Production and acceptance

First author/import a small Rail Yard kit and inspect a real Unreal render before broad placement. Blender output alone does not pass05A. Preserve asset hashes/backups and old gameplay snapshots. Expand only after fixing major render/scale/composition faults. Use real continuous playback for the existing22s animation and short native enemy clips; still frames prove framing/contact only. One integrated Windows package and bounded actual-input route validate gameplay, disk persistence and cooking. A separate low-overhead sample measures p50/p95/p99 and >50ms spikes. One owner visual/pacing review is required for final art acceptance;12–16min remains a target until naturally timed.

Original project-authored assets avoid third-party public-repository restrictions and paid providers. Blender/UE are existing tools; their software licenses are not relabeled as the artwork license. See ASSET_SOURCES for exact source/import records. No external asset acquisition is currently required.

Technical references: [UE5.8 instancing](https://dev.epicgames.com/documentation/unreal-engine/instanced-static-mesh-component-in-unreal-engine?lang=en-US), [native audio volumes](https://dev.epicgames.com/documentation/unreal-engine/audio-gameplay-volumes-quick-start?lang=en-US), [Blender4.5 IK](https://docs.blender.org/manual/en/4.5/animation/constraints/tracking/ik_solver.html). Installed headers and Python bindings remain the API authority for the exact local builds.
