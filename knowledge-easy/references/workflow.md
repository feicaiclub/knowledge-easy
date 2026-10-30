# Commands and Project Files

See [SKILL.md](../SKILL.md) for the production method and quality criteria. This page is an interface index. Do not run production commands when the task is only to edit the Skill.

## Command entry points

`<skill>` is this Skill's directory; `<project>` is a project directory outside it. On macOS / Linux, use `sh "<skill>/scripts/run.sh"`; on Windows, use `& "<skill>/scripts/run.ps1"`. Read [Runtime Setup](runtime.md) before running commands. Production entry points such as voice, render, and mix may prepare dependencies as needed; they are not read-only file checks.

The following macOS / Linux examples are available as needed for the task:

```sh
sh "<skill>/scripts/run.sh" init --project "<project>" --language zh-CN
sh "<skill>/scripts/run.sh" voice --project "<project>" --plan voice-plan.json
sh "<skill>/scripts/run.sh" transcribe --project "<project>" --file audio/narration/narration.wav
sh "<skill>/scripts/run.sh" build --project "<project>"
sh "<skill>/scripts/run.sh" preview --project "<project>"
sh "<skill>/scripts/run.sh" mix --project "<project>" --plan music-plan.json
sh "<skill>/scripts/run.sh" render --project "<project>" --output final/film-v1.mp4
```

Fill in the actual inputs before running each command. If film.mix changes after mixing, rebuild before rendering. render will not overwrite an existing destination. After changes to fonts, images, code, or audio, review records for an earlier build or export no longer establish the quality of the new result.

## Inputs and provenance

| File | Purpose |
| --- | --- |
| project.json | Project identity, language, and established decisions |
| film.json | Scenes, components, media, captions, optional beats/extensions, and mix |
| voice-plan.json | Complete passages, optional pronunciation corrections, and per-segment direction |
| music-plan.json | narration, duration, cues, and mix output; audio is positioned by start or event/offset |
| assets.json | Media sources, selected ranges, and original shot identities |
| kit/editorial-lock.json | Snapshot of the project's rendering source and fonts |

Components currently use a 1920×1080 working canvas at a default 30 fps. scene.start is in absolute seconds; a layer's start, duration, and cues use local time. A different aspect ratio requires actual composition and rendering changes, not just different metadata.

## Build and review outputs

| Stage | Outputs and review entry points | What they establish |
| --- | --- | --- |
| build | research/component-usage.json, research/build-receipt.json | Actual source usage, content, reading order, and version |
| render, including technical checks | review/technical-check.json, review/render-receipt.json | Decoding, duration, audio tracks, and export binding; not an aesthetic judgment |
| review-visuals | review/visual-review.json and its linked comparison pages, frames, and motion clips | Evidence from the actual export, ready for inspection |
| accept-visuals | Validation of those records, evidence, and versions | Whether the recorded self-review is complete; it does not judge quality automatically or replace user approval |

```sh
sh "<skill>/scripts/run.sh" verify --project "<project>" --file final/film-v1.mp4
sh "<skill>/scripts/run.sh" review-visuals --project "<project>" --file final/film-v1.mp4
sh "<skill>/scripts/run.sh" accept-visuals --project "<project>"
```

render already prepares review evidence once. review-visuals prepares it again for the same export; it does not watch the film for you. The record's frames, motion_file, sequence, and full-film playback link support different levels of inspection. Adding a screenshot does not automatically change pending to pass.

## Optional entry points

- `catalog --base`: inspect the 12 base component types. `catalog --art`: inspect the original drawing starting points. Complete extended examples require `--media-dir` pointing to usable media. If the goal is only to understand parameters, read the source directly rather than generating a sample reel.
- `install-pack --update`: deliberately upgrade an existing project's snapshot while preserving older film versions. Do not include an upgrade as an incidental part of an ordinary revision.
- `audit-media`: check assets.json when the project requires unique moving shots. Also compare the records to what is actually edited into the film; incomplete records cannot establish that no shots are repeated.
- `register --file final/film-v1.mp4 --label "First cut" --id v1`, followed by `studio`: register an existing export and open [Lazy Studio](studio.md). Add `--review-file <notes.md>` to attach review notes to that revision. The sidebar and its feedback-file links follow the selected version.
