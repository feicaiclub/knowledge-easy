# Direction: carry quality across subjects

This guide separates reusable craft from the choices a new film needs to make. It applies to live footage, original illustration, code animation and mixed media.

## Start from a visual premise

Read the script for its question, evidence, tensions and change in understanding. Propose plausible structures internally and choose the one that makes this content work; involve the user when a choice requires their knowledge or when they asked to participate. A software tutorial, personal essay, scientific mechanism and historical dispute do not need the same opening, palette or rhythm.

Record a compact treatment in the project before browsing example story code. Use existing project notes if they already serve this purpose:

- the audience's question and what they should understand differently by the end;
- the subject or recurring idea that holds attention, and its progression;
- the visual premise: what the viewer actually sees changing, rather than adjectives such as “premium”;
- the chosen material and visual language, with actual references and the craft to learn;
- the key shots: focal subject, framing, action/change, handoff and reading time;
- voice intent and how the sound state changes with the argument.

Use as much detail as the work needs. This is a set of decisions, not a form-filling gate. A one-line correction does not require a new treatment. An established series can retain its identity while changing the form of each episode.

## References set a floor, not a plot

Choose references for the current treatment, not automatically the last film's examples. Compare concrete properties: material behavior, light separation, silhouette, scale, staging, movement, reading time and sound relationships. Keep references in the project with source notes. A supplied reference can replace a bundled library reference.

The [classic editorial handbook](visual-handbook.html) is one useful visual language. The [drawing languages](illustration.md) are other starting points. Neither defines the complete set of allowed film aesthetics. Adapt or invent when the project needs it, keeping the evidence, legibility and production contract intact.

Before copying example code, separate what travels from what belongs to its story:

| Reusable | Reconsider for the new film |
| --- | --- |
| Brush behavior, plate printing, coordinate transforms, rigs, reveal mechanisms | Characters, objects, composition and camera route |
| Type hierarchy and a material's color logic | Actual text, palette, density and shot scale |
| Continuous motion and audio-event synchronization | Duration, accent, pauses and the shape of the score |
| Clear source and render records | The claim, emotional arc, opening and ending |

Use the demo to learn *how something was drawn or moved*. Compare your result with it to detect inherited story or staging. No numeric novelty quota: repeated structure can be deliberate, but the treatment should explain why it serves the new content.

## Visual translation

Choose the kind of contribution a passage needs:

- **Observed action:** preserve cause, response and consequence in real footage. Evaluate the actor's moment, camera angle and cut, not only whether an office or object is present.
- **Evidence:** bring in the actual artifact, show the relevant detail, then its implication. Do not turn an invented prop into documentary evidence.
- **Mechanism:** let states or relationships change. A label that says “pressure” is weaker than a visible constraint that changes a subject's options.
- **Metaphor or illustration:** establish a recognizable shape and a precise relationship, then act on it. Original drawing may be a better answer than another stock search.
- **Reflection or emotion:** a held performance, a meaningful landscape, silence or negative space can carry the passage. Do not fill every pause with animation.

A list is appropriate when the argument is a list; a process needs an unfolding process. Do not convert every passage into a numbered card. Use text to direct attention, retain names or make an exact claim, while the rest of the image contributes something of its own.

## Prove the art before expanding it

Render representative style frames and the key action with the real code/media. Include the shot with the highest visual risk: a handover, character expression, dense evidence, unusual material or change of scale. Inspect silhouettes, focal hierarchy, foreground/background separation, text contrast, crop, spatial relationships and material consistency at delivery size.

For an original character, establish its proportions, expressions and relevant poses. A rig is a starting drawing tool; design a character for the film, rather than importing a demo protagonist. Blend pose changes and inspect the action enlarged. For an abstract or object-led piece, establish its states and the transformation that explains the point.

If the result is visually weak, improve the drawing, staging or material before producing more scenes. A functioning renderer is not approval of the art.

## Editing has several clocks

Coordinate the clocks of meaning, performance, image and music. Some statements deserve a pause; some actions need a reaction shot; some mechanisms need a build and then a stable reading moment. Do not infer pacing from average shot length alone.

Write the important visual changes and emotional turn into the treatment, then arrange shots around them. Vary shot scale, material or density when the content calls for a shift. Avoid both an unchanging image with sequential labels and arbitrary novelty that loses the argument. Continuous transformation may be more effective than a cut.

Camera vocabulary is available, not compulsory: a close-up reveals material or expression; a pull-back reveals context; lateral movement can follow a process; a stable two-shot lets a relationship read. Design transitions through a meaningful object or material when it helps the handoff. Anticipation and follow-through should be visible in key actions.

## One event clock

`film.json` may contain `beats`, a list of `{ "id": "reveal", "time": 6.2, "purpose": "The two sources become one result" }`. These are editorial events, not a mandatory music grid. Times are absolute seconds. Unique IDs and timeline bounds are checked during build.

The builder supplies scene-local beat times to code artwork as `data.beats`. An audio cue can use `{ "event": "reveal", "offset": -0.08, ... }` instead of `start`; the mixer resolves it from the same film beat map. Native components still use local semantic cues. An event can name a cut, an action, a change of understanding or a sound bridge. Do not manufacture events solely to increase their number.

Keep narration intact. Where exact phrase alignment matters, use verified word timings to place events. For music-led work, plan the score's accents first; for spoken explanation, place music around natural phrasing. Choose and review each method rather than enforcing one across topics.

## Hear the intent

Separate voice identity, speaking rate, phrasing, pitch and emotional emphasis. Ask for more intention with better phrasing and stress, not a large speed/pitch change. Compare a representative take against the chosen voice, keeping changes small and specific. Tools without expressive control must not claim that a direction field changes the performance.

Use ambience to establish a place or material, foley to clarify consequential action, and music to shape energy. Continuous wallpaper music is not a substitute for a score with progression. Neither is adding a sound to every visual element. Check speech, music and effects together on the export; report listening limitations honestly.

## What successful generalization means

The new topic should change the visual idea, subjects, composition and/or movement for a content-driven reason, while preserving craft. Test a reusable technique with another subject and staging problem. Also check a project-owned style/reference outside the bundle so the library does not become the boundary of what can be made.

Assess the *film*: its first impression, clarity, variety with purpose, emotional development and ending. A technical test, style contact sheet or second dataset validates only the behavior it exercises. They do not by themselves prove consistent direction or aesthetic quality.
