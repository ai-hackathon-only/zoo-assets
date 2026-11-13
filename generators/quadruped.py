"""Four-legged mammals (elephant, rhino, hippo, bears, canids, marsupials, small mammals).

size_m = [width, length nose-to-tail, height to top of head]. The animal faces -Y (DECISION in Plan & roles).
params:
  body: fur colour (palette name); belly: underside colour (default: body);
  leg: leg length / height (default from the height/length ratio);
  marks: features, any of
    head/face: trunk, tusks, big_ears, small_ears, round_ears, pointed_ears, fluffy_ears, horn1, horn2,
               wide_mouth, long_snout, blunt_snout, duck_bill, white_face, mask, face_stripes, face_rings,
               eye_rings, panda_patches
    body:      plates, patches, chest_v, chest_stripe, stripe_diag, quills, upright
    tail:      ringed_tail, bushy_tail, white_tail_tip, big_tail, flat_tail, long_tail
"""
import math

from mathutils import Vector

INK = {"black": "charcoal", "charcoal": "black"}  # dark marks on dark fur


def _limb(z, a, b, r, colour, r2=None, seg=7):
    """Tapered cylinder from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    e = d.normalized().to_track_quat("Z", "Y").to_euler()
    return z.cyl(r, d.length, loc=(a + b) / 2, colour=colour, rot=tuple(math.degrees(x) for x in e),
                 seg=seg, r2=r if r2 is None else r2)


def build(a, z):
    W, L, H = a["size_m"]
    p = a.get("params", {})
    m = set(p.get("marks", []))
    fur = p.get("body", "grey")
    belly = p.get("belly", fur)
    ink = INK.get(fur, "black")
    if "upright" in m:
        return _upright(z, W, L, H, fur, belly, ink, m)

    ratio = H / L
    leg_h = H * p.get("leg", min(0.48, max(0.22, 0.12 + 0.55 * ratio)))
    if "wide_mouth" in m:
        leg_h = H * 0.24
    elif "leg" in p:
        pass  # per-species leg length wins over the family default
    elif "round_ears" in m or "panda_patches" in m or "chest_v" in m or "face_rings" in m:
        leg_h = H * 0.3  # bears: short, thick legs
    big_head = "trunk" in m or "wide_mouth" in m
    body_l = L * (0.62 if "long_tail" not in m and "big_tail" not in m else 0.55)
    torso_h = (H - leg_h) * (0.78 if big_head else 0.62)
    bz = leg_h + torso_h / 2
    br = (W * 0.5, body_l / 2, torso_h / 2)
    by = -L * 0.02
    z.ball(1, loc=(0, by, bz), colour=fur, scale=br, seg=14, rings=9)
    z.joint("body", (0, by + br[1] * 0.8, bz), (0, by - br[1] * 0.8, bz))
    if belly != fur:
        z.ball(1, loc=(0, by, bz - br[2] * 0.3), colour=belly, scale=(br[0] * 0.85, br[1] * 0.85, br[2] * 0.72),
               seg=12, rings=7)

    # legs: front pair at -Y
    lr = min(W, body_l) * (0.17 if big_head or W > 1 else 0.11)
    leg_col = ink if "panda_patches" in m or "chest_v" in m else belly
    for x in (W * 0.27, -W * 0.27):
        for y in (by - br[1] * 0.55, by + br[1] * 0.55):
            top = bz - br[2] * 0.2
            leg = f"leg_{'F' if y < by else 'B'}{'L' if x > 0 else 'R'}"
            z.joint(leg, (x, y, top), (x, y, 0), "body")
            z.set_bone(leg)
            _limb(z, (x, y, 0), (x, y, top), lr * 0.9, leg_col, r2=lr)
            if W > 1:  # big toes on heavy animals
                z.ball(lr * 0.95, loc=(x, y - lr * 0.15, lr * 0.25), colour="light_grey" if fur != "light_grey"
                       else "grey", scale=(1, 1, 0.3), seg=8, rings=4)

    z.set_bone("body")

    # head
    hr = min(H - leg_h, body_l) * (0.3 if big_head else 0.33)
    if "wide_mouth" in m:
        hr = torso_h * 0.42
    hy = by - br[1] - hr * (0.25 if big_head else 0.8)
    hz = H - hr
    if "wide_mouth" in m:
        hz = bz + br[2] * 0.25
    neck_top = (0, hy + hr * 0.3, hz - hr * 0.2)
    neck_base = (0, by - br[1] * 0.6, bz + br[2] * 0.2)
    z.joint("neck", neck_base, neck_top, "body")
    z.joint("head", neck_top, (0, hy - hr * 1.2, hz), "neck")
    z.set_bone("neck")
    _limb(z, neck_base, neck_top, hr * 0.7, fur, seg=8)
    z.set_bone("head")
    face = "white" if ("panda_patches" in m or "face_stripes" in m) else fur
    if "white_face" in m:
        face = "cream"
    horned = "horn1" in m or "horn2" in m
    z.ball(hr, loc=(0, hy, hz), colour=face, scale=(0.9, 1.35, 0.85) if horned else (1, 1.05, 0.95), seg=12, rings=8)
    if horned:
        hy -= hr * 0.35
    front = hy - hr  # tip of the face sphere

    # snout
    sn_end = (0, front - hr * 0.35, hz - hr * 0.35)
    snout_col = fur if face == fur else face
    if "long_snout" in m:
        sn_end = (0, front - hr * 2.4, hz - hr * 0.8)
        _limb(z, (0, hy - hr * 0.5, hz - hr * 0.1), sn_end, hr * 0.42, fur, r2=hr * 0.12)
    elif "duck_bill" in m:
        z.box((hr * 1.3, hr * 1.4, hr * 0.25), loc=(0, front - hr * 0.55, hz - hr * 0.25), colour="black", taper=0.9)
        sn_end = None
    elif "wide_mouth" in m:
        z.box((hr * 1.7, hr * 1.3, hr * 1.1), loc=(0, front - hr * 0.35, hz - hr * 0.3), colour=fur, taper=0.85)
        z.box((hr * 1.6, hr * 1.2, hr * 0.12), loc=(0, front - hr * 0.42, hz - hr * 0.55), colour="pink")
        sn_end = (0, front - hr * 0.95, hz + hr * 0.1)
    elif "blunt_snout" in m:
        sw, sl = p.get("snout", (1.1, 0.8))  # width, length in head radii (capybara: long box, wombat: wide stub)
        z.box((hr * sw, hr * sl, hr * 0.9), loc=(0, front - hr * (sl * 0.5 - 0.3), hz - hr * 0.3), colour=fur, taper=0.9)
        sn_end = (0, front - hr * (sl - 0.3), hz - hr * 0.1)
    elif "trunk" not in m:
        snl = hr * (0.9 if "pointed_ears" in m or "white_tail_tip" in m or "big_ears" in m else 0.55)
        sn_end = (0, front - snl, hz - hr * 0.35)
        snc = "cream" if "face_rings" in m or "chest_v" in m else snout_col
        _limb(z, (0, hy - hr * 0.4, hz - hr * 0.25), sn_end, hr * 0.45, snc, r2=hr * 0.28)
    if sn_end and "trunk" not in m:
        z.ball(hr * 0.16, loc=(sn_end[0], sn_end[1] - hr * 0.02, sn_end[2] + hr * 0.05), colour="black",
               seg=6, rings=4)

    if "trunk" in m:
        pts = [(0, front + hr * 0.15, hz - hr * 0.1), (0, front - hr * 0.35, hz - hr * 0.9),
               (0, front - hr * 0.45, hz - hr * 1.9), (0, front - hr * 0.75, max(hz - hr * 2.7, hr * 0.3))]
        rs = [hr * 0.38, hr * 0.3, hr * 0.24, hr * 0.18]
        for i in range(3):
            _limb(z, pts[i], pts[i + 1], rs[i], fur, r2=rs[i + 1], seg=8)
    if "tusks" in m:
        for s in (1, -1):
            _limb(z, (s * hr * 0.35, front + hr * 0.1, hz - hr * 0.6),
                  (s * hr * 0.45, front - hr * 0.9, hz - hr * 0.75), hr * 0.12, "cream", r2=hr * 0.02, seg=6)
    if "horn2" in m or "horn1" in m:
        hb = (0, front - hr * 0.2, hz + hr * 0.15)
        _limb(z, hb, (0, hb[1] - hr * 0.35, hb[2] + hr * 1.5), hr * 0.3, "cream", r2=0.0, seg=7)
        if "horn2" in m:
            _limb(z, (0, front + hr * 0.4, hz + hr * 0.5), (0, front + hr * 0.3, hz + hr * 1.0), hr * 0.16,
                  "cream", r2=0.0, seg=7)

    # eyes and face marks
    ey, ez, ex = hy - hr * 0.75, hz + hr * 0.2, hr * 0.42
    for s in (1, -1):
        if "panda_patches" in m or "eye_rings" in m or "mask" in m:
            z.ball(hr * 0.26, loc=(s * ex, ey + hr * 0.08, ez), colour="black", scale=(1, 0.5, 0.8), seg=8, rings=5)
        if "face_rings" in m:
            z.ball(hr * 0.36, loc=(s * ex, ey - hr * 0.02, ez + hr * 0.05), colour="cream", scale=(1, 0.45, 1.1),
                   seg=8, rings=5)
        if "face_stripes" in m:
            _limb(z, (s * hr * 0.3, hy - hr * 0.9, hz), (s * hr * 0.45, hy + hr * 0.7, hz + hr * 0.6),
                  hr * 0.17, "black", seg=6)
        eye_col = "white" if fur in ("black", "charcoal") and "panda_patches" not in m else "black"
        z.ball(hr * 0.1, loc=(s * ex, ey - hr * 0.08, ez), colour=eye_col, seg=6, rings=4)
    if "mask" in m:
        z.box((hr * 1.4, hr * 0.2, hr * 0.3), loc=(0, ey + hr * 0.05, ez), colour="black")

    # ears
    for s in (1, -1):
        ex2, ez2 = s * hr * 0.6, hz + hr * 0.7
        if "big_ears" in m and "trunk" in m:
            z.ball(hr * 1.3, loc=(s * hr * 1.15, hy + hr * 0.2, hz - hr * 0.2), colour=fur, scale=(0.15, 0.8, 1.0),
                   rot=(0, 0, s * 20), seg=10, rings=6)
        elif "small_ears" in m:
            z.ball(hr * 0.6, loc=(s * hr * 0.9, hy + hr * 0.3, hz), colour=fur, scale=(0.15, 0.7, 0.9), seg=8, rings=5)
        elif "big_ears" in m or "pointed_ears" in m:
            sz = 0.85 if "big_ears" in m else 0.55
            ec = ink if "patches" in m else fur
            _limb(z, (ex2, hy + hr * 0.15, hz + hr * 0.5), (s * hr * (0.7 + sz * 0.4), hy + hr * 0.2, hz + hr * (0.6 + sz)),
                  hr * sz * 0.4, ec, r2=0.0, seg=5)
        elif "fluffy_ears" in m:
            z.ball(hr * 0.45, loc=(s * hr * 0.85, hy + hr * 0.2, ez2), colour="light_grey", scale=(1, 0.5, 1), seg=8, rings=5)
        elif "wide_mouth" in m or "horn1" in m or "horn2" in m:
            z.ball(hr * 0.2, loc=(s * hr * 0.5, hy + hr * 0.5, hz + hr * 0.85), colour=fur, scale=(0.8, 0.6, 1.4),
                   seg=6, rings=4)
        elif "duck_bill" in m or "flat_tail" in m:
            pass  # platypus, beaver: ears hidden in fur
        else:  # round_ears and default
            ec = "black" if "panda_patches" in m else ("white" if "white_face" in m else fur)
            z.ball(hr * 0.28, loc=(ex2, hy + hr * 0.2, ez2), colour=ec, scale=(1, 0.55, 1), seg=8, rings=5)

    z.set_bone("body")

    # body marks
    if "panda_patches" in m:
        z.ball(1, loc=(0, by - br[1] * 0.3, bz + br[2] * 0.05), colour="black",
               scale=(br[0] * 1.04, br[1] * 0.28, br[2] * 1.04), seg=14, rings=8)
    if "chest_v" in m or "chest_stripe" in m:
        col = "cream" if "chest_v" in m else "white"
        for s in (1, -1):
            _limb(z, (s * br[0] * 0.55, by - br[1] * 0.72, bz + br[2] * 0.45), (0, by - br[1] * 0.98, bz - br[2] * 0.1),
                  br[2] * (0.22 if "chest_v" in m else 0.12), col, seg=6)
    if "stripe_diag" in m:
        for s in (1, -1):
            _limb(z, (s * br[0] * 0.9, by - br[1] * 0.45, bz - br[2] * 0.5), (s * br[0] * 0.5, by + br[1] * 0.35,
                  bz + br[2] * 0.75), br[2] * 0.18, "black", seg=6)
            _limb(z, (s * br[0] * 0.95, by - br[1] * 0.6, bz - br[2] * 0.45), (s * br[0] * 0.55, by + br[1] * 0.15,
                  bz + br[2] * 0.85), br[2] * 0.1, "white", seg=6)
    if "plates" in m:
        for y in (-0.35, 0.25):
            z.ball(1, loc=(0, by + br[1] * y, bz + br[2] * 0.05), colour="charcoal",
                   scale=(br[0] * 1.03, br[1] * 0.06, br[2] * 1.03), seg=14, rings=8)
    if "patches" in m:
        for i in range(10):
            u = (i * 137.5) % 360
            v = -0.6 + (i * 0.37) % 1.2
            cu, cv = math.radians(u), v
            c = (br[0] * math.cos(cv) * math.sin(cu), by + br[1] * math.sin(cv), bz + br[2] * math.cos(cv) * math.cos(cu))
            if c[2] < bz - br[2] * 0.4:
                continue
            z.ball(br[2] * 0.3, loc=c, colour="black" if i % 2 else "cream", scale=(1, 1.3, 0.4), seg=7, rings=3,
                   rot=(0, math.degrees(math.sin(cu)) * 50, 0))
    if "quills" in m:
        for i in range(36):
            u = math.radians(-80 + (i * 47) % 160)
            v = -0.5 + (i * 0.29) % 1.2
            c = Vector((br[0] * math.cos(v) * math.sin(u), by + br[1] * math.sin(v), bz + br[2] * math.cos(v) * math.cos(u)))
            n = Vector((math.sin(u), 0.6, math.cos(u))).normalized()
            _limb(z, c, c + n * H * 0.28, H * 0.035, "white" if i % 3 == 0 else "black", r2=0.0, seg=4)

    # tail (behind, +Y)
    ty, tz = by + br[1] * 0.9, bz + br[2] * 0.2
    tail_room = L / 2 - ty
    z.joint("tail", (0, ty, tz), (0, ty + max(tail_room, br[1] * 0.3), tz - br[2] * 0.3), "body")
    z.set_bone("tail")
    if "big_tail" in m or "long_tail" in m:
        _limb(z, (0, ty, tz), (0, L / 2, br[2] * 0.4), br[2] * 0.45, fur, r2=br[2] * 0.08)
    elif "flat_tail" in m:
        col = "black" if "duck_bill" not in m else fur
        z.box((W * 0.6, tail_room * 1.2, br[2] * 0.18), loc=(0, ty + tail_room * 0.45, br[2] * 0.25), colour=col,
              rot=(-8, 0, 0))
    elif "ringed_tail" in m:
        ring = "black" if fur == "grey" else "cream"
        n = 6
        for i in range(n):
            a0 = Vector((0, ty + tail_room * i / n, tz + br[2] * 0.6 * i / n))
            a1 = Vector((0, ty + tail_room * (i + 1) / n, tz + br[2] * 0.6 * (i + 1) / n))
            _limb(z, a0, a1, br[2] * 0.32, ring if i % 2 else fur, r2=br[2] * 0.3, seg=8)
    elif "bushy_tail" in m or "white_tail_tip" in m:
        z.ball(1, loc=(0, ty + tail_room * 0.5, tz - br[2] * 0.2), colour=fur,
               scale=(br[2] * 0.4, tail_room * 0.55, br[2] * 0.4), rot=(25, 0, 0), seg=10, rings=6)
        if "white_tail_tip" in m:
            z.ball(br[2] * 0.33, loc=(0, ty + tail_room * 0.98, tz - br[2] * 0.6), colour="white", seg=8, rings=5)
    elif "stripe_diag" in m:  # anteater: big flag tail
        z.ball(1, loc=(0, ty + tail_room * 0.5, tz + br[2] * 0.1), colour=fur,
               scale=(br[0] * 0.25, tail_room * 0.55, br[2] * 0.9), seg=10, rings=6)
    elif "quills" in m or "round_ears" in m or "panda_patches" in m or "wide_mouth" in m or "blunt_snout" in m:
        z.ball(br[2] * 0.15, loc=(0, ty + br[1] * 0.08, tz), colour=fur, seg=6, rings=4)  # stub tail
    else:
        tl = max(tail_room, br[1] * 0.4)
        _limb(z, (0, ty, tz), (0, ty + tl * 0.8, tz - tl * 0.6), br[2] * 0.08, fur, r2=br[2] * 0.05, seg=6)
        if "trunk" in m or "horn1" in m or "horn2" in m:
            z.ball(br[2] * 0.1, loc=(0, ty + tl * 0.8, tz - tl * 0.6), colour="black", scale=(1, 1, 1.6), seg=6, rings=4)


def _upright(z, W, L, H, fur, belly, ink, m):
    """Sitting or standing on hind legs: meerkat, koala, kangaroo."""
    roo = "big_tail" in m
    koala = "fluffy_ears" in m
    hr = H * (0.13 if roo else 0.22 if koala else 0.12)
    torso_h = H * (0.5 if roo else 0.48 if koala else 0.58)
    tz0 = H * (0.15 if roo else 0.08)
    tr = (W * 0.45 if not roo else W * 0.4, W * (0.45 if not roo else 0.5), torso_h / 2)
    tc = (0, 0, tz0 + tr[2])
    z.joint("body", (0, 0, tz0), (0, 0, tz0 + torso_h), "root")
    z.ball(1, loc=tc, colour=fur, scale=tr, rot=(-15 if roo else 0, 0, 0), seg=12, rings=8)
    z.ball(1, loc=(0, tc[1] - tr[1] * 0.3, tc[2] - tr[2] * 0.05), colour="cream" if fur != "grey" else "white",
           scale=(tr[0] * 0.7, tr[1] * 0.75, tr[2] * 0.8), seg=10, rings=6)
    # hind legs / feet
    for s in (1, -1):
        if roo:
            _limb(z, (s * tr[0] * 0.6, tr[1] * 0.2, tz0 + tr[2] * 0.6), (s * tr[0] * 0.6, -tr[1] * 0.1, H * 0.08),
                  tr[0] * 0.42, fur, r2=tr[0] * 0.22)
            z.box((tr[0] * 0.35, L * 0.32, H * 0.05), loc=(s * tr[0] * 0.6, -L * 0.1, H * 0.025), colour=fur)
        else:
            z.ball(tr[0] * 0.45, loc=(s * tr[0] * 0.55, -tr[1] * 0.3, tr[0] * 0.3), colour=fur,
                   scale=(0.9, 1.4, 0.7), seg=8, rings=5)
        # arms
        sh = (s * tr[0] * 0.75, -tr[1] * 0.4, tc[2] + tr[2] * 0.5)
        _limb(z, sh, (s * tr[0] * 0.45, -tr[1] * 1.1, tc[2] + tr[2] * (0.0 if not koala else 0.2)),
              tr[0] * (0.16 if not koala else 0.25), fur if not ("eye_rings" in m) else ink, seg=6)
    # head
    hz = tz0 + torso_h + hr * 0.75
    hy = -tr[1] * (0.25 if not roo else 0.45)
    z.joint("head", (0, hy, hz - hr * 0.8), (0, hy - hr * 1.2, hz - hr * 0.8), "body")
    z.set_bone("head")
    z.ball(hr, loc=(0, hy, hz), colour=fur, scale=(1, 1.05, 1), seg=12, rings=8)
    if koala:
        z.ball(hr * 0.3, loc=(0, hy - hr * 0.95, hz - hr * 0.1), colour="black", scale=(0.7, 0.5, 1.0), seg=8, rings=5)
    else:
        sl = hr * (1.5 if roo else 1.0)
        end = (0, hy - hr * 0.6 - sl, hz - hr * 0.2)
        _limb(z, (0, hy - hr * 0.5, hz), end, hr * 0.45, fur, r2=hr * 0.2)
        z.ball(hr * 0.13, loc=end, colour="black", seg=6, rings=4)
    for s in (1, -1):
        ex, ey, ez = s * hr * 0.4, hy - hr * 0.8, hz + hr * 0.2
        if "eye_rings" in m:
            z.ball(hr * 0.3, loc=(ex, ey + hr * 0.08, ez), colour="black", scale=(1, 0.5, 0.9), seg=8, rings=5)
        z.ball(hr * 0.1, loc=(ex, ey - hr * 0.05, ez), colour="black" if "eye_rings" not in m else "white", seg=6, rings=4)
        if koala:
            z.ball(hr * 0.55, loc=(s * hr * 1.0, hy + hr * 0.1, hz + hr * 0.55), colour="light_grey", scale=(1, 0.45, 1),
                   seg=8, rings=5)
            z.ball(hr * 0.35, loc=(s * hr * 0.98, hy - hr * 0.03, hz + hr * 0.55), colour="white", scale=(1, 0.3, 1),
                   seg=8, rings=5)
        elif roo:
            _limb(z, (s * hr * 0.4, hy + hr * 0.1, hz + hr * 0.6), (s * hr * 0.6, hy + hr * 0.2, hz + hr * 2.0),
                  hr * 0.35, fur, r2=0.0, seg=5)
        else:
            z.ball(hr * 0.2, loc=(s * hr * 0.85, hy + hr * 0.1, hz + hr * 0.2), colour=ink, scale=(0.5, 0.6, 1), seg=6, rings=4)
    # tail behind (+Y)
    z.set_bone("tail")
    z.joint("tail", (0, tr[1] * 0.6, tz0 + tr[2] * 0.3), (0, L * 0.5, H * 0.03), "body")
    if roo:
        _limb(z, (0, tr[1] * 0.6, tz0 + tr[2] * 0.4), (0, L / 2, H * 0.03), tr[0] * 0.5, fur, r2=tr[0] * 0.12)
    elif not koala:
        _limb(z, (0, tr[1] * 0.7, tz0 + tr[2] * 0.2), (0, L * 0.85 - tr[1], H * 0.02), tr[0] * 0.25, fur,
              r2=tr[0] * 0.05, seg=6)
        z.ball(tr[0] * 0.12, loc=(0, L * 0.85 - tr[1], H * 0.03), colour="black", seg=6, rings=4)
