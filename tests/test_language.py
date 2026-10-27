import json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'knowledge-easy/scripts'))
import vibe
from language import resolve,caption_lines,CONFIG

class LanguageTests(unittest.TestCase):
    def test_new_projects_record_chinese_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);vibe.init(root,'zh-CN')
            for name in ['project.json','film.json','voice-plan.json']:
                self.assertEqual(json.loads((root/name).read_text())['language'],'zh-CN')

    def test_legacy_projects_stay_chinese_and_unsupported_language_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.assertEqual(resolve(root),'zh-CN')
            self.assertEqual(CONFIG[resolve(root)]['tts'],'Chinese')
            self.assertEqual(CONFIG[resolve(root)]['asr'],'zh')
            with self.assertRaises(ValueError):resolve(root,{'language':'en-US'})
            (root/'project.json').write_text('{"language":"en-US"}')
            with self.assertRaises(ValueError):resolve(root)

    def test_unsupported_caption_language_is_not_silently_used(self):
        with self.assertRaises(ValueError):caption_lines('Unsupported language','en-US')

    def test_chinese_captions_stay_on_one_line_without_losing_words(self):
        text='我们改变的，也许不是选择，而是解释。'
        self.assertEqual(caption_lines(text,'zh-CN'),text)
        self.assertEqual(caption_lines('字'*26,'zh-CN'),'字'*26)
        for text in ['第一句\n第二句','字'*27]:
            with self.assertRaises(ValueError):caption_lines(text,'zh-CN')

    def test_build_uses_chinese_fonts_and_html_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);vibe.init(root,'zh-CN')
            film={'language':'zh-CN','duration':4,'fps':30,'scenes':[{'id':'test','start':0,'duration':4,'component':'quote-reveal','data':{'lead':'一个前提','emphasis':'一个判断'}}],'subtitles':[{'start':.1,'end':2,'text':'什么改变了答案？'}]}
            film['scenes'][0].update(purpose='检查中文字体。',surface_reason='独立排版测试。')
            vibe.save(root/'film.json',film);vibe.build(root)
            page=(root/'index.html').read_text();scene=(root/'compositions/test.html').read_text()
            self.assertIn('lang="zh-CN"',page)
            self.assertIn('notosanssc-',page)
            self.assertIn('notoserifsc-',scene)
            self.assertNotIn('source-serif-4.ttf',scene)

if __name__=='__main__':unittest.main()
