"""Editable cinematic titles, medallion relationship graphics, and editorial portrait layouts."""
import html,json,math
E=html.escape
IDS={'lit-title':'hero','medallion-labels':'relation','editorial-portrait':'hero'}

def render(kind,prefix,duration,data,cues,locale):
    if locale!='zh-CN':raise ValueError('These layouts currently support Chinese only.')
    out=[];moves=[];order=[];settles={}
    def identity(key):return prefix+'-'+key
    def enter(key,at,role='label',deps=(),dy=12,span=.65):
        proposed=float(cues.get(key,at));earliest=max([0]+[settles[d]+.04 for d in deps])
        if key in cues and proposed<earliest:raise ValueError(key+' enters before its prerequisite has settled.')
        at=max(proposed,earliest);span=min(span,duration-at-.12)
        if span<=0:raise ValueError('Allow enough time for the title to appear and be read.')
        moves.append(f"tl.fromTo('#{identity(key)}',{{opacity:0,y:{dy}}},{{opacity:1,y:0,duration:{span},ease:'power3.out'}},{at});")
        settles[key]=at+span
        order.append({'id':identity(key),'role':role,'enter_at':at,'settle_at':at+span,'depends_on':[identity(k) for k in deps]})
    def image(key,info,x=0,y=0,w=1920,h=1080):
        if isinstance(info,str):info={'src':info}
        fit=info.get('fit','cover')
        if fit not in ('cover','contain'):raise ValueError('Image fit must be cover or contain.')
        grade=E(json.dumps(info.get('grading',{}),ensure_ascii=False,separators=(',',':')),quote=True)
        src=E(info['src'],quote=True)
        style=f'position:absolute;inset:0;width:100%;height:100%;object-fit:{fit};object-position:{E(info.get("focus","50% 50%"),quote=True)}'
        if info.get('type')=='video' or src.lower().endswith(('.mp4','.mov','.webm')):
            media=f'<video id="{identity(key+"-media")}" class="clip" src="{src}" data-color-grading="{grade}" muted playsinline data-start="0" data-duration="{duration}" data-media-start="{float(info.get("start",0))}" data-playback-rate="1" style="{style}"></video>'
        else:media=f'<img id="{identity(key+"-media")}" src="{src}" style="{style}">'
        return f'<div id="{identity(key)}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;overflow:hidden">'+media+'</div>'
    def glyphs(text):
        return ''.join('<span class="ke-metal-word">'+''.join('<i class="ke-glyph" data-copy="'+E(ch,quote=True)+'"><b>'+E(ch)+'</b></i>' for ch in line)+'</span>' for line in text.split('\n'))
    def metal(key,text,x,y,w,size,align='center'):
        if not isinstance(text,str) or not text.strip():raise ValueError('The title cannot be empty.')
        count=max(sum(1 if ord(c)>255 else .55 for c in line) for line in text.split('\n'))
        size=min(float(size),w/max(1,count*1.14))
        if size<40:raise ValueError('The text is too long. Revise the title or layout.')
        return f'<div id="{identity(key)}" class="ke-metal" data-copy="{E(text,quote=True)}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;text-align:{align}">{glyphs(text)}</div>'
    def label(key,text,x,y,w,size=34,color='#eee7d5',align='center',serif=False,weight=None):
        tracking='.05em' if serif else '.015em'
        return f'<div id="{identity(key)}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;color:{color};font:{weight or (500 if serif else 450)} {size}px/1.5 {"PackSerif" if serif else "PackSans"};letter-spacing:{tracking};text-align:{align}">{E(text).replace(chr(10),"<br>")}</div>'
    if kind=='lit-title':
        out += [image('image',data['image']),'<div class="ke-cinema-vignette"></div>']
        out += [metal('left',data['left'],40,405,520,216),metal('right',data['right'],1360,405,520,216)]
        if data.get('caption'):out.append(label('caption',data['caption'],390,875,1140,38))
        enter('image',0,'subject',dy=0,span=.4);enter('left',.45,'subject',('image',),dy=6,span=.8);enter('right',1.35,'conclusion',('left',),dy=6,span=.8)
        if data.get('caption'):enter('caption',3.1,'explanation',('right',),dy=8)
        moves.append(f"tl.fromTo('#{identity('image')}',{{scale:1.025}},{{scale:1,duration:{duration},ease:'sine.inOut'}},0);")
    elif kind=='medallion-labels':
        labels=data['labels']
        if not 2<=len(labels)<=4:raise ValueError('Medallion relationships require 2–4 clearly defined subjects.')
        # Render the background with the shared backdrop, outside the foreground animation container.
        if data.get('title'):out.append(label('title',data['title'],160,110,1600,58,serif=True));enter('title',.12,'subject')
        gap=1480/(len(labels)-1);centers=[]
        for i,item in enumerate(labels):
            x=220+i*gap;key='label'+str(i);centers.append(x)
            out.append(f'<div id="{identity(key)}" style="position:absolute;left:{x-132}px;top:470px;width:264px;height:264px;border-radius:50%;background:radial-gradient(circle at 30% 20%,#5b747acc,#1c303dd9);border:1.5px solid #e8d6a6;box-shadow:inset 0 0 0 8px #182a3455,inset 0 0 0 9px #e3c68e40,0 16px 40px #0005">'+f'<div class="ke-metal" data-copy="{E(item,quote=True)}" style="left:22px;top:70px;width:220px;font-size:{min(58,192/max(1,len(item)))}px;text-align:center">{glyphs(item)}</div><div style="position:absolute;left:76px;top:170px;width:112px;height:1px;background:#c9b68188"></div></div>')
            enter(key,.6+i*.8,'relationship',dy=14)
        if data.get('caption'):out.append(label('caption',data['caption'],360,855,1200,38));enter('caption',3.7,'conclusion',tuple('label'+str(i) for i in range(len(labels))))
    else:
        out.append('<div style="position:absolute;inset:0;background:#f7f5ec"></div>')
        out.append(image('image',data['image'],440,0,1480,1080))
        out.append(f'<div style="position:absolute;left:130px;top:185px;width:64px;height:8px;background:{E(data.get("accent","#1764df"),quote=True)}"></div>')
        out.append(label('title',data['title'],130,245,710,94,'#202426','left',False,700))
        if data.get('caption'):out.append(label('caption',data['caption'],136,680,580,36,'#46535c','left'))
        enter('image',0,'subject',dy=0,span=.6);enter('title',.55,'subject',('image',),dy=14)
        if data.get('caption'):enter('caption',2.1,'explanation',('title',),dy=8)
    return {'html':'<div class="ev-component">'+''.join(out)+'</div>','js':''.join(moves),'reading_order':order,'component':kind,'parent':IDS[kind], 'implementation':'library-variant','design_reference':IDS[kind],'layout':{'family':'type-and-image','material':'layered-type' if kind!='editorial-portrait' else 'print'}}
