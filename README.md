# Zoo Assets

A library of 500 low-poly 3D models for a toy-style zoo. Every model is built from code using headless Blender Python and mapped to a single shared colour palette texture.

You can browse all models in the web gallery at https://ai-hackathon-only.github.io/zoo-assets/.

## Contents

The library includes 500 models across 13 categories:
- Animals (130 models across 8 body plans)
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
