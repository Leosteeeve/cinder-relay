"""Targeted native Interchange reimport after editing the existing Blender source/exports."""
import unreal,runpy,json
from pathlib import Path
p=Path(unreal.Paths.project_dir());assets=unreal.EditorAssetLibrary
manager=unreal.InterchangeManager.get_interchange_manager_scripted()
params=unreal.ImportAssetParameters();params.is_automated=True;params.follow_redirectors=True;params.replace_existing=True
results=[]
paths=['/Game/Generated/Phase03/Animation/AN_CR03_RookRestoration'] if '-CR03AnimationOnly' in unreal.SystemLibrary.get_command_line() else ['/Game/Generated/Phase03/Meshes/SM_CR03_SurveyOptic','/Game/Generated/Phase03/Animation/SK_CR03_Restoration','/Game/Generated/Phase03/Animation/AN_CR03_RookRestoration']
for path in paths:
    a=assets.load_asset(path);assert a and assets.get_metadata_tag(a,'CR.GeneratedBy')=='CinderRelay.Phase03.v1'
    result=manager.reimport_asset(a,params);assert result is not None and result is not False,'Reimport failed '+path
    assets.save_loaded_asset(assets.load_asset(path));results.append({'asset':path,'result':str(result)})
(p.parent/'.environment-local/phase-03/reimport.json').write_text(json.dumps(results,indent=2))
runpy.run_path(str(p/'Scripts/generate_restoration.py'))
