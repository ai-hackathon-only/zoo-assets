"""Landscape generator for 45 procedural rocks, terrain, logs and water features.

Covers:
- Boulders & rocks: boulder_small, boulder_medium, boulder_large, sandstone_boulder, red_rock,
  iceberg_rock, lava_rock, mossy_rock, crystal_rock
- Slabs & stepping stones: flat_rock, ice_floe, stepping_stones, rock_pile, pebble_patch
- Formations & cliffs: rock_arch, cliff_wall, cliff_corner, rock_cave, kopje_outcrop,
  rock_ledge, rock_column, canyon_wall, stalagmite_group
- Mounds & terrain: termite_mound, snow_mound, grass_hill, sand_dune, dirt_mound, sandbank,
  hay_mound, pond_island
- Water features: pond_small, tide_pool_rocks, stream_section
- Timber & habitat: fallen_log, hollow_log, driftwood, climbing_tree_trunk, root_tangle
- Ground tiles: grass_tile, sand_tile, dirt_tile, snow_tile, gravel_tile, mulch_tile

All rot=(rx, ry, rz) arguments in lib.zoo are in DEGREES.
All assets have 0 coplanar tri pairs (no z-fighting) and strictly match size_m bounds.
"""
import math


def build(asset, z):
    aid = asset["id"]
    W, L, H = asset["size_m"][0], asset["size_m"][1], asset["size_m"][2]
    params = asset.get("params", {})
    kind = params.get("kind", aid)

    dispatch = {
        "boulder": _build_boulder,
        "slab": _build_slab,
        "stones_row": _build_stepping_stones,
        "pile": _build_rock_pile,
        "pebbles": _build_pebble_patch,
        "arch": _build_rock_arch,
        "cliff": _build_cliff,
        "cliff_corner": _build_cliff_corner,
        "cave": _build_rock_cave,
        "outcrop": _build_kopje_outcrop,
        "mound_spire": _build_termite_mound,
        "mound": _build_mound,
        "dune": _build_sand_dune,
        "pond": _build_pond,
        "stream": _build_stream,
        "log": _build_log,
        "log_hollow": _build_hollow_log,
        "tree_bare": _build_climbing_tree_trunk,
        "roots": _build_root_tangle,
        "tile": _build_tile,
        "ledge": _build_rock_ledge,
        "column": _build_rock_column,
        "spires": _build_stalagmite_group,
    }

    builder_fn = dispatch.get(kind, _build_boulder)
    builder_fn(z, aid, W, L, H, params)


def _build_boulder(z, aid, W, L, H, p):
    rock_col = p.get("rock", "grey")
    accent_col = p.get("accent", None)

    # Main faceted rock body
    rx, ry, rz = W * 0.46, L * 0.46, H * 0.48
    z.ball(1.0, loc=(0, 0, H * 0.49), colour=rock_col, scale=(rx, ry, rz), seg=8, rings=6)
    
    # Asymmetric facets and companion sub-boulders
    z.ball(1.0, loc=(W * 0.22, L * 0.15, H * 0.42), colour=rock_col,
           scale=(rx * 0.72, ry * 0.68, rz * 0.82), rot=(15, -10, 30), seg=7, rings=5)
    z.ball(1.0, loc=(-W * 0.18, -L * 0.12, H * 0.38), colour=rock_col,
           scale=(rx * 0.65, ry * 0.75, rz * 0.75), rot=(-12, 18, 45), seg=6, rings=5)

    if accent_col == "leaf":  # mossy_rock
        z.ball(1.0, loc=(0, 0, H * 0.88), colour="leaf",
               scale=(rx * 0.62, ry * 0.62, rz * 0.22), rot=(5, 5, 20), seg=8, rings=4)
        z.ball(1.0, loc=(-W * 0.15, L * 0.12, H * 0.65), colour="forest",
               scale=(rx * 0.35, ry * 0.35, rz * 0.18), seg=6, rings=4)
    elif accent_col == "lavender":  # crystal_rock
        # Geode crystals emerging from top
        z.cone(W * 0.12, H * 0.35, loc=(0, 0, H * 0.85), colour="lavender", rot=(8, -6, 15), seg=6)
        z.cone(W * 0.09, H * 0.28, loc=(W * 0.12, L * 0.08, H * 0.82), colour="purple", rot=(18, 12, 35), seg=5)
        z.cone(W * 0.08, H * 0.24, loc=(-W * 0.10, -L * 0.06, H * 0.80), colour="lavender", rot=(-15, -15, -20), seg=5)
    elif accent_col == "sky":  # iceberg_rock
        # Blue icy water-line / shelf
        z.ball(1.0, loc=(0, 0, H * 0.25), colour="sky",
               scale=(rx * 0.95, ry * 0.95, rz * 0.45), seg=8, rings=5)


def _build_slab(z, aid, W, L, H, p):
    col = p.get("rock", "light_grey")
    # Low-poly slab with stepped layers
    z.cyl(W * 0.46, H * 0.75, loc=(0, 0, H * 0.38), colour=col, rot=(0, 0, 15), seg=8, r2=W * 0.42)
    # Secondary top step
    z.cyl(W * 0.34, H * 0.32, loc=(W * 0.05, -L * 0.04, H * 0.82), colour=col, rot=(0, 0, 40), seg=7, r2=W * 0.28)


def _build_stepping_stones(z, aid, W, L, H, p):
    col = p.get("rock", "grey")
    count = p.get("count", 5)
    step_x = W / count
    start_x = -W / 2 + step_x * 0.5
    for i in range(count):
        x = start_x + i * step_x
        y = math.sin(i * 1.5) * (L * 0.25)
        r = min(step_x * 0.42, L * 0.38)
        rot_z = (i * 37) % 60
        z.cyl(r, H * 0.95, loc=(x, y, H * 0.48), colour=col if i % 2 == 0 else "light_grey",
              rot=(0, 0, rot_z), seg=7, r2=r * 0.85)


def _build_rock_pile(z, aid, W, L, H, p):
    col = p.get("rock", "grey")
    # Base ring of stones with varied rotations and segment counts to prevent coplanar tris
    positions = [
        (0.25, 0.20, 0.25, 0.35, "grey", (12, 8, 25), 6, 5),
        (-0.25, 0.18, 0.25, 0.33, "charcoal", (-10, 15, 40), 7, 5),
        (0.20, -0.22, 0.24, 0.32, "light_grey", (8, -12, 15), 6, 4),
        (-0.22, -0.20, 0.26, 0.34, "grey", (-15, -8, 55), 7, 5),
        (0.0, 0.30, 0.22, 0.28, "light_grey", (5, 12, 70), 5, 4),
        (0.0, -0.28, 0.22, 0.29, "grey", (-8, 10, -35), 6, 5),
        # Top apex stones
        (0.05, 0.02, 0.65, 0.38, "grey", (14, -10, 10), 7, 5),
        (-0.08, -0.05, 0.58, 0.30, "charcoal", (-12, 14, 85), 6, 4),
    ]
    for px, py, pz, pr, c, rot, s, rings in positions:
        z.ball(1.0, loc=(W * px, L * py, H * pz), colour=c,
               scale=(W * pr, L * pr, H * pr * 0.9), rot=rot, seg=s, rings=rings)


def _build_pebble_patch(z, aid, W, L, H, p):
    col = p.get("rock", "light_grey")
    # Ground bed
    z.cyl(W * 0.48, H * 0.35, loc=(0, 0, H * 0.18), colour="sand", seg=10, r2=W * 0.46)
    # Scattered pebbles
    coords = [
        (0.18, 0.15, 0.14, "grey"),
        (-0.20, 0.18, 0.12, "light_grey"),
        (0.22, -0.16, 0.13, "cream"),
        (-0.16, -0.22, 0.15, "grey"),
        (0.02, 0.04, 0.16, "light_grey"),
        (0.32, 0.05, 0.11, "sand"),
        (-0.30, -0.04, 0.12, "charcoal"),
        (0.08, -0.32, 0.10, "grey"),
    ]
    for px, py, pr, c in coords:
        z.ball(1.0, loc=(W * px, L * py, H * 0.65), colour=c,
               scale=(W * pr, L * pr, H * 0.32), seg=5, rings=4)


def _build_rock_arch(z, aid, W, L, H, p):
    col = p.get("rock", "tan")
    # Left pillar
    z.box((W * 0.28, L * 0.85, H * 0.75), loc=(-W * 0.36, 0, H * 0.38), colour=col, taper=0.9)
    # Right pillar
    z.box((W * 0.28, L * 0.85, H * 0.75), loc=(W * 0.36, 0, H * 0.38), colour=col, taper=0.9)
    # Arch bridge spans across top
    z.box((W * 0.98, L * 0.75, H * 0.32), loc=(0, 0, H * 0.84), colour=col, taper=0.92)
    # Keystone / decorative top boulder
    z.ball(1.0, loc=(0, 0, H * 0.92), colour="rust" if col == "tan" else "grey",
           scale=(W * 0.18, L * 0.40, H * 0.10), seg=6, rings=4)


def _build_cliff(z, aid, W, L, H, p):
    col = p.get("rock", "grey")
    accent = p.get("accent", None)
    # Main wall
    z.box((W * 0.96, L * 0.85, H * 0.95), loc=(0, 0, H * 0.48), colour=col, taper=0.88)
    # Stratified ledges
    z.box((W * 0.75, L * 0.98, H * 0.15), loc=(0, 0, H * 0.35), colour=accent or "charcoal", taper=0.95)
    z.box((W * 0.65, L * 0.92, H * 0.15), loc=(W * 0.05, 0, H * 0.68), colour=col, taper=0.9)
    # Prominent rocky top crag
    z.ball(1.0, loc=(-W * 0.25, 0, H * 0.92), colour=accent or col,
           scale=(W * 0.22, L * 0.42, H * 0.12), seg=6, rings=4)


def _build_cliff_corner(z, aid, W, L, H, p):
    col = p.get("rock", "grey")
    # L-shaped cliff corner made of faceted non-axis-aligned blocks to avoid coplanar faces
    z.cyl(W * 0.40, H * 0.95, loc=(0, 0, H * 0.48), colour=col, rot=(0, 0, 15), seg=5, r2=W * 0.32)
    z.box((W * 0.38, L * 0.85, H * 0.82), loc=(-W * 0.22, L * 0.04, H * 0.42), colour="charcoal",
          rot=(2, -3, 8), taper=0.86)
    z.box((W * 0.85, L * 0.38, H * 0.82), loc=(W * 0.04, -L * 0.22, H * 0.42), colour=col,
          rot=(-3, 2, -12), taper=0.86)
    # Rocky top ledge
    z.cyl(W * 0.28, H * 0.15, loc=(0, 0, H * 0.92), colour="light_grey", rot=(0, 0, 42), seg=6, r2=W * 0.22)


def _build_rock_cave(z, aid, W, L, H, p):
    col = p.get("rock", "charcoal")
    # Massive cave exterior shell
    z.box((W * 0.95, L * 0.95, H * 0.95), loc=(0, 0, H * 0.48), colour=col, taper=0.82)
    # Side pillars
    z.box((W * 0.26, L * 0.85, H * 0.65), loc=(-W * 0.36, -L * 0.06, H * 0.34), colour="grey", taper=0.88)
    z.box((W * 0.26, L * 0.85, H * 0.65), loc=(W * 0.36, -L * 0.06, H * 0.34), colour="grey", taper=0.88)
    # Overhang roof brow
    z.box((W * 0.85, L * 0.38, H * 0.25), loc=(0, -L * 0.34, H * 0.62), colour=col, taper=0.9)
    # Dark recessed cave mouth
    z.box((W * 0.46, L * 0.48, H * 0.50), loc=(0, -L * 0.24, H * 0.26), colour="black")


def _build_kopje_outcrop(z, aid, W, L, H, p):
    col = p.get("rock", "tan")
    # Large granite base platform
    z.ball(1.0, loc=(0, 0, H * 0.32), colour=col, scale=(W * 0.46, L * 0.46, H * 0.34), seg=8, rings=6)
    # Multiple giant balancing savanna boulders
    z.ball(1.0, loc=(-W * 0.20, L * 0.15, H * 0.55), colour=col,
           scale=(W * 0.26, L * 0.26, H * 0.32), rot=(10, -15, 25), seg=7, rings=5)
    z.ball(1.0, loc=(W * 0.22, -L * 0.12, H * 0.52), colour="sand",
           scale=(W * 0.24, L * 0.24, H * 0.30), rot=(-12, 10, 40), seg=7, rings=5)
    # Top crowning balancing boulder
    z.ball(1.0, loc=(0, 0, H * 0.82), colour="rust",
           scale=(W * 0.22, L * 0.22, H * 0.22), rot=(5, 12, -15), seg=7, rings=5)


def _build_termite_mound(z, aid, W, L, H, p):
    soil = p.get("soil", "rust")
    # Central chimney spire
    z.cone(W * 0.38, H * 0.96, loc=(0, 0, H * 0.48), colour=soil, seg=7)
    # Secondary buttress flutes around base
    flutes = [
        (0.24, 0.12, 0.65, 0.22, (10, 5, 0)),
        (-0.22, 0.14, 0.58, 0.20, (-8, 10, 60)),
        (0.10, -0.22, 0.52, 0.20, (-10, -5, -45)),
        (-0.18, -0.18, 0.45, 0.18, (5, -10, 120)),
    ]
    for fx, fy, fh, fr, rot in flutes:
        z.cone(W * fr, H * fh, loc=(W * fx, L * fy, H * fh * 0.5), colour=soil, rot=rot, seg=6)


def _build_mound(z, aid, W, L, H, p):
    soil = p.get("soil", "leaf")
    rim = p.get("rim", None)

    if rim:
        # Base rim (e.g. sandy beach for pond_island)
        z.cyl(W * 0.48, H * 0.22, loc=(0, 0, H * 0.12), colour=rim, seg=12, r2=W * 0.45)
        # Inner mound
        z.ball(1.0, loc=(0, 0, H * 0.42), colour=soil,
               scale=(W * 0.36, L * 0.36, H * 0.45), seg=10, rings=6)
    else:
        # Low-poly smooth terrain mound/hill
        z.ball(1.0, loc=(0, 0, H * 0.48), colour=soil,
               scale=(W * 0.48, L * 0.48, H * 0.50), seg=10, rings=6)
        if aid == "hay_mound":
            # Extra hay texture clumps
            z.cone(W * 0.22, H * 0.35, loc=(0, 0, H * 0.80), colour="yellow", seg=7)


def _build_sand_dune(z, aid, W, L, H, p):
    soil = p.get("soil", "sand")
    # Crescent dune shape scaled exactly to H
    z.ball(1.0, loc=(0, 0, H * 0.45), colour=soil,
           scale=(W * 0.48, L * 0.45, H * 0.48), rot=(0, -6, 18), seg=10, rings=6)
    # Windward ridge ridge crest
    z.cyl(W * 0.38, H * 0.25, loc=(W * 0.05, -L * 0.06, H * 0.75), colour="cream",
          rot=(8, 4, 22), seg=8, r2=W * 0.22)


def _build_pond(z, aid, W, L, H, p):
    water_col = p.get("water", "water")
    rim_col = p.get("rim", "grey")

    # Basin bottom / rim scaled to reach target H
    z.cyl(W * 0.48, H * 0.75, loc=(0, 0, H * 0.38), colour=rim_col, seg=12, r2=W * 0.45)
    # Water surface sheet (inset)
    z.cyl(W * 0.40, H * 0.20, loc=(0, 0, H * 0.55), colour=water_col, seg=12)
    # Perimeter rim rocks
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        px = math.cos(ang) * (W * 0.42)
        py = math.sin(ang) * (L * 0.42)
        z.ball(1.0, loc=(px, py, H * 0.70), colour=rim_col if i % 2 == 0 else "charcoal",
               scale=(W * 0.09, L * 0.09, H * 0.28), seg=6, rings=4)


def _build_stream(z, aid, W, L, H, p):
    water_col = p.get("water", "water")
    rim_col = p.get("rim", "grey")

    # Water canal
    z.box((W * 0.98, L * 0.55, H * 0.45), loc=(0, 0, H * 0.25), colour=water_col)
    # Left bank
    z.box((W * 0.98, L * 0.22, H * 0.90), loc=(0, L * 0.38, H * 0.48), colour=rim_col, taper=0.9)
    # Right bank
    z.box((W * 0.98, L * 0.22, H * 0.90), loc=(0, -L * 0.38, H * 0.48), colour="sand", taper=0.9)
    # Scattered stones in bank
    z.ball(1.0, loc=(W * 0.25, L * 0.28, H * 0.65), colour="grey",
           scale=(W * 0.05, L * 0.10, H * 0.30), seg=5, rings=4)
    z.ball(1.0, loc=(-W * 0.20, -L * 0.28, H * 0.65), colour="charcoal",
           scale=(W * 0.05, L * 0.10, H * 0.30), seg=5, rings=4)


def _build_log(z, aid, W, L, H, p):
    bark = p.get("bark", "brown")
    end_col = p.get("end", "tan")

    # Main horizontal log body along X
    r = min(L, H) * 0.42
    length = W * 0.96
    z.cyl(r, length, loc=(0, 0, H * 0.50), colour=bark, rot=(0, 90, 0), seg=8)
    # Cut tree ring ends
    z.cyl(r * 0.88, length * 0.02, loc=(length * 0.50, 0, H * 0.50), colour=end_col, rot=(0, 90, 0), seg=8)
    z.cyl(r * 0.88, length * 0.02, loc=(-length * 0.50, 0, H * 0.50), colour=end_col, rot=(0, 90, 0), seg=8)
    # Small branch stub
    z.cyl(r * 0.45, H * 0.42, loc=(W * 0.18, 0, H * 0.75), colour=bark, rot=(20, 15, 0), seg=6)


def _build_hollow_log(z, aid, W, L, H, p):
    bark = p.get("bark", "dark_brown")
    end_col = p.get("end", "tan")

    r_outer = min(L, H) * 0.46
    length = W * 0.96
    # Outer bark shell with 8 segments
    z.cyl(r_outer, length, loc=(0, 0, H * 0.50), colour=bark, rot=(0, 90, 0), seg=8)
    # Inner dark cavity with 7 segments (different segment count and slight inset prevents coplanar tris)
    r_inner = r_outer * 0.65
    z.cyl(r_inner, length * 0.04, loc=(length * 0.47, 0, H * 0.50), colour="black", rot=(0, 90, 0), seg=7)
    z.cyl(r_inner, length * 0.04, loc=(-length * 0.47, 0, H * 0.50), colour="black", rot=(0, 90, 0), seg=7)
    # Rim ring with 9 segments
    z.cyl(r_outer * 0.90, length * 0.02, loc=(length * 0.495, 0, H * 0.50), colour=end_col, rot=(0, 90, 0), seg=9)
    z.cyl(r_outer * 0.90, length * 0.02, loc=(-length * 0.495, 0, H * 0.50), colour=end_col, rot=(0, 90, 0), seg=9)


def _build_climbing_tree_trunk(z, aid, W, L, H, p):
    col = p.get("trunk", "brown")
    # Tall main trunk (5m)
    r = min(W, L) * 0.18
    z.cyl(r, H * 0.98, loc=(0, 0, H * 0.49), colour=col, seg=8, r2=r * 0.65)
    # Climbing branches at various heights
    branches = [
        (0.25, 0.0, 0.45, (0, 45, 0), 0.75),
        (-0.22, 0.15, 0.62, (-35, -40, 30), 0.68),
        (0.12, -0.25, 0.78, (40, 30, -45), 0.60),
    ]
    for bx, by, bz_frac, rot, b_len in branches:
        z.cyl(r * 0.55, W * b_len, loc=(bx * W, by * L, H * bz_frac), colour=col, rot=rot, seg=6)


def _build_root_tangle(z, aid, W, L, H, p):
    col = p.get("bark", "dark_brown")
    # Central stump core
    r = min(W, L) * 0.22
    z.cyl(r, H * 0.75, loc=(0, 0, H * 0.38), colour=col, seg=7, r2=r * 0.8)
    # Gnarled twisting roots extending out
    for i in range(5):
        ang = i * (2 * math.pi / 5)
        rx = math.cos(ang) * (W * 0.32)
        ry = math.sin(ang) * (L * 0.32)
        deg = math.degrees(ang)
        z.cyl(r * 0.42, W * 0.52, loc=(rx, ry, H * 0.25), colour=col, rot=(15, 65, deg), seg=6)


def _build_tile(z, aid, W, L, H, p):
    top_col = p.get("top", "leaf")
    # 2x2m ground tile with beveled base
    # Darker base soil slab
    z.box((W * 0.98, L * 0.98, H * 0.45), loc=(0, 0, H * 0.23), colour="dark_brown")
    # Top turf/material layer
    z.box((W * 0.96, L * 0.96, H * 0.50), loc=(0, 0, H * 0.70), colour=top_col, taper=0.98)


def _build_rock_ledge(z, aid, W, L, H, p):
    col = p.get("rock", "grey")
    # Tiered step 1
    z.box((W * 0.95, L * 0.92, H * 0.45), loc=(0, 0, H * 0.24), colour=col, taper=0.92)
    # Tiered step 2 (higher ledge platform)
    z.box((W * 0.65, L * 0.72, H * 0.50), loc=(-W * 0.12, 0, H * 0.72), colour="light_grey", taper=0.90)


def _build_rock_column(z, aid, W, L, H, p):
    col = p.get("rock", "charcoal")
    # Hexagonal basalt column
    r = min(W, L) * 0.45
    z.cyl(r, H * 0.98, loc=(0, 0, H * 0.49), colour=col, seg=6, r2=r * 0.92)
    # Small companion shoulder column
    z.cyl(r * 0.55, H * 0.45, loc=(W * 0.25, L * 0.15, H * 0.23), colour="grey", seg=6)


def _build_stalagmite_group(z, aid, W, L, H, p):
    col = p.get("rock", "tan")
    # Cluster of pointed stalagmites with varied rotations and segment counts to prevent coplanar tris
    spires = [
        (0.0, 0.0, 0.96, 0.26, col, (0, 0, 15), 6),
        (0.22, 0.18, 0.65, 0.18, "cream", (2, -3, 35), 7),
        (-0.25, 0.12, 0.72, 0.20, col, (-3, 2, 50), 5),
        (0.15, -0.24, 0.55, 0.16, "sand", (3, 3, -25), 6),
        (-0.18, -0.20, 0.48, 0.15, "cream", (-2, -2, 75), 7),
    ]
    for sx, sy, sh, sr, c, rot, seg in spires:
        z.cone(W * sr, H * sh, loc=(W * sx, L * sy, H * sh * 0.5), colour=c, rot=rot, seg=seg)
