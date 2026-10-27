# Drawing and Artwork Interfaces

See [SKILL.md](../SKILL.md) for form, materials, creative freedom, and visual assessment. This page documents callable source files and their actual capabilities.

## Default illustration presets

Editable artwork based on the references selected by the user:

| Artwork | Editable layers | Source status |
| --- | --- | --- |
| [reference-portrait.svg](../assets/packaging/illustrations/reference-portrait.svg) | person, thought, connection | A copied study of a thinking figure in profile and primary-color shapes |
| [reference-balance.svg](../assets/packaging/illustrations/reference-balance.svg) | person, question, answer, balance | A copied study of a seesaw figure and a question-and-answer composition |
| [reference-writing.svg](../assets/packaging/illustrations/reference-writing.svg) | paper, idea, hand, window | A copied study of a writing gesture and a paper-based composition |

These are integrated into the current examples, with review references registered as art-reference-portrait, art-reference-balance, and art-reference-writing. When these files are reused directly, the source selects the matching reference by artwork filename. New drawings should provide an explicit design_reference. The three earlier original SVGs are also retained. Copied studies are not claimed as original work; see [sources.md](sources.md).

## Retained material and structure studies

| Visual approach | Method | SVG source and available layers |
| --- | --- | --- |
| Structural Linework | [etch.md](styles/etch.md) | [etch.svg](../assets/packaging/illustrations/etch.svg): seed, pod, stem, interior; h defines a fill pattern |
| Flat Color and Overprinting | [print.md](styles/print.md) | [print.svg](../assets/packaging/illustrations/print.svg): canopy, shade |
| Natural Wash | [wash.md](styles/wash.md) | [wash.svg](../assets/packaging/illustrations/wash.svg): land, water, river, tributary, bridge |

These SVGs are drawing source files. Copy them into a project and retain their paths and layers while adapting them. They are not approved animations and do not require a new film to include a seedpod, porch, or river. See [examples.json](../assets/packaging/src/artwork/examples.json) for configurations; establish the film's approach before reading the relevant examples.

These earlier drawings and the JavaScript files in examples/ are studies in construction, mark-making, and timing. The default figure style uses the selected references above. Technical examples are not substitutes for finished visual design.

## SVG integration

Set the scene's component to "artwork" and data.source to an .svg path within the project. The caller prefixes layer IDs per instance and updates path, gradient, and fill references.

```json
{
  "id":"inside","start":0,"duration":8,
  "purpose":"Establish the complete object before revealing its internal structure.",
  "component":"artwork",
  "data":{
    "style":"etch","source":"assets/artwork/subject.svg",
    "description":"A subject and internal relationships designed for this film",
    "motion":[{"target":"interior","type":"fade","at":2.4,"duration":0.7}]
  }
}
```

The source must contain an actual interior layer. motion.type may be fade, draw, or move. move.from/to support x, y, scale, rotation, and opacity. draw requires an existing stroked path whose length can be measured; it cannot simply trace a filled layer. A matching target name in cues overrides at. Declare only one motion entry per layer; use project drawing code or an extension for complex actions with multiple stages.

SVG integration preserves the static vector structure and rejects script, external image, foreignObject, and native SVG timing animations. Clipping, gradients, and structural layers are retained, while the project timeline controls motion. Inspect the source viewBox and actual layer positions.

## JavaScript integration

data.source can also point to assets/artwork/scene.js in the project. The file is a drawing-function body receiving ctx, t, data, and art. t is local component time in seconds. data comes from configuration, with duration and local beats injected.

Drawing resets every frame. Derive poses from t rather than accumulating the previous frame's position. Use seeded art.rng for randomness, not wall-clock time or network requests. The current interface uses a full 1920×1080 canvas with an opaque base, so account for occlusion when composing layers.

| Method | Parameters and purpose | Limits |
| --- | --- | --- |
| path | path(svgPath, fill, stroke, width) | The caller draws the contours; the tool does not invent forms |
| line / quadratic | line(points, width, ink, progress); quadratic(a,control,b,steps) | progress advances through sampled points; even speed requires appropriate sampling |
| stroke | stroke(points,width,ink,{progress,opacity,profile,seed}) | wash builds a pressure-shaped outline along path normals; other modes use constant-width strokes |
| hatch | hatch(shape,[x,y,w,h],{spacing,bend,width,opacity,ink}) | Clips regular curves to the supplied shape; it does not infer surfaces, occlusion, or light |
| over / plate | over(fn); plate({x,y,opacity},fn) | Multiply blending with caller-controlled offset; no automatic print simulation |
| camera / pose | camera({x,y,zoom,angle},fn); pose(keys,t) | Camera and pose interpolation; angle uses radians, and keys must be ordered by t with consistent structure |
| person / hand / eye | Construction helpers with adjustable proportions, orientation, and pose | Not a general-purpose character or automatic performance system |
| leaf / foliage / branch | Starting points for leaves, clusters, and branches | Seeded foliage placement does not automatically align with branches; design the support relationships |

All implementations are in [runtime.js](../assets/packaging/src/artwork/runtime.js). Draw new objects directly with Canvas 2D whenever needed; these helpers do not limit the work. In wash mode, stroke supports profiles such as even, trunk, tip, and leaf. The design still determines transparency and path geometry.

## Palettes, text, and provenance

data.style accepts etch / print / wash, or an object containing engine and palette. palette supports paper, ink, accent, and secondary; print can also specify inks. The current engine uses Canvas 2D without external brush or color-separation dependencies.

Text can live in data.labels: id, text, x, y, width, size, at, and optional end, font, weight, align, and color. Position values such as x/y use the working canvas coordinates. Labels are separate from captions; see [artwork.py](../assets/packaging/src/artwork.py) for bounds. The default label fade is only an interface starting point; use an extension when the text needs different motion.

composition.py reads the actual source and records drawing_source and its checksum. Successful integration still requires reviewing the actual forms, materials, actions, and full-film performance as described in SKILL.md.
