"""Review actual exports. Project references are optional; old screenshots are no longer required dependencies."""
import hashlib, html, json, re, shutil, subprocess, os
from pathlib import Path

FILM_CRITERIA={
    'direction':'Explain how the subjects, media, and shots create the intended change in understanding. Cite actual frames and check whether the work merely replaces example text or objects.',
    'rhythm':'After watching the full film, identify specific moments of progression, holds, shot-size changes, and shifts in information density. Check reading time and passages that drag or end abruptly.',
    'sound':'If audio is present, listen to the full film and review voice identity, delivery by passage, phrase endings and joins, speech clarity, material-specific effects, and musical transitions. If silent, record that design choice.'}

CRITERIA={
    'hierarchy':'At final size, identify the first and second reading targets. Check letterforms, contrast, and reveal order. Confirm readability after scaling and compare hierarchy with the reference when available.',
    'composition':'Check silhouettes, scale, balance, negative space, cropping, and caption clearance. Subjects, contact points, and relationships must remain clear before and after key actions.',
    'material':'Explain how the chosen media or graphics support the subject. Inspect actual lighting, volume, edges, overlaps, and line or color-shape quality rather than counting textures.',
    'motion':'Watch the complete clip and locate its key changes. Check subjects before connections, anticipation and follow-through, contact and overlap, reading holds, and edit points.',
    'explanation':'Identify the evidence, comparison, mechanism, or emotional contribution added by the image. Compare custom work with the selected reference for explanatory value and finish.'}


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda:file.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def save(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def local(project,name):
    path=(project/name).resolve()
    if not path.is_relative_to(project.resolve()) or not path.is_file():raise ValueError('Missing or escaping review resource: '+name)
    return path


def source_signature(project, include_runtime=True):
    project=project.resolve()
    paths={project/'film.json',project/'index.html',project/'kit/editorial-lock.json',project/'research/component-usage.json'}
    paths.update((project/'compositions').glob('*.html'))
    lock=load(project/'kit/editorial-lock.json')
    paths.update(project/lock['local_snapshot']/name for name in lock['files_sha256'])
    paths.update(project/'assets/fonts'/name for name in lock.get('fonts_sha256',{}))
    film=load(project/'film.json')
    paths.update(local(project,x['source']) for x in film.get('extensions',[]))
    for row in load(project/'research/component-usage.json'):
        if row.get('provenance',{}).get('drawing_source'):paths.add(local(project,row['provenance']['drawing_source']))
        reference=row.get('design_reference')
        if isinstance(reference,dict):paths.add(local(project,reference['src']))
    for page in list(paths):
        if page.suffix=='.html':
            for name in re.findall(r'(?:src|href)=[\"\'](assets/[^\"\']+)',page.read_text()):
                if include_runtime or not name.startswith('assets/vendor/'):
                    paths.add(local(project,html.unescape(name)))
    hashes={str(p.relative_to(project)):sha(p) for p in sorted(paths)}
    return {'sha256':hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),'files':hashes}


def require_current_build(project):
    receipt=load(project/"research/build-receipt.json")
    if receipt!=source_signature(project,include_runtime=False):
        raise ValueError("Project changed since build; run build before rendering.")


def bind_render(project,file,signature):
    current=source_signature(project)
    if current!=signature:raise ValueError('Project changed during render; rebuild and render again before review.')
    save(project/'review/render-receipt.json',{'file':file,'sha256':sha(local(project,file)),'source':signature})


def bound_export(project,file):
    receipt=load(project/'review/render-receipt.json')
    if receipt['file']!=file or receipt['sha256']!=sha(local(project,file)):raise ValueError('Export does not match the render receipt.')
    if source_signature(project)!=receipt['source']:raise ValueError('Source changed after render; review a new export.')
    return receipt


def run(cmd,env):
    result=subprocess.run([str(x) for x in cmd],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if result.returncode:raise RuntimeError(result.stderr[-2000:])


def prepare(project,file,skill,env=None):
    receipt=bound_export(project,file);film=load(project/'film.json');usage=load(project/'research/component-usage.json')
    language=film.get('language','zh-CN');folder=project/'review'/('visual-'+receipt['sha256'][:12]);folder.mkdir(parents=True,exist_ok=True)
    rows=[];sections=[];evidence={};export=local(project,file)
    for item in usage:
        id=item['id'];reference=item.get('design_reference');poster=None
        if isinstance(reference,dict):poster=local(project,reference['src']);name=reference.get('name','Design Reference for This Film')
        elif isinstance(reference,str) and reference.startswith('art-'):poster=skill/'assets/packaging/illustrations'/(reference[4:]+'.svg');name=reference
        else:name=str(reference or 'Current Design')
        ref=None
        if poster is not None:
            if not poster.is_file():raise ValueError('Missing design reference: '+str(reference))
            ref=folder/(id+'-reference'+poster.suffix);shutil.copy2(poster,ref)
        start=item['start'];end=start+item['duration'];scene_start=item.get('scene_start',start)
        order=item['reading_order'];settled=max([start+.1]+[scene_start+float(n['settle_at']) for n in order])
        times=sorted(set(round(min(end-.04,max(start+.04,t)),3) for t in [start+.12,(start+settled)/2,settled+.15,end-.12]))
        frames=[]
        for i,time in enumerate(times):
            frame=folder/(id+'-'+str(i)+'.jpg')
            run(['ffmpeg','-v','error','-y','-ss',time,'-i',export,'-frames:v','1','-vf','scale=960:-2','-q:v','3',frame],env)
            frames.append({'file':str(frame.relative_to(project)),'time':time,'sha256':sha(frame)})
        clip=folder/(id+'-motion.mp4')
        run(['ffmpeg','-v','error','-y','-ss',start,'-i',export,'-t',item['duration'],'-vf','scale=960:-2','-c:v','libx264','-preset','veryfast','-crf','24','-c:a','aac','-movflags','+faststart',clip],env)
        files={str(clip.relative_to(project)):sha(clip),**{x['file']:x['sha256'] for x in frames}}
        if ref is not None:files[str(ref.relative_to(project))]=sha(ref)
        evidence.update(files)
        row={'id':id,'design_reference':reference,'implementation':item['implementation'],
             'frames':frames,'motion_file':str(clip.relative_to(project)),'reference_file':str(ref.relative_to(project)) if ref is not None else None,
             'criteria':{k:{'verdict':'pending','observation':''} for k in CRITERIA},'motion_watched':False,'verdict':'pending'}
        rows.append(row)
        pics=''.join('<figure><img src="'+html.escape(Path(x['file']).name)+'"><figcaption>'+str(x['time'])+'s</figcaption></figure>' for x in frames)
        reference_panel=('<figure><img src="'+ref.name+'"><figcaption>Selected reference: compare form, materials, and clarity</figcaption></figure>') if ref is not None else '<div><h3>Review Against the Current Design Requirements</h3><p>This passage has no specified reference image. Inspect composition, letterforms, materials, motion, and explanatory value directly. Do not substitute an old screenshot or assume a pass.</p></div>'
        sections.append('<section><h2>'+html.escape(id)+' · '+html.escape(name)+'</h2><p>'+html.escape(item['purpose'])+'</p><div class="pair">'+reference_panel+'<figure><video controls preload="metadata" src="'+clip.name+'"></video><figcaption>Actual export: watch the complete passage</figcaption></figure></div><div class="phases">'+pics+'</div></section>')
    sequence=[]
    for scene in film['scenes']:
        at=float(scene['start'])+float(scene['duration'])*.5
        frame=folder/('sequence-'+scene['id']+'.jpg')
        run(['ffmpeg','-v','error','-y','-ss',at,'-i',export,'-frames:v','1','-vf','scale=640:-2','-q:v','3',frame],env)
        relative=str(frame.relative_to(project));evidence[relative]=sha(frame)
        sequence.append({'id':scene['id'],'start':scene['start'],'duration':scene['duration'],'frame':relative,'time':at})
    review={'schema':2,'export':file,'export_sha256':receipt['sha256'],'source_sha256':receipt['source']['sha256'],
            'status':'pending','reviewer':'','sequence':sequence,'whole_film':{'watched':False,'listened':False,'audio_present':load(project/'review/technical-check.json').get('audio_present',False),'criteria':{k:{'verdict':'pending','observation':''} for k in FILM_CRITERIA}},'criteria':CRITERIA,'scenes':rows,'evidence_sha256':evidence,
            'limits':'Inspect the actual export before recording a judgment. Counts, screenshots, and completed fields do not certify visual quality. Keep self-review and user approval separate.'}
    evidence_index={'export_sha256':receipt['sha256'],'source_sha256':receipt['source']['sha256'],'evidence_sha256':evidence,
                    'scenes':[{k:r[k] for k in ('id','design_reference','implementation','frames','motion_file','reference_file')} for r in rows]}
    evidence_index['sequence']=sequence
    save(folder/'evidence-index.json',evidence_index)
    review['evidence_index']=str((folder/'evidence-index.json').relative_to(project))
    dest=project/'review/visual-review.json'
    if dest.exists():
        old=load(dest)
        if all(old.get(k)==review[k] for k in ('export_sha256','source_sha256','evidence_sha256')):
            review=old
    save(dest,review)
    film_view='<section><h2>Whole-Film Direction, Rhythm, and Sound</h2><video controls preload="metadata" src="'+html.escape(os.path.relpath(export,folder),quote=True)+'"></video><div class="phases">'+''.join('<figure><img loading="lazy" src="'+Path(x['frame']).name+'"><figcaption>'+html.escape(x['id'])+'</figcaption></figure>' for x in sequence)+'</div></section>'
    css='body{margin:32px;background:#151c1c;color:#efe4ce;font:18px/1.6 system-ui}h1{font-size:30px}section{margin:45px 0}img,video{width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}.phases{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}figure{margin:0}figcaption{color:#bccbc7;font-size:14px}p{max-width:1100px}'
    (folder/'index.html').write_text('<!doctype html><html lang="en-US"><meta charset="utf-8"><title>Visual Review</title><style>'+css+'</style><body><h1>Visual Review · '+receipt['sha256'][:12]+'</h1><p>Watch and listen to the full film first, then inspect individual shots for hierarchy, composition, materials, motion, and explanation. Record locations, observations, and resolutions in review/visual-review.json. Leave unreviewed items pending. accept-visuals checks only record completeness and version correspondence.</p>'+film_view+''.join(sections)+'</body></html>',encoding='utf-8')
    return {'status':review['status'],'scenes':len(rows),'comparison':str((folder/'index.html').relative_to(project)),'record':'review/visual-review.json'}


def accept(project):
    review=load(project/'review/visual-review.json');receipt=bound_export(project,review['export'])
    if review['export_sha256']!=receipt['sha256'] or review['source_sha256']!=receipt['source']['sha256']:raise ValueError('Visual review is stale.')
    index=load(local(project,review['evidence_index']))
    expected={k:review[k] for k in ('export_sha256','source_sha256','evidence_sha256')}
    if any(index[k]!=v for k,v in expected.items()):raise ValueError('Review evidence index differs.')
    records=[{k:r[k] for k in ('id','design_reference','implementation','frames','motion_file','reference_file')} for r in review['scenes']]
    if records!=index['scenes']:raise ValueError('Review evidence coverage was changed.')
    if review.get('schema',1)>=2:
        sequence=review.get('sequence',[])
        if sequence!=index.get('sequence') or [x['id'] for x in sequence]!=[x['id'] for x in load(project/'film.json')['scenes']]:
            raise ValueError('Whole-film scene coverage was changed.')
    usage=load(project/'research/component-usage.json')
    if {x['id'] for x in usage}!={x['id'] for x in review['scenes']} or len(usage)!=len(review['scenes']):raise ValueError('Visual review must cover every rendered component instance.')
    if not review.get('reviewer','').strip():raise ValueError('Record who performed the visual review.')
    for name,digest in review['evidence_sha256'].items():
        if sha(local(project,name))!=digest:raise ValueError('Review evidence changed: '+name)
    for row in review['scenes']:
        if row['verdict']!='pass' or row.get('motion_watched') is not True:raise ValueError(row['id']+': watch actual motion and resolve the design review.')
        for key in CRITERIA:
            decision=row.get('criteria',{}).get(key,{})
            if decision.get('verdict')!='pass' or not str(decision.get('observation','')).strip():raise ValueError(row['id']+': missing supported judgment for '+key)
    if review.get('schema',1)>=2:
        whole=review.get('whole_film',{})
        if whole.get('watched') is not True:raise ValueError('Watch the full exported film; component clips do not establish whole-film rhythm.')
        if whole.get('audio_present') and whole.get('listened') is not True:raise ValueError('The full mix still needs listening review.')
        for key in FILM_CRITERIA:
            judgment=whole.get('criteria',{}).get(key,{})
            if judgment.get('verdict')!='pass' or not judgment.get('observation','').strip():raise ValueError('Record a supported whole-film judgment for '+key)
    review['status']='passed';save(project/'review/visual-review.json',review)
    return {'status':'passed','export':review['export'],'sha256':receipt['sha256'],'scope':'The recorded shot and whole-film self-review has passed. User approval is recorded separately.'}
