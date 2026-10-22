#!/usr/bin/env python3
"""Fixed independent reference, semantic takes, complete decode and body-v1."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from language import resolve,CONFIG
from pedalboard import time_stretch

ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'assets/voice/profile.json').read_text(encoding='utf-8'))
FINISH=json.loads((ROOT/'assets/voice/timbre-body-v1.json').read_text(encoding='utf-8'))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def complete_decode(model,record):
    import mlx.core as mx
    original=model.speech_tokenizer.decode
    def decode(codes):
        if codes.shape[0]!=1:raise ValueError('Full decode guard requires batch-one unpadded generation')
        wav,lengths=original(codes);mx.eval(wav,lengths)
        record.append({'frames':int(codes.shape[1]),'reported_samples':int(lengths[0]),'full_samples':int(wav.shape[1])})
        return wav,mx.array([wav.shape[1]],dtype=mx.int32)
    model.speech_tokenizer.decode=decode


def loudness(p):
    r=subprocess.run(['ffmpeg','-v','info','-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1])


def finish(source,target):
    x,sr=sf.read(source,dtype='float32')
    if x.ndim!=1:raise ValueError('Narration must be mono')
    # Choose existing quiet regions only. Never remove speech or change pauses.
    step=round(.02*sr);n=len(x)//step
    rms=np.sqrt(np.mean(x[:n*step].reshape(-1,step).astype('float64')**2,axis=1)+1e-15)
    quiet=[];start=None
    for i,v in enumerate([*rms,1.]):
        if v<.008 and start is None:start=i
        elif v>=.008 and start is not None:
            if (i-start)*.02>=.28:quiet.append((start+i)*.01)
            start=None
    cuts=[0.]
    while len(x)/sr-cuts[-1]>35:
        options=[t for t in quiet if 12<=t-cuts[-1]<=34]
        if not options:break
        cuts.append(min(options,key=lambda t:abs(t-cuts[-1]-27)))
    cuts.append(len(x)/sr);edges=[round(t*sr) for t in cuts];out=np.zeros_like(x)
    for a,b in zip(edges,edges[1:]):
        lo=max(0,a-round(.6*sr));hi=min(len(x),b+round(.6*sr))
        chunk=np.asarray(time_stretch(x[lo:hi],sr,stretch_factor=1.,pitch_shift_in_semitones=FINISH['pitch_shift_semitones'],high_quality=True,transient_mode='crisp',transient_detector='compound',retain_phase_continuity=True,preserve_formants=False)).reshape(-1)
        if len(chunk)!=hi-lo:raise RuntimeError('Voice finishing changed the duration. This take cannot be delivered.')
        out[a:b]=chunk[a-lo:b-lo]
    temp=target.with_name(target.stem+'-processing.wav');eq=target.with_name(target.stem+'-eq.wav')
    sf.write(temp,out,sr,subtype='FLOAT')
    try:
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-af','highpass=f=45,equalizer=f=160:t=q:w=0.75:g=1.2,equalizer=f=420:t=q:w=1:g=-0.35','-c:a','pcm_f32le',str(eq)],check=True)
        gain=float(loudness(source)['input_i'])-float(loudness(eq)['input_i'])
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(eq),'-af',f'volume={gain:.8f}dB,alimiter=limit=0.841395:attack=5:release=50:level=false:latency=true','-c:a','pcm_s24le',str(target)],check=True)
        y,_=sf.read(target)
        if len(y)!=len(x):raise RuntimeError('Finishing changed the total sample count. Delivery is blocked.')
        return {'variant':FINISH['id'],'samples':len(y),'sample_rate':sr,'seconds':len(y)/sr,'processing_boundaries':cuts,'duration_change_samples':0,'gain_db':gain}
    finally:
        temp.unlink(missing_ok=True);eq.unlink(missing_ok=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--plan',required=True);ap.add_argument('--model',required=True);ap.add_argument('--backend',choices=['mlx'],required=True);args=ap.parse_args()
    project=Path(args.project).resolve();plan=json.loads(Path(args.plan).read_text(encoding='utf-8'));language=resolve(project,plan);tts_language=CONFIG[language]['tts']
    ref=ROOT/'assets/voice'/PROFILE['reference_file']
    if sha(ref)!=PROFILE['reference_sha256']:raise ValueError('The voice reference failed its checksum check.')
    segments=plan['segments']
    if not segments:raise ValueError('The voice plan has no passages.')
    dest=project/'audio/narration';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'narration.wav').exists():raise ValueError('Use a new project copy or archive audio/narration first. Existing takes will not be overwritten.')
    import mlx.core as mx
    from mlx_audio.tts.utils import load_model
    model=load_model(args.model);decodes=[];complete_decode(model,decodes)
    waves=[];records=[];offset=.10
    for i,seg in enumerate(segments):
        text=seg.get('tts_text',seg['text']).strip()
        if not text:raise ValueError('Empty segment')
        seed=int(seg.get('seed',22102271+i));limit=int(seg.get('max_tokens',3500))
        # Base does not offer a reliable instruct control. Record direction, do not pretend it is applied.
        mx.random.seed(seed)
        results=list(model.generate(text=text,ref_audio=str(ref),ref_text=PROFILE['reference_text'],lang_code=tts_language,temperature=float(seg.get('temperature',.65)),top_p=.9,top_k=50,repetition_penalty=1.5,max_tokens=limit,split_pattern=None,verbose=False))
        if not results or any(r.token_count>=limit for r in results):raise RuntimeError('Generation reached the token limit. Reject this take and regenerate the complete passage.')
        sr=results[0].sample_rate;a=np.concatenate([np.asarray(r.audio) for r in results]);tokens=[r.token_count for r in results]
        if not len(a) or not np.isfinite(a).all() or np.max(np.abs(a))<.001:raise RuntimeError('Invalid synthesis output.')
        pad=float(seg.get('gap_after',0))
        if pad<0 or pad>2:raise ValueError('gap_after must be 0–2 seconds; review semantic boundaries explicitly')
        file=dest/f'take-{i+1:02}.wav';sf.write(file,a,sr,subtype='PCM_24')
        records.append({'id':seg.get('id',str(i+1)),'text':seg['text'],'tts_text':text,'seed':seed,'tokens':tokens,'start':offset,'seconds':len(a)/sr,'direction':seg.get('direction',''),'gap_after':pad,'file':str(file.relative_to(project))})
        waves += [a,np.zeros(round(pad*sr),dtype='float32')];offset+=(len(a)/sr)+pad
        print(f'Passage {i+1}/{len(segments)}: {len(a)/sr:.2f}s',flush=True)
    raw=dest/'narration-base.wav';sf.write(raw,np.concatenate([np.zeros(round(.10*sr)),*waves,np.zeros(round(.4*sr))]),sr,subtype='PCM_24')
    report=finish(raw,dest/'narration.wav')
    report.update(language=language,backend=args.backend,reference_sha256=sha(ref),model=args.model,segments=records,decode=decodes,review='Listen to the take and check its transcript. Technical checks do not establish naturalness.',output='audio/narration/narration.wav')
    (dest/'generation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(str(dest/'narration.wav'))

if __name__=='__main__':main()
