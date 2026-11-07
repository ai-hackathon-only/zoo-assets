"""Facilities generator for zoo enclosures, buildings, kiosks, paths, gates, and water features.

All models adhere to:
- Real-world dimensions from asset size_m ([width x, length y, height z])
- Origin at floor center (handled by zoo.finish)
- Colors mapped to palette/palette.png via lib.zoo
- Low-poly toy-style aesthetic
- Clean non-overlapping surfaces without z-fighting
"""
import math


def build(asset, z):
    W, L, H = asset["size_m"][0], asset["size_m"][1], asset["size_m"][2]
    params = asset.get("params", {})
    family = params.get("family", "")
    variant = params.get("variant", "")
    aid = asset["id"]

    dispatch = {
        "fence_wood": _build_fence_wood,
        "fence_chainlink": _build_fence_chainlink,
        "fence_bamboo": _build_fence_bamboo,
        "fence_rope": _build_fence_rope,
        "wall_glass": _build_wall_glass,
        "wall_stone": _build_wall_stone,
        "moat": _build_moat,
        "gate": _build_gate,
        "shelter": _build_shelter,
        "pavilion": _build_pavilion,
        "canopy": _build_canopy,
        "building": _build_building,
        "kiosk": _build_kiosk,
        "path": _build_path,
        "bridge": _build_bridge,
        "water": _build_water,
        "water_feature": _build_water,
        "viewing": _build_viewing,
        "enclosure": _build_enclosure,
        "platform": _build_platform,
        "utility": _build_utility,
        "bench": _build_bench,
        "lamp": _build_lamp,
        "bin": _build_bin,
        "sign": _build_sign,
        "amenity": _build_amenity,
    }

    builder = dispatch.get(family, _build_generic_facility)
    builder(W, L, H, variant, aid, z)

    # Standardize exact metric modular bounds (multiples of 2m or 0.5m edge)
    import bpy
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    xs = [v.co.x for o in obs for v in o.data.vertices]
    ys = [v.co.y for o in obs for v in o.data.vertices]
    zs = [v.co.z for o in obs for v in o.data.vertices]
    if xs and ys and zs:
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        dx, dy, dz = max_x - min_x, max_y - min_y, max_z - min_z
        if dx > 0 and dy > 0 and dz > 0:
            scale_x = W / dx
            scale_y = L / dy
            scale_z = H / dz
            for o in obs:
                for v in o.data.vertices:
                    v.co.x = (v.co.x - (min_x + max_x) / 2) * scale_x
                    v.co.y = (v.co.y - (min_y + max_y) / 2) * scale_y
                    v.co.z = (v.co.z - min_z) * scale_z


# --- FENCES & WALLS ---

def _build_fence_wood(W, L, H, variant, aid, z):
    if variant == "post":
        pw = min(W, L) * 0.8
        z.box((pw, pw, H * 0.88), loc=(0, 0, H * 0.44), colour="brown")
        z.box((pw * 1.2, pw * 1.2, H * 0.14), loc=(0, 0, H * 0.93), colour="dark_brown", taper=0.6)
    elif variant == "corner":
        pw = 0.22
        # Corner post spanning outer bounds
        z.box((pw, pw, H * 0.92), loc=(-W * 0.45, -L * 0.45, H * 0.46), colour="dark_brown")
        z.box((pw * 1.2, pw * 1.2, H * 0.1), loc=(-W * 0.45, -L * 0.45, H * 0.95), colour="brown", taper=0.7)
        # End posts at (+X, -L*0.45) and (-W*0.45, +Y)
        z.box((pw, pw, H * 0.92), loc=(W * 0.45, -L * 0.45, H * 0.46), colour="dark_brown")
        z.box((pw, pw, H * 0.92), loc=(-W * 0.45, L * 0.45, H * 0.46), colour="dark_brown")
        # Rails in +X and +Y
        for rz in (H * 0.35, H * 0.75):
            z.box((W * 0.88, pw * 0.4, 0.09), loc=(0, -L * 0.45, rz), colour="brown")
            z.box((pw * 0.4, L * 0.88, 0.09), loc=(-W * 0.45, 0, rz), colour="brown")
    else:  # straight
        pw = 0.2
        for x in (-W * 0.45, 0, W * 0.45):
            z.box((pw, L * 0.8, H * 0.92), loc=(x, 0, H * 0.46), colour="dark_brown")
            z.box((pw * 1.2, L * 0.9, H * 0.1), loc=(x, 0, H * 0.95), colour="brown", taper=0.7)
        for rz in (H * 0.25, H * 0.55, H * 0.82):
            z.box((W * 0.98, L * 0.35, 0.09), loc=(0, 0, rz), colour="brown")
        slats = 7
        step = (W * 0.76) / (slats - 1)
        for i in range(slats):
            sx = -W * 0.38 + i * step
            if abs(sx) > pw * 0.8:
                z.box((W * 0.045, L * 0.22, H * 0.68), loc=(sx, 0, H * 0.5), colour="tan")


def _build_fence_chainlink(W, L, H, variant, aid, z):
    if variant == "post":
        pr = min(W, L) * 0.35
        z.box((W * 0.9, L * 0.9, H * 0.12), loc=(0, 0, H * 0.06), colour="grey")
        z.cyl(pr, H * 0.8, loc=(0, 0, H * 0.12 + H * 0.4), colour="charcoal", seg=8)
        z.ball(pr * 1.3, loc=(0, 0, H * 0.96), colour="light_grey", seg=8, rings=6)
    else:  # panel
        pr = 0.05
        z.cyl(pr, H * 0.98, loc=(-W * 0.46, 0, H * 0.49), colour="charcoal", seg=6)
        z.cyl(pr, H * 0.98, loc=(W * 0.46, 0, H * 0.49), colour="charcoal", seg=6)
        z.box((W * 0.96, pr * 1.5, pr * 1.4), loc=(0, 0, H * 0.95), colour="charcoal")
        z.box((W * 0.96, pr * 1.5, pr * 1.4), loc=(0, 0, H * 0.5), colour="charcoal")
        z.box((W * 0.96, pr * 1.5, pr * 1.4), loc=(0, 0, 0.1), colour="charcoal")
        z.box((W * 0.92, 0.02, H * 0.82), loc=(0, 0, H * 0.51), colour="light_grey")
        z.box((W * 0.95, 0.03, 0.03), loc=(0, 0, H * 0.51), rot=(0, -22, 0), colour="grey")


def _build_fence_bamboo(W, L, H, variant, aid, z):
    canes = 14
    step = (W * 0.92) / (canes - 1)
    br = 0.04
    for i in range(canes):
        bx = -W * 0.46 + i * step
        ch = H * (0.88 + 0.12 * math.sin(i * 1.5))
        col = "olive" if i % 3 == 0 else "lime" if i % 3 == 1 else "tan"
        z.cyl(br, ch, loc=(bx, 0, ch * 0.5), colour=col, seg=6)
    for hz in (H * 0.25, H * 0.55, H * 0.8):
        z.box((W * 0.98, br * 2.2, br * 1.5), loc=(0, 0, hz), colour="dark_brown")


def _build_fence_rope(W, L, H, variant, aid, z):
    posts = 3
    step = (W * 0.9) / (posts - 1)
    pr = 0.1
    for i in range(posts):
        px = -W * 0.45 + i * step
        z.cyl(pr, H * 0.88, loc=(px, 0, H * 0.44), colour="brown", seg=8)
        z.ball(pr * 1.25, loc=(px, 0, H * 0.93), colour="gold", seg=8, rings=5)
    for seg_idx in range(posts - 1):
        x1 = -W * 0.45 + seg_idx * step
        x2 = x1 + step
        z.box((step * 0.55, 0.04, 0.04), loc=(x1 + step * 0.25, 0, H * 0.72), rot=(0, 15, 0), colour="tan")
        z.box((step * 0.55, 0.04, 0.04), loc=(x2 - step * 0.25, 0, H * 0.72), rot=(0, -15, 0), colour="tan")


def _build_wall_glass(W, L, H, variant, aid, z):
    base_h = H * 0.25
    z.box((W, L, base_h), loc=(0, 0, base_h * 0.5), colour="grey")
    if variant == "curved":
        subsegs = 5
        arc_w = W * 0.95 / subsegs
        for i in range(subsegs):
            t = (i - (subsegs - 1) / 2) / ((subsegs - 1) / 2)
            y_off = (1 - t * t) * (L * 0.35)
            x_pos = t * (W * 0.4)
            rot_y = -t * 20
            z.box((arc_w * 1.05, 0.06, H * 0.68), loc=(x_pos, y_off, base_h + H * 0.35), rot=(0, 0, rot_y), colour="teal")
        z.box((W * 0.98, 0.12, 0.06), loc=(0, L * 0.15, H * 0.97), colour="charcoal")
    else:
        # Posts rest on top of base
        z.box((0.1, L * 0.65, H * 0.71), loc=(-W * 0.44, 0, base_h + H * 0.36), colour="charcoal")
        z.box((0.1, L * 0.65, H * 0.71), loc=(W * 0.44, 0, base_h + H * 0.36), colour="charcoal")
        z.box((W * 0.82, 0.06, H * 0.67), loc=(0, 0, base_h + H * 0.345), colour="teal")
        z.box((W * 0.98, 0.14, 0.06), loc=(0, 0, H * 0.97), colour="light_grey")


def _build_wall_stone(W, L, H, variant, aid, z):
    coping_h = 0.14
    wall_h = H - coping_h
    z.box((W * 0.95, L * 0.85, wall_h), loc=(0, 0, wall_h * 0.5), colour="grey")
    z.box((W * 0.99, L * 1.05, coping_h), loc=(0, 0, wall_h + coping_h * 0.5), colour="sand")
    if variant == "tall":
        z.box((0.45, L * 1.15, wall_h * 0.86), loc=(-W * 0.35, 0, 0.03 + wall_h * 0.43), colour="charcoal")
        z.box((0.45, L * 1.15, wall_h * 0.86), loc=(W * 0.35, 0, 0.03 + wall_h * 0.43), colour="charcoal")
    else:
        z.box((W * 0.25, L * 0.92, wall_h * 0.3), loc=(-W * 0.25, 0, wall_h * 0.35), colour="charcoal")
        z.box((W * 0.25, L * 0.92, wall_h * 0.3), loc=(W * 0.25, 0, wall_h * 0.65), colour="charcoal")


def _build_moat(W, L, H, variant, aid, z):
    z.box((W * 0.98, L * 0.95, H * 0.25), loc=(0, 0, H * 0.125), colour="sand")
    z.box((W * 0.94, L * 0.45, H * 0.18), loc=(0, 0.05, H * 0.24), colour="water")
    z.box((W * 0.96, L * 0.22, H * 0.7), loc=(0, -L * 0.36, H * 0.49), colour="grey")
    z.box((W * 0.98, 0.09, 0.09), loc=(0, -L * 0.36, H * 0.95), colour="charcoal")


# --- GATES & ACCESS ---

def _build_gate(W, L, H, variant, aid, z):
    if variant == "arch":
        pillar_w = W * 0.18
        pillar_l = L * 0.8
        z.box((pillar_w * 1.3, pillar_l * 1.3, 0.3), loc=(-W * 0.38, 0, 0.15), colour="grey")
        z.box((pillar_w * 1.3, pillar_l * 1.3, 0.3), loc=(W * 0.38, 0, 0.15), colour="grey")
        z.box((pillar_w, pillar_l, H * 0.68), loc=(-W * 0.38, 0, 0.3 + H * 0.34), colour="sand")
        z.box((pillar_w, pillar_l, H * 0.68), loc=(W * 0.38, 0, 0.3 + H * 0.34), colour="sand")
        z.box((pillar_w * 1.25, pillar_l * 1.25, H * 0.15), loc=(-W * 0.38, 0, H * 0.925), colour="forest", taper=0.6)
        z.box((pillar_w * 1.25, pillar_l * 1.25, H * 0.15), loc=(W * 0.38, 0, H * 0.925), colour="forest", taper=0.6)
        z.box((W * 0.68, L * 0.42, H * 0.22), loc=(0, 0, H * 0.75), colour="leaf")
        z.box((W * 0.42, L * 0.46, H * 0.12), loc=(0, 0, H * 0.88), colour="gold")
    elif variant == "turnstile" or variant == "turnstile_bank":
        units = 4 if variant == "turnstile_bank" else 1
        uw = W / units
        for u in range(units):
            ux = -W * 0.5 + uw * (u + 0.5)
            z.box((uw * 0.7, L * 0.7, H * 0.8), loc=(ux, 0, H * 0.4), colour="light_grey")
            z.cyl(0.06, 0.15, loc=(ux, L * 0.2, H * 0.75), rot=(45, 0, 0), colour="charcoal")
            for rot_deg in (0, 120, 240):
                z.box((0.03, 0.03, max(uw, L) * 0.65), loc=(ux, L * 0.28, H * 0.75), rot=(rot_deg, 45, 0), colour="light_grey")
        if variant == "turnstile_bank":
            z.box((W * 0.98, L * 0.92, 0.15), loc=(0, 0, H * 0.95), colour="navy")
            z.cyl(0.06, H * 0.92, loc=(-W * 0.46, -L * 0.4, H * 0.46), colour="charcoal", seg=6)
            z.cyl(0.06, H * 0.92, loc=(W * 0.46, -L * 0.4, H * 0.46), colour="charcoal", seg=6)
    elif variant == "ticket_barrier":
        cab_w = W * 0.25
        for x in (-W * 0.35, W * 0.35):
            z.box((cab_w, L * 0.85, H * 0.85), loc=(x, 0, H * 0.425), colour="light_grey")
            z.box((cab_w * 0.7, L * 0.4, 0.05), loc=(x, 0, H * 0.86), colour="teal")
        z.box((W * 0.35, 0.04, H * 0.35), loc=(0, 0, H * 0.55), colour="teal")
    elif variant == "keeper_slide":
        z.box((0.15, L * 0.8, H * 0.92), loc=(-W * 0.45, 0, H * 0.46), colour="charcoal")
        z.box((0.15, L * 0.8, H * 0.92), loc=(W * 0.45, 0, H * 0.46), colour="charcoal")
        z.box((W * 0.98, L * 0.6, 0.15), loc=(0, 0, H * 0.95), colour="charcoal")
        z.box((W * 0.85, 0.08, H * 0.85), loc=(W * 0.05, 0, H * 0.45), colour="light_grey")
        z.box((W * 0.82, 0.12, 0.08), loc=(W * 0.05, 0, H * 0.45), colour="charcoal")
    elif variant == "safari_airlock":
        z.box((W * 0.95, L * 0.95, 0.2), loc=(0, 0, 0.1), colour="grey")
        for x in (-W * 0.45, W * 0.45):
            for y in (-L * 0.45, L * 0.45):
                z.box((0.3, 0.3, H * 0.74), loc=(x, y, 0.2 + H * 0.37), colour="charcoal")
        z.box((W * 0.98, L * 0.98, 0.18), loc=(0, 0, H * 0.94), colour="charcoal")
        z.box((W * 0.78, 0.15, H * 0.7), loc=(0, -L * 0.45, 0.2 + H * 0.36), colour="rust")
        z.box((W * 0.78, 0.15, H * 0.7), loc=(0, L * 0.45, 0.2 + H * 0.36), colour="rust")
    else:
        post_w = 0.22
        z.box((post_w, L * 0.8, H * 0.95), loc=(-W * 0.45, 0, H * 0.475), colour="dark_brown")
        z.box((post_w, L * 0.8, H * 0.95), loc=(W * 0.45, 0, H * 0.475), colour="dark_brown")
        gw = W * 0.42 if variant == "paddock_double" else W * 0.8
        gh = H * 0.8
        for gx in ((-W * 0.22, W * 0.22) if variant == "paddock_double" else (0,)):
            z.box((gw * 0.95, 0.08, gh), loc=(gx, 0, gh * 0.5 + 0.1), colour="brown")
            z.box((gw * 0.9, 0.1, 0.08), loc=(gx, 0, gh * 0.5 + 0.1), rot=(0, 25, 0), colour="tan")


# --- BUILDINGS & SHELTERS ---

def _build_building(W, L, H, variant, aid, z):
    if variant == "aquarium_dome":
        z.cyl(min(W, L) * 0.48, H * 0.38, loc=(0, 0, H * 0.19), colour="sand", seg=12)
        z.ball(min(W, L) * 0.46, loc=(0, 0, H * 0.4), scale=(1, 1, 0.78), colour="teal", seg=12, rings=8)
        z.box((W * 0.32, L * 0.28, H * 0.38), loc=(0, -L * 0.43, H * 0.2), colour="sand")
        z.box((W * 0.2, 0.08, H * 0.26), loc=(0, -L * 0.54, 0.02 + H * 0.13), colour="navy")
        return
    elif variant == "aviary":
        z.cyl(min(W, L) * 0.48, H * 0.52, loc=(0, 0, H * 0.26), colour="charcoal", seg=12)
        z.ball(min(W, L) * 0.47, loc=(0, 0, H * 0.52), scale=(1, 1, 0.7), colour="forest", seg=12, rings=8)
        z.box((W * 0.25, L * 0.22, H * 0.38), loc=(0, -L * 0.45, H * 0.2), colour="charcoal")
        return
    elif variant == "greenhouse":
        # Butterfly hothouse: Victorian glasshouse with stone foundation, glass panels, clean white framing
        base_h = H * 0.2
        wall_h = H * 0.45
        roof_h = H * 0.35
        # Masonry foundation (widest base)
        z.box((W * 0.96, L * 0.96, base_h), loc=(0, 0, base_h * 0.5), colour="sand")
        # Glass wall structure (inset slightly from base)
        z.box((W * 0.88, L * 0.88, wall_h), loc=(0, 0, base_h + wall_h * 0.5), colour="sky")
        # White framing posts sunk into foundation to prevent coplanar z-fighting
        for x in (-W * 0.445, W * 0.445):
            for y in (-L * 0.445, L * 0.445):
                z.box((0.16, 0.16, wall_h + 0.1), loc=(x, y, base_h - 0.05 + (wall_h + 0.1) * 0.5), colour="white")
        # Glass pitched roof (inset from base, resting cleanly on walls)
        roof_z = base_h + wall_h
        z.box((W * 0.89, L * 0.89, roof_h), loc=(0, 0, roof_z + roof_h * 0.5), colour="sky", taper=0.35)
        # White roof ridge cap (rests cleanly on top)
        z.box((0.16, L * 0.91, 0.08), loc=(0, 0, roof_z + roof_h * 0.96), colour="white")
        # Double entrance door standing proud from front wall
        z.box((W * 0.24, 0.08, wall_h * 0.78), loc=(0, -L * 0.465, base_h + 0.03 + wall_h * 0.39), colour="white")
        z.box((W * 0.18, 0.12, wall_h * 0.70), loc=(0, -L * 0.465, base_h + 0.03 + wall_h * 0.39), colour="teal")
        return
    elif variant == "rock_cave":
        z.box((W * 0.95, L * 0.9, H * 0.85), loc=(0, 0, H * 0.425), colour="charcoal", taper=0.85)
        z.ball(W * 0.3, loc=(-W * 0.3, -L * 0.3, H * 0.4), scale=(1, 1.2, 0.9), colour="grey", seg=7, rings=5)
        z.ball(W * 0.3, loc=(W * 0.3, -L * 0.3, H * 0.4), scale=(1, 1.2, 0.9), colour="grey", seg=7, rings=5)
        z.box((W * 0.45, L * 0.25, H * 0.52), loc=(0, -L * 0.39, 0.02 + H * 0.26), colour="black")
        return

    # Specialized building variants
    if variant == "hay_barn":
        body_h = H * 0.65
        roof_h = H * 0.35
        # Red barn body
        z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour="rust")
        # Pitch barn roof
        z.box((W * 0.98, L * 0.98, roof_h), loc=(0, 0, body_h + roof_h * 0.5), colour="dark_brown", taper=0.3)
        # Double barn door with white frame and X-cross braces
        door_w, door_h = W * 0.4, body_h * 0.65
        z.box((door_w, 0.08, door_h), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), colour="dark_brown")
        z.box((door_w * 0.9, 0.1, 0.08), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), rot=(0, 30, 0), colour="white")
        z.box((door_w * 0.9, 0.1, 0.08), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), rot=(0, -30, 0), colour="white")
        # Upper hayloft opening with visible hay bale
        z.box((W * 0.25, 0.08, H * 0.18), loc=(0, -L * 0.455, body_h * 0.88), colour="dark_brown")
        z.box((W * 0.18, 0.12, H * 0.12), loc=(0, -L * 0.45, body_h * 0.86), colour="yellow")
        return

    elif variant == "reptile_house":
        body_h = H * 0.68
        roof_h = H * 0.32
        # Desert stone walls with dark jungle green roof
        z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour="tan")
        z.box((W * 0.98, L * 0.98, roof_h), loc=(0, 0, body_h + roof_h * 0.5), colour="forest", taper=0.4)
        # Entry door
        door_w, door_h = W * 0.24, body_h * 0.7
        z.box((door_w, 0.08, door_h), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), colour="dark_brown")
        # Prominent green canopy sign above entrance
        z.box((W * 0.45, 0.25, 0.12), loc=(0, -L * 0.46, body_h * 0.82), colour="leaf")
        # Large front terrarium viewing windows with sky glass
        z.box((W * 0.22, 0.06, body_h * 0.42), loc=(-W * 0.28, -L * 0.455, body_h * 0.5), colour="sky")
        z.box((W * 0.22, 0.06, body_h * 0.42), loc=(W * 0.28, -L * 0.455, body_h * 0.5), colour="sky")
        return

    elif variant == "restroom":
        body_h = H * 0.72
        roof_h = H * 0.28
        # Cream clean tile building with navy hip roof
        z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour="cream")
        z.box((W * 0.98, L * 0.98, roof_h), loc=(0, 0, body_h + roof_h * 0.5), colour="navy", taper=0.35)
        # Dual doors (men / women) side by side
        door_w, door_h = W * 0.22, body_h * 0.68
        z.box((door_w, 0.08, door_h), loc=(-W * 0.22, -L * 0.455, 0.03 + door_h * 0.5), colour="navy")
        z.box((door_w, 0.08, door_h), loc=(W * 0.22, -L * 0.455, 0.03 + door_h * 0.5), colour="navy")
        # Restroom sign markers above doors
        z.box((door_w * 0.6, 0.1, 0.12), loc=(-W * 0.22, -L * 0.455, body_h * 0.85), colour="sky")
        z.box((door_w * 0.6, 0.1, 0.12), loc=(W * 0.22, -L * 0.455, body_h * 0.85), colour="pink")
        # Rooftop ventilation pipe
        z.cyl(0.12, 0.45, loc=(W * 0.28, L * 0.2, H + 0.15), colour="charcoal", seg=6)
        return

    elif variant == "shed":
        # Keeper tool shed: rustic timber siding, single door with latch, side lean-to roof
        body_h = H * 0.72
        roof_h = H * 0.28
        z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour="brown")
        # Mono-pitch slanted shed roof
        z.box((W * 0.98, L * 1.02, 0.14), loc=(0, 0, body_h + 0.1), rot=(-12, 0, 0), colour="dark_brown")
        door_w, door_h = W * 0.35, body_h * 0.75
        z.box((door_w, 0.08, door_h), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), colour="dark_brown")
        z.box((0.08, 0.1, 0.12), loc=(door_w * 0.3, -L * 0.46, body_h * 0.45), colour="charcoal")
        # Side wall tool rack / broom handle
        z.cyl(0.04, body_h * 0.8, loc=(W * 0.465, 0, body_h * 0.5), rot=(0, 10, 0), colour="tan", seg=6)
        return

    elif variant == "quarantine":
        # Quarantine bay: reinforced concrete, security barred windows, heavy gate with hazard sign
        body_h = H * 0.72
        roof_h = H * 0.28
        z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour="light_grey")
        z.box((W * 0.98, L * 0.98, roof_h), loc=(0, 0, body_h + roof_h * 0.5), colour="charcoal", taper=0.5)
        # Heavy steel roll-up door
        door_w, door_h = W * 0.48, body_h * 0.72
        z.box((door_w, 0.08, door_h), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), colour="grey")
        # Yellow caution banner stripe above door
        z.box((door_w * 1.1, 0.1, 0.15), loc=(0, -L * 0.455, body_h * 0.84), colour="yellow")
        # Security slit windows
        z.box((W * 0.15, 0.06, 0.15), loc=(-W * 0.32, -L * 0.455, body_h * 0.65), colour="charcoal")
        z.box((W * 0.15, 0.06, 0.15), loc=(W * 0.32, -L * 0.455, body_h * 0.65), colour="charcoal")
        return

    elif variant == "staff_quarters":
        # Staff breakroom: warm modern clubhouse with covered entry porch and roof vent
        body_h = H * 0.72
        roof_h = H * 0.28
        z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour="tan")
        z.box((W * 0.98, L * 0.98, roof_h), loc=(0, 0, body_h + roof_h * 0.5), colour="forest", taper=0.35)
        # Entry door
        door_w, door_h = W * 0.25, body_h * 0.7
        z.box((door_w, 0.08, door_h), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), colour="dark_brown")
        # Covered entry porch awning
        z.box((door_w * 1.4, 0.45, 0.08), loc=(0, -L * 0.52, body_h * 0.8), colour="dark_brown")
        z.cyl(0.04, body_h * 0.78, loc=(-door_w * 0.65, -L * 0.55, body_h * 0.39), colour="dark_brown", seg=6)
        z.cyl(0.04, body_h * 0.78, loc=(door_w * 0.65, -L * 0.55, body_h * 0.39), colour="dark_brown", seg=6)
        # Windows
        z.box((W * 0.2, 0.06, body_h * 0.35), loc=(-W * 0.28, -L * 0.455, body_h * 0.55), colour="sky")
        z.box((W * 0.2, 0.06, body_h * 0.35), loc=(W * 0.28, -L * 0.455, body_h * 0.55), colour="sky")
        return

    # Fallback clinic / first aid / generic
    wall_col, roof_col = "white", "teal"
    body_h = H * 0.7
    roof_h = H * 0.3
    z.box((W * 0.9, L * 0.9, body_h), loc=(0, 0, body_h * 0.5), colour=wall_col)
    z.box((W * 0.98, L * 0.98, roof_h), loc=(0, 0, body_h + roof_h * 0.5), colour=roof_col, taper=0.4)
    door_w, door_h = W * 0.22, body_h * 0.72
    z.box((door_w, 0.08, door_h), loc=(0, -L * 0.455, 0.03 + door_h * 0.5), colour="dark_brown")
    z.box((W * 0.2, 0.06, body_h * 0.35), loc=(-W * 0.28, -L * 0.455, body_h * 0.55), colour="sky")
    z.box((W * 0.2, 0.06, body_h * 0.35), loc=(W * 0.28, -L * 0.455, body_h * 0.55), colour="sky")
    if variant in ("clinic", "first_aid"):
        z.box((0.4, 0.07, 0.15), loc=(0, -L * 0.46, body_h * 0.88), colour="red")
        z.box((0.15, 0.09, 0.4), loc=(0, -L * 0.46, body_h * 0.88), colour="red")


def _build_shelter(W, L, H, variant, aid, z):
    if variant == "timber_lean":
        for x in (-W * 0.42, W * 0.42):
            z.box((0.2, 0.2, H * 0.9), loc=(x, -L * 0.42, H * 0.45), colour="dark_brown")
            z.box((0.2, 0.2, H * 0.65), loc=(x, L * 0.42, H * 0.325), colour="dark_brown")
        z.box((W * 0.98, L * 1.05, 0.12), loc=(0, 0, H * 0.78), rot=(-14, 0, 0), colour="brown")
        z.box((W * 0.82, 0.08, H * 0.58), loc=(0, L * 0.4, 0.02 + H * 0.29), colour="tan")
        z.box((W * 0.6, L * 0.25, 0.38), loc=(0, L * 0.18, 0.02 + 0.19), colour="brown")
        z.box((W * 0.55, L * 0.2, 0.14), loc=(0, L * 0.18, 0.42), colour="yellow")
    else:  # night_brick
        z.box((W * 0.92, L * 0.92, H * 0.75), loc=(0, 0, H * 0.375), colour="rust")
        z.box((W * 0.98, L * 0.98, H * 0.18), loc=(0, 0, H * 0.88), colour="charcoal")
        z.box((W * 0.35, 0.1, H * 0.48), loc=(0, -L * 0.465, 0.03 + H * 0.24), colour="charcoal")


def _build_pavilion(W, L, H, variant, aid, z):
    deck_h = 0.3
    z.box((W * 0.95, L * 0.95, deck_h), loc=(0, 0, deck_h * 0.5), colour="brown")
    post_h = H * 0.6
    for x in (-W * 0.4, W * 0.4):
        for y in (-L * 0.4, L * 0.4):
            z.box((0.2, 0.2, post_h), loc=(x, y, deck_h + post_h * 0.5), colour="dark_brown")
    rf_h = H * 0.35
    z.box((W * 1.05, L * 1.05, rf_h), loc=(0, 0, H - rf_h * 0.5), colour="sand", taper=0.1)
    z.box((W * 0.86, 0.08, 0.68), loc=(0, -L * 0.42, deck_h + 0.02 + 0.34), colour="tan")
    z.box((W * 0.86, 0.08, 0.68), loc=(0, L * 0.42, deck_h + 0.02 + 0.34), colour="tan")


def _build_canopy(W, L, H, variant, aid, z):
    deck_w = W * 0.8
    deck_th = 0.15
    if variant == "ramp":
        z.box((deck_w, L * 0.95, deck_th), loc=(0, 0, H * 0.5), rot=(20, 0, 0), colour="brown")
        for y in (-L * 0.35, 0, L * 0.35):
            cur_h = H * (0.35 + 0.55 * (y / L + 0.5))
            for x in (-W * 0.35, W * 0.35):
                z.box((0.15, 0.15, cur_h), loc=(x, y, cur_h * 0.5), colour="dark_brown")
    else:
        walk_z = H * 0.75
        z.box((deck_w, L * 0.95, deck_th), loc=(0, 0, walk_z), colour="brown")
        for y in (-L * 0.38, L * 0.38):
            for x in (-W * 0.38, W * 0.38):
                z.box((0.2, 0.2, walk_z), loc=(x, y, walk_z * 0.5), colour="dark_brown")
            z.box((W * 0.75, 0.1, 0.1), loc=(0, y, walk_z * 0.45), colour="dark_brown")
        z.box((0.08, L * 0.95, 0.8), loc=(-deck_w * 0.45, 0, walk_z + 0.4), colour="tan")
        z.box((0.08, L * 0.95, 0.8), loc=(deck_w * 0.45, 0, walk_z + 0.4), colour="tan")


# --- KIOSKS & COMMERCIAL ---

def _build_kiosk(W, L, H, variant, aid, z):
    if variant == "cart":
        z.box((W * 0.75, L * 0.65, H * 0.45), loc=(0, 0, H * 0.35), colour="teal")
        for y in (-L * 0.35, L * 0.35):
            z.cyl(0.25, 0.08, loc=(-W * 0.25, y, 0.25), rot=(90, 0, 0), colour="charcoal", seg=8)
        z.box((W * 0.8, L * 0.7, 0.08), loc=(0, 0, H * 0.58), colour="white")
        z.box((0.3, 0.3, 0.4), loc=(W * 0.15, 0, H * 0.78), colour="red")
        z.cyl(0.03, H * 0.6, loc=(0, 0, H * 0.7), colour="light_grey", seg=6)
        z.cone(min(W, L) * 0.45, 0.25, loc=(0, 0, H * 0.9), colour="orange", seg=8)
        return

    theme_col = "orange" if variant == "ice_cream" else "rust" if variant == "snack" else "leaf" if variant == "info" else "navy"
    body_h = H * 0.65
    z.box((W * 0.85, L * 0.85, body_h), loc=(0, 0, body_h * 0.5), colour="cream")
    z.box((W * 0.55, 0.08, body_h * 0.35), loc=(0, -L * 0.435, body_h * 0.55), colour="cream", emissive=True)
    z.box((W * 0.6, 0.22, 0.08), loc=(0, -L * 0.45, body_h * 0.38), colour="dark_brown")
    rf_h = H * 0.28
    z.box((W * 0.98, L * 0.98, rf_h), loc=(0, 0, body_h + rf_h * 0.5), colour=theme_col, taper=0.5)
    if variant == "ice_cream":
        z.cone(0.18, 0.35, loc=(0, -L * 0.3, H * 0.95), rot=(180, 0, 0), colour="tan")
        z.ball(0.15, loc=(0, -L * 0.3, H * 0.98), colour="pink", seg=8, rings=6)
    elif variant == "info":
        z.box((0.35, 0.35, 0.35), loc=(0, 0, H * 0.95), colour="navy")
        z.box((0.1, 0.38, 0.25), loc=(0, 0, H * 0.95), colour="white")


# --- PATHS & BRIDGES ---

def _build_path(W, L, H, variant, aid, z):
    th = H
    pcol = "charcoal" if "asphalt" in variant else "grey" if variant == "cobblestone" else "sand" if variant == "gravel" else "brown"
    if "asphalt" in variant:
        curb_w = 0.15
        z.box((W * 0.9 - curb_w * 2, L * 0.98, th * 0.9), loc=(0, 0, th * 0.45), colour="charcoal")
        z.box((curb_w, L * 0.98, th), loc=(-W * 0.44, 0, th * 0.5), colour="light_grey")
        z.box((curb_w, L * 0.98, th), loc=(W * 0.44, 0, th * 0.5), colour="light_grey")
    elif variant == "boardwalk":
        z.box((0.15, L * 0.96, th * 0.5), loc=(-W * 0.35, 0, th * 0.25), colour="dark_brown")
        z.box((0.15, L * 0.96, th * 0.5), loc=(W * 0.35, 0, th * 0.25), colour="dark_brown")
        planks = 10
        plank_w = (L * 0.9) / planks
        for i in range(planks):
            py = -L * 0.45 + i * plank_w + plank_w * 0.5
            col = "tan" if i % 2 == 0 else "brown"
            z.box((W * 0.95, plank_w * 0.85, th * 0.5), loc=(0, py, th * 0.75), colour=col)
    else:
        z.box((W * 0.98, L * 0.98, th), loc=(0, 0, th * 0.5), colour=pcol)


def _build_bridge(W, L, H, variant, aid, z):
    if variant == "stone":
        z.box((W * 0.85, L * 0.9, H * 0.65), loc=(0, 0, H * 0.325), colour="grey")
        z.box((0.2, L * 0.98, H * 0.92), loc=(-W * 0.42, 0, 0.02 + H * 0.46), colour="sand")
        z.box((0.2, L * 0.98, H * 0.92), loc=(W * 0.42, 0, 0.02 + H * 0.46), colour="sand")
    else:  # timber
        z.box((W * 0.82, L * 0.95, 0.2), loc=(0, 0, H * 0.45), colour="brown")
        for x in (-W * 0.42, W * 0.42):
            z.box((0.08, L * 0.95, 0.08), loc=(x, 0, H * 0.95), colour="tan")
            z.box((0.08, L * 0.95, 0.08), loc=(x, 0, H * 0.65), colour="tan")
            for y in (-L * 0.4, -L * 0.15, L * 0.15, L * 0.4):
                z.box((0.11, 0.11, H * 0.94), loc=(x, y, H * 0.47), colour="dark_brown")


# --- WATER FEATURES ---

def _build_water(W, L, H, variant, aid, z):
    rim_col = "grey" if variant in ("penguin_pool", "fountain") else "sand" if variant in ("shallow_lagoon", "splash_pool") else "dark_brown"
    wat_col = "teal" if variant in ("penguin_pool", "splash_pool") else "sky" if variant == "fountain" else "olive" if variant == "swamp" else "water"

    if variant == "fountain":
        r_base = min(W, L) * 0.45
        z.cyl(r_base, H * 0.25, loc=(0, 0, H * 0.125), colour="sand", seg=12)
        z.cyl(r_base * 0.88, H * 0.18, loc=(0, 0, H * 0.2), colour="water", seg=12)
        z.cyl(r_base * 0.2, H * 0.5, loc=(0, 0, H * 0.45), colour="grey", seg=8)
        z.cyl(r_base * 0.5, 0.14, loc=(0, 0, H * 0.68), colour="sand", seg=10)
        z.ball(r_base * 0.15, loc=(0, 0, H * 0.93), colour="gold", seg=8, rings=6)
        return
    elif variant == "waterfall":
        z.box((W * 0.9, L * 0.7, H * 0.92), loc=(0, L * 0.1, H * 0.46), colour="grey", taper=0.7)
        z.box((W * 0.95, L * 0.4, H * 0.22), loc=(0, -L * 0.3, 0.03 + H * 0.11), colour="water")
        z.box((W * 0.5, 0.1, H * 0.6), loc=(0, -L * 0.15, H * 0.6), rot=(-15, 0, 0), colour="teal")
        return

    # Basin spans full H * 0.92
    z.box((W * 0.98, L * 0.98, H * 0.92), loc=(0, 0, H * 0.46), colour=rim_col)
    z.box((W * 0.86, L * 0.86, H * 0.82), loc=(0, 0, H * 0.5), colour=wat_col)


# --- VIEWING & ENCLOSURES ---

def _build_viewing(W, L, H, variant, aid, z):
    if variant == "sunshade":
        for x in (-W * 0.4, W * 0.4):
            for y in (-L * 0.4, L * 0.4):
                z.cyl(0.08, H * 0.85, loc=(x, y, H * 0.425), rot=(5 if x > 0 else -5, 5 if y > 0 else -5, 0), colour="dark_brown", seg=6)
        z.box((W * 0.9, L * 0.9, 0.08), loc=(0, 0, H * 0.88), rot=(5, 3, 0), colour="sand")
    elif variant == "tower":
        for x in (-W * 0.4, W * 0.4):
            for y in (-L * 0.4, L * 0.4):
                z.box((0.2, 0.2, H * 0.85), loc=(x, y, H * 0.425), colour="dark_brown")
        deck_z = H * 0.75
        z.box((W * 0.95, L * 0.95, 0.2), loc=(0, 0, deck_z), colour="brown")
        z.box((W * 0.95, 0.08, 0.8), loc=(0, -L * 0.45, deck_z + 0.4), colour="tan")
        z.box((W * 0.95, 0.08, 0.8), loc=(0, L * 0.45, deck_z + 0.4), colour="tan")
        z.box((0.08, L * 0.95, 0.8), loc=(-W * 0.45, 0, deck_z + 0.4), colour="tan")
        z.box((0.08, L * 0.95, 0.8), loc=(W * 0.45, 0, deck_z + 0.4), colour="tan")
        rf_h = H * 0.15
        z.box((W * 1.05, L * 1.05, rf_h), loc=(0, 0, H - rf_h * 0.5), colour="forest", taper=0.2)
    elif variant == "glass_deck":
        z.box((W * 0.95, L * 0.95, 0.25), loc=(0, 0, 0.125), colour="grey")
        z.box((W * 0.92, 0.06, H * 0.78), loc=(0, -L * 0.45, 0.25 + H * 0.39), colour="teal")
        z.box((0.06, L * 0.92, H * 0.78), loc=(-W * 0.45, 0, 0.25 + H * 0.39), colour="teal")
        z.box((0.06, L * 0.92, H * 0.78), loc=(W * 0.45, 0, 0.25 + H * 0.39), colour="teal")
        z.box((W * 0.95, 0.12, 0.06), loc=(0, -L * 0.45, H * 0.95), colour="light_grey")
    elif variant == "acrylic_dome":
        z.box((W * 0.95, L * 0.95, H * 0.25), loc=(0, 0, H * 0.125), colour="sand")
        z.ball(min(W, L) * 0.35, loc=(0, 0, H * 0.45), scale=(1, 1, 0.9), colour="teal", seg=10, rings=6)
    elif variant == "underwater_tunnel":
        z.box((W * 0.95, L * 0.95, 0.2), loc=(0, 0, 0.1), colour="grey")
        z.box((0.08, L * 0.95, H * 0.7), loc=(-W * 0.45, 0, 0.2 + H * 0.35), colour="teal")
        z.box((0.08, L * 0.95, H * 0.7), loc=(W * 0.45, 0, 0.2 + H * 0.35), colour="teal")
        z.box((W * 0.95, L * 0.95, 0.08), loc=(0, 0, H * 0.92), colour="teal")
    else:  # pergola
        for x in (-W * 0.42, W * 0.42):
            for y in (-L * 0.42, L * 0.42):
                z.box((0.18, 0.18, H * 0.9), loc=(x, y, H * 0.45), colour="dark_brown")
        rafters = 6
        step = (L * 0.9) / (rafters - 1)
        for i in range(rafters):
            ry = -L * 0.45 + i * step
            z.box((W * 1.05, 0.08, 0.12), loc=(0, ry, H * 0.94), colour="brown")


def _build_enclosure(W, L, H, variant, aid, z):
    if variant == "petting_pen":
        th = 0.12
        for x in (-W * 0.45, W * 0.45):
            for y in (-L * 0.45, L * 0.45):
                z.box((th * 1.6, th * 1.6, H * 0.98), loc=(x, y, H * 0.49), colour="dark_brown")
        # Rails stay 5cm above floor to avoid coplanar bottom
        z.box((W * 0.88, th, H * 0.75), loc=(0, -L * 0.45, 0.05 + H * 0.375), colour="brown")
        z.box((W * 0.88, th, H * 0.75), loc=(0, L * 0.45, 0.05 + H * 0.375), colour="brown")
        z.box((th, L * 0.88, H * 0.75), loc=(-W * 0.45, 0, 0.05 + H * 0.375), colour="brown")
        z.box((th, L * 0.88, H * 0.75), loc=(W * 0.45, 0, 0.05 + H * 0.375), colour="brown")
        z.box((W * 0.84, L * 0.84, 0.04), loc=(0, 0, 0.02), colour="cream")
    else:  # otter_holt
        z.box((W * 0.9, L * 0.85, H * 0.92), loc=(0, 0, H * 0.46), colour="grey", taper=0.8)
        z.box((W * 0.35, L * 0.35, H * 0.38), loc=(0, -L * 0.32, 0.03 + H * 0.19), colour="black")


def _build_platform(W, L, H, variant, aid, z):
    deck_z = H * 0.65
    z.box((W * 0.9, L * 0.9, 0.2), loc=(0, 0, deck_z), colour="brown")
    for x in (-W * 0.4, W * 0.4):
        for y in (-L * 0.4, L * 0.4):
            z.box((0.2, 0.2, deck_z), loc=(x, y, deck_z * 0.5), colour="dark_brown")
    z.box((W * 0.4, 0.3, 0.4), loc=(0, -L * 0.42, H * 0.85), colour="tan")
    z.box((W * 0.35, 0.25, 0.2), loc=(0, -L * 0.42, H * 0.92), colour="leaf")


def _build_utility(W, L, H, variant, aid, z):
    z.box((W * 0.95, L * 0.95, 0.15), loc=(0, 0, 0.075), colour="grey")
    z.box((W * 0.95, 0.15, H * 0.8), loc=(0, L * 0.4, 0.15 + H * 0.4), colour="charcoal")
    bay_w = W * 0.3
    for x in (-W * 0.45, -W * 0.15, W * 0.15, W * 0.45):
        z.box((0.12, L * 0.72, H * 0.75), loc=(x, -0.04, 0.15 + H * 0.375), colour="charcoal")
    z.box((bay_w * 0.78, L * 0.52, H * 0.42), loc=(-W * 0.3, -0.06, 0.15 + H * 0.21), colour="dark_brown", taper=0.7)
    z.box((bay_w * 0.78, L * 0.52, H * 0.32), loc=(0, -0.06, 0.15 + H * 0.16), colour="olive", taper=0.7)


def _build_generic_facility(W, L, H, variant, aid, z):
    z.box((W * 0.9, L * 0.9, H * 0.8), loc=(0, 0, H * 0.4), colour="tan")
    z.box((W * 0.95, L * 0.95, H * 0.2), loc=(0, 0, H * 0.9), colour="rust", taper=0.7)


# --- BENCHES, LAMPS, BINS, SIGNS & AMENITIES ---

def _build_bench(W, L, H, variant, aid, z):
    if variant == "wood_classic":
        leg_w, leg_t = 0.05, 0.04
        seat_z = H * 0.46
        for x in (-W * 0.44, W * 0.44):
            # Front and back legs
            z.box((leg_w, leg_t, seat_z), loc=(x, -L * 0.35, seat_z * 0.5), colour="charcoal")
            z.box((leg_w, leg_t, H * 0.94), loc=(x, L * 0.35, H * 0.47), colour="charcoal")
            # Armrest rail slightly narrower (0.042) to avoid coplanar side faces with legs
            z.box((0.042, L * 0.72, 0.035), loc=(x, 0, seat_z * 1.35), colour="charcoal")
        # Wooden slats for seat sitting on top of seat height
        slat_t = 0.028
        for sy in (-L * 0.25, 0, L * 0.25):
            z.box((W * 0.96, L * 0.2, slat_t), loc=(0, sy, seat_z + slat_t * 0.5), colour="brown")
        # Wooden slats for backrest forward of rear leg
        for bz in (H * 0.66, H * 0.84):
            z.box((W * 0.96, slat_t, H * 0.15), loc=(0, L * 0.35 - leg_t * 0.5 - slat_t * 0.5, bz), colour="brown")

    elif variant == "cast_iron":
        seat_z = H * 0.44
        for x in (-W * 0.45, W * 0.45):
            z.box((0.05, 0.05, seat_z), loc=(x, -L * 0.38, seat_z * 0.5), colour="forest")
            z.box((0.05, 0.05, H * 0.94), loc=(x, L * 0.38, H * 0.47), colour="forest")
            # Armrest slightly wider (0.062) to prevent any coplanar side faces
            z.box((0.062, L * 0.78, 0.04), loc=(x, 0, seat_z * 1.3), colour="forest")
            # Diagonal brace with distinct thickness
            z.box((0.038, 0.038, seat_z * 0.75), loc=(x, 0, seat_z * 0.5), rot=(22, 0, 0), colour="forest")
        # Dark brown wooden slats
        slat_t = 0.024
        for sy in (-L * 0.27, -L * 0.09, L * 0.09, L * 0.27):
            z.box((W * 0.96, L * 0.14, slat_t), loc=(0, sy, seat_z + slat_t * 0.5), colour="dark_brown")
        for bz in (H * 0.64, H * 0.82):
            z.box((W * 0.96, slat_t, H * 0.14), loc=(0, L * 0.38 - 0.035, bz), colour="dark_brown")

    elif variant == "concrete_modern":
        z.box((W * 0.92, L * 0.88, H * 0.75), loc=(0, 0, H * 0.375), colour="light_grey", taper=0.92)
        z.box((W * 0.78, L * 0.72, H * 0.22), loc=(0, 0, H * 0.75 + H * 0.11), colour="tan")

    elif variant == "rustic_log":
        stump_r = min(L * 0.45, 0.22)
        stump_h = H * 0.65
        z.cyl(stump_r, stump_h, loc=(-W * 0.35, 0, stump_h * 0.5), colour="dark_brown", seg=8)
        z.cyl(stump_r, stump_h, loc=(W * 0.35, 0, stump_h * 0.5), colour="dark_brown", seg=8)
        z.box((W * 0.98, L * 0.88, H * 0.32), loc=(0, 0, stump_h + H * 0.16), colour="brown", taper=0.9)

    elif variant == "picnic_combo":
        tbl_z = H * 0.92
        bench_z = H * 0.52
        z.box((W * 0.96, L * 0.46, 0.06), loc=(0, 0, tbl_z), colour="brown")
        z.box((W * 0.96, L * 0.22, 0.05), loc=(0, -L * 0.38, bench_z), colour="brown")
        z.box((W * 0.96, L * 0.22, 0.05), loc=(0, L * 0.38, bench_z), colour="brown")
        for x in (-W * 0.38, W * 0.38):
            z.box((0.08, L * 0.92, 0.08), loc=(x, 0, bench_z - 0.04), colour="dark_brown")
            z.box((0.08, 0.1, tbl_z), loc=(x, 0, tbl_z * 0.5), colour="dark_brown")


def _build_lamp(W, L, H, variant, aid, z):
    if variant == "victorian_single":
        base_h = H * 0.12
        z.box((W * 0.8, L * 0.8, base_h), loc=(0, 0, base_h * 0.5), colour="charcoal", taper=0.7)
        post_h = H * 0.68
        z.cyl(0.06, post_h, loc=(0, 0, base_h + post_h * 0.5), colour="charcoal", seg=8)
        z.cyl(0.025, W * 0.6, loc=(0, 0, base_h + post_h * 0.9), rot=(0, 90, 0), colour="charcoal", seg=6)
        lantern_z = base_h + post_h + H * 0.09
        z.box((W * 0.6, L * 0.6, H * 0.16), loc=(0, 0, lantern_z), colour="yellow", taper=0.8, emissive=True)
        z.cone(W * 0.45, H * 0.06, loc=(0, 0, lantern_z + H * 0.11), colour="charcoal", seg=8)
        z.ball(0.03, loc=(0, 0, lantern_z + H * 0.15), colour="gold", seg=6, rings=4)

    elif variant == "victorian_double":
        base_h = H * 0.1
        z.box((W * 0.45, L * 0.8, base_h), loc=(0, 0, base_h * 0.5), colour="charcoal", taper=0.7)
        post_h = H * 0.72
        z.cyl(0.07, post_h, loc=(0, 0, base_h + post_h * 0.5), colour="charcoal", seg=8)
        arm_z = base_h + post_h
        z.box((W * 0.88, 0.06, 0.06), loc=(0, 0, arm_z), colour="charcoal")
        for x in (-W * 0.38, W * 0.38):
            z.box((0.26, 0.26, H * 0.09), loc=(x, 0, arm_z + H * 0.05), colour="yellow", taper=0.8, emissive=True)
            z.cone(0.18, H * 0.05, loc=(x, 0, arm_z + H * 0.12), colour="charcoal", seg=8)
            z.ball(0.025, loc=(x, 0, arm_z + H * 0.15), colour="gold", seg=6, rings=4)

    elif variant == "modern_led":
        z.box((W * 0.7, L * 0.7, H * 0.92), loc=(0, 0, H * 0.46), colour="charcoal")
        z.box((W * 0.72, L * 0.95, H * 0.08), loc=(0, L * 0.12, H * 0.96), colour="charcoal")
        z.box((W * 0.58, L * 0.42, 0.02), loc=(0, L * 0.25, H * 0.91), colour="yellow", emissive=True)

    elif variant == "solar_bollard":
        post_r = min(W, L) * 0.4
        z.cyl(post_r, H * 0.78, loc=(0, 0, H * 0.39), colour="light_grey", seg=12)
        z.cyl(post_r * 0.95, H * 0.12, loc=(0, 0, H * 0.84), colour="yellow", seg=12, emissive=True)
        z.cyl(post_r * 1.05, H * 0.04, loc=(0, 0, H * 0.92), colour="charcoal", seg=12)
        z.cyl(post_r * 0.8, 0.01, loc=(0, 0, H * 0.95), colour="navy", seg=12)


def _build_bin(W, L, H, variant, aid, z):
    if variant == "timber_slat":
        can_r = min(W, L) * 0.42
        z.cyl(can_r * 0.9, H * 0.75, loc=(0, 0, H * 0.375), colour="charcoal", seg=10)
        num_slats = 10
        slat_w = (can_r * 2 * math.pi / num_slats) * 0.7
        for i in range(num_slats):
            ang = 2 * math.pi * i / num_slats
            x = (can_r * 0.98) * math.cos(ang)
            y = (can_r * 0.98) * math.sin(ang)
            z.box((slat_w, 0.03, H * 0.72), loc=(x, y, H * 0.38), rot=(0, 0, math.degrees(ang) + 90), colour="brown")
        z.cyl(can_r * 1.04, H * 0.06, loc=(0, 0, H * 0.78), colour="charcoal", seg=12)
        z.ball(can_r * 0.95, loc=(0, 0, H * 0.82), scale=(1, 1, 0.6), colour="dark_brown", seg=10, rings=6)

    elif variant == "recycle_dual":
        z.box((W * 0.92, L * 0.9, H * 0.78), loc=(0, 0, H * 0.39), colour="light_grey")
        lid_w = W * 0.43
        z.box((lid_w, L * 0.86, H * 0.16), loc=(-W * 0.23, 0, H * 0.86), colour="teal", taper=0.85)
        z.box((lid_w, L * 0.86, H * 0.16), loc=(W * 0.23, 0, H * 0.86), colour="leaf", taper=0.85)
        z.box((lid_w * 0.6, L * 0.35, 0.02), loc=(-W * 0.23, 0, H * 0.95), colour="charcoal")
        z.box((lid_w * 0.6, L * 0.35, 0.02), loc=(W * 0.23, 0, H * 0.95), colour="charcoal")

    elif variant == "solar_compactor":
        z.box((W * 0.9, L * 0.9, H * 0.86), loc=(0, 0, H * 0.43), colour="teal")
        z.box((W * 0.55, 0.08, H * 0.22), loc=(0, -L * 0.46, H * 0.58), colour="light_grey")
        z.box((W * 0.45, 0.05, 0.04), loc=(0, -L * 0.51, H * 0.62), colour="charcoal")
        z.box((W * 0.92, L * 0.92, H * 0.08), loc=(0, 0, H * 0.9), colour="charcoal")
        z.box((W * 0.75, L * 0.75, 0.02), loc=(0, 0, H * 0.95), colour="navy")
        z.box((0.05, 0.02, 0.05), loc=(W * 0.32, -L * 0.46, H * 0.78), colour="leaf")

    elif variant == "animal_proof":
        base_h = 0.06
        # Base plate sits on floor
        z.box((W * 0.98, L * 0.98, base_h), loc=(0, 0, base_h * 0.5), colour="charcoal")
        # Body sits ON the base plate
        body_h = H * 0.74
        z.box((W * 0.92, L * 0.92, body_h), loc=(0, 0, base_h + body_h * 0.5), colour="forest")
        # Slanted latch hood top
        z.box((W * 0.88, L * 0.88, H * 0.16), loc=(0, 0, base_h + body_h + H * 0.08), colour="charcoal", taper=0.75)
        # Heavy front latch bar
        z.box((0.12, 0.06, 0.14), loc=(0, -L * 0.47, base_h + body_h), colour="rust")


def _build_sign(W, L, H, variant, aid, z):
    if variant == "fingerpost":
        post_r = 0.06
        z.cyl(post_r, H * 0.92, loc=(0, 0, H * 0.46), colour="dark_brown", seg=8)
        z.cone(post_r * 1.3, H * 0.07, loc=(0, 0, H * 0.95), colour="brown", seg=8)
        blade_defs = [
            (0, H * 0.82, "cream", 0.45),
            (90, H * 0.72, "tan", 0.45),
            (180, H * 0.62, "forest", 0.45),
            (270, H * 0.52, "navy", 0.45),
        ]
        for ang, hz, col, length in blade_defs:
            rad = math.radians(ang)
            dx = math.cos(rad) * (length * 0.5)
            dy = math.sin(rad) * (length * 0.5)
            z.box((length, 0.03, 0.12), loc=(dx, dy, hz), rot=(0, 0, ang), colour=col)

    elif variant == "map_board":
        post_t = 0.12
        for x in (-W * 0.42, W * 0.42):
            z.box((post_t, post_t, H * 0.95), loc=(x, 0, H * 0.475), colour="dark_brown")
        # Wooden backing board
        z.box((W * 0.78, 0.08, H * 0.58), loc=(0, 0, H * 0.55), colour="cream")
        # Map inset panel in front
        z.box((W * 0.7, 0.02, H * 0.48), loc=(0, -0.05, H * 0.55), colour="sky")
        z.box((W * 0.35, 0.02, H * 0.28), loc=(-W * 0.1, -0.065, H * 0.54), colour="leaf")
        # Protective pitched roof header
        z.box((W * 0.96, L * 0.88, 0.06), loc=(0, 0, H * 0.96), colour="brown", rot=(10, 0, 0))

    elif variant == "info_lectern":
        base_h = 0.04
        # Base plate on the floor
        z.box((W * 0.6, L * 0.6, base_h), loc=(0, 0, base_h * 0.5), colour="charcoal")
        # Pedestal post starts on top of base plate
        ped_z = H * 0.68
        ped_h = ped_z - base_h
        z.box((0.14, 0.14, ped_h), loc=(0, 0, base_h + ped_h * 0.5), colour="charcoal")
        # Angled lectern plaque
        ang = 35
        rad = math.radians(ang)
        plaque_z = ped_z + H * 0.14
        z.box((W * 0.88, L * 0.78, 0.04), loc=(0, 0, plaque_z), rot=(ang, 0, 0), colour="cream")
        ny, nz = -math.sin(rad), math.cos(rad)
        step = 0.025
        z.box((W * 0.72, L * 0.62, 0.015), loc=(0, step * ny, plaque_z + step * nz), rot=(ang, 0, 0), colour="teal")

    elif variant == "caution_a_frame":
        frame_t = 0.03
        panel_h = H * 0.92
        ang = 18
        rad = math.radians(ang)
        # Left and right slanted panels
        z.box((W * 0.88, frame_t, panel_h), loc=(0, -L * 0.22, panel_h * 0.48), rot=(ang, 0, 0), colour="yellow")
        z.box((W * 0.88, frame_t, panel_h), loc=(0, L * 0.22, panel_h * 0.48), rot=(-ang, 0, 0), colour="yellow")
        # Warning stripe stepped forward along front face normal: normal=(0, -sin(ang), cos(ang))
        ny, nz = -math.sin(rad), math.cos(rad)
        step = 0.02
        z.box((W * 0.74, 0.01, panel_h * 0.22), loc=(0, -L * 0.22 + step * ny, panel_h * 0.46 + step * nz), rot=(ang, 0, 0), colour="black")
        z.box((W * 0.25, 0.015, panel_h * 0.18), loc=(0, -L * 0.22 + (step + 0.01) * ny, panel_h * 0.46 + (step + 0.01) * nz), rot=(ang, 0, 0), colour="red")

    elif variant == "totem_monolith":
        z.box((W * 0.8, L * 0.8, 0.12), loc=(0, 0, 0.06), colour="grey")
        z.box((W * 0.65, L * 0.65, H * 0.92), loc=(0, 0, 0.12 + H * 0.46), colour="charcoal")
        z.box((W * 0.52, L * 0.68, H * 0.62), loc=(0, 0, H * 0.52), colour="cream")
        z.box((W * 0.56, L * 0.7, H * 0.12), loc=(0, 0, H * 0.88), colour="orange")


def _build_amenity(W, L, H, variant, aid, z):
    if variant == "drinking_fountain":
        z.box((W * 0.45, L * 0.55, H * 0.88), loc=(-W * 0.2, 0, H * 0.44), colour="teal")
        z.box((W * 0.48, L * 0.58, 0.08), loc=(-W * 0.2, 0, H * 0.9), colour="light_grey")
        z.cyl(0.02, 0.06, loc=(-W * 0.2, -L * 0.12, H * 0.95), colour="white", seg=6)
        low_z = H * 0.62
        z.box((W * 0.45, L * 0.45, 0.08), loc=(W * 0.22, 0, low_z), colour="light_grey")
        z.box((W * 0.38, L * 0.38, low_z - 0.08), loc=(W * 0.22, 0, (low_z - 0.08) * 0.5), colour="teal")
        z.cyl(0.02, 0.06, loc=(W * 0.22, -L * 0.1, low_z + 0.05), colour="white", seg=6)

    elif variant == "mist_arch":
        leg_t = 0.12
        plate_h = 0.04
        # Base mounting plates on the floor
        z.box((leg_t * 2.2, leg_t * 2.2, plate_h), loc=(-W * 0.45, 0, plate_h * 0.5), colour="charcoal")
        z.box((leg_t * 2.2, leg_t * 2.2, plate_h), loc=(W * 0.45, 0, plate_h * 0.5), colour="charcoal")
        # Vertical posts stand on the base plates (above Z=plate_h)
        post_h = H - plate_h
        z.box((leg_t, leg_t, post_h), loc=(-W * 0.45, 0, plate_h + post_h * 0.5), colour="teal")
        z.box((leg_t, leg_t, post_h), loc=(W * 0.45, 0, plate_h + post_h * 0.5), colour="teal")
        # Overhead crossbar
        z.box((W * 0.98, leg_t, leg_t), loc=(0, 0, H * 0.95), colour="teal")
        for x in (-W * 0.3, 0, W * 0.3):
            z.cyl(0.04, 0.06, loc=(x, 0, H * 0.9), colour="sky", seg=6)
