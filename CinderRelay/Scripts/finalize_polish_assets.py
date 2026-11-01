"""Bounded final asset pass: three loop reimports, read-only structural audit, real renders."""
from pathlib import Path
import unreal
scripts=Path(unreal.Paths.project_dir())/'Scripts'
for name in ('reimport_polish_ambience.py','validate_polish_assets.py'):
 code=(scripts/name).read_text(encoding='utf-8');code=code.replace('unreal.SystemLibrary.quit_editor()','')
 exec(compile(code,str(scripts/name),'exec'),{'__name__':'__main__'})
exec(compile((scripts/'capture_polish.py').read_text(encoding='utf-8'),str(scripts/'capture_polish.py'),'exec'),{'__name__':'__main__'})
