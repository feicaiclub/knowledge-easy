import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'knowledge-easy/scripts'))
import vibe

kit=vibe.module(vibe.SKILL/'assets/packaging/src/editorial.py','visual_tests')

class VisualTests(unittest.TestCase):
    def scene(self):
        return {'id':'reason','component':'quote-reveal','purpose':'Explain a changed judgment.',
                'background':{'src':'assets/media/scene.mp4'}}

    def test_background_preserves_authored_treatment_without_forcing_a_look(self):
        s=self.scene();original=copy.deepcopy(s)
        self.assertEqual(vibe.visual_background(s),s['background'])
        self.assertEqual(s,original)
        s['background']['grading']={'effects':{'blur':0},'adjust':{'exposure':.2}}
        self.assertEqual(vibe.visual_background(s)['grading']['effects']['blur'],0)

    def test_old_snapshots_keep_their_legacy_background_defaults(self):
        bg=vibe.visual_background(self.scene(),legacy=True)
        self.assertEqual(bg['grading']['effects']['blur'],.7)
        self.assertEqual(bg['shade'],.25)

    def test_accidental_blank_or_hidden_surface_fails(self):
        s=self.scene();s.pop('background')
        with self.assertRaisesRegex(ValueError,'choose a surface'):vibe.visual_background(s)
        s=self.scene();s['background']['src']='poster.jpg'
        with self.assertRaisesRegex(ValueError,'moving video'):vibe.visual_background(s)
        s=self.scene();s['footage']={'src':'cover.mp4'}
        with self.assertRaisesRegex(ValueError,'cover the background'):vibe.visual_background(s)
        s=self.scene();s['background']['grading']={'effects':{'blur':-1}}
        with self.assertRaisesRegex(ValueError,'blur'):vibe.visual_background(s)

    def test_designed_surfaces_and_clear_footage_are_first_class(self):
        for surface in [{'kind':'solid','color':'#ffffff'},{'kind':'gradient','color':'#223344','to':'#aabbcc'}]:
            s=self.scene();s.pop('background');s['surface']=surface
            self.assertIsNone(vibe.visual_background(s));self.assertIn('background:',vibe.surface_markup(surface))
        s=self.scene();s.pop('background');s.update(component='artwork')
        self.assertIsNone(vibe.visual_background(s))
        s=self.scene();s.pop('background');s.update(component='annotation',footage={'src':'scene.mp4'})
        self.assertIsNone(vibe.visual_background(s))

    def test_connectors_cannot_cross_or_crowd_images(self):
        boxes={'image':(600,250,400,300)}
        for points in [[(200,400),(1300,400)],[(200,240),(1300,240)]]:
            with self.assertRaisesRegex(ValueError,'crosses or crowds'):
                kit.LAYOUT.validate_layout(boxes,[{'id':'edge','points':points}])
        kit.LAYOUT.validate_layout(boxes,[{'id':'edge','points':[(200,210),(1300,210)]}])

    def test_information_and_arrowheads_stay_in_safe_area(self):
        with self.assertRaisesRegex(ValueError,'caption reserve'):
            kit.LAYOUT.validate_layout({'label':(300,810,500,60)})
        with self.assertRaisesRegex(ValueError,'safe area'):
            kit.LAYOUT.validate_layout({},[{'id':'edge','points':[(200,80),(500,80)]}])
        with self.assertRaisesRegex(ValueError,'overlap'):
            kit.LAYOUT.validate_layout({'photo':(300,200,600,400),'label':(500,400,300,80)})

    def test_production_examples_fit_and_reveal_connections_after_nodes(self):
        for locale in ('zh-CN',):
            path=kit.ROOT/'variants.json'
            for row in json.loads(path.read_text()):
                c=row['configuration'];r=kit.render(row['id'],'test',8,c['data'],c.get('cues'),locale)
                if row['id'] in ('feedback-loop','evidence-collage','context-reveal','relation-bridge'):
                    self.assertIsNotNone(r['layout'],row['id'])
                order={n['id']:n for n in r['reading_order']}
                for node in r['reading_order']:
                    for dep in node['depends_on']:
                        self.assertGreaterEqual(node['enter_at']+.001,order[dep]['settle_at'],(row['id'],node['id'],dep))

    def test_context_reveal_uses_one_media_placement(self):
        r=kit.render('context-reveal','test',8,{'image':{'src':'assets/media/context.mp4','type':'video'},'detail':'The detail','context':'The full picture'},locale='zh-CN')
        self.assertEqual(r['html'].count('<video '),1)
        self.assertEqual(r['html'].count('assets/media/context.mp4'),1)

    def test_usage_report_flags_a_review_without_imposing_variety(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);vibe.init(root,'zh-CN')
            (root/'assets/media/scene.mp4').write_bytes(b'build-only fixture')
            scenes=[]
            for i in range(4):
                s=self.scene();s.update(id=f'scene{i}',start=i*4,duration=4,data={'lead':'The evidence','emphasis':'The question'})
                scenes.append(s)
            vibe.save(root/'film.json',{'language':'zh-CN','duration':16,'scenes':scenes})
            vibe.build(root)
            report=vibe.load(root/'review/visual-plan.json')
            self.assertTrue(report['review_notes'])
            self.assertEqual(report['components']['quote-reveal'],4)
            usage=vibe.load(root/'research/component-usage.json')
            self.assertEqual(len(usage),4)
            self.assertEqual(usage[0]['background']['src'],'assets/media/scene.mp4')
            self.assertEqual(usage[0]['background']['grading']['effects']['blur'],.7)

if __name__=='__main__':unittest.main()
