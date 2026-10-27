#!/usr/bin/env python3
"""Discover first, install only missing capabilities, never inside the Skill."""
import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json, os, platform, re, shutil, subprocess, tempfile, urllib.request, zipfile, tarfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
LOCK = json.loads((Path(__file__).with_name('runtime-lock.json')).read_text(encoding='utf-8'))
FEATURES = {'core', 'render', 'voice', 'asr', 'download', 'audio'}


def contained(path, root):
    try: Path(path).resolve().relative_to(Path(root).resolve()); return True
    except ValueError: return False


def runtime_home():
    if os.environ.get('VIBE_RUNTIME_HOME'):
        p = Path(os.environ['VIBE_RUNTIME_HOME']).expanduser()
    elif sys.platform == 'win32':
        p = Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local')))/'FEICAI/vibe-knowledge-video'
    elif sys.platform == 'darwin':
        p = Path.home()/'Library/Caches/FEICAI/vibe-knowledge-video'
    else:
        p = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache')))/'feicai/vibe-knowledge-video'
    p = p.resolve()
    if contained(p, SKILL): raise ValueError('VIBE_RUNTIME_HOME must be outside the Skill folder.')
    return p


def child_env(root):
    env = dict(os.environ)
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', UV_NO_PROGRESS='1', DO_NOT_TRACK='1')
    uv_cache=root/'uv-cache'
    if shutil.which('uv'):
        try:uv_cache=Path(subprocess.check_output([shutil.which('uv'),'cache','dir'],text=True,timeout=10).strip())
        except (OSError,subprocess.SubprocessError):pass
    # Reuse each user's standard cache when it exists; reject overrides into the bundle.
    for name, default in [('UV_CACHE_DIR',uv_cache),('npm_config_cache',Path.home()/'.npm'),
                          ('HF_HOME',Path.home()/'.cache/huggingface')]:
        target = Path(env.get(name,str(default))).expanduser().resolve()
        if contained(target,SKILL): raise ValueError(name+' must point outside the Skill')
        env[name]=str(target)
    return env


def run(args, env=None, cwd=None, capture=True, timeout=None):
    args = [str(x) for x in args]
    if os.name=='nt' and args[0].lower().endswith(('.cmd','.bat')):
        args=[os.environ.get('COMSPEC','cmd.exe'),'/d','/c',*args]
    result = subprocess.run(args,env=env,cwd=cwd,text=True,encoding='utf-8',errors='replace',
                            stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None,timeout=timeout)
    if result.returncode:
        detail=(result.stderr or result.stdout or '')[-5000:]
        raise RuntimeError(f'Command failed ({result.returncode}): {args[0]}\n{detail}')
    return (result.stdout or '').strip()


def download(url, target):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    tmp=target.with_suffix(target.suffix+'.part')
    try:
        with urllib.request.urlopen(url,timeout=90) as response, tmp.open('wb') as out: shutil.copyfileobj(response,out)
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)


def ensure_uv(root,env,install):
    exe='uv.exe' if os.name=='nt' else 'uv'
    options=[shutil.which('uv'),root/'tools/uv'/exe,Path.home()/'.local/bin'/exe,Path.home()/'.cargo/bin'/exe]
    for value in options:
        if value and Path(value).is_file():
            try: run([value,'--version'],env,timeout=10);return str(value)
            except (RuntimeError,subprocess.TimeoutExpired): pass
    if not install: return None
    print('Installing uv in the user cache; system PATH stays unchanged.',file=sys.stderr)
    suffix='ps1' if os.name=='nt' else 'sh';installer=root/('uv-install.'+suffix)
    download(f'https://astral.sh/uv/{LOCK["uv_installer"]}/install.{suffix}',installer)
    e=dict(env,UV_UNMANAGED_INSTALL=str(root/'tools/uv'),UV_NO_MODIFY_PATH='1')
    try: run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',installer] if os.name=='nt' else ['sh',installer],e,capture=False)
    finally: installer.unlink(missing_ok=True)
    return str(root/'tools/uv'/exe)


def requirements(features):
    groups=[]
    if 'core' in features: groups+=['core']
    if features & {'audio','voice'}: groups+=['audio']
    if 'voice' in features: groups+=['voice_mlx']
    if 'asr' in features: groups+=['asr']
    if 'download' in features: groups+=['download']
    return [v for g in groups for v in LOCK['python_groups'][g]]


def compatible_python(executable,reqs,env):
    if not executable or not Path(executable).is_file():return False
    code='''import sys,json,importlib.metadata as m
from packaging.requirements import Requirement
ok=sys.version_info[:2]==(3,12)
for text in json.loads(sys.argv[1]):
 r=Requirement(text)
 try: ok=ok and (m.version(r.name) in r.specifier)
 except m.PackageNotFoundError: ok=False
print(json.dumps(ok))
'''
    try:return json.loads(run([executable,'-c',code,json.dumps(reqs)],env,timeout=30))
    except (RuntimeError,ValueError,subprocess.TimeoutExpired):return False


def ensure_python(root,env,features,uv,install):
    reqs=requirements(features);tag=hashlib.sha256(json.dumps(reqs).encode()).hexdigest()[:10]
    venv=root/'envs'/('py312-'+tag);exe=venv/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    # An explicit existing environment is reusable only after checking its packages.
    candidates=[os.environ.get('VIBE_PYTHON'),str(exe),sys.executable]
    if (root/'envs').exists():
        candidates += [str(p/('Scripts/python.exe' if os.name=='nt' else 'bin/python')) for p in (root/'envs').iterdir() if p.is_dir()]
    for candidate in candidates:
        if compatible_python(candidate,reqs,env):return str(candidate)
    if not install:return None
    if not exe.is_file():run([uv,'venv','--allow-existing','--python',LOCK['python'],venv],env,capture=False)
    run([uv,'pip','install','--python',exe,'packaging',*reqs],env,capture=False)
    if not compatible_python(str(exe),reqs,env):raise RuntimeError('Python dependency validation failed after installation.')
    return str(exe)


def ffmpeg_pair(a,b,env):
    if not a or not b:return None
    try:
        av=run([a,'-version'],env,timeout=15).splitlines()[0];bv=run([b,'-version'],env,timeout=15).splitlines()[0]
        am=re.search(r'version (\d+)\.(\d+)',av);bm=re.search(r'version (\d+)\.(\d+)',bv)
        if not am or not bm or am.groups()!=bm.groups() or int(am[1])<7:return None
        enc=run([a,'-hide_banner','-encoders'],env,timeout=15)
        if 'libx264' not in enc or 'aac' not in enc:return None
        return {'ffmpeg':str(a),'ffprobe':str(b),'version':av}
    except (RuntimeError,OSError,subprocess.TimeoutExpired):return None


def ensure_media(root,env,python,install):
    pair=ffmpeg_pair(os.environ.get('VIBE_FFMPEG') or shutil.which('ffmpeg'),os.environ.get('VIBE_FFPROBE') or shutil.which('ffprobe'),env)
    if pair:return pair
    # Common user-managed environments may not have been added to PATH.
    for base in [Path.home()/'.local/micromamba/envs',Path.home()/'miniforge3/envs',Path.home()/'miniconda3/envs']:
        if base.exists():
            for folder in base.glob('*/bin'):
                pair=ffmpeg_pair(folder/'ffmpeg',folder/'ffprobe',env)
                if pair:return pair
    exe='.exe' if os.name=='nt' else ''
    for folder in (root/'ffmpeg').glob('*') if (root/'ffmpeg').exists() else []:
        pair=ffmpeg_pair(folder/('ffmpeg'+exe),folder/('ffprobe'+exe),env)
        if pair:return pair
    if not install:return None
    print('Preparing a matching FFmpeg/ffprobe pair in the user cache.',file=sys.stderr)
    code='''import json,sys
from pathlib import Path
from static_ffmpeg.run import get_platform_key,get_or_fetch_platform_executables_else_raise
p=Path(sys.argv[1])/get_platform_key()
a,b=get_or_fetch_platform_executables_else_raise(download_dir=str(p))
print(json.dumps([a,b]))
'''
    result=run([python,'-c',code,root/'ffmpeg'],env,timeout=900)
    a,b=json.loads(result.splitlines()[-1]);pair=ffmpeg_pair(a,b,env)
    if not pair:raise RuntimeError('FFmpeg did not pass its post-install check.')
    return pair


def ensure_node(root,env,install):
    node=shutil.which('node');npm=shutil.which('npm')
    if node and npm:
        try:
            if int(run([node,'-v'],env,timeout=10).lstrip('v').split('.')[0])>=22:return node,npm
        except (RuntimeError,ValueError):pass
    plat={'darwin':'darwin','linux':'linux','win32':'win'}.get(sys.platform)
    arch={'arm64':'arm64','aarch64':'arm64','x86_64':'x64','amd64':'x64'}.get(platform.machine().lower())
    if not plat or not arch:raise RuntimeError('Automatic Node setup is unavailable on this platform. Install Node 22+ and retry.')
    version=LOCK['node_fallback'];base=f'node-v{version}-{plat}-{arch}';folder=root/'tools'/base
    node=folder/('node.exe' if os.name=='nt' else 'bin/node');npm=folder/('npm.cmd' if os.name=='nt' else 'bin/npm')
    if node.exists() and npm.exists():return str(node),str(npm)
    if not install:return None,None
    print('Preparing Node.js in the user cache.',file=sys.stderr)
    ext='.zip' if os.name=='nt' else '.tar.gz';archive=root/(base+ext)
    url=f'https://nodejs.org/dist/v{version}/'
    sums=urllib.request.urlopen(url+'SHASUMS256.txt',timeout=60).read().decode()
    expected=next(line.split()[0] for line in sums.splitlines() if line.split()[-1]==archive.name)
    download(url+archive.name,archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise RuntimeError('The Node download failed its checksum check.')
    target=root/'tools';target.mkdir(exist_ok=True)
    try:
        if ext=='.zip':
            with zipfile.ZipFile(archive) as z:
                for n in z.namelist():
                    if not contained(target/n,target):raise ValueError('Unsafe archive')
                z.extractall(target)
        else:
            with tarfile.open(archive) as t:
                # Official Node archives contain relative symlinks to npm.
                for m in t.getmembers():
                    if not contained(target/m.name,target):raise ValueError('Unsafe archive')
                for m in t.getmembers():
                    if m.issym() and not contained(target/Path(m.name).parent/m.linkname,target):raise ValueError('Unsafe archive link')
                    if m.islnk() and not contained(target/m.linkname,target):raise ValueError('Unsafe archive link')
                t.extractall(target)
    finally:archive.unlink(missing_ok=True)
    return str(node),str(npm)


def ensure_render(root,env,install):
    node,npm=ensure_node(root,env,install)
    folder=root/'npm';packages=LOCK['npm'];valid=True
    for name,version in packages.items():
        try:valid=valid and json.loads((folder/'node_modules'/name/'package.json').read_text())['version']==version
        except (FileNotFoundError,KeyError,ValueError):valid=False
    if not valid:
        if not install:return None
        folder.mkdir(parents=True,exist_ok=True)
        e=dict(env,PATH=str(Path(node).parent)+os.pathsep+env.get('PATH',''))
        run([npm,'install','--prefix',folder,'--no-audit','--no-fund','--save-exact',*[k+'@'+v for k,v in packages.items()]],e,cwd=folder,capture=False)
    if not node:return None
    pkg=json.loads((folder/'node_modules/hyperframes/package.json').read_text())
    b=pkg['bin'];rel=b if isinstance(b,str) else b['hyperframes']
    cli=folder/'node_modules/hyperframes'/rel
    return {'node':node,'cli':str(cli),'gsap':str(folder/'node_modules/gsap/dist/gsap.min.js')}


def ensure(features=('core',),install=True):
    features=set(features)
    if not features<=FEATURES:raise ValueError('Unknown features: '+','.join(features-FEATURES))
    if features & {'voice','asr'} and not (sys.platform=='darwin' and platform.machine().lower() in ('arm64','aarch64')):
        raise RuntimeError(
            f'The default MLX narration/transcription requires macOS on Apple Silicon; detected {sys.platform} {platform.machine()}. '
            'This implementation cannot run here. Follow references/runtime.md to investigate a compatible setup for this machine, '
            'preserving the approved model and voice where possible. Record any adaptation in the project and check a short sample before production.'
        )
    if features:features.add('core')
    root=runtime_home();env=child_env(root)
    if install:root.mkdir(parents=True,exist_ok=True)
    result={'runtime_home':str(root),'features':sorted(features),'ready':True,'missing':[]}
    if not features:return result,env
    uv=ensure_uv(root,env,install)
    python=ensure_python(root,env,features,uv,install) if uv or not install else None
    result.update(uv=uv,python=python)
    if not python:result['missing'].append('python-packages')
    media=ensure_media(root,env,python,install) if python or not install else None
    if media:
        result.update(media);env['PATH']=str(Path(media['ffmpeg']).parent)+os.pathsep+env.get('PATH','')
    else:result['missing'].append('ffmpeg-pair')
    if 'render' in features:
        render=ensure_render(root,env,install)
        if render:
            result['render']=render;env['PATH']=str(Path(render['node']).parent)+os.pathsep+env['PATH']
            if install:
                # Chromium is handled by HyperFrames in its own user cache, never this Skill.
                run([render['node'],render['cli'],'browser','ensure'],env,cwd=root,capture=False)
            try:
                browser=run([render['node'],render['cli'],'browser','path'],env,cwd=root if root.exists() else Path.home(),timeout=30)
                result['render']['browser']=browser
            except (RuntimeError,subprocess.TimeoutExpired):result['missing'].append('render-browser')
        else:result['missing'].append('render-runtime')
    for feature,model_key,path_key in [('voice','mlx','model_path'),('asr','asr','asr_model_path')]:
        if feature not in features:continue
        result[feature+'_backend']='mlx'
        model=LOCK['models'][model_key]
        if python:
            code='''from huggingface_hub import snapshot_download
import sys
print(snapshot_download(sys.argv[1],revision=sys.argv[2],local_files_only=sys.argv[3]=='check'))
'''
            try:
                try:result[path_key]=run([python,'-c',code,model['repo'],model['revision'],'check'],env)
                except RuntimeError:
                    if not install:raise
                    result[path_key]=run([python,'-c',code,model['repo'],model['revision'],'install'],env)
            except RuntimeError:
                if install:raise
                result['missing'].append(feature+'-model')
    result['ready']=not result['missing']
    if install:
        (root/'last-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result,env


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--features',default='core');p.add_argument('--check',action='store_true');args=p.parse_args()
    try:
        info,_=ensure(filter(None,args.features.split(',')),not args.check)
        print(json.dumps(info,ensure_ascii=False,indent=2));sys.exit(0 if info['ready'] else 2)
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)
