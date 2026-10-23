import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vibe,composition,visual_review

class CompositionTests(unittest.TestCase):
    def setUp(self):self.kit=vibe.module(vibe.SKILL/'assets/packaging/src/editorial.py','composition_tests')
    def examples(self,locale):return vibe.load(self.kit.ROOT/'locales'/locale/'base-examples.json')
    def test_all_twelve_base_designs_use_production_entry_and_local_media(self):
        for locale in ('en-US','zh-CN'):
            for row in self.examples(locale):
                data=copy.deepcopy(row['configuration']['data'])
                data['media']={k:{'src':'assets/media/user-'+str(i)+'.png'} for i,k in enumerate(data['media'])}
                result=self.kit.render(row['id'],'instance',9,data,locale=locale)
                self.assertEqual(result['implementation'],'handbook-base')
                self.assertEqual(result['design_reference'],row['id'])
                self.assertNotIn('<video',result['html'])
                self.assertNotIn('assets/media/book.mp4',result['html'])
                self.assertTrue(result['reading_order'])
                order={x['id']:x for x in result['reading_order']}
                for event in order.values():
                    self.assertLess(event['settle_at'],9)
                    for dep in event['depends_on']:self.assertGreaterEqual(event['enter_at'],order[dep]['settle_at'])
    def test_missing_media_and_content_cannot_silently_use_demo(self):
        data=copy.deepcopy(self.examples('zh-CN')[1]['configuration']['data'])
        del data['media']['a-film']
        with self.assertRaisesRegex(ValueError,'foreground media'):self.kit.render('compare','test',8,data,locale='zh-CN')
        data=copy.deepcopy(self.examples('en-US')[8]['configuration']['data']);del data['focus']
        with self.assertRaisesRegex(ValueError,'production never inherits'):self.kit.render('map-focus','test',8,data)
    def test_semantic_cues_and_dependency_failures_are_explicit(self):
        data=self.examples('en-US')[4]['configuration']['data']
        result=self.kit.render('relation','test',12,data,{'c':2,'a':4,'b':6,'l1':6,'l2':8})
        order={x['id']:x for x in result['reading_order']}
        self.assertEqual(order['test-l2']['enter_at'],8)
        with self.assertRaisesRegex(ValueError,'precedes settled anchors'):self.kit.render('relation','test',12,data,{'l1':0})
        with self.assertRaisesRegex(ValueError,'Unknown cue'):self.kit.render('relation','test',12,data,{'typo':4})
    def test_composed_timing_unique_ids_and_custom_review_inventory(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);vibe.init(p,'en-US');(p/'assets/media/bg.mp4').write_bytes(b'fixture')
            (p/'custom.py').write_text('def render(kit,prefix,duration,data,cues,locale):\n return kit.render("quote-reveal",prefix,duration,data,cues,locale)\n')
            film={'language':'en-US','duration':10,'extensions':[{'id':'new-name','source':'custom.py','design_reference':'evidence','reason':'A quotation needs deliberate pacing.'}],'scenes':[{'id':'scene','start':0,'duration':10,'purpose':'Compare two readings.','background':{'src':'assets/media/bg.mp4'},'components':[{'id':'first','component':'quote-reveal','duration':4,'data':{'lead':'First','emphasis':'Evidence'}},{'id':'second','component':'new-name','start':5,'duration':5,'data':{'lead':'Second','emphasis':'Context'}}]}]}
            vibe.save(p/'film.json',film);vibe.build(p)
            usage=vibe.load(p/'research/component-usage.json')
            self.assertEqual([x['start'] for x in usage],[0,5])
            self.assertEqual(usage[1]['implementation'],'project-extension')
            notes=vibe.load(p/'review/visual-plan.json')['review_notes']
            self.assertEqual(len(notes),2)
            self.assertTrue(any('Custom design' in s for s in notes[1]['reasons']))
            self.assertEqual(usage[1]['visual_inventory']['images'],0)
            self.assertGreater(usage[1]['visual_inventory']['text_characters'],0)
            page=(p/'compositions/scene.html').read_text()
            self.assertIn('scene-first-',page);self.assertIn('scene-second-',page)
            film['scenes'][0]['components'][1]['id']='first';vibe.save(p/'film.json',film)
            with self.assertRaisesRegex(ValueError,'unique id'):vibe.build(p)
    def test_undeclared_monkey_patch_is_not_library_reuse(self):
        def replacement(self):return {}
        self.kit.Component.render=replacement
        with self.assertRaisesRegex(ValueError,'Unregistered render override'):composition.verify_renderer(self.kit)
    def test_scale_outside_frame_and_count_overrides_fail(self):
        data=copy.deepcopy(self.examples('en-US')[6]['configuration']['data']);data['text']['part']='99'
        with self.assertRaisesRegex(ValueError,'Counts come from'):self.kit.render('quantity','test',8,data)

if __name__=='__main__':unittest.main()
