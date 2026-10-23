# Visual material: source, generate, or build

Start with what the passage needs to show: a person, action, object, contrast, or relationship. Search and design while the script is still editable. Combine photographic footage, archival images, illustration, and motion graphics where each contributes to the explanation; let the subject determine the mix.

## Choose the material route

| Need | Useful route |
| --- | --- |
| Human behavior, atmosphere, space, or a physical action | Find relevant film, TV, real-world, or stock footage. Inspect the actual shot and its context, rather than selecting by a title or a dramatic thumbnail. |
| A real person, artwork, place, document, or historical object | Start with identifiable sources such as [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) or [The Met Open Access](https://www.metmuseum.org/hubs/open-access). Verify identity, context, resolution, and the selected item's reuse terms. |
| A metaphor or conceptual illustration | Adapt suitable existing art or generate an original illustration when the needed image is missing. Editorial collage can combine cutout figures, sculptures, engravings, photographs, and texture around one clear idea. |
| Exact text, categories, numbers, relationships, or processes | Build or adapt editable HTML/SVG in the [shared renderer](packaging.md). Reuse compatible icons from a consistent collection; [SVG Repo](https://www.svgrepo.com/page/licensing/) is one source with item-specific licenses. |
| A reusable motion element | Existing animations, including assets from [LottieFiles](https://lottiefiles.com/page/license), can save work when their meaning and style fit. Verify reuse terms and compatibility with the rendering pipeline; adapt the timing or rebuild the element when its choreography cannot follow the explanation. |

These are starting points, not exclusive providers or guaranteed matches. Record the actual source and license of a selected file. Generated or reconstructed imagery must not stand in for historical or documentary evidence.

## Select for cinematic light and texture

Look for a readable subject, intentional light, separation from the background, depth, and material detail. Side light, backlight, rim light, practical lamps, or warm/cool contrast can create the dramatic lighting the series uses. Daylight can be equally effective when it gives shape to the subject and suits the mood.

Search by subject or action plus a lighting or camera cue: for example, `person at desk window side light`, `backlit figure hallway slow tracking shot`, or `hands opening book warm practical light`. Use these as search vocabulary, not a fixed look for every topic. A shot should express the passage's situation or idea, rather than merely look expensive.

Inspect the usable range for action, camera movement, highlight and shadow detail, composition, and room for graphics. Grade sources into a coherent palette while preserving visible motion and subject detail. Heavy darkening, saturation, or blur cannot repair an unsuitable shot.

## Compose illustrations and motion around the explanation

Give an illustration or collage a recognizable subject and a clear conceptual role. Match palette, light direction, edge treatment, texture, and scale across its parts. Use generation for imagery that benefits from original pictorial invention; keep precise labels, values, and diagram geometry in editable code.

SVG is a vector format; motion graphics is the animated treatment. Either may be sourced or authored. For explanatory graphics, adapt the bundled component source or write topic-specific elements within its visual system. Arrange real counterparts for a comparison, meaningful items for a group, or explicit nodes and links for a relationship. Reveal them in the order the narration establishes the idea, and hold them long enough to read.

An imported animation still needs the same deterministic timing and seekable states as the film. Choose a simpler custom element when a ready-made animation cannot be inspected, restyled, or synchronized reliably. Use footage or a still directly when it already communicates the point.

## Bundled resources and provenance

- **Fonts:** Source Serif 4 and Inter for English, Noto Serif SC and Noto Sans SC for Chinese, and Barlow Condensed for numbers. Their SIL Open Font Licenses are included.
- **Maps:** Natural Earth land, rivers, and geographic points. These are public-domain datasets; source details are in `assets/packaging/src/maps/source.json`.
- **Voice:** The independently generated D reference and body-v1 settings. Model weights are downloaded separately when needed.
- **Lazy Studio:** The project's review-room code and FEICAI's existing UI kit.
- **Layout previews:** Still images documenting layouts, not a default script or shot list. Pre-rendered demo videos and raw third-party footage are not bundled; use licensed clips to rebuild the catalog.

Recorded stock-footage sources for earlier examples:

- https://mixkit.co/free-stock-video/friends-playing-chess-in-cinematic-light-100109/
- https://mixkit.co/free-stock-video/book-being-leafed-through-seen-in-detail-3819/
- https://mixkit.co/free-stock-video/a-person-reading-a-book-close-up-1724/
- https://mixkit.co/free-stock-video/window-on-a-rainy-day-2846/
- https://mixkit.co/free-stock-video/traffic-on-a-rainy-night-4331/

Source records and used ranges belong in the film project, not as labels on screen. Examples do not grant additional rights to the original files. See [third-party notices](../THIRD_PARTY_NOTICES.md) for the public release's license boundaries and [demo media](../assets/packaging/demo-media/README.md) for rebuilding previews.
