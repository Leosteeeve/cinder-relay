"""Create only owned Phase055 interface assets using the actual UE5.8 Editor.

The native bridge builds a real editable WidgetTree, not a screenshot-only UI.
An existing Designer tree is verified and preserved; no prior-phase asset changes.
Run after compiling CRInterfaceLibrary. No engine/plugin changes are needed.
"""
import hashlib
import json
from pathlib import Path
import unreal

PROJECT = Path(unreal.Paths.project_dir())
EVIDENCE = PROJECT.parent / '.environment-local' / 'phase-05-5'
SOURCE = PROJECT / 'ArtSource' / 'Interface' / 'Phase055'
ROOT = '/Game/Generated/Phase055/Interface'
OWNER = 'CinderRelay.Phase055.Interface.v1'
ASSETS = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
LIB = unreal.CRInterfaceLibrary
EVIDENCE.mkdir(parents=True, exist_ok=True)
receipt = {'owner': OWNER, 'created': [], 'preserved': [], 'source_files': []}


def owned(path):
    obj = ASSETS.load_asset(path) if ASSETS.does_asset_exist(path) else None
    if obj:
        assert ASSETS.get_metadata_tag(obj, 'CR.GeneratedBy') == OWNER, 'Refusing unowned asset: ' + path
        receipt['preserved'].append(path)
    return obj


def save(obj):
    assert obj is not None
    ASSETS.set_metadata_tag(obj, 'CR.GeneratedBy', OWNER)
    assert ASSETS.save_loaded_asset(obj), obj.get_path_name()
    return obj


def import_file(source, name, folder, factory=None):
    path = ROOT + '/' + folder + '/' + name
    current = owned(path)
    if current:
        return current
    assert source.is_file(), 'Missing cleared source: ' + str(source)
    receipt['source_files'].append({'path': str(source.relative_to(PROJECT)), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_name = name
    task.destination_path = ROOT + '/' + folder
    task.automated = True
    task.save = False
    task.replace_existing = False
    if factory:
        task.factory = factory
    TOOLS.import_asset_tasks([task])
    assert task.imported_object_paths, str(source)
    for actual in task.imported_object_paths:
        imported = ASSETS.load_asset(actual)
        assert imported, actual
        assert imported.get_path_name().startswith(ROOT + '/'), actual
        save(imported)
        receipt['created'].append(imported.get_path_name())
    result = ASSETS.load_asset(path)
    assert result, 'Importer changed expected asset name: ' + path
    return result


def font(source_name, label):
    factory = unreal.FontFileImportFactory()
    factory.set_editor_property('batch_create_font_asset', unreal.BatchCreateFontAsset.NO)
    face = import_file(SOURCE / 'Fonts' / source_name, 'FF_CR055_' + label, 'Fonts', factory)
    assert isinstance(face, unreal.FontFace), face
    # Inline a small licensed face so a menu's first glyph does not trigger font-file streaming.
    if hasattr(unreal, 'FontLoadingPolicy'):
        face.set_editor_property('loading_policy', unreal.FontLoadingPolicy.INLINE)
        save(face)
    name = 'F_CR055_' + label
    existing = owned(ROOT + '/Fonts/' + name)
    if existing:
        return existing
    result = TOOLS.create_asset(name, ROOT + '/Fonts', unreal.Font, unreal.FontFactory())
    assert LIB.configure_composite_font(result, face), name
    save(result)
    receipt['created'].append(result.get_path_name())
    return result


body = font('Barlow-Regular.ttf', 'Body')
title = font('BarlowCondensed-SemiBold.ttf', 'Title')
images = {}
for source_name, name, is_mark in [
    ('CR055_MenuBackground.png', 'T_CR055_MenuBackground', False),
    ('CR055_RelayMark.png', 'T_CR055_RelayMark', True),
    ('CR055_GameIcon.png', 'T_CR055_GameIcon', True),
    ('Icons/CR055_IconRook.png', 'T_CR055_IconRook', True),
    ('Icons/CR055_IconOptic.png', 'T_CR055_IconOptic', True),
    ('Icons/CR055_IconAmmo.png', 'T_CR055_IconAmmo', True),
    ('Icons/CR055_IconPowerModule.png', 'T_CR055_IconPowerModule', True),
]:
    source = SOURCE / source_name
    # The authoring render may be in its dedicated exports child folder.
    if not source.is_file() and (SOURCE / 'Exports' / source_name).is_file():
        source = SOURCE / 'Exports' / source_name
    texture = import_file(source, name, 'Textures')
    assert isinstance(texture, unreal.Texture2D)
    texture.set_editor_property('srgb', True)
    texture.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_DEFAULT)
    texture.set_editor_property('max_texture_size', 512 if is_mark else 2048)
    texture.set_editor_property('never_stream', True)
    # Only the compressed1920x1080 derivative enters the title UI; promotional masters are not imported.
    save(texture)
    images[name] = texture.get_path_name()

name = 'WBP_CR_HUDRoot'
path = ROOT + '/Widgets/' + name
blueprint = owned(path)
if not blueprint:
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property('parent_class', unreal.load_class(None, '/Script/CinderRelay.CRHUDWidget'))
    blueprint = TOOLS.create_asset(name, ROOT + '/Widgets', unreal.WidgetBlueprint, factory)
    assert blueprint
    assert LIB.build_designer_layout(blueprint, body, title, 'HUDRoot'), 'Native WidgetTree authoring failed; do not fabricate binary assets'
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    save(blueprint)
    receipt['created'].append(blueprint.get_path_name())

names = {str(n) for n in LIB.get_designer_widget_names(blueprint)}
# Bounded migration after the first actual1080p capture: avoid title/subtitle
# overlap caused by Slate's point-size metrics. Preserve all other Designer edits.
if ASSETS.get_metadata_tag(blueprint, 'CR.TitleSpacingRevision') != '2':
    tree = unreal.find_object(blueprint, 'WidgetTree')
    subtitle = unreal.find_object(tree, 'MenuBody')
    slot = subtitle.get_editor_property('slot')
    position = slot.get_position()
    assert abs(position.x - 100) < .01 and (abs(position.y - 410) < .01 or abs(position.y - 460) < .01), 'Unexpected authored title position; preserve and review'
    blueprint.modify()
    subtitle.modify()
    slot.modify()
    slot.set_position(unreal.Vector2D(100, 460))
    slot.set_size(unreal.Vector2D(580, 58))
    ASSETS.set_metadata_tag(blueprint, 'CR.TitleSpacingRevision', '2')
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
if ASSETS.get_metadata_tag(blueprint, 'CR.ReadabilityRevision') != '3':
    tree = unreal.find_object(blueprint, 'WidgetTree')
    def widget(name):
        value = unreal.find_object(tree, name)
        assert value, name
        value.modify()
        return value
    def font_size(name, points):
        value = widget(name)
        info = value.get_editor_property('font')
        info.set_editor_property('size', points)
        value.set_font(info)
    blueprint.modify()
    font_size('HealthValue', 36)
    optic_slot = widget('OpticState').get_editor_property('slot')
    optic_slot.set_position(unreal.Vector2D(24, -30))
    optic_slot.set_size(unreal.Vector2D(216, 24))
    state = widget('PackDetailState')
    font_size('PackDetailState', 18)
    state.set_editor_property('justification', unreal.TextJustify.LEFT)
    state_slot = state.get_editor_property('slot')
    state_slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0, 0), maximum=unreal.Vector2D(0, 0)))
    state_slot.set_alignment(unreal.Vector2D(0, 0))
    state_slot.set_position(unreal.Vector2D(40, 94))
    state_slot.set_size(unreal.Vector2D(900, 32))
    icon_slot = widget('PackIcon').get_editor_property('slot')
    icon_slot.set_position(unreal.Vector2D(0, 150))
    icon_slot.set_size(unreal.Vector2D(520, 260))
    font_size('PackDetailBody', 22)
    body_slot = widget('PackDetailBody').get_editor_property('slot')
    offsets = body_slot.get_offsets()
    offsets.set_editor_property('top', 430)
    body_slot.set_offsets(offsets)
    ASSETS.set_metadata_tag(blueprint, 'CR.ReadabilityRevision', '3')
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
required = {
    'HUDRoot', 'GameplayLayer', 'ObjectivePanel', 'ObjectiveLabel', 'Objective',
    'Prompt', 'StreamingStatus', 'CheckpointStatus', 'EventNotice', 'HealthBar', 'HealthValue',
    'HealthState', 'WeaponLabel', 'Magazine', 'Reserve', 'ReloadState', 'OpticState',
    'Reticle', 'ConfirmedHit', 'DamageTint', 'SubtitlePanel', 'Subtitle', 'AssemblyHelp',
    'MenuBackdrop', 'TitleBackground', 'RelayMark', 'MenuTitle', 'MenuBody', 'SaveAvailability',
    'Resume', 'Continue', 'Restart', 'Settings', 'Credits', 'Exit',
    'ModalPanel', 'ModalTitle', 'ModalBody', 'ModalChoices',
    'PackPanel', 'PackCategories', 'PackItems', 'PackDetailTitle', 'PackDetailState',
    'PackDetailBody', 'PackIcon', 'PackFooter', 'PackClose',
}
assert required <= names, sorted(required - names)
assert blueprint.generated_class(), 'Widget Blueprint must compile to a native usable class'
cdo = unreal.get_default_object(blueprint.generated_class())
# The authored tree already contains fonts. Native dynamic modal rows use these
# same class defaults, avoiding an unrelated engine-default typeface at runtime.
if cdo.get_editor_property('body_font') is None:
    cdo.set_editor_property('body_font', body)
if cdo.get_editor_property('title_font') is None:
    cdo.set_editor_property('title_font', title)
save(blueprint)
receipt.update({'widget_blueprint': blueprint.get_path_name(), 'generated_class': blueprint.generated_class().get_path_name(),
    'designer_widgets': sorted(names), 'body_font': body.get_path_name(), 'title_font': title.get_path_name(),
    'images': images, 'layout': 'One active Designer-editable hierarchy with reusable native construction functions; no unused duplicate panel Blueprints',
    'scope': 'Asset authoring only; no gameplay/input/package/visual acceptance claimed'})
(EVIDENCE / 'interface-import.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
unreal.log('CR055_INTERFACE_IMPORT_PASS ' + json.dumps(receipt))
unreal.SystemLibrary.quit_editor()
