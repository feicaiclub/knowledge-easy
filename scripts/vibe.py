#!/usr/bin/env python3
"""One public entry for the portable FEICAI knowledge-video toolset."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,html,importlib.util,inspect,json,os,re,shutil,subprocess
from pathlib import Path
from bootstrap import SKILL,contained,ensure,run
from language import normalize,resolve,caption_lines,CONFIG


def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def project_path(value):
    p=Path(value).expanduser().resolve()
    if contained(p,SKILL):raise ValueError('Film projects, caches, and runtime dependencies must be outside the Skill folder.')
    return p


def local(project,relative):
    if Path(relative).is_absolute() or '..' in Path(relative).parts:raise ValueError('Use a project-relative asset path: '+relative)
    p=(project/relative).resolve()
    if not contained(p,project) or not p.is_file():raise ValueError('Missing project asset: '+relative)
    return p


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def install_pack(project,update=False):
    src=SKILL/'assets/packaging/src';version=module(src/'editorial.py','library_version').VERSION;dest=project/'kit'/('editorial-'+version)
    files=[p for p in src.rglob('*') if p.is_file() and p.name!='README.md']
    previous=load(project/'kit/editorial-lock.json') if (project/'kit/editorial-lock.json').exists() else None
    if previous and previous['version']!=version and not update:
        raise ValueError('A different component version is installed. Review it, then use install-pack --update.')
    changed=[str(p.relative_to(src)) for p in files if (dest/p.relative_to(src)).exists() and sha(dest/p.relative_to(src))!=sha(p)]
    if changed and not update:raise ValueError('The installed component snapshot differs. Review the changes, then use install-pack --update: '+', '.join(changed))
    for p in files:
        d=dest/p.relative_to(src);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    fontdest=project/'assets/fonts';fontdest.mkdir(parents=True,exist_ok=True)
    for p in (SKILL/'assets/packaging/fonts').iterdir():
        d=fontdest/p.name
        if d.exists() and sha(d)!=sha(p) and not update:raise ValueError('The installed font has changed: '+p.name)
        shutil.copy2(p,d)
    lock={'version':version,'source':'knowledge-easy/assets/packaging/src','local_snapshot':'kit/editorial-'+version,
          'files_sha256':{str(p.relative_to(src)):sha(p) for p in files},'fonts_sha256':{p.name:sha(p) for p in fontdest.iterdir() if p.is_file()}}
    save(project/'kit/editorial-lock.json',lock)
    return dest


def init(project,language="en-US"):
    language=normalize(language)
    if (project/'project.json').exists():raise ValueError('The project already exists and will not be overwritten.')
    project.mkdir(parents=True,exist_ok=True)
    for p in ['assets/media','audio','compositions','research','review','final']:(project/p).mkdir(parents=True,exist_ok=True)
    install_pack(project)
    save(project/'project.json',{'title':project.name,'skill':'knowledge-easy','language':language,'final_file':None,'locked':[]})
    save(project/'film.json',{'title':project.name,'language':language,'fps':30,'duration':0,'scenes':[],'subtitles':[]})
    save(project/'voice-plan.json',{'language':language,'segments':[],'instruction':'Write complete passages. Keep the script in text; use tts_text for pronunciation adjustments only. Direction records delivery intent, not a guaranteed model control.'})
    save(project/'assets.json',{'sources':[],'placements':[]})
    print(str(project))


def media_tag(project,item,id,duration,background=False):
    src=item['src'];local(project,src)
    start=float(item.get('media_start',0));rate=float(item.get('rate',1))
    if start<0 or rate<=0:raise ValueError('Invalid source timing')
    grading=html.escape(json.dumps(item.get('grading',{})),quote=True)
    return f'<video id="{id}" class="clip scene-film" src="{html.escape(src,quote=True)}" data-start="0" data-duration="{duration}" data-media-start="{start}" data-playback-rate="{rate}" data-color-grading="{grading}" muted playsinline></video>'


def build(project,manifest=None):
    film=load(manifest or project/'film.json');language=resolve(project,film);duration=float(film['duration']);fps=float(film.get('fps',30))
    if duration<=0 or fps<=0:raise ValueError('Set the duration, frame rate, and scenes first.')
    lock=load(project/'kit/editorial-lock.json');path=project/lock['local_snapshot']
    kit=module(path/'editorial.py','editorial')
    locale_options={'locale':language} if 'locale' in inspect.signature(kit.render).parameters else {}
    if not locale_options and language!='zh-CN':raise ValueError('This older component snapshot supports Chinese only. Use install-pack --update for English.')
    for name,h in lock['files_sha256'].items():
        if sha(path/name)!=h:raise ValueError('The component snapshot changed. Update it explicitly before building: '+name)
    hosts=[];usage=[];ids=set();objects=[]
    for scene in film['scenes']:
        cid=scene['id'];start=float(scene['start']);d=float(scene['duration'])
        if not re.fullmatch(r'[a-zA-Z][\w-]*',cid) or cid in ids:raise ValueError('Duplicate or invalid scene ID.')
        ids.add(cid)
        if start<0 or d<=0 or start+d>duration+1/fps:raise ValueError('Scene extends beyond the timeline: '+cid)
        body='';js=''
        if scene.get('background'):body+=media_tag(project,scene['background'],cid+'-background',d,True)
        if scene.get('footage'):body+=media_tag(project,scene['footage'],cid+'-footage',d)
        if scene.get('component'):
            def check_content(v):
                if isinstance(v,dict):
                    if 'src' in v:local(project,v['src'])
                    for x in v.values():check_content(x)
                elif isinstance(v,list):
                    for x in v:check_content(x)
            check_content(scene.get('data',{}))
            r=kit.render(scene['component'],cid,d,scene['data'],scene.get('cues',{}),**locale_options);body+=r['html'];js+=r['js']
            usage.append({'id':cid,'start':start,'duration':d,'purpose':scene.get('purpose',''),'data':scene['data'],'cues':scene.get('cues',{}),**{k:r[k] for k in ['component','parent','version','reading_order']}})
        if not body:raise ValueError('Scene has no visual content: '+cid)
        css=kit.css('assets/fonts/',**locale_options)+'.scene-film{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}#root{position:absolute;inset:0;overflow:hidden}'
        doc=f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"></head><body><template><style>{css}</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080" data-duration="{d}">{body}</div><script>const tl=gsap.timeline({{paused:true}});{js}window.__timelines=window.__timelines||{{}};window.__timelines['{cid}']=tl;</script></template></body></html>'''
        (project/'compositions'/f'{cid}.html').write_text(doc,encoding='utf-8')
        hosts.append(f'<div id="host-{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{start}" data-duration="{d}" data-width="1920" data-height="1080" data-track-index="1" data-track-kind="graphics"></div>')
        objects.append({'id':cid,'start':start,'end':start+d,'label':scene.get('purpose',cid),'kind':'scene'})
    previous_end=-1
    for i,sub in enumerate(film.get('subtitles',[])):
        a=round(float(sub['start'])*fps)/fps;b=round(float(sub['end'])*fps)/fps
        if a<previous_end-1e-7 or a<0 or b<=a or b>duration+1/fps:raise ValueError('Caption timings overlap or extend beyond the film.')
        previous_end=b
        hosts.append(f'<div id="subtitle-{i}" class="clip captions" data-start="{a}" data-duration="{b-a}" data-track-kind="captions" data-track-index="10"><span>{html.escape(caption_lines(sub["text"],language))}</span></div>')
    if film.get('mix'):
        local(project,film['mix']);hosts.append(f'<audio id="film-mix" class="clip" src="{html.escape(film["mix"],quote=True)}" data-start="0" data-duration="{duration}" data-volume="1" data-track-index="20"></audio>')
    doc='''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><script src="assets/vendor/gsap.min.js"></script><style>@font-face{font-family:CaptionSans;src:url('assets/fonts/notosanssc-NotoSansSC[wght].ttf')}html,body{margin:0;overflow:hidden;background:#151c1c}.clip{position:absolute;inset:0}#root{width:100%;height:100%;position:relative}.captions{display:flex;align-items:flex-end;justify-content:center;box-sizing:border-box;padding:0 192px 105px;pointer-events:none}.captions span{white-space:pre-line;font:42px/1.4 CaptionSans,sans-serif;color:#fff;text-shadow:0 2px 8px #000;background:#0008;padding:4px 18px;border-radius:4px}</style></head><body>'''+f'<div id="root" data-composition-id="film" data-width="1920" data-height="1080" data-fps="{fps}" data-duration="{duration}">'+''.join(hosts)+'''</div><script>window.__timelines=window.__timelines||{};window.__timelines.film=gsap.timeline({paused:true});</script></body></html>'''
    doc=doc.replace('{language}',language).replace('notosanssc-NotoSansSC[wght].ttf',CONFIG[language]['caption_font'])
    (project/'index.html').write_text(doc,encoding='utf-8');save(project/'hyperframes.json',{})
    save(project/'research/component-usage.json',usage);save(project/'review/timeline.json',{'objects':objects})
    print(json.dumps({'scenes':len(film['scenes']),'components':len(usage),'seconds':duration}))


def catalog(project,base=False,language="en-US",media_dir=None):
    language=normalize(language)
    src=SKILL/'assets/packaging/src';variants=load(src/('locales/zh-CN/variants.json' if language=='zh-CN' else 'variants.json'));scenes=[]
    source=module(src/'base_catalog.py','base_catalog') if base else None
    samples=[(item[0],*source.build_scene(i,item[0],{'language':language})) for i,item in enumerate(source.ITEMS,1)] if base else []
    required=set(re.findall(r'assets/(?:pack-media|media)/([a-z0-9_-]+\.mp4)', '\n'.join(row[1] for row in samples) if base else json.dumps(variants)))
    if not base:required.add('street.mp4')
    media=Path(media_dir).expanduser().resolve() if media_dir else SKILL/'assets/packaging/demo-media'
    missing=sorted(name for name in required if not (media/name).is_file())
    if missing:
        raise ValueError('Catalog source clips are not included in the public release. Supply licensed clips with --media-dir. Missing: '+', '.join(missing)+'. See assets/packaging/demo-media/README.md. The handbook contains still previews.')
    init(project,language)
    for name in sorted(required):shutil.copy2(media/name,project/'assets/media'/name)
    if base:
        kit=module(src/'editorial.py','base_style');hosts=[]
        for i,(kind,body,js) in enumerate(samples,1):
            cid='base-'+kind
            doc=f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"></head><body><template><style>{kit.css('assets/fonts/',locale=language)}#root{{position:absolute;inset:0;overflow:hidden;background:#151c1c;color:#efe4ce;font-family:PackSans,sans-serif}}</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080" data-duration="8">{body}</div><script>const tl=gsap.timeline({{paused:true}});{js}window.__timelines=window.__timelines||{{}};window.__timelines['{cid}']=tl;</script></template></body></html>'''
            (project/'compositions'/f'{cid}.html').write_text(doc,encoding='utf-8')
            hosts.append(f'<div id="host-{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{(i-1)*8}" data-duration="8" data-width="1920" data-height="1080"></div>')
        doc='<!doctype html><html><head><meta charset="utf-8"><script src="assets/vendor/gsap.min.js"></script><style>html,body{margin:0;overflow:hidden;background:#151c1c}#root{position:relative;width:100%;height:100%}.clip{position:absolute;inset:0}</style></head><body><div id="root" data-composition-id="base-catalog" data-width="1920" data-height="1080" data-fps="30" data-duration="96">'+''.join(hosts)+"</div><script>window.__timelines=window.__timelines||{};window.__timelines['base-catalog']=gsap.timeline({paused:true});</script></body></html>"
        (project/'index.html').write_text(doc,encoding='utf-8');save(project/'hyperframes.json',{});save(project/'film.json',{'language':language,'duration':96,'fps':30,'catalog_only':True})
        print('12 base designs generated');return
    for i,row in enumerate(variants):
        conf=json.loads(json.dumps(row['configuration']).replace('assets/pack-media/','assets/media/'))
        scenes.append({'id':'demo-'+row['id'],'start':i*8,'duration':8,'component':row['id'],**conf,
                       'purpose':row['purpose'],'background':{'src':'assets/media/street.mp4','grading':{'adjust':{'exposure':-.7,'saturation':-.25},'effects':{'blur':.6}}}})
    save(project/'film.json',{'title':'Shared component examples','language':language,'fps':30,'duration':len(scenes)*8,'scenes':scenes,'subtitles':[],'catalog_only':True})
    build(project)
    # Historical twelve-design source is included as base_catalog.py; new production uses the shared renderer.


def ready_render(project,info):
    target=project/'assets/vendor/gsap.min.js';target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(info['render']['gsap'],target)
    if not (project/'package.json').exists():save(project/'package.json',{'name':'feicai-film','private':True,'type':'module'})


def verify(project,file,env):
    p=local(project,file);probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p],env))
    run(['ffmpeg','-v','error','-i',p,'-f','null','-'],env)
    report={'file':file,'sha256':sha(p),'full_decode':'passed','duration':float(probe['format']['duration']),
            'video':next((s for s in probe['streams'] if s['codec_type']=='video'),None),'audio_present':any(s['codec_type']=='audio' for s in probe['streams']),
            'visual_review':'pending','listening_review':'pending'}
    if not report['video']:raise ValueError('No video stream was found.')
    if (project/'film.json').exists():
        film=load(project/'film.json');expected=film['duration'];fps=film.get('fps',30)
        if abs(expected-report['duration'])>2/fps:raise ValueError('The exported duration does not match the timeline.')
        if film.get('mix') and not report['audio_present']:raise ValueError('The export is missing its audio track.')
    save(project/'review/technical-check.json',report);print(json.dumps({k:v for k,v in report.items() if k!='video'},ensure_ascii=False,indent=2))


def audit_media(project):
    data=load(project/'assets.json');seen={};duplicates=[]
    for row in data['placements']:
        if row.get('static',False):continue
        local(project,row['file'])
        if not row.get('original_shots'):raise ValueError('Moving footage is missing its original shot identity: '+row['id'])
        for shot in row['original_shots']:
            if shot in seen:duplicates.append({'shot':shot,'first':seen[shot],'again':row['id']})
            seen[shot]=row['id']
    save(project/'review/footage-check.json',{'placements':len(data['placements']),'duplicates':duplicates,'scope':'Original-shot ledger check. Cross-check every compiled video element; filenames and time ranges alone do not prove uniqueness.'})
    if duplicates:raise ValueError('Repeated original moving shot: '+json.dumps(duplicates,ensure_ascii=False))
    print('No repeated original shots appear in the ledger. Check the actual footage and ledger completeness as well.')


def main():
    ap=argparse.ArgumentParser(description='FEICAI · Explainer Video');subs=ap.add_subparsers(dest='cmd',required=True)
    p=subs.add_parser('doctor');p.add_argument('--features',default='core');p.add_argument('--install',action='store_true')
    for name in ['init','catalog','build','install-pack','voice','mix','audit-media','check','render','snapshot','preview','register','studio','verify','transcribe','download']:
        p=subs.add_parser(name);p.add_argument('--project',required=True)
        if name in ['init','catalog']:p.add_argument('--language',choices=['en-US','zh-CN'],default='en-US')
        if name=='install-pack':p.add_argument('--update',action='store_true')
        if name=='catalog':
            p.add_argument('--base',action='store_true');p.add_argument('--media-dir',help='Folder of licensed demo clips; see assets/packaging/demo-media/README.md.')
        if name in ['voice','mix']:p.add_argument('--plan',required=True)
        if name in ['register','verify','transcribe']:p.add_argument('--file',required=True)
        if name=='transcribe':p.add_argument('--prompt',default='',help='Optional names and terminology, not the expected transcript.')
        if name=='register':
            p.add_argument('--label',required=True);p.add_argument('--id',required=True);p.add_argument('--audio')
        if name=='studio':
            p.add_argument('--port',type=int,default=8798);p.add_argument('--restart',action='store_true')
        if name=='render':p.add_argument('--output',default='final/film.mp4');p.add_argument('--quality',choices=['draft','looks','delivery'],default='delivery')
        if name=='snapshot':p.add_argument('--at',required=True)
        if name=='download':p.add_argument('--url',required=True)
    args=ap.parse_args()
    if args.cmd=='doctor':
        info,_=ensure(filter(None,args.features.split(',')),args.install);print(json.dumps(info,ensure_ascii=False,indent=2));return 0 if info['ready'] else 2
    project=project_path(args.project)
    if args.cmd=='init':init(project,args.language);return 0
    if args.cmd=='catalog':catalog(project,args.base,args.language,args.media_dir);return 0
    if not (project/'project.json').exists() and args.cmd not in ['register','studio','verify']:raise ValueError('Run init first, or use a registered review project.')
    if args.cmd=='build':build(project);return 0
    if args.cmd=='install-pack':install_pack(project,args.update);return 0
    if args.cmd=='audit-media':audit_media(project);return 0
    features={'render'} if args.cmd in ['render','check','snapshot','preview'] else {'voice'} if args.cmd=='voice' else {'audio'} if args.cmd=='mix' else {'asr'} if args.cmd=='transcribe' else {'download'} if args.cmd=='download' else {'core'}
    info,env=ensure(features,True)
    if not info['ready']:raise RuntimeError('Dependency setup is incomplete.')
    if args.cmd in ['render','check','snapshot','preview']:
        ready_render(project,info);cmd=[info['render']['node'],info['render']['cli']]
        if args.cmd=='render':
            target=(project/args.output).resolve()
            if not contained(target,project):raise ValueError('Output must stay inside the project.')
            if target.exists():raise ValueError('Output already exists. Choose a new --output to preserve the reviewed version.')
            if (project/'film.json').exists():
                film=load(project/'film.json')
                if film.get('mix'):
                    audio_info=json.loads(run(['ffprobe','-v','error','-show_format','-of','json',local(project,film['mix'])],env))
                    if float(audio_info['format']['duration'])>float(film['duration'])+.001:
                        raise ValueError('The film is shorter than the complete mix. Extend the visuals rather than cutting the audio.')
            target.parent.mkdir(parents=True,exist_ok=True)
            run([*cmd,'check','--json'],env,project,capture=False)
            run([*cmd,'render','--quality',args.quality,'--output',str(target)],env,project,capture=False)
            verify(project,args.output,env)
        elif args.cmd=='snapshot':run([*cmd,'snapshot','--at',args.at],env,project,capture=False)
        elif args.cmd=='preview':run([*cmd,'preview','--background'],env,project,capture=False)
        else:run([*cmd,'check','--json'],env,project,capture=False)
    elif args.cmd=='voice':run([info['python'],SKILL/'scripts/voice.py','--project',project,'--plan',local(project,args.plan),'--model',info['model_path'],'--backend',info['voice_backend']],env,project,capture=False)
    elif args.cmd=='mix':run([info['python'],SKILL/'scripts/mix.py','--project',project,'--plan',local(project,args.plan)],env,project,capture=False)
    elif args.cmd=='transcribe':run([info['python'],SKILL/'scripts/transcribe.py','--project',project,'--file',local(project,args.file),'--model',info['asr_model_path'],'--prompt',args.prompt],env,project,capture=False)
    elif args.cmd=='download':run([info['python'],'-m','yt_dlp','--no-playlist','-f','bv*[height<=1080]+ba/b[height<=1080]','--merge-output-format','mp4','-o',project/'assets/media/%(id)s.%(ext)s',args.url],env,project,capture=False)
    elif args.cmd=='register':
        cmd=[info['python'],SKILL/'scripts/studio/project.py','--project',project,'--file',args.file,'--label',args.label,'--id',args.id]
        if args.audio:cmd+=['--audio',args.audio]
        if (project/'review/timeline.json').exists():cmd+=['--timeline','review/timeline.json']
        run(cmd,env,project,capture=False)
    elif args.cmd=='studio':run([info['python'],SKILL/'scripts/studio/launch.py','--project',project,'--port',str(args.port),*(['--restart'] if args.restart else [])],env,project,capture=False)
    elif args.cmd=='verify':verify(project,args.file,env)
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)
