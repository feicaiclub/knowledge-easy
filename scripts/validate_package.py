#!/usr/bin/env python3
"""Check closure and integrity of the distributable, without installing anything."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
TEXT={'.md','.py','.json','.js','.css','.html','.sh','.ps1','.txt'}
FORBIDDEN_DIRS={'node_modules','__pycache__','.venv','venv','.git','snapshots','blobs'}


def package_paths(root):
    return [p for p in root.rglob('*') if '.git' not in p.relative_to(root).parts]


def scan(root):
    paths=package_paths(root)
    errors=[];files=[p for p in paths if p.is_file()]
    skills=[p for p in files if p.name=='SKILL.md']
    if skills!=[root/'SKILL.md']:errors.append('Exactly one root SKILL.md required')
    for p in paths:
        if p.is_symlink():errors.append('Symlink: '+str(p.relative_to(root)))
        if p.is_dir() and p.name in FORBIDDEN_DIRS:errors.append('Bundled runtime/cache: '+str(p.relative_to(root)))
    for p in files:
        rel=str(p.relative_to(root))
        if p.name in ['CLAUDE.md','AGENTS.md','.env'] or p.suffix in ['.safetensors','.gguf','.pyc','.exe','.whl']:errors.append('Forbidden bundle file: '+rel)
        if rel.startswith('assets/packaging/previews/') and p.suffix=='.mp4':errors.append('Bundled demo video: '+rel)
        if p.suffix not in TEXT:continue
        text=p.read_text(encoding='utf-8')
        personal_pattern='/'+'Users/'+r'[^\s/]+/|/'+'home/'+r'[^\s/]+/|[A-Z]:\\'+'Users'+r'\\'
        if re.search(personal_pattern,text):errors.append('Personal absolute path: '+rel)
        if re.search(r'\bsk[_-][A-Za-z0-9_-]{25,}',text):errors.append('Possible credential: '+rel)
        if p.suffix=='.py':
            try:ast.parse(text)
            except SyntaxError as e:errors.append(f'{rel}: {e}')
        links=[]
        if p.suffix=='.md':links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',text)
        elif p.suffix=='.html':links=re.findall(r'(?:href|src|poster)=[\"\']([^\"\']+)',text)+re.findall(r'url\([\"\']?([^\)\"\']+)',text)
        elif p.suffix=='.css':links=re.findall(r'url\([\"\']?([^\)\"\']+)',text)
        for link in links:
            link=unquote(link.strip('<>').split('#')[0].split('?')[0])
            if not link or re.match(r'^(?:https?:|data:|mailto:)',link):continue
            if rel=='assets/lazy-studio/index.html' and link=='/queue':continue
            if rel=='assets/lazy-studio/index.html' and link.startswith('/'):link=link.lstrip('/')
            target=(p.parent/link).resolve()
            try:target.relative_to(root.resolve())
            except ValueError:errors.append(f'Escaping reference: {rel}: {link}');continue
            if not target.exists():errors.append(f'Missing reference: {rel}: {link}')
    profile=json.loads((root/'assets/voice/profile.json').read_text())
    if hashlib.sha256((root/'assets/voice'/profile['reference_file']).read_bytes()).hexdigest()!=profile['reference_sha256']:errors.append('Voice reference hash differs')
    return {'files':len(files),'bytes':sum(p.stat().st_size for p in files),'one_skill':len(skills)==1,'errors':errors}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',action='store_true');p.add_argument('--verify-manifest',action='store_true');a=p.parse_args()
    result=scan(ROOT)
    if a.verify_manifest:
        manifest=json.loads((ROOT/'package-manifest.json').read_text())
        current={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in package_paths(ROOT) if p.is_file() and p.name!='package-manifest.json'}
        if current!=manifest['sha256']:result['errors'].append('Manifest differs from bundle')
    if a.manifest and not result['errors']:
        files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in package_paths(ROOT) if p.is_file() and p.name!='package-manifest.json'}
        (ROOT/'package-manifest.json').write_text(json.dumps({'skill':'zhulong-skill','sha256':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
