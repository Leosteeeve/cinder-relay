"""Reimport only the three owned loop WAVs after their verified seam correction."""
import unreal,json
from pathlib import Path
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05';assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();done=[]
for name in ('YardWind','WorkshopHum','BunkerHum'):
 n='S_CR05_'+name;path='/Game/Generated/Phase05/Audio/'+n;a=assets.load_asset(path);assert a and assets.get_metadata_tag(a,'CR.GeneratedBy')=='CinderRelay.Phase05.v1'
 task=unreal.AssetImportTask();task.filename=str(out/'exports'/(n+'.wav'));task.destination_path='/Game/Generated/Phase05/Audio';task.destination_name=n;task.automated=True;task.replace_existing=True;task.save=True;tools.import_asset_tasks([task]);a=assets.load_asset(path);a.set_editor_property('looping',True);assert assets.save_loaded_asset(a);done.append(path)
(out/'audio-reimport.json').write_text(json.dumps(done,indent=2));unreal.log('CR05_AMBIENCE_REIMPORT_PASS');unreal.SystemLibrary.quit_editor()
