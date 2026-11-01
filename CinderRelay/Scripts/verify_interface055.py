"""Read-only UE5.8 native asset audit after Phase055 imports.

Loads objects/maps, reads native properties and writes only ignored local evidence.
Never modifies, compiles, creates, duplicates or saves Unreal assets. Run this in
a fresh Editor process. A receipt is written even when one audit section fails.
Asset validity is not packaged gameplay, visual, auditory or performance acceptance.
"""
import hashlib
import json
import re
import traceback
from pathlib import Path
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
OUT = PROJECT.parent / '.environment-local' / 'phase-05-5' / 'native-interface-verification.json'
ROOT = '/Game/Generated/Phase055'
UI = ROOT + '/Interface'
AUDIO = ROOT + '/Audio'
ASSETS = unreal.EditorAssetLibrary
REGISTRY = unreal.AssetRegistryHelpers.get_asset_registry()
REPORT = {'scope': 'Read-only native Editor asset inspection', 'checks': [], 'failures': [],
          'runtime_acceptance': False, 'human_visual_acceptance': False,
          'human_auditory_acceptance': False, 'performance_acceptance': False,
          'protected_binary_hash_comparison': 'Separate root verification; not claimed by this script'}


def path(obj):
    return obj.get_path_name() if obj else None


def package(obj):
    return path(obj).split('.')[0] if obj else None


def check(condition, message):
    REPORT['checks'].append({'passed': bool(condition), 'message': message})
    if not condition:
        REPORT['failures'].append(message)


def require_asset(name, kind=None):
    obj = ASSETS.load_asset(name)
    if not obj or (kind and not isinstance(obj, kind)):
        raise AssertionError('Missing/wrong native asset: ' + name)
    return obj


def near(actual, expected, tolerance=.0001):
    return abs(float(actual) - expected) <= tolerance


def hard_dependencies(obj):
    options = unreal.AssetRegistryDependencyOptions()
    for name, value in (
        ('include_soft_package_references', False), ('include_hard_package_references', True),
        ('include_searchable_names', False), ('include_soft_management_references', False),
        ('include_hard_management_references', False),
    ):
        options.set_editor_property(name, value)
    return sorted(str(n) for n in REGISTRY.get_dependencies(package(obj), options))


def audit_section(name, callback):
    try:
        REPORT[name] = callback()
    except Exception as error:
        REPORT['failures'].append(name + ': ' + str(error))
        REPORT[name] = {'exception': str(error), 'traceback': traceback.format_exc()}


def interface():
    bp = require_asset(UI + '/Widgets/WBP_CR_HUDRoot', unreal.WidgetBlueprint)
    check(ASSETS.get_metadata_tag(bp, 'CR.GeneratedBy') == 'CinderRelay.Phase055.Interface.v1', 'Interface Blueprint ownership')
    generated = bp.generated_class()
    if not generated:
        raise AssertionError('WBP has no generated class')
    cdo = unreal.get_default_object(generated)
    check(isinstance(cdo, unreal.CRHUDWidget), 'Generated WBP inherits the original native HUD authority')
    fonts = {name: require_asset(UI + '/Fonts/F_CR055_' + name, unreal.Font) for name in ('Body', 'Title')}
    faces = {name: require_asset(UI + '/Fonts/FF_CR055_' + name, unreal.FontFace) for name in ('Body', 'Title')}
    font_details = {}
    for name, font in fonts.items():
        dependencies = hard_dependencies(font)
        check(package(faces[name]) in dependencies, name + ' composite font really references its imported FontFace')
        check(font.get_editor_property('font_cache_type') == unreal.FontCacheType.RUNTIME, name + ' uses runtime font cache')
        check(faces[name].get_editor_property('loading_policy') == unreal.FontLoadingPolicy.INLINE, name + ' font data is inline')
        check(path(cdo.get_editor_property(name.lower() + '_font')) == path(font), name + ' CDO font matches authored font')
        font_details[name] = {'font': path(font), 'face': path(faces[name]), 'hard_dependencies': dependencies}
    font_source = PROJECT / 'ArtSource/Interface/Phase055/Fonts'
    check((font_source / 'OFL.txt').is_file(), 'Barlow OFL source license retained')

    required = {
        'HUDRoot': unreal.CanvasPanel, 'GameplayLayer': unreal.CanvasPanel,
        'ObjectivePanel': unreal.Border, 'ObjectiveLabel': unreal.TextBlock, 'Objective': unreal.TextBlock,
        'Prompt': unreal.TextBlock, 'StreamingStatus': unreal.TextBlock, 'CheckpointStatus': unreal.TextBlock,
        'EventNotice': unreal.TextBlock, 'HealthBar': unreal.ProgressBar, 'HealthValue': unreal.TextBlock,
        'HealthState': unreal.TextBlock, 'WeaponLabel': unreal.TextBlock, 'Magazine': unreal.TextBlock,
        'Reserve': unreal.TextBlock, 'ReloadState': unreal.TextBlock, 'OpticState': unreal.TextBlock,
        'Reticle': unreal.TextBlock, 'ConfirmedHit': unreal.TextBlock, 'DamageTint': unreal.Border,
        'SubtitlePanel': unreal.Border, 'Subtitle': unreal.TextBlock, 'AssemblyHelp': unreal.TextBlock,
        'MenuBackdrop': unreal.CanvasPanel, 'TitleBackground': unreal.Image, 'RelayMark': unreal.Image,
        'MenuTitle': unreal.TextBlock, 'MenuBody': unreal.TextBlock, 'SaveAvailability': unreal.TextBlock,
        'Resume': unreal.Button, 'Continue': unreal.Button, 'Restart': unreal.Button,
        'Settings': unreal.Button, 'Credits': unreal.Button, 'Exit': unreal.Button,
        'ModalPanel': unreal.Border, 'ModalTitle': unreal.TextBlock, 'ModalBody': unreal.TextBlock,
        'ModalChoices': unreal.VerticalBox, 'PackPanel': unreal.Border,
        'PackCategories': unreal.VerticalBox, 'PackItems': unreal.VerticalBox,
        'PackDetailTitle': unreal.TextBlock, 'PackDetailState': unreal.TextBlock,
        'PackDetailBody': unreal.TextBlock, 'PackIcon': unreal.Image,
        'PackFooter': unreal.TextBlock, 'PackClose': unreal.Button,
    }
    names = {str(n) for n in unreal.CRInterfaceLibrary.get_designer_widget_names(bp)}
    check(set(required) <= names, 'All functional Designer widget names exist, including EventNotice')
    tree = unreal.find_object(bp, 'WidgetTree')
    if not tree:
        tree = unreal.find_object(None, path(bp) + ':WidgetTree')
    if not tree:
        raise AssertionError('Designer WidgetTree object not discoverable; name-only validation is insufficient')
    widgets = {}
    for name, kind in required.items():
        widget = unreal.find_object(tree, name)
        check(widget is not None and isinstance(widget, kind), name + ' is the required real widget type')
        if not widget:
            continue
        row = {'class': widget.get_class().get_name(), 'path': path(widget)}
        if isinstance(widget, unreal.TextBlock):
            info = widget.get_editor_property('font')
            row.update({'font': path(info.get_editor_property('font_object')),
                        'size': float(info.get_editor_property('size')),
                        'text': str(widget.get_editor_property('text'))})
            check(row['font'] in (path(fonts['Body']), path(fonts['Title'])), name + ' uses the licensed interface family')
        if name == 'TitleBackground':
            brush = widget.get_editor_property('brush')
            resource = brush.get_editor_property('resource_object')
            row['authored_brush_resource'] = path(resource)
            check(resource is None, 'Title artwork has no hard widget brush reference')
        widgets[name] = row
    check(widgets.get('MenuTitle', {}).get('font') == path(fonts['Title']), 'Title typography uses the independently editable title font')
    deps = hard_dependencies(bp)
    check(not any(p.startswith(UI + '/Textures/') for p in deps), 'HUD Blueprint has no hard title/icon texture package references')
    for name in ('MenuBackground', 'RelayMark', 'GameIcon', 'IconRook', 'IconOptic', 'IconAmmo', 'IconPowerModule'):
        texture = require_asset(UI + '/Textures/T_CR055_' + name, unreal.Texture2D)
        check(texture.get_editor_property('compression_settings') == unreal.TextureCompressionSettings.TC_DEFAULT, name + ' uses compressed runtime texture storage')
        check(texture.get_editor_property('max_texture_size') <= (2048 if name == 'MenuBackground' else 512), name + ' runtime size limit')
    return {'blueprint': path(bp), 'generated_class': path(generated), 'fonts': font_details,
            'widgets': widgets, 'designer_names': sorted(names), 'hard_dependencies': deps}


PARENTS = {'SFX': 'Master', 'Weapons': 'SFX', 'Foley': 'SFX', 'Ambience': 'Master',
           'UI': 'Master', 'Voice': 'Master', 'Music': 'Master'}
LIMITS = {'Shot': (3, 0), 'Handling': (4, 0), 'Foot': (2, .08), 'Slide': (1, 0),
          'UI': (3, .025), 'Impact': (6, 0), 'Ambience': (3, 0), 'Voice': (2, 0)}
LEGACY = {
    'EnemyShot': ('/Game/Generated/Phase05/Audio/S_CR05_RookShot', 'Weapons', 'Shot'),
    'EnemyHit': ('/Game/Generated/Phase05/Audio/S_CR05_Impact', 'Foley', 'Impact'),
    'EnemyDeath': ('/Game/Generated/Phase02/Audio/S_Proto_Hurt', 'Foley', 'Impact'),
    'PowerRise': ('/Game/Generated/Phase05/Audio/S_CR05_PowerRise', 'Voice', 'Voice'),
    'SignalEnding': ('/Game/Generated/Phase05/Audio/S_CR05_SignalEnding', 'Voice', 'Voice'),
    'Calibration': ('/Game/Generated/Phase05/Audio/S_CR05_Calibration', 'Foley', 'Handling'),
    'Seat': ('/Game/Generated/Phase052/Audio/S_CR052_Seat', 'Foley', 'Handling'),
    'Secure': ('/Game/Generated/Phase052/Audio/S_CR052_Secure', 'Foley', 'Handling'),
}
SEQUENCES = {
    'RelayPower': '/Game/Generated/Phase05/Sequences/LS_CR05_RelayPower',
    'RelayEnding': '/Game/Generated/Phase05/Sequences/LS_CR05_RelayEnding',
    'RookRestoration': '/Game/Generated/Phase053/Assembly/Sequences/LS_CR053_RookRestoration',
}


def concurrency_name(name, category):
    if name.startswith('S_CR055_Rook'):
        return 'Shot'
    if 'Foot' in name:
        return 'Foot'
    if name.endswith('SlideLoop'):
        return 'Slide'
    if category in ('UI', 'Ambience', 'Voice'):
        return category
    if name.endswith('Impact') or name.endswith('Damage'):
        return 'Impact'
    return 'Handling'


def sound_properties(sound, category, concurrency):
    check(package(sound.get_editor_property('sound_class_object')) == AUDIO + '/SC_CR055_' + category, sound.get_name() + ' class assignment')
    check({package(c) for c in sound.get_editor_property('concurrency_set')} == {AUDIO + '/CON_CR055_' + concurrency}, sound.get_name() + ' concurrency assignment')


def audio():
    manifest_path = PROJECT / 'ArtSource/Audio/Phase055/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    check(len(manifest['sounds']) == 44, 'Manifest has the intended 44 original sounds')
    check(manifest['original_samples_only'] and not manifest['external_samples'], 'Sound manifest declares original synthesis only')
    classes = {name: require_asset(AUDIO + '/SC_CR055_' + name, unreal.SoundClass) for name in ('Master', *PARENTS)}
    class_rows = {}
    for name, obj in classes.items():
        parent = package(obj.get_editor_property('parent_class'))
        children = sorted(package(c) for c in obj.get_editor_property('child_classes'))
        check(parent == (AUDIO + '/SC_CR055_' + PARENTS[name] if name in PARENTS else None), name + ' parent sound class')
        check(children == sorted(AUDIO + '/SC_CR055_' + n for n, p in PARENTS.items() if p == name), name + ' child classes')
        class_rows[name] = {'parent': parent, 'children': children}
    for name, (count, retrigger) in LIMITS.items():
        obj = require_asset(AUDIO + '/CON_CR055_' + name, unreal.SoundConcurrency)
        settings = obj.get_editor_property('concurrency')
        check(settings.get_editor_property('max_count') == count, name + ' concurrency bound')
        check(near(settings.get_editor_property('retrigger_time'), retrigger), name + ' retrigger guard')
        check(settings.get_editor_property('resolution_rule') == unreal.MaxConcurrentResolutionRule.STOP_OLDEST, name + ' bounded voice replacement')
        check(near(settings.get_editor_property('voice_steal_release_time'), .035), name + ' short voice release')
    attenuation = require_asset(AUDIO + '/ATT_CR055_Spatial', unreal.SoundAttenuation)
    settings = attenuation.get_editor_property('attenuation')
    for name in ('attenuate', 'spatialize', 'enable_occlusion'):
        check(settings.get_editor_property(name), 'Native spatial attenuation: ' + name)
    check(near(settings.get_editor_property('falloff_distance'), 2400), 'Spatial falloff distance')
    check(near(settings.get_editor_property('occlusion_volume_attenuation'), .4), 'Occlusion gain')
    mix = require_asset(AUDIO + '/SMX_CR055_Settings', unreal.SoundMix)
    check(near(mix.get_editor_property('duration'), -1), 'Settings SoundMix persists until replaced')
    waves = []
    for spec in manifest['sounds']:
        obj = require_asset(AUDIO + '/' + spec['name'], unreal.SoundWave)
        original = PROJECT / 'ArtSource/Audio/Phase055' / spec['file']
        check(hashlib.sha256(original.read_bytes()).hexdigest() == spec['sha256'], spec['name'] + ' source hash')
        check(ASSETS.get_metadata_tag(obj, 'CR.GeneratedBy') == 'CinderRelay.Phase055.Audio.v1', spec['name'] + ' ownership')
        check(ASSETS.get_metadata_tag(obj, 'CR.SourceHash') == spec['sha256'], spec['name'] + ' native source provenance hash')
        check(ASSETS.get_metadata_tag(obj, 'CR.SourceLicense') == spec['license'], spec['name'] + ' native license metadata')
        check(obj.get_editor_property('looping') == spec['loop'], spec['name'] + ' loop state')
        expected_loading = unreal.SoundWaveLoadingBehavior.RETAIN_ON_LOAD if spec['loop'] else unreal.SoundWaveLoadingBehavior.FORCE_INLINE
        check(obj.get_editor_property('loading_behavior') == expected_loading, spec['name'] + ' load policy')
        sound_properties(obj, spec['sound_class'], concurrency_name(spec['name'], spec['sound_class']))
        waves.append({'path': path(obj), 'source_hash': spec['sha256'], 'class': spec['sound_class'], 'loop': spec['loop']})
    derivatives = []
    for name, (original, category, concurrent) in LEGACY.items():
        obj = require_asset(AUDIO + '/S_CR055_Legacy' + name, unreal.SoundWave)
        check(ASSETS.get_metadata_tag(obj, 'CR.DerivedFrom') == original, name + ' explicit original derivative provenance')
        sound_properties(obj, category, concurrent)
        if name.startswith('Enemy'):
            check(path(obj.get_editor_property('attenuation_settings')) == path(attenuation), name + ' distance attenuation')
        derivatives.append(path(obj))
    registry_waves = []
    for name in ASSETS.list_assets(AUDIO, recursive=True, include_folder=False):
        obj = ASSETS.load_asset(name)
        if isinstance(obj, unreal.SoundWave):
            registry_waves.append(path(obj))
    check(len(registry_waves) == 52, 'Exactly 44 original plus 8 explicit legacy SoundWave derivatives')
    return {'original_count': len(waves), 'originals': waves, 'legacy_derivatives': derivatives,
            'registry_wave_count': len(registry_waves), 'classes': class_rows,
            'concurrency_limits': LIMITS, 'attenuation': path(attenuation), 'mix': path(mix)}


def guid_value(guid):
    # KismetGuidLibrary.h exposes Conv_GuidToString with ScriptMethod="ToString".
    # str(Guid) is only Python's struct representation and includes a heap address.
    value = guid.to_string()
    if not re.fullmatch(r'[0-9A-Fa-f-]{32,36}', value):
        raise AssertionError('Native Guid.ToString did not return a GUID value: ' + value)
    return value.upper()


def numeric_channel_shape(channel):
    """Read the authored curve, including interpolation/defaults, without editing it."""
    keys = []
    for key in channel.get_keys():
        time = key.get_time(unreal.MovieSceneTimeUnit.TICK_RESOLUTION)
        keys.append({
            'tick': int(time.frame_number.value), 'sub_frame': float(time.sub_frame),
            'value': float(key.get_value()),
            'interpolation': str(key.get_interpolation_mode()),
            'tangent_mode': str(key.get_tangent_mode()),
            'arrive_tangent': float(key.get_arrive_tangent()),
            'leave_tangent': float(key.get_leave_tangent()),
            'tangent_weight_mode': str(key.get_tangent_weight_mode()),
            'arrive_tangent_weight': float(key.get_arrive_tangent_weight()),
            'leave_tangent_weight': float(key.get_leave_tangent_weight()),
        })
    return {'name': str(channel.get_editor_property('channel_name')),
            'type': channel.get_class().get_name(),
            'default': float(channel.get_default()) if channel.has_default() else None,
            'pre_infinity': str(channel.get_pre_infinity_extrapolation()),
            'post_infinity': str(channel.get_post_infinity_extrapolation()), 'keys': keys}


def section_shape(section):
    result = {'type': section.get_class().get_name(),
              'start': section.get_start_frame() if section.has_start_frame() else None,
              'end': section.get_end_frame() if section.has_end_frame() else None,
              'completion': str(section.get_completion_mode())}
    if isinstance(section, unreal.MovieSceneSkeletalAnimationSection):
        result['animation'] = path(section.get_editor_property('params').get_editor_property('animation'))
    if isinstance(section, (unreal.MovieSceneFloatSection, unreal.MovieScene3DTransformSection,
                            unreal.MovieSceneAudioSection)):
        numeric_types = (unreal.MovieSceneScriptingFloatChannel, unreal.MovieSceneScriptingDoubleChannel)
        result['numeric_channels'] = [numeric_channel_shape(c) for c in section.get_all_channels()
                                      if isinstance(c, numeric_types)]
    return result


def sequence_shape(seq):
    tracks, audio_sections = [], []

    def read_tracks(scope, items):
        for index, track in enumerate(items):
            sections = list(track.get_sections())
            tracks.append({'scope': scope, 'index': index, 'type': track.get_class().get_name(),
                           'sections': [section_shape(s) for s in sections]})
            if isinstance(track, unreal.MovieSceneAudioTrack):
                for number, section in enumerate(sections):
                    audio_sections.append({'scope': scope, 'track': index, 'section': number,
                                           'sound': path(section.get_sound())})

    # Root/master tracks are deliberately covered; binding-only scans are insufficient.
    read_tracks('root', seq.get_tracks())
    bindings = []
    for binding in seq.get_bindings():
        guid = guid_value(binding.get_id())
        bindings.append({'id': guid, 'name': binding.get_name(), 'parent': guid_value(binding.get_parent().get_id())})
        read_tracks('binding:' + guid, binding.get_tracks())
    rate, tick = seq.get_display_rate(), seq.get_tick_resolution()
    return {'start': seq.get_playback_start(), 'end': seq.get_playback_end(),
            'display_rate': [rate.numerator, rate.denominator], 'tick_resolution': [tick.numerator, tick.denominator],
            'bindings': bindings, 'tracks': tracks}, audio_sections


def sequences():
    replacements = {old + '.' + old.rsplit('/', 1)[1]: AUDIO + '/S_CR055_Legacy' + name + '.S_CR055_Legacy' + name
                    for name, (old, _, _) in LEGACY.items()}
    rows = []
    for name, source in SEQUENCES.items():
        old = require_asset(source, unreal.LevelSequence)
        new = require_asset(ROOT + '/Sequences/LS_CR055_' + name, unreal.LevelSequence)
        old_shape, old_audio = sequence_shape(old)
        new_shape, new_audio = sequence_shape(new)
        check(old_shape == new_shape, name + ' preserves playback, rates, real GUID values, parent bindings, section timing, numeric curve keys/tangents/defaults and skeletal animation references')
        check(len(old_audio) == len(new_audio), name + ' preserves all audio section counts including root tracks')
        for index, original in enumerate(old_audio):
            if index >= len(new_audio):
                break
            current = new_audio[index]
            expected = replacements.get(original['sound'])
            check(expected is not None, name + ' audio section has a known cleared replacement: ' + str(original['sound']))
            check(current['sound'] == expected, name + ' replaces ' + original['scope'] + ' audio section ' + str(index))
            check(bool(current['sound']) and current['sound'].startswith(AUDIO + '/'), name + ' contains no unclassified legacy sequence sound')
        rows.append({'name': name, 'source': path(old), 'derivative': path(new), 'source_shape': old_shape,
                     'derivative_shape': new_shape, 'original_audio': old_audio, 'derivative_audio': new_audio,
                     'root_audio_sections': sum(s['scope'] == 'root' for s in new_audio)})
    return rows


def actors():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor_actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent'):
        raise AssertionError('Unable to load native persistent chapter for read-only assignment audit')
    all_actors = editor_actors.get_all_level_actors()
    expected = ('CR02_Scout_1', 'CR02_Scout_2', 'CR03_CalibrationWorkbench', 'CR05_RelayPresentation',
                'CR05_Ambience_RailYard', 'CR05_Ambience_Workshop', 'CR05_Ambience_RelayBunker')
    found = {}
    for label in expected:
        matches = [a for a in all_actors if a.get_actor_label() == label]
        check(len(matches) == 1, label + ' uniquely exists in loaded native levels')
        if len(matches) == 1:
            found[label] = matches[0]
    rows = {}
    for label, obj in found.items():
        row = {'actor': path(obj), 'class': obj.get_class().get_name(), 'level': path(obj.get_level()), 'references': {}}
        assignments = {}
        if label.startswith('CR02_Scout_'):
            assignments = {p: AUDIO + '/S_CR055_Legacy' + s for p, s in
                           (('shot_sound', 'EnemyShot'), ('hit_sound', 'EnemyHit'), ('death_sound', 'EnemyDeath'))}
        elif label == 'CR03_CalibrationWorkbench':
            assignments = {'sequence': ROOT + '/Sequences/LS_CR055_RookRestoration',
                           'activation_sound': AUDIO + '/S_CR055_LegacyCalibration'}
        elif label == 'CR05_RelayPresentation':
            assignments = {'power_sequence': ROOT + '/Sequences/LS_CR055_RelayPower',
                           'ending_sequence': ROOT + '/Sequences/LS_CR055_RelayEnding'}
        else:
            ambient = {'CR05_Ambience_RailYard': 'AmbYard', 'CR05_Ambience_Workshop': 'AmbWorkshop', 'CR05_Ambience_RelayBunker': 'AmbBunker'}
            component = obj.get_editor_property('audio_component')
            sound = component.get_editor_property('sound')
            row['references']['sound'] = path(sound)
            check(package(sound) == AUDIO + '/S_CR055_' + ambient[label], label + ' original loop assignment')
            check(near(component.get_editor_property('volume_multiplier'), .8), label + ' deliberate loop gain')
            row['attenuation_override'] = bool(component.get_editor_property('override_attenuation'))
            row['attenuation_asset'] = path(component.get_editor_property('attenuation_settings'))
            if row['attenuation_override']:
                attenuation = component.get_editor_property('attenuation_overrides')
                row['spatialize'] = bool(attenuation.get_editor_property('spatialize'))
                row['falloff_distance'] = float(attenuation.get_editor_property('falloff_distance'))
                check(row['spatialize'] and attenuation.get_editor_property('attenuate'), label + ' retains native spatial region')
        for prop, target in assignments.items():
            value = obj.get_editor_property(prop)
            row['references'][prop] = path(value)
            check(package(value) == target, label + ' ' + prop + ' points to intended Phase055 derivative')
        rows[label] = row
    check(len(rows) == 7, 'All seven existing actor assignments audited without mutation')
    return rows


def weapon():
    obj = require_asset('/Game/Generated/Phase02/Data/DA_Rook5', unreal.CRWeaponData)
    expected = {'shot_interval': .9, 'reload_duration': 2.4, 'magazine_capacity': 5,
                'initial_reserve': 25, 'aim_fov': 65}
    values = {name: obj.get_editor_property(name) for name in expected}
    for name, value in expected.items():
        check(near(values[name], value), 'Immutable ROOK-5 native value: ' + name)
    source = (PROJECT / 'Source/CinderRelay/CRWeaponComponent.cpp').read_text(encoding='utf-8-sig')
    optic_source = bool(re.search(r'HasSurveyUpgrade\(\)\s*\?\s*60\.f\s*:', source))
    check(optic_source, 'Installed optic 60-degree FOV remains in existing native policy source')
    return {'asset': path(obj), 'native_values': values, 'optic_fov': 60,
            'optic_verification': 'Source policy inspection only; actual ADS runtime is separate acceptance',
            'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest()}


for section_name, callback in (('interface', interface), ('audio', audio), ('sequences', sequences), ('actors', actors), ('weapon', weapon)):
    audit_section(section_name, callback)
REPORT['passed'] = not REPORT['failures']
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(REPORT, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
message = 'CR055_NATIVE_VERIFY_' + ('PASS ' if REPORT['passed'] else 'FAIL ') + json.dumps({'receipt': str(OUT), 'checks': len(REPORT['checks']), 'failures': REPORT['failures']})
if REPORT['passed']:
    unreal.log(message)
else:
    unreal.log_error(message)
unreal.SystemLibrary.quit_editor()
