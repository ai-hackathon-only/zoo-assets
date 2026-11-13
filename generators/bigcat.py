"""Big cats and other felids (lion, tiger, leopard, cheetah, lynx, ...). Params come from the asset row.

size_m = [width, length nose-to-tail, height to top of head]. params:
  body: fur colour (palette name); belly: underside/muzzle colour (default cream);
  marks: list of "mane", "stripes", "rosettes", "rosettes_big", "spots", "tear_lines",
         "thick_tail", "short_tail", "ear_tufts", "big_ears", "long_legs" (serval), "stocky" (jaguar), "plain".
Markings are thin shells on the body surface, so they read in a 256 px thumbnail.
"""
import math

import bpy
from mathutils import Matrix, Vector

DARK = {"black": "charcoal"}  # mark colour on very dark fur


def _on_body(c, r, u, v, lift=1.0):
    """Point on an ellipsoid (centre c, radii r) at angle u around the long (Y) axis and v along it."""
    cy = math.cos(v)
    return (c[0] + r[0] * cy * math.sin(u) * lift, c[1] + r[1] * math.sin(v) * lift,
            c[2] + r[2] * cy * math.cos(u) * lift)


def build(a, z):
    W, L, H = a["size_m"]
    p = a.get("params", {})
    marks = set(p.get("marks", []))
    fur = p.get("body", "sand")
    belly = p.get("belly", "charcoal" if fur == "black" else "cream")
    ink = DARK.get(fur, "black")

    tail_frac = 0.12 if "short_tail" in marks else 0.32
    body_len = L * (1 - tail_frac) * 0.72  # torso; head sticks out in front
    leg_h = H * (0.46 if "long_legs" in marks else 0.34)
    torso_h = H * (0.34 if "long_legs" in marks else 0.44)
    bz = leg_h + torso_h * 0.45
    br = (W * (0.56 if "stocky" in marks else 0.46), body_len / 2, torso_h / 2 * (1.12 if "stocky" in marks else 1))
    by = L / 2 - L * 0.13 - br[1]  # torso centre (y = 0 is the middle of the full length)
    z.ball(1, loc=(0, by, bz), colour=fur, scale=br, seg=12, rings=8)
    z.joint("body", (0, by - br[1] * 0.8, bz), (0, by + br[1] * 0.8, bz))  # built facing +Y, turned at the end
    z.ball(1, loc=(0, by, bz - br[2] * 0.35), colour=belly, scale=(br[0] * 0.8, br[1] * 0.85, br[2] * 0.7), seg=10, rings=6)

    # legs: thick cylinders with paws
    lr = W * 0.13
    for y in (by + br[1] * 0.6, by - br[1] * 0.62):
        for x in (W * 0.22, -W * 0.22):
            top = leg_h + torso_h * 0.2
            leg = f"leg_{'F' if y > by else 'B'}{'L' if x < 0 else 'R'}"  # names after the turn
            z.joint(leg, (x, y, top), (x, y, 0), "body")
            z.set_bone(leg)
            z.cyl(lr, leg_h + torso_h * 0.2, loc=(x, y, (leg_h + torso_h * 0.2) / 2), colour=fur, r2=lr * 1.15, seg=7)
            z.ball(lr * 1.35, loc=(x, y + lr * 0.4, lr * 0.6), colour=belly if fur != "black" else fur,
                   scale=(1, 1.3, 0.6), seg=8, rings=4)

    z.set_bone("body")

    # neck and head
    hr = min(W * 0.4, H * 0.21) * (1.2 if "stocky" in marks else 0.8 if "long_legs" in marks else 1)
    hy, hz = by + br[1] + hr * 0.35, H - hr * 1.05
    neck_base = (0, by + br[1] * 0.6, bz + br[2] * 0.2)
    neck_top = (0, hy - hr * 0.5, hz - hr * 0.5)
    z.joint("neck", neck_base, neck_top, "body")
    z.joint("head", neck_top, (0, hy + hr * 1.2, hz), "neck")
    z.set_bone("neck")
    z.cyl(hr * 0.75, hz - bz, loc=(0, (by + br[1] * 0.7 + hy) / 2, (bz + hz) / 2), colour=fur, rot=(-35, 0, 0), seg=8)
    z.set_bone("head")
    if "mane" in marks and fur in ("sand", "tan", "orange"):  # lion mane; tamarins use other generators
        z.ball(hr * 1.5, loc=(0, hy - hr * 0.75, hz - hr * 0.2), colour="brown", scale=(1, 0.55, 1.05), seg=12, rings=8)
    z.ball(hr, loc=(0, hy, hz), colour=fur, scale=(1, 0.95, 0.9), seg=12, rings=8)
    z.ball(hr * 0.5, loc=(0, hy + hr * 0.75, hz - hr * 0.3), colour=belly, scale=(1.1, 0.9, 0.75), seg=8, rings=5)
    z.ball(hr * 0.14, loc=(0, hy + hr * 1.12, hz - hr * 0.12), colour="pink" if fur != "black" else "black",
           scale=(1.3, 1, 0.8), seg=6, rings=4)
    for s in (1, -1):
        z.ball(hr * 0.13, loc=(s * hr * 0.38, hy + hr * 0.8, hz + hr * 0.22), colour="yellow" if fur == "black" else "black",
               seg=6, rings=4)
        er = hr * (0.55 if "big_ears" in marks else 0.38)
        z.cone(er * 0.6, er, loc=(s * hr * 0.55, hy - hr * 0.1, hz + hr * 0.75 + er * 0.3), colour=fur,
               rot=(0, s * -20, 0), seg=6)
        if "ear_tufts" in marks:
            z.cone(er * 0.15, er * 0.8, loc=(s * hr * 0.62, hy - hr * 0.1, hz + hr * 0.75 + er * 1.1), colour="black", seg=4)
            z.cone(hr * 0.35, hr * 0.5, loc=(s * hr * 0.9, hy + hr * 0.1, hz - hr * 0.55), colour=belly,
                   rot=(0, s * 120, 0), seg=5)  # cheek ruff
        if "tear_lines" in marks:
            z.box((hr * 0.07, hr * 0.06, hr * 0.6), loc=(s * hr * 0.3, hy + hr * 0.92, hz - hr * 0.15), colour="black",
                  rot=(0, s * 12, 0))

    z.set_bone("tail")
    # tail: two segments, the second one raised; thick for snow leopard, black tip for lion
    tl = L * tail_frac
    tr = lr * (0.75 if "thick_tail" in marks else 0.4)
    ty0 = by - br[1] * 0.95
    tz0 = bz + br[2] * 0.3
    z.joint("tail", (0, ty0 + tl * 0.05, tz0), (0, ty0 - tl * 0.85, tz0 - tl * 0.25), "body")
    t1 = (0, ty0 - tl * 0.25, tz0 - tl * 0.2)
    z.cyl(tr, tl * 0.6, loc=t1, colour=fur, rot=(-55, 0, 0), seg=6)
    t2 = (0, ty0 - tl * 0.62, tz0 - tl * 0.26)
    z.cyl(tr * 0.92, tl * 0.5, loc=t2, colour=fur, rot=(-100, 0, 0), seg=7)  # seg differs from t1: no coplanar sides
    if "mane" in marks or "short_tail" in marks:
        z.ball(tr * 1.6, loc=(0, ty0 - tl * 0.85, tz0 - tl * 0.22), colour="black" if "short_tail" in marks else "brown",
               seg=6, rings=4)

    z.set_bone("body")
    # coat patterns on the torso
    if "stripes" in marks:  # bands that wrap the torso
        for i in range(8):
            t = -0.8 + i * 0.23
            k = math.sqrt(max(0.0, 1 - t * t)) * 1.08
            z.ball(1, loc=(0, by + br[1] * t, bz), colour=ink, scale=(br[0] * k, br[1] * 0.05, br[2] * k),
                   rot=(0, 0, 0), seg=10, rings=6)
        for s in (1, -1):  # face stripes
            with z.bone("head"):
                z.box((hr * 0.06, hr * 0.5, hr * 0.12), loc=(s * hr * 0.85, hy, hz + hr * 0.05), colour=ink, rot=(0, 0, s * 15))
    spot_kind = next((m for m in ("rosettes_big", "rosettes", "spots") if m in marks), None)
    if spot_kind:
        sr = W * {"rosettes_big": 0.09, "rosettes": 0.07, "spots": 0.045}[spot_kind]
        ring = spot_kind != "spots" and fur != "black"
        for i in range(6):
            for j, u in enumerate((-1.6, -1.0, -0.4, 0.4, 1.0, 1.6)):
                v = -1.05 + i * 0.42 + (0.2 if j % 2 else 0)
                c = _on_body((0, by, bz), br, u, v, 1.0)
                # flat disc lying on the coat: z axis along the ellipsoid normal, small spin per spot (z-fighting check)
                n = Vector(((c[0]) / br[0] ** 2, (c[1] - by) / br[1] ** 2, (c[2] - bz) / br[2] ** 2)).normalized()
                q = n.to_track_quat("Z", "Y").to_euler()
                rot = (math.degrees(q.x), math.degrees(q.y), math.degrees(q.z) + (i * 23 + j * 41) % 60)
                z.ball(sr, loc=c, colour=ink, scale=(1, 1, 0.3), rot=rot, seg=7, rings=3)
                if ring:  # lighter centre makes a rosette; jaguar ("stocky") also gets a dark dot inside
                    c2 = Vector(c) + n * sr * 0.22
                    rot2 = (rot[0], rot[1], rot[2] + 29)  # turned, so its faces never line up with the ring
                    z.ball(sr * 0.6, loc=c2, colour="tan" if fur != "tan" else "brown", scale=(1, 1, 0.3), rot=rot2, seg=6, rings=3)
                    if "stocky" in marks:
                        z.ball(sr * 0.22, loc=Vector(c) + n * sr * 0.36, colour=ink, scale=(1, 1, 0.4), rot=rot, seg=5, rings=2)

    # face -Y (front toward the thumbnail camera; glTF +Z)
    turn = Matrix.Rotation(math.pi, 4, "Z")
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            o.data.transform(turn)
    z.transform_joints(turn)
