"""Focused evidence-preservation test; no Unreal process or gameplay assertions."""
import runpy
import sys
import tempfile
import types
import unittest
from pathlib import Path

SCRIPT=Path(__file__).with_name('review_presentation.py')

class NativeBoundary(Exception):
    pass

class EvidenceGuard(unittest.TestCase):
    def check_case(self,after,existing):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            project=root/'CinderRelay'
            project.mkdir()
            out=root/'.environment-local/phase-05-2'
            out.mkdir(parents=True)
            baseline=out/'before-inventory.json'
            if existing:
                baseline.write_text('protected original audit')
            fake=types.SimpleNamespace(
                Paths=types.SimpleNamespace(project_dir=lambda:str(project)),
                SystemLibrary=types.SimpleNamespace(get_command_line=lambda:'-CR052After' if after else ''),
                LevelEditorSubsystem=object)
            def native(*args):
                raise NativeBoundary('Native editor access reached')
            fake.get_editor_subsystem=native
            previous=sys.modules.get('unreal')
            sys.modules['unreal']=fake
            try:
                expected=FileExistsError if existing and not after else NativeBoundary
                with self.assertRaises(expected):
                    runpy.run_path(str(SCRIPT))
                if existing:
                    self.assertEqual(baseline.read_text(),'protected original audit')
            finally:
                if previous is None:
                    sys.modules.pop('unreal',None)
                else:
                    sys.modules['unreal']=previous

    def test_original_cannot_be_overwritten(self):
        self.check_case(False,True)

    def test_after_review_is_allowed(self):
        self.check_case(True,True)

    def test_new_before_audit_is_allowed(self):
        self.check_case(False,False)

if __name__=='__main__':
    unittest.main()
