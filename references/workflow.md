# Production tools

`<skill>` is this Skill folder; `<project>` is the film project's absolute path. The examples use macOS/Linux syntax. On Windows, replace `sh .../run.sh` with `& .../run.ps1`. Run only the steps the current request needs.

```sh
sh "<skill>/scripts/run.sh" init --project "<project>" --language en-US
```

This creates the project, a versioned component snapshot, fonts, and empty film and voice plans. Use `--language zh-CN` for Chinese. Keep each episode's research, source footage, captions, audio, and feedback in its project, outside the Skill.

## From script to export

1. Develop the explanation in words and images. Research the subject, write conversational narration, and consider what viewers should compare, retain, connect, or see change. Use the [material guide](assets.md) to explore suitable footage, illustration, and graphics while the argument is still editable. Keep the spoken script clean and any visual outline separate; use the joint review below before recording.
2. Fill `voice-plan.json` with complete passages. Use `tts_text` for pronunciation changes, `direction` for delivery notes, and `gap_after` only for a pause you have reviewed. Keep the original spelling in the script and captions.
3. Check the recording for complete sentences, pronunciation, voice consistency, and natural transitions. Transcription can help. Plan shot timing, music changes, and graphic reveals around the finished narration.
4. Turn the visual outline into scenes and captions in `film.json`, using the [component guide](packaging.md). Refine the writing or material choices if a planned explanation does not work on screen. Custom scenes use the shared renderer and visual system; adapt a suitable design to the content and actual narration timing.
5. Read `review/visual-plan.json`, check the composition with captions, watch the motion, render, and review the actual export. Check that backgrounds still look like moving footage and that no image, label, or transition obscures a connector. Record anything that has not been watched or heard.

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

## Review writing and visual logic together

For the important passages, establish what the viewer should understand and what seeing adds to hearing. A brief outline can pair each passage with its explanation, material, and reveal order; use only as much planning as the task needs. A script-only request still delivers natural narration, not a storyboard embedded in the spoken text.

Give comparisons identifiable counterparts and a shared question, lists a meaningful grouping, and processes an understandable sequence. Let a story supply a situation, evidence, or a turning point; keep a longer narrative when its events carry the explanation. Do not force every subject into numbered points or shorten away the reasoning needed to connect them.

Check whether the picture contributes a distinction, context, or relationship. If it can only repeat the subtitle over unrelated footage, reconsider the passage or its material. Sometimes a real action or a quiet shot already does the job. Choose graphics where they improve understanding, and reveal information when the narration earns it rather than displaying the conclusion early.

When studying a reference creator, compare the actual passage with its frames and transitions: note how the writing makes a visual explanation possible and what the image contributes. Borrow the useful relationship between words and images, with original wording and topic-specific material. Keep approved lines, viewpoint, and conclusions when condensing; change the structure when the requested revision calls for it. Record the decisions and sources that matter to the project.

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

For a footage-only scene, use `footage` with the same fields as `background` and omit `component`. Caption endpoints are snapped to frames before their duration is calculated. Chinese captions stay on one line and reject explicit line breaks or overlong cues. English captions wrap at word boundaries and reject more than two lines. Split long speech into separate, phrase-timed cues instead of shrinking, truncating, or forcing it into another Chinese line.

Each component scene needs a `purpose` and normally a moving `background`. For diagrams/cards, omitted grading fields receive a modest grade and blur; inspect and tune the actual result. `annotation` and `dateline` can overlay clear `footage`. To use an intentional full-frame map, document, or interlude without background video, supply `surface_reason` explaining that decision. A missing background is otherwise a build error. Do not place another full-frame `footage` layer over a diagram's background.

All media paths are relative to the project root. Register every moving placement: main shots, backgrounds, and video in cards.

## Footage and audio plans

`assets.json` stores sources and placements. Sources record origin, people, period, usable ranges, and original shot boundaries. Each placement has `id`, `file`, `original_shots`, and `purpose`; still portraits may use `static: true`. Cropping, renaming, retiming, or taking a different slice does not make an original shot new. `audit-media` detects duplicates in the ledger; also compare the ledger with every compiled video element.

`music-plan.json` contains `narration`, `duration`, `output`, and `cues`. Each cue has `src`, `start`, `duration`, `media_start`, `gain_db`, `fade_in`, `fade_out`, and `role` (`music` or `sfx`). Set `duck_music: false` to disable automatic music ducking. Default gains are starting points; balance each actual track against the narration by listening. The mix cannot be shorter than the narration, and the film cannot be shorter than its mix.

Use `download --project <project> --url <url>` to acquire footage. A successful download does not establish narrative fit or publication rights. Keep source and license notes in the project.
