---
name: knowledge-easy
description: Create and revise narrated explainer videos in English or Chinese, including scripts, storyboards, editing, voiceover, music, motion graphics, and frame-by-frame review.
---

[Purpose]
    Make narrated explainer videos that help viewers understand a question and make a clearer judgment. The narrator stays off camera by default.
    Reproduce the quality of the approved films with the same production workflow, series voice, and visual system. Let the topic shape the story, length, pace, and treatment.

[Working approach]
    If the user asks for a script, deliver a script. If they ask for a finished video, complete production and review before delivering it.
    Make decisions the user has delegated to you. Ask only when essential information is missing and you cannot reasonably infer it.
    Research and write first, then plan footage, narration, music, and graphics. Revisit earlier work when the film needs it.
    Take responsibility for the writing and design. Build on the proven workflow and adapt the creative treatment to each topic.
    Save requirements, decisions, approvals, and progress in the project. Read those records when resuming, and load other references only as needed.

[Setup and language]
    Follow the [production guide](references/workflow.md) to create a project outside the Skill folder. Set its language to en-US or zh-CN from the user's request.
    Use [run.sh](scripts/run.sh), or [run.ps1](scripts/run.ps1) on Windows. Commands check the machine and install missing dependencies when needed.
    Keep dependencies and model weights in the user's cache, never in this Skill. Script-only work needs no production downloads. See [runtime setup](references/runtime.md).
    Start with the approved dependencies and model revisions in scripts/runtime-lock.json. If setup fails on the user's machine, explain the cause, repair it where possible, and find compatible alternatives when needed. Preserve the approved quality and voice; explain and record any changes that affect the result.
    Resolve paths from the Skill and project locations. Do not hardcode personal paths or bundle credentials. Explain missing resources and their impact.
    For English films, use natural American English, English narration and captions, and the English typography presets. Keep Chinese production available. See [language support](references/language.md).

[Writing]
    Open with a question, situation, or conflict worth following. Use events, details, and evidence to make the reasoning clear.
    Let the ending follow from the story. Avoid a forced moral or a tacked-on call to action.
    Check historical facts, numbers, and quotations. Distinguish evidence from interpretation, and keep the viewpoint, names, and chronology consistent.
    Keep sources in project records; do not add source labels to the film by default. Verify dates, locations, boundaries, and values in maps and charts.

[Footage]
    Prefer relevant film, TV, and real-world footage. Check who and what the shot depicts, and make it support the narration.
    Use each original moving shot only once, including blurred backgrounds and video inside cards. Different shots from the same work are fine; still portraits may repeat.
    Record sources and used ranges. Exclude smoking shots. Omit brand bugs and closing credits by default.

[Visuals]
    Follow the [visual handbook](references/visual-handbook.html) for typography, color, and layout. Use the actual bundled renderer as described in the [component guide](references/packaging.md).
    Choose a visual form for the reasoning: cycles, evidence, context, comparisons, or sequences. Check the full library; do not default to whichever text or card template is easiest to call. Use no component when footage explains enough.
    Put explanatory cards and diagrams over graded, softly blurred moving video that remains visible. Use a full-frame map, document, or intentional interlude only when it serves the explanation; record the reason instead of silently using a solid background.
    Settle type hierarchy, alignment, spacing, and visual balance first. Route connectors through clear space between real anchors; keep arrowheads, images, labels, and captions from covering each other. Reserve safe margins throughout the animation, then time reveals to the narration.
    Keep Chinese subtitles on one line and English subtitles to at most two. Split long speech into separate, phrase-timed cues; do not shrink or truncate it to fit.
    Review the full motion, not just a settled frame. Adapt or create components when needed. Add reusable, tested variants and examples to the library and handbook.

[Sound]
    Use the approved Qwen3-TTS D voice and body-v1 finishing settings in the [voice profile](assets/voice/profile.json).
    Keep the voice identity stable. Design emotion, emphasis, pacing, and pauses for each topic using the [voice guide](references/voice.md).
    Generate complete passages. Include surrounding context when rerecording. Check names, pronunciation, omissions, repetitions, and the first and last syllables.
    Make the narration sound natural before fitting the visuals. Do not make large speed changes to force it into a cut.
    Choose and change music with the story. Plan fades and silence. Give the score feeling and momentum while keeping speech clear; use effects with purpose.

[Review and delivery]
    Read the visual-plan review notes. Check the actual exported film with captions: explanatory variety, visibly moving backgrounds, clear connectors, alignment, safe edges, entrances, exits, and audio transitions. Fix issues before delivery.
    Record what was checked and what was not seen or heard. Frames, transcripts, and measurements do not replace watching and listening.
    Deliver the film and a project that can be rendered again. Identify the current approved version. Keep source files, needed media, settings, and important records; remove only obsolete, reproducible intermediates.

[Feedback and revisions]
    Use [Lazy Studio](references/studio.md): press M to mark a frame, write a comment, and press Enter to save. Keep side-by-side comparison and the Marks and Review tabs; do not add a separate chat or model runner.
    When the user says feedback is ready, read the project's review/feedback.md and linked images. Use the path reported by Studio for older projects. Check the version and frame before editing.
    Address the feedback and look for the same issue elsewhere. Preserve approved work that is unaffected, and deliver a new version for review.

[Startup]
    Show this FEICAI mark in the conversation the first time the Skill is used. Do not repeat it when resuming the same project or add it to the film.
    ```text
    ███████╗███████╗██╗ ██████╗ █████╗ ██╗
    ██╔════╝██╔════╝██║██╔════╝██╔══██╗██║
    █████╗  █████╗  ██║██║     ███████║██║
    ██╔══╝  ██╔══╝  ██║██║     ██╔══██║██║
    ██║     ███████╗██║╚██████╗██║  ██║██║
    ╚═╝     ╚══════╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝
    ```
    Read the request and existing project records. Briefly state where the work stands and what you will do next.
