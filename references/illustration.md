# Original code illustration

Code can draw subjects, poses, material, space and movement, not only labels and charts. The supplied engines are small drawing toolkits. Every project writes its own scene source; no preset chooses its story or composition.

Read a style's principles first, develop the project's treatment, then inspect its examples to learn techniques. The examples are studies, not a six-scene film template.

| Starting language | Reusable craft | Examples with different subjects |
| --- | --- | --- |
| [Expressive ink](styles/etch.md) | Contours, form-following hatching, silhouettes, sculpted hands and clear spatial metaphors | Attention as selection; capacity and boundaries |
| [Overprint theatre](styles/print.md) | Separate ink densities, translucent overprint, halftone, plate registration and material reveals | A shaded street; overlapping fields creating a shared result |
| [Living brush](styles/wash.md) | Width-shaped strokes, dry bristles, seeded leaf clusters and drawn growth | Above/below-ground growth; a topographic river network |

Profiles are editable palettes and material parameters. They do not fix objects, character identity, framing, number of shots, order, timing or ending. A project may use a custom profile, a different renderer, or combine illustration with photographs and footage. Keep material logic coherent within the chosen treatment; a different style does not need to resemble these examples.

## Production entry

Put a JavaScript drawing body in the project, for example `assets/artwork/scene.js`, and use:

```json
{
  "id":"observation", "start":0, "duration":12,
  "purpose":"Show a field of information becoming one usable clue.",
  "visual_change":"The eye changes its focus; one path becomes distinct.",
  "component":"artwork",
  "data":{
    "style":"etch",
    "source":"assets/artwork/scene.js",
    "description":"An original illustration of selective attention",
    "configuration":{"duration":12},
    "labels":[{"id":"finding","text":"A useful clue","x":1200,"y":160,"width":500,"size":64,"at":7}]
  }
}
```

The drawing body receives `ctx` (Canvas 2D), `t` (local seconds), `data` (project configuration and local beats), and `art` (drawing tools). It can use any ordinary deterministic Canvas drawing code. The runtime resets the canvas before every frame; objects and camera are calculated from `t`, so arbitrary seeking remains reliable. Essential labels can stay in `data.labels` as editable DOM text above the artwork; drawn text still requires pixel-level visual review.

The source file is tracked in the build/render signature. Changing it requires a rebuild. Do not use network requests, unseeded randomness or wall-clock timers in drawing code. For complex scenes, create project-specific helper functions or a [renderer extension](packaging.md#project-owned-renderers) rather than trying to express every new idea with a fixed list of icons.

## Drawing vocabulary

`art.ctx`, `W`, `H`, `P` (palette), `color(role)`, `clear()`, `path(svgPath, fill, stroke, width)`, `line(points, width, ink, progress)`, `ellipse(x,y,rx,ry,ink,angle)`, `stroke(points,width,ink,options)`, `hatch(path,bounds,options)`, `camera({x,y,zoom,angle}, fn)`, `pose(keyframes,t)`, `phase(t,start,end)`, `mix`, `clamp`, and `rng(seed)` are available.

`person`, `hand`, `eye`, `leaf` and `branch` provide editable examples of shape construction. Use them where suitable, change their proportions and poses, or draw different subjects. They are not required subjects for a style. `art.brush` exposes `qctrl`, `qcurve`, `mk`, `drawS`, `drawList`, `clump` and `withSeed` for more detailed stroke construction. Construct stable geometry with a fixed seed; animate its reveal or pose from time.

For print work, `art.color` encodes ink density rather than a display RGB color. Roles map to plates: `ink`, `accent`, `secondary`; an explicit density triple is also accepted. `art.over(fn)` adds plates, producing a real overprint. Set `art.printOptions` per frame for plate gates, sweeps or controlled registration; final composition is handled by the print engine. Keep small saturated halftones out of skin and essential reading areas; inspect moiré after encoding.

For a custom palette use `data.style` as an object containing `engine`, `palette` and (for print) three `inks`. Give it a project reference with `design_reference: {"src":"assets/references/look.jpg","reason":"The intended material and focal hierarchy"}` when the bundled reference no longer fits. There is no requirement to add a permanent global style for one film.

## Source and example locations

- Material profiles: [profiles.json](../assets/packaging/src/artwork/profiles.json).
- Common drawing and pose helpers: [runtime.js](../assets/packaging/src/artwork/runtime.js).
- Brush and print implementations: [brush.js](../assets/packaging/src/artwork/brush.js), [print.js](../assets/packaging/src/artwork/print.js).
- Six authored studies and editable descriptions: [examples.json](../assets/packaging/src/artwork/examples.json), with separate JavaScript sources in the same directory's `examples/` folder.

The brush and print kernels are adapted from MIT-licensed Lemo-Opuscar. Their license and attribution remain with the source. The example subjects and staging here are original; the borrowed engines do not prescribe a story. See [third-party notices](../THIRD_PARTY_NOTICES.md).

For a separate technique gallery, run `catalog --art --project <new-project> --language zh-CN` (or `en-US`), then inspect/render it through the normal workflow. This command creates studies in a new project; do not use their fixed ordering as a new film's treatment.
