# Component Inputs and Integration

[SKILL.md](../SKILL.md) defines design choices, reuse quality, and review requirements. This page documents the current source interfaces.

## Find the actual implementation

| Need | Interfaces and implementations to read first |
| --- | --- |
| The 12 base layouts | [Input examples](../assets/packaging/src/base-examples.json), [base_catalog.py](../assets/packaging/src/base_catalog.py), [pack.css](../assets/packaging/src/pack.css) |
| Extended components | public_variants in [renderer-contract.json](../assets/packaging/src/renderer-contract.json), [editorial.py](../assets/packaging/src/editorial.py), [editorial.css](../assets/packaging/src/editorial.css) |
| SVG or custom drawing | [Drawing Interface](illustration.md), [artwork.py](../assets/packaging/src/artwork.py), [runtime.js](../assets/packaging/src/artwork/runtime.js) |
| New layouts and renderers | film.extensions; see [composition.py](../scripts/composition.py) for loading behavior |

The base component IDs are hero, compare, chapter, evidence, relation, feedback, quantity, timeline, map-focus, map-route, map-period, and context. Extensions include evidence-sheet, relation-bridge, feedback-loop, context-reveal, and others. Treat the source as authoritative for names and fields. Replace example media paths, screen copy, and scene order with the content needed for the film.

## Additional type and portrait layouts

See [type_designs.py](../assets/packaging/src/type_designs.py) and [type.css](../assets/packaging/src/type.css).

- lit-title: image, left, right, and optional caption. Each character's face, lit edge, dark edge, and fine grain are drawn in separate layers.
- medallion-labels: image, 2–4 labels, and optional title and caption. Thin metallic rims surround translucent medallions with lit typography.
- editorial-portrait: image, title, and optional caption and accent. A close-up portrait on a paper surface has its own space alongside the text.

Images support image.fit (cover / contain) and image.focus. The paper portrait preset bottom-aligns the complete image to avoid cropped artwork or a floating torso. Apply media fades, movement, and scale to the outer container. The medallion background uses the shared backdrop directly so foreground animation does not interfere with the media treatment layer.

The examples create a lit Song-style effect with the available Noto Serif SC font. They do not identify it as the exact typeface in the reference video. Projects supply their own content parameters, using the same integration pattern as other extensions.

## Scene input

The following is a valid compare input. The project must supply the media files, and the duration must be adjusted to the actual narration. Chinese strings inside data are sample screen copy:

```json
{
  "id":"distinction","start":0,"duration":8,
  "purpose":"Make the difference between two judgments visible at a common scale.",
  "background":{"src":"assets/media/environment.mp4","treatment":"cinematic"},
  "component":"compare",
  "data":{
    "text":{"a-label":"可见行为","b-label":"真实动机","ta":"观察","tb":"推断","q":"已有证据能支持哪一步？","ghost":"辨"},
    "media":{"a-film":{"src":"assets/media/observation.mp4","type":"video"},"b-film":{"src":"assets/media/evidence.mp4","type":"video"}}
  },
  "cues":{}
}
```

Slots in `data.text` and `data.media` vary by base component. Extensions have their own structures; do not pass the same fields to every type. Keys in `cues` also come from the cue names actually used by that component. `data.appearance` can override foreground, accent, secondary, and muted. It changes colors, not the layout.

By default, `background` uses moving footage with the cinematic blur treatment. [backdrop.py](../assets/packaging/src/backdrop.py) supplies tonal, saturation, blur, and shade settings. Production builds and previews call the same render_background, using HyperFrames' native data-color-grading. Only the background receives this treatment; foreground components and media remain sharp.

Override individual background settings through grading/shade. Use treatment: "raw" or footage when the shot needs a sharp full-frame image. Paper, solid-color surfaces, and original canvases belong to deliberately selected designs; they are not the default substitute for cinematic graphics. Replace preset media paths for the new content.

## Composition and timing

A scene uses either component or a nonempty components array, never both. Each entry in components has a unique id, component, and data, with optional purpose, cues, start, duration, frame, and design_reference.

- start is relative to the scene; duration must remain within it. cues are relative to the layer.
- frame is [x,y,width,height] on the 1920×1080 working canvas. It centers and scales the design proportionally without reflowing it. Shrinking an entire design cannot solve every composition problem.
- Later entries sit above earlier layers. An opaque full-frame canvas hides the layers beneath it. Establish how drawing surfaces, foreground objects, text, and captions overlap before combining them.
- Judge reading areas and caption space from the actual layout. Staying within frame bounds does not establish readability.

## Project extensions

Declare an extension in film.extensions:

```json
{"id":"decision-space","source":"components/decision_space.py","design_reference":{"src":"assets/references/composition.png","reason":"Compare subject scale, contour hierarchy, and space around connectors."},"reason":"This passage needs continuous spatial transformation that the existing layouts do not provide."}
```

The project Python file provides `render(kit, prefix, duration, data, cues, locale)`, returning html, js, and reading_order, with optional layout. Each reading_order entry has a unique element id, role, enter_at, settle_at, and depends_on. Prefix all element IDs with prefix and control timing through a seekable local timeline. Extensions may compose calls to kit.render or implement new drawings. Do not replace shared library functions in memory.

The base entry point is `render(component, instance_id, duration, data, cues, locale)`. Its return record includes component, parent, version, implementation, and design_reference. composition.py adds these provenance fields for project extensions.

## Design references and provenance

A reference can be a component ID, a registered illustration ID, or a project image with src and reason. The current figure presets use art-reference-portrait, art-reference-balance, and art-reference-writing. art-etch / art-print / art-wash remain available for the corresponding material studies. Resolution order is layer → scene → film → the renderer's default reference. Explain a new comparison target when changing references; do not switch merely to avoid an existing quality gap.

In research/component-usage.json, provenance identifies the library snapshot. Original drawing adds drawing_source/drawing_sha256; extensions record source/sha256/reason. reading_order comes from the actual render result. source_signature binds the relevant source and referenced files to the export.

<a id="visual-review"></a>
## Connection to review

review-visuals prepares references, sampled frames, and motion_file for the actual export. The complete sequence supports whole-film review. If a built-in component has no reference screenshot, judge it against the actual current implementation and the film's design requirements rather than substituting an old preview.

The review covers hierarchy, composition, material, motion, and explanation, plus whole-film direction, rhythm, and sound. See SKILL.md for observation methods and revision principles. accept-visuals validates records and evidence; it cannot score aesthetics automatically.
