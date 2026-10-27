from pathlib import Path
import json, math, html, re, shutil
from contextvars import ContextVar
import importlib.util
_support_spec = importlib.util.spec_from_file_location("base_support", Path(__file__).with_name("base_support.py"))
SUPPORT = importlib.util.module_from_spec(_support_spec)
_support_spec.loader.exec_module(SUPPORT)
_STATE = ContextVar("base_design_state", default=None)
P = Path(__file__).resolve().parent
K = P

_LANG = 'zh-CN'
_COPY = json.loads((P/'base-copy.json').read_text(encoding='utf-8'))
def copy_text(key):
    return _COPY[key]

def language():
    state = _STATE.get()
    return state.locale if state else 'zh-CN'

E = html.escape
DURATION = 8
PALETTE = {'ink': '#151c1c', 'paper': '#efe4ce', 'gold': '#d8b676', 'jade': '#8db7b2', 'wine': '#562331'}
ITEMS = [('hero', copy_text('s000'), copy_text('s001'), copy_text('s002'), copy_text('s003'), copy_text('s004')), ('compare', copy_text('s005'), copy_text('s006'), copy_text('s007'), copy_text('s008'), copy_text('s009')), ('chapter', copy_text('s010'), copy_text('s011'), copy_text('s012'), copy_text('s013'), copy_text('s014')), ('evidence', copy_text('s015'), copy_text('s016'), copy_text('s017'), copy_text('s018'), copy_text('s019')), ('relation', copy_text('s020'), copy_text('s021'), copy_text('s022'), copy_text('s023'), copy_text('s024')), ('feedback', copy_text('s025'), copy_text('s026'), copy_text('s027'), copy_text('s028'), copy_text('s029')), ('quantity', copy_text('s030'), copy_text('s031'), copy_text('s032'), copy_text('s033'), copy_text('s034')), ('timeline', copy_text('s035'), copy_text('s036'), copy_text('s037'), copy_text('s038'), copy_text('s039')), ('map-focus', copy_text('s040'), copy_text('s041'), copy_text('s042'), copy_text('s043'), copy_text('s044')), ('map-route', copy_text('s045'), copy_text('s046'), copy_text('s047'), copy_text('s048'), copy_text('s049')), ('map-period', copy_text('s050'), copy_text('s051'), copy_text('s052'), copy_text('s053'), copy_text('s054')), ('context', copy_text('s055'), copy_text('s056'), copy_text('s057'), copy_text('s058'), copy_text('s059'))]

def video(id, name, rect=None, blur=0, rate=1, start=0):
    state = _STATE.get()
    if state and state.production:
        return state.media(id, rect)
    style = ''
    if rect:
        (x, y, w, h) = rect
        style = f'left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
    grade = {'adjust': {'contrast': 0.07, 'highlights': -0.12, 'shadows': -0.02, 'saturation': -0.14, 'temperature': 0.015}, 'effects': {'blur': blur}}
    return f'<video id="{id}" class="clip kp-bg" src="assets/media/{name}.mp4" data-start="0" data-duration="8" data-media-start="{start}" data-playback-rate="{rate}" data-hf-media-start-basis="local" data-track-index="0" data-color-grading="{E(json.dumps(grade), quote=True)}" muted playsinline style="{style}"></video>'

def photo(id, name, x, y, w, h, shape='', label='', rate=1, start=0):
    state = _STATE.get()
    if state and state.production and label:
        label = state.copy(id + '-label', label, w - 52, 34)
    return f'<div id="{id}" class="kp-photo {shape}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">' + video(id + '-film', name, rate=rate, start=start) + (f'<div id="{id}-label" class="kp-photo-label">{E(label)}</div>' if label else '') + '</div>'

def text(id, copy, x, y, size=70, kind='kp-title', width=None, color=None):
    state = _STATE.get()
    if state and state.production:
        copy = E(state.copy(id, copy, width or min(560, 1770-x), size, decorative='kp-ghost' in kind)).replace('\n', '<br>')
    centered = bool(width and (width >= 1100 or id.endswith(('-note', '-q', '-question'))))
    if centered:
        x = (1920 - width) / 2
    st = f'position:absolute;left:{x}px;top:{y}px;font-size:{size}px;'
    if 'kp-title' in kind and 'kp-ghost' not in kind:
        raw=html.unescape(re.sub(r'<[^>]+>','',str(copy)))
        short=max((len(line) for line in raw.splitlines()),default=0)<=4 and width is None
        st+='letter-spacing:'+('7px' if short else '1.2px')+';'
    if width:
        st += f'width:{width}px;'
    if centered:
        st += 'text-align:center;'
    if color:
        st += f'color:{color};'
    decorative = ' aria-hidden="true" data-layout-ignore="true"' if 'kp-ghost' in kind else ''
    return f'<div id="{id}" class="{kind}" style="{st}"{decorative}>{copy}</div>'

def enter(id, at=0.4, x=0, y=18, d=0.5):
    state = _STATE.get()
    if state and state.production:
        at, d = state.motion(id, at, d)
    return f"tl.fromTo('#{id}',{{opacity:0,x:{x},y:{y}}},{{opacity:1,x:0,y:0,duration:{d},ease:'power3.out'}},{at});"

def draw(id, at=1, d=1):
    state = _STATE.get()
    if state and state.production:
        at, d = state.motion(id, at, d, relationship=True)
    return f"{{const p=document.getElementById('{id}'),n=p.getTotalLength();p.style.strokeDasharray=n;p.style.strokeDashoffset=n;tl.fromTo(p,{{strokeDashoffset:n}},{{strokeDashoffset:0,duration:{d},ease:'power2.inOut'}},{at});const a=document.getElementById('{id}-head');if(a)tl.fromTo(a,{{opacity:0}},{{opacity:1,duration:.12}},{at + d - 0.1});}}"

def path(id, d, color='#d8b676', w=3, arrow=True):
    return f'<path id="{id}" d="{d}" fill="none" stroke="{color}" stroke-width="{w}"' + (f' marker-end="url(#{id}-arrow)"' if arrow else '') + '/>' + (f'<defs><marker id="{id}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path id="{id}-head" d="M1 1 L9 5 L1 9" fill="none" stroke="{color}" stroke-width="1.1"/></marker></defs>' if arrow else '')

def svg(content):
    return f'<svg class="kp-svg" viewBox="0 0 1920 1080" aria-hidden="true">{content}</svg>'

def background(prefix, name='book', blur=0.3):
    state = _STATE.get()
    if state and state.production:return ''
    return video(prefix + '-bg', name, blur=blur, start=0.15) + '<div class="kp-wash"></div>'

def map_base(prefix, view=(70, 15, 140, 55), w=1680, h=770):
    import importlib.util
    spec = importlib.util.spec_from_file_location('pack_geography', K / 'geography.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.map_base(prefix, view, w, h, K / 'maps')

def map_pin(prefix, point, lon, lat, label, color='#874a47', dx=22, dy=-25, occupied=None):
    (x, y) = point(lon, lat)
    units = sum(1 if ord(c)>255 else .56 for c in html.unescape(label))
    production = bool(_STATE.get() and _STATE.get().production)
    size = min(35 if production else 32, (280 if production else 240) / max(1, units))
    assert size >= (34.2 if production else 22), 'Shorten the place label or use a separate inset.'
    width = units * size
    anchor = 'start'
    if x + dx + width > point.width - 20:
        dx = -22
        anchor = 'end'
    occupied = [] if occupied is None else occupied
    placed = False

    def box(offset):
        left = x + dx - (width if anchor == 'end' else 0)
        return (left, y + offset - size, width, size + 8)
    for offset in [dy, 45, -75, 85]:
        q = box(offset)
        if q[1] < 15 or q[1] + q[3] > point.height - 18:
            continue
        if not any((q[0] < b[0] + b[2] + 10 and q[0] + q[2] + 10 > b[0] and (q[1] < b[1] + b[3] + 8) and (q[1] + q[3] + 8 > b[1]) for b in occupied)):
            dy = offset
            placed = True
            break
    assert placed, 'Map labels are too dense; tighten the map viewport or shorten labels.'
    occupied.append(box(dy))
    return f'<g id="{prefix}"><circle cx="{x:.2f}" cy="{y:.2f}" r="10" fill="{color}"/><circle cx="{x:.2f}" cy="{y:.2f}" r="18" fill="none" stroke="{color}" stroke-width="2"/><text class="place-label" x="{x + dx:.2f}" y="{y + dy:.2f}" text-anchor="{anchor}" style="font-size:{size}px">{label}</text></g>'

def build_scene(i, kind, config=None):
    config = config or {}
    state = SUPPORT.State(config, kind, config.get('instance_id', f's{i:02d}'))
    token = _STATE.set(state)
    try:
        return _build_scene(i, kind, config)
    finally:
        _STATE.reset(token)

def _build_scene(i, kind, config):
    p = config.get('instance_id', f's{i:02d}')
    b = ''
    js = ''
    title = ''
    if kind == 'hero':
        b = background(p, 'chess', 0.18) + text(p + '-ghost', copy_text('s064'), 10, 35, 470, 'kp-ghost ruby')
        b += photo(p + '-portrait', 'blue', 590, 110, 740, 740, 'kp-diamond')
        b += f'<div id="{p}-edge" class="kp-diamond-border" style="left:700px;top:220px;width:520px;height:520px"></div>'
        b += text(p + '-left', copy_text('s065'), 230, 255, 126, 'kp-title gold') + text(p + '-right', copy_text('s066'), 1440 if language() == 'en-US' else 1510, 255, 112 if language() == 'en-US' else 126, 'kp-title', color='#8db7b2')
        b += text(p + '-question', copy_text('s060'), 360, 850, 58, 'kp-title', 1200)
        js += enter(p + '-portrait', 0.05, 0, 50, 1.1) + enter(p + '-edge', 0.25, 0, 0) + enter(p + '-left', 0.65, -50, 0) + enter(p + '-right', 1.35, 50, 0) + enter(p + '-question', 2.8, 0, 18)
        scene_duration = config.get('duration', 8)
        js += f"tl.fromTo('#{p}-ghost',{{x:40}},{{x:-35,duration:{scene_duration},ease:'none'}},0);tl.fromTo('#{p}-portrait-film',{{scale:1.16}},{{scale:1,duration:{scene_duration},ease:'power1.out'}},0);"
    elif kind == 'compare':
        b = background(p, 'book', 0.75) + text(p + '-ghost', copy_text('s074'), 690, 120, 660, 'kp-ghost outline')
        b += photo(p + '-a', 'book', 145, 190, 710, 600, label=copy_text('s078')) + photo(p + '-b', 'typing', 1065, 190, 710, 600, label=copy_text('s079'))
        b += text(p + '-ta', copy_text('s075'), 170, 95, 96, 'kp-title gold') + text(p + '-tb', copy_text('s076'), 1090, 95, 96, 'kp-title', color='#8db7b2')
        b += svg(path(p + '-line', 'M960 185 V800', w=2, arrow=False))
        b += text(p + '-q', copy_text('s067'), 440, 865, 56, 'kp-title', 1300)
        js += enter(p + '-a', 0.15, -65, 0) + enter(p + '-ta', 0.45, 0, 20) + enter(p + '-b', 1.35, 65, 0) + enter(p + '-tb', 1.65, 0, 20) + draw(p + '-line', 1.1, 0.7) + enter(p + '-q', 3.25, 0, 15)
    elif kind == 'chapter':
        b = background(p, 'rain', 0.22) + text(p + '-ghost', copy_text('s089'), 60, 100, 450, 'kp-ghost') + text(p + '-t', copy_text('s080'), 390, 80, 82, 'kp-title', 1450)
        chapters = config.get('chapters', [[copy_text('s090'), '从现象开始', 'chess'], [copy_text('s091'), '找到疑问', 'book'], [copy_text('s092'), '拆解原因', 'notes'], [copy_text('s093'), '重新理解', 'street']])
        assert 2 <= len(chapters) <= 5
        width = min(280, (1450 - 55 * (len(chapters) - 1)) / len(chapters))
        group = width * len(chapters) + 55 * (len(chapters) - 1)
        for (n, (word, eng, clip)) in enumerate(chapters):
            assert len(word) <= (10 if language() == "en-US" else 4)
            x = (1920 - group) / 2 + n * (width + 55)
            size = (48 if len(word) <= 7 else 40) if language() == "en-US" else (64 if len(word) <= 3 else 48)
            b += f'<div id="{p}-tab{n}" class="kp-bookmark" style="left:{x}px;width:{width}px">' + video(p + f'-film{n}', clip) + f"""<div class="shade"></div><div class="roman">{['I', 'II', 'III', 'IV', 'V'][n]}</div><div class="word" style="font-size:{size}px">{E(word)}</div><div class="caption">{E(eng)}</div></div>"""
            js += enter(p + f'-tab{n}', 0.45 + n * 0.58, 0, 80, 0.8)
        b += text(p + '-note', copy_text('s077'), 360, 865, 49, 'kp-title', 1450)
        js += enter(p + '-t', 0.1, 0, 20) + enter(p + '-note', 3.8, 0, 20)
    elif kind == 'evidence':
        b = background(p, 'book', 0.6) + text(p + '-ghost', copy_text('s094'), 20, 12, 450, 'kp-ghost')
        ev = config.get('evidence', {})
        heading = ev.get('heading', copy_text('s081'))
        questions = ev.get('questions', [copy_text('s095'), copy_text('s096'), copy_text('s097')])
        closing = ev.get('closing', copy_text('s082'))
        assert 1 <= len(questions) <= 3 and all((len(v) <= (28 if language() == "en-US" else 15) for v in questions)) and (len(closing) <= (32 if language() == "en-US" else 16)) and all((len(v) <= (15 if language() == "en-US" else 8) for v in heading.split('\n')))
        h = E(heading).replace('\n', '<br>')
        qs = '<br>'.join((E(v) for v in questions))
        b += f'<div id="{p}-paper" class="kp-paper" style="left:1080px;top:155px;width:620px;height:700px"><div class="paper-label">{E(ev.get("kicker", "READ BETWEEN THE LINES"))}</div><h2>{h}</h2><div class="paper-rule"></div><p>{qs}</p><div class="paper-rule"></div><div class="paper-caption">{E(closing)}</div></div>'
        b += photo(p + '-large', 'book', 175, 190, 775, 570, label=copy_text('s098'))
        b += text(p + '-t', copy_text('s083'), 190, 70, 90, 'kp-title gold')
        js += enter(p + '-large', 0.2, -100, 10, 1) + enter(p + '-t', 0.5, 0, 20) + enter(p + '-paper', 1.5, 100, 0, 1)
        state = _STATE.get()
        paper_at = next((x['enter_at'] for x in state.order if x['id']==p+'-paper'),1.5)
        paper_duration = min(1.2,state.duration-paper_at-.15)
        js += f"tl.fromTo('#{p}-paper',{{rotationY:-12,rotationZ:0}},{{rotationY:0,rotationZ:0,duration:{paper_duration},ease:'power3.out'}},{paper_at});"
    elif kind == 'relation':
        b = background(p, 'street', 0.8) + text(p + '-t', copy_text('s099'), 235, 80, 88, 'kp-title', 1550)
        b += photo(p + '-a', 'chess', 200, 325, 440, 420, label=copy_text('s104')) + photo(p + '-b', 'notes', 1280, 325, 440, 420, label=copy_text('s105'))
        b += photo(p + '-c', 'blue', 780, 270, 360, 520, label=copy_text('s100'))
        b += svg(path(p + '-l1', 'M665 530 H755') + path(p + '-l2', 'M1255 530 H1165', '#8db7b2'))
        b += text(p + '-n1', copy_text('s101'), 655, 420, 34, 'kp-node-label', 110) + text(p + '-n2', copy_text('s102'), 1155, 420, 34, 'kp-node-label', 110)
        js += enter(p + '-c', 0.1, 0, 40) + enter(p + '-a', 0.8, -70, 0) + enter(p + '-b', 1.5, 70, 0) + enter(p + '-t', 0.3, 0, 15) + draw(p + '-l1', 2.2, 0.7) + draw(p + '-l2', 3, 0.7) + enter(p + '-n1', 2.5, 0, 10) + enter(p + '-n2', 3.3, 0, 10)
    elif kind == 'feedback':
        b = background(p, 'typing', 0.8) + text(p + '-t', copy_text('s106'), 310, 75, 90, 'kp-title', 1500)
        positions = [(270, 300, 'clock', copy_text('s107')), (1280, 300, 'typing', copy_text('s108')), (785, 610, 'notes', copy_text('s109'))]
        for (n, (x, y, clip, label)) in enumerate(positions):
            b += photo(p + f'-p{n}', clip, x, y, 365, 240, label=label)
            js += enter(p + f'-p{n}', 0.3 + n * 0.7, 0, 35)
        b += svg(path(p + '-f1', 'M665 420 H1248') + path(p + '-f2', 'M1462 565 C1462 735 1310 735 1185 735') + path(p + '-f3', 'M755 735 C595 735 452 735 452 570'))
        js += enter(p + '-t', 0.1, 0, 20) + draw(p + '-f1', 1.05, 1) + draw(p + '-f2', 2.15, 1) + draw(p + '-f3', 3.4, 1.2)
        b += text(p + '-note', copy_text('s103'), 370, 900, 43, 'kp-title', 1400)
        js += enter(p + '-note', 4.7, 0, 15)
    elif kind == 'quantity':
        b = background(p, 'rain', 0.65) + text(p + '-ghost', copy_text('s112'), 15, 50, 450, 'kp-ghost outline')
        b += text(p + '-title', copy_text('s110'), 175, 85, 85, 'kp-title', 1650)
        total = int(config.get('total', 10))
        selected = config.get('selected', [1, 4, 7])
        assert 1 <= total <= 30 and len(set(selected)) == len(selected) and all((0 <= k < total for k in selected))
        cols = min(5, total)
        rows = math.ceil(total / cols)
        cell = min(155, 480 / rows)
        size = min(94, cell * 0.7)
        for n in range(total):
            x = 185 + n % cols * 155
            y = 345 + n // cols * cell
            b += f'<div id="{p}-dot{n}" class="kp-dot" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px"></div>'
            js += enter(p + f'-dot{n}', 0.4 + n * 0.035, 0, 20, 0.4)
        b += text(p + '-total', str(total), 1180, 280, 220, 'kp-number') + text(p + '-total-label', copy_text('s113'), 1370, 425, 42, 'kp-label')
        b += text(p + '-part', str(len(selected)), 1195, 555, 175, 'kp-number') + text(p + '-part-label', copy_text('s114'), 1330, 655, 42, 'kp-label')
        b += text(p + '-note', copy_text('s111'), 800, 880, 34, 'kp-small', 400)
        js += enter(p + '-title', 0.1, 0, 20) + enter(p + '-total', 0.65, 0, 25) + enter(p + '-total-label', 0.8, 0, 20) + enter(p + '-part', 2.5, 0, 25) + enter(p + '-part-label', 2.65, 0, 20) + enter(p + '-note', 3.5, 0, 10)
        for (j, n) in enumerate(selected):
            js += f"tl.to('#{p}-dot{n}',{{backgroundColor:'#d8b676',borderColor:'#d8b676',duration:.5}},{2.2 + j * min(0.3, 1.5 / max(1, len(selected)))});"
    elif kind == 'timeline':
        b = background(p, 'book', 0.45) + text(p + '-t', copy_text('s115'), 250, 70, 88, 'kp-title', 1550)
        b += svg(path(p + '-axis', 'M280 320 H1640', w=3) + ''.join((f'<path d="M{x} 308 V332" stroke="#d8b676" stroke-width="2"/>' for x in [405, 955, 1505])))
        for (n, (name, clip)) in enumerate(config.get('stages', [(copy_text('s116'), 'chess'), (copy_text('s117'), 'book'), (copy_text('s118'), 'notes')])):
            x = 220 + n * 550
            b += f'<div id="{p}-time{n}" class="kp-timepoint" style="left:{x}px"><div class="stamp">0{n + 1}</div><div class="photo">' + video(p + f'-time-film{n}', clip) + f'</div><div class="name">{E(name)}</div></div>'
            js += enter(p + f'-time{n}', 0.7 + n * 1.3, 0, 45)
        js += enter(p + '-t', 0.1, 0, 20) + draw(p + '-axis', 0.4, 3.2)
    elif kind in ['map-focus', 'map-route', 'map-period']:
        (b, js) = build_map_scene(p, kind, config)
    elif kind == 'context':
        b = background(p, 'chess', 0.6) + text(p + '-ghost', copy_text('s119'), 20, 60, 450, 'kp-ghost')
        b += f'<div id="{p}-window" class="kp-reveal-window">' + video(p + '-detail', 'chess') + '</div>'
        b += text(p + '-a', copy_text('s120'), 455, 80, 82, 'kp-title', 1450) + text(p + '-b', copy_text('s121'), 445, 870, 60, 'kp-title', 1450)
        js += enter(p + '-a', 0.2, 0, 20)
        state = _STATE.get()
        at, duration = state.motion(p + '-widen', 1.2, 2.8, relationship=True) if state.production else (1.2, 2.8)
        js += f"tl.fromTo('#{p}-detail',{{scale:2.3,x:340,y:65}},{{scale:1,x:0,y:0,duration:{duration},ease:'power3.inOut'}},{at});" + enter(p + '-b', 4.25, 0, 20)
    js += f"tl.fromTo('#{p}-bg',{{scale:1.055}},{{scale:1,duration:8,ease:'none'}},0);" if f'id="{p}-bg"' in b else ''
    state = _STATE.get()
    if state.production:
        b, js = state.finish(b, js)
    return (b, js)

def build_map_scene(p, kind, cfg):
    b = background(p, 'book', 0.7)
    js = ''
    if kind == 'map-focus':
        focus = cfg.get('focus', {'name': copy_text('s068'), 'lon': 108.94, 'lat': 34.34})
        default_view = [focus['lon'] - 20, focus['lat'] - 12, focus['lon'] + 20, focus['lat'] + 12] if 'focus' in cfg else [70, 15, 140, 55]
        view = tuple(cfg.get('view', default_view))
        assert view[0] <= focus['lon'] <= view[2] and view[1] <= focus['lat'] <= view[3]
        (base, xy) = map_base(p, view)
        (x, y) = xy(focus['lon'], focus['lat'])
        pin = map_pin(p + '-place', xy, focus['lon'], focus['lat'], E(focus['name']))
        ring = f'<circle id="{p}-ring" class="focus-ring" cx="{x}" cy="{y}" r="92"/>'
        b += text(p + '-t', copy_text('s061'), 160, 48, 74, 'kp-title', 1600)
        b += f'''<div id="{p}-atlas" class="kp-atlas"><svg class="kp-map" viewBox="0 0 1680 770"><g id="{p}-map-layer">{base}{ring}{pin}{copy_text('s062')}'''
        b += text(p + '-note', copy_text('s063'), 360, 945, 38, 'kp-small', 1500)
        js += enter(p + '-atlas', 0.15, 0, 40, 0.9) + enter(p + '-t', 0.3, 0, 20) + enter(p + '-place', 1.4, 0, 0) + enter(p + '-note', 3.8, 0, 15)
        state = _STATE.get()
        ring_at, ring_duration = state.motion(p+'-ring',1.2,1.0) if state.production else (1.2,1.5)
        zoom_at, zoom_duration = state.motion(p+'-zoom',2,2.2) if state.production else (2,3.6)
        js += f"tl.fromTo('#{p}-ring',{{opacity:0,scale:.55,svgOrigin:'{x} {y}'}},{{opacity:1,scale:1,duration:{ring_duration},ease:'power3.out'}},{ring_at});tl.to('#{p}-map-layer',{{scale:1.12,svgOrigin:'{x} {y}',duration:{zoom_duration},ease:'power2.inOut'}},{zoom_at});"
    elif kind == 'map-route':
        points = cfg.get('points', [{'name': copy_text('s084'), 'lon': 108.94, 'lat': 34.34}, {'name': copy_text('s085'), 'lon': 103.834, 'lat': 36.062}, {'name': copy_text('s086'), 'lon': 94.662, 'lat': 40.142}])
        assert 2 <= len(points) <= 6
        auto = [min((x['lon'] for x in points)) - 8, min((x['lat'] for x in points)) - 7, max((x['lon'] for x in points)) + 8, max((x['lat'] for x in points)) + 7]
        view = tuple(cfg.get('view', auto if 'points' in cfg else [82, 26, 119, 46]))
        assert all((view[0] <= x['lon'] <= view[2] and view[1] <= x['lat'] <= view[3] for x in points))
        (base, xy) = map_base(p, view)
        pins = ''
        roads = ''
        boxes = []
        for (n, a) in enumerate(points):
            pins += map_pin(p + f'-pin{n}', xy, a['lon'], a['lat'], E(a['name']), dx=24, dy=42 if n % 2 else -25, occupied=boxes)
            js += enter(p + f'-pin{n}', 0.8 + n * 1.5, 0, 0, 0.5)
            if n:
                (x0, y0) = xy(points[n - 1]['lon'], points[n - 1]['lat'])
                (x1, y1) = xy(a['lon'], a['lat'])
                d = f'M{x0} {y0} Q{(x0 + x1) / 2} {(y0 + y1) / 2 - 35} {x1} {y1}'
                roads += path(p + f'-route{n}', d, '#874a47', 5)
                js += draw(p + f'-route{n}', 0.7 + n * 0.95, 1.5)
        b += text(p + '-t', copy_text('s069'), 160, 48, 74, 'kp-title', 1600)
        b += f'''<div id="{p}-atlas" class="kp-atlas"><svg class="kp-map" viewBox="0 0 1680 770">{base}{roads}{pins}{copy_text('s070')}'''
        b += text(p + '-note', copy_text('s071'), 730, 945, 35, 'kp-small', 600)
        js += enter(p + '-atlas', 0.1, 0, 40) + enter(p + '-t', 0.3, 0, 20) + enter(p + '-note', 4.7, 0, 15)
    else:
        periods = cfg.get('periods', [{'label': copy_text('s087'), 'area': [[99, 32], [105, 30], [111, 33], [112, 39], [107, 42], [101, 39], [99, 32]], 'source': 'illustrative'}, {'label': copy_text('s088'), 'area': [[93, 35], [97, 31], [104, 29], [113, 32], [117, 39], [111, 44], [103, 45], [96, 41], [93, 35]], 'source': 'illustrative'}])
        assert len(periods) == 2
        b += text(p + '-t', copy_text('s072'), 160, 65, 76, 'kp-title', 1700)
        for (n, period) in enumerate(periods):
            if cfg.get('historical'):
                assert period.get('date') and period.get('source') and (period['source'] != 'illustrative'), 'Historical boundaries require dated evidence.'
            (base, xy) = map_base(p + f'-pair{n}', tuple(cfg.get('view', [78, 22, 130, 51])), 760, 490)
            geom = period.get('geometry', {'type': 'Polygon', 'coordinates': [period.get('area', [])]})
            assert geom['type'] in ['Polygon', 'MultiPolygon']
            polygons = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']
            rings = []
            for polygon in polygons:
                for ring in polygon:
                    assert len(ring) >= 4 and ring[0] == ring[-1], 'Close each GeoJSON polygon ring.'
                    coords = [xy(*pt) for pt in ring]
                    rings.append('M' + ' L'.join((f'{x:.1f} {y:.1f}' for (x, y) in coords)) + 'Z')
            d = ' '.join(rings)
            color = '#874a47' if n == 0 else '#387c79'
            area = f'<path id="{p}-area{n}" d="{d}" fill="{color}" fill-rule="evenodd" fill-opacity=".34" stroke="{color}" stroke-width="3" stroke-dasharray="8 5"/>'
            label = (str(period['date']) + ' / ' if period.get('date') else '') + period['label']
            assert sum((1 if ord(c) > 256 else 0.55 for c in label)) <= 19, 'Shorten the period caption; keep the date visible.'
            x = 160 + n * 840
            b += f'<div id="{p}-period{n}" class="kp-small-atlas" style="left:{x}px"><svg class="kp-map" viewBox="0 0 760 490">{base}{area}</svg><div class="period">{E(label)}</div></div>'
            js += enter(p + f'-period{n}', 0.4 + n * 1.3, (-1 if n == 0 else 1) * 70, 0, 0.9) + enter(p + f'-area{n}', 1.1 + n * 1.6, 0, 0, 1)
        b += text(p + '-note', copy_text('s073'), 300, 900, 48, 'kp-title', 1500)
        js += enter(p + '-t', 0.15, 0, 25) + enter(p + '-note', 3.6, 0, 20)
    return (b, js)


def render(kind, prefix, duration, data, cues=None, locale='zh-CN'):
    config = dict(data, language=locale, instance_id=prefix, duration=duration,
                  cues=cues or {}, _production=True)
    state = SUPPORT.State(config, kind, prefix)
    token = _STATE.set(state)
    try:
        body, js = _build_scene(0, kind, config)
        return {'html':'<div class="ev-component" data-editorial-component="'+kind+'">'+body+'</div>',
                'js':js, 'reading_order':state.order, 'component':kind, 'parent':kind,
                'design_reference':kind, 'implementation':'handbook-base',
                'layout':{'composition_scale':state.scale,'caption_reserve':True}}
    finally:
        _STATE.reset(token)
