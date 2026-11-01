# Elias anatomy review candidate

The anatomical geometry, default skeleton, skin weights and six muscle/hand morph targets derive from MakeHuman's **CC0-1.0 graphical data**, pinned to commit `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`. The OBJ and rig headers identify Data Collection AB, Joel Palmius and Jonas Hauquier; target headers credit Manuel Bastioni and the subsequent MakeHuman community transfer. Retain these credits even though CC0 does not require attribution.

- [Publisher license explanation](https://www.makehumancommunity.org/about/license.html)
- [Publisher graphical-data license](https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.ASSETS.md)
- Exact source URLs, byte counts and SHA-256: `upstream-manifest.json`.

MakeHuman program code is separately AGPL licensed. **No program code was copied or executed.** The independent scripts here parse published graphical data. Raw inputs stay in ignored evaluation storage and can be reacquired with `acquire_reference.py`. The `.blend` contains the derived anatomical mesh and necessary deform weights; its original atlas images are packed and also supplied as editable PNG sources.

Fitted garments, procedural shading/atlas baking, articulation keys, authoring scripts and review setup are Cinder Relay project work. `LicenseRef-CinderRelay-Project` records project ownership, not an additional public reuse license. CC0 upstream rights are preserved; publishing this derivative does not claim exclusive rights to the underlying anatomy. No purchased Fab or KINEMATION content is present. The restrictive Fab candidates remain references only.

## Coordinate and rig contract

Blender geometry uses centimeters (`scene.unit_settings.scale_length=0.01`), X forward, Y lateral, Z up. The FBX export follows the existing project `-Y` forward / `Z` up convention and imports with scene-unit conversion. The independent GLB package explicitly converts geometry, edit bones and translation keys to meters in memory; it does not save those export-only transforms into the Blender source.

The mesh has 49 deform bones, including root, original MakeHuman split upper/lower arm chains, wrists, metacarpals and independent finger chains. Four additional Blender-only IK control bones and hand/elbow targets are editable but **disabled in this anatomy clip**. This is not a Manny-compatible skeleton by bone name. Weapon contact, thumb opposition, active IK calibration and gameplay/workbench retargeting remain pending review.

The only current animation is a 3-second, 60-fps **anatomical articulation sample**: relax, curl, wrist twist, countertwist, grasp shape, release. It is not Idle/Reload/FireCycle, and does not demonstrate real prop contact. No clip is activated in gameplay. Normal atlas uses OpenGL tangents; the Unreal import flips green and uses normal-map compression.

`create_elias_review.py` refuses to overwrite an existing source. `finish_elias_review.py` is a one-time targeted atlas/budget pass, not a script to rerun for animation edits. Use `export_elias_review.py` for subsequent exports of the existing editable source. Do not rerun earlier chapter generators.
