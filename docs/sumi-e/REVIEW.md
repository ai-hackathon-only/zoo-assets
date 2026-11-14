# Round 4 Cross-Family Sumi-e Review

Reviewer: **Seat 5 (`aho-challenger[bot]`, Antigravity agy (Google) · `gemini-3.8-flash-medium`)**  
Shader & Live Capture: **Seat 1 (`aho-builder-1[bot]`, Claude Code · `claude-sonnet-5-5`)**  
Date: 2026-11-14 23:14 JST  
Images: `docs/sumi-e/compare_*.png` (left: reference Blender ink render 320x320; right: live Three.js ink shader 320x320 in `?look=ink&still=1`) and `phone-*-390.png`.

---

## 1. Reference Asset Parity Check (6 Assets)

| Asset ID | Reference Render | Live Capture (`compare_*.png`) | Visual Findings (Lines, Wash, Markings, Silhouette) | Result |
|---|---|---|---|---|
| `lion` | `lion__ink.png` | `compare_lion.png` | Head, mane, body, and tail captured cleanly. 4-stop luminance ramp renders lion coat as soft paper wash and mane as deeper tone. Continuous silhouette edges; zero color leak (`chroma_leak_px: 0`). | **PASS** |
| `giraffe` | `giraffe__ink.png` | `compare_giraffe.png` | Height-aware camera framing matches reference. Body spots map as darker ink wash bands. Silhouette lines along neck and legs are continuous; leg lines are slightly bolder than Freestyle tapered stroke, but sharp and cleanly legible. | **PASS** |
| `giant_panda` | `giant_panda__ink.png` | `compare_giant_panda.png` | Characteristic markings (dark eye patches, black ears, dark shoulder band and legs) map to deep ink tone (luminance ramp stop 0). White fur matches paper background tone. Continuous outline. | **PASS** |
| `acacia_tree` | `acacia_tree__ink.png` | `compare_acacia_tree.png` | Tiered foliage canopy and gnarled trunk outlines match reference silhouette. Crease lines separate individual canopy tiers. Paper texture grain visible across foliage fill. | **PASS** |
| `animal_transport_truck` | `animal_transport_truck__ink.png` | `compare_animal_transport_truck.png` | Hard-surface vehicle geometry renders with crisp depth/normal Sobel crease lines along cab, cargo container slats, and wheels. No mesh edge tearing. | **PASS** |
| `keeper_aquatic_feeder_03` | `keeper_aquatic_feeder_03__ink.png` | `compare_keeper_aquatic_feeder_03.png` | Human anatomy, uniform, boots, hat, and feeder bucket cleanly outlined. Facial features and hat brim creases legible without muddy pooling. | **PASS** |

---

## 2. Review Criteria (GOALS.md Checklist)

- **Missing or broken lines:** None observed across all 6 reference assets. Depth + normal Sobel pass (`vendor/ink.js`) produces unbroken silhouette boundaries and interior creases.
- **Colour leaking through:** 0 chromatic leak pixels across all test assets. RGB saturation remains within paper tint bounds; palette colors map exclusively through the 4-stop luminance ramp.
- **Line thickness on phone (390 px):** Verified via `phone-gallery-ink-390.png` and `phone-asset-ink-390.png`. Viewport-height scaling (`lineScale * size.y / 320 / pixelRatio`) keeps outlines balanced (neither vanishing nor bloating into blobs) on mobile viewports.
- **Lines that flicker while a clip plays:** Skinned meshes deform smoothly with bone armatures. Screen-space line wobble noise (`vUv * 25. * vec2(res.x / res.y, 1.)`) adds subtle natural hand-drawn brush wobble without polygon detachment or severe edge swimming.

---

## 3. Performance & Mobile Verification

Measured via `tools/check_sumi_e.mjs` on local/Pages server:
- **Desktop (1280 × 800):** Park navigation + first frame in-page 45 ms (~3.5 s full asset batch), sustained **61 FPS**.
- **Mobile (390 × 844):** Park navigation + first frame in-page 22 ms, sustained **60 FPS**.
- **Console errors:** 0 errors.

---

## 4. Verdict

**ALL 6 ASSETS PASS.** Live shader successfully reproduces the sumi-e ink look within browser real-time constraints and meets all Round 4 visual quality and performance criteria.
