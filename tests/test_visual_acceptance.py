import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'knowledge-easy/scripts'))
import vibe,visual_review as review

class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name).resolve();p=self.p
        vibe.init(p,'zh-CN');(p/'assets/media/bg.mp4').write_bytes(b'build fixture')
        vibe.save(p/'film.json',{'language':'zh-CN','duration':4,'scenes':[{'id':'scene','start':0,'duration':4,'purpose':'An isolated review fixture.','background':{'src':'assets/media/bg.mp4'},'component':'quote-reveal','data':{'lead':'Evidence','emphasis':'Context'}}]})
        (p/'assets/vendor').mkdir();(p/'assets/vendor/gsap.min.js').write_text('/* fixture */')
        vibe.build(p);(p/'final/fixture.mp4').write_bytes(b'not a real film: unit test binding fixture')
        review.bind_render(p,'final/fixture.mp4',review.source_signature(p))
        receipt=vibe.load(p/'review/render-receipt.json');usage=vibe.load(p/'research/component-usage.json')
        record={'export':'final/fixture.mp4','export_sha256':receipt['sha256'],'source_sha256':receipt['source']['sha256'],'reviewer':'test fixture','status':'pending','evidence_sha256':{},'evidence_index':'review/index.json','scenes':[]}
        for item in usage:
            row={'id':item['id'],'design_reference':item['design_reference'],'implementation':item['implementation'],'frames':[],'motion_file':'review/motion.mp4','reference_file':'review/ref.jpg','motion_watched':False,'verdict':'pending','criteria':{k:{'verdict':'pending','observation':''} for k in review.CRITERIA}}
            record['scenes'].append(row)
        for name in ['review/motion.mp4','review/ref.jpg']:
            (p/name).write_bytes(b'unit test evidence');record['evidence_sha256'][name]=review.sha(p/name)
        index={k:record[k] for k in ('export_sha256','source_sha256','evidence_sha256')}
        index['scenes']=[{k:r[k] for k in ('id','design_reference','implementation','frames','motion_file','reference_file')} for r in record['scenes']]
        vibe.save(p/'review/index.json',index);vibe.save(p/'review/visual-review.json',record);self.record=record
    def tearDown(self):self.tmp.cleanup()
    def pass_record(self):
        r=copy.deepcopy(self.record)
        for row in r['scenes']:
            row.update(motion_watched=True,verdict='pass')
            row['criteria']={k:{'verdict':'pass','observation':'Unit test judgment fixture.'} for k in review.CRITERIA}
        vibe.save(self.p/'review/visual-review.json',r)
    def test_technical_export_cannot_automatically_pass_design(self):
        with self.assertRaisesRegex(ValueError,'watch actual motion'):review.accept(self.p)
        self.pass_record();self.assertEqual(review.accept(self.p)['status'],'passed')
    def test_new_export_or_changed_source_invalidates_review(self):
        self.pass_record();(self.p/'compositions/scene.html').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Source changed'):review.accept(self.p)
    def test_evidence_or_coverage_changes_are_rejected(self):
        self.pass_record();(self.p/'review/motion.mp4').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'evidence changed'):review.accept(self.p)
        r=copy.deepcopy(self.record);r['scenes']=[];vibe.save(self.p/'review/visual-review.json',r)
        with self.assertRaisesRegex(ValueError,'coverage was changed'):review.accept(self.p)
    def test_content_changes_require_a_fresh_build(self):
        review.require_current_build(self.p)
        p=self.p/'film.json';film=vibe.load(p);film['scenes'][0]['data']['lead']='Changed content';vibe.save(p,film)
        with self.assertRaisesRegex(ValueError,'changed since build'):review.require_current_build(self.p)

    def test_whole_film_and_listening_are_not_implied_by_component_passes(self):
        self.pass_record();r=vibe.load(self.p/'review/visual-review.json');r['schema']=2
        r['sequence']=[{'id':'scene'}]
        r['whole_film']={'watched':False,'listened':False,'audio_present':True,'criteria':{k:{'verdict':'pass','observation':'Unit test only.'} for k in review.FILM_CRITERIA}}
        index=vibe.load(self.p/'review/index.json');index['sequence']=r['sequence'];vibe.save(self.p/'review/index.json',index)
        vibe.save(self.p/'review/visual-review.json',r)
        with self.assertRaisesRegex(ValueError,'full exported film'):review.accept(self.p)
        r['whole_film']['watched']=True;vibe.save(self.p/'review/visual-review.json',r)
        with self.assertRaisesRegex(ValueError,'listening review'):review.accept(self.p)
        r['whole_film']['listened']=True;vibe.save(self.p/'review/visual-review.json',r)
        self.assertEqual(review.accept(self.p)['status'],'passed')

    def test_missing_observations_do_not_count_as_a_pass(self):
        self.pass_record();r=vibe.load(self.p/'review/visual-review.json');r['scenes'][0]['criteria']['material']['observation']=''
        vibe.save(self.p/'review/visual-review.json',r)
        with self.assertRaisesRegex(ValueError,'supported judgment'):review.accept(self.p)

if __name__=='__main__':unittest.main()
