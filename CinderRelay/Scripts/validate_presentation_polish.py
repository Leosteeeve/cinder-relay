"""Read-only Phase052 asset preservation, native collision and sequence checks."""
import ast,hashlib,json
from collections import Counter
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir()).resolve();baseline=p.parent/'.environment-local/phase-05-2'
human='-cr053human' in unreal.SystemLibrary.get_command_line().lower()
out=p.parent/'.environment-local/phase-05-3' if human else baseline
assets=unreal.EditorAssetLibrary;levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
all_actors=actors.get_all_level_actors();now={a.get_actor_label():a for a in all_actors};assert len(now)==len(all_actors)
before=json.loads((baseline/'before-inventory.json').read_text())['actors']
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
def shape(r):
    r=json.loads(json.dumps(r))
    for k in('level','hidden','bounds'):r.pop(k,None)
    if r['label'] in('CR05_RailCar-800','CR05_RailCar800'):
        for c in r['components']:
            for k in('mesh','materials'):c.pop(k,None)
    return r
for n,r in before.items():
    assert n in now and now[n].get_level().get_outer().get_name()==r['level'],n
    assert shape(scope['snapshot'](now[n]))==shape(r),n
    assert now[n].get_editor_property('hidden')==r['hidden'],n
added=[a for n,a in now.items() if n not in before]
for a in added:
    assert 'CR_Phase052_Generated' in [str(t) for t in a.tags]
    assert a.get_level().get_outer().get_name()!='L_CH01_Persistent'
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component;assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION and not c.get_editor_property('can_ever_affect_navigation'),a.get_actor_label()
hashes=json.loads((baseline/'protected-hashes.json').read_text(encoding='utf-8-sig'))
authorized_source_changes={'CRCharacter.cpp','CRCheckpointRoute.cpp','CRCombatAcceptance.cpp','CRCombatAcceptance.h','CRWeaponViewComponent.cpp','CRWeaponViewComponent.h','CinderRelay.Build.cs'} if human else set()
checked_hashes=0
for r in hashes:
    if r['path'].startswith('CinderRelay/Source/CinderRelay/') and Path(r['path']).name in authorized_source_changes:continue
    f=p.parent/r['path'];assert f.exists() and hashlib.sha256(f.read_bytes()).hexdigest().upper()==r['sha256'],r['path']
    checked_hashes+=1
bench=now['CR03_CalibrationWorkbench']
expected='/Phase053/Assembly/' if human else '/Phase052/'
assert expected in bench.get_editor_property('assembly_mesh').get_path_name()
seq=assets.load_asset(bench.get_editor_property('sequence').get_path_name());assert expected in seq.get_path_name()
assert seq.get_playback_end()==660 and seq.get_display_rate().numerator==30
tracks=[t for b in seq.get_bindings() for t in b.get_tracks()]
assert len([t for t in tracks if isinstance(t,unreal.MovieSceneSkeletalAnimationTrack)])==1
assert len([t for t in tracks if isinstance(t,unreal.MovieScene3DTransformTrack)])==1
assert len([t for t in tracks if isinstance(t,unreal.MovieSceneAudioTrack)])==2
for t in tracks:
    for s in t.get_sections():assert s.get_completion_mode()==unreal.MovieSceneCompletionMode.RESTORE_STATE
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
points={'invalid_prior_camera':(-600,700,165),'train_route':(-650,430,165),'shadow_flank':(-950,1150,165),'workshop_interior':(1950,100,165)}
overlaps={}
for n,loc in points.items():
    found=unreal.SystemLibrary.sphere_overlap_actors(world,unreal.Vector(*loc),18,[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],unreal.Actor,[])
    overlaps[n]=[a.get_actor_label() for a in (found or [])]
assert any('CarBody' in n for n in overlaps['invalid_prior_camera']),overlaps
assert all(not overlaps[n] for n in points if n!='invalid_prior_camera'),overlaps
receipt={'original_actors_preserved':len(before),'added':len(added),'ownership':dict(Counter(a.get_level().get_outer().get_name() for a in added)),
 'protected_files_unchanged':checked_hashes,'authorized_source_exceptions':sorted(authorized_source_changes),'collision_camera_audit':overlaps,'checkpoint_anchors':{n:scope['transform'](a.get_actor_transform()) for n,a in now.items() if isinstance(a,unreal.CRCheckpoint)},
 'sequence':seq.get_path_name(),'sequence_tracks':[t.get_class().get_name() for t in tracks],'runtime_acceptance':False}
(out/('native-asset-validation.json' if human else 'asset-validation.json')).write_text(json.dumps(receipt,indent=2));unreal.log('CR052_ASSET_VALIDATION_PASS '+json.dumps(receipt))
unreal.SystemLibrary.quit_editor()
