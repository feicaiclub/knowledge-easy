"""Open-ended code illustration: drawing engines are reusable; scenes are authored."""
import html,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'artwork'
PROFILES=json.loads((ROOT/'profiles.json').read_text())
REFERENCES={x['reference']:str(ROOT.parent.parent/'illustration-previews'/(key+'.jpg')) for key,x in PROFILES.items()}


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
    body=f'<canvas id="{canvas}" width="1920" height="1080" style="position:absolute;inset:0;width:1920px;height:1080px" aria-label="{html.escape(data.get("description","Original code illustration"),quote=True)}"></canvas>'
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
        scripts.append(f"tl.fromTo('#{id}',{{opacity:0,y:12}},{{opacity:1,y:0,duration:.35}},{at});")
        if end<duration:scripts.append(f"tl.to('#{id}',{{opacity:0,duration:.18}},{max(at+.35,end-.18)});")
        order.append({'id':id,'role':'label','enter_at':at,'settle_at':min(end,at+.35),'depends_on':[]})
    # Code is isolated per instance. Time comes only from the seekable parent timeline.
    helpers='\n'.join((ROOT/name).read_text() for name in ['print.js','brush.js','runtime.js'])
    config=json.dumps(data.get('configuration',{}),ensure_ascii=False)
    script='{'+helpers+f'\nconst canvas=document.getElementById({json.dumps(canvas)});const art=createArtwork(canvas,{json.dumps(profile)});const data={config};const clock={{t:0}};\nfunction drawScene(t){{const ctx=art.ctx;art.clear();\n'+source+'\n}\nfunction paint(){art.printOptions={};drawScene(clock.t);art.finish(clock.t,art.printOptions);}\npaint();'+f'tl.to(clock,{{t:{duration},duration:{duration},ease:"none",onUpdate:paint}},0);'+'}\n'+''.join(scripts)
    order.insert(0,{'id':canvas,'role':'illustration','enter_at':0,'settle_at':0,'depends_on':[]})
    return {'html':body,'js':script,'reading_order':order,'component':'artwork','parent':'original-art','implementation':'authored-artwork','design_reference':data.get('design_reference',profile.get('reference','art-'+profile['engine'])),'layout':{'source':data.get('source'),'engine':profile['engine']}}
