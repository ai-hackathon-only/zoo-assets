"""Hoofed animals (giraffe, zebras, camels, deer, antelopes, bison, goats, tapir, horse, warthog).

size_m = [width, length nose-to-tail, height to top of head or horns]. The animal faces -Y (DECISION in Plan & roles).
params:
  body: coat colour (palette name);
  marks: any of
    neck/head: long_neck, ossicones, big_ears, banana_ears, beard, face_mask, upright_mane, mane_strip, tusks
    horns:     antlers, antlers_small, palm_antlers, straight_horns, lyre_horns, spiral_horns, corkscrew_horns,
               curved_horns, boss_horns, small_horns
    body:      stripes, thin_stripes, patches, spots, leg_stripes, saddle_white, hump1, hump2, hump_fur, fluffy
The parts are built at toy proportions, then scaled on Y and Z so length and height match size_m exactly.
"""
import math

import bpy
from mathutils import Matrix, Vector

HORN_ROOM = {"antlers": 0.2, "palm_antlers": 0.2, "antlers_small": 0.12, "straight_horns": 0.22,
             "corkscrew_horns": 0.22, "spiral_horns": 0.18, "lyre_horns": 0.16, "curved_horns": 0.07,
             "boss_horns": 0.06, "small_horns": 0.06, "ossicones": 0.03}
LOW_HEAD = ("hump_fur", "tusks", "saddle_white")


def _limb(z, a, b, r, colour, r2=None, seg=7):
    """Tapered cylinder from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    e = d.normalized().to_track_quat("Z", "Y").to_euler()
    return z.cyl(r, d.length, loc=(a + b) / 2, colour=colour, rot=tuple(math.degrees(x) for x in e),
                 seg=seg, r2=r if r2 is None else r2)


def _chain(z, pts, r0, r1, colour, seg=6):
    n = len(pts) - 1
    for i in range(n):
        _limb(z, pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, colour, r2=r0 + (r1 - r0) * (i + 1) / n, seg=seg)


def _fit(z, L, H):
    """Scale every part about the floor centre so the bounding box is L long (Y) and H tall (Z)."""
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    lo_y, hi_y = min(p.y for p in pts), max(p.y for p in pts)
    lo_z, hi_z = min(p.z for p in pts), max(p.z for p in pts)
    m = Matrix.Diagonal((1, L / (hi_y - lo_y), H / (hi_z - lo_z), 1)) @ Matrix.Translation((0, -(lo_y + hi_y) / 2, -lo_z))
    for o in obs:
        o.matrix_world = m @ o.matrix_world
    z.transform_joints(m)


def build(a, z):
    W, L, H = a["size_m"]
    p = a.get("params", {})
    m = set(p.get("marks", []))
    coat = p.get("body", "tan")
    ink = "charcoal" if coat == "black" else "black"
    giraffe = "ossicones" in m
    llama = "long_neck" in m and not giraffe
    low = any(k in m for k in LOW_HEAD)
    room = max([HORN_ROOM.get(k, 0) for k in m] + [0])

    leg_h = H * (0.42 if giraffe else 0.4 if llama else 0.3 if "tusks" in m else 0.34 if low else
                 0.42 if room >= 0.12 else 0.45)
    th = H * (0.17 if giraffe else 0.3 if "hump_fur" in m else 0.25 if low else 0.22)
    if "fluffy" in m:
        th *= 1.25
    body_l = L * (0.5 if giraffe else 0.56)
    by = L * 0.04
    bz = leg_h + th / 2
    br = (W * 0.42, body_l / 2, th / 2)
    z.ball(1, loc=(0, by, bz), colour=coat, scale=br, seg=14, rings=8)
    z.joint("body", (0, by + br[1] * 0.8, bz), (0, by - br[1] * 0.8, bz))
    belly = "white" if "lyre_horns" in m or "spots" in m or "straight_horns" in m else None
    if belly:
        z.ball(1, loc=(0, by, bz - br[2] * 0.35), colour=belly, scale=(br[0] * 0.85, br[1] * 0.85, br[2] * 0.68),
               seg=12, rings=6)

    # legs (front pair at -Y), dark hooves
    lr = max(W * 0.075, H * 0.025) * (1.5 if "hump_fur" in m or "boss_horns" in m else 1)
    for x in (br[0] * 0.55, -br[0] * 0.55):
        for y in (by - br[1] * 0.62, by + br[1] * 0.62):
            top = bz - br[2] * 0.1
            leg = f"leg_{'F' if y < by else 'B'}{'L' if x > 0 else 'R'}"
            z.joint(leg, (x, y, top), (x, y, 0), "body")
            z.set_bone(leg)
            _limb(z, (x, y, H * 0.03), (x, y, top), lr * 0.75, coat if "leg_stripes" not in m or y < by else "white",
                  r2=lr * 1.15)
            z.cyl(lr * 0.85, H * 0.04, loc=(x, y, H * 0.02), colour=ink if coat != "black" else "charcoal", seg=7)
            if "leg_stripes" in m and y > by:
                for i in range(4):
                    zz = leg_h * (0.25 + 0.17 * i)
                    z.cyl(lr * 1.2, leg_h * 0.06, loc=(x, y, zz), colour="black", seg=8)
            if "stripes" in m or "thin_stripes" in m and coat == "white":
                for i in range(3):
                    z.cyl(lr * 1.2, leg_h * 0.06, loc=(x, y, leg_h * (0.35 + 0.2 * i)), colour="black", seg=8)
            if "upright_mane" in m:
                z.cyl(lr * 0.95, leg_h * 0.35, loc=(x, y, leg_h * 0.2), colour="dark_brown", seg=7)

    z.set_bone("body")

    # humps
    if "hump1" in m:
        z.ball(1, loc=(0, by, bz + br[2] * 0.9), colour=coat, scale=(br[0] * 0.65, br[1] * 0.45, th * 0.8), seg=10, rings=6)
    if "hump2" in m:
        for f in (-0.5, 0.45):
            z.ball(1, loc=(0, by + br[1] * f, bz + br[2] * 0.9), colour=coat, scale=(br[0] * 0.55, br[1] * 0.28, th * 0.75),
                   seg=10, rings=6)
    if "hump_fur" in m:
        shag = "brown" if coat == "dark_brown" else "dark_brown"
        z.ball(1, loc=(0, by - br[1] * 0.45, bz + br[2] * 0.45), colour=shag,
               scale=(br[0] * 1.12, br[1] * 0.6, br[2] * 1.45), seg=12, rings=7)

    # neck and head
    hr = L * (0.075 if not giraffe else 0.05) * (1.25 if "tusks" in m else 1)
    top = H * (1 - room)
    neck_base = (0, by - br[1] * 0.72, bz + br[2] * 0.45)
    if low:
        hz = bz + br[2] * (0.1 if "hump_fur" in m else 0.2)
        hy = by - br[1] - hr * 1.0
    elif giraffe or llama:
        hz = top - hr * 0.9
        hy = neck_base[1] - hr * (1.4 if giraffe else 1.0)
    else:
        hz = top - hr * 0.95
        hy = by - br[1] - hr * 0.7
    neck_r = hr * (0.55 if giraffe else 0.7)
    if "fluffy" in m:
        neck_r *= 1.35
    neck_top = (0, hy + hr * 0.4, hz - hr * 0.1)
    z.joint("neck", neck_base, neck_top, "body")
    z.joint("head", neck_top, (0, hy - hr * 2.0, hz - hr * 0.3), "neck")
    with z.bone("neck"):
        _limb(z, neck_base, neck_top, neck_r * 1.2, coat, r2=neck_r, seg=8)
    z.set_bone("head")
    z.ball(hr, loc=(0, hy, hz), colour=coat, scale=(0.85, 1.0, 0.95), seg=10, rings=7)
    snl = hr * (1.1 if "saddle_white" in m else 1.5 if not "tusks" in m else 1.3)
    sn_end = (0, hy - hr * 0.5 - snl, hz - hr * (0.35 if not low else 0.55))
    muzzle = ("cream" if "upright_mane" in m or "lyre_horns" in m or llama else
              "black" if "stripes" in m or "thin_stripes" in m and coat == "white" or "beard" in m and coat == "charcoal"
              else coat)
    _limb(z, (0, hy - hr * 0.3, hz - hr * 0.1), sn_end, hr * 0.62, coat, r2=hr * 0.45, seg=8)
    z.ball(hr * 0.47, loc=sn_end, colour=muzzle if muzzle != coat else ink if "tusks" in m or "saddle_white" in m
           else coat, scale=(1, 0.7, 0.9), seg=8, rings=5)
    if "tusks" in m:
        for s in (1, -1):
            _chain(z, [(s * hr * 0.35, sn_end[1] + hr * 0.3, sn_end[2] - hr * 0.1),
                       (s * hr * 0.75, sn_end[1] + hr * 0.15, sn_end[2] + hr * 0.25),
                       (s * hr * 0.7, sn_end[1] + hr * 0.35, sn_end[2] + hr * 0.75)], hr * 0.12, hr * 0.03, "cream")
            z.ball(hr * 0.22, loc=(s * hr * 0.6, hy - hr * 0.6, hz - hr * 0.1), colour=coat, seg=6, rings=4)  # warts
    if "face_mask" in m:
        for s in (1, -1):
            _limb(z, (s * hr * 0.45, hy + hr * 0.2, hz + hr * 0.4), (s * hr * 0.38, sn_end[1] + hr * 0.2, sn_end[2]),
                  hr * 0.18, "black", seg=6)
        z.ball(hr * 0.5, loc=sn_end, colour="white", scale=(1.05, 0.7, 0.95), seg=8, rings=5)
    # eyes
    for s in (1, -1):
        z.ball(hr * 0.15, loc=(s * hr * 0.75, hy - hr * 0.35, hz + hr * 0.2), colour="black" if coat not in
               ("black", "charcoal", "dark_brown") else "white", seg=6, rings=4)
    # ears
    big = "banana_ears" in m or "big_ears" in m
    for s in (1, -1):
        ear_col = "black" if "face_mask" in m else coat
        if "banana_ears" in m:
            _chain(z, [(s * hr * 0.4, hy + hr * 0.3, hz + hr * 0.6), (s * hr * 0.6, hy + hr * 0.35, hz + hr * 1.3),
                       (s * hr * 0.45, hy + hr * 0.3, hz + hr * 1.8)], hr * 0.22, hr * 0.06, ear_col)
        else:
            sz = 0.75 if big else 0.45
            z.ball(hr * sz, loc=(s * hr * (0.8 + sz * 0.6), hy + hr * 0.35, hz + hr * 0.55), colour=ear_col,
                   scale=(1, 0.3, 0.45), rot=(0, s * -25, 0), seg=7, rings=4)

    # horns and antlers
    hb = [(s * hr * 0.4, hy + hr * 0.2, hz + hr * 0.75) for s in (1, -1)]
    horn_h = H * room
    for (x, y, zz), s in zip(hb, (1, -1)):
        if giraffe:
            _limb(z, (x * 0.8, y, zz), (x, y + hr * 0.1, zz + horn_h * 1.2), hr * 0.16, coat, seg=6)
            z.ball(hr * 0.2, loc=(x, y + hr * 0.1, zz + horn_h * 1.2), colour="dark_brown", seg=6, rings=4)
        elif "antlers" in m or "antlers_small" in m:
            col = "cream" if coat != "white" else "tan"
            beam = [(x, y, zz), (x + s * horn_h * 0.35, y + horn_h * 0.15, zz + horn_h * 0.5),
                    (x + s * horn_h * 0.55, y + horn_h * 0.05, zz + horn_h * 1.0)]
            _chain(z, beam, hr * 0.13, hr * 0.06, col)
            tines = 3 if "antlers" in m else 1
            for i in range(tines):
                b = Vector(beam[1]).lerp(Vector(beam[2]), 0.2 + 0.35 * i)
                _limb(z, b, b + Vector((s * horn_h * 0.05, -horn_h * 0.3, horn_h * 0.25)), hr * 0.07, col, r2=hr * 0.02, seg=5)
        elif "palm_antlers" in m:
            _limb(z, (x, y, zz), (x + s * horn_h * 0.4, y, zz + horn_h * 0.3), hr * 0.15, "tan", seg=6)
            z.ball(1, loc=(x + s * horn_h * 0.9, y + hr * 0.1, zz + horn_h * 0.55), colour="tan",
                   scale=(horn_h * 0.6, hr * 0.12, horn_h * 0.4), rot=(0, s * -25, 0), seg=10, rings=5)
            for i in range(4):
                tip = (x + s * horn_h * (0.5 + 0.28 * i), y, zz + horn_h * (0.85 + 0.1 * math.sin(i * 1.7)))
                _limb(z, (tip[0], tip[1], tip[2] - horn_h * 0.25), tip, hr * 0.07, "tan", r2=hr * 0.02, seg=5)
        elif "straight_horns" in m:
            _limb(z, (x, y, zz), (x * 1.3, y + horn_h * 0.55, zz + horn_h), hr * 0.1, "black", r2=hr * 0.03, seg=6)
        elif "lyre_horns" in m or "spiral_horns" in m or "corkscrew_horns" in m:
            twist = 3 if "spiral_horns" in m else 4 if "corkscrew_horns" in m else 1
            n = 6 if twist > 1 else 4
            pts = []
            for i in range(n + 1):
                t = i / n
                ang = t * twist * math.pi
                rad = hr * (0.4 if twist > 1 else 0.2) * (1 - 0.5 * t)
                pts.append((x + s * (rad * math.cos(ang) + horn_h * 0.25 * t),
                            y + horn_h * (0.3 if twist < 4 else 0.12) * t + rad * math.sin(ang),
                            zz + horn_h * t))
            _chain(z, pts, hr * 0.12, hr * 0.04, "black" if twist == 1 else "dark_brown" if coat != "dark_brown" else "tan")
        elif "curved_horns" in m or "boss_horns" in m:
            th_r = hr * (0.24 if "boss_horns" in m else 0.13)
            col = "charcoal" if coat in ("black", "charcoal") else "dark_brown" if coat != "dark_brown" else "black"
            _chain(z, [(x * 0.3, y, zz + hr * 0.05), (x + s * hr * 0.9, y, zz - hr * 0.1),
                       (x + s * hr * 1.6, y + hr * 0.1, zz + horn_h * 0.6), (x + s * hr * 1.4, y - hr * 0.1, zz + horn_h)],
                   th_r, th_r * 0.25, col)
        elif "small_horns" in m:
            _chain(z, [(x, y, zz), (x, y + horn_h * 0.4, zz + horn_h * 0.8), (x, y + horn_h * 0.9, zz + horn_h)],
                   hr * 0.09, hr * 0.03, "black")
        elif "hump_fur" in m:
            _chain(z, [(x, y, zz - hr * 0.2), (x + s * hr * 0.6, y, zz - hr * 0.1), (x + s * hr * 0.75, y, zz + hr * 0.4)],
                   hr * 0.12, hr * 0.03, "black")

    if "beard" in m:
        col = "black" if coat == "charcoal" else "white"
        _limb(z, (0, hy - hr * 0.2, hz - hr * 0.6), (0, hy - hr * 0.1, hz - hr * 1.7), hr * 0.3, col, r2=hr * 0.05, seg=6)
    z.set_bone("neck")
    # manes
    mane = None
    if "stripes" in m or "thin_stripes" in m and coat == "white":
        mane = "black"
    elif "upright_mane" in m or "mane_strip" in m:
        mane = "dark_brown" if coat != "dark_brown" else "black"
    elif giraffe:
        mane = "brown"
    if mane:
        n0 = Vector(neck_base) + Vector((0, br[1] * 0.1, neck_r * 1.1))
        n1 = Vector((0, hy + hr * 0.6, hz + hr * 0.75))
        _limb(z, n0, n1, neck_r * 0.35, mane, seg=5)
        if "mane_strip" in m:
            with z.bone("body"):
                _limb(z, n0, (0, by + br[1] * 0.4, bz + br[2] * 1.05), neck_r * 0.3, mane, seg=5)
    if "fluffy" in m:
        with z.bone("head"):
            z.ball(hr * 0.75, loc=(0, hy + hr * 0.1, hz + hr * 0.75), colour=coat, scale=(1, 1, 0.6), seg=8, rings=5)

    z.set_bone("body")

    # coat patterns
    if "stripes" in m or "thin_stripes" in m:
        n = 6 if "stripes" in m else 9
        col = "black" if coat == "white" else "white"
        thick = 0.08 if "stripes" in m else 0.03
        for i in range(n):
            f = -0.78 + 1.56 * i / (n - 1)
            sc = math.sqrt(max(0.05, 1 - f * f))
            z.ball(1, loc=(0, by + br[1] * f, bz + br[2] * 0.08), colour=col,
                   scale=(br[0] * sc * 1.07, br[1] * thick, br[2] * sc * 1.06), rot=(-11, 0, 0), seg=12, rings=6)
        if coat == "white":  # neck bands
            for t in (0.3, 0.55, 0.77):
                c = Vector(neck_base).lerp(Vector((0, hy, hz)), t)
                for s in (1, -1):
                    with z.bone("neck"):
                        z.ball(neck_r * 0.6, loc=(s * neck_r * 0.66, c.y, c.z), colour="black", scale=(0.6, 0.35, 1.1), seg=7, rings=5)
    if "patches" in m:
        for i in range(16):
            u = math.radians((i * 137.5) % 360)
            v = -0.7 + (i * 0.37) % 1.4
            c = (br[0] * math.cos(v) * math.sin(u), by + br[1] * math.sin(v), bz + br[2] * math.cos(v) * math.cos(u))
            if c[2] < bz - br[2] * 0.3:
                continue
            c = Vector((0, by, bz)).lerp(Vector(c), 0.9)  # sunk sphere shows as a flat patch
            z.ball(br[2] * 0.42, loc=c, colour="brown", seg=7, rings=5)
        for t in (0.2, 0.45, 0.7):
            c = Vector(neck_base).lerp(Vector((0, hy, hz)), t)
            for s in (1, -1):
                with z.bone("neck"):
                    z.ball(neck_r * 0.5, loc=(s * neck_r * 0.7, c.y, c.z), colour="brown", seg=6, rings=4)
    if "spots" in m:
        for i in range(12):
            s = 1 if i % 2 else -1
            v = -0.6 + (i // 2) * 0.24
            u = math.radians(s * 45)
            c = Vector((br[0] * math.cos(v) * math.sin(u), by + br[1] * math.sin(v), bz + br[2] * math.cos(v) * math.cos(u)))
            z.ball(br[2] * 0.2, loc=Vector((0, by, bz)).lerp(c, 0.93), colour="white", seg=6, rings=4)
    if "saddle_white" in m:
        z.ball(1, loc=(0, by + br[1] * 0.25, bz + br[2] * 0.06), colour="white",
               scale=(br[0] * 1.04, br[1] * 0.4, br[2] * 1.04), seg=14, rings=8)

    # tail (+Y)
    t0 = (0, by + br[1] * 0.95, bz + br[2] * 0.4)
    tl = H * (0.12 if giraffe else 0.25 if "upright_mane" in m or "stripes" in m or "thin_stripes" in m else 0.15)
    t1 = (0, t0[1] + tl * 0.2, t0[2] - tl)
    z.joint("tail", t0, t1, "body")
    z.set_bone("tail")
    _limb(z, t0, t1, lr * 0.3, coat, r2=lr * 0.2, seg=5)
    tuft = ink if coat not in ("cream", "white", "tan") or giraffe or "stripes" in m else coat
    z.ball(lr * 0.45, loc=t1, colour=tuft, scale=(1, 1, 1.8), seg=6, rings=4)

    _fit(z, L, H)
