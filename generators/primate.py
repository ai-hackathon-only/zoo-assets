"""Primates: great apes and gibbons (sitting, arms to the ground or raised), monkeys and lemurs (on all fours, tail).

size_m = [width, length incl. tail, height]. The animal faces -Y (DECISION in Plan & roles).
params:
  body: fur colour (palette name)
  marks: any of
    apes:    pale_face, silver_back, long_arms, parted_hair, face_ring
    monkeys: ringed_tail, red_blue_face, red_face, mane, prehensile_tail, big_nose, white_mask
An asset is an ape when it has none of the monkey marks.
"""
import math

from generators.bird import _Tagger, _bounds
from generators.quadruped import _limb

MONKEY = {"ringed_tail", "red_blue_face", "red_face", "mane", "prehensile_tail", "big_nose", "white_mask"}
LONG_TAIL = {"ringed_tail", "mane", "prehensile_tail", "big_nose", "white_mask"}


def build(a, z):
    W, L, H = a["size_m"]
    p = a.get("params", {})
    m = set(p.get("marks", []))
    fur = p.get("body", "brown")
    t = _Tagger(z)
    t.SIDED = ("leg", "arm")  # +X is the animal's left (it faces -Y)
    if m & MONKEY:
        _monkey(t, W, L, H, fur, m)
    else:
        _ape(t, W, L, H, fur, m)
    _declare_joints(z)


def _declare_joints(z):
    """Pivots from the tagged parts. Bones: hips (whole torso), neck, head, tail, and either arm_L/R + leg_L/R (apes)
    or leg_FL/FR/BL/BR (monkeys). Limbs hang from their shoulder or hip and swing about X."""
    import bpy
    from mathutils import Vector as V
    bpy.context.view_layer.update()
    groups = {}
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            groups.setdefault(o.get("bone", "hips"), []).append(o)
    bb = {k: _bounds(v) for k, v in groups.items()}
    lo, hi = bb["hips"]
    zc = (lo.z + hi.z) / 2
    z.joint("hips", (0, hi.y, zc), (0, lo.y, zc), "root")
    body_lo, body_hi = lo, hi
    lo, hi = bb["neck"]
    xc, yc = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    z.joint("neck", (xc, yc, lo.z), (xc, yc, hi.z), "hips")
    hp = V((xc, yc, hi.z))
    lo, hi = bb["head"]
    z.joint("head", hp, (hp.x, lo.y, hp.z), "neck")
    if "tail" in bb:
        lo, hi = bb["tail"]
        z.joint("tail", (0, lo.y, hi.z), (0, hi.y, lo.z), "hips")
    sh_z = body_lo.z + 0.85 * (body_hi.z - body_lo.z)
    for k, (lo, hi) in bb.items():
        if k.startswith("leg_"):
            xc, yc = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
            top = hi.z if len(k) == 7 else min(hi.z, body_lo.z + 0.5 * (body_hi.z - body_lo.z))
            z.joint(k, (xc, yc, top), (xc, yc, lo.z), "hips")
        elif k.startswith("arm_"):
            xi = lo.x if k.endswith("L") else hi.x
            top = max(lo.z, min(hi.z, sh_z))
            z.joint(k, (xi, (lo.y + hi.y) / 2, top), (xi, (lo.y + hi.y) / 2, lo.z), "hips")


def _face(z, c, r, fur, m, ape):
    """Face on the -Y side of a head ball at c with radius r."""
    x, y, h = c
    skin = {"pale_face": "skin_2", "red_face": "red", "big_nose": "skin_2", "mane": "skin_4"}
    face = next((skin[k] for k in skin if k in m), "black" if fur in ("black", "charcoal") else "skin_4")
    if "ringed_tail" in m or "white_mask" in m:
        face = "white"
    if "face_ring" in m:  # white ring around a black face
        z.ball(r * 0.86, loc=(x, y - r * 0.5, h + r * 0.03), colour="white", scale=(1.04, 0.5, 1.08), seg=12, rings=7)
        face = "black"
    z.ball(r * 0.72, loc=(x, y - r * 0.68, h), colour=face, scale=(1, 0.55, 1.0), seg=12, rings=7)
    # muzzle
    mz = "black" if "white_mask" in m else face
    mlen = 0.65 if "ringed_tail" in m else 0.3 if "red_blue_face" not in m else 0.75
    z.ball(r * 0.45, loc=(x, y - r * (0.9 + mlen * 0.4), h - r * 0.4), colour=mz,
           scale=(1.1, 0.6 + mlen, 0.75), seg=10, rings=6)
    if "red_blue_face" in m:  # mandrill: red nose ridge, blue ridges each side, yellow beard
        z.ball(r * 0.16, loc=(x, y - r * 1.25, h - r * 0.2), colour="red", scale=(1, 2.6, 1.2), seg=8, rings=5)
        for s in (1, -1):
            z.ball(r * 0.2, loc=(x + s * r * 0.3, y - r * 1.1, h - r * 0.3), colour="sky", scale=(0.8, 2.6, 1.3),
                   seg=8, rings=5)
        z.ball(r * 0.4, loc=(x, y - r * 0.6, h - r * 0.85), colour="yellow", scale=(1.2, 0.8, 0.9), seg=8, rings=5)
    if "big_nose" in m:  # proboscis monkey: long drooping nose
        z.ball(r * 0.28, loc=(x, y - r * 1.3, h - r * 0.45), colour="pink", scale=(1, 0.9, 1.6), seg=8, rings=6)
    if "ringed_tail" in m:  # lemur: black eye patches and nose
        z.ball(r * 0.12, loc=(x, y - r * 1.75, h - r * 0.35), colour="black", seg=6, rings=4)
    if "parted_hair" in m:  # bonobo: pink lips, hair parted into two side tufts
        z.ball(r * 0.25, loc=(x, y - r * 1.02, h - r * 0.55), colour="pink", scale=(1.4, 0.6, 0.5), seg=8, rings=5)
        for s in (1, -1):
            z.ball(r * 0.5, loc=(x + s * r * 0.55, y + r * 0.1, h + r * 0.75), colour=fur, scale=(0.9, 1.1, 0.6),
                   seg=8, rings=5)
    if "prehensile_tail" in m:  # howler: dark beard
        z.ball(r * 0.45, loc=(x, y - r * 0.45, h - r * 0.85), colour=fur, scale=(1, 0.8, 1.0), seg=8, rings=5)
    # eyes (with dark patches on lemurs, dark cap above white mask)
    for s in (1, -1):
        ex, ey, eh = x + s * r * 0.3, y - r * 1.06, h + r * 0.15
        if "ringed_tail" in m or "white_mask" in m:
            z.ball(r * 0.22, loc=(ex, ey + r * 0.05, eh), colour="black", scale=(1, 0.5, 1.1), seg=8, rings=5)
            z.ball(r * 0.09, loc=(ex, ey - r * 0.08, eh), colour="orange" if "ringed_tail" in m else "white",
                   seg=6, rings=4)
        else:
            z.ball(r * 0.1, loc=(ex, ey, eh), colour="white" if face == "black" else "black", seg=6, rings=4)
        # ears (hidden in the mane on tamarins)
        if "mane" not in m:
            ec = face if ape else fur
            z.ball(r * (0.3 if ape else 0.22), loc=(x + s * r * 0.98, y, h + r * 0.1), colour=ec, scale=(0.4, 0.8, 1),
                   seg=8, rings=5)
    if ape:  # brow ridge
        z.ball(r * 0.6, loc=(x, y - r * 0.78, h + r * 0.38), colour=fur, scale=(1.2, 0.4, 0.3), seg=8, rings=4)
    if "white_mask" in m:  # squirrel monkey: dark crown cap
        z.ball(r * 0.85, loc=(x, y + r * 0.1, h + r * 0.35), colour="black", scale=(1, 1, 0.6), seg=10, rings=5)


def _ape(z, W, L, H, fur, m):
    """Sitting ape. Knuckles on the ground in front; gibbons hold both arms up."""
    gibbon = "face_ring" in m
    big = "silver_back" in m
    hr = H * (0.11 if big else 0.12 if not gibbon else 0.14)
    top = H * 0.72 if gibbon else H  # gibbon arms reach the top
    hc = (0, -W * 0.12, top - hr * (1.25 if big else 1.0))
    t_lo, t_hi = H * 0.12, hc[2] - hr * 0.6
    tr = (W * (0.4 if big else 0.32), W * (0.32 if big else 0.27), (t_hi - t_lo) / 2)
    tc = (0, 0, t_lo + tr[2])
    z.tag("hips")
    z.ball(1, loc=tc, colour=fur, scale=tr, rot=(-10, 0, 0), seg=14, rings=9)
    if big:  # gorilla: silver saddle, high crest, heavy shoulders
        z.ball(1, loc=(0, tr[1] * 0.3, tc[2] + tr[2] * 0.1), colour="light_grey", scale=(tr[0] * 1.03, tr[1] * 0.8, tr[2] * 0.8),
               seg=12, rings=8)
        z.tag("head")
        z.ball(hr * 0.8, loc=(0, hc[1] + hr * 0.2, hc[2] + hr * 0.75), colour=fur, scale=(0.7, 1, 0.8), seg=8, rings=5)
        z.tag("hips")
    # belly / chest skin on chimps and orangutans
    if "pale_face" in m or "long_arms" in m and not gibbon:
        z.ball(1, loc=(0, -tr[1] * 0.45, tc[2] - tr[2] * 0.1),
               colour="skin_4" if "long_arms" in m else "charcoal", scale=(tr[0] * 0.6, tr[1] * 0.6, tr[2] * 0.6),
               seg=10, rings=6)
    z.tag("neck")
    _limb(z, (0, tc[1], tc[2] + tr[2] * 0.6), (hc[0], hc[1], hc[2]), hr * 0.55, fur, seg=8)  # neck
    z.tag("head")
    z.ball(hr, loc=hc, colour=fur, seg=12, rings=8)
    _face(z, hc, hr, fur, m, ape=True)
    for s in (1, -1):
        z.tag("leg")
        # legs folded in front: thigh forward, shin down, flat foot
        hip = (s * tr[0] * 0.5, -tr[1] * 0.2, t_lo + tr[2] * 0.25)
        knee = (s * tr[0] * 0.75, -tr[1] * 1.15, t_lo + tr[2] * 0.45)
        _limb(z, hip, knee, tr[0] * 0.32, fur, r2=tr[0] * 0.24)
        _limb(z, knee, (s * tr[0] * 0.65, -tr[1] * 1.2, H * 0.03), tr[0] * 0.2, fur)
        z.box((tr[0] * 0.38, tr[1] * 0.8, H * 0.04), loc=(s * tr[0] * 0.65, -tr[1] * 1.45, H * 0.02),
              colour="black" if fur != "black" else "charcoal")
        # arms
        z.tag("arm")
        sh = (s * tr[0] * 0.95, -tr[1] * 0.1, tc[2] + tr[2] * 0.6)
        ar = tr[0] * (0.22 if big else 0.2)
        if gibbon:
            hand = (s * W * 0.2, hc[1] + hr * 0.3, H - ar)
            elbow = (s * W * 0.42, hc[1], (sh[2] + hand[2]) / 2)
        elif "long_arms" in m:  # orangutan: long arms reaching out wide
            hand = (s * W * 0.42, -tr[1] * 1.3, ar * 0.8)
            elbow = (s * W * 0.47, -tr[1] * 0.4, (sh[2] + hand[2]) / 2)
        else:
            hand = (s * tr[0] * 1.1, -tr[1] * 1.9, ar * 0.8)
            elbow = (s * tr[0] * 1.25, -tr[1] * 0.8, (sh[2] + hand[2]) * 0.5)
        _limb(z, sh, elbow, ar * 1.1, fur, r2=ar)
        _limb(z, elbow, hand, ar, fur, r2=ar * 0.85)
        if "long_arms" in m and not gibbon:  # shaggy hair hanging off the arms
            z.ball(ar * 1.3, loc=((sh[0] + elbow[0]) / 2, (sh[1] + elbow[1]) / 2, (sh[2] + elbow[2]) / 2 - ar),
                   colour=fur, scale=(0.8, 1, 1.6), seg=8, rings=5)
        z.ball(ar * 1.05, loc=hand, colour="black" if fur not in ("black", "charcoal") else "charcoal",
               scale=(1, 1.2, 0.8), seg=8, rings=5)


def _monkey(z, W, L, H, fur, m):
    """Monkey or lemur on all fours, tail behind (+Y)."""
    long_tail = bool(m & LONG_TAIL)
    bl = L * (0.42 if long_tail else 0.55)
    hr = H * (0.2 if "big_nose" not in m else 0.18)
    if "mane" in m:
        hr = H * 0.22
    leg_h = H * 0.3
    body_h = (H - leg_h) * 0.72
    by = -L / 2 + hr * 1.4 + bl / 2
    bz = leg_h + body_h / 2
    br = (W * 0.42, bl / 2, body_h / 2)
    limb = {"big_nose": "light_grey", "white_mask": "yellow"}.get(next(iter(m & {"big_nose", "white_mask"}), ""), fur)
    back = "grey" if "white_mask" in m else fur
    z.tag("hips")
    z.ball(1, loc=(0, by, bz), colour=fur, scale=br, rot=(-6, 0, 0), seg=14, rings=9)
    if back != fur:
        z.ball(1, loc=(0, by, bz + br[2] * 0.25), colour=back, scale=(br[0] * 0.85, br[1] * 0.95, br[2] * 0.8),
               seg=12, rings=7)
    if "big_nose" in m:  # pale rump and belly
        z.ball(1, loc=(0, by + br[1] * 0.5, bz - br[2] * 0.15), colour="light_grey",
               scale=(br[0] * 0.95, br[1] * 0.55, br[2] * 0.85), seg=10, rings=6)
    if "red_blue_face" in m:  # mandrill: blue and red rump
        z.ball(br[2] * 0.6, loc=(0, by + br[1] * 0.92, bz - br[2] * 0.1), colour="sky", scale=(1.2, 0.5, 1), seg=8,
               rings=5)
    lr = min(W, bl) * 0.12
    for s in (1, -1):
        for fy in (-0.6, 0.6):
            y = by + br[1] * fy
            x = s * br[0] * 0.65
            z.tag("leg_" + ("F" if fy < 0 else "B") + ("L" if s > 0 else "R"))
            _limb(z, (x, y, 0), (x, y, bz), lr, limb, r2=lr * 1.15, seg=7)
            z.ball(lr * 1.15, loc=(x, y - lr * 0.4, lr * 0.4), colour="black" if limb != "black" else "charcoal",
                   scale=(1, 1.4, 0.5), seg=6, rings=4)
    # head
    hc = (0, by - br[1] - hr * 0.55, H - hr)
    z.tag("neck")
    _limb(z, (0, by - br[1] * 0.7, bz + br[2] * 0.3), hc, hr * 0.55, fur, seg=8)
    z.tag("head")
    if "mane" in m:  # tamarin: big round golden mane around the face
        z.ball(hr * 1.35, loc=(hc[0], hc[1] + hr * 0.3, hc[2]), colour="gold", scale=(1, 0.75, 1), seg=12, rings=8)
    z.ball(hr, loc=hc, colour=fur, seg=12, rings=8)
    _face(z, hc, hr, fur, m, ape=False)
    # tail
    z.tag("tail")
    ty, tz = by + br[1] * 0.92, bz + br[2] * 0.2
    tr = br[2] * (0.32 if "ringed_tail" in m else 0.18)
    room = L / 2 - ty
    if not long_tail:  # macaque, mandrill: short stub
        _limb(z, (0, ty, tz), (0, ty + br[2] * 0.6, tz + br[2] * 0.2), br[2] * 0.15, fur, r2=br[2] * 0.08, seg=6)
        return
    n = 16
    pts = []
    for i in range(n + 1):
        t = i / n
        if "ringed_tail" in m:  # S-curve up, like a question mark
            pts.append((0, ty + room * (0.9 * t - 0.15 * t * t), tz + (H - tz - tr) * math.sin(t * math.pi * 0.6)))
        elif "prehensile_tail" in m:  # drooping, then a curl at the tip
            if t < 0.6:
                pts.append((0, ty + room * 0.75 * t / 0.6, tz - (tz - H * 0.25) * t / 0.6))
            else:
                u = (t - 0.6) / 0.4 * math.pi * 1.6
                cr = room * 0.17
                pts.append((0, ty + room * 0.75 + cr * math.sin(u), H * 0.25 + cr * (1 - math.cos(u))))
        else:  # long tail hanging in an arc
            pts.append((0, ty + room * t, tz - (tz - H * 0.08) * math.sin(t * math.pi / 2)))
    tail_col = "light_grey" if "big_nose" in m else fur
    for i in range(n):
        if "ringed_tail" in m:
            col = "black" if i % 2 else "white"
        elif "white_mask" in m and i >= n - 2:
            col = "black"  # squirrel monkey: black tail tip
        else:
            col = tail_col
        _limb(z, pts[i], pts[i + 1], tr * (1 - 0.3 * i / n), col, r2=tr * (1 - 0.3 * (i + 1) / n), seg=7)
