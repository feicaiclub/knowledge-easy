# Media Sources and Records

See [SKILL.md](../SKILL.md) for selection methods, lighting standards, and mixed-media decisions. This page provides research starting points and a record format.

## Candidate records

In the project's existing media notes or the sources section of assets.json, record each candidate's purpose, source URL or original file, usable range, original shot identity, action changes, shot size, lighting, and reason for selection or rejection. Keep the project's existing format if it serves these needs. A download URL alone is not enough.

For example, two shots might both suggest hesitation. One shows a hand stopping just short of a door handle, with side lighting and a clear edit point; the other simply shows someone sitting in an office. The specific behavior in the first shot is the reason to choose it. Record what you actually observed instead of inferring shot content from keywords or thumbnails.

## Research starting points

- Use [ShotDeck](https://shotdeck.com/) and [Flim](https://flim.ai/) to study action, composition, shot size, color, and lighting. After finding a reference, verify the original work and a usable source for the footage.
- Wikimedia Commons, open museum collections, and primary documents can help identify people, places, objects, and archival material. Check identity, date, context, and terms of use.
- Choose stock libraries, self-shot footage, user-provided videos, or other available sources according to the shot's purpose. Download convenience is not an aesthetic criterion. A creator's visual style does not establish which stock library they use.
- Use original SVG, Canvas, photo collage, or generated media for specific mechanisms, spatial metaphors, and actions that are difficult to source. Do not present generated scenes or reconstructions as documentary records.

## Original shot identification

When a project requires unique moving shots, audit-media reads placements:

```json
{
  "sources":[],
  "placements":[{
    "id":"shot-a","file":"assets/media/door.mp4",
    "original_shots":["source-video:shot-012"],
    "source_in":12.4,"source_out":15.8,
    "use":"The hand approaches the door handle, then stops just before the narrative turn."
  }]
}
```

The tool currently uses id, file, original_shots, and optional static. source_in, source_out, and use support manual comparison. Mark a still image with static: true. Establish a moving shot's identity from the original video rather than generating a seemingly unique ID from its filename.

The command checks for repeated identities in the records; it does not recognize the edited footage automatically. During production, compare the records against the actual film.json, source ranges, and export. See [Licenses and Sources](sources.md) for fonts, geographic data, and the default voice.
