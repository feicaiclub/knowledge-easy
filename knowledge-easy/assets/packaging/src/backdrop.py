"""Moving backgrounds for cinematic graphics. Production builds and previews share settings and native media treatment."""
import copy,html,json,math
DEFAULTS={'adjust':{'exposure':-.55,'saturation':-.2,'contrast':.04},'effects':{'blur':.7}}

def resolve(spec):
    result=copy.deepcopy(spec)
    treatment=result.get('treatment','cinematic')
    if treatment not in ('cinematic','raw'):raise ValueError('Background treatment must be cinematic or raw.')
    if treatment=='cinematic':
        grading=copy.deepcopy(DEFAULTS)
        for key,value in result.get('grading',{}).items():
            if isinstance(value,dict) and isinstance(grading.get(key),dict):grading[key].update(value)
            else:grading[key]=value
        result['grading']=grading;result.setdefault('shade',.25)
    else:result.setdefault('grading',{});result.setdefault('shade',0)
    return result

def render(prefix,duration,spec):
    spec=resolve(spec);start=float(spec.get('media_start',0));rate=float(spec.get('rate',1));shade=float(spec['shade'])
    if not all(math.isfinite(v) for v in (start,rate,shade,duration)) or start<0 or rate<=0 or not 0<=shade<=1:raise ValueError('Invalid background timing, playback rate, or shade settings.')
    E=lambda value:html.escape(str(value),quote=True)
    grade=E(json.dumps(spec['grading'],ensure_ascii=False,separators=(',',':')))
    focus=E(spec.get('focus','50% 50%'))
    style=f'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{focus};z-index:0'
    common=f'id="{E(prefix)}" class="clip ke-backdrop" data-visual-role="ambient-background" src="{E(spec["src"])}" data-start="0" data-duration="{duration}" data-color-grading="{grade}" style="{style}"'
    is_image=spec.get('type')=='image' or str(spec['src']).lower().endswith(('.png','.jpg','.jpeg','.webp','.avif'))
    media=('<img '+common+'>' if is_image else f'<video {common} data-media-start="{start}" data-playback-rate="{rate}" data-hf-media-start-basis="local" muted playsinline></video>')
    if shade:media+=f'<div aria-hidden="true" style="position:absolute;inset:0;z-index:1;background:rgba(5,10,14,{shade});pointer-events:none"></div>'
    return media
