"""Import the original station sounds and receiver instrument using the native Editor."""
import hashlib
import json
from pathlib import Path

import unreal

project = Path(unreal.Paths.project_dir()).resolve()
out = project.parent / '.environment-local/phase-06/remake'
exports = out / 'exports'
source = project / 'ArtSource/Audio/Phase06'
root = '/Game/Generated/Phase06'
legacy = '/Game/Generated/Phase055'
owner = 'CinderRelay.Chapter01.Receiver'
world = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
assets = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def load(path):
    obj = assets.load_asset(path)
    assert obj, path
    return obj


def owned(path):
    if not assets.does_asset_exist(path):
        return None
    obj = load(path)
    assert assets.get_metadata_tag(obj, 'CR.GeneratedBy') == owner, path
    return obj


def save(obj):
    assets.set_metadata_tag(obj, 'CR.GeneratedBy', owner)
    assert assets.save_loaded_asset(obj, only_if_is_dirty=False), obj.get_name()
    return obj


def import_file(file, folder, options=None):
    dest = root + '/' + folder
    path = dest + '/' + file.stem
    previous = owned(path)
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    if previous and assets.get_metadata_tag(previous, 'CR.SourceHash') == digest:
        return previous
    task = unreal.AssetImportTask()
    task.filename = str(file)
    task.destination_path = dest
    task.destination_name = file.stem
    task.automated = True
    task.save = False
    task.replace_existing = previous is not None
    if options:
        task.options = options
    tools.import_asset_tasks([task])
    obj = load(path)
    assets.set_metadata_tag(obj, 'CR.SourceHash', digest)
    return obj


sounds = {}
for spec in json.loads((source / 'station-sounds.json').read_text()):
    wave_path = source / spec['file']
    assert hashlib.sha256(wave_path.read_bytes()).hexdigest() == spec['sha256']
    sound = import_file(wave_path, 'Audio')
    is_receiver = spec['event'] in ('RelayWake', 'CarrierLock')
    category = 'Voice' if is_receiver else 'Foley'
    concurrency = 'Voice' if is_receiver else 'Handling'
    sound.set_editor_property('sound_class_object', load(legacy + '/Audio/SC_CR055_' + category))
    sound.set_editor_property('concurrency_set', {load(legacy + '/Audio/CON_CR055_' + concurrency)})
    sound.set_editor_property('loading_behavior', unreal.SoundWaveLoadingBehavior.FORCE_INLINE)
    assert abs(sound.get_editor_property('duration') - spec['seconds']) < .01
    sounds[spec['event']] = save(sound)

options = unreal.FbxImportUI()
options.automated_import_should_detect_type = False
options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
options.import_as_skeletal = options.import_materials = options.import_textures = options.import_animations = False
options.import_mesh = True
options.static_mesh_import_data.combine_meshes = True
options.static_mesh_import_data.auto_generate_collision = False
options.static_mesh_import_data.convert_scene = True
options.static_mesh_import_data.convert_scene_unit = True
meshes = {}
for spec in json.loads((exports / 'receiver.json').read_text()):
    name = spec['name']
    mesh = import_file(exports / (name + '.fbx'), 'Receiver', options)
    slots = list(mesh.get_editor_property('static_materials'))
    for slot in slots:
        k = str(slot.get_editor_property('imported_material_slot_name'))
        assert k.startswith('CR06Meter_'), k
        mat = load('/Game/Generated/Phase052/Materials/MI_CR052_' + k.removeprefix('CR06Meter_'))
        slot.set_editor_property('material_interface', mat)
    mesh.set_editor_property('static_materials', slots)
    bounds = mesh.get_bounds().box_extent * 2
    assert all(abs(a-b) < 1 for a, b in zip((bounds.x, bounds.y, bounds.z), spec['dimensions_cm'])), (name, bounds)
    meshes[name] = save(mesh)

sequences = {}
for name, sound_name in (('RelayPower', 'RelayWake'), ('RelayEnding', 'CarrierLock')):
    destination = root + '/Sequences/LS_CR06_' + name
    original_path = legacy + '/Sequences/LS_CR055_' + name
    sequence = owned(destination) or assets.duplicate_asset(original_path, destination)
    assert sequence
    sections = [s for b in sequence.get_bindings() for track in b.get_tracks()
                if isinstance(track, unreal.MovieSceneAudioTrack) for s in track.get_sections()]
    assert len(sections) == 1, name
    sections[0].set_sound(sounds[sound_name])
    assert sequence.get_playback_end() == load(original_path).get_playback_end()
    sequences[name] = save(sequence)

assert levels.load_level(world)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
assert levels.set_current_level_by_name('L_CH01_RelayBunker')
presentation = scene['CR05_RelayPresentation']
presentation.modify()
dial = presentation.get_editor_property('receiver_dial')
needle = presentation.get_editor_property('receiver_needle')
dial.set_static_mesh(meshes['SM_CR06_ReceiverDial'])
needle.set_static_mesh(meshes['SM_CR06_ReceiverNeedle'])
# The feet rest on the -600 cm bunker floor and its back meets the rear wall.
position = unreal.Vector(7167, 0, -377)
dial.set_world_location(position, False, False)
dial.set_world_rotation(unreal.Rotator(), False, False)
needle.set_relative_rotation(unreal.Rotator(roll=-64), False, False)
for prop, seq in (('power_sequence', 'RelayPower'), ('ending_sequence', 'RelayEnding')):
    presentation.set_editor_property(prop, sequences[seq])
assert levels.save_current_level()
assert levels.load_level(world)
restored = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'CR05_RelayPresentation')
for key, name in (('receiver_dial', 'SM_CR06_ReceiverDial'), ('receiver_needle', 'SM_CR06_ReceiverNeedle')):
    part = restored.get_editor_property(key)
    assert part.get_editor_property('static_mesh').get_name() == name
    assert (part.get_world_location() - position).length() < 1
assert restored.get_editor_property('ending_sequence').get_name() == 'LS_CR06_RelayEnding'
(out / 'receiver-native.json').write_text(json.dumps(dict(sounds=list(sounds), sequences=list(sequences),
    meshes=list(meshes), position_cm=[position.x, position.y, position.z]), indent=2))
unreal.log('CR06_RECEIVER PASS')
