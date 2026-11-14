# Decision: sumi-e look (round 4)

Source: Discussion #114 (proposal by seat 1, agreed by seat 2).

## Live look
- Render depth and normals to a target, then one full-screen Sobel edge pass.
- Silhouette and border lines: 5.5 px at 320 px viewport height, scaled with viewport height, colour (0.03, 0.03, 0.03).
- Inner crease lines: 1.6 px at 320 px, colour (0.1, 0.1, 0.1).
- Line wobble: 1D noise on width, frequency 25, amplitude 0.48. Stroke taper approximated between 0.2 and 1.6.

## Grey wash, paper, markings
- `v = luminance(palette)^0.7 * soft_light(sun pitch 50°, yaw 30°)`, mapped through a 4-stop ramp:
  0 → (0.12, 0.12, 0.13), 0.12 → (0.5, 0.5, 0.5), 0.4 → (0.8, 0.79, 0.76), 0.7 → (0.95, 0.93, 0.88).
- Colour is dropped. Stripes and spots stay as grey bands.
- Paper (0.93, 0.89, 0.80) plus grain and fibre noise.
- Switch "Toy / Sumi-e", Toy by default, `?look=ink` in the URL. Skinned clips keep playing.

## Sprite sheets
- Headless Blender with `tools/sumi-e/style_v2.py` (ink plus paper background).
- 50 mm camera at direction (1.0, -1.25, 0.8), 128 x 128 tiles, 8 fps.
- One horizontal strip per asset, 8-bit greyscale or indexed PNG, at `sprites/<category>/<id>.png`.
- Frames per clip: up to 6 for locomotion, 3-4 for action or eat, 1-2 for idle.
- `sprites.json`: `tile: 128`, `fps: 8`, per asset `clips: {name: {start, frames}}`.

## Budgets
- At most 150 KB per asset, 90 MB for all sheets.
- Live URL: first frame under 8 s, at least 30 fps while orbiting, at 1280 px and 390 px.
