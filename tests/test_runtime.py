import importlib.util,json,os,sys,tempfile,unittest,subprocess,wave
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'knowledge-easy/scripts'))
import bootstrap
import vibe

class RuntimeTests(unittest.TestCase):
    def test_mix_refuses_to_cut_narration(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with wave.open(str(root/'voice.wav'),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000);wav.writeframes(b'\0\0'*16000)
            (root/'plan.json').write_text(json.dumps({'duration':1,'narration':'voice.wav','cues':[]}))
            result=subprocess.run([sys.executable,str(bootstrap.SKILL/'scripts/mix.py'),'--project',str(root),'--plan',str(root/'plan.json')],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((root/'audio/mix.wav').exists())

    def test_reject_dependency_directory_inside_bundle(self):
        with patch.dict(os.environ,{'VIBE_RUNTIME_HOME':str(bootstrap.SKILL/'bad-runtime')}):
            with self.assertRaises(ValueError):bootstrap.runtime_home()
        self.assertFalse((bootstrap.SKILL/'bad-runtime').exists())

    def test_readonly_cold_check_does_not_create_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'uninstalled'
            with patch.dict(os.environ,{'VIBE_RUNTIME_HOME':str(root)}),patch.object(bootstrap,'ensure_uv',return_value=None),patch.object(bootstrap,'ensure_python',return_value=None),patch.object(bootstrap,'ensure_media',return_value=None),patch.object(bootstrap,'ensure_render',return_value=None):
                result,_=bootstrap.ensure({'render'},install=False)
            self.assertFalse(result['ready']);self.assertIn('render-runtime',result['missing']);self.assertFalse(root.exists())

    def test_project_cannot_write_into_skill(self):
        with self.assertRaises(ValueError):vibe.project_path(bootstrap.SKILL/'test-film')

    def test_snapshot_update_requires_explicit_choice(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);dest=vibe.install_pack(root)
            (dest/'editorial.py').write_text('# changed')
            with self.assertRaises(ValueError):vibe.install_pack(root)
            vibe.install_pack(root,update=True)
            self.assertIn('def render(', (dest/'editorial.py').read_text())

    def test_component_version_upgrade_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);vibe.install_pack(root)
            lock=vibe.load(root/'kit/editorial-lock.json');lock['version']='1.1.0';vibe.save(root/'kit/editorial-lock.json',lock)
            with self.assertRaises(ValueError):vibe.install_pack(root)
            vibe.install_pack(root,update=True)
            expected=vibe.load(bootstrap.SKILL/'assets/packaging/src/renderer-contract.json')['version']
            self.assertEqual(vibe.load(root/'kit/editorial-lock.json')['version'],expected)

    def test_new_project_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);vibe.init(root)
            (root/'project.json').write_text('{"keep":true}')
            with self.assertRaises(ValueError):vibe.init(root)
            self.assertEqual(json.loads((root/'project.json').read_text()),{'keep':True})

    def test_subtitle_quantization_avoids_adjacent_overlap(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);vibe.init(root)
            film={'duration':3,'fps':30,'scenes':[{'id':'test','start':0,'duration':3,'component':'quote-reveal','data':{'lead':'Premise','emphasis':'Judgment'},'cues':{'lead':.1,'emphasis':1}}],
                  'subtitles':[{'start':.03,'end':1.049,'text':'Premise'},{'start':1.051,'end':2.5,'text':'Judgment'}]}
            film['scenes'][0].update(purpose='Check caption endpoints.',surface_reason='Isolated subtitle-timing test fixture.')
            vibe.save(root/'film.json',film);vibe.build(root)
            self.assertTrue((root/'index.html').exists())
            film['subtitles'][1]['start']=.5;vibe.save(root/'film.json',film)
            with self.assertRaises(ValueError):vibe.build(root)

    def test_scene_identity_not_alias_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'a.mp4').write_bytes(b'fixture');(root/'b.mp4').write_bytes(b'fixture')
            vibe.save(root/'assets.json',{'placements':[{'id':'one','file':'a.mp4','original_shots':['origin:0-3']},{'id':'two','file':'b.mp4','original_shots':['origin:0-3']}]})
            with self.assertRaises(ValueError):vibe.audit_media(root)

if __name__=='__main__':unittest.main()
