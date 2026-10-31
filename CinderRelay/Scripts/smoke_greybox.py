"""One bounded Editor PIE smoke through real CharacterMovement and Enhanced Input.

No teleport, objective setters, or test-only runtime classes. Camera aims are
scripted and action values injected: this is not a human feel/physical-key test.
Run with -ExecutePythonScript in a rendering Editor, never a NullRHI commandlet.
"""
import json
import math
import time
import traceback
from pathlib import Path
import unreal

MAP = '/Game/Generated/Phase01A/Maps/L_CH01_Greybox'
OUT = Path(unreal.Paths.project_saved_dir()).resolve() / 'Phase01A'
OUT.mkdir(parents=True, exist_ok=True)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
performance_settings = unreal.get_default_object(unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
# This editor settings class has no generated Python alias table; use its exact
# reflected C++ property name (EditorPerformanceSettings.h / FindEditorPropertyImpl).
original_background_throttle = performance_settings.get_editor_property('bThrottleCPUWhenNotForeground')
# Session-only, restored by finish; never SaveConfig or change the user's preferences file.
performance_settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
if not editor.get_game_world():
    assert levels.load_level(MAP)
    levels.editor_request_begin_play()


class Smoke:
    def __init__(self):
        self.started = time.monotonic()
        self.stage_started = self.started
        self.stage = 'wait_pie'
        self.stage_ticks = 0
        self.records = []
        self.samples = []
        self.last_sample = 0
        self.callback = None
        self.waypoints = []
        self.after_walk = ''
        self.actor = None
        self.world = None
        self.paused_location = None
        self.jump_peak = -1e9
        self.in_tick = False

    def record(self, name, **fields):
        item = {'check': name, 'elapsed_s': round(time.monotonic()-self.started, 2), **fields}
        self.records.append(item)
        unreal.log('CR_SMOKE ' + json.dumps(item))

    def advance(self, stage):
        self.stage = stage
        self.stage_ticks = 0
        self.stage_started = time.monotonic()
        self.stage_started_game = unreal.GameplayStatics.get_time_seconds(self.world) if self.world else 0

    def inject(self, prop, value=1.0):
        action = self.actor.get_editor_property(prop)
        assert action, 'Missing input action: ' + prop
        self.inputs.inject_input_vector_for_action(action, unreal.Vector(value, 0, 0), [], [])

    def bind_world(self):
        self.world = editor.get_game_world()
        if not self.world:
            return False
        self.pc = unreal.GameplayStatics.get_player_controller(self.world, 0)
        self.actor = unreal.GameplayStatics.get_player_character(self.world, 0)
        if not self.pc or not isinstance(self.actor, unreal.CRCharacter):
            return False
        self.mode = unreal.GameplayStatics.get_game_mode(self.world)
        # The BlueprintInternalUseOnly subsystem getter is not exported to Python.
        # A class-filtered native ObjectIterator is used once at session/restart setup,
        # never as gameplay polling. Require a unique live local-player instance.
        candidates = [s for s in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem)
                      if isinstance(s.get_outer(), unreal.LocalPlayer)]
        assert len(candidates) == 1, 'Expected one live local-player input subsystem, got ' + str(len(candidates))
        self.inputs = candidates[0]
        self.movement = self.actor.get_component_by_class(unreal.CharacterMovementComponent)
        self.capsule = self.actor.get_component_by_class(unreal.CapsuleComponent)
        self.objects = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(self.world, unreal.CRInteractionActor)}
        return True

    def shot(self, name):
        # Native viewport capture only; no fabricated renders. CUA is used separately for UMG inspection.
        unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, str(OUT / (name + '.png')))

    def aim(self, target):
        camera = self.actor.get_component_by_class(unreal.CameraComponent)
        rotation = unreal.MathLibrary.find_look_at_rotation(camera.get_world_location(), target)
        self.pc.set_control_rotation(rotation)

    def walk(self, waypoints, next_stage):
        self.waypoints = list(waypoints)
        self.after_walk = next_stage
        self.advance('walk')

    def finish(self, passed, error=None):
        performance_settings.set_editor_property('bThrottleCPUWhenNotForeground', original_background_throttle)
        receipt = {'passed': passed, 'stage': self.stage, 'error': error, 'checks': self.records,
                   'positions_cm': self.samples, 'input_method': 'Enhanced Input action injection; camera steering scripted',
                   'teleports': 0, 'manual_feel_acceptance': False, 'packaged_validation': False}
        (OUT / 'smoke.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        if self.callback is not None:
            unreal.unregister_slate_post_tick_callback(self.callback)
            self.callback = None
        if passed:
            unreal.log('CR_SMOKE_PASS')
        else:
            unreal.log_error('CR_SMOKE_FAIL ' + str(error))
        # Keep the genuine Editor viewport open for inspection; no automatic retries.

    def tick(self, delta):
        # Native screenshot capture can pump Slate while this callback is active.
        if self.in_tick:
            return
        self.in_tick = True
        try:
            self.step()
        except Exception:
            self.finish(False, traceback.format_exc())
        finally:
            self.in_tick = False

    def step(self):
        now = time.monotonic()
        self.stage_ticks += 1
        # Action checks must age in game time: the first background Editor frame
        # can arrive seconds later, before an injected action has been processed.
        age = (now-self.stage_started if self.stage in ['wait_pie', 'paused', 'ending', 'ending_capture', 'restart_wait']
               else unreal.GameplayStatics.get_time_seconds(self.world)-self.stage_started_game)
        assert now-self.started < 240, 'Smoke exceeded its 240-second bound'
        if self.stage == 'wait_pie':
            if self.bind_world():
                self.record('PIE pawn and input subsystem ready')
                assert self.mode.get_objective() == unreal.CRObjective.REACH_WORKSHOP
                # Actual interface rejects premature and distant invocation.
                self.objects['CR_RelayTerminal'].interact(self.actor)
                assert not self.objects['CR_RelayTerminal'].get_editor_property('used')
                self.actor.try_interact()
                assert self.mode.get_objective() == unreal.CRObjective.REACH_WORKSHOP
                self.record('early and out-of-range interaction rejected')
                self.initial_yaw = self.pc.get_control_rotation().yaw
                self.advance('look')
            return
        if self.stage != 'restart_wait' and now-self.last_sample >= .25:
            pos = self.actor.get_actor_location()
            self.samples.append([round(now-self.started, 2), round(pos.x, 1), round(pos.y, 1), round(pos.z, 1)])
            self.last_sample = now
            assert pos.z > -800, 'Player fell below intended floors'
        if self.stage == 'look':
            if age < .35 or self.stage_ticks < 4:
                self.inject('yaw_action', 3)
            else:
                assert abs(self.pc.get_control_rotation().yaw-self.initial_yaw) > .1
                self.record('look action changed yaw')
                self.pc.set_control_rotation(unreal.Rotator(pitch=0, yaw=0, roll=0))
                self.advance('crouch')
        elif self.stage == 'crouch':
            self.inject('crouch_action')
            if age > .5 and self.stage_ticks >= 4:
                assert self.capsule.get_scaled_capsule_half_height() <= 61
                self.record('crouch shrank native capsule')
                self.advance('uncrouch')
        elif self.stage == 'uncrouch':
            if age > .5 and self.stage_ticks >= 4:
                assert self.capsule.get_scaled_capsule_half_height() >= 95
                self.jump_start = self.actor.get_actor_location().z
                self.inject('jump_action')
                self.advance('jump')
        elif self.stage == 'jump':
            self.jump_peak = max(self.jump_peak, self.actor.get_actor_location().z)
            if age > 1.3:
                assert self.jump_peak > self.jump_start + 25
                self.record('jump rose and returned', rise_cm=round(self.jump_peak-self.jump_start, 1))
                self.inject('sprint_action')
                self.advance('pause')
        elif self.stage == 'pause':
            if age < .15 or self.stage_ticks < 4:
                self.inject('sprint_action')
            else:
                assert self.movement.max_walk_speed == self.actor.sprint_speed
                self.pc.toggle_prototype_pause()
                assert unreal.GameplayStatics.is_game_paused(self.world)
                assert self.pc.show_mouse_cursor
                self.paused_location = self.actor.get_actor_location()
                self.advance('paused')
        elif self.stage == 'paused':
            if age > 1:
                assert (self.actor.get_actor_location()-self.paused_location).length() < .1
                self.pc.resume_prototype()
                assert not unreal.GameplayStatics.is_game_paused(self.world)
                assert self.movement.max_walk_speed == self.actor.walk_speed
                self.record('pause released cursor and reset held sprint; resume unpaused')
                self.advance('wall')
        elif self.stage == 'wall':
            self.inject('back_action')
            if age > 2.5:
                pos = self.actor.get_actor_location()
                assert -1945 < pos.x < -1900, 'Back wall collision or movement failed'
                self.record('native movement blocked by yard boundary', x=pos.x)
                self.pc.set_control_rotation(unreal.Rotator(pitch=0, yaw=0, roll=0))
                self.shot('yard')
                self.walk([(1800, 0), (2500, 0), (2800, -170)], 'module_aim')
        elif self.stage == 'walk':
            assert age < 75, 'Movement route timed out (collision/path blocker)'
            x, y = self.waypoints[0]
            pos = self.actor.get_actor_location()
            dx, dy = x-pos.x, y-pos.y
            if math.hypot(dx, dy) < 35:
                self.waypoints.pop(0)
                if not self.waypoints:
                    self.advance(self.after_walk)
                return
            self.pc.set_control_rotation(unreal.Rotator(pitch=0, yaw=math.degrees(math.atan2(dy, dx)), roll=0))
            self.inject('forward_action')
        elif self.stage == 'module_aim':
            assert self.mode.get_objective() == unreal.CRObjective.FIND_MODULE
            self.aim(self.objects['CR_PowerModule'].get_actor_location())
            if age > .4 and self.stage_ticks >= 4:
                assert self.actor.can_interact_with(self.objects['CR_PowerModule'])
                assert '[E]' in str(self.actor.get_current_prompt())
                self.shot('workshop_module')
                self.inject('interact_action')
                self.advance('module_taken')
        elif self.stage == 'module_taken':
            if age > .4 and self.stage_ticks >= 4:
                assert self.mode.get_objective() == unreal.CRObjective.RESTORE_POWER
                self.objects['CR_PowerModule'].interact(self.actor)
                assert self.mode.get_objective() == unreal.CRObjective.RESTORE_POWER
                self.record('workshop arrival, module prompt, E action, duplicate rejection')
                self.walk([(3300, 0), (3550, 0), (5450, 0), (6000, -320)], 'relay_aim')
        elif self.stage == 'relay_aim':
            assert -510 < self.actor.get_actor_location().z < -495
            self.aim(self.objects['CR_RelayTerminal'].get_actor_location())
            if age > .4 and self.stage_ticks >= 4:
                assert self.actor.can_interact_with(self.objects['CR_RelayTerminal'])
                self.shot('relay_terminal')
                self.inject('interact_action')
                self.advance('relay_powered')
        elif self.stage == 'relay_powered':
            if age > .4 and self.stage_ticks >= 4:
                assert self.mode.get_objective() == unreal.CRObjective.INVESTIGATE_SIGNAL
                self.record('walked ramp without teleport and powered relay', z=self.actor.get_actor_location().z)
                self.walk([(6500, -250), (6700, 0)], 'signal_aim')
        elif self.stage == 'signal_aim':
            self.aim(self.objects['CR_SignalConsole'].get_actor_location())
            if age > .4 and self.stage_ticks >= 4:
                assert self.actor.can_interact_with(self.objects['CR_SignalConsole'])
                self.inject('interact_action')
                self.advance('ending')
        elif self.stage == 'ending':
            if age > 2:
                assert self.mode.get_objective() == unreal.CRObjective.COMPLETE
                assert self.pc.get_editor_property('prototype_ended')
                assert unreal.GameplayStatics.is_game_paused(self.world)
                self.record('ending objective and paused menu reached')
                self.shot('ending')
                self.advance('ending_capture')
        elif self.stage == 'ending_capture':
            if age > 20:
                self.pc.restart_prototype()
                self.advance('restart_wait')
        elif self.stage == 'restart_wait':
            if age > 2 and self.bind_world():
                assert self.mode.get_objective() == unreal.CRObjective.REACH_WORKSHOP
                assert not unreal.GameplayStatics.is_game_paused(self.world)
                self.restart_x = self.actor.get_actor_location().x
                self.advance('restart_move')
        elif self.stage == 'restart_move':
            self.inject('forward_action')
            if age > .7:
                assert self.actor.get_actor_location().x > self.restart_x + 80
                self.record('restart reset objectives and accepted movement input')
                self.finish(True)


smoke = Smoke()
smoke.callback = unreal.register_slate_post_tick_callback(smoke.tick)
