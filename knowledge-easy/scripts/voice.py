#!/usr/bin/env python3
"""Use the selected Ryan voice with script-specific delivery instructions and preserve the native synthesis output."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import soundfile as sf
from language import resolve,CONFIG

ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'assets/voice/profile.json').read_text(encoding='utf-8'))
LOCK=json.loads((ROOT/'scripts/runtime-lock.json').read_text(encoding='utf-8'))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def instruction_for(segment):
    direction=segment.get('direction','').strip()
    if direction and direction[-1] not in '。！？；.!?;':direction+='。'
    return PROFILE['instruction_prefix']+direction+PROFILE['instruction_suffix']


def validate_profile():
    expected={'repo':PROFILE['synthesis_model'],'revision':PROFILE['model_revision']}
    if LOCK['models']['mlx']!=expected:
        raise ValueError('The voice profile and model lock do not match. Update both before generating.')
    if PROFILE['generation_mode']!='custom_voice' or not PROFILE['speaker']:
        raise ValueError('The default narrator requires the selected CustomVoice preset.')


def complete_decode(model,record):
    import mlx.core as mx
    original=model.speech_tokenizer.decode
    def decode(codes):
        if codes.shape[0]!=1:raise ValueError('Full decode guard requires batch-one unpadded generation')
        wav,lengths=original(codes);mx.eval(wav,lengths)
        record.append({'frames':int(codes.shape[1]),'reported_samples':int(lengths[0]),'full_samples':int(wav.shape[1])})
        return wav,mx.array([wav.shape[1]],dtype=mx.int32)
    model.speech_tokenizer.decode=decode


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--plan',required=True);ap.add_argument('--model',required=True);ap.add_argument('--backend',choices=['mlx'],required=True);args=ap.parse_args()
    project=Path(args.project).resolve();plan=json.loads(Path(args.plan).read_text(encoding='utf-8'));language=resolve(project,plan);tts_language=CONFIG[language]['tts']
    validate_profile()
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
        seed=int(seg.get('seed',PROFILE['default_seed']+i));limit=int(seg.get('max_tokens',3500))
        instruction=instruction_for(seg)
        mx.random.seed(seed)
        sampling={key:seg.get(key,PROFILE.get('synthesis_settings',{}).get(key)) for key in ('temperature','top_p','top_k','repetition_penalty')}
        sampling={key:value for key,value in sampling.items() if value is not None}
        results=list(model.generate_custom_voice(text=text,speaker=PROFILE['speaker'],language=tts_language,instruct=instruction,max_tokens=limit,verbose=False,**sampling))
        if not results or any(r.token_count>=limit for r in results):raise RuntimeError('Generation reached the token limit. Reject this take and regenerate the complete passage.')
        sr=results[0].sample_rate;a=np.concatenate([np.asarray(r.audio) for r in results]);tokens=[r.token_count for r in results]
        if a.ndim!=1 or not len(a) or not np.isfinite(a).all() or np.max(np.abs(a))<.001:raise RuntimeError('Invalid synthesis output.')
        pad=float(seg.get('gap_after',0))
        if pad<0 or pad>2:raise ValueError('gap_after must be 0–2 seconds; review semantic boundaries explicitly')
        file=dest/f'take-{i+1:02}.wav';sf.write(file,a,sr,subtype='PCM_24')
        records.append({'id':seg.get('id',str(i+1)),'text':seg['text'],'tts_text':text,'seed':seed,'tokens':tokens,'start':offset,'seconds':len(a)/sr,'direction':seg.get('direction',''),'instruct':instruction,'gap_after':pad,'sampling':sampling,'file':str(file.relative_to(project))})
        waves += [a,np.zeros(round(pad*sr),dtype='float32')];offset+=(len(a)/sr)+pad
        print(f'Passage {i+1}/{len(segments)}: {len(a)/sr:.2f}s',flush=True)
    audio=np.concatenate([np.zeros(round(.10*sr)),*waves,np.zeros(round(.18*sr))])
    output=dest/'narration.wav';sf.write(output,audio,sr,subtype='PCM_24')
    report={'variant':'native','samples':len(audio),'sample_rate':sr,'seconds':len(audio)/sr,
            'pitch_shift_semitones':0,'playback_speed':1,'gain_db':0}
    report.update(language=language,backend=args.backend,reference_sha256=sha(ref),reference_role='listening_baseline',
                  model=args.model,model_repo=PROFILE['synthesis_model'],model_revision=PROFILE['model_revision'],
                  generation_mode=PROFILE['generation_mode'],speaker=PROFILE['speaker'],
                  segments=records,decode=decodes,review='Pending listening review of naturalness, meaningful emphasis, pauses, and intact beginnings and endings. Approval of the default reference does not automatically pass a new script.',
                  output='audio/narration/narration.wav',output_sha256=sha(output))
    (dest/'generation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(str(output))

if __name__=='__main__':main()
