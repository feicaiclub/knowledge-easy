# Licenses and Sources

## Original project work

The project's own code, instructions, and earlier original SVG illustrations use the [MIT License](licenses/MIT.txt). The current drawing tools use native Canvas 2D and do not include the reference project's brush implementation, color-separation implementation, or example scenes.

## Default voice reference

assets/voice/reference.wav is the user-selected “Steady Male Voice — Tight Phrasing and Clear Emphasis.” It was generated with Qwen3-TTS CustomVoice's Ryan preset, without a human reference recording, retiming, pitch lowering, or voice-character postprocessing. See the [Voice Profile](../assets/voice/profile.json) for the text, model revision, settings, and checksum. The model and its outputs remain subject to the model provider's applicable terms; this project's code license does not replace them.

## Fonts and geographic data

The following fonts retain their original licenses:

- [Noto Serif SC](../assets/packaging/fonts/notoserifsc-OFL.txt)
- [Noto Sans SC](../assets/packaging/fonts/notosanssc-OFL.txt)
- [Barlow Condensed](../assets/packaging/fonts/barlow-OFL.txt)

Map geometry comes from Natural Earth, which is in the public domain. See the [geographic data source record](../assets/packaging/src/maps/source.json). Verify historical names, periods, borders, and routes for the specific subject.

## Live-action media

The Skill does not include earlier component screenshots or third-party film clips. Supply media appropriate to the production's intended use. See [Media Sources and Records](assets.md) and [Example Media Slots](../assets/packaging/demo-media/README.md).

## External runtime dependencies

Runtime libraries, browsers, and models are installed during setup when needed and retain their own licenses and terms. They are not bundled as a runtime environment in the Skill's source directory.

## Copied visual studies

reference-portrait.svg, reference-balance.svg, and reference-writing.svg are visual studies copied at the user's explicit request, based on the figures, compositions, and graphic language of [BUCK / Notion — Think it. Make it.](https://buck.co/work/notion-think-it-make-it). They were redrawn as local vector paths with editable layers. The project does not claim the third-party characters or compositions as original work, and its code license does not replace the original work's rights.

The type treatments in lit-title and medallion-labels reference the Song-style letterforms, lit faces, and shadows in the user-selected video. They use the available Noto Serif SC font with adjusted weight and surface treatment. The exact typeface in the original video has not been identified, so the project does not claim an exact font match.
