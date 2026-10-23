<div align="center">

**English** | [简体中文](README.zh-CN.md)

# Knowledge Easy

**Ideas, brought to light.**

[![License: MIT](https://img.shields.io/badge/License-MIT-d8b676)](LICENSE)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-151c1c)](https://learn.chatgpt.com/docs/build-skills)
[![English + Chinese](https://img.shields.io/badge/Films-English%20%2B%20Chinese-8db7b2)](references/language.md)
[![FEICAI CLUB](https://img.shields.io/badge/By-FEICAI%20CLUB-2B4CF5)](https://www.feicaiclub.cn)

Give Codex a question. Knowledge Easy researches it, shapes a story, builds the visual explanation,<br>
and brings the finished film into a local review room.

<img src="assets/readme/knowledge-easy-banner.png" alt="Knowledge Easy: FEICAI's 3D cartoon portrait beside a book and film projector, bringing ideas to light" width="100%" />

[Install](#install-in-codex) · [Finished films](#from-finished-films) · [Visual system](#one-visual-language-many-kinds-of-explanation) · [Lazy Studio](#lazy-studio-a-local-review-room) · [About](#about-the-author)

</div>

## Install in Codex

**Run this in a terminal** with Node.js 22.20+ (including npm/npx) and Git installed:

```bash
npx -y skills add feicaiclub/knowledge-easy --agent codex --global --yes
```

This uses Vercel's [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) to download the skill from GitHub and install it for Codex. `--agent codex` selects Codex; `--global` makes it available across projects. The skill and its bundled resources go into `~/.agents/skills/knowledge-easy/`.

<details>
<summary>Alternative: install directly from a Codex chat</summary>

If you do not have Node.js or prefer to let Codex handle installation, paste this into a Codex chat:

```text
$skill-installer Install https://github.com/feicaiclub/knowledge-easy from the repository root (path: .), with the skill name knowledge-easy.
```

This is an instruction for Codex's [built-in Skill Installer](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use), not a terminal command. Choose either installation method; you do not need both.

</details>

Codex detects newly installed skills automatically. If Knowledge Easy does not appear, restart Codex.

Then tell it what you want to make:

```text
$knowledge-easy Make an English explainer about why we rationalize decisions we have already made. Build it around a concrete story. Use the series narrator and visual system, with footage, music, and graphics that follow the argument. Deliver a finished film and open it in Lazy Studio for review.
```

You can ask for a complete film, topic ideas, a script, or a revision. Dependencies are checked and installed **when needed**, outside the skill folder. If setup fails on your machine, Codex diagnoses the cause and works through compatible alternatives, explaining meaningful differences in the result.

## From finished films

### History: a person's choices, seen from the inside

The film about Xun Yu follows the tension between the man he helped and the dynasty he hoped to preserve. It moves between dramatic footage, geographic decisions, evidence, and reflection.

<img src="assets/showcase/history-portrait.jpg" alt="Xun Yu in the finished historical explainer" width="100%" />

<table>
<tr><td width="50%"><img src="assets/showcase/history-identity.jpg" alt="Introduce the person and their position" width="100%" /><br><b>Introduce the person and their position</b></td><td width="50%"><img src="assets/showcase/history-map.jpg" alt="Make a strategic choice visible" width="100%" /><br><b>Make a strategic choice visible</b></td></tr>
<tr><td width="50%"><img src="assets/showcase/history-context.jpg" alt="Shift attention across the same map" width="100%" /><br><b>Shift attention across the same map</b></td><td width="50%"><img src="assets/showcase/history-evidence.jpg" alt="Put a proposal beside its implications" width="100%" /><br><b>Put a proposal beside its implications</b></td></tr>
<tr><td width="50%"><img src="assets/showcase/history-relationships.jpg" alt="Separate two centers of power" width="100%" /><br><b>Separate two centers of power</b></td><td width="50%"><img src="assets/showcase/history-roster.jpg" alt="Bring in names when the story needs them" width="100%" /><br><b>Bring in names when the story needs them</b></td></tr>
</table>

<img src="assets/showcase/history-question.jpg" alt="The central conflict in the Xun Yu film: did supporting Cao Cao still mean supporting the Han?" width="100%" />

### Psychology: an everyday situation becomes a clearer judgment

The sunk-cost film starts with an ordinary movie ticket and follows the reasoning into work, relationships, and the time still ahead. Real scenes give the explanation a human setting; graphics make the pattern easier to see.

<table>
<tr><td width="50%"><img src="assets/showcase/psychology-cost.jpg" alt="Money already spent. Time still ahead." width="100%" /><br><b>Money already spent. Time still ahead.</b></td><td width="50%"><img src="assets/showcase/psychology-loop.jpg" alt="Show how a decision reinforces itself" width="100%" /><br><b>Show how a decision reinforces itself</b></td></tr>
<tr><td width="50%"><img src="assets/showcase/psychology-future.jpg" alt="Put the next choice back in view" width="100%" /><br><b>Put the next choice back in view</b></td><td width="50%"><img src="assets/showcase/psychology-street.jpg" alt="Return to life outside the diagram" width="100%" /><br><b>Return to life outside the diagram</b></td></tr>
</table>

These stills are taken from completed edits. Underlying film and stock imagery retains its original rights; see [third-party notices](THIRD_PARTY_NOTICES.md).

## One visual language, many kinds of explanation

The package includes **21 editable designs and 42 English/Chinese still previews**. The shared system covers typography, cards, diagrams, timelines, evidence layouts, and maps. Content, footage, coordinates, and reveal timing adapt to the story.

<table>
<tr><td width="50%"><img src="assets/packaging/previews/en-US/quote-reveal.jpg" alt="A thought, then its implication" width="100%" /><br><b>A thought, then its implication</b></td><td width="50%"><img src="assets/packaging/previews/zh-CN/map-route.jpg" alt="Routes and geography" width="100%" /><br><b>Routes and geography</b></td></tr>
<tr><td width="50%"><img src="assets/packaging/previews/en-US/evidence-sheet.jpg" alt="Evidence and interpretation" width="100%" /><br><b>Evidence and interpretation</b></td><td width="50%"><img src="assets/packaging/previews/zh-CN/compare.jpg" alt="Two ideas on equal visual footing" width="100%" /><br><b>Two ideas on equal visual footing</b></td></tr>
<tr><td width="50%"><img src="assets/packaging/previews/zh-CN/context.jpg" alt="A detail inside its context" width="100%" /><br><b>A detail inside its context</b></td><td width="50%"><img src="assets/packaging/previews/en-US/milestone-pair.jpg" alt="Two moments, one shared scale" width="100%" /><br><b>Two moments, one shared scale</b></td></tr>
</table>

- Open the [visual handbook](references/visual-handbook.html) locally after installation. It combines still references with layout and motion guidance.
- Use the [component source](assets/packaging/src/README.md), [renderer guide](references/packaging.md), and [motion contract](assets/packaging/src/motion-contract.json) to build and extend the system.
- Review the actual motion in each new film. A layout preview shows composition; the source and cue parameters define entrances, holds, and exits.

Use graphics when they add understanding. Let the footage and narration carry the rest.

## Lazy Studio: a local review room

### Mark the exact frame

Pause, press **M**, write a comment, and press **Enter**. The version, frame, comment, and screenshot stay together.

<img src="assets/showcase/studio-mark.png" alt="Actual Lazy Studio interaction: a frame selected and a comment being entered" width="100%" />

### Keep the feedback and review notes beside the picture

<table>
<tr><td width="50%"><img src="assets/showcase/studio-feedback.png" alt="Saved comments keep their original frame and version" width="100%" /><br><b>Saved comments keep their original frame and version</b></td><td width="50%"><img src="assets/showcase/studio-review.png" alt="Read the project review without leaving the film" width="100%" /><br><b>Read the project review without leaving the film</b></td></tr>
</table>

### Compare two versions at the same moment

<img src="assets/showcase/studio-compare.png" alt="Lazy Studio comparing the English and Chinese component demos at the same time position" width="100%" />

<sub>The comparison above uses English and Chinese demos to show the interface. It is not presented as a before-and-after edit.</sub>

### Give the film the whole screen

<img src="assets/showcase/studio-focus.png" alt="Lazy Studio focus view with a scene from the finished Xun Yu film" width="100%" />

Notes are written to the film project's `review/feedback.md`, with version/frame records and linked screenshots. Return to the original Codex chat and say: **“My notes are ready. Read the feedback and make the changes.”** The current integration works through local files; it does not automatically attach notes to the chat composer.

The screenshots were captured through actual UI interactions in a separate demonstration workspace. Sample comments are labeled as examples, and the original films and feedback records were preserved.

## A consistent narrator, a different performance for each story

Knowledge Easy uses the approved **Qwen3-TTS D reference and body-v1 finishing**. The speaker identity stays consistent while emphasis, emotion, pacing, and phrasing follow the subject.

[Listen to the approved English pilot](assets/voice/english-pilot.wav) · [Mandarin reference](assets/voice/reference.wav) · [Voice guide](references/voice.md)

The English pilot was approved through user listening. Transcription checks content and timing; it does not certify accent or naturalness.

## What the workflow handles

| Stage | What happens |
| --- | --- |
| Research and writing | Find evidence, build a story, and leave viewers with a clearer understanding. |
| Footage and shot planning | Match images to meaning; plan cuts, music changes, and graphic reveals. |
| Narration | Use the fixed reference; generate complete passages and review names, phrasing, and endpoints. |
| Editing and graphics | Call the shared renderer and adapt the composition to the explanation. |
| Sound | Use separate music cues, purposeful effects, transitions, and silence while keeping speech clear. |
| Review and revision | Inspect the export, read exact-frame notes, preserve approved work, and deliver a new version. |

The quality floor comes from completed films and repeated revisions. The topic still determines the story, duration, rhythm, and creative treatment.

## What's included

```text
knowledge-easy/
├── SKILL.md                  One skill: the production workflow
├── references/               Visual handbook and production guides
├── scripts/                  Setup, voice, transcription, editing, review tools
├── assets/
│   ├── packaging/            Renderer, fonts, maps, static visual references
│   ├── voice/                Fixed reference, pilot, profiles, pronunciation
│   ├── lazy-studio/          Review interface
│   └── showcase/             Stills from finished films and real UI captures
└── package-manifest.json     File integrity checks
```

The package contains one skill. Runtime dependencies, model weights, API keys, film projects, and demo videos are not bundled. The public handbook uses still images; production motion remains in the source code.

## Dependencies and practical limits

The default stack preserves the approved workflow: **Qwen3-TTS through MLX Audio, MLX Whisper large-v3, HyperFrames, FFmpeg, and the shared renderer**. Exact versions and model revisions are in [runtime-lock.json](scripts/runtime-lock.json).

The original narration and transcription ran on Apple Silicon Macs. Other machines may need a compatible implementation, which Codex investigates when the skill is used. Local model downloads can be large, and synthesis speed depends on the machine. Optional music and effects services use your own account and credits. See the [runtime guide](references/runtime.md).

The original generic component catalogs can be rebuilt with licensed local footage using `catalog --media-dir`; raw third-party clips are not distributed. See [demo media](assets/packaging/demo-media/README.md).


## Contributing and license

Open an [issue](https://github.com/feicaiclub/knowledge-easy/issues) with your OS, hardware, the failing step, and a redacted error message. For visual changes, show the entrance, reading order, hold, and exit; update the component and handbook together.

Before submitting changes, run `python3 scripts/validate_package.py --manifest` and `python3 scripts/validate_package.py --verify-manifest`. Package CI checks files and references without installing production models.

Original code and documentation are [MIT licensed](LICENSE). Fonts retain their SIL Open Font Licenses, and map geometry comes from Natural Earth. Third-party imagery visible in screenshots is not relicensed under MIT. [Third-party notices](THIRD_PARTY_NOTICES.md).

The workflow uses Qwen3-TTS, MLX Audio, MLX Whisper, HyperFrames, GSAP, FFmpeg, and Pedalboard. Lazy Studio builds on FEICAI's existing review tools and UI kit.

## About the author

**Feicai (废才)**, founder of **Feicai Club (废才俱乐部)**, is an AI builder and educator focused on agents, software, and filmmaking. Each workflow is developed through real projects, then the reusable parts are shared as open source.

- Author of *驱动 AI 提示词：指令入门与场景应用* (Tsinghua University Press), a book on prompting AI and applying it to real work.
- Creator of the Brutally Honest PM (毒舌产品经理) and Seedance Storyboarder (Seedance 分镜师) series.
- More projects: [Ad Storyboarder](https://github.com/feicaiclub/ad-storyboarder), [previz](https://github.com/feicaiclub/previz), [video-spec-builder](https://github.com/feicaiclub/video-spec-builder), and the [DeepSeek Harness whitepaper](https://github.com/feicaiclub/deepseek-harness-whitepaper).

| | |
|:---|:---|
| 🌐 Website | [www.feicaiclub.cn](https://www.feicaiclub.cn) |
| 𝕏 | [@zhu185178](https://x.com/zhu185178) |
| ▶️ YouTube | [@feicaiclub](https://www.youtube.com/@feicaiclub) |
| 📺 Bilibili | [废才俱乐部Club](https://space.bilibili.com/3546566589679687) |
| 📕 Xiaohongshu (RED) | [废才俱乐部](https://www.xiaohongshu.com/user/profile/5c6ec0c20000000010032d24) |
| 🎵 Douyin | search for 废才俱乐部 |
| 💬 WeChat Official Account | search for 废才俱乐部 |

[![Feicai Club: a hands-on community for AI builders](assets/readme/feicai-club.jpg)](https://www.feicaiclub.cn)
