import json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vibe,event_clock,visual_review

class ArtDirectionTests(unittest.TestCase):
    def test_picture_and_audio_share_events_without_a_required_music_grid(self):
        film={'duration':12,'beats':[{'id':'arrival','time':5.2}]}
        self.assertAlmostEqual(event_clock.cue_start({'event':'arrival','offset':-.08},film),5.12)
        self.assertEqual(event_clock.beats({'duration':12}),{})
        with self.assertRaisesRegex(ValueError,'Unknown audio event'):event_clock.cue_start({'event':'missing'},film)
        with self.assertRaisesRegex(ValueError,'unique'):event_clock.beats({'duration':12,'beats':[{'id':'x','time':1},{'id':'x','time':2}]})
        with self.assertRaisesRegex(ValueError,'outside'):event_clock.beats({'duration':12,'beats':[{'id':'x','time':15}]})

    def test_authored_subjects_and_custom_references_build_without_legacy_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp).resolve();vibe.init(p,'en-US')
            (p/'assets/art').mkdir();(p/'assets/art/new.js').write_text('art.path("M200 200 L700 180 L800 650 Z", "accent");')
            (p/'assets/art/reference.jpg').write_bytes(b'reference fixture')
            film={'language':'en-US','duration':10,'beats':[{'id':'focus','time':4.5}],'scenes':[{'id':'new-subject','start':2,'duration':8,'purpose':'A custom spatial idea.','component':'artwork','data':{'source':'assets/art/new.js','style':{'engine':'etch','palette':{'paper':'#ffffff','ink':'#1b1f26','accent':'#245cd3'}},'design_reference':{'src':'assets/art/reference.jpg','reason':'The project owns its visual target.'},'configuration':{}}}]}
            film['design_reference']=film['scenes'][0]['data'].pop('design_reference')
            vibe.save(p/'film.json',film);vibe.build(p)
            usage=vibe.load(p/'research/component-usage.json');self.assertEqual(usage[0]['implementation'],'authored-artwork')
            self.assertEqual(usage[0]['design_reference']['src'],'assets/art/reference.jpg')
            page=(p/'compositions/new-subject.html').read_text();self.assertIn('"focus": 2.5',page)
            self.assertNotIn('class="scene-shade"',page)
            receipt=vibe.load(p/'research/build-receipt.json');self.assertIn('assets/art/new.js',receipt['files'])
            (p/'assets/art/new.js').write_text('art.ellipse(400,400,200,100,"ink");')
            with self.assertRaisesRegex(ValueError,'changed since build'):visual_review.require_current_build(p)

    def test_original_art_does_not_require_one_of_twelve_reference_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp).resolve();vibe.init(p,'en-US');(p/'ref.jpg').write_bytes(b'reference')
            (p/'shape.py').write_text('def render(kit,prefix,duration,data,cues,locale):\n return {"html":"<svg viewBox=\\"0 0 1920 1080\\"><circle cx=\\"960\\" cy=\\"480\\" r=\\"200\\"/></svg>","js":"", "reading_order":[]}\n')
            film={'duration':4,'language':'en-US','extensions':[{'id':'independent','source':'shape.py','design_reference':{'src':'ref.jpg','reason':'A project-specific target.'},'reason':'New spatial vocabulary.'}],'scenes':[{'id':'a','start':0,'duration':4,'purpose':'An intentionally geometric study.','surface':{'kind':'solid','color':'#ffffff'},'component':'independent','data':{}}]}
            vibe.save(p/'film.json',film);vibe.build(p)
            usage=vibe.load(p/'research/component-usage.json');self.assertEqual(usage[0]['parent'],'project-art-direction')

if __name__=='__main__':unittest.main()
