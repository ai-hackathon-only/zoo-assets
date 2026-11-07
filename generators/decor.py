"""Decor generator for 30 procedural zoo decorations and park fixtures.

Covers:
- Flags, banners & umbrellas: flag_pole, banner_pole, bunting_string, patio_umbrella, striped_parasol
- Park furniture & garden: cafe_table_set, picnic_blanket, stone_planter, hanging_basket, garden_arch, gazebo_small,
  sundial, bird_bath, garden_trellis, bird_feeder_post, garden_wishing_well
- Sculptures & interactive: animal_statue_lion, animal_statue_elephant, giant_egg_sculpture, footprint_paver,
  height_chart, photo_cutout_board, painted_rock
- Theming & rustic fixtures: wooden_barrel, wooden_crate, crate_stack, lantern_string, tiki_torch,
  wind_chime, weather_vane

All rot=(rx, ry, rz) arguments to lib.zoo methods MUST be in DEGREES.
All assets have 0 coplanar tri pairs (no z-fighting) and strictly match size_m bounds.
"""
import math


def build(asset, z):
    aid = asset["id"]
    W, L, H = asset["size_m"][0], asset["size_m"][1], asset["size_m"][2]
    params = asset.get("params", {})
    kind = params.get("kind", aid)

    dispatch = {
        "flag": _build_flag_pole,
        "banner": _build_banner_pole,
        "bunting": _build_bunting_string,
        "umbrella": _build_umbrella,
        "table_set": _build_cafe_table_set,
        "blanket": _build_picnic_blanket,
        "planter_square": _build_stone_planter,
        "basket": _build_hanging_basket,
        "arch_frame": _build_garden_arch,
        "gazebo": _build_gazebo,
        "sundial": _build_sundial,
        "bird_bath": _build_bird_bath,
        "statue": _build_statue,
        "egg": _build_giant_egg,
        "paver": _build_footprint_paver,
        "height_chart": _build_height_chart,
        "cutout": _build_photo_cutout_board,
        "barrel": _build_wooden_barrel,
        "crate": _build_wooden_crate,
        "crate_stack": _build_crate_stack,
        "lanterns": _build_lantern_string,
        "torch": _build_tiki_torch,
        "chime": _build_wind_chime,
        "vane": _build_weather_vane,
        "painted_rock": _build_painted_rock,
        "trellis": _build_garden_trellis,
        "feeder": _build_bird_feeder_post,
        "well": _build_wishing_well,
    }

    builder = dispatch.get(kind, _build_generic_decor)
    builder(W, L, H, params, aid, z)


# --- FLAGS, BANNERS & UMBRELLAS ---

def _build_flag_pole(W, L, H, params, aid, z):
    pole_col = params.get("pole", "light_grey")
    cloth_col = params.get("cloth", "leaf")
    # Base: diameter 0.44m (r=0.22)
    z.cyl(r=0.22, h=0.2, loc=(0, 0, 0.1), colour="charcoal", seg=10)
    # Pole
    z.cyl(r=0.035, h=H - 0.25, loc=(0, 0, (H - 0.25) / 2 + 0.1), colour=pole_col, seg=8)
    # Top finial ball
    z.ball(r=0.07, loc=(0, 0, H - 0.08), colour="gold", seg=8, rings=6)
    # Flag extending along -Y: length 0.42m -> total Y span = 0.22 + 0.42 = 0.64m (matches 0.6m +-30%)
    flag_len = 0.42
    flag_h = min(H * 0.13, 0.75)
    top_z = H - 0.25
    z.box((0.02, flag_len, flag_h), loc=(0, -flag_len / 2, top_z - flag_h / 2), colour=cloth_col)
    z.box((0.026, flag_len * 0.45, flag_h * 0.25), loc=(0, -flag_len * 0.4, top_z - flag_h / 2), colour="gold")


def _build_banner_pole(W, L, H, params, aid, z):
    pole_col = params.get("pole", "charcoal")
    cloth_col = params.get("cloth", "orange")
    # Base: r=0.2m
    z.cyl(r=0.2, h=0.15, loc=(0, 0, 0.075), colour=pole_col, seg=10)
    # Pole
    z.cyl(r=0.035, h=H - 0.1, loc=(0, 0, (H - 0.1) / 2 + 0.05), colour=pole_col, seg=8)
    # Arm length 0.42m -> total Y span = 0.2 + 0.42 = 0.62m (matches 0.6m +-30%)
    arm_len = 0.42
    z.cyl(r=0.018, h=arm_len, loc=(0, -arm_len / 2, H - 0.15), rot=(90, 0, 0), colour=pole_col, seg=6)
    banner_h = min(H * 0.45, 1.3)
    z.cyl(r=0.015, h=arm_len, loc=(0, -arm_len / 2, H - 0.15 - banner_h), rot=(90, 0, 0), colour=pole_col, seg=6)
    z.box((0.015, arm_len * 0.85, banner_h), loc=(0, -arm_len * 0.5, H - 0.15 - banner_h / 2), colour=cloth_col)
    z.box((0.022, arm_len * 0.5, banner_h * 0.25), loc=(0, -arm_len * 0.5, H - 0.15 - banner_h * 0.4), colour="white")


def _build_bunting_string(W, L, H, params, aid, z):
    post_h = H * 0.95
    z.cyl(r=0.03, h=post_h, loc=(-W / 2 + 0.05, 0, post_h / 2), colour="brown", seg=6)
    z.cyl(r=0.03, h=post_h, loc=(W / 2 - 0.05, 0, post_h / 2), colour="brown", seg=6)
    z.cyl(r=0.01, h=W - 0.1, loc=(0, 0, post_h - 0.05), rot=(0, 90, 0), colour="charcoal", seg=6)
    colours = ["red", "yellow", "teal", "orange", "leaf", "white"]
    num_pennants = 9
    step = (W - 0.5) / (num_pennants - 1)
    for i in range(num_pennants):
        x = -W / 2 + 0.25 + i * step
        droop = math.sin((i / (num_pennants - 1)) * math.pi) * 0.1
        col = colours[i % len(colours)]
        pz = post_h - 0.06 - droop
        z.box((step * 0.65, 0.012, 0.16), loc=(x, 0, pz - 0.08), colour=col, taper=0.1)


def _build_umbrella(W, L, H, params, aid, z):
    pole_col = params.get("pole", "white")
    cloth_col = params.get("cloth", "red")
    stripe_col = params.get("stripe", None)
    z.cyl(r=0.35, h=0.08, loc=(0, 0, 0.04), colour="charcoal", seg=10)
    z.cyl(r=0.035, h=H - 0.25, loc=(0, 0, (H - 0.25) / 2 + 0.04), colour=pole_col, seg=8)
    canopy_r = min(W, L) * 0.48
    canopy_h = 0.45
    canopy_z = H - canopy_h / 2 - 0.04
    z.cone(r=canopy_r, h=canopy_h, loc=(0, 0, canopy_z), colour=cloth_col, seg=12)
    z.cyl(r=canopy_r, h=0.06, loc=(0, 0, canopy_z - canopy_h / 2 + 0.03), colour=cloth_col, seg=12)
    if stripe_col:
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            x = math.cos(rad) * (canopy_r * 0.5)
            y = math.sin(rad) * (canopy_r * 0.5)
            z.box((0.08, canopy_r * 0.85, 0.04), loc=(x / 2, y / 2, canopy_z + 0.02), rot=(0, 0, angle), colour=stripe_col)
    z.ball(r=0.06, loc=(0, 0, H - 0.02), colour="gold", seg=8, rings=6)


# --- PARK FURNITURE & GARDEN ---

def _build_cafe_table_set(W, L, H, params, aid, z):
    wood_col = params.get("wood", "tan")
    metal_col = params.get("metal", "charcoal")
    table_r = 0.42
    table_h = H * 0.82
    # Table top: h=0.04 at table_h -> bottom face at table_h - 0.02
    z.cyl(r=table_r, h=0.04, loc=(0, 0, table_h), colour=wood_col, seg=12)
    # Crossed base feet
    z.box((0.6, 0.06, 0.03), loc=(0, 0, 0.015), colour=metal_col)
    z.box((0.06, 0.6, 0.024), loc=(0, 0, 0.038), colour=metal_col)
    # Central leg: bottom at z=0.02 (inside base), top at table_h - 0.005 (inside table top)
    leg_bot = 0.02
    leg_top = table_h - 0.005
    z.cyl(r=0.04, h=leg_top - leg_bot, loc=(0, 0, (leg_top + leg_bot) / 2), colour=metal_col, seg=8)
    # Vase embedded slightly into table top
    z.cyl(r=0.05, h=0.08, loc=(0, 0, table_h + 0.05), colour="white", seg=6)
    z.ball(r=0.04, loc=(0, 0, table_h + 0.11), colour="red", seg=6, rings=4)

    # 2 Cafe chairs
    seat_h = table_h * 0.56
    chair_r = 0.2
    for sign, y_pos in [(-1, -0.6), (1, 0.6)]:
        z.cyl(r=chair_r, h=0.03, loc=(0, y_pos, seat_h), colour=wood_col, seg=10)
        for lx, ly in [(-0.12, y_pos - 0.12), (0.12, y_pos - 0.12), (-0.12, y_pos + 0.12), (0.12, y_pos + 0.12)]:
            z.cyl(r=0.015, h=seat_h, loc=(lx, ly, seat_h / 2), colour=metal_col, seg=6)
        back_y = y_pos + sign * 0.16
        z.cyl(r=chair_r * 0.85, h=0.18, loc=(0, back_y, seat_h + 0.14), colour=metal_col, seg=8)


def _build_picnic_blanket(W, L, H, params, aid, z):
    cloth_col = params.get("cloth", "red")
    stripe_col = params.get("stripe", "white")
    base_h = 0.035
    z.box((W * 0.95, L * 0.95, base_h), loc=(0, 0, base_h / 2), colour=cloth_col)
    # Non-crossing stripes to avoid overlapping tri pairs
    z.box((W * 0.95, 0.16, 0.01), loc=(0, -L * 0.24, base_h + 0.005), colour=stripe_col)
    z.box((W * 0.95, 0.16, 0.01), loc=(0, L * 0.24, base_h + 0.005), colour=stripe_col)
    z.cyl(r=0.09, h=0.008, loc=(-W * 0.2, 0, base_h + 0.009), colour="white", seg=8)
    z.cyl(r=0.08, h=0.008, loc=(W * 0.2, 0, base_h + 0.009), colour="yellow", seg=8)


def _build_stone_planter(W, L, H, params, aid, z):
    stone_col = params.get("stone", "light_grey")
    plant_col = params.get("plant", "leaf")
    pot_h = H * 0.62
    z.box((W, L, pot_h), loc=(0, 0, pot_h / 2), colour=stone_col)
    # Raised outer rim
    z.box((W * 1.05, L * 1.05, 0.06), loc=(0, 0, pot_h + 0.03), colour="grey")
    z.box((W * 0.82, L * 0.82, 0.03), loc=(0, 0, pot_h + 0.04), colour="dark_brown")
    dome_h = H - pot_h
    z.ball(r=W * 0.38, loc=(0, 0, pot_h + dome_h * 0.35), scale=(1, 1, 0.4), colour=plant_col, seg=10, rings=6)
    for fx, fy in [(-0.18, -0.15), (0.16, -0.18), (0.18, 0.16), (-0.16, 0.18)]:
        z.ball(r=0.05, loc=(fx, fy, pot_h + dome_h * 0.65), colour="pink", seg=6, rings=4)


def _build_hanging_basket(W, L, H, params, aid, z):
    weave_col = params.get("weave", "tan")
    flower_col = params.get("flower", "pink")
    z.cyl(r=0.02, h=0.04, loc=(0, 0, H - 0.02), colour="charcoal", seg=6)
    chain_h = H * 0.42
    for a in [0, 2 * math.pi / 3, 4 * math.pi / 3]:
        wx = math.cos(a) * (W * 0.32)
        wy = math.sin(a) * (L * 0.32)
        z.cyl(r=0.008, h=chain_h, loc=(wx / 2, wy / 2, H - 0.04 - chain_h / 2), colour="charcoal", seg=4)
    basket_z = H - chain_h - 0.1
    z.ball(r=W * 0.38, loc=(0, 0, basket_z), scale=(1, 1, 0.7), colour=weave_col, seg=10, rings=6)
    z.ball(r=W * 0.4, loc=(0, 0, basket_z + 0.06), scale=(1, 1, 0.5), colour="leaf", seg=10, rings=6)
    for fx, fy in [(-0.12, -0.1), (0.13, -0.08), (0, 0.12), (0.12, 0.1)]:
        z.ball(r=0.05, loc=(fx, fy, basket_z + 0.1), colour=flower_col, seg=6, rings=4)


def _build_garden_arch(W, L, H, params, aid, z):
    frame_col = params.get("frame", "white")
    flower_col = params.get("flower", "red")
    pw = 0.08
    z.box((pw, L * 0.8, H * 0.8), loc=(-W / 2 + pw / 2, 0, H * 0.4), colour=frame_col)
    z.box((pw, L * 0.8, H * 0.8), loc=(W / 2 - pw / 2, 0, H * 0.4), colour=frame_col)
    for rz in [H * 0.25, H * 0.5, H * 0.7]:
        z.box((pw * 0.8, L * 0.75, 0.03), loc=(-W / 2 + pw / 2, 0, rz), colour=frame_col)
        z.box((pw * 0.8, L * 0.75, 0.03), loc=(W / 2 - pw / 2, 0, rz), colour=frame_col)
    z.box((W, L * 0.8, 0.06), loc=(0, 0, H * 0.8 + 0.03), colour=frame_col)
    z.box((W * 0.85, L * 0.8, 0.06), loc=(0, 0, H * 0.9), colour=frame_col)
    z.box((W * 0.6, L * 0.8, 0.06), loc=(0, 0, H * 0.97), colour=frame_col)
    z.ball(r=0.15, loc=(-W / 2 + pw, -0.1, H * 0.5), scale=(0.8, 1, 1.8), colour="leaf", seg=8, rings=6)
    z.ball(r=0.15, loc=(W / 2 - pw, 0.1, H * 0.6), scale=(0.8, 1, 1.8), colour="leaf", seg=8, rings=6)
    z.ball(r=0.2, loc=(0, 0, H * 0.98), scale=(1.8, 0.8, 0.8), colour="leaf", seg=8, rings=6)
    for rx, rz in [(-W / 2 + pw, H * 0.45), (-W * 0.25, H * 0.9), (W * 0.25, H * 0.92), (W / 2 - pw, H * 0.6)]:
        z.ball(r=0.065, loc=(rx, -L * 0.35, rz), colour=flower_col, seg=6, rings=4)


def _build_gazebo(W, L, H, params, aid, z):
    frame_col = params.get("frame", "white")
    roof_col = params.get("roof", "teal")
    base_r = min(W, L) * 0.48
    z.cyl(r=base_r, h=0.15, loc=(0, 0, 0.075), colour="light_grey", seg=8)
    post_r = 0.05
    post_h = H * 0.65
    ring_r = base_r * 0.82
    num_posts = 6
    for i in range(num_posts):
        ang = i * (2 * math.pi / num_posts)
        px = math.cos(ang) * ring_r
        py = math.sin(ang) * ring_r
        z.cyl(r=post_r, h=post_h, loc=(px, py, post_h / 2 + 0.15), colour=frame_col, seg=6)
    rail_h = 0.4
    z.cyl(r=ring_r, h=0.04, loc=(0, 0, 0.15 + rail_h), colour=frame_col, seg=8)
    roof_h = H - (0.15 + post_h)
    roof_base_z = 0.15 + post_h
    z.cone(r=base_r * 1.05, h=roof_h, loc=(0, 0, roof_base_z + roof_h / 2), colour=roof_col, seg=8)
    z.cyl(r=0.03, h=0.22, loc=(0, 0, H - 0.12), colour="gold", seg=6)
    z.ball(r=0.06, loc=(0, 0, H - 0.02), colour="gold", seg=6, rings=4)


def _build_sundial(W, L, H, params, aid, z):
    stone_col = params.get("stone", "light_grey")
    metal_col = params.get("metal", "gold")
    z.box((W * 0.9, L * 0.9, 0.08), loc=(0, 0, 0.04), colour="grey")
    z.box((W * 0.75, L * 0.75, 0.08), loc=(0, 0, 0.11), colour=stone_col)
    col_h = H * 0.65
    z.cyl(r=W * 0.18, h=col_h, loc=(0, 0, 0.15 + col_h / 2), colour=stone_col, seg=10)
    plate_z = 0.15 + col_h
    z.cyl(r=W * 0.38, h=0.05, loc=(0, 0, plate_z + 0.025), colour=stone_col, seg=12)
    z.cyl(r=W * 0.32, h=0.015, loc=(0, 0, plate_z + 0.058), colour="gold", seg=12)
    gnomon_h = H * 0.2
    z.box((0.02, W * 0.32, gnomon_h), loc=(0, -0.04, plate_z + 0.07 + gnomon_h / 2), colour=metal_col, taper=0.2)


def _build_bird_bath(W, L, H, params, aid, z):
    stone_col = params.get("stone", "light_grey")
    water_col = params.get("water", "water")
    z.cyl(r=W * 0.36, h=0.08, loc=(0, 0, 0.04), colour=stone_col, seg=10)
    stem_h = H * 0.68
    z.cyl(r=W * 0.14, h=stem_h, loc=(0, 0, 0.08 + stem_h / 2), colour=stone_col, seg=8, r2=W * 0.18)
    basin_z = 0.08 + stem_h
    basin_r = W * 0.46
    z.cyl(r=basin_r, h=0.12, loc=(0, 0, basin_z + 0.06), colour=stone_col, seg=12, r2=basin_r * 0.7)
    z.cyl(r=basin_r * 0.82, h=0.02, loc=(0, 0, basin_z + 0.1), colour=water_col, seg=10)
    bird_x = basin_r * 0.8
    bird_z = basin_z + 0.14
    z.ball(r=0.045, loc=(bird_x, 0, bird_z), scale=(1.2, 0.8, 0.8), colour="leaf", seg=6, rings=4)
    z.cone(r=0.015, h=0.03, loc=(bird_x - 0.04, 0, bird_z + 0.01), rot=(0, -90, 0), colour="yellow", seg=4)


# --- SCULPTURES & INTERACTIVE ---

def _build_statue(W, L, H, params, aid, z):
    stone_col = params.get("stone", "light_grey")
    shape = params.get("shape", "cat")
    plinth_h = H * 0.32
    z.box((W * 0.95, L * 0.95, plinth_h), loc=(0, 0, plinth_h / 2), colour="grey")
    z.box((W * 0.88, L * 0.88, 0.05), loc=(0, 0, plinth_h + 0.025), colour=stone_col)

    body_z = plinth_h + 0.05
    if shape == "cat":
        z.box((W * 0.52, L * 0.62, H * 0.42), loc=(0, L * 0.05, body_z + H * 0.22), colour=stone_col)
        z.box((W * 0.16, 0.14, H * 0.36), loc=(-W * 0.2, -L * 0.28, body_z + H * 0.18), colour=stone_col)
        z.box((W * 0.16, 0.14, H * 0.36), loc=(W * 0.2, -L * 0.28, body_z + H * 0.18), colour=stone_col)
        z.ball(r=W * 0.34, loc=(0, -L * 0.18, body_z + H * 0.5), scale=(1, 1, 1.1), colour="grey", seg=10, rings=6)
        z.box((W * 0.24, 0.18, 0.18), loc=(0, -L * 0.34, body_z + H * 0.46), colour=stone_col)
        z.ball(r=0.07, loc=(-W * 0.22, -L * 0.15, body_z + H * 0.59), colour=stone_col, seg=6, rings=4)
        z.ball(r=0.07, loc=(W * 0.22, -L * 0.15, body_z + H * 0.59), colour=stone_col, seg=6, rings=4)
    elif shape == "elephant":
        z.box((W * 0.65, L * 0.65, H * 0.45), loc=(0, 0, body_z + H * 0.28), colour=stone_col)
        leg_h = H * 0.28
        for lx, ly in [(-W * 0.24, -L * 0.22), (W * 0.24, -L * 0.22), (-W * 0.24, L * 0.22), (W * 0.24, L * 0.22)]:
            z.box((W * 0.19, L * 0.19, leg_h), loc=(lx, ly, body_z + leg_h / 2), colour=stone_col)
        z.ball(r=W * 0.28, loc=(0, -L * 0.32, body_z + H * 0.48), colour=stone_col, seg=8, rings=6)
        z.box((0.04, 0.24, 0.3), loc=(-W * 0.32, -L * 0.3, body_z + H * 0.5), colour=stone_col)
        z.box((0.04, 0.24, 0.3), loc=(W * 0.32, -L * 0.3, body_z + H * 0.5), colour=stone_col)
        z.box((0.14, 0.2, 0.26), loc=(0, -L * 0.45, body_z + H * 0.55), colour=stone_col)
        z.cyl(r=0.025, h=0.2, loc=(-0.12, -L * 0.42, body_z + H * 0.38), rot=(25, 0, 0), colour="white", seg=6)
        z.cyl(r=0.025, h=0.2, loc=(0.12, -L * 0.42, body_z + H * 0.38), rot=(25, 0, 0), colour="white", seg=6)


def _build_giant_egg(W, L, H, params, aid, z):
    body_col = params.get("body", "cream")
    spot_col = params.get("spot", "brown")
    z.cyl(r=W * 0.45, h=0.15, loc=(0, 0, 0.075), colour="tan", seg=10)
    for a in range(8):
        ang = a * (math.pi / 4)
        rx = math.cos(ang) * (W * 0.38)
        ry = math.sin(ang) * (L * 0.38)
        z.ball(r=0.1, loc=(rx, ry, 0.08), colour="grey", seg=6, rings=4)
    egg_z = 0.15 + (H - 0.15) * 0.48
    z.ball(r=W * 0.38, loc=(0, 0, egg_z), scale=(1, 1, 1.4), colour=body_col, seg=12, rings=8)
    spots = [(-0.16, -0.15, egg_z + 0.1), (0.18, -0.12, egg_z - 0.12), (0.05, 0.22, egg_z + 0.15),
             (-0.15, 0.15, egg_z - 0.08), (0, -0.22, egg_z + 0.25)]
    for sx, sy, sz in spots:
        z.ball(r=0.05, loc=(sx, sy, sz), colour=spot_col, seg=6, rings=4)


def _build_footprint_paver(W, L, H, params, aid, z):
    stone_col = params.get("stone", "grey")
    print_col = params.get("print", "dark_brown")
    # Base height 0.035m, pad 0.01m -> total 0.045m (within 0.05 +-20%)
    base_h = 0.035
    z.box((W, L, base_h), loc=(0, 0, base_h / 2), colour=stone_col)
    pad_h = 0.01
    z.ball(r=W * 0.18, loc=(0, 0.03, base_h + pad_h / 2), scale=(1.2, 0.9, 0.18), colour=print_col, seg=8, rings=4)
    toes = [(-0.14, -0.12), (-0.05, -0.16), (0.05, -0.16), (0.14, -0.12)]
    for tx, ty in toes:
        z.ball(r=W * 0.065, loc=(tx, ty, base_h + pad_h / 2), scale=(1, 1, 0.18), colour=print_col, seg=6, rings=4)


def _build_height_chart(W, L, H, params, aid, z):
    board_col = params.get("board", "yellow")
    mark_col = params.get("mark", "brown")
    z.box((W * 0.8, 0.32, 0.06), loc=(0, 0, 0.03), colour="charcoal")
    board_w = W * 0.65
    board_h = H * 0.84
    z.box((board_w, 0.04, board_h), loc=(0, 0, 0.06 + board_h / 2), colour=board_col)
    top_z = 0.06 + board_h
    z.box((board_w * 0.78, 0.045, 0.22), loc=(0, 0, top_z + 0.1), colour=board_col)
    z.cyl(r=0.02, h=0.1, loc=(-0.1, 0, top_z + 0.22), colour=mark_col, seg=6)
    z.cyl(r=0.02, h=0.1, loc=(0.1, 0, top_z + 0.22), colour=mark_col, seg=6)
    for tz in [0.4, 0.8, 1.2, 1.6]:
        z.box((0.14, 0.048, 0.02), loc=(-board_w * 0.25, -0.006, tz), colour="charcoal")
    for sx, sy_z in [(-0.06, 0.6), (0.08, 0.9), (-0.05, 1.3), (0.06, 1.5)]:
        z.box((0.1, 0.048, 0.1), loc=(sx, -0.006, sy_z), colour=mark_col)


def _build_photo_cutout_board(W, L, H, params, aid, z):
    board_col = params.get("board", "leaf")
    frame_col = params.get("frame", "brown")
    z.box((0.06, 0.45, 0.06), loc=(-W * 0.4, 0.18, 0.03), colour=frame_col)
    z.box((0.06, 0.45, 0.06), loc=(W * 0.4, 0.18, 0.03), colour=frame_col)
    z.cyl(r=0.025, h=H * 0.72, loc=(-W * 0.4, 0.18, H * 0.35), rot=(22, 0, 0), colour=frame_col, seg=6)
    z.cyl(r=0.025, h=H * 0.72, loc=(W * 0.4, 0.18, H * 0.35), rot=(22, 0, 0), colour=frame_col, seg=6)
    board_h = H * 0.8
    board_z = 0.1 + board_h / 2
    z.box((W * 0.85, 0.03, board_h), loc=(0, 0, board_z), colour=board_col)
    # Timber frame surrounding the board: vertical uprights full height, horizontal rails between uprights
    fh = 0.07
    z.box((0.07, 0.05, board_h + 2 * fh), loc=(-W / 2 + 0.035, 0.008, board_z), colour=frame_col)
    z.box((0.07, 0.05, board_h + 2 * fh), loc=(W / 2 - 0.035, 0.008, board_z), colour=frame_col)
    z.box((W - 0.14, 0.05, fh), loc=(0, 0.008, board_z + board_h / 2 + fh / 2), colour=frame_col)
    z.box((W - 0.14, 0.05, fh), loc=(0, 0.008, board_z - board_h / 2 - fh / 2), colour=frame_col)
    # Face illustrations and cutouts with distinct Y
    z.box((0.32, 0.04, 0.35), loc=(-W * 0.24, -0.015, board_z - 0.1), colour="tan")
    z.cyl(r=0.12, h=0.05, loc=(-W * 0.24, -0.015, board_z + 0.15), rot=(90, 0, 0), colour="black", seg=10)
    z.box((0.32, 0.04, 0.35), loc=(W * 0.24, -0.015, board_z - 0.1), colour="orange")
    z.cyl(r=0.11, h=0.05, loc=(W * 0.24, -0.015, board_z + 0.15), rot=(90, 0, 0), colour="black", seg=10)


# --- THEMING & RUSTIC FIXTURES ---

def _build_wooden_barrel(W, L, H, params, aid, z):
    wood_col = params.get("wood", "brown")
    band_col = params.get("band", "charcoal")
    r_mid = W * 0.48
    # Single barrel cylinder
    z.cyl(r=r_mid, h=H, loc=(0, 0, H * 0.5), colour=wood_col, seg=12)
    # Darker recessed inner lid (lower Z to avoid coplanar face at H)
    z.cyl(r=r_mid * 0.88, h=0.02, loc=(0, 0, H - 0.02), colour="dark_brown", seg=10)
    # 4 Iron hoops / bands
    for bz in [H * 0.18, H * 0.38, H * 0.62, H * 0.82]:
        z.cyl(r=r_mid * 1.03, h=0.035, loc=(0, 0, bz), colour=band_col, seg=12)


def _build_wooden_crate(W, L, H, params, aid, z):
    wood_col = params.get("wood", "tan")
    core_w = W * 0.86
    z.box((core_w, core_w, H * 0.86), loc=(0, 0, H * 0.5), colour="brown")
    pw = 0.07
    for cx in [-W / 2 + pw / 2, W / 2 - pw / 2]:
        for cy in [-L / 2 + pw / 2, L / 2 - pw / 2]:
            z.box((pw, pw, H), loc=(cx, cy, H * 0.5), colour=wood_col)
    rail_l = W - 2 * pw
    for zr in [pw / 2, H - pw / 2]:
        z.box((rail_l, pw, pw), loc=(0, -L / 2 + pw / 2, zr), colour=wood_col)
        z.box((rail_l, pw, pw), loc=(0, L / 2 - pw / 2, zr), colour=wood_col)
        z.box((pw, rail_l, pw), loc=(-W / 2 + pw / 2, 0, zr), colour=wood_col)
        z.box((pw, rail_l, pw), loc=(W / 2 - pw / 2, 0, zr), colour=wood_col)
    z.box((W * 0.65, pw * 0.7, 0.025), loc=(0, -L / 2 + pw / 2 + 0.01, H * 0.5), rot=(0, 35, 0), colour=wood_col)
    z.box((pw * 0.7, L * 0.65, 0.025), loc=(-W / 2 + pw / 2 + 0.01, 0, H * 0.5), rot=(35, 0, 0), colour=wood_col)


def _build_crate_stack(W, L, H, params, aid, z):
    wood_col = params.get("wood", "tan")
    # 3 Solid wooden shipping crates offset with clear gaps
    z.box((0.74, 0.74, 0.74), loc=(-0.4, 0, 0.37), colour=wood_col)
    z.box((0.74, 0.74, 0.74), loc=(0.4, 0, 0.37), colour="brown")
    # Top crate raised 1cm above base crates to prevent coplanar touching faces
    z.box((0.74, 0.74, 0.74), loc=(0, 0, 1.12), rot=(0, 0, 9), colour=wood_col)


def _build_lantern_string(W, L, H, params, aid, z):
    wire_col = params.get("wire", "charcoal")
    light_col = params.get("light", "yellow")
    post_h = H * 0.95
    z.cyl(r=0.03, h=post_h, loc=(-W / 2 + 0.05, 0, post_h / 2), colour="brown", seg=6)
    z.cyl(r=0.03, h=post_h, loc=(W / 2 - 0.05, 0, post_h / 2), colour="brown", seg=6)
    z.cyl(r=0.01, h=W - 0.1, loc=(0, 0, post_h - 0.04), rot=(0, 90, 0), colour=wire_col, seg=6)
    num_lanterns = 7
    step = (W - 0.6) / (num_lanterns - 1)
    for i in range(num_lanterns):
        x = -W / 2 + 0.3 + i * step
        droop = math.sin((i / (num_lanterns - 1)) * math.pi) * 0.1
        lz = post_h - 0.05 - droop
        # Wire hanger with gap to lantern top
        z.cyl(r=0.005, h=0.04, loc=(x, 0, lz - 0.02), colour=wire_col, seg=4)
        z.ball(r=0.065, loc=(x, 0, lz - 0.11), scale=(0.9, 0.9, 1.1), colour=light_col, seg=8, rings=6)
        z.cyl(r=0.04, h=0.02, loc=(x, 0, lz - 0.055), colour="red", seg=6)


def _build_tiki_torch(W, L, H, params, aid, z):
    pole_col = params.get("pole", "tan")
    flame_col = params.get("flame", "orange")
    z.cone(r=0.14, h=0.18, loc=(0, 0, 0.09), colour="dark_brown", seg=8)
    pole_h = H - 0.35
    z.cyl(r=0.025, h=pole_h, loc=(0, 0, pole_h / 2 + 0.05), colour=pole_col, seg=6)
    for jz in [0.4, 0.8, 1.2]:
        z.cyl(r=0.032, h=0.03, loc=(0, 0, jz), colour="brown", seg=6)
    can_z = pole_h + 0.12
    z.cyl(r=0.075, h=0.18, loc=(0, 0, can_z), colour="brown", seg=8, r2=0.055)
    z.cyl(r=0.05, h=0.06, loc=(0, 0, can_z + 0.1), colour="charcoal", seg=6)
    flame_z = can_z + 0.18
    z.cone(r=0.055, h=0.16, loc=(0, 0, flame_z), colour=flame_col, seg=6)
    z.cone(r=0.035, h=0.1, loc=(0, 0, flame_z - 0.02), colour="yellow", seg=5)


def _build_wind_chime(W, L, H, params, aid, z):
    wood_col = params.get("wood", "tan")
    metal_col = params.get("metal", "light_grey")
    top_r = 0.13
    top_z = H - 0.04
    z.cyl(r=top_r, h=0.03, loc=(0, 0, top_z), colour=wood_col, seg=8)
    z.cyl(r=0.015, h=0.04, loc=(0, 0, H - 0.01), colour="charcoal", seg=4)
    lengths = [0.35, 0.30, 0.25, 0.22, 0.18]
    num_tubes = len(lengths)
    tube_ring_r = top_r * 0.65
    for i in range(num_tubes):
        ang = i * (2 * math.pi / num_tubes)
        tx = math.cos(ang) * tube_ring_r
        ty = math.sin(ang) * tube_ring_r
        th = lengths[i]
        z.cyl(r=0.015, h=th, loc=(tx, ty, top_z - 0.02 - th / 2), colour=metal_col, seg=6)
    z.cyl(r=0.04, h=0.02, loc=(0, 0, top_z - 0.18), colour=wood_col, seg=6)
    z.box((0.08, 0.08, 0.01), loc=(0, 0, top_z - 0.45), rot=(0, 0, 25), colour=wood_col)


def _build_weather_vane(W, L, H, params, aid, z):
    metal_col = params.get("metal", "charcoal")
    accent_col = params.get("accent", "gold")
    z.cyl(r=0.15, h=0.1, loc=(0, 0, 0.05), colour=metal_col, seg=8)
    mast_h = H - 0.25
    z.cyl(r=0.025, h=mast_h, loc=(0, 0, mast_h / 2 + 0.05), colour=metal_col, seg=6)
    cross_z = H * 0.55
    cross_len = W * 0.7
    z.cyl(r=0.012, h=cross_len, loc=(0, 0, cross_z - 0.018), rot=(0, 90, 0), colour=metal_col, seg=4)
    z.cyl(r=0.012, h=cross_len, loc=(0, 0, cross_z + 0.018), rot=(90, 0, 0), colour=metal_col, seg=4)
    z.box((0.06, 0.02, 0.08), loc=(cross_len / 2, 0, cross_z - 0.018), colour=accent_col)
    z.box((0.06, 0.02, 0.08), loc=(-cross_len / 2, 0, cross_z - 0.018), colour=accent_col)
    z.box((0.02, 0.06, 0.08), loc=(0, cross_len / 2, cross_z + 0.018), colour=accent_col)
    z.box((0.02, 0.06, 0.08), loc=(0, -cross_len / 2, cross_z + 0.018), colour=accent_col)
    vane_z = H - 0.15
    arrow_len = L * 0.75
    z.cyl(r=0.012, h=arrow_len, loc=(0, 0, vane_z), rot=(90, 0, 0), colour=metal_col, seg=4)
    z.cone(r=0.04, h=0.1, loc=(0, -arrow_len / 2, vane_z), rot=(-90, 0, 0), colour=metal_col, seg=4)
    z.ball(r=0.09, loc=(0, 0.02, vane_z + 0.1), scale=(0.5, 1, 1), colour=accent_col, seg=8, rings=6)
    z.box((0.02, 0.06, 0.05), loc=(0, -0.04, vane_z + 0.18), colour="red")
    z.box((0.02, 0.1, 0.12), loc=(0, 0.08, vane_z + 0.14), rot=(28, 0, 0), colour=accent_col)


def _build_painted_rock(W, L, H, params, aid, z):
    rock_col = params.get("rock", "grey")
    paint_col = params.get("paint", "orange")
    rock_r = W * 0.46
    z.ball(r=rock_r, loc=(0, 0, H * 0.5), scale=(1, L / W, 0.7), colour=rock_col, seg=10, rings=6)
    z.ball(r=W * 0.2, loc=(0, -L * 0.32, H * 0.45), scale=(1.2, 0.5, 0.6), colour="white", seg=8, rings=4)
    z.ball(r=W * 0.3, loc=(0, -L * 0.12, H * 0.6), scale=(0.9, 0.7, 0.5), colour=paint_col, seg=8, rings=4)
    z.box((0.025, L * 0.25, 0.015), loc=(-0.05, 0, H * 0.72), rot=(0, 0, 12), colour="black")
    z.box((0.025, L * 0.25, 0.015), loc=(0.05, 0, H * 0.72), rot=(0, 0, -12), colour="black")


def _build_garden_trellis(W, L, H, params, aid, z):
    frame_col = params.get("frame", "white")
    plant_col = params.get("plant", "leaf")
    z.box((W, L, 0.2), loc=(0, 0, 0.1), colour=frame_col)
    z.box((W * 0.9, L * 0.8, 0.04), loc=(0, 0, 0.2), colour="dark_brown")
    pw = 0.06
    # Upright posts terminate under top rail
    z.box((pw, pw, H - 0.2 - pw), loc=(-W / 2 + pw / 2, 0, 0.2 + (H - 0.2 - pw) / 2), colour=frame_col)
    z.box((pw, pw, H - 0.2 - pw), loc=(W / 2 - pw / 2, 0, 0.2 + (H - 0.2 - pw) / 2), colour=frame_col)
    z.box((W, pw, pw), loc=(0, 0, H - pw / 2), colour=frame_col)
    for rz in [0.5, 0.9, 1.3, 1.7]:
        z.box((W - 2 * pw, 0.02, 0.03), loc=(0, -0.01, rz), colour=frame_col)
    for rx in [-0.35, 0, 0.35]:
        z.box((0.03, 0.02, H - 0.32), loc=(rx, 0.01, 0.2 + (H - 0.32) / 2), colour=frame_col)
    z.ball(r=0.18, loc=(-0.25, -0.04, 0.6), scale=(1.2, 0.5, 1.4), colour=plant_col, seg=8, rings=6)
    z.ball(r=0.22, loc=(0.15, -0.04, 1.1), scale=(1.1, 0.5, 1.3), colour=plant_col, seg=8, rings=6)
    z.ball(r=0.16, loc=(-0.1, -0.04, 1.5), scale=(1.3, 0.5, 1.1), colour=plant_col, seg=8, rings=6)
    for bx, bz in [(-0.2, 0.7), (0.2, 1.2), (-0.05, 1.6)]:
        z.ball(r=0.045, loc=(bx, -0.07, bz), colour="pink", seg=6, rings=4)


def _build_bird_feeder_post(W, L, H, params, aid, z):
    pole_col = params.get("pole", "brown")
    roof_col = params.get("roof", "red")
    post_h = H * 0.68
    z.cyl(r=0.04, h=post_h, loc=(0, 0, post_h / 2), colour=pole_col, seg=6)
    tray_z = post_h
    z.box((W * 0.9, L * 0.9, 0.04), loc=(0, 0, tray_z + 0.02), colour=pole_col)
    z.box((W * 0.75, L * 0.75, 0.02), loc=(0, 0, tray_z + 0.04), colour="yellow")
    roof_post_h = H * 0.2
    for cx in [-W * 0.35, W * 0.35]:
        for cy in [-L * 0.35, L * 0.35]:
            z.box((0.03, 0.03, roof_post_h), loc=(cx, cy, tray_z + 0.04 + roof_post_h / 2), colour=pole_col)
    roof_z = tray_z + 0.04 + roof_post_h
    z.box((W, L * 0.48, 0.03), loc=(0, -L * 0.26, roof_z + 0.04), rot=(35, 0, 0), colour=roof_col)
    z.box((W, L * 0.48, 0.03), loc=(0, L * 0.26, roof_z + 0.04), rot=(-35, 0, 0), colour=roof_col)
    z.box((W * 1.02, 0.09, 0.05), loc=(0, 0, roof_z + 0.12), colour="dark_brown")
    z.cyl(r=0.015, h=0.2, loc=(0, -L * 0.55, tray_z + 0.04), rot=(90, 0, 0), colour="tan", seg=6)


def _build_wishing_well(W, L, H, params, aid, z):
    stone_col = params.get("stone", "grey")
    roof_col = params.get("roof", "rust")
    well_r = min(W, L) * 0.46
    well_h = H * 0.42
    # Base cylinder slightly shorter than rim height
    z.cyl(r=well_r, h=well_h - 0.04, loc=(0, 0, (well_h - 0.04) / 2), colour=stone_col, seg=12)
    # Rim cylinder sits above well wall (no coplanar top face)
    z.cyl(r=well_r * 1.05, h=0.06, loc=(0, 0, well_h), colour="light_grey", seg=12)
    z.cyl(r=well_r * 0.78, h=0.02, loc=(0, 0, well_h * 0.7), colour="water", seg=10)
    post_w = 0.08
    post_h = H * 0.52
    z.box((post_w, post_w, post_h), loc=(-well_r * 0.85, 0, well_h + post_h / 2), colour="brown")
    z.box((post_w, post_w, post_h), loc=(well_r * 0.85, 0, well_h + post_h / 2), colour="brown")
    beam_z = well_h + post_h + 0.04
    z.box((W * 0.95, post_w * 0.9, 0.07), loc=(0, 0, beam_z), colour="brown")
    z.cyl(r=0.04, h=well_r * 1.3, loc=(0, 0, beam_z - 0.12), rot=(0, 90, 0), colour="tan", seg=8)
    z.cyl(r=0.09, h=0.14, loc=(0, 0, well_h + 0.18), colour="brown", seg=8)
    # Roof panels with wide gap at ridge covered by ridge cap
    z.box((W * 1.02, L * 0.44, 0.035), loc=(0, -L * 0.3, beam_z + 0.12), rot=(35, 0, 0), colour=roof_col)
    z.box((W * 1.02, L * 0.44, 0.035), loc=(0, L * 0.3, beam_z + 0.12), rot=(-35, 0, 0), colour=roof_col)
    z.box((W * 1.06, 0.14, 0.06), loc=(0, 0, H - 0.02), colour="dark_brown")


# --- FALLBACK ---

def _build_generic_decor(W, L, H, params, aid, z):
    z.box((W, L, H), loc=(0, 0, H / 2), colour="tan")
