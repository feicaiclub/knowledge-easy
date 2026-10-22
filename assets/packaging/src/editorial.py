# -*- coding: utf-8 -*-
"""Shared, content-configured editorial components used by films and the handbook.

No episode copy, timecode, actor or media filename belongs in this module.
The caller provides content and semantic cue times in local seconds.
"""
from pathlib import Path
import html, json, math, importlib.util, re

ROOT = Path(__file__).resolve().parent
VERSION = '1.2.0'
E = html.escape
FAMILIES = {
    'map-decision': 'map-route', 'map-focus-chain': 'map-focus',
    'evidence-sheet': 'evidence', 'credential': 'evidence',
    'relation-bridge': 'relation', 'foundation': 'relation',
    'name-roster': 'relation', 'concept-link': 'compare',
    'quote-reveal': 'evidence', 'milestone-pair': 'timeline',
    'portrait-question': 'hero', 'annotation': 'typography',
    'dateline': 'typography', 'concept-stack': 'compare',
    'declaration': 'compare',
}

def css(asset_prefix='../assets/fonts/', locale='en-US'):
    base = (ROOT/'pack.css').read_text()
    # Catalog CSS may also style a standalone page. In a mounted component,
    # a body background would become an opaque full-frame layer (including
    # captions), so only reusable visual classes enter the composition.
    base = re.sub(r'html,body\{[^}]*\}|(?<![-\w])body\{[^}]*\}', '', base)
    base = base.replace('../fonts/', asset_prefix)
    styles=base + '\n' + (ROOT/'editorial.css').read_text()
    if locale=='en-US':
        styles=styles.replace('notoserifsc-NotoSerifSC[wght].ttf','source-serif-4.ttf').replace('notosanssc-NotoSansSC[wght].ttf','inter.ttf')
        styles+='\n'+(ROOT/'english.css').read_text()
    return styles

def geography(prefix, view, w=1680, h=678):
    """Same map implementation and source data as the original catalog."""
    spec = importlib.util.spec_from_file_location('editorial_geo', ROOT/'geography.py')
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod.map_base(prefix, view, w, h, ROOT/'maps')

class Component:
    def __init__(self, kind, prefix, duration, data, cues, locale='en-US'):
        assert kind in FAMILIES
        assert duration >= .6
        self.kind,self.p,self.duration,self.data,self.cues = kind,prefix,duration,data,cues
        self.locale=locale
        self.body=[];self.js=[];self.order=[];self.starts={}

    def id(self,key):return self.p+'-'+key
    def cue(self,key,default=.1):
        return round(max(0,min(self.duration-.36,float(self.cues.get(key,default)))),4)

    def enter(self,key,when=None,role='evidence',deps=(),axis='y',distance=24,duration=.48):
        at=self.cue(key) if when is None else max(0,float(when))
        if deps:at=max(at,max(self.starts[x]+.24 for x in deps))
        assert at < self.duration-.20,(self.kind,key,at,self.duration)
        duration=min(duration,self.duration-at-.10)
        self.js.append(f"tl.fromTo('#{self.id(key)}',{{opacity:0,{axis}:{distance}}},{{opacity:1,{axis}:0,duration:{duration:.4f},ease:'power3.out'}},{at:.4f});")
        self.starts[key]=at
        self.order.append({'id':self.id(key),'role':role,'enter_at':round(at,4),'settle_at':round(at+duration,4),'depends_on':[self.id(x) for x in deps]})
        return at

    def draw(self,key,at,deps=(),duration=.65):
        if deps:at=max(at,max(self.starts[x]+.28 for x in deps))
        duration=min(duration,self.duration-at-.15)
        assert duration>.05,(key,at,self.duration)
        self.js.append(f"{{const el=document.getElementById('{self.id(key)}'),n=el.getTotalLength();el.style.strokeDasharray=n;tl.fromTo(el,{{strokeDashoffset:n,opacity:0}},{{strokeDashoffset:0,opacity:1,duration:{duration:.4f},ease:'power2.inOut'}},{at:.4f});}}")
        self.starts[key]=at
        self.order.append({'id':self.id(key),'role':'relationship','enter_at':round(at,4),'settle_at':round(at+duration,4),'depends_on':[self.id(x) for x in deps]})

    def text(self,key,text,x,y,w,size=64,color=None,role='ev-title',align='left'):
        assert isinstance(text,str) and len(text)<=(180 if self.locale=='en-US' else 65),(key,'Shorten the label.')
        lines=text.split('\n')
        for line in lines:
            advance=sum(1 if ord(c)>255 else .56 for c in line)*size+max(0,len(line)-1)*2
            assert advance<=w+12,(self.kind,key,text,'Text does not fit',advance,w)
        content=''.join(f'<div>{E(line)}</div>' for line in lines)
        return f'<div id="{self.id(key)}" class="{role}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;text-align:{align};'+(f'color:{color};' if color else '')+f'">{content}</div>'

    def image(self,key,src,x,y,w,h,label='',focus='50% 32%'):
        info=src if isinstance(src,dict) else {'src':src,'type':'image'}
        assert info['src'] and not info['src'].startswith(('http:','https:'))
        focus=info.get('focus',focus)
        style=f'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{focus}'
        if info.get('type')=='video':
            start=info.get('start',0);available=info.get('end',start+self.duration)-start
            rate=min(1.,available/self.duration-.001);assert rate>=.6,('Choose a longer shot for',key)
            grade=E(json.dumps({'adjust':{'exposure':.12,'shadows':.08,'saturation':-.08,'contrast':.025,'temperature':.012}}),quote=True)
            media=f'<video id="{self.id(key+"-media")}" class="clip" src="{E(info["src"])}" data-start="0" data-duration="{self.duration}" data-media-start="{start}" data-playback-rate="{rate:.6f}" data-hf-media-start-basis="local" data-color-grading="{grade}" muted playsinline style="{style}"></video>'
        else:media=f'<img src="{E(info["src"])}" style="{style}">'
        return f'<div id="{self.id(key)}" class="ev-photo" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'+media+(f'<div class="ev-photo-caption">{E(label)}</div>' if label else '')+'</div>'

    def svg(self,body):return f'<svg class="ev-svg" viewBox="0 0 1920 1080">{body}</svg>'
    def path(self,key,path,color='#d8b676',width=3):return f'<path id="{self.id(key)}" d="{path}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="butt" stroke-linejoin="round"/>'

    def render(self):
        d=self.data;p=self.p;k=self.kind
        if k in ['map-decision','map-focus-chain']:
            self.map()
        elif k=='annotation':
            place=d.get('placement','lower-left');x,y,w={'lower-left':(150,620,1380),'lower-right':(1110,650,660),'upper-left':(150,165,1500)}[place]
            self.body += [self.text('title',d['title'],x,y,w,d.get('size',90),d.get('color'))]
            self.enter('title',role='subject',distance=18,duration=.36)
            if d.get('note'):
                self.body += [self.text('note',d['note'],x+4,y+138,w,32,'#d8b676','ev-sans')]
                self.enter('note',self.cue('note',.26),role='supporting_label')
        elif k=='dateline':
            self.body += [f'<div id="{self.id("stamp")}" class="ev-dateline"><b>{E(str(d["date"]))}</b><span>{E(d["label"])}</span></div>']
            self.enter('stamp',.05,role='supporting_label',distance=12,duration=.32)
        elif k=='declaration':
            self.body += [self.text('context',d['context'],150,190,1050,78),self.text('condition',d['condition'],155,325,1000,64,'#d8b676'),self.text('decision',d['decision'],150,535,1280,132)]
            self.enter('context',self.cue('context',.05),role='subject');self.enter('condition',self.cue('condition',.38),role='evidence');self.enter('decision',self.cue('decision',1.2),role='conclusion',distance=30,duration=.32)
        elif k=='portrait-question':
            self.body += [self.image('portrait',d['image'],230,155,555,650),self.text('lead',d['lead'],930,285,810,74),self.text('question',d['question'],930,425,830,91,'#d8b676')]
            self.enter('portrait',.0,role='subject',axis='x',distance=-28,duration=.36)
            self.enter('lead',.08,role='evidence',distance=18,duration=.32)
            self.enter('question',self.cue('question',.3),role='conclusion',distance=18,duration=.36)
        elif k=='name-roster':
            names=d['items'];assert 1<=len(names)<=3
            ending=d.get('layout')=='closing'
            if ending:
                self.body += [self.text('date',str(d['date']),150,150,650,138,'#d8b676','ev-number'),self.text('title',d['title'],150,320,750,76),self.text('subtitle',d['subtitle'],155,470,650,34,'#d8b676','ev-sans')]
                self.enter('date',.05,role='subject');self.enter('title',.22,role='subject');self.enter('subtitle',self.cue('subtitle',.55),role='supporting_label')
                x,w=1050,680
            else:
                self.body += [self.image('portrait',d['image'],215,160,590,660,d.get('subject','')),self.text('title',d['title'],950,160,790,76)]
                self.enter('portrait',.0,role='subject',axis='x',distance=-28,duration=.36);self.enter('title',.06,role='subject',duration=.34)
                x,w=950,790
            top=340 if not ending else 360
            compact=len(names)==3
            height=156 if compact else 182
            row_gap=20 if compact else 28
            for i,item in enumerate(names):
                key=f'item{i}';y=top+i*(height+row_gap)
                number=self.text(key+'-number',f'{i+1:02d}',30,30,88,67,'#9a7949','ev-number')
                name=self.text(key+'-name',item['name'],140,22 if compact else 26,w-170,56 if compact else 66,'#243a38')
                note=self.text(key+'-note',item.get('note',''),145,106 if compact else 119,w-175,24 if compact else 27,'#54675e','ev-sans')
                separator='<div style="position:absolute;left:118px;top:30px;width:1px;height:72px;background:#b6ab90"></div>'
                self.body += [f'<div id="{self.id(key)}" class="ev-record" style="left:{x}px;top:{y}px;width:{w}px;height:{height}px">{number}{separator}{name}{note}</div>']
                at=self.cue(key,.16+i*.22)
                if i:at=max(at,self.starts[f'item{i-1}']+.2)
                read_time=max(.6,len(item['name'].split())/3) if self.locale=='en-US' else .16*len(item['name'])
                assert at+.38+.35+read_time<=self.duration,(key,'Leave time to read the roster item.')
                self.enter(key,at,axis='x',distance=42,duration=.38)
        elif k=='credential':
            self.body += [self.image('portrait',d['image'],190,180,590,620,d['person']),f'<div id="{self.id("paper")}" class="ev-paper" style="left:930px;top:180px;width:800px;height:620px"></div>']
            self.body += [self.text('issuer',d['issuer'],990,220,670,31,'#785d36','ev-sans'),self.text('role',d['role'],990,290,670,104,'#243a38')]
            self.enter('portrait',.0,role='subject',axis='x',distance=-45);self.enter('paper',.1,axis='x',distance=45);self.enter('issuer',.25,role='supporting_label');self.enter('role',.38,role='subject')
            for i,item in enumerate(d['details']):
                self.body += [self.text(f'detail{i}',item,995,505+i*124,650,41,'#243a38','ev-sans')]
                self.enter(f'detail{i}',self.cue(f'detail{i}',1.2+i*1.4),role='evidence',distance=16)
        elif k=='evidence-sheet':
            self.body += [self.image('image',d['image'],155,180,800,620,d.get('image_label','')),f'<div id="{self.id("paper")}" class="ev-paper" style="left:1080px;top:180px;width:650px;height:620px"></div>']
            self.body += [self.text('kicker',d.get('kicker',''),1140,220,540,30,'#785d36','ev-sans'),self.text('title',d['title'],1140,300,540,64,'#243a38')]
            self.enter('image',.0,role='subject',axis='x',distance=-45);self.enter('paper',.16,axis='x',distance=45);self.enter('kicker',.28,role='supporting_label');self.enter('title',.4,role='subject')
            if d.get('body'):
                self.body += [self.text('body',d['body'],1140,510,540,43,'#243a38','ev-sans')];self.enter('body',self.cue('body',1.0))
            if d.get('closing'):
                self.body += [self.text('closing',d['closing'],1140,670,540,48,'#785d36')];self.enter('closing',self.cue('closing',1.8),role='conclusion')
        elif k=='relation-bridge':
            nodes=d['nodes'];assert len(nodes)==2
            if d.get('title'):
                self.body += [self.text('title',d['title'],220,90,1480,70,align='center')];self.enter('title',.12,role='subject')
            for i,n in enumerate(nodes):
                x=180 if i==0 else 1190
                self.body += [self.image(f'node{i}',n['image'],x,225,550,390,n['name'])]
                self.enter(f'node{i}',self.cue(f'node{i}',.1+i*.28),role='subject',axis='x',distance=(-35 if i==0 else 35))
                if n.get('sub'):
                    self.body += [self.text(f'sub{i}',n['sub'],x,675,550,47,align='center')]
                    self.enter(f'sub{i}',self.cue(f'sub{i}',1+i*.6),role='evidence')
            if any(n.get('sub') for n in nodes):
                widths=[sum(1 if ord(ch)>255 else .56 for ch in n.get('sub',''))*47+max(0,len(n.get('sub',''))-1)*2 for n in nodes]
                left=455+widths[0]/2+28;right=1465-widths[1]/2-28
                bridge=f'M455 635 V655 M1465 635 V655 M{left} 710 H{right}'
            else:bridge='M760 435 H1160'
            self.body += [self.svg(self.path('bridge',bridge)),self.text('relation',d['relation'],765,630 if any(n.get('sub') for n in nodes) else 345,390,38,'#d8b676','ev-sans','center')]
            deps=['sub0','sub1'] if all(n.get('sub') for n in nodes) else ['node0','node1']
            at=max(self.cue('relation',2.0),max(self.starts[x] for x in deps)+.32)
            self.draw('bridge',at,deps);self.enter('relation',at+.1,role='relationship',distance=12,duration=.35)
        elif k=='foundation':
            items=d['items'];assert 2<=len(items)<=4
            self.body += [self.text('title',d['title'],190,135,1540,83),self.text('note',d['note'],195,265,1500,35,'#d8b676','ev-sans')]
            self.enter('title',.05,role='subject');self.enter('note',.2,role='supporting_label')
            width=350;gap=(1540-len(items)*width)/(len(items)-1);centers=[]
            for i,item in enumerate(items):
                x=190+i*(width+gap);centers.append(x+width/2);key=f'node{i}'
                self.body += [f'<div id="{self.id(key)}" style="position:absolute;left:{x}px;top:420px;width:{width}px;height:280px"><svg viewBox="0 0 390 180" style="width:350px;height:162px"><path d="M36 172 V55 H60 V28 H90 V55 H120 V28 H150 V55 H240 V28 H270 V55 H300 V28 H330 V55 H354 V172 H239 V124 Q239 82 195 82 Q151 82 151 124 V172 Z" fill="#efe4ce"/><path d="M55 70 H335" stroke="#d8b676" stroke-width="3"/></svg><div class="ev-node-name">{E(item)}</div></div>']
                self.enter(key,self.cue(key,.7+i*.18),role='evidence',distance=40)
            dep=[f'node{i}' for i in range(len(items))]
            path=f'M{centers[0]} 704 V750 H{centers[-1]} V704'+''.join(f'M{x} 704 V750' for x in centers[1:-1])+' M960 750 V790'
            self.body += [self.svg(self.path('group',path)),self.text('conclusion',d['conclusion'],530,810,860,52,align='center')]
            at=max(self.cue('conclusion',2.0)-.35,max(self.starts[x] for x in dep)+.28);self.draw('group',at,dep,.42);self.enter('conclusion',at+.35,role='conclusion',distance=16,duration=.38)
        elif k=='concept-link':
            items=d['items'];assert len(items)==2
            for i,item in enumerate(items):
                x=220+i*960;self.body += [self.text(f'node{i}',item,x,285,520,120,'#d8b676' if i else None,align='center')]
                self.enter(f'node{i}',self.cue(f'node{i}',.1+i*.45),role='subject',axis='x',distance=(-35 if i==0 else 35))
            self.body += [self.svg(self.path('connection','M480 490 V580 H1440 V490 M960 580 V650')),self.text('conclusion',d['conclusion'],460,700,1000,83,align='center')]
            at=max(self.cue('conclusion',1.6)-.5,self.starts['node1']+.3);self.draw('connection',at,['node0','node1'],.5);self.enter('conclusion',at+.45,role='conclusion',distance=18,duration=.4)
        elif k=='quote-reveal':
            self.body += [f'<div id="{self.id("paper")}" class="ev-paper ev-quote-paper"></div>',self.text('mark','“',255,175,220,210,'#b99b68'),self.text('lead',d['lead'],420,305,1190,66,'#243a38'),self.text('emphasis',d['emphasis'],420,485,1190,112,'#243a38')]
            self.enter('paper',.0,role='evidence',distance=20,duration=.4);self.enter('mark',.06,role='supporting_label',distance=0);self.enter('lead',self.cue('lead',.16),role='evidence');self.enter('emphasis',self.cue('emphasis',1.2),role='conclusion',distance=20)
        elif k=='milestone-pair':
            items=d['items'];assert len(items)==2
            for i,n in enumerate(items):
                x=160+960*i;key=f'panel{i}'
                self.body += [f'<div id="{self.id(key)}" class="ev-milestone" style="left:{x}px"><div class="ev-milestone-date">{E(str(n["date"]))}</div><div class="ev-milestone-context">{E(n["context"])}</div><div class="ev-milestone-statement">{E(n["statement"])}</div></div>']
                self.enter(key,self.cue(key,.05+i*2.2),role='evidence',axis='x',distance=(-30 if i==0 else 30))
            self.body += [self.svg(self.path('axis','M220 740 H1700',width=2))]
            self.draw('axis',self.cue('axis',2.9),['panel0','panel1'],.7)
        elif k=='concept-stack':
            self.body += [self.text('title',d['title'],150,170,1540,86)]
            self.enter('title',.04,role='subject')
            if d.get('note'):
                self.body += [self.text('note',d['note'],155,310,1500,39,'#d8b676','ev-sans')];self.enter('note',.28,role='supporting_label')
            items=d['items'];assert 1<=len(items)<=3
            width=490;gap=(1620-width*len(items))/max(1,len(items)-1)
            for i,item in enumerate(items):
                x=150+i*(width+gap);key=f'item{i}'
                self.body += [self.text(key,item,x,565,width,57),f'<div id="{self.id(key+"-rule")}" class="ev-hairline" style="left:{x}px;top:690px;width:{width}px"></div>']
                at=self.cue(key,.5+i*.4);self.enter(key,at);self.enter(key+'-rule',at+.1,distance=0)
        else:raise ValueError(k)
        return {
            'html':'<div class="ev-component" data-editorial-component="'+k+'" data-editorial-version="'+VERSION+'">'+''.join(self.body)+'</div>',
            'js':''.join(self.js), 'reading_order':self.order,
            'component':k,'parent':FAMILIES[k],'version':VERSION,'locale':self.locale,
        }

    def map(self):
        d=self.data;p=self.p;points=d['points'];assert 2<=len(points)<=4
        base,xy=geography(p,tuple(d.get('view',[105,29,124,42])))
        marks='';first=self.cue('point0',.3)
        for i,n in enumerate(points):
            x,y=xy(n['lon'],n['lat']);side=n.get('side','right');dx=-40 if side=='left' else 40;anchor='end' if side=='left' else 'start';dy=n.get('label_dy',-18)
            label=f'<text x="{x+dx:.2f}" y="{y+dy:.2f}" text-anchor="{anchor}" class="ev-map-place">{E(n["name"])}</text>'
            marks+=f'<g id="{self.id(f"point{i}")}"><circle cx="{x}" cy="{y}" r="9" fill="#874a47"/><circle cx="{x}" cy="{y}" r="19" fill="none" stroke="#874a47" stroke-width="2"/>{label}</g>'
            self.enter(f'point{i}',self.cue(f'point{i}',.3+i*.7),role='subject',distance=0,duration=.42)
        route=''
        if self.kind=='map-decision':
            x0,y0=xy(points[0]['lon'],points[0]['lat']);x1,y1=xy(points[1]['lon'],points[1]['lat'])
            dist=math.hypot(x1-x0,y1-y0);assert dist>70,'Map view is too broad to explain this short direction; choose a closer view.'
            ux,uy=(x1-x0)/dist,(y1-y0)/dist
            sx,sy=x0+ux*24,y0+uy*24;ex,ey=x1-ux*24,y1-uy*24
            bend=min(52,dist*.22);cx,cy=(sx+ex)/2-uy*bend,(sy+ey)/2+ux*bend
            path=f'M{sx:.2f} {sy:.2f} Q{cx:.2f} {cy:.2f} {ex:.2f} {ey:.2f}'
            norm=math.hypot(ex-cx,ey-cy);tx,ty=(ex-cx)/norm,(ey-cy)/norm
            ax,ay=ex-tx*15-ty*9,ey-ty*15+tx*9;bx,by=ex-tx*15+ty*9,ey-ty*15-tx*9
            route=f'<defs><mask id="{self.id("route-reveal")}" maskUnits="userSpaceOnUse" x="0" y="0" width="1680" height="678"><path id="{self.id("route-draw")}" d="{path}" fill="none" stroke="white" stroke-width="14"/></mask></defs><path d="{path}" class="ev-map-route" stroke-dasharray="9 6" mask="url(#{self.id("route-reveal")})"/>'
            route+=f'<path id="{self.id("arrow")}" d="M{ax:.2f} {ay:.2f} L{ex:.2f} {ey:.2f} L{bx:.2f} {by:.2f}" fill="none" stroke="#874a47" stroke-width="3"/>'
            at=max(self.cue('route',1.5),self.starts['point1']+.28);self.draw('route-draw',at,['point0','point1'],.85);self.enter('arrow',at+.7,role='relationship',distance=0,duration=.15)
        else:
            for i,n in enumerate(points):
                x,y=xy(n['lon'],n['lat']);key=f'focus{i}'
                route+=f'<circle id="{self.id(key)}" cx="{x}" cy="{y}" r="53" class="ev-focus-ring"/>'
                self.enter(key,self.cue(f'focus{i}',1+i*2.3),role='evidence',distance=0,duration=.65)
        self.body += [self.text('title',d['title'],160,85,1600,68),f'<div id="{self.id("atlas")}" class="ev-atlas"><svg class="kp-map" viewBox="0 0 1680 678"><g id="{self.id("camera")}">{base}{route}{marks}</g></svg><div class="ev-map-caption">{E(d.get("map_note",""))}</div></div>']
        self.enter('atlas',.0,role='subject',distance=22,duration=.6);self.enter('title',.10,role='subject',distance=18)
        # All geographic layers, points and paths share exactly the same transform.
        focus=d.get('focus',{'lon':sum(n['lon'] for n in points)/len(points),'lat':sum(n['lat'] for n in points)/len(points)})
        fx,fy=xy(focus['lon'],focus['lat']);zoom=float(d.get('zoom',1.35));assert 1<=zoom<=2
        self.js += [f"tl.fromTo('#{self.id('camera')}',{{scale:1,svgOrigin:'{fx:.3f} {fy:.3f}'}},{{scale:{zoom},svgOrigin:'{fx:.3f} {fy:.3f}',duration:1.5,ease:'power2.inOut'}},{self.cue('zoom',.35)});"]
        stages=d.get('stages',[])
        # A note may use a small set of designed slots; it must not cover a
        # geographic name at either end of the camera move. One slot is held
        # for every stage so replacing the message never jumps the layout.
        label_boxes=[]
        for n in points:
            px,py=xy(n['lon'],n['lat']);left=n.get('side','right')=='left';dx=-40 if left else 40;dy=n.get('label_dy',-18)
            for z in [1,zoom]:
                lx=120+fx+(px+dx-fx)*z;ly=190+fy+(py+dy-fy)*z;lw=len(n['name'])*34*z
                label_boxes.append((lx-lw if left else lx,ly-39*z,lw,47*z))
        def overlaps(a,b):return a[0]<b[0]+b[2]+28 and a[0]+a[2]+28>b[0] and a[1]<b[1]+b[3]+28 and a[1]+a[3]+28>b[1]
        slots=[(1195,395,565,310),(1195,510,565,310),(150,510,565,310),(150,220,565,310)]
        clear=[slot for slot in slots if not any(overlaps(slot,box) for box in label_boxes)]
        assert clear or not stages,'No clear map-note slot; change the viewport or shorten place labels.'
        slot=clear[0] if clear else slots[0]
        for i,s in enumerate(stages):
            key=f'callout{i}';at=self.cue(key,.7+i*2.6);x,y,w,h=slot
            body=f'<div class="ev-map-note-label">{E(s["label"])}</div><div class="ev-map-note-title">{E(s["text"]).replace(chr(10),"<br>")}</div>'
            if s.get('small'):body+=f'<div class="ev-map-note-small">{E(s["small"])}</div>'
            self.body += [f'<div id="{self.id(key)}" class="ev-map-note" style="left:{x}px;top:{y}px;width:{w}px;min-height:{h}px">{body}</div>']
            self.enter(key,at,role='conclusion' if i else 'evidence',axis='x',distance=38,duration=.45)
            if i<len(stages)-1:
                end=self.cue(f'callout{i+1}',.7+(i+1)*2.6)
                self.js += [f"tl.to('#{self.id(key)}',{{opacity:0,x:-20,duration:.18,ease:'power2.in'}},{max(at+.45,end-.19):.4f});"]

def render(kind,prefix,duration,data,cues=None,locale='en-US'):
    if locale not in ['en-US','zh-CN']:raise ValueError('Use en-US or zh-CN for component layouts.')
    return Component(kind,prefix,duration,data,cues or {},locale).render()
