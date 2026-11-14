# Sumi-e (ink brush) look: owner's reference for round 4

The owner tried 21 looks on six test assets (`all-styles-contact-sheet.jpg`) and picked **ink brush (sumi-e)**. These renders are the target for round 4. They were made with Claude Code before the round, from the GLBs on `main`, with no change to the assets.

| file | what it shows |
|---|---|
| `*__ink.png` | six assets in the ink look, 320 px |
| `lion-clips-ink.jpg` | the lion's rig clips in ink: 6 walk frames, 3 eat frames, 1 idle frame |
| `all-styles-contact-sheet.jpg` | all 10 cel and paper variants side by side (ink is one column) |

## How the reference is made (Blender, `tools/sumi-e/`)

`style_v2.py` holds every style; the ink branch is `style(ob, "ink", img)`. `clip_check.py` loads an exported GLB with its clips and renders frames in ink:

```
blender -b -noaudio --factory-startup --python tools/sumi-e/clip_check.py -- . /tmp/ink animals/lion
```

Measured on the owner's Mac (M2 Max): 10 frames of the lion at 320 px in 7 s, Blender start included, so about 0.5 s per frame. One frame is about 100 KB as a full-colour PNG.

The numbers a real-time version needs to match:

- **Paper**: background RGB `(0.93, 0.89, 0.80)`, world strength 1.0, plus a light noise texture over the whole image (`paper_bg`).
- **Grey wash** (the fill): luminance of the asset's palette colour, raised to the power 0.7, times a soft light term (sun at 50° pitch, 30° yaw), then a 4-stop ramp with ease between stops:
  `0.00 → (0.12, 0.12, 0.13)`, `0.12 → (0.50, 0.50, 0.50)`, `0.40 → (0.80, 0.79, 0.76)`, `0.70 → (0.95, 0.93, 0.88)`. Colour is dropped on purpose: the look is ink on paper.
- **Brush line** (outline): Freestyle silhouette and border edges, colour `(0.03, 0.03, 0.03)`, thickness 5.5 px at 320 px, round caps, Perlin 1D noise (frequency 25, amplitude 0.48) so the width wobbles, and an along-stroke taper from 0.2 to 1.6 that peaks at 35 % of the stroke.
- **Fine line** (inner creases): crease angle 140°, colour `(0.1, 0.1, 0.1)`, thickness 1.6 px, same taper, no noise.
- Camera: 50 mm, from the front-right and above (direction `(1.0, -1.25, 0.8)`), framing the bounding sphere.

Freestyle does not exist in the browser, so the live version has to rebuild these lines another way (for example an edge pass on depth and normals, with noise on the line width). The tapered stroke ends are the hardest part to copy in real time.
