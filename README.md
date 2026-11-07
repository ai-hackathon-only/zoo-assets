# Zoo Assets

A library of 566 low-poly 3D models for a toy-style zoo (500 base assets plus 66 procedural animal variants). Every model is built from code using headless Blender Python and mapped to a single shared colour palette texture.

You can browse all models in the web gallery at https://ai-hackathon-only.github.io/zoo-assets/ or explore the procedural 3D zoo map at https://ai-hackathon-only.github.io/zoo-assets/park/.

## Contents

The library includes 566 models across 13 base categories plus variants:
- Animals (130 base models across 8 body plans)
- Animal Variants (66 baby and rare morph variants across 33 species)
- Facilities (70 enclosures, fences, gates, shelters, and paths)
- Plants and trees (55 species)
- Landscape and rocks (45 terrain pieces and boulders)
- Decor (30 zoo decorations)
- Visitors (25 figures)
- Vehicles (25 trains, carts, and service trucks)
- Keepers (20 staff figures with uniforms and tools)
- Food and feeding (20 food items and troughs)
- Enrichment toys (20 animal play items)
- Gift shop (20 souvenirs and toys)
- Vet equipment (20 medical tools and crates)
- Benches and signs (20 park furniture pieces)

All models share one palette texture (`assets/palette.png`). They have clean origins at floor center, real-world meter scales, and strict triangle limits (under 5,000 for animals, under 3,000 for keepers, under 10,000 for facilities, and under 2,000 for all other items).

## Procedural Zoo Map (Park)

The interactive 3D zoo map at `park/` (https://ai-hackathon-only.github.io/zoo-assets/park/) assembles GLB assets into complete procedural zoos in the browser using three.js.

Key capabilities:
- **Controls**: Adjust zoo size (80 m to 600 m), asset density, visitor population (0 to 300 people), and layout style.
- **Layout Styles**: Choose between **Grid** (orthogonal avenue blocks), **Loop** (perimeter ring thoroughfare with central plaza), and **Radial** (central grand plaza concourse with radiating boulevards).
- **Shuffle & Seed**: Generate randomized layouts from a seed string. Settings and seed sync to URL parameters for sharing.
- **Top-Down Minimap**: Click any enclosure on the 2D overview to jump the 3D camera to that animal.
- **Batch Rendering**: Loads each model file once and draws duplicate assets with instancing.

## Layout Generator Rules

The layout engine (`park/generator.js`) is written in pure JavaScript with no DOM dependencies. It turns a settings object and a seed string into a structured layout matching `park/layout.schema.json`.

Rules enforced by the generator:
- **Single Entrance**: Exactly one park gate on the outer perimeter.
- **Path Connectivity**: Continuous paths link the entrance to every enclosure and facility.
- **Enclosure Sizing**: Footprints scale from each animal species' real-world `size_m`.
- **Variant Placement**: When present, babies and rare morphs spawn next to adults in their enclosures.
- **No Overlaps**: Enclosures, facilities, and boundary fences maintain clear non-overlapping boundaries.
- **Facility Placement**: Kiosks, shelters, and restrooms sit along path edges.
- **Visitor Spawning**: People stand on paths or gather around enclosures.
- **Full Coverage**: At maximum settings (600 m size, 1.0 density), all 130 animal species are placed in the park.

To verify layout rules across 200 random seeds, run:

```bash
node park/check_layout.mjs
```

## Modular Grid System

Environmental assets (fences, enclosures, kiosks, paths, and gates) follow a standard metric grid agreed in Round 2:
- **Grid Cell**: 2 m standard cell.
- **Edge Pieces**: 0.5 m depth along grid lines.
- **Posts & Corners**: 0.5 m × 0.5 m footprint.
- **Pivot Origin**: Bottom-center (minimum Z = 0, center X = 0, center Y = 0) with a 1 mm tolerance.

`validate.py` checks that all facility bounding boxes snap to multiples of the 2 m grid and match the bottom-center pivot convention.

## Animal Variants

To add diversity to the zoo population, 33 animal species have three distinct models:
1. **Standard Adult**: Base species model.
2. **Baby**: Scaled down to 0.45× body dimensions with enlarged head proportions for a toy aesthetic.
3. **Rare Color Mutation**: Alternative colorways (such as albino, melanistic, or distinct markings) drawn from the shared palette texture.

All 66 variants are generated programmatically via `tools/make_variants.py` and `lib/variants.py`. They are indexed in `assets.json`, include individual thumbnails, and pass `validate.py` scale and triangle budgets.

## Rebuilding

### Requirements

- Blender 5.2+ (run headless from your shell)
- Python 3.10+

### Rebuild all assets

To generate all 500 GLB files and thumbnail renders from scratch:

```bash
blender -b -noaudio --factory-startup --python build_all.py
```

### Validate models

To test models against scale, budget, texture, and naming rules:

```bash
blender -b -noaudio --factory-startup --python validate.py
```

To update asset metrics (triangle count, file size, paths) in `assets.json`:

```bash
blender -b -noaudio --factory-startup --python validate.py -- --write
```

## Adding a new asset

Follow these steps to add an asset:

1. **Add entry to assets.json**: Add an object with an `id`, `category`, `name`, `real_world_size_m`, `generator`, and `budget_tris`.
2. **Add generator code**: Open the generator script for that category in `generators/`. Define the mesh shapes using Blender primitives or BMesh operations. Assign UV coordinates pointing to colors in `assets/palette.png`.
3. **Build the model**: Run the generator script in headless Blender to export the `.glb` file and `.png` thumbnail.
4. **Validate**: Run `blender -b -noaudio --factory-startup --python validate.py` to ensure the model satisfies all size, triangle, and scale constraints.

## Licenses

- Code: MIT License
- 3D models and thumbnails: Creative Commons Zero v1.0 Universal (CC0 1.0 Public Domain Dedication)
