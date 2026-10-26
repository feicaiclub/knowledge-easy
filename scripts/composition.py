"""Compose registered designs and explicit project extensions on one scene.

Family labels are descriptive. Provenance and visible primitives are collected
from the actual render result, never inferred from a component's chosen name.
"""
import copy, hashlib, html, importlib.util, json, math, re
from pathlib import Path
from html.parser import HTMLParser


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class VisualInventory(HTMLParser):
    def __init__(self):
        super().__init__();self.counts={'images':0,'videos':0,'svg_shapes':0,'text_characters':0}
    def handle_starttag(self,tag,attrs):
        if tag=='img':self.counts['images']+=1
        elif tag=='video':self.counts['videos']+=1
        elif tag in ('path','circle','ellipse','rect','polygon','polyline','line'):self.counts['svg_shapes']+=1
    def handle_data(self,data):self.counts['text_characters']+=len(data.strip())


def inventory(markup):
    parser=VisualInventory();parser.feed(markup);return parser.counts


def verify_renderer(kit):
    expected=(kit.ROOT/'editorial.py').resolve()
    for function in (kit.render,kit.Component.render):
        if Path(function.__code__.co_filename).resolve()!=expected:
            raise ValueError('Unregistered render override: declare custom implementations in film.extensions.')


def validate_reference(project,reference,kit,local):
    if isinstance(reference,str) and reference in getattr(kit,'REFERENCE_IDS',kit.BASE_IDS):return
    if isinstance(reference,dict) and reference.get('src') and reference.get('reason','').strip():
        local(project,reference['src']);return
    raise ValueError('Use a library style reference or a project image reference with src and reason.')


def extension_registry(project,film,kit,local):
    registry={}
    verify_renderer(kit)
    for spec in film.get('extensions',[]):
        kind=spec['id']
        if kind in kit.FAMILIES or kind in registry:raise ValueError('Extension must have a new id: '+kind)
        reference=spec.get('design_reference')
        validate_reference(project,reference,kit,local)
        if not spec.get('reason','').strip():raise ValueError(kind+': state the design reason for the extension.')
        path=local(project,spec['source'])
        module_spec=importlib.util.spec_from_file_location('project_'+kind.replace('-','_'),path)
        mod=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(mod)
        if not callable(getattr(mod,'render',None)):raise ValueError(kind+': extension must export render(kit, prefix, duration, data, cues, locale).')
        registry[kind]={'render':mod.render,'source':spec['source'],'sha256':sha(path),'design_reference':reference,'reason':spec['reason']}
    return registry


def layers(scene):
    if scene.get('component') and 'components' in scene:raise ValueError('Use component or components, not both.')
    if 'components' in scene:
        if not isinstance(scene['components'],list) or not scene['components']:raise ValueError('components must be a nonempty list.')
        return scene['components']
    return [{'id':'main',**{k:scene[k] for k in ('component','data','cues','design_reference') if k in scene}}] if scene.get('component') else []


def render_scene(project,scene,kit,registry,local):
    bodies=[];scripts=[];usage=[];ids=set();d=float(scene['duration'])
    for layer in layers(scene):
        key=layer.get('id')
        if not key or not re.fullmatch(r'[A-Za-z][\w-]*',key) or key in ids:raise ValueError('Every composition layer needs a unique id.')
        ids.add(key);prefix=scene['id']+'-'+key;kind=layer['component']
        start=float(layer.get('start',0));duration=float(layer.get('duration',d-start))
        if not all(math.isfinite(x) for x in (start,duration)) or start<0 or duration<=0 or start+duration>d+.0001:raise ValueError('Component layer extends beyond its scene.')
        def check_content(value):
            if isinstance(value,dict):
                if 'src' in value:local(project,value['src'])
                for child in value.values():check_content(child)
            elif isinstance(value,list):
                for child in value:check_content(child)
        data=layer.get('data',{});check_content(data)
        render_data=copy.deepcopy(data)
        art_source=None
        if kind=='artwork':
            if not hasattr(kit,'ARTWORK'):raise ValueError('This project snapshot predates code artwork; use install-pack --update intentionally.')
            art_source=local(project,data['source'])
            source=art_source.read_text(encoding='utf-8')
            if re.search(r'\b(?:Date\.now|Math\.random|setInterval|setTimeout|fetch)\s*\(',source):
                raise ValueError('Artwork must be deterministic and local; use t and art.rng(seed).')
            render_data['_source_code']=source
            render_data.setdefault('configuration',{})['duration']=duration
            render_data['configuration']['beats']={k:time-float(scene['start'])-start for k,time in scene.get('_beats',{}).items() if float(scene['start'])+start<=time<float(scene['start'])+start+duration}
        ext=registry.get(kind);locale=scene['_locale']
        if ext:
            result=ext['render'](kit,prefix,duration,copy.deepcopy(data),copy.deepcopy(layer.get('cues',{})),locale)
            result=dict(result,component=kind,parent=ext['design_reference'] if isinstance(ext['design_reference'],str) else 'project-art-direction',design_reference=ext['design_reference'],version=kit.VERSION,implementation='project-extension')
            verify_renderer(kit)
            provenance={k:ext[k] for k in ('source','sha256','reason')}
        else:
            result=kit.render(kind,prefix,duration,render_data,layer.get('cues',{}),locale=locale)
            if not result.get('implementation'):raise ValueError(kind+': unregistered render override; use film.extensions for custom designs.')
            provenance={'source':str(kit.ROOT.relative_to(project.resolve())),'version':kit.VERSION}
            if art_source:provenance.update(drawing_source=data['source'],drawing_sha256=sha(art_source))
        for field in ('html','js','reading_order','component','parent','version'):
            if field not in result:raise ValueError(kind+': renderer omitted '+field)
        reference=layer.get('design_reference') or scene.get('design_reference') or scene.get('_design_reference') or result.get('design_reference')
        validate_reference(project,reference,kit,local)
        frame=layer.get('frame',[0,0,1920,1080])
        if len(frame)!=4:raise ValueError('frame must be [x, y, width, height].')
        x,y,w,h=[float(v) for v in frame]
        if not all(math.isfinite(v) for v in (x,y,w,h)) or min(w,h)<=0 or min(x,y)<0 or x+w>1920+.01 or y+h>1080+.01:raise ValueError('Component frame outside canvas.')
        scale=min(w/1920,h/1080);x+=(w-1920*scale)/2;y+=(h-1080*scale)/2
        # Timed wrapper controls the layer; embedded videos use scene-local times.
        markup=re.sub(r'(\bdata-start=")([\d.]+)(")',lambda m:m[1]+str(float(m[2])+start)+m[3],result['html'])
        outer=prefix+'-placement';inner=prefix+'-design'
        bodies.append(f'<div id="{outer}" style="position:absolute;inset:0;z-index:10;pointer-events:none"><div id="{inner}" style="position:absolute;width:1920px;height:1080px;transform-origin:0 0;transform:translate({x}px,{y}px) scale({scale})">{markup}</div></div>')
        scripts.append('{const parent=tl;{const tl=gsap.timeline();'+result['js']+'parent.add(tl,'+str(start)+');}}')
        if start>0:scripts.append(f"tl.set('#{outer}',{{opacity:0}},0);tl.set('#{outer}',{{opacity:1}},{start});")
        if start+duration<d:scripts.append(f"tl.set('#{outer}',{{opacity:0}},{start+duration});")
        features=inventory(result['html'])
        reading=[dict(row,enter_at=float(row['enter_at'])+start,settle_at=float(row['settle_at'])+start) for row in result['reading_order']]
        usage.append({'id':prefix,'scene_id':scene['id'],'start':float(scene['start'])+start,'duration':duration,
                      'purpose':layer.get('purpose',scene['purpose']),'component':kind,'parent':result['parent'],'version':result['version'],
                      'implementation':result.get('implementation'),'design_reference':reference,'provenance':provenance,
                      'frame':frame,'scale':scale,'visual_inventory':features,'layout':result.get('layout'),
                      'data':data,'cues':layer.get('cues',{}),'reading_order':reading,'scene_start':float(scene['start'])})
    return ''.join(bodies),''.join(scripts),usage


def review_plan(usage):
    notes=[]
    for row in usage:
        counts=row['visual_inventory'];reasons=[]
        if row['implementation']=='project-extension':reasons.append('Custom design: compare the actual explanatory result and motion with the chosen project/style reference. Judge craft and meaning, not similarity to a fixed layout.')
        if not counts['images'] and not counts['videos'] and row['implementation']!='authored-artwork':
            reasons.append('No foreground media: assess whether typography/geometry explains the idea or only restates narration. This is a review prompt, not an image quota.')
        if row['implementation']=='authored-artwork':reasons.append('Original illustration: inspect silhouette, material, staging, performance and camera across key poses; do not treat a working drawing function as design approval.')
        if row['scale']<.8:reasons.append('Scaled composition: inspect effective text size, whitespace and caption clearance in the export.')
        if reasons:notes.append({'instance':row['id'],'design_reference':row['design_reference'],'reasons':reasons})
    return notes
