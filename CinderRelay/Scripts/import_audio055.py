"""Phase055 native audio import and bounded actor/sequence audio assignments.

Run in UE5.8.4 after compiling the Phase055 module. Never reruns old generators,
changes DA_Rook5, rewrites old sound/sequence assets, or touches player saves.
New assets require ownership metadata on a repeat run. Native import failures
stop rather than substituting fake binary assets.
"""
import hashlib
import json
from pathlib import Path
import unreal

project = Path(unreal.Paths.project_dir())
source = project / "ArtSource/Audio/Phase055"
evidence = project.parent / ".environment-local/phase-05-5/audio-import"
evidence.mkdir(parents=True, exist_ok=True)
root = "/Game/Generated/Phase055"
audio_root = root + "/Audio"
owner = "CinderRelay.Phase055.Audio.v1"
assets = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manifest = json.loads((source / "manifest.json").read_text())
assert manifest["owner"] == "CinderRelay.Phase055.OriginalAudio.v1"


def owned(path):
    asset = assets.load_asset(path) if assets.does_asset_exist(path) else None
    if asset:
        assert assets.get_metadata_tag(asset, "CR.GeneratedBy") == owner, "Refuse unowned asset: " + path
    return asset


def save(asset):
    assets.set_metadata_tag(asset, "CR.GeneratedBy", owner)
    assert assets.save_loaded_asset(asset), asset.get_path_name()
    return asset


def create(name, kind, factory):
    return owned(audio_root + "/" + name) or save(tools.create_asset(name, audio_root, kind, factory))


classes = {name: create("SC_CR055_" + name, unreal.SoundClass, unreal.SoundClassFactory())
           for name in ("Master", "SFX", "Weapons", "Foley", "Ambience", "UI", "Voice", "Music")}
parents = {"SFX": "Master", "Weapons": "SFX", "Foley": "SFX", "Ambience": "Master", "UI": "Master", "Voice": "Master", "Music": "Master"}
for name, cls in classes.items():
    properties = cls.get_editor_property("properties")
    properties.set_editor_property("volume", 1.0)
    properties.set_editor_property("pitch", 1.0)
    # UI-ness is chosen at the event call, so gameplay hit/kill cues pause.
    properties.set_editor_property("is_ui_sound", False)
    cls.set_editor_property("properties", properties)
    cls.set_editor_property("parent_class", classes[parents[name]] if name in parents else None)
    cls.set_editor_property("child_classes", [classes[child] for child, parent in parents.items() if parent == name])
    save(cls)
mix = create("SMX_CR055_Settings", unreal.SoundMix, unreal.SoundMixFactory())
for key, value in (("initial_delay", 0.0), ("fade_in_time", .08), ("duration", -1.0), ("fade_out_time", .08)):
    mix.set_editor_property(key, value)
save(mix)

concurrency = {}
for name, count, retrigger in (("Shot", 3, .0), ("Handling", 4, .0), ("Foot", 2, .08), ("Slide", 1, .0),
                              ("UI", 3, .025), ("Impact", 6, .0), ("Ambience", 3, .0), ("Voice", 2, .0)):
    item = create("CON_CR055_" + name, unreal.SoundConcurrency, unreal.SoundConcurrencyFactory())
    settings = unreal.SoundConcurrencySettings()
    settings.set_editor_property("max_count", count)
    settings.set_editor_property("resolution_rule", unreal.MaxConcurrentResolutionRule.STOP_OLDEST)
    settings.set_editor_property("retrigger_time", retrigger)
    settings.set_editor_property("voice_steal_release_time", .035)
    item.set_editor_property("concurrency", settings)
    concurrency[name] = save(item)

attenuation = create("ATT_CR055_Spatial", unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
settings = unreal.SoundAttenuationSettings()
settings.set_editor_property("attenuate", True)
settings.set_editor_property("spatialize", True)
settings.set_editor_property("attenuation_shape_extents", unreal.Vector(100, 0, 0))
settings.set_editor_property("falloff_distance", 2400.0)
settings.set_editor_property("enable_occlusion", True)
settings.set_editor_property("occlusion_volume_attenuation", .4)
settings.set_editor_property("occlusion_low_pass_filter_frequency", 2200.0)
settings.set_editor_property("occlusion_interpolation_time", .12)
attenuation.set_editor_property("attenuation", settings)
save(attenuation)


def concurrency_for(name, category):
    if name.startswith("S_CR055_Rook"):
        return concurrency["Shot"]
    if "Foot" in name:
        return concurrency["Foot"]
    if name.endswith("SlideLoop"):
        return concurrency["Slide"]
    if category in ("UI", "Ambience", "Voice"):
        return concurrency[category]
    if name.endswith("Impact") or name.endswith("Damage"):
        return concurrency["Impact"]
    return concurrency["Handling"]


sounds = {}
for spec in manifest["sounds"]:
    wav = source / spec["file"]
    assert hashlib.sha256(wav.read_bytes()).hexdigest() == spec["sha256"], str(wav)
    name = spec["name"]
    sound = owned(audio_root + "/" + name)
    if sound:
        assert assets.get_metadata_tag(sound, "CR.SourceHash") == spec["sha256"], "Intentional reimport required: " + name
    else:
        task = unreal.AssetImportTask()
        task.filename = str(wav)
        task.destination_path = audio_root
        task.destination_name = name
        task.automated = True
        task.save = True
        task.replace_existing = False
        tools.import_asset_tasks([task])
        sound = assets.load_asset(audio_root + "/" + name)
        assert isinstance(sound, unreal.SoundWave), name
    sound.set_editor_property("looping", spec["loop"])
    sound.set_editor_property("sound_class_object", classes[spec["sound_class"]])
    sound.set_editor_property("concurrency_set", {concurrency_for(name, spec["sound_class"])})
    sound.set_editor_property("loading_behavior", unreal.SoundWaveLoadingBehavior.RETAIN_ON_LOAD if spec["loop"] else unreal.SoundWaveLoadingBehavior.FORCE_INLINE)
    assets.set_metadata_tag(sound, "CR.SourceHash", spec["sha256"])
    assets.set_metadata_tag(sound, "CR.SourceAuthor", spec["author"])
    assets.set_metadata_tag(sound, "CR.SourceLicense", spec["license"])
    sounds[name.removeprefix("S_CR055_")] = save(sound)

# Explicit derivatives: preserve every earlier binary/source unchanged. The
# original sequencer lengths/bindings/sections remain unchanged; only Sound refs.
legacy_specs = [
    ("EnemyShot", "/Game/Generated/Phase05/Audio/S_CR05_RookShot", "CinderRelay.Phase05.v1", "Weapons", "Shot"),
    ("EnemyHit", "/Game/Generated/Phase05/Audio/S_CR05_Impact", "CinderRelay.Phase05.v1", "Foley", "Impact"),
    ("EnemyDeath", "/Game/Generated/Phase02/Audio/S_Proto_Hurt", "CinderRelay.Phase02.v1", "Foley", "Impact"),
    ("PowerRise", "/Game/Generated/Phase05/Audio/S_CR05_PowerRise", "CinderRelay.Phase05.v1", "Voice", "Voice"),
    ("SignalEnding", "/Game/Generated/Phase05/Audio/S_CR05_SignalEnding", "CinderRelay.Phase05.v1", "Voice", "Voice"),
    ("Calibration", "/Game/Generated/Phase05/Audio/S_CR05_Calibration", "CinderRelay.Phase05.v1", "Foley", "Handling"),
    ("Seat", "/Game/Generated/Phase052/Audio/S_CR052_Seat", "CinderRelay.Phase052.v1", "Foley", "Handling"),
    ("Secure", "/Game/Generated/Phase052/Audio/S_CR052_Secure", "CinderRelay.Phase052.v1", "Foley", "Handling"),
]
replacements = {}
legacy_receipt = []
for name, path, old_owner, category, concurrent in legacy_specs:
    original = assets.load_asset(path)
    assert original and assets.get_metadata_tag(original, "CR.GeneratedBy") == old_owner, path
    target = audio_root + "/S_CR055_Legacy" + name
    derivative = owned(target)
    if not derivative:
        derivative = assets.duplicate_asset(path, target)
        assert derivative
    derivative.set_editor_property("sound_class_object", classes[category])
    derivative.set_editor_property("concurrency_set", {concurrency[concurrent]})
    derivative.set_editor_property("loading_behavior", unreal.SoundWaveLoadingBehavior.FORCE_INLINE)
    if name.startswith("Enemy"):
        derivative.set_editor_property("attenuation_settings", attenuation)
    assets.set_metadata_tag(derivative, "CR.DerivedFrom", path)
    save(derivative)
    replacements[original.get_path_name()] = derivative
    sounds["Legacy" + name] = derivative
    legacy_receipt.append({"source": path, "target": target, "category": category, "original_unchanged": True})

sequences = {}
for name, path, old_owner in (
        ("RelayPower", "/Game/Generated/Phase05/Sequences/LS_CR05_RelayPower", "CinderRelay.Phase05.v1"),
        ("RelayEnding", "/Game/Generated/Phase05/Sequences/LS_CR05_RelayEnding", "CinderRelay.Phase05.v1"),
        ("RookRestoration", "/Game/Generated/Phase053/Assembly/Sequences/LS_CR053_RookRestoration", "CinderRelay.Phase053.Restoration.v1")):
    original = assets.load_asset(path)
    assert original and assets.get_metadata_tag(original, "CR.GeneratedBy") == old_owner, path
    target = root + "/Sequences/LS_CR055_" + name
    seq = owned(target)
    if not seq:
        seq = assets.duplicate_asset(path, target)
        assert seq
    replaced = []
    for binding in seq.get_bindings():
        for track in binding.get_tracks():
            if isinstance(track, unreal.MovieSceneAudioTrack):
                for section in track.get_sections():
                    old = section.get_sound()
                    if old and old.get_path_name() in replacements:
                        section.set_sound(replacements[old.get_path_name()])
                        replaced.append(old.get_path_name())
    assert seq.get_playback_start() == original.get_playback_start()
    assert seq.get_playback_end() == original.get_playback_end()
    assert len(seq.get_bindings()) == len(original.get_bindings())
    assets.set_metadata_tag(seq, "CR.DerivedFrom", path)
    sequences[name] = save(seq)

assert levels.load_level("/Game/Generated/Phase01B/Maps/L_CH01_Persistent")
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
expected = ("CR02_Scout_1", "CR02_Scout_2", "CR03_CalibrationWorkbench", "CR05_RelayPresentation",
            "CR05_Ambience_RailYard", "CR05_Ambience_Workshop", "CR05_Ambience_RelayBunker")
assert all(name in by_label for name in expected), "Required existing native audio owners missing"
changes = []
for label in ("CR02_Scout_1", "CR02_Scout_2"):
    actor = by_label[label]
    actor.modify()
    for prop, sound in (("shot_sound", "LegacyEnemyShot"), ("hit_sound", "LegacyEnemyHit"), ("death_sound", "LegacyEnemyDeath")):
        actor.set_editor_property(prop, sounds[sound])
    changes.append(label + ": audio references only")
for zone, key in (("RailYard", "AmbYard"), ("Workshop", "AmbWorkshop"), ("RelayBunker", "AmbBunker")):
    actor = by_label["CR05_Ambience_" + zone]
    actor.modify()
    actor.audio_component.set_sound(sounds[key])
    # Sources carry deliberate headroom; preserve existing native spatial region.
    actor.audio_component.set_volume_multiplier(.8)
    changes.append(actor.get_actor_label() + ": loop and gain; native attenuation/occlusion unchanged")
bench = by_label["CR03_CalibrationWorkbench"]
bench.modify()
bench.set_editor_property("sequence", sequences["RookRestoration"])
bench.set_editor_property("activation_sound", sounds["LegacyCalibration"])
presentation = by_label["CR05_RelayPresentation"]
presentation.modify()
presentation.set_editor_property("power_sequence", sequences["RelayPower"])
presentation.set_editor_property("ending_sequence", sequences["RelayEnding"])
changes += ["CR03_CalibrationWorkbench: audio-only sequence derivative and activation reference", "CR05_RelayPresentation: audio-only sequence derivatives"]
assert levels.save_all_dirty_levels()
receipt = {"owner": owner, "new_original_waves": len(manifest["sounds"]), "legacy_derivatives": legacy_receipt,
           "classes": {n: a.get_path_name() for n, a in classes.items()}, "mix": mix.get_path_name(),
           "concurrency": {n: a.get_path_name() for n, a in concurrency.items()}, "attenuation": attenuation.get_path_name(),
           "sequences": {n: a.get_path_name() for n, a in sequences.items()}, "actor_changes": changes,
           "DA_Rook5_touched": False, "old_source_assets_touched": False,
           "evidence_boundary": "Real native import and assignment only. Packaged audible playback/quality verification remains separate."}
(evidence / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
unreal.log("CR055_AUDIO_IMPORT_PASS " + json.dumps({"waves": len(manifest["sounds"]), "classes": len(classes), "actors": len(expected)}))
unreal.SystemLibrary.quit_editor()
