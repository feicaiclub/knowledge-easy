# Design Notes and Timing Interface

[SKILL.md](../SKILL.md) contains the complete directing method, design standards, and review sequence. This page explains how project decisions map to production inputs; it does not define a separate workflow.

## Design notes

Use the project's existing notes, or research/design.md if there are none. Record the viewer's central question and change in understanding, the presentation approach and its tradeoffs, reference qualities, visual language, and shot intent. These notes guide production without imposing a new fixed film format.

A shot table can use these columns:

| Line or point in the argument | Subject and shot size | Before → change → result | Implementation and media | Timing basis |
| --- | --- | --- | --- | --- |
| The causal relationship being explained | Where the viewer looks first and how close they need to be | How the visible change supports the conclusion | Source range, component, or original file | Actual speech, completion of the action, and reading time |

State the qualities to compare in each visual reference. A design_reference in film.json should be a registered component ID, art-etch / art-print / art-wash, or a project image object with src and reason. Do not put the path to a Markdown note in an image field. During production, carry identified risks into the review observations for the affected shots.

<a id="one-event-clock"></a>
## One shared narrative event

In film.json, beats use absolute seconds for the entire film, with unique IDs:

```json
{"beats":[{"id":"finding","time":6.2,"purpose":"A visible connection forms between two objects."}]}
```

scene.start uses film time; components[].start is relative to the scene; cues and drawing time t are relative to the component. The scripts convert events within a component's active range into data.beats: local event time = beats.time − scene.start − component.start.

For example, if the scene begins at 4 seconds and the component enters 0.5 seconds later, finding occurs at 1.7 seconds in the drawing. Design the graphic action around that time. In music-plan.json, align the sound effect with event: "finding" and offset: 0.

```json
{"src":"assets/audio/contact.wav","role":"sfx","event":"finding","offset":0,"duration":0.35,"gain_db":-14,"fade_in":0.01,"fade_out":0.08}
```

Each audio cue uses either event or start. offset allows an early or delayed entrance, but the resulting time cannot precede the start of the film. After changing an event, rebuild and remix rather than updating only the picture. Events provide shared timing cues; they do not force shots onto a musical beat grid.

See the actual parsers in [event_clock.py](../scripts/event_clock.py), [composition.py](../scripts/composition.py), and [mix.py](../scripts/mix.py).
