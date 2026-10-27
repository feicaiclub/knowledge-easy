"""中文制作入口与字幕边界。"""
import json
from pathlib import Path

ALIASES={'zh':'zh-CN','zh-cn':'zh-CN','chinese':'zh-CN','mandarin':'zh-CN','中文':'zh-CN'}
CONFIG={'zh-CN':{'tts':'Chinese','asr':'zh','caption_font':'notosanssc-NotoSansSC[wght].ttf'}}

def normalize(value):
    language=ALIASES.get(str(value).strip().lower())
    if not language:raise ValueError('当前版本只制作中文，请使用 zh-CN。')
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
        raise ValueError('中文字幕保持单行；请在自然语意处拆分并对齐口播，不缩字、不截字。')
    return line
