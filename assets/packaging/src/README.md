# Shared visual components

[Visual handbook](../../../references/visual-handbook.html) · [Production guide](../../../references/packaging.md)

- `editorial.py` and `editorial.css`: shared production renderer and layouts.
- `pack.css` and `tokens.json`: fonts, colors, spacing, and information hierarchy.
- `variants.json` and `renderer-contract.json`: production variants and their inputs.
- `base_catalog.py` and `base_support.py`: the original twelve compositions with production inputs, foreground media and narration cues.
- `components.json` and `locales/*/base-examples.json`: base design definitions and complete content examples.
- `locales/`: language-specific example copy; layout behavior stays in the shared renderer.
- `layout.py`: diagram information bounds, image/label obstacles, and connector/arrowhead clearance.
- `geography.py` and `maps/`: map projection, land, and river data.
- `acceptance.json` and `motion-contract.json`: layout and reveal-order requirements.
- `validation-baseline.json`: prior cross-content checks.

`scripts/vibe.py install-pack` copies a versioned snapshot into a film project. Fonts come from `../fonts/`. Runtime dependencies are prepared outside this Skill by `scripts/bootstrap.py`.

Version 1.4.0 calls all twelve base designs directly through `render`, with explicit text/media inputs and semantic cues. Catalogs use that same path. `scripts/composition.py` combines instances and records explicit project extensions. `scripts/visual_review.py` creates export-bound handbook comparisons and validates recorded visual judgments; technical success never marks design quality approved. See the production guide for complete inputs, composition and acceptance commands.
