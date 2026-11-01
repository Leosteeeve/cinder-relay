"""Evaluate the real native sequence and verify camera restoration; never save maps.

This bounded Editor check complements packaged gameplay lifecycle acceptance.
It checks component binding/evaluation, not human motion quality or runtime input.
"""
import json
from pathlib import Path
import unreal

human='-cr053human' in unreal.SystemLibrary.get_command_line().lower()
out=Path(unreal.Paths.project_dir()).resolve().parent/('.environment-local/phase-05-3' if human else '.environment-local/phase-05-2')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.CRWorkbench))
sequence=unreal.EditorAssetLibrary.load_asset('/Game/Generated/Phase053/Assembly/Sequences/LS_CR053_RookRestoration' if human else '/Game/Generated/Phase052/Sequences/LS_CR052_RookRestoration')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
player,actor=unreal.LevelSequencePlayer.create_level_sequence_player(world,sequence,unreal.MovieSceneSequencePlaybackSettings())
assert player and actor
actor.set_binding_by_tag('CR03_Hands',[bench])

def camera():
    p=bench.camera.get_editor_property('relative_location')
    r=bench.camera.get_editor_property('relative_rotation')
    return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll]

initial=camera();samples=[]
for seconds in (6.0,19.2):
    player.play()
    params=unreal.MovieSceneSequencePlaybackParams()
    params.position_type=unreal.MovieScenePositionType.TIME
    params.time=seconds
    params.update_method=unreal.UpdatePositionMethod.JUMP
    player.set_playback_position(params)
    active=camera()
    assert max(abs(a-b) for a,b in zip(active,initial))>2,('Camera binding did not evaluate',active)
    player.stop()
    restored=camera()
    assert max(abs(a-b) for a,b in zip(restored,initial))<.01,('Camera did not restore',restored)
    samples.append({'seconds':seconds,'evaluated':active,'after_stop':restored})
actors.destroy_actor(actor)
(out/'contact-track-validation.json').write_text(json.dumps({'initial':initial,'samples':samples,'passed':True,'scope':'Native Editor sequence evaluation; packaged input/lifecycle tested separately'},indent=2))
unreal.log('CR052_TRACK_VALIDATION_PASS')
unreal.SystemLibrary.quit_editor()
