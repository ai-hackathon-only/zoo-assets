"""Vehicle generator: 25 procedural zoo utility, transit, and service vehicles.

All models adhere to:
- Dimensions matching size_m ([width x, length y, height z])
- Origin at floor center (Z=0 at bottom, X=0, Y=0 centered)
- Forward facing -Y (matching camera and orientation conventions)
- Triangle budget <= 2,000 tris, file size <= 150 KB
- Colors mapped to palette/palette.png via lib.zoo
- Non-coplanar faces with 0 z-fighting
"""
import math


def build(asset, z):
    aid = asset["id"]
    params = asset.get("params", {})
    W, L, H = asset["size_m"][0], asset["size_m"][1], asset["size_m"][2]

    dispatch = {
        "keeper_golf_cart": _build_golf_cart,
        "utility_truck": _build_utility_truck,
        "safari_jeep": _build_safari_jeep,
        "safari_bus": _build_safari_bus,
        "zoo_train_engine": _build_zoo_train_engine,
        "zoo_train_carriage": _build_zoo_train_carriage,
        "tractor": _build_tractor,
        "feed_trailer": _build_feed_trailer,
        "animal_transport_truck": _build_animal_transport_truck,
        "vet_van": _build_vet_van,
        "ice_cream_cart": _build_ice_cream_cart,
        "delivery_van": _build_delivery_van,
        "wheelbarrow": _build_wheelbarrow,
        "hand_cart": _build_hand_cart,
        "stroller": _build_stroller,
        "wheelchair": _build_wheelchair,
        "bicycle": _build_bicycle,
        "kick_scooter": _build_kick_scooter,
        "pedal_boat": _build_pedal_boat,
        "rowing_boat": _build_rowing_boat,
        "keeper_quad_bike": _build_keeper_quad_bike,
        "lawn_mower": _build_lawn_mower,
        "forklift": _build_forklift,
        "water_tanker": _build_water_tanker,
        "sky_tram_gondola": _build_sky_tram_gondola,
    }

    builder = dispatch.get(aid)
    if builder:
        builder(W, L, H, aid, params, z)
    else:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="leaf")
    _rig(z)


def _rig(z):
    """One bone per wheel (pivot on the axle, bone along X so a turn about its own axis rolls the wheel); every other
    part is on the chassis bone (child of root). A wheel is a thin round part (X <= 0.3 m, Y and Z equal, >= 8 cm) standing on the ground;
    tyre and hub share a centre, so they share a bone. Doors and ramps are not rigged yet."""
    import bpy
    from mathutils import Vector
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    box = {}
    for o in meshes:
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = Vector(min(c[i] for c in cs) for i in range(3))
        hi = Vector(max(c[i] for c in cs) for i in range(3))
        box[o] = (lo, hi)
    keys = {}
    for o, (lo, hi) in box.items():
        d = hi - lo
        c = (lo + hi) / 2
        if d.x <= 0.3 and d.y >= 0.08 and abs(d.y - d.z) < 0.01 and c.z - d.z / 2 < 0.02:
            keys.setdefault((round(c.x, 2), round(c.y, 2)), []).append(o)
    hubs = {k: max(box[o][1].x - box[o][0].x for o in v) for k, v in keys.items()}
    for o in meshes:
        o["bone"] = "chassis"
    z.joint("chassis", (0, 0, 0), (0, 0, 0.1))
    for i, (k, objs) in enumerate(sorted(keys.items())):
        c = (box[objs[0]][0] + box[objs[0]][1]) / 2
        for o in objs:
            o["bone"] = f"wheel_{i}"
        half = hubs[k] / 2
        z.joint(f"wheel_{i}", (c.x - half, c.y, c.z), (c.x + half, c.y, c.z), parent="chassis")


def _add_wheel(z, r, w, loc, tire_col="black", hub_col="light_grey"):
    """Wheel oriented along X axis (rolls along Y). Hubcap extends clearly beyond tire face."""
    x, y, zpos = loc
    z.cyl(r=r, h=w, loc=(x, y, zpos), rot=(0, 90, 0), colour=tire_col)
    z.cyl(r=r * 0.52, h=w + 0.024, loc=(x, y, zpos), rot=(0, 90, 0), colour=hub_col)


# ==============================================================================
# 1. ZOO UTILITY & WORK VEHICLES
# ==============================================================================

def _build_golf_cart(W, L, H, aid, p, z):
    body = p.get("body", "leaf")
    roof = p.get("roof", "white")
    rw = 0.22
    for wx in (-W * 0.42, W * 0.42):
        _add_wheel(z, rw, 0.12, (wx, -L * 0.32, rw))
        _add_wheel(z, rw, 0.12, (wx, L * 0.32, rw))

    # Chassis floor platform
    z.box((W * 0.84, L * 0.88, 0.1), loc=(0, 0, rw * 1.35), colour="charcoal")
    # Front cowl
    z.box((W * 0.82, L * 0.28, H * 0.22), loc=(0, -L * 0.26, rw * 1.5 + H * 0.11), colour=body)
    # Windshield
    z.box((W * 0.78, 0.04, H * 0.26), loc=(0, -L * 0.12, rw * 1.5 + H * 0.35), colour="sky")
    # Front bumper & headlights
    z.box((W * 0.86, 0.08, 0.08), loc=(0, -L * 0.45, rw * 1.2), colour="charcoal")
    z.cyl(r=0.06, h=0.03, loc=(W * 0.28, -L * 0.45, rw * 1.6), rot=(90, 0, 0), colour="yellow")
    z.cyl(r=0.06, h=0.03, loc=(-W * 0.28, -L * 0.45, rw * 1.6), rot=(90, 0, 0), colour="yellow")
    # Bench seat & backrest
    z.box((W * 0.74, L * 0.24, 0.12), loc=(0, L * 0.04, rw * 1.5 + 0.16), colour="charcoal")
    z.box((W * 0.74, 0.08, 0.24), loc=(0, L * 0.16, rw * 1.5 + 0.34), colour="charcoal")
    # Steering column & wheel
    z.cyl(r=0.025, h=0.38, loc=(0.15, -L * 0.08, rw * 1.5 + 0.32), rot=(-30, 0, 0), colour="charcoal")
    z.cyl(r=0.12, h=0.03, loc=(0.15, -L * 0.02, rw * 1.5 + 0.48), rot=(-30, 0, 0), colour="black")
    # Rear utility cargo box
    z.box((W * 0.8, L * 0.28, H * 0.2), loc=(0, L * 0.32, rw * 1.5 + H * 0.1), colour=body)
    # 4 canopy posts
    for px in (-W * 0.38, W * 0.38):
        for py in (-L * 0.14, L * 0.38):
            z.cyl(r=0.02, h=H * 0.58, loc=(px, py, rw * 1.5 + H * 0.42), colour="light_grey")
    # White curved canopy roof
    z.box((W * 0.9, L * 0.86, 0.06), loc=(0, L * 0.1, H * 0.94), colour=roof)


def _build_utility_truck(W, L, H, aid, p, z):
    body = p.get("body", "white")
    accent = p.get("accent", "leaf")
    rw = 0.42
    for wx in (-W * 0.46, W * 0.46):
        _add_wheel(z, rw, 0.22, (wx, -L * 0.3, rw))
        _add_wheel(z, rw, 0.22, (wx, L * 0.28, rw))

    # Chassis frame & bumper
    z.box((W * 0.84, L * 0.94, 0.16), loc=(0, 0, rw * 1.05), colour="charcoal")
    z.box((W * 0.9, 0.12, 0.16), loc=(0, -L * 0.48, rw * 1.05), colour="charcoal")
    z.box((W * 0.9, 0.12, 0.16), loc=(0, L * 0.48, rw * 1.05), colour="charcoal")

    # Front cab lower body
    z.box((W * 0.86, L * 0.44, H * 0.36), loc=(0, -L * 0.22, rw * 1.1 + H * 0.22), colour=body)
    # Hood slope
    z.box((W * 0.84, L * 0.22, H * 0.18), loc=(0, -L * 0.34, rw * 1.1 + H * 0.24), colour=body)
    # Green accent side panels
    z.box((W * 0.89, L * 0.38, 0.09), loc=(0, -L * 0.22, rw * 1.1 + H * 0.16), colour=accent)
    # Upper cabin & windows
    z.box((W * 0.82, L * 0.22, H * 0.34), loc=(0, -L * 0.11, rw * 1.1 + H * 0.56), colour=body)
    # Windshield
    z.box((W * 0.76, 0.04, H * 0.22), loc=(0, -L * 0.225, rw * 1.1 + H * 0.56), colour="sky")
    # Side windows
    z.box((W * 0.84, L * 0.14, H * 0.2), loc=(0, -L * 0.11, rw * 1.1 + H * 0.56), colour="sky")
    # Front grille & headlights
    z.box((W * 0.56, 0.04, 0.18), loc=(0, -L * 0.46, rw * 1.1 + H * 0.18), colour="black")
    z.box((0.14, 0.04, 0.12), loc=(W * 0.34, -L * 0.46, rw * 1.1 + H * 0.22), colour="yellow")
    z.box((0.14, 0.04, 0.12), loc=(-W * 0.34, -L * 0.46, rw * 1.1 + H * 0.22), colour="yellow")

    # Rear pickup bed
    z.box((W * 0.84, L * 0.44, 0.08), loc=(0, L * 0.24, rw * 1.1 + 0.1), colour="grey")
    z.box((0.08, L * 0.44, H * 0.28), loc=(W * 0.4, L * 0.24, rw * 1.1 + H * 0.21), colour=body)
    z.box((0.08, L * 0.44, H * 0.28), loc=(-W * 0.4, L * 0.24, rw * 1.1 + H * 0.21), colour=body)
    z.box((W * 0.72, 0.08, H * 0.28), loc=(0, L * 0.46, rw * 1.1 + H * 0.21), colour=body)


def _build_safari_jeep(W, L, H, aid, p, z):
    body = p.get("body", "sand")
    accent = p.get("accent", "dark_brown")
    rw = 0.42
    for wx in (-W * 0.46, W * 0.46):
        _add_wheel(z, rw, 0.22, (wx, -L * 0.3, rw))
        _add_wheel(z, rw, 0.22, (wx, L * 0.28, rw))

    # Chassis & bumpers
    z.box((W * 0.84, L * 0.92, 0.16), loc=(0, 0, rw * 1.1), colour="charcoal")
    z.box((W * 0.88, 0.12, 0.14), loc=(0, -L * 0.48, rw * 1.1), colour=accent)
    # Lower body
    z.box((W * 0.84, L * 0.84, H * 0.28), loc=(0, 0, rw * 1.1 + H * 0.18), colour=body)
    # Hood
    z.box((W * 0.78, L * 0.34, H * 0.16), loc=(0, -L * 0.26, rw * 1.1 + H * 0.36), colour=body)
    # Front grille & round headlights
    z.box((W * 0.56, 0.04, 0.2), loc=(0, -L * 0.44, rw * 1.1 + H * 0.21), colour="black")
    z.cyl(r=0.08, h=0.04, loc=(W * 0.3, -L * 0.45, rw * 1.1 + H * 0.23), rot=(90, 0, 0), colour="yellow")
    z.cyl(r=0.08, h=0.04, loc=(-W * 0.3, -L * 0.45, rw * 1.1 + H * 0.23), rot=(90, 0, 0), colour="yellow")

    # Open cockpit interior
    z.box((0.32, 0.32, 0.28), loc=(W * 0.22, -L * 0.06, rw * 1.1 + H * 0.26), colour=accent)
    z.box((0.32, 0.32, 0.28), loc=(-W * 0.22, -L * 0.06, rw * 1.1 + H * 0.26), colour=accent)
    z.box((W * 0.7, 0.32, 0.28), loc=(0, L * 0.2, rw * 1.1 + H * 0.26), colour=accent)

    # Windshield frame & glass
    z.box((W * 0.74, 0.08, H * 0.26), loc=(0, -L * 0.1, rw * 1.1 + H * 0.52), colour=body)
    z.box((W * 0.64, 0.03, H * 0.18), loc=(0, -L * 0.1, rw * 1.1 + H * 0.52), colour="sky")

    # Dark brown roll cage
    for px in (-W * 0.38, W * 0.38):
        z.cyl(r=0.03, h=H * 0.45, loc=(px, -L * 0.09, rw * 1.1 + H * 0.62), colour=accent)
        z.cyl(r=0.03, h=H * 0.45, loc=(px, L * 0.36, rw * 1.1 + H * 0.62), colour=accent)
    z.box((W * 0.76, L * 0.44, 0.05), loc=(0, L * 0.13, rw * 1.1 + H * 0.85), colour=accent)

    # Rear mounted spare tire
    z.cyl(r=rw * 0.82, h=0.18, loc=(0, L * 0.45, rw * 1.1 + H * 0.25), rot=(90, 0, 0), colour="black")


def _build_safari_bus(W, L, H, aid, p, z):
    body = p.get("body", "olive")
    roof = p.get("roof", "cream")
    rw = 0.48
    for wx in (-W * 0.45, W * 0.45):
        for wy in (-L * 0.35, L * 0.15, L * 0.35):
            _add_wheel(z, rw, 0.24, (wx, wy, rw))

    # Chassis
    z.box((W * 0.84, L * 0.9, 0.2), loc=(0, 0, rw * 1.1), colour="charcoal")
    # Front cab
    z.box((W * 0.82, L * 0.22, H * 0.3), loc=(0, -L * 0.37, rw * 1.1 + H * 0.2), colour=body)
    z.box((W * 0.78, 0.04, H * 0.24), loc=(0, -L * 0.32, rw * 1.1 + H * 0.48), colour="sky")
    z.box((W * 0.62, 0.03, 0.18), loc=(0, -L * 0.482, rw * 1.1 + H * 0.16), colour="black")
    z.cyl(r=0.09, h=0.05, loc=(W * 0.32, -L * 0.488, rw * 1.1 + H * 0.18), rot=(90, 0, 0), colour="yellow")
    z.cyl(r=0.09, h=0.05, loc=(-W * 0.32, -L * 0.488, rw * 1.1 + H * 0.18), rot=(90, 0, 0), colour="yellow")

    # Open passenger deck with side half-walls
    z.box((W * 0.86, L * 0.64, 0.28), loc=(0, L * 0.08, rw * 1.1 + 0.2), colour=body)
    # 4 rows of benches
    for ypos in (-L * 0.15, 0.0, L * 0.15, L * 0.3):
        z.box((W * 0.7, 0.24, 0.2), loc=(0, ypos, rw * 1.1 + 0.44), colour="tan")
        z.box((W * 0.7, 0.05, 0.2), loc=(0, ypos + 0.11, rw * 1.1 + 0.64), colour="tan")

    # Canopy support posts (8)
    for px in (-W * 0.42, W * 0.42):
        for py in (-L * 0.24, -L * 0.08, L * 0.12, L * 0.38):
            z.cyl(r=0.03, h=H * 0.54, loc=(px, py, rw * 1.1 + H * 0.55), colour="charcoal")

    # Cream canopy roof
    z.box((W * 0.92, L * 0.78, 0.1), loc=(0, L * 0.06, H * 0.94), colour=roof)


def _build_zoo_train_engine(W, L, H, aid, p, z):
    body = p.get("body", "red")
    accent = p.get("accent", "yellow")
    rw = 0.28
    for wx in (-W * 0.44, W * 0.44):
        for wy in (-L * 0.32, 0.0, L * 0.32):
            z.cyl(r=rw, h=0.1, loc=(wx, wy, rw), rot=(0, 90, 0), colour="black")
            z.cyl(r=rw * 0.65, h=0.13, loc=(wx, wy, rw), rot=(0, 90, 0), colour=body)

    # Chassis plate
    z.box((W * 0.86, L * 0.9, 0.14), loc=(0, 0, rw * 1.25), colour="charcoal")
    # Front cowcatcher wedge
    z.box((W * 0.82, 0.26, 0.18), loc=(0, -L * 0.46, rw * 1.1), colour=accent, taper=0.6)

    # Red boiler cylinder
    z.cyl(r=0.38, h=L * 0.52, loc=(0, -L * 0.16, rw * 1.3 + 0.42), rot=(90, 0, 0), colour=body)
    # Front boiler face & big headlamp
    z.ball(r=0.37, loc=(0, -L * 0.42, rw * 1.3 + 0.42), colour="black")
    z.cyl(r=0.11, h=0.08, loc=(0, -L * 0.45, rw * 1.3 + 0.65), rot=(90, 0, 0), colour=accent)
    z.cyl(r=0.08, h=0.03, loc=(0, -L * 0.5, rw * 1.3 + 0.65), rot=(90, 0, 0), colour="yellow")

    # Smokestack (black funnel)
    z.cyl(r=0.1, h=0.42, loc=(0, -L * 0.32, rw * 1.3 + 0.95), colour="black", r2=0.14)
    # Steam dome (yellow)
    z.ball(r=0.12, loc=(0, -L * 0.1, rw * 1.3 + 0.88), colour=accent)

    # Driver cab at rear
    z.box((W * 0.84, L * 0.36, H * 0.48), loc=(0, L * 0.26, rw * 1.3 + H * 0.35), colour=body)
    # Cab roof
    z.box((W * 0.88, L * 0.4, 0.08), loc=(0, L * 0.26, H * 0.94), colour="black")
    # Cab windows
    z.box((W * 0.86, L * 0.18, 0.2), loc=(0, L * 0.26, rw * 1.3 + H * 0.42), colour="sky")


def _build_zoo_train_carriage(W, L, H, aid, p, z):
    body = p.get("body", "sky")
    roof = p.get("roof", "white")
    rw = 0.24
    for wx in (-W * 0.44, W * 0.44):
        for wy in (-L * 0.32, -L * 0.16, L * 0.16, L * 0.32):
            z.cyl(r=rw, h=0.08, loc=(wx, wy, rw), rot=(0, 90, 0), colour="black")
            z.cyl(r=rw * 0.55, h=0.11, loc=(wx, wy, rw), rot=(0, 90, 0), colour="light_grey")

    # Base floor & couplers
    z.box((W * 0.86, L * 0.9, 0.12), loc=(0, 0, rw * 1.25), colour="charcoal")
    z.cyl(r=0.05, h=0.16, loc=(0, -L * 0.48, rw * 1.25), rot=(90, 0, 0), colour="charcoal")
    z.cyl(r=0.05, h=0.16, loc=(0, L * 0.48, rw * 1.25), rot=(90, 0, 0), colour="charcoal")

    # Sky blue passenger body
    z.box((W * 0.86, L * 0.86, 0.3), loc=(0, 0, rw * 1.3 + 0.2), colour=body)
    # 3 wooden benches
    for by in (-L * 0.24, 0.0, L * 0.24):
        z.box((W * 0.72, 0.2, 0.16), loc=(0, by, rw * 1.3 + 0.34), colour="tan")
        z.box((W * 0.72, 0.04, 0.18), loc=(0, by + 0.1, rw * 1.3 + 0.52), colour="tan")

    # 6 roof canopy posts
    for px in (-W * 0.4, W * 0.4):
        for py in (-L * 0.36, 0.0, L * 0.36):
            z.cyl(r=0.02, h=H * 0.52, loc=(px, py, rw * 1.3 + H * 0.45), colour="charcoal")

    # White canopy roof
    z.box((W * 0.92, L * 0.94, 0.08), loc=(0, 0, H * 0.94), colour=roof)


def _build_tractor(W, L, H, aid, p, z):
    body = p.get("body", "red")
    rr = 0.58
    _add_wheel(z, rr, 0.26, (W * 0.44, L * 0.24, rr), "black", body)
    _add_wheel(z, rr, 0.26, (-W * 0.44, L * 0.24, rr), "black", body)
    rf = 0.32
    _add_wheel(z, rf, 0.18, (W * 0.38, -L * 0.32, rf), "black", body)
    _add_wheel(z, rf, 0.18, (-W * 0.38, -L * 0.32, rf), "black", body)

    # Central transmission chassis
    z.box((W * 0.52, L * 0.82, 0.26), loc=(0, 0, rf * 1.3), colour="charcoal")

    # Red engine hood
    z.box((W * 0.5, L * 0.44, H * 0.3), loc=(0, -L * 0.16, rf * 1.3 + H * 0.24), colour=body)
    # Front grille & headlights
    z.box((W * 0.44, 0.04, 0.2), loc=(0, -L * 0.39, rf * 1.3 + H * 0.2), colour="black")
    z.cyl(r=0.07, h=0.03, loc=(W * 0.18, -L * 0.4, rf * 1.3 + H * 0.24), rot=(90, 0, 0), colour="yellow")
    z.cyl(r=0.07, h=0.03, loc=(-W * 0.18, -L * 0.4, rf * 1.3 + H * 0.24), rot=(90, 0, 0), colour="yellow")

    # Exhaust pipe
    z.cyl(r=0.035, h=0.65, loc=(W * 0.22, -L * 0.22, rf * 1.3 + H * 0.55), colour="black")

    # Driver station
    z.box((0.4, 0.36, 0.26), loc=(0, L * 0.2, rf * 1.3 + H * 0.28), colour="charcoal")
    z.cyl(r=0.025, h=0.35, loc=(0, L * 0.02, rf * 1.3 + H * 0.42), rot=(-25, 0, 0), colour="charcoal")
    z.cyl(r=0.14, h=0.03, loc=(0, L * 0.08, rf * 1.3 + H * 0.56), rot=(-25, 0, 0), colour="black")

    # Safety roll bar (ROPS)
    for px in (-W * 0.35, W * 0.35):
        z.cyl(r=0.035, h=H * 0.5, loc=(px, L * 0.34, H * 0.68), colour="charcoal")
    z.box((W * 0.74, 0.08, 0.08), loc=(0, L * 0.34, H * 0.94), colour="charcoal")


def _build_feed_trailer(W, L, H, aid, p, z):
    body = p.get("body", "grey")
    load = p.get("load", "yellow")
    rw = 0.32
    _add_wheel(z, rw, 0.18, (W * 0.46, L * 0.06, rw))
    _add_wheel(z, rw, 0.18, (-W * 0.46, L * 0.06, rw))

    # Towing tongue at front (-Y)
    z.box((0.12, L * 0.26, 0.08), loc=(0, -L * 0.32, rw * 1.1), colour="charcoal")
    z.cyl(r=0.06, h=0.10, loc=(0, -L * 0.48, rw * 1.1), colour="grey")

    # Main trailer box
    z.box((W * 0.82, L * 0.62, H * 0.38), loc=(0, L * 0.08, rw * 1.1 + H * 0.2), colour=body)
    # Hay / feed load mound sitting distinctly higher and narrower
    z.box((W * 0.72, L * 0.52, H * 0.26), loc=(0, L * 0.08, rw * 1.1 + H * 0.48), colour=load)
    # Tailgate & rear lights
    z.box((W * 0.82, 0.05, 0.08), loc=(0, L * 0.4, rw * 1.1 + 0.12), colour="red")


def _build_animal_transport_truck(W, L, H, aid, p, z):
    body = p.get("body", "white")
    accent = p.get("accent", "forest")
    rw = 0.52
    for wx in (-W * 0.44, W * 0.44):
        for wy in (-L * 0.35, L * 0.2, L * 0.36):
            _add_wheel(z, rw, 0.26, (wx, wy, rw), "black", "charcoal")

    # Heavy chassis frame
    z.box((W * 0.86, L * 0.92, 0.26), loc=(0, 0, rw * 1.1), colour="charcoal")
    # Front cab
    z.box((W * 0.86, L * 0.22, H * 0.34), loc=(0, -L * 0.36, rw * 1.1 + H * 0.24), colour=body)
    # Forest green front bumper
    z.box((W * 0.9, 0.1, 0.2), loc=(0, -L * 0.47, rw * 1.05), colour=accent)
    # Windshield & grille
    z.box((W * 0.8, 0.04, 0.46), loc=(0, -L * 0.42, rw * 1.1 + H * 0.36), colour="sky")
    z.box((W * 0.6, 0.04, 0.22), loc=(0, -L * 0.48, rw * 1.1 + 0.18), colour="black")
    z.box((0.14, 0.04, 0.14), loc=(W * 0.34, -L * 0.48, rw * 1.1 + 0.2), colour="yellow")
    z.box((0.14, 0.04, 0.14), loc=(-W * 0.34, -L * 0.48, rw * 1.1 + 0.2), colour="yellow")

    # Transport container box
    z.box((W * 0.9, L * 0.62, H * 0.62), loc=(0, L * 0.12, rw * 1.1 + H * 0.38), colour=body)
    # Forest green accent side stripes
    z.box((W * 0.92, L * 0.6, 0.16), loc=(0, L * 0.12, rw * 1.1 + H * 0.2), colour=accent)
    # Ventilation grilles (4 slats per side)
    for gy in (-L * 0.1, 0.0, L * 0.1, L * 0.25):
        z.box((W * 0.93, 0.14, 0.05), loc=(0, gy, rw * 1.1 + H * 0.52), colour="charcoal")

    # Rear door ramp frame
    z.box((W * 0.84, 0.05, H * 0.54), loc=(0, L * 0.44, rw * 1.1 + H * 0.36), colour="grey")


def _build_vet_van(W, L, H, aid, p, z):
    _build_enclosed_van(W, L, H, p.get("body", "white"), p.get("accent", "red"), is_vet=True, z=z)


def _build_delivery_van(W, L, H, aid, p, z):
    _build_enclosed_van(W, L, H, p.get("body", "sky"), p.get("accent", "navy"), is_vet=False, z=z)


def _build_enclosed_van(W, L, H, body, accent, is_vet, z):
    rw = 0.4
    for wx in (-W * 0.45, W * 0.45):
        _add_wheel(z, rw, 0.22, (wx, -L * 0.3, rw))
        _add_wheel(z, rw, 0.22, (wx, L * 0.28, rw))

    # Chassis
    z.box((W * 0.84, L * 0.92, 0.16), loc=(0, 0, rw * 1.1), colour="charcoal")
    # Main lower van body
    z.box((W * 0.86, L * 0.88, H * 0.36), loc=(0, 0, rw * 1.1 + H * 0.2), colour=body)
    # Upper cabin
    z.box((W * 0.82, L * 0.84, H * 0.36), loc=(0, L * 0.02, rw * 1.1 + H * 0.56), colour=body)

    # Front hood slope & windshield
    z.box((W * 0.84, L * 0.18, H * 0.2), loc=(0, -L * 0.34, rw * 1.1 + H * 0.2), colour=body)
    z.box((W * 0.78, 0.04, H * 0.26), loc=(0, -L * 0.32, rw * 1.1 + H * 0.52), colour="sky")
    z.box((W * 0.85, 0.5, 0.24), loc=(0, -L * 0.16, rw * 1.1 + H * 0.52), colour="sky")

    # Front grille & headlights
    z.box((W * 0.6, 0.04, 0.16), loc=(0, -L * 0.46, rw * 1.1 + 0.18), colour="black")
    z.box((0.14, 0.04, 0.12), loc=(W * 0.33, -L * 0.46, rw * 1.1 + 0.2), colour="yellow")
    z.box((0.14, 0.04, 0.12), loc=(-W * 0.33, -L * 0.46, rw * 1.1 + 0.2), colour="yellow")

    if is_vet:
        # Red side stripe
        z.box((W * 0.88, L * 0.58, 0.1), loc=(0, L * 0.08, rw * 1.1 + H * 0.34), colour=accent)
        # Non-intersecting cross components
        z.box((W * 0.89, 0.05, 0.18), loc=(0, L * 0.1, rw * 1.1 + H * 0.55), colour="red")
        z.box((W * 0.89, 0.055, 0.05), loc=(0, L * 0.1 - 0.055, rw * 1.1 + H * 0.55), colour="red")
        z.box((W * 0.89, 0.055, 0.05), loc=(0, L * 0.1 + 0.055, rw * 1.1 + H * 0.55), colour="red")
        # Roof emergency light bar
        z.box((0.42, 0.14, 0.09), loc=(0, -L * 0.12, H * 0.94), colour="red")
    else:
        # Delivery van navy accent lower trim
        z.box((W * 0.88, L * 0.86, 0.1), loc=(0, 0, rw * 1.1 + 0.08), colour=accent)
        # Roof rack
        z.box((W * 0.74, L * 0.58, 0.05), loc=(0, L * 0.1, H * 0.94), colour="charcoal")


def _build_ice_cream_cart(W, L, H, aid, p, z):
    body = p.get("body", "pink")
    roof = p.get("roof", "white")
    rw = 0.35
    z.cyl(r=rw, h=0.06, loc=(W * 0.44, L * 0.15, rw), rot=(0, 90, 0), colour=roof)
    z.cyl(r=rw, h=0.06, loc=(-W * 0.44, L * 0.15, rw), rot=(0, 90, 0), colour=roof)
    rc = 0.1
    z.cyl(r=rc, h=0.05, loc=(0, -L * 0.32, rc), rot=(0, 90, 0), colour="charcoal")

    # Pink insulated freezer box
    z.box((W * 0.76, L * 0.64, H * 0.36), loc=(0, 0, rw * 1.1 + H * 0.18), colour=body)
    # Chrome counter lid with 2 round dipping wells
    z.box((W * 0.8, L * 0.66, 0.04), loc=(0, 0, rw * 1.1 + H * 0.37), colour="light_grey")
    z.cyl(r=0.12, h=0.03, loc=(0, -L * 0.14, rw * 1.1 + H * 0.4), colour="grey")
    z.cyl(r=0.12, h=0.03, loc=(0, L * 0.14, rw * 1.1 + H * 0.4), colour="grey")

    # Push handlebar at rear
    z.box((W * 0.66, 0.04, 0.04), loc=(0, L * 0.4, rw * 1.1 + H * 0.32), colour="charcoal")

    # 4 canopy posts
    for px in (-W * 0.36, W * 0.36):
        for py in (-L * 0.28, L * 0.28):
            z.cyl(r=0.02, h=H * 0.52, loc=(px, py, rw * 1.1 + H * 0.52), colour="light_grey")

    # Canopy roof
    z.box((W * 0.88, L * 0.78, 0.1), loc=(0, 0, H * 0.92), colour=roof)
    z.cone(r=0.08, h=0.16, loc=(0, 0, H * 0.98), colour="tan")


def _build_wheelbarrow(W, L, H, aid, p, z):
    # size_m: [0.7, 1.5, 0.7] -> target height 0.7
    body = p.get("body", "leaf")
    rw = 0.18
    # Single front wheel
    z.cyl(r=rw, h=0.06, loc=(0, -L * 0.35, rw), rot=(0, 90, 0), colour="black")
    z.cyl(r=rw * 0.5, h=0.08, loc=(0, -L * 0.35, rw), rot=(0, 90, 0), colour="grey")

    # Leaf green tray
    z.box((W * 0.75, L * 0.55, 0.28), loc=(0, -0.04, 0.36), colour=body, taper=0.75)

    # 2 handles lying along Y, tilted gently upward
    for hx in (-W * 0.28, W * 0.28):
        z.cyl(r=0.022, h=L * 0.8, loc=(hx, L * 0.1, 0.46), rot=(78, 0, 0), colour="brown")
        # Support legs
        z.box((0.035, 0.035, 0.25), loc=(hx, L * 0.05, 0.13), colour="charcoal")


def _build_hand_cart(W, L, H, aid, p, z):
    # size_m: [0.8, 1.4, 1.0] -> target height 1.0
    body = p.get("body", "brown")
    rw = 0.26
    z.cyl(r=rw, h=0.06, loc=(W * 0.44, 0, rw), rot=(0, 90, 0), colour="charcoal")
    z.cyl(r=rw, h=0.06, loc=(-W * 0.44, 0, rw), rot=(0, 90, 0), colour="charcoal")

    # Wooden slatted bed
    z.box((W * 0.76, L * 0.7, 0.08), loc=(0, 0, rw * 1.15), colour=body)
    # Side stakes and corner posts reaching up to H=0.92
    z.box((0.05, L * 0.7, 0.3), loc=(W * 0.36, 0, rw * 1.15 + 0.18), colour=body)
    z.box((0.05, L * 0.7, 0.3), loc=(-W * 0.36, 0, rw * 1.15 + 0.18), colour=body)

    # Upright front stake rack
    z.box((W * 0.76, 0.05, 0.5), loc=(0, -L * 0.34, 0.65), colour=body)

    # Pull handle at front
    z.cyl(r=0.025, h=0.8, loc=(0, -L * 0.36, 0.55), rot=(-35, 0, 0), colour="charcoal")
    z.box((W * 0.4, 0.04, 0.04), loc=(0, -L * 0.48, 0.88), colour="charcoal")
    # Front floor rest stand
    z.box((0.05, 0.05, rw * 1.1), loc=(0, -L * 0.28, rw * 0.55), colour="charcoal")


def _build_stroller(W, L, H, aid, p, z):
    body = p.get("body", "navy")
    rw = 0.1
    for wx in (-W * 0.4, W * 0.4):
        for wy in (-L * 0.3, L * 0.26):
            z.cyl(r=rw, h=0.05, loc=(wx, wy, rw), rot=(0, 90, 0), colour="black")

    # Diagonal aluminum frame
    for fx in (-W * 0.35, W * 0.35):
        z.cyl(r=0.02, h=H * 0.85, loc=(fx, 0, H * 0.48), rot=(20, 0, 0), colour="light_grey")

    # Navy fabric seat
    z.box((W * 0.65, L * 0.38, 0.28), loc=(0, -0.02, rw * 1.5 + 0.24), colour=body)
    # Sun canopy hood
    z.box((W * 0.68, 0.32, 0.24), loc=(0, -0.04, H * 0.68), colour=body)
    # Push handlebar at rear
    z.box((W * 0.62, 0.04, 0.04), loc=(0, L * 0.35, H * 0.94), colour="charcoal")


def _build_wheelchair(W, L, H, aid, p, z):
    body = p.get("body", "charcoal")
    rr = 0.32
    _add_wheel(z, rr, 0.05, (W * 0.44, L * 0.12, rr), "black", "light_grey")
    _add_wheel(z, rr, 0.05, (-W * 0.44, L * 0.12, rr), "black", "light_grey")
    rf = 0.08
    z.cyl(r=rf, h=0.04, loc=(W * 0.35, -L * 0.3, rf), rot=(0, 90, 0), colour="black")
    z.cyl(r=rf, h=0.04, loc=(-W * 0.35, -L * 0.3, rf), rot=(0, 90, 0), colour="black")

    # Frame & seat cushion
    z.box((W * 0.62, L * 0.44, 0.08), loc=(0, -0.02, rr * 1.3), colour=body)
    # Padded backrest
    z.box((W * 0.62, 0.06, 0.38), loc=(0, L * 0.2, rr * 1.3 + 0.22), colour=body)
    # Armrests
    z.box((0.05, 0.35, 0.04), loc=(W * 0.33, 0, rr * 1.3 + 0.18), colour="black")
    z.box((0.05, 0.35, 0.04), loc=(-W * 0.33, 0, rr * 1.3 + 0.18), colour="black")
    # Footrests
    z.box((0.15, 0.18, 0.03), loc=(W * 0.2, -L * 0.36, rf * 2.0), colour="grey")
    z.box((0.15, 0.18, 0.03), loc=(-W * 0.2, -L * 0.36, rf * 2.0), colour="grey")
    # Push handles
    z.cyl(r=0.02, h=0.14, loc=(W * 0.26, L * 0.24, H * 0.92), colour="black")
    z.cyl(r=0.02, h=0.14, loc=(-W * 0.26, L * 0.24, H * 0.92), colour="black")


def _build_bicycle(W, L, H, aid, p, z):
    body = p.get("body", "teal")
    rw = 0.35
    z.cyl(r=rw, h=0.05, loc=(0, -L * 0.32, rw), rot=(0, 90, 0), colour="black")
    z.cyl(r=rw, h=0.05, loc=(0, L * 0.32, rw), rot=(0, 90, 0), colour="black")
    z.cyl(r=rw * 0.6, h=0.07, loc=(0, -L * 0.32, rw), rot=(0, 90, 0), colour="light_grey")
    z.cyl(r=rw * 0.6, h=0.07, loc=(0, L * 0.32, rw), rot=(0, 90, 0), colour="light_grey")

    # Diamond frame in teal
    z.cyl(r=0.025, h=0.65, loc=(0, 0, rw * 1.3), rot=(20, 0, 0), colour=body)
    z.cyl(r=0.025, h=0.6, loc=(0, -L * 0.12, rw * 1.3), rot=(-35, 0, 0), colour=body)
    z.cyl(r=0.025, h=0.55, loc=(0, -L * 0.08, rw * 1.8), colour=body)

    # Handlebars & grips
    z.box((W * 0.85, 0.04, 0.04), loc=(0, -L * 0.24, H * 0.92), colour="charcoal")
    # Saddle
    z.box((0.18, 0.25, 0.06), loc=(0, L * 0.06, H * 0.82), colour="black")
    # Luggage rack
    z.box((0.18, 0.35, 0.04), loc=(0, L * 0.26, rw * 2.1), colour="grey")


def _build_kick_scooter(W, L, H, aid, p, z):
    body = p.get("body", "orange")
    rw = 0.1
    z.cyl(r=rw, h=0.04, loc=(0, -L * 0.36, rw), rot=(0, 90, 0), colour="black")
    z.cyl(r=rw, h=0.04, loc=(0, L * 0.36, rw), rot=(0, 90, 0), colour="black")

    # Foot deck
    z.box((W * 0.38, L * 0.58, 0.05), loc=(0, 0, rw * 1.2), colour=body)
    # Rear foot brake
    z.box((0.08, 0.14, 0.08), loc=(0, L * 0.3, rw * 1.6), colour="charcoal")
    # Steering column
    z.cyl(r=0.025, h=0.82, loc=(0, -L * 0.32, H * 0.52), rot=(10, 0, 0), colour="light_grey")
    # T-bar handlebars
    z.box((W * 0.88, 0.04, 0.04), loc=(0, -L * 0.28, H * 0.94), colour="charcoal")


# ==============================================================================
# 2. WATER & SPECIALTY TRANSIT
# ==============================================================================

def _build_pedal_boat(W, L, H, aid, p, z):
    body = p.get("body", "yellow")
    accent = p.get("accent", "white")
    for fx in (-W * 0.32, W * 0.32):
        z.box((0.36, L * 0.86, 0.3), loc=(fx, 0, 0.2), colour=body, taper=0.7)

    # Central cockpit deck
    z.box((W * 0.88, L * 0.68, 0.22), loc=(0, 0, 0.35), colour=body)
    # Two white bucket seats
    z.box((0.42, 0.34, 0.44), loc=(W * 0.24, L * 0.04, 0.62), colour=accent)
    z.box((0.42, 0.34, 0.44), loc=(-W * 0.24, L * 0.04, 0.62), colour=accent)
    # Central steering wheel
    z.cyl(r=0.12, h=0.03, loc=(0, -L * 0.12, 0.68), rot=(-25, 0, 0), colour="charcoal")
    # Rear paddle wheel cover
    z.box((0.35, 0.35, 0.32), loc=(0, L * 0.38, 0.35), colour=body)

    # Bimini sun shade canopy arch to reach target height ~1.15m
    for px in (-W * 0.4, W * 0.4):
        z.cyl(r=0.02, h=0.55, loc=(px, L * 0.08, 0.88), colour="light_grey")
    z.box((W * 0.85, 0.65, 0.05), loc=(0, L * 0.08, 1.16), colour=accent)


def _build_rowing_boat(W, L, H, aid, p, z):
    body = p.get("body", "brown")
    # Wooden hull - target height 0.6m
    z.box((W * 0.72, L * 0.88, 0.22), loc=(0, 0, 0.14), colour=body)
    z.box((W * 0.86, L * 0.9, 0.38), loc=(0, 0, 0.38), colour=body, taper=0.85)
    # Hollow inner cavity
    z.box((W * 0.68, L * 0.82, 0.28), loc=(0, 0, 0.42), colour="cream")
    # 2 wooden rowing thwarts / benches
    z.box((W * 0.74, 0.24, 0.06), loc=(0, -L * 0.12, 0.46), colour="tan")
    z.box((W * 0.74, 0.24, 0.06), loc=(0, L * 0.18, 0.46), colour="tan")
    # Pair of oars lying flat along gunwales
    z.cyl(r=0.022, h=1.6, loc=(W * 0.34, 0, 0.54), rot=(90, 0, 10), colour="tan")
    z.cyl(r=0.022, h=1.6, loc=(-W * 0.34, 0, 0.54), rot=(90, 0, -10), colour="tan")


def _build_keeper_quad_bike(W, L, H, aid, p, z):
    body = p.get("body", "forest")
    rw = 0.32
    for wx in (-W * 0.44, W * 0.44):
        _add_wheel(z, rw, 0.22, (wx, -L * 0.28, rw), "black", "charcoal")
        _add_wheel(z, rw, 0.22, (wx, L * 0.28, rw), "black", "charcoal")

    # Forest green fenders & body
    z.box((W * 0.82, L * 0.74, 0.26), loc=(0, 0, rw * 1.1 + 0.16), colour=body)
    # Black saddle seat
    z.box((0.36, L * 0.46, 0.14), loc=(0, 0.04, rw * 1.1 + 0.34), colour="black")
    # Front & rear cargo racks
    z.box((W * 0.72, 0.28, 0.1), loc=(0, -L * 0.36, rw * 1.1 + 0.26), colour="charcoal")
    z.box((W * 0.74, 0.32, 0.1), loc=(0, L * 0.36, rw * 1.1 + 0.28), colour="charcoal")
    # Handlebars & headlights
    z.box((W * 0.68, 0.04, 0.04), loc=(0, -L * 0.18, H * 0.88), colour="charcoal")
    z.cyl(r=0.06, h=0.03, loc=(W * 0.18, -L * 0.22, H * 0.72), rot=(90, 0, 0), colour="yellow")
    z.cyl(r=0.06, h=0.03, loc=(-W * 0.18, -L * 0.22, H * 0.72), rot=(90, 0, 0), colour="yellow")


def _build_lawn_mower(W, L, H, aid, p, z):
    body = p.get("body", "leaf")
    rr = 0.26
    rf = 0.18
    _add_wheel(z, rr, 0.16, (W * 0.44, L * 0.26, rr), "black", "yellow")
    _add_wheel(z, rr, 0.16, (-W * 0.44, L * 0.26, rr), "black", "yellow")
    _add_wheel(z, rf, 0.12, (W * 0.4, -L * 0.3, rf), "black", "yellow")
    _add_wheel(z, rf, 0.12, (-W * 0.4, -L * 0.3, rf), "black", "yellow")

    # Mower deck
    z.box((W * 0.84, 0.64, 0.12), loc=(0, -0.05, 0.18), colour="charcoal")
    # Body hood
    z.box((W * 0.64, L * 0.72, 0.32), loc=(0, -0.08, rf * 1.2 + 0.25), colour=body)
    # High-back driver seat
    z.box((0.42, 0.36, 0.34), loc=(0, L * 0.16, rf * 1.2 + 0.48), colour="charcoal")
    # Steering wheel
    z.cyl(r=0.14, h=0.03, loc=(0, -0.12, H * 0.78), rot=(25, 0, 0), colour="charcoal")
    # Grass collection hopper at rear
    z.box((W * 0.72, 0.4, 0.4), loc=(0, L * 0.38, rf * 1.2 + 0.4), colour="charcoal")


def _build_forklift(W, L, H, aid, p, z):
    body = p.get("body", "yellow")
    rf = 0.28
    rr = 0.24
    _add_wheel(z, rf, 0.16, (W * 0.44, -L * 0.15, rf))
    _add_wheel(z, rf, 0.16, (-W * 0.44, -L * 0.15, rf))
    _add_wheel(z, rr, 0.14, (W * 0.42, L * 0.28, rr))
    _add_wheel(z, rr, 0.14, (-W * 0.42, L * 0.28, rr))

    # Yellow body with rear counterweight
    z.box((W * 0.8, L * 0.54, 0.52), loc=(0, L * 0.14, rf * 1.2 + 0.2), colour=body)
    # Vertical mast at front
    z.box((W * 0.62, 0.08, H * 0.8), loc=(0, -L * 0.28, H * 0.48), colour="charcoal")
    # Dual lifting forks extending forward
    z.box((0.1, 0.72, 0.04), loc=(W * 0.2, -L * 0.5, 0.08), colour="grey")
    z.box((0.1, 0.72, 0.04), loc=(-W * 0.2, -L * 0.5, 0.08), colour="grey")
    # Overhead protective roll cage (FOPS)
    for cx in (-W * 0.36, W * 0.36):
        for cy in (-0.05, L * 0.32):
            z.cyl(r=0.03, h=H * 0.52, loc=(cx, cy, H * 0.66), colour="charcoal")
    z.box((W * 0.76, L * 0.42, 0.06), loc=(0, L * 0.14, H * 0.94), colour="charcoal")
    # Driver seat
    z.box((0.4, 0.36, 0.26), loc=(0, L * 0.12, rf * 1.2 + 0.55), colour="black")


def _build_water_tanker(W, L, H, aid, p, z):
    body = p.get("body", "water")
    rw = 0.45
    _add_wheel(z, rw, 0.22, (W * 0.44, L * 0.14, rw))
    _add_wheel(z, rw, 0.22, (-W * 0.44, L * 0.14, rw))

    # Chassis frame & tow hitch
    z.box((W * 0.74, L * 0.84, 0.16), loc=(0, 0, rw * 1.1), colour="charcoal")
    z.cyl(r=0.06, h=0.36, loc=(0, -L * 0.44, rw * 1.1), rot=(90, 0, 0), colour="charcoal")

    # Cylindrical water tank
    z.cyl(r=0.56, h=L * 0.62, loc=(0, 0.08, rw * 1.1 + 0.58), rot=(90, 0, 0), colour=body)
    z.ball(r=0.55, loc=(0, -L * 0.23, rw * 1.1 + 0.58), colour=body)
    z.ball(r=0.55, loc=(0, L * 0.39, rw * 1.1 + 0.58), colour=body)

    # Top manhole inspection dome
    z.cyl(r=0.2, h=0.08, loc=(0, 0.08, H * 0.94), colour="charcoal")
    # Rear water discharge valve, hose reel, and dispensing tap
    z.cyl(r=0.18, h=0.14, loc=(0, L * 0.44, rw * 1.1 + 0.22), rot=(90, 0, 0), colour="grey")


def _build_sky_tram_gondola(W, L, H, aid, p, z):
    body = p.get("body", "red")
    win = p.get("window", "sky")

    # Red cabin body
    z.box((W * 0.84, L * 0.84, H * 0.54), loc=(0, 0, H * 0.32), colour=body, taper=0.9)
    # Panoramic window band
    z.box((W * 0.88, L * 0.88, 0.4), loc=(0, 0, H * 0.38), colour=win)
    # Lower bumper band
    z.box((W * 0.86, L * 0.86, 0.08), loc=(0, 0, 0.12), colour="charcoal")

    # Suspension hanger arm rising from roof
    z.cyl(r=0.05, h=H * 0.35, loc=(0, 0, H * 0.75), colour="charcoal")
    # Upper cable pulley clamp
    z.box((0.22, 0.44, 0.14), loc=(0, 0, H * 0.94), colour="charcoal")
    z.cyl(r=0.09, h=0.05, loc=(0, -0.16, H * 0.94), rot=(0, 90, 0), colour="grey")
    z.cyl(r=0.09, h=0.05, loc=(0, 0.16, H * 0.94), rot=(0, 90, 0), colour="grey")
