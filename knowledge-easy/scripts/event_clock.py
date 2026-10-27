"""One optional event clock for semantic actions and audio cues."""
import math,re


def beats(film):
    result={};duration=float(film['duration'])
    for item in film.get('beats',[]):
        key=item['id'];time=float(item['time'])
        if not re.fullmatch(r'[A-Za-z][\w-]*',key) or key in result:raise ValueError('Beat IDs must be valid and unique.')
        if not math.isfinite(time) or not 0<=time<duration:raise ValueError('Beat lies outside the film: '+key)
        result[key]=time
    return result


def cue_start(cue,film):
    if 'event' not in cue:return float(cue['start'])
    if 'start' in cue:raise ValueError('Use event or start for an audio cue, not both.')
    lookup=beats(film)
    if cue['event'] not in lookup:raise ValueError('Unknown audio event: '+cue['event'])
    value=lookup[cue['event']]+float(cue.get('offset',0))
    if not math.isfinite(value) or value<0:raise ValueError('Invalid audio-event offset.')
    return value
