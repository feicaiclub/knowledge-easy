# Production workflow

`<skill>` is this Skill folder and `<project>` is a project outside it. Use `sh <skill>/scripts/run.sh` on macOS/Linux, or `& <skill>/scripts/run.ps1` on Windows. Run only the stages relevant to the request.

```sh
sh "<skill>/scripts/run.sh" init --project "<project>" --language zh-CN
```

The project receives a versioned rendering toolkit, fonts, and editable film, voice and asset plans. An established project keeps its locked snapshot; use `install-pack --update` deliberately when the work needs a newer capability.

## From an idea to an authored film

1. Read the content, audience and constraints. Develop the [treatment](direction.md) before choosing a demo's scene structure. Record the argument, visual premise, key shots, reference qualities and sound progression. Resolve delegated decisions without unnecessary approval stops.
2. Gather strong material and/or create original artwork. Use [material routes](assets.md), [drawing languages](illustration.md) and project-owned implementations. Compare actual candidates and render representative style frames/key actions with the real code. Refine the image before repeating it across a film.
3. Prepare the voice. Honor the selected recording or identity. Generate complete passages when using the built-in voice route, compare a representative take, and check words and phrasing. Direct performance independently from pitch and overall speed; see [voice](voice.md).
4. Build the edit around the actual performance and visual changes. Configure scenes, subtitles and optional shared `beats` in `film.json`. Use music-led timing only when it suits the treatment; give natural explanation and essential action their own time.
5. Render a candidate and review its full viewing experience, with scene comparisons as supporting evidence. Repair weak staging, material, timing or sound, not only technical errors. Preserve the user's approved work outside the requested change.
6. Deliver the current film and reproducible project; use [Lazy Studio](studio.md) for exact-frame feedback. Record actual approval separately from a successful export or a self-review.

```sh
sh "<skill>/scripts/run.sh" voice --project "<project>" --plan voice-plan.json
sh "<skill>/scripts/run.sh" transcribe --project "<project>" --file audio/narration/narration.wav
sh "<skill>/scripts/run.sh" mix --project "<project>" --plan music-plan.json
sh "<skill>/scripts/run.sh" build --project "<project>"
sh "<skill>/scripts/run.sh" check --project "<project>"
sh "<skill>/scripts/run.sh" snapshot --project "<project>" --at 0.2,1.2,3.5
sh "<skill>/scripts/run.sh" preview --project "<project>"
sh "<skill>/scripts/run.sh" render --project "<project>" --output final/film-v1.mp4
# After genuine comparative, full-film and listening judgments are recorded:
sh "<skill>/scripts/run.sh" accept-visuals --project "<project>"
```

Transcription writes recognized speech, word timings and source/model hashes to `review/transcript.json`. An optional prompt may contain names or terminology, never the expected script as recognition evidence. Transcription and measurements do not replace listening. If viewing or listening is unavailable, retain that check as pending.

## Scene configuration

The default canvas is 1920×1080 at 30 fps. Scene starts are absolute seconds; component starts/cues are local. Keep exact text and source facts editable. Each graphic scene has a `purpose`; a significant visual change can be recorded in `visual_change`. These decisions help review, not automatic aesthetic scoring.

A scene can use source `footage`, a chosen `background`, a designed `surface`, code `artwork`, or a composition of independently timed layers. Background grading, blur and shade are explicit artistic choices. See [rendering routes](packaging.md) for classic layouts, original drawing and project-specific renderers.

```json
{
  "title":"A new explanation", "language":"zh-CN", "fps":30, "duration":12,
  "beats":[{"id":"finding","time":7.2,"purpose":"An overlooked relationship becomes visible"}],
  "scenes":[{
    "id":"observe", "start":0, "duration":12,
    "purpose":"Show the relationship rather than only name it.",
    "component":"artwork",
    "data":{"style":"etch","source":"assets/artwork/observe.js","configuration":{"duration":12}}
  }],
  "subtitles":[]
}
```

Original drawing code receives `t`, `ctx`, `art`, and its `data`; shared beats arrive in `data.beats` as local seconds. Footage-only passages need no graphic. Different editorial forms may share a visual identity without sharing the same shot list or layout sequence.

All paths are project-relative. Caption endpoints are quantized to frames. Chinese captions default to one line, English up to two; phrase-level cues preserve words and avoid shrinking long text into unreadability. Different delivery formats need intentional layout design, not simply scaling the landscape film.

## Media and sound records

`assets.json` records sources and used ranges. Register original moving-shot identities for main shots, backgrounds and insets. For a series with a no-repeat requirement, renaming, cropping or retiming does not make a shot new; `audit-media` checks the ledger. Cross-check the compiled placements with the actual material.

`music-plan.json` records `narration`, `duration`, `output` and `cues`. A cue uses a literal `start` or an `event` ID plus optional `offset`, with `src`, `duration`, `media_start`, `gain_db`, fades and `role`. Events resolve from `film.json`, so a moved hit point moves the corresponding audio cue when remixed. Use meaningful sound bridges and material-specific effects where they improve the film. Avoid cutting speech to force a desired duration.

Built-in synthesis is one voice route; supplied recordings and explicitly requested providers can be used without changing the global series reference. Keep their settings, reference identity and review decisions with the project. An approved voice identity does not approve every generated performance.

## Example and film boundaries

Library examples demonstrate a technique. Replacing their text/media is a useful smoke test, not an authored film. Reuse the brush, rig, shader, layout or cue method, then design the user's content in its own structure. A new reusable technique needs a second subject and a different staging problem, plus actual rendered evidence. Keep examples, temporary tests and user films separate.
