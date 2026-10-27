#!/usr/bin/env python3
"""Reuse the film's MLX Whisper large-v3 transcription and word timing."""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

from bootstrap import LOCK
from language import resolve, CONFIG


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--file', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--prompt', default='')
    args = parser.parse_args()
    project = Path(args.project).resolve()
    source = (project / args.file).resolve()
    relative = source.relative_to(project)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    import mlx_whisper
    parameters = {
        'language': CONFIG[resolve(project)]['asr'],
        'word_timestamps': True,
        'condition_on_previous_text': False,
        'initial_prompt': args.prompt,
    }
    result = mlx_whisper.transcribe(
        str(source), path_or_hf_repo=args.model, **parameters,
    )
    result.update({
        '_source_sha256': source_hash,
        'source': relative.as_posix(),
        'backend': 'mlx-whisper',
        'backend_version': version('mlx-whisper'),
        'model': LOCK['models']['asr'],
        'parameters': parameters,
        'note': 'Use transcription to check omissions, repetitions, and timing. It cannot certify pronunciation, tone, accent, or naturalness.',
    })
    out = project / 'review/transcript.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
