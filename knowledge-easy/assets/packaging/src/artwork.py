"""Open-ended code illustration: drawing engines are reusable; scenes are authored."""
import html,json,math,re
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'artwork'
PROFILES=json.loads((ROOT/'profiles.json').read_text())
REFERENCE_FILES={x['reference']:key+'.svg' for key,x in PROFILES.items()}
REFERENCE_FILES.update({
    'art-reference-portrait':'reference-portrait.svg',
    'art-reference-balance':'reference-balance.svg',
    'art-reference-writing':'reference-writing.svg',
})
REFERENCES={key:str(ROOT.parent.parent/'illustrations'/name) for key,name in REFERENCE_FILES.items()}


def selected_reference(data,profile):
    if data.get('design_reference'):return data['design_reference']
    source=Path(data.get('source','')).name
    return next((key for key,name in REFERENCE_FILES.items() if name==source),profile.get('reference','art-'+profile['engine']))



def vector_source(prefix,duration,source,data,cues):
    """Reuse original SVG layers directly so the handbook and film share the same drawing source."""
    ET.register_namespace('','http://www.w3.org/2000/svg')
    root=ET.fromstring(source)
    if root.tag.split('}')[-1]!='svg':raise ValueError('The vector source must have an svg root element.')
    ids={};elements=list(root.iter())
    for el in elements:
        if el.tag.split('}')[-1] in ('script','foreignObject','image','animate','animateTransform','set'):
            raise ValueError('This interface accepts static vector layers; the component timeline controls their motion.')
        for key,value in el.attrib.items():
            if key.lower().startswith('on') or re.search(r'https?:|javascript:|data:',value,re.I):
                raise ValueError('SVG files must not contain scripts or external resources.')
        if el.get('id'):
            key=el.get('id')
            if key in ids or not re.fullmatch(r'[A-Za-z][\w-]*',key):raise ValueError('SVG layer IDs must be unique.')
            ids[key]=prefix+'-vector-'+key
    for el in elements:
        for key,value in list(el.attrib.items()):
            if key=='id':value=ids[value]
            else:
                value=re.sub(r'url\(#([\w-]+)\)',lambda m:'url(#'+ids.get(m[1],m[1])+')',value)
                if key.split('}')[-1]=='href' and value.startswith('#'):value='#'+ids.get(value[1:],value[1:])
            el.set(key,value)
    root.set('width','1920');root.set('height','1080');root.set('preserveAspectRatio','xMidYMid meet')
    root.set('style','position:absolute;inset:0;width:1920px;height:1080px')
    root.set('aria-label',data.get('description','Original vector illustration'))
    root.set('id',root.get('id',prefix+'-vector-root'))
    scripts=[];order=[{'id':root.get('id'),'role':'illustration','enter_at':0,'settle_at':0,'depends_on':[]}];used=set()
    for motion in data.get('motion',[]):
        key=motion['target'];kind=motion.get('type','fade')
        if key not in ids or key in used:raise ValueError('Each motion target must identify a unique SVG layer ID.')
        used.add(key);target=ids[key]
        at=float(cues.get(key,motion.get('at',0)));seconds=float(motion.get('duration',.6))
        if not all(math.isfinite(v) for v in (at,seconds)) or at<0 or seconds<=0 or at+seconds>duration:raise ValueError('SVG motion extends beyond the clip.')
        if kind=='draw':
            scripts.append(f"{{const p=document.getElementById('{target}');if(typeof p.getTotalLength!=='function')throw new Error('The draw-on target must be a path');const n=p.getTotalLength();p.style.strokeDasharray=n;tl.fromTo(p,{{strokeDashoffset:n}},{{strokeDashoffset:0,duration:{seconds},ease:'sine.inOut'}},{at});}}")
        else:
            before=motion.get('from',{'opacity':0});after=motion.get('to',{'opacity':1})
            allowed={'x','y','scale','rotation','opacity'}
            for state in (before,after):
                if not isinstance(state,dict) or set(state)-allowed or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in state.values()):raise ValueError('SVG motion transforms must use finite numeric values.')
            if kind not in ('fade','move'):raise ValueError('SVG motion supports fade, draw, or move.')
            scripts.append(f"tl.set('#{target}',{{transformOrigin:'50% 50%'}},0);tl.fromTo('#{target}',{json.dumps(before)},{json.dumps(dict(after,duration=seconds,ease='sine.inOut'))},{at});")
        order.append({'id':target,'role':'illustration-detail','enter_at':at,'settle_at':at+seconds,'depends_on':[]})
    return ET.tostring(root,encoding='unicode'),''.join(scripts),order


def render(prefix,duration,data,cues,locale):
    source=data.get('_source_code')
    if not source:raise ValueError('artwork needs a project-owned drawing source; use data.source through build.')
    if re.search(r'</script',source,re.I):raise ValueError('Drawing source may not close the composition script.')
    profile=data.get('style','etch')
    if isinstance(profile,str):
        if profile not in PROFILES:raise ValueError('Choose a bundled artwork style or supply an engine/palette object.')
        profile=dict(PROFILES[profile])
    else:
        profile=dict(profile)
        if profile.get('engine') not in ('etch','print','wash'):raise ValueError('Custom artwork style needs an available engine.')
    canvas=prefix+'-canvas';order=[]
    is_svg=str(data.get('source','')).lower().endswith('.svg')
    if is_svg:body,vector_js,order=vector_source(prefix,duration,source,data,cues)
    else:body=f'<canvas id="{canvas}" width="1920" height="1080" style="position:absolute;inset:0;width:1920px;height:1080px" aria-label="{html.escape(data.get("description","Original illustration"),quote=True)}"></canvas>'
    scripts=[]
    for i,label in enumerate(data.get('labels',[])):
        key=label.get('id','label'+str(i));id=prefix+'-'+key
        if not re.fullmatch(r'[A-Za-z][\w-]*',key):raise ValueError('Invalid artwork label id')
        x,y,w=label['x'],label['y'],label['width'];size=label.get('size',64)
        if not all(math.isfinite(float(v)) for v in (x,y,w,size)):raise ValueError('Label bounds must be finite')
        if min(x,y)<0 or x+w>1920 or y+size*1.4>900:raise ValueError('Place reading text above the caption reserve.')
        at=float(cues.get(key,label.get('at',.2)));end=float(label.get('end',duration))
        if not 0<=at<end<=duration:raise ValueError('Invalid artwork label timing')
        color=label.get('color',profile.get('palette',{}).get('ink','#18272d'))
        text=html.escape(label['text']).replace('\n','<br>')
        face='PackSans' if label.get('font','sans')=='sans' else 'PackSerif'
        body+=f'<div id="{id}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font:{label.get("weight",600)} {size}px/1.3 {face};color:{color};text-align:{label.get("align","left")}">{text}</div>'
        enter_duration=min(.42,(end-at)*.65)
        scripts.append(f"tl.fromTo('#{id}',{{opacity:0,y:6}},{{opacity:1,y:0,duration:{enter_duration},ease:'power2.out'}},{at});")
        if end<duration:
            exit_duration=min(.18,(end-at)*.25)
            scripts.append(f"tl.to('#{id}',{{opacity:0,duration:{exit_duration}}},{end-exit_duration});")
        order.append({'id':id,'role':'label','enter_at':at,'settle_at':at+enter_duration,'depends_on':[]})
    if is_svg:
        return {'html':body,'js':vector_js+''.join(scripts),'reading_order':order,
                'component':'artwork','parent':'original-art','implementation':'authored-artwork',
                'design_reference':selected_reference(data,profile),
                'layout':{'source':data.get('source'),'engine':'svg','editable_layers':True}}
    # Code is isolated per instance. Time comes only from the seekable parent timeline.
    helpers=(ROOT/'runtime.js').read_text()
    config=json.dumps(data.get('configuration',{}),ensure_ascii=False)
    script='{'+helpers+f'\nconst canvas=document.getElementById({json.dumps(canvas)});const art=createArtwork(canvas,{json.dumps(profile)});const data={config};const clock={{t:0}};\nfunction drawScene(t){{const ctx=art.ctx;art.clear();\n'+source+'\n}\nfunction paint(){drawScene(clock.t);art.finish();}\npaint();'+f'tl.to(clock,{{t:{duration},duration:{duration},ease:"none",onUpdate:paint}},0);'+'}\n'+''.join(scripts)
    order.insert(0,{'id':canvas,'role':'illustration','enter_at':0,'settle_at':0,'depends_on':[]})
    return {'html':body,'js':script,'reading_order':order,'component':'artwork','parent':'original-art','implementation':'authored-artwork','design_reference':selected_reference(data,profile),'layout':{'source':data.get('source'),'engine':profile['engine']}}
