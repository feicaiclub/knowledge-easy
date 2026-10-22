"""Production language, separate from the English authoring interface."""
import json,textwrap
from pathlib import Path

ALIASES={'en':'en-US','en-us':'en-US','english':'en-US','zh':'zh-CN','zh-cn':'zh-CN','chinese':'zh-CN','mandarin':'zh-CN'}
CONFIG={'en-US':{'tts':'English','asr':'en','caption_font':'inter.ttf'},'zh-CN':{'tts':'Chinese','asr':'zh','caption_font':'notosanssc-NotoSansSC[wght].ttf'}}

def normalize(value):
    language=ALIASES.get(str(value).strip().lower())
    if not language:raise ValueError('Supported production languages are en-US and zh-CN.')
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
    limit=58 if language=='en-US' else 26
    lines=[]
    for paragraph in text.splitlines():
        if language=='en-US':
            lines+=textwrap.wrap(paragraph,width=limit,break_long_words=False,break_on_hyphens=False)
        else:lines += [paragraph[i:i+limit] for i in range(0,len(paragraph),limit)]
    if len(lines)>2:raise ValueError('Caption exceeds two lines. Split it at a phrase boundary and retime the cues.')
    if any(len(s)>limit for s in lines):raise ValueError('Caption contains an unbroken word that will not fit.')
    return '\n'.join(lines)
