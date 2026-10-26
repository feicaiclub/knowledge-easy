# Rendering a chosen design

Choose the treatment using the [direction guide](direction.md), then choose implementation tools. The library is a set of usable techniques and finished example layouts; it is not a compulsory visual identity.

## Available routes

- **Classic editorial layouts:** the twelve base designs (`hero`, `compare`, `chapter`, `evidence`, `relation`, `feedback`, `quantity`, `timeline`, `map-focus`, `map-route`, `map-period`, `context`) and the existing variants. Use their complete compositions when they fit. [Chinese input examples](../assets/packaging/src/locales/zh-CN/base-examples.json) and [English input examples](../assets/packaging/src/locales/en-US/base-examples.json) show the required fields.
- **Original code artwork:** `artwork` runs a project-owned drawing source using reusable brush, print and shape tools. See the [illustration guide](illustration.md). Its subjects, composition, camera and timeline are authored for the film.
- **Project-owned renderers:** a project can provide a new HTML/SVG/Canvas implementation and its own design reference. This is the route for a new visual language, custom geometry or a technique not in the library.
- **Source material:** footage and artifacts can carry a scene on their own. A component is not required for every idea.

`init` copies a versioned renderer, fonts and map data into the project. `kit/editorial-lock.json` binds the source. `build` uses that snapshot and records the actual implementations in `research/component-usage.json`. `install-pack --update` is an intentional project upgrade; delivered films are never silently changed.

## Content and composition

`render(component, instance_id, duration, data, cues, locale)` returns editable markup, seekable motion, reading order and provenance. Base designs accept named text/media slots and their own structured fields; missing inputs never silently inherit sample facts. Foreground media can be images or video with a source range and focal point. Keep wording and values editable.

A scene can have one `component` or a `components` array. Each layer in the array has a unique `id`, its `component` and `data`, optional local `cues`, and optional `start`, `duration` and `frame: [x,y,width,height]`. The default is the full scene. This allows temporal sequencing and deliberate spatial composition. A frame scales an existing composition uniformly; it is not an automatic re-layout. Use a new authored arrangement when scaling would reduce readability or weaken staging.

For precise narrative synchronization, native layouts use local semantic cues. Original artwork also receives scene-local values from the optional film beat map; audio can refer to the same events. See [one event clock](direction.md#one-event-clock).

## Surfaces and photographic treatment

Choose the ground deliberately. It can be clear or graded footage, a document, authored illustration, paper, a solid field or a gradient. The builder no longer adds a dark wash or blur simply because a graphic exists.

- `background` supplies one full-frame moving video; `grading` and optional `shade` are explicit shot choices. Blur may be zero. Preserve material detail, meaningful movement and subject separation.
- `footage` carries a full-frame shot, optionally with overlays. Do not add it above a second full-frame background.
- `surface` can be `{ "kind":"solid", "color":"#f3eee3" }`, `paper`, or a `gradient` with `color`, `to`, and `angle`. It is a designed ground, not evidence of an error.
- Code artwork draws its own ground. Legacy `surface_reason` remains readable, but new films do not need ceremonial exceptions to choose a graphic style.

Background consistency means serving the chosen visual language. It does not mean applying the same exposure, blur and palette to every shot.

## Project-owned renderers

Declare a source in `film.extensions`, for example:

```json
{"id":"decision-space","source":"components/decision_space.py","design_reference":{"src":"assets/references/look.jpg","reason":"The intended silhouette, material and scale relationship"},"reason":"This idea needs its own spatial action."}
```

The file exports `render(kit, prefix, duration, data, cues, locale)` and returns `html`, `js`, and `reading_order`; optional `layout` can hold geometry evidence. Every reading-order entry has `id`, `role`, `enter_at`, `settle_at`, `depends_on`. Use unique prefixed DOM IDs and deterministic timelines. You may call complete library designs, use its drawing methods, or construct a different visual language. Do not replace the shared renderer in memory and present that replacement as an unchanged library implementation.

`design_reference` can be a classic design ID, `art-etch` / `art-print` / `art-wash`, or a project image with `src` and `reason`. Set a film-level `design_reference` to share one project benchmark; a scene or layer can override it. A project's benchmark is allowed to differ from every preset. The source and reference are tracked for review; a family name does not certify craft.

## Quality floor across implementations

Make the main subject, supporting material and reading order clear at the delivery size. Keep labels and connections distinct; place connectors between actual anchors and reveal them when the relationship is established. Preserve an appropriate caption reserve through entrances and camera motion. Use the bundled geometry tools where applicable, and inspect authored artwork and footage visually where geometry metadata cannot describe them.

Chinese captions normally use one line, English up to two. Split long speech at natural phrase boundaries rather than shrinking or truncating it. The bundled language fonts are usable defaults; a project's type direction may differ when the required glyphs and font files are available.

HyperFrames scenes need timed elements, project-root media paths and one paused seekable timeline. Use media grading for footage rather than CSS filters. Painting/shader effects inside an original illustration are part of that renderer, not footage grading. Run `check` and inspect the actual export.

## Visual review

Rendering produces a candidate, verifies decoding, and prepares comparisons from actual encoded frames and complete component clips. The reference can be the project's chosen artwork or a library example. The report also keeps whole-film direction, rhythm and listening judgments pending; component correctness does not settle them.

Open the reported `review/visual-<export hash>/index.html`. Compare material, silhouette, staging, focal hierarchy, meaningful transformation and reading time, then watch the complete film with its mix. In `review/visual-review.json`, record specific observations, actual viewing/listening and unresolved issues. Run `accept-visuals` only after those judgments are complete. It rejects stale source/export bindings, changed evidence and incomplete recorded reviews; it does not itself possess an aesthetic verdict.

Read the usage prompts as questions. A sustained shot, pure typography or repeated form can be appropriate. No image, effect, cut or component quota is imposed. New techniques should travel to another subject and staging problem; a second palette or dataset proves only parameter substitution.

## Catalogs and existing projects

`catalog --base` builds the twelve classic designs through the same production renderer; omit `--base` for the variant collection. Supply licensed source clips with `--media-dir`, as described in [demo media](../assets/packaging/demo-media/README.md). These catalogs test techniques and inputs, not new-film direction. The artwork examples are code-only studies and need no stock-media download.

Existing films keep their explicit grading, cues and snapshot. Upgrade deliberately to use the new artwork entry or project reference route. Existing approved colors and footage decisions should remain unchanged unless the requested revision includes them.
