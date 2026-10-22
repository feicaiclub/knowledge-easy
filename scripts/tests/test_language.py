import importlib.util,json,re,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vibe
from language import resolve,caption_lines,CONFIG

class LanguageTests(unittest.TestCase):
    def test_new_projects_record_the_selected_language(self):
        for language in ['en-US','zh-CN']:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);vibe.init(root,language)
                for name in ['project.json','film.json','voice-plan.json']:
                    self.assertEqual(json.loads((root/name).read_text())['language'],language)

    def test_conflicting_languages_fail_and_legacy_projects_stay_chinese(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.assertEqual(resolve(root),'zh-CN')
            (root/'project.json').write_text('{"language":"en-US"}')
            with self.assertRaises(ValueError):resolve(root,{'language':'zh-CN'})
            self.assertEqual(CONFIG[resolve(root)]['tts'],'English')
            self.assertEqual(CONFIG[resolve(root)]['asr'],'en')

    def test_english_captions_preserve_words_and_limit_lines(self):
        text='The same evidence can lead to a different judgment when we understand the context.'
        result=caption_lines(text,'en-US')
        self.assertEqual(' '.join(result.split()),text)
        self.assertLessEqual(len(result.splitlines()),2)
        with self.assertRaises(ValueError):caption_lines('word '*80,'en-US')
        with self.assertRaises(ValueError):caption_lines('x'*70,'en-US')

    def test_english_and_chinese_catalogs_use_the_same_code(self):
        p=vibe.SKILL/'assets/packaging/src/base_catalog.py'
        m=vibe.module(p,'localized_base')
        for i,item in enumerate(m.ITEMS,1):
            en,_=m.build_scene(i,item[0],{'language':'en-US'})
            zh,_=m.build_scene(i,item[0],{'language':'zh-CN'})
            self.assertIsNone(re.search(r'[\u4e00-\u9fff]',en),item[0])
            self.assertIsNotNone(re.search(r'[\u4e00-\u9fff]',zh),item[0])

    def test_build_uses_english_fonts_and_html_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);vibe.init(root,'en-US')
            film={'language':'en-US','duration':4,'fps':30,'scenes':[{'id':'test','start':0,'duration':4,'component':'quote-reveal','data':{'lead':'A premise','emphasis':'A judgment'}}],'subtitles':[{'start':.1,'end':2,'text':'What changes the answer?'}]}
            vibe.save(root/'film.json',film);vibe.build(root)
            page=(root/'index.html').read_text();scene=(root/'compositions/test.html').read_text()
            self.assertIn('lang="en-US"',page);self.assertIn('inter.ttf',page)
            self.assertIn('source-serif-4.ttf',scene);self.assertNotIn('notoserifsc-',scene)

if __name__=='__main__':unittest.main()
