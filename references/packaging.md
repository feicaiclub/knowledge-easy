# Using the component library

Start with the [visual handbook](visual-handbook.html), then choose a component for the specific explanation the scene needs. The library establishes a visual system; it does not require every film to use the same graphics or opening.

The [source directory](../assets/packaging/src/README.md) contains the shared renderer. `render(component, instance_id, duration, data, cues, locale)` returns editable HTML, deterministic motion, and reading order. `variants.json` provides English examples; `locales/zh-CN/variants.json` retains Chinese examples. `base_catalog.py` contains the twelve base designs.

`init` installs a versioned source snapshot, maps, and fonts into the film project. `kit/editorial-lock.json` records hashes. `build` calls that snapshot and writes `research/component-usage.json`. Use `install-pack --update` for an intentional upgrade; do not quietly change a delivered film.

```sh
sh "<skill>/scripts/run.sh" catalog --project "<new-demo-project>" --language en-US --media-dir "<licensed-clips>"
sh "<skill>/scripts/run.sh" render --project "<new-demo-project>" --output final/catalog.mp4
```

The handbook includes still previews and written motion guidance. Demo videos are not bundled. To render a local motion catalog, supply your own licensed clips as described in [demo media](../assets/packaging/demo-media/README.md); raw third-party source clips are not redistributed. Add `--base` to build the twelve base designs. Select `zh-CN` for Chinese samples. Catalogs reuse sample footage to compare designs; production films still use each original moving shot once. New reusable variants need source, input documentation, a rendered example using another topic, and an updated handbook entry.

Use Source Serif 4 and Inter for English, the Noto families for Chinese, and the same palette and layout principles in both. Preserve words and phrases when wrapping English copy. Do not solve overflow by shrinking it into unreadable type. See [language support](language.md).

HyperFrames scenes declare timed elements with start and duration, use project-root media paths, mute B-roll, and register a single paused timeline in `window.__timelines`. Visible motion must be seekable and deterministic. Use the media-grading contract rather than CSS filters on footage. Run `check` after changes and inspect the export.

Review baselines, group alignment, negative space, visual weight, line endpoints, and caption clearance. Check entrances, moving transitions, holds, and exits. Establish the subject before connections and reveal the conclusion when the narration reaches it.

Maps use the bundled Natural Earth land and river data. Verify historical names, boundaries, and routes for each topic. An illustrative area is not a historical border. Keep maps large enough to explain spatial relationships, with coordinated titles, labels, and notes.
