# Production tools

`<skill>` is this Skill folder; `<project>` is the film project's absolute path. The examples use macOS/Linux syntax. On Windows, replace `sh .../run.sh` with `& .../run.ps1`. Run only the steps the current request needs.

```sh
sh "<skill>/scripts/run.sh" init --project "<project>" --language en-US
```

This creates the project, a versioned component snapshot, fonts, and empty film and voice plans. Use `--language zh-CN` for Chinese. Keep each episode's research, source footage, captions, audio, and feedback in its project, outside the Skill.

## From script to export

1. Research and write. Record the agreed facts, viewpoint, constraints, and approved elements. Keep useful evidence without creating documents just to fill a checklist.
2. Fill `voice-plan.json` with complete passages. Use `tts_text` for pronunciation changes, `direction` for delivery notes, and `gap_after` only for a pause you have reviewed. Keep the original spelling in the script and captions.
3. Check the recording for complete sentences, pronunciation, voice consistency, and natural transitions. Transcription can help. Plan shot timing, music changes, and graphic reveals around the finished narration.
4. Configure scenes and captions in `film.json`. The builder is a starting point, not a creative ceiling. Custom scenes can use the same fonts, colors, layout principles, and shared component source.
5. Check the composition, watch the motion, render, and review the actual export. Record anything that has not been watched or heard.

```sh
sh "<skill>/scripts/run.sh" voice --project "<project>" --plan voice-plan.json
sh "<skill>/scripts/run.sh" transcribe --project "<project>" --file audio/narration/narration.wav
sh "<skill>/scripts/run.sh" mix --project "<project>" --plan music-plan.json
sh "<skill>/scripts/run.sh" build --project "<project>"
sh "<skill>/scripts/run.sh" check --project "<project>"
sh "<skill>/scripts/run.sh" snapshot --project "<project>" --at 0.2,1.2,3.5
sh "<skill>/scripts/run.sh" preview --project "<project>"
sh "<skill>/scripts/run.sh" render --project "<project>" --output final/film-v1.mp4
sh "<skill>/scripts/run.sh" verify --project "<project>" --file final/film-v1.mp4
```

Transcription uses the original MLX Whisper large-v3 implementation. It saves the recognized text, word timestamps, model revision, and source-audio hash in `review/transcript.json`. For unusual names, add `--prompt "Names and terminology"`; do not supply the expected script as recognition evidence.

Existing delivery files are not overwritten. Use a new output filename for a revision. Set `final_file` and `locked` in `project.json` from actual review decisions; a tool finishing does not make a film approved.

## Film configuration

The default canvas is 1920×1080 at 30 fps. Times are in seconds; component cues are local to the scene. Redesign the layout for portrait video rather than stretching a landscape composition.

```json
{
  "title": "The question behind the choice",
  "language": "en-US",
  "fps": 30,
  "duration": 8,
  "mix": "audio/mix.wav",
  "scenes": [{
    "id": "evidence-01",
    "start": 0,
    "duration": 8,
    "purpose": "Establish the premise before revealing the distinction.",
    "background": {
      "src": "assets/media/context.mp4",
      "media_start": 0,
      "grading": {"adjust": {"exposure": -0.7}, "effects": {"blur": 0.6}}
    },
    "component": "quote-reveal",
    "data": {"lead": "The same event", "emphasis": "A different\ninterpretation"},
    "cues": {"lead": 0.4, "emphasis": 2.7}
  }],
  "subtitles": [{"start": 0.3, "end": 2.5, "text": "The same event can lead to a different interpretation."}]
}
```

For a footage-only scene, use `footage` with the same fields as `background` and omit `component`. Caption endpoints are snapped to frames before their duration is calculated. English captions wrap at word boundaries and reject more than two lines. Split a long caption into well-timed phrases instead of shrinking its type.

All media paths are relative to the project root. Register every moving placement: main shots, backgrounds, and video in cards.

## Footage and audio plans

`assets.json` stores sources and placements. Sources record origin, people, period, usable ranges, and original shot boundaries. Each placement has `id`, `file`, `original_shots`, and `purpose`; still portraits may use `static: true`. Cropping, renaming, retiming, or taking a different slice does not make an original shot new. `audit-media` detects duplicates in the ledger; also compare the ledger with every compiled video element.

`music-plan.json` contains `narration`, `duration`, `output`, and `cues`. Each cue has `src`, `start`, `duration`, `media_start`, `gain_db`, `fade_in`, `fade_out`, and `role` (`music` or `sfx`). Set `duck_music: false` to disable automatic music ducking. Default gains are starting points; balance each actual track against the narration by listening. The mix cannot be shorter than the narration, and the film cannot be shorter than its mix.

Use `download --project <project> --url <url>` to acquire footage. A successful download does not establish narrative fit or publication rights. Keep source and license notes in the project.
