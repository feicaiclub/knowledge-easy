"""Production inputs and timing for the original handbook designs.

The catalog and films call the same composition functions. Background ownership
stays with the film; foreground media and semantic cues belong to each instance.
"""
import html, json, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFINITIONS = {x['id']: x for x in json.loads((ROOT/'components.json').read_text())}


def finite(value, name):
    value=float(value)
    if not math.isfinite(value):raise ValueError(name+' must be finite')
    return value


class State:
    def __init__(self, config, kind, prefix):
        self.config=config;self.kind=kind;self.prefix=prefix
        self.locale=config.get('language','zh-CN');self.production=config.get('_production',False)
        self.duration=finite(config.get('duration',8),'duration')
        self.order=[];self.settles={};self.used_text=set();self.used_media=set();self.used_cues=set()
        self.cues=config.get('cues',{});self.text=config.get('text',{});self.media_inputs=config.get('media',{})
        self.scale=.82 if kind.startswith('map-') else .86
        if not self.production:return
        if kind not in DEFINITIONS:raise ValueError('Unknown base design: '+kind)
        if not re.fullmatch(r'[A-Za-z][\w-]*',prefix):raise ValueError('Invalid component instance id')
        if self.duration<2:raise ValueError('Base designs need at least two seconds; allow a readable hold.')
        if 'bg' in self.media_inputs:raise ValueError('Put background in the scene, not in component media.bg.')
        required=set(DEFINITIONS[kind]['text_slots'])-{'total','part'}
        missing=required-self.text.keys()
        if missing:raise ValueError(kind+': missing text slots '+', '.join(sorted(missing)))
        for key,value in self.cues.items():
            at=finite(value,key)
            if not 0<=at<self.duration-.2:raise ValueError('Cue outside component duration: '+key)
        requirements={'chapter':['chapters'],'evidence':['evidence'],'timeline':['stages'],
                      'quantity':['total','selected'],'map-focus':['focus','view'],
                      'map-route':['points','view'],'map-period':['periods','view']}
        for key in requirements.get(kind,[]):
            if key not in config:raise ValueError(kind+': supply '+key+'; production never inherits example facts.')
        if kind=='chapter':
            for row in config['chapters']:
                if len(row)!=3 or not all(isinstance(x,str) for x in row):raise ValueError('chapters: [heading, subtitle, media slot alias]')
        if kind=='timeline':
            if len(config['stages'])!=3 or any(len(x)!=2 for x in config['stages']):raise ValueError('timeline: three [label, media slot alias] stages')
        if kind=='evidence' and not all(k in config['evidence'] for k in ('heading','questions','closing','kicker')):
            raise ValueError('evidence needs heading, questions, closing and kicker')
        if kind=='quantity' and ('total' in self.text or 'part' in self.text):
            raise ValueError('Counts come from total and selected, never independent text overrides.')

    def key(self,id):return id[len(self.prefix)+1:]

    def copy(self,id,default,width,size,decorative=False):
        key=self.key(id);self.used_text.add(key)
        value=self.text.get(key,'' if decorative else default)
        if not isinstance(value,str):raise ValueError('Text slot must be a string: '+key)
        if decorative:return value
        for line in value.split('\n'):
            advance=sum(1 if ord(c)>255 else .54 for c in line)*size+max(0,len(line)-1)*.6
            if advance>width+12:raise ValueError(key+': text exceeds its designed width; shorten it or use a considered line break.')
        return value

    def media(self,id,rect):
        key=self.key(id);self.used_media.add(key)
        if key not in self.media_inputs:raise ValueError(self.kind+': supply foreground media slot '+key)
        info=self.media_inputs[key]
        if isinstance(info,str):info={'src':info}
        src=info.get('src','')
        if not src or Path(src).is_absolute() or '..' in Path(src).parts or re.match(r'\w+:',src):raise ValueError('Use a project-relative media path')
        image=info.get('type')=='image' or Path(src).suffix.lower() in ('.png','.jpg','.jpeg','.webp','.svg','.avif')
        style='position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:'+html.escape(info.get('focus','50% 50%'),quote=True)+';'
        if rect:
            x,y,w,h=rect;style+=f'left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        attrs=f'id="{id}" data-visual-role="subject-media" src="{html.escape(src,quote=True)}" style="{style}"'
        if image:return '<img '+attrs+'>'
        start=finite(info.get('start',0),'media start');rate=finite(info.get('rate',1),'media rate')
        if start<0 or rate<=0:raise ValueError('Invalid foreground media timing')
        if 'end' in info and finite(info['end'],'media end')<start+self.duration*rate-.001:
            raise ValueError(key+': source range is too short; choose a longer shot.')
        grade=html.escape(json.dumps(info.get('grading',{})),quote=True)
        return f'<video {attrs} class="clip" data-start="0" data-duration="{self.duration}" data-media-start="{start}" data-playback-rate="{rate}" data-hf-media-start-basis="local" data-color-grading="{grade}" muted playsinline></video>'

    def dependencies(self,key):
        if self.kind=='map-route' and re.fullmatch(r'route[1-9]\d*',key):
            n=int(key[5:]);return ['pin'+str(n-1),'pin'+str(n)]
        pairs={'hero':{'question':['portrait','left','right']},
               'map-focus':{'ring':['place'],'zoom':['ring']},
               'relation':{'l1':['a','c'],'l2':['b','c'],'n1':['l1'],'n2':['l2']},
               'feedback':{'f1':['p0','p1'],'f2':['p1','p2'],'f3':['p2','p0'],'note':['f3']},
               'compare':{'line':['a','b'],'q':['a','b']},
               'context':{'widen':['a'],'b':['widen']}}
        return pairs.get(self.kind,{}).get(key,[])

    def motion(self,id,default,duration,relationship=False):
        key=self.key(id);self.used_cues.add(key)
        # Short scenes accelerate default reveals, not explicitly supplied cues.
        speed=min(1.,self.duration/8)
        at=finite(self.cues.get(key,default*speed),key);d=min(duration,self.duration/8*duration)
        deps=self.dependencies(key)
        if any(dep not in self.settles for dep in deps):raise ValueError('Missing motion anchor for '+key)
        earliest=max([0]+[self.settles[dep]+.04 for dep in deps])
        if key in self.cues and at<earliest-.001:raise ValueError(key+': cue precedes settled anchors '+', '.join(deps))
        at=max(at,earliest)
        if at+d>self.duration-.15:raise ValueError(key+': leave time for animation and a readable hold; extend duration or move cues.')
        self.settles[key]=at+d
        role='relationship' if relationship else 'conclusion' if key in ('q','question','note','b') and self.kind!='relation' else 'subject'
        self.order.append({'id':id,'role':role,'enter_at':round(at,4),'settle_at':round(at+d,4),'depends_on':[self.prefix+'-'+x for x in deps]})
        return at,d

    def finish(self,body,js):
        unknown=set(self.text)-self.used_text
        if unknown:raise ValueError('Unknown text slots: '+', '.join(sorted(unknown)))
        unknown=set(self.media_inputs)-self.used_media
        if unknown:raise ValueError('Unknown media slots: '+', '.join(sorted(unknown)))
        # Camera and quantitative changes are also explicit semantic phases.
        if self.kind=='quantity':
            at=float(self.cues.get('select',2.2*min(1,self.duration/8)));self.used_cues.add('select')
            if at<self.settles.get('total',0):raise ValueError('Reveal the whole count before selecting the subset.')
            # Replace original selection times, keeping source geometry and colors.
            for j,n in enumerate(self.config['selected']):
                old=2.2+j*min(.3,1.5/max(1,len(self.config['selected'])))
                when=at+j*min(.3,.8/max(1,len(self.config['selected'])))
                if when+.5>self.duration-.15:raise ValueError('Leave time to read selected counts.')
                js=js.replace(f'}},{old});',f'}},{when});')
            self.order.append({'id':self.prefix+'-select','role':'relationship','enter_at':at,'settle_at':at+1.3,'depends_on':[self.prefix+'-total']})
        unknown=set(self.cues)-self.used_cues
        if unknown:raise ValueError('Unknown cue keys: '+', '.join(sorted(unknown)))
        # Caption-safe, uniform scaling preserves the approved composition.
        x=(1920-1920*self.scale)/2
        return f'<div class="base-stage" style="position:absolute;inset:0;transform-origin:0 0;transform:translateX({x}px) scale({self.scale});width:1920px;height:1080px">{body}</div>',js
