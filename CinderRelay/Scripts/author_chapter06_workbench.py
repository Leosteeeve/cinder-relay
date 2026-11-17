"""Author two sequences against the existing workbench, then evaluate camera binding."""
import json
from pathlib import Path

import unreal


project = Path(unreal.Paths.project_dir())
evidence = project.parent / '.environment-local/phase-06/expanded'
root = '/Game/Generated/Phase06/Sequences'
owner = 'CinderRelay.Phase06.Workbench.v1'
assets = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world_path = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
assert levels.load_level(world_path)
bench = next(a for a in actors.get_all_level_actors() if isinstance(a, unreal.CRWorkbench))
assembly_mesh = assets.load_asset('/Game/Generated/Phase053/Assembly/Animation/SK_CR053_Restoration')
skeleton = assembly_mesh.get_editor_property('skeleton')
original = assets.load_asset('/Game/Generated/Phase053/Assembly/Sequences/LS_CR053_RookRestoration')
assert original and skeleton


def owned(path):
    if not assets.does_asset_exist(path):
        return None
    obj = assets.load_asset(path)
    assert assets.get_metadata_tag(obj, 'CR.GeneratedBy') == owner, path
    return obj


def save(obj):
    assets.set_metadata_tag(obj, 'CR.GeneratedBy', owner)
    assert assets.save_loaded_asset(obj)
    return obj


def import_action():
    name = 'AN_CR06_OpticFitting'
    result = owned(root + '/' + name)
    if result:
        return result
    ui = unreal.FbxImportUI()
    ui.automated_import_should_detect_type = False
    ui.import_mesh = False
    ui.import_as_skeletal = True
    ui.import_animations = True
    ui.import_materials = False
    ui.import_textures = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
    ui.skeleton = skeleton
    ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate', True)
    task = unreal.AssetImportTask()
    task.filename = str(evidence / 'animation' / (name + '.fbx'))
    task.destination_path = root
    task.destination_name = name
    task.automated = True
    task.save = False
    task.options = ui
    tools.import_asset_tasks([task])
    candidates = [assets.load_asset(p) for p in task.imported_object_paths]
    assert len(candidates) == 1 and isinstance(candidates[0], unreal.AnimSequence), task.imported_object_paths
    result = candidates[0]
    if result.get_name() != name:
        assert assets.rename_asset(result.get_path_name(), root + '/' + name)
        result = assets.load_asset(root + '/' + name)
    return save(result)


retimed = import_action()
assert retimed.get_editor_property('skeleton') == skeleton and abs(retimed.sequence_length - 22) < .02
timings = json.loads((evidence / 'animation/retime.json').read_text(encoding='utf-8'))


def configure(name, duration, poses, optic):
    path = root + '/' + name
    sequence = owned(path) or assets.duplicate_asset(original.get_path_name(), path)
    sequence.set_playback_start(0)
    sequence.set_playback_end(duration)
    count = {'skeletal': 0, 'camera': 0}
    cues = iter((timings['seat'], timings['secure']))
    for binding in sequence.get_bindings():
        for track in binding.get_tracks():
            if isinstance(track, unreal.MovieSceneSkeletalAnimationTrack):
                for section in track.get_sections():
                    if optic:
                        params = section.get_editor_property('params')
                        params.animation = retimed
                        section.set_editor_property('params', params)
                    section.set_range(0, duration)
                    count['skeletal'] += 1
            elif isinstance(track, unreal.MovieScene3DTransformTrack):
                for section in track.get_sections():
                    section.set_range(0, duration)
                    channels = section.get_all_channels()
                    for channel in channels:
                        for key in channel.get_keys():
                            channel.remove_key(key)
                    for frame, location, rotation in poses:
                        for channel, value in zip(channels, (*location, *rotation, 1, 1, 1)):
                            channel.add_key(unreal.FrameNumber(frame), value, interpolation=unreal.MovieSceneKeyInterpolation.AUTO)
                    count['camera'] += 1
            elif isinstance(track, unreal.MovieSceneAudioTrack):
                if not optic:
                    binding.remove_track(track)
                    continue
                for section in track.get_sections():
                    frame = next(cues)
                    section.set_range(frame, frame + 12)
    assert count == {'skeletal': 1, 'camera': 1}, count
    return save(sequence)


base = (-62, 0, 166)
optic = configure('LS_CR06_OpticFitting', 660, [
    (0, base, (0, -48, 0)), (65, (-60, -4, 165), (0, -48, 4)),
    (126, (-57, -6, 165), (0, -49, 5)), (246, (-55, -4, 164), (0, -50, 3)),
    (372, (-58, -2, 168), (0, -47, 1.5)), (450, (-64, 0, 172), (0, -46, 0)),
    (595, (-67, 0, 173), (0, -44, 0)), (660, base, (0, -48, 0))], True)
iron = configure('LS_CR06_IronService', 96, [
    (0, base, (0, -48, 0)), (20, (-55, 4, 159), (0, -47, -4)),
    (62, (-56, 5, 161), (0, -46, -5)), (96, base, (0, -48, 0))], False)

assert levels.set_current_level_by_name('L_CH01_Workshop')
bench.modify()
bench.set_editor_property('sequence', optic)
assert levels.save_current_level()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def camera_pose():
    p = bench.camera.get_editor_property('relative_location')
    r = bench.camera.get_editor_property('relative_rotation')
    return (p.x, p.y, p.z, r.pitch, r.yaw, r.roll)


def evaluate(sequence, samples):
    initial = camera_pose()
    player, actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, sequence, unreal.MovieSceneSequencePlaybackSettings())
    assert player and actor
    actor.set_binding_by_tag('CR03_Hands', [bench])
    values = []
    for seconds in samples:
        player.play()
        params = unreal.MovieSceneSequencePlaybackParams()
        params.position_type = unreal.MovieScenePositionType.TIME
        params.time = seconds
        params.update_method = unreal.UpdatePositionMethod.JUMP
        player.set_playback_position(params)
        active = camera_pose()
        assert max(abs(a-b) for a, b in zip(active, initial)) > 2, (seconds, active, initial)
        player.stop()
        assert max(abs(a-b) for a, b in zip(camera_pose(), initial)) < .02, (seconds, camera_pose(), initial)
        values.append(dict(seconds=seconds, pose=active))
    actors.destroy_actor(actor)
    return values


samples = {optic.get_name(): evaluate(optic, (4.5, 8., 12.4, 18.)), iron.get_name(): evaluate(iron, (1., 2.))}
(evidence / 'workbench-native.json').write_text(json.dumps(dict(animation=retimed.get_path_name(),
    original_skeleton=skeleton.get_path_name(), duration_seconds=retimed.sequence_length, camera=samples), indent=2))
unreal.log('CR06_EXPANSION_WORKBENCH PASS')
