#!/usr/bin/env python3
"""Place multiple music/SFX cues and optional narration-driven ducking."""
import sys
sys.dont_write_bytecode=True
import argparse,json,subprocess
from pathlib import Path
from vibe import local,save

p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--plan',required=True);a=p.parse_args()
root=Path(a.project).resolve();plan=json.loads(Path(a.plan).read_text(encoding='utf-8'));duration=float(plan['duration'])
def seconds(path):
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(path)]))
    return float(meta['format']['duration'])
narration=local(root,plan['narration'])
if duration < seconds(narration)-.001:raise ValueError('The mix is shorter than the narration. Extend the timeline rather than cutting speech.')
output=root/plan.get('output','audio/mix.wav');output.resolve().relative_to(root)
if output.exists():raise ValueError('This mix already exists. Choose a new output filename.')
output.parent.mkdir(parents=True,exist_ok=True)
cmd=['ffmpeg','-v','error','-y','-i',str(local(root,plan['narration']))];chains=[];music=[];effects=[]
for i,cue in enumerate(plan.get('cues',[]),1):
    cmd+=['-i',str(local(root,cue['src']))]
    start=float(cue['start']);length=float(cue['duration']);source=float(cue.get('media_start',0));fi=float(cue.get('fade_in',.25));fo=float(cue.get('fade_out',.5))
    if min(start,length,source,fi,fo)<0 or length==0 or start+length>duration+.01 or fi>length or fo>length:raise ValueError('Invalid music or sound-effect cue timing.')
    gain=float(cue.get('gain_db',-18 if cue.get('role','music')=='music' else -12))
    if source+length>seconds(local(root,cue['src']))+.01:raise ValueError('The music or sound-effect source is too short for this cue.')
    chain=f'[{i}:a]atrim=start={source}:duration={length},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB'
    if fi:chain+=f',afade=t=in:d={fi}'
    if fo:chain+=f',afade=t=out:st={length-fo}:d={fo}'
    chain+=f',adelay={round(start*1000)}:all=1[c{i}]';chains.append(chain)
    (music if cue.get('role','music')=='music' else effects).append(f'[c{i}]')
duck=bool(plan.get('duck_music',True) and music)
chains.insert(0,f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=duration={duration}'+(',asplit=2[v][det]' if duck else '[v]'))
parts=['[v]']
if music:
    chains.append(''.join(music)+f'amix=inputs={len(music)}:normalize=0:duration=longest[mb]')
    if duck:chains.append('[mb][det]sidechaincompress=threshold=0.03:ratio=4:attack=25:release=250[md]');parts.append('[md]')
    else:parts.append('[mb]')
parts+=effects
chains.append(''.join(parts)+f'amix=inputs={len(parts)}:normalize=0:duration=longest,apad,atrim=duration={duration},alimiter=limit=0.841395:level=false:latency=true[out]')
subprocess.run([*cmd,'-filter_complex',';'.join(chains),'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(output)],check=True)
save(output.with_suffix('.json'),{'plan':plan,'filters':chains,'output':str(output.relative_to(root)),'review':'Default gain is a starting point. Review the actual music level by listening.'})
print(output)
