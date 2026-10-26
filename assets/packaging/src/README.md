# Versioned visual toolkit

[Direction](../../../references/direction.md) · [Rendering](../../../references/packaging.md) · [Original illustration](../../../references/illustration.md)

- `editorial.py`, `base_catalog.py`, `base_support.py` and the CSS files preserve the classic editorial layouts.
- `artwork.py` and `artwork/` supply an open-ended drawing entry, material engines, profiles and separately authored example scenes.
- `layout.py` checks declared diagram geometry; it is not an aesthetic judge for every renderer.
- `geography.py` and `maps/` provide geographic geometry.
- `renderer-contract.json` records the implementation boundary.

Version 2.0 removes a compulsory project look: surfaces, grading and project references are explicit choices. A film can use complete classic layouts, code artwork, footage or project-owned implementations. Example scenes are techniques to study, not the prescribed structure of a new film.

The installer locks source and fonts per project. Existing snapshots remain until explicitly upgraded. Brush/print kernel attribution is included in `artwork/LEMO-LICENSE.txt`.
