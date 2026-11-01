"""Genuine Editor-rendered anatomical samples; not gameplay or weapon-animation acceptance."""
import json
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
import unreal

project = Path(unreal.Paths.project_dir())
run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
out = project.parent / '.environment-local/phase-05-3/arms-review-neutral/runs' / run_id
# A prior PNG must never satisfy a new request's success check.
out.mkdir(parents=True, exist_ok=False)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not globals().get('CR053_MAP_ALREADY_OPEN', False):
    assert levels.load_level('/Game/Generated/Phase053/Review/Maps/L_CR053_ArmsReview')
hands = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'CR053_AnatomyCandidate')
component = hands.skeletal_mesh_component
animation = unreal.EditorAssetLibrary.load_asset('/Game/Generated/Phase053/Review/Animation/AN_CR053_AnatomyReview')
component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
component.set_animation(animation)
component.set_update_animation_in_editor(True)
component.set_component_tick_enabled(True)
component.play(False)
component.set_play_rate(0)
camera = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'CR053_ReviewCamera')
settings = unreal.get_default_object(unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
throttle = settings.get_editor_property('bThrottleCPUWhenNotForeground')
settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
actors.clear_actor_selection_set()

# Relative to the mesh actor; framed from actual imported wrist/finger landmarks.
samples = [
    ('01-overview-relaxed', .5, (135, -100, 35), (-10, 0, -35), 55),
    ('02-right-palm-open', 0, (33, -10, -42), (5, -47, -50), 37),
    ('03-right-dorsal', .5, (40, -95, -37), (5, -47, -50), 37),
    ('04-right-curl', 1, (33, -10, -42), (5, -47, -50), 37),
    ('05-thumb-opposition', 1.5, (42, -25, -50), (5, -47, -50), 35),
    ('06-left-curl', 1, (33, 10, -42), (5, 47, -50), 37),
    ('07-wrist-countertwist', 2, (60, -90, -10), (-3, -43, -44), 44),
    ('08-grasp-shape', 2.5, (33, -10, -42), (5, -47, -50), 37),
    ('09-release', 3, (40, -95, -37), (5, -47, -50), 37),
]
index = 0
task = None
handle = None
receipt = []
started = time.monotonic()
changed = started


def setup():
    global changed
    _, seconds, pos, target, fov = samples[index]
    component.set_position(seconds, False)
    base = hands.get_actor_location()
    camera.set_actor_location(base + unreal.Vector(*pos), False, False)
    camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(base + unreal.Vector(*pos), base + unreal.Vector(*target)), False)
    camera.camera_component.set_field_of_view(fov)
    changed = time.monotonic()


def finish(error=None):
    settings.set_editor_property('bThrottleCPUWhenNotForeground', throttle)
    unreal.unregister_slate_post_tick_callback(handle)
    (out / 'review.json').write_text(json.dumps({'frames': receipt, 'error': error, 'continuous_playback_review': False, 'gameplay_integrated': False}, indent=2), encoding='utf-8')
    unreal.log('CR053_ARMS_REVIEW ' + str(error or 'PASS') + ' evidence=' + str(out))
    unreal.SystemLibrary.quit_editor()


def tick(delta):
    global index, task
    try:
        if time.monotonic() - started > 200:
            raise RuntimeError('Bounded anatomical review timeout')
        if task and task.is_task_done():
            name, seconds, _, _, fov = samples[index]
            file = out / (name + '.png')
            assert file.exists() and file.stat().st_size > 10000
            receipt.append({'name': name, 'seconds': seconds, 'path': str(file), 'camera': str(camera.get_actor_transform()), 'fov': fov,
                            'bones_cm': {str(component.get_bone_name(i)): str(component.get_socket_transform(component.get_bone_name(i))) for i in range(component.get_num_bones()) if str(component.get_bone_name(i)).startswith(('wrist', 'finger1', 'finger2'))}})
            index += 1
            task = None
            if index == len(samples):
                finish()
                return
            setup()
        elif not task and time.monotonic() - changed > 5:
            task = unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, str(out / (samples[index][0] + '.png')), camera=camera, force_game_view=True)
    except Exception:
        finish(traceback.format_exc())


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
setup()
handle = unreal.register_slate_post_tick_callback(tick)
