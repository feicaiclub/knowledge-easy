# Shared visual components

[Visual handbook](../../../references/visual-handbook.html) · [Production guide](../../../references/packaging.md)

- `editorial.py` and `editorial.css`: shared production renderer and layouts.
- `pack.css` and `tokens.json`: fonts, colors, spacing, and information hierarchy.
- `variants.json` and `renderer-contract.json`: production variants and their inputs.
- `base_catalog.py`, `components.json`, and `examples.json`: twelve base designs and editable slots.
- `locales/`: language-specific example copy; layout behavior stays in the shared renderer.
- `layout.py`: diagram information bounds, image/label obstacles, and connector/arrowhead clearance.
- `geography.py` and `maps/`: map projection, land, and river data.
- `acceptance.json` and `motion-contract.json`: layout and reveal-order requirements.
- `validation-baseline.json`: prior cross-content checks.

`scripts/vibe.py install-pack` copies a versioned snapshot into a film project. Fonts come from `../fonts/`. Runtime dependencies are prepared outside this Skill by `scripts/bootstrap.py`.

Version 1.3.0 makes `feedback-loop`, `evidence-collage`, and `context-reveal` directly callable by the production renderer. These adapt the existing feedback, evidence, and context families. The production guide explains selection, blurred-video backgrounds, caption clearance, and intentional full-frame exceptions.
