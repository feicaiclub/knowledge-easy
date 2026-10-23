# Using the component library

Start with the [visual handbook](visual-handbook.html), then choose a component for the specific explanation the scene needs. The library establishes a visual system; it does not require every film to use the same graphics or opening.

The [source directory](../assets/packaging/src/README.md) contains the shared renderer. `render(component, instance_id, duration, data, cues, locale)` returns editable HTML, deterministic motion, and reading order. `variants.json` provides English examples; `locales/zh-CN/variants.json` retains Chinese examples. `base_catalog.py` contains the twelve base designs.

`init` installs a versioned source snapshot, maps, and fonts into the film project. `kit/editorial-lock.json` records hashes. `build` calls that snapshot and writes `research/component-usage.json`. Use `install-pack --update` for an intentional upgrade; do not quietly change a delivered film.

## Choose the explanation before the template

Use the script and visual outline developed in the [production guide](workflow.md). For each graphic, write its `purpose`: what becomes clearer by seeing it? Select or adapt from the full library for the actual entities, evidence, and relationships. Repeated components are fine when the reasoning repeats; there is no component quota. If the graphic only restates a subtitle, reconsider its purpose or let the footage carry the passage.

Keep precise text, values, diagrams, and connectors editable in the shared renderer's HTML/SVG. Source or generate illustrations and cutouts when they help explain the idea, then compose them with the same hierarchy, palette, and reveal logic. Existing SVGs or motion assets are useful ingredients when their style, meaning, and timing fit; they do not determine the argument. See the [material guide](assets.md) for sourcing and construction choices.

| What the viewer needs to understand | Starting form | Production entry |
| --- | --- | --- |
| How an action reinforces itself | A cycle whose last arrow returns to the first stage | `feedback-loop` |
| What two actual records show or omit | Source images, crops, and attached readings | `evidence-collage`, `evidence-sheet` |
| How a detail changes meaning in context | One continuous image that opens to a wider view | `context-reveal` |
| How people, causes, or ideas relate | Nodes and clear connecting lanes | `relation-bridge`, `foundation`, `concept-link` |
| What changed between moments | A shared time axis or paired milestones | `milestone-pair`, the base timeline design |
| Where events happened | A large shared map with meaningful routes or focus | `map-decision`, `map-focus-chain` |

`feedback-loop`, `evidence-collage`, and `context-reveal` adapt the base designs for direct `film.json` use. Their localized examples are in `variants.json` and `locales/zh-CN/variants.json`. Other base designs remain editable catalog source: adapt them when appropriate, rather than replacing their function with a convenient card. Update the shared source and document reusable extensions.

## Keep the footage visible

An explanatory card or diagram normally has a **playing video** behind it, softly defocused and consistently graded. `build` applies a modest grade and blur when those values are omitted; set the grade for the actual shot. Check that scene changes and motion remain perceptible after export. A heavily darkened, opaque, or over-blurred background that reads as a flat fill fails this intent.

Supply `background.src` and its source timing. Do not add a second full-frame `footage` layer above it. Put foreground media in the component. `annotation` and `dateline` may sit on clear footage. A full-frame map, sourced document, or intentional interlude can omit the video when the explanation calls for it: state why in `surface_reason`. The builder rejects an unexplained missing background rather than silently producing a solid canvas. Never use `surface_reason` just to bypass this check.

## Connectors, alignment, and safe areas

Lay out image bounds, text bounds, and connector lanes together. Use shared baselines and group centers. Attach lines to defined node edges with a visible gap; route around every intervening image, card, and label. Draw a relationship after both anchors have settled. Keep the arrowhead clear and point it at the intended node. Raising `z-index` alone does not fix a route through a picture.

The normal stack is background video → surfaces/images → connectors in reserved lanes → labels. Deliberate callouts over an image need their own legible treatment and a meaningful target; they are not a reason to let unrelated pictures obscure diagram edges.

At 1920×1080, the shared diagram information area is x=150–1770 and y=80–830. The lower region reserves space for one Chinese subtitle line or up to two English lines; decorative surfaces and full-bleed media can extend beyond the information area. Keep at least 16 px around routed lines and enough additional space for arrowheads and stroke width. These are landscape defaults: redesign and measure for another aspect ratio or caption treatment.

Check the entrance, settled state, transitions, and exit with actual captions, long labels, and the selected language. A card can be clear in its final position yet sweep across a line while entering. Use the shared `layout.py` checks when defining routes; `feedback-loop` and `evidence-collage` already validate their image/label obstacles, and `context-reveal` validates its information bounds. Existing variants and custom scenes still require visual inspection; geometry checks are not a general pixel-occlusion detector.

`build` writes `review/visual-plan.json` with component/family usage and review prompts. Resolve those prompts through design judgment, not by adding unnecessary graphics. Inspect the actual export for background visibility, overlapping labels/lines, safe edges, and caption collisions.

```sh
sh "<skill>/scripts/run.sh" catalog --project "<new-demo-project>" --language en-US --media-dir "<licensed-clips>"
sh "<skill>/scripts/run.sh" render --project "<new-demo-project>" --output final/catalog.mp4
```

The handbook includes still previews and written motion guidance. Demo videos are not bundled. To render a local motion catalog, supply your own licensed clips as described in [demo media](../assets/packaging/demo-media/README.md); raw third-party source clips are not redistributed. Add `--base` to build the twelve base designs. Select `zh-CN` for Chinese samples. Catalogs reuse sample footage to compare designs; production films still use each original moving shot once. New reusable variants need source, input documentation, a rendered example using another topic, and an updated handbook entry.

Use Source Serif 4 and Inter for English, the Noto families for Chinese, and the same palette and layout principles in both. Preserve words and phrases when wrapping English copy. Do not solve overflow by shrinking it into unreadable type. See [language support](language.md).

HyperFrames scenes declare timed elements with start and duration, use project-root media paths, mute B-roll, and register a single paused timeline in `window.__timelines`. Visible motion must be seekable and deterministic. Use the media-grading contract rather than CSS filters on footage. Run `check` after changes and inspect the export.

Review baselines, group alignment, negative space, visual weight, line endpoints, and caption clearance. Check entrances, moving transitions, holds, and exits. Establish the subject before connections and reveal the conclusion when the narration reaches it. Use the checks above for all graphic scenes, including newly designed ones.

Maps use the bundled Natural Earth land and river data. Verify historical names, boundaries, and routes for each topic. An illustrative area is not a historical border. Keep maps large enough to explain spatial relationships, with coordinated titles, labels, and notes.
