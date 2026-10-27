"""Chinese production language and caption limits."""
import json
from pathlib import Path

ALIASES={'zh':'zh-CN','zh-cn':'zh-CN','chinese':'zh-CN','mandarin':'zh-CN','中文':'zh-CN'}
CONFIG={'zh-CN':{'tts':'Chinese','asr':'zh','caption_font':'notosanssc-NotoSansSC[wght].ttf'}}

def normalize(value):
    language=ALIASES.get(str(value).strip().lower())
    if not language:raise ValueError('This version produces Chinese-language videos only. Use zh-CN.')
    return language

def resolve(project,document=None):
    p=Path(project)/'project.json'
    settings=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    # Earlier projects predate the language field and were Chinese.
    language=normalize(settings.get('language','zh-CN'))
    if document and document.get('language') and normalize(document['language'])!=language:
        raise ValueError('Project and document languages differ. Update the project, film, and voice plan together.')
    return language

def caption_lines(text,language):
    language=normalize(language)
    line=text.strip()
    if len(line.splitlines())>1 or len(line)>26:
        raise ValueError('Keep Chinese captions on one line. Split at natural phrase boundaries and align to the speech; do not shrink or truncate the text.')
    return line
