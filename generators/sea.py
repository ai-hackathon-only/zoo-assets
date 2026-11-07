"""Sea animals: whales and dolphins, sharks and fish, seals and their kin, an octopus, a jellyfish, a sea otter.

size_m = [width, length, height]. The animal faces -Y (DECISION in Plan & roles); swimmers rest their
belly on the floor so the origin stays at floor centre. One builder per asset id, all sized from size_m.
"""
from generators.quadruped import _limb


def build(a, z):
    W, L, H = a["size_m"]
    body = a.get("params", {}).get("body", "grey")
    BUILDERS[a["id"]](z, W, L, H, body)


def _fin(z, base, length, height, loc, colour, rot=(0, 0, 0), thick=None):
    """Upright wedge fin: base along Y, tip at +Z before rotation."""
    z.box((thick or base * 0.18, base, height), loc=loc, colour=colour, rot=rot, taper=0.12)


def _eyes(z, x, y, h, r, white=False):
    for s in (1, -1):
        if white:
            z.ball(r * 1.6, loc=(s * x, y, h), colour="white", scale=(0.5, 1, 1), seg=8, rings=5)
        z.ball(r, loc=(s * (x + r * 0.3), y, h), colour="black", seg=6, rings=4)


def _flukes(z, y, h, span, colour):
    """Horizontal tail flukes (whales, dolphins, manatee use their own)."""
    for s in (1, -1):
        z.ball(1, loc=(s * span * 0.26, y, h + s * span * 0.012), colour=colour, scale=(span * 0.28, span * 0.12, span * 0.03),
               rot=(0, 0, s * 28), seg=10, rings=5)


def _cetacean(z, W, L, H, top, belly, orca=False):
    rz = H * (0.3 if orca else 0.34)
    cz = rz
    z.ball(1, loc=(0, -L * 0.04, cz), colour=top, scale=(W * 0.3, L * 0.36, rz), seg=16, rings=10)
    z.ball(1, loc=(0, -L * 0.1, cz - rz * 0.32), colour=belly, scale=(W * 0.26, L * 0.3, rz * 0.78), seg=14, rings=8)
    # tail stock and flukes
    _limb(z, (0, L * 0.2, cz + rz * 0.1), (0, L * 0.43, cz + rz * 0.05), rz * 0.55, top, r2=rz * 0.18, seg=10)
    _flukes(z, L * 0.45, cz + rz * 0.05, W * 1.0, top)
    if orca:  # rounded head, white eye patch, tall straight fin
        z.ball(1, loc=(0, -L * 0.36, cz - rz * 0.05), colour=top, scale=(W * 0.24, L * 0.14, rz * 0.82), seg=12, rings=8)
        for s in (1, -1):
            z.ball(1, loc=(s * W * 0.2, -L * 0.33, cz + rz * 0.35), colour="white", scale=(W * 0.07, L * 0.06, rz * 0.2),
                   seg=8, rings=5)
        z.ball(1, loc=(0, L * 0.06, cz + rz * 0.6), colour="grey", scale=(W * 0.18, L * 0.08, rz * 0.4), seg=8, rings=5)
        _fin(z, L * 0.14, 0, H - cz - rz * 0.8, (0, L * 0.02, (H + cz + rz * 0.8) / 2 + H * 0.02), top,
             rot=(-6, 0, 0), thick=W * 0.06)
        _eyes(z, W * 0.2, -L * 0.37, cz + rz * 0.15, rz * 0.08)
    else:  # dolphin: melon forehead, long beak, curved fin
        z.ball(1, loc=(0, -L * 0.34, cz + rz * 0.1), colour=top, scale=(W * 0.22, L * 0.1, rz * 0.7), seg=12, rings=8)
        z.ball(1, loc=(0, -L * 0.45, cz - rz * 0.2), colour="light_grey", scale=(W * 0.08, L * 0.06, rz * 0.2),
               seg=8, rings=5)
        _fin(z, L * 0.15, 0, H - cz - rz * 0.8, (0, L * 0.06, (H + cz + rz * 0.8) / 2), top, rot=(-25, 0, 0),
             thick=W * 0.05)
        _eyes(z, W * 0.19, -L * 0.37, cz + rz * 0.05, rz * 0.08)
    for s in (1, -1):  # pectoral flippers
        z.ball(1, loc=(s * W * 0.3, -L * 0.2, cz - rz * 0.4), colour=top, scale=(W * 0.16, L * 0.05, rz * 0.08),
               rot=(0, s * 20, s * -30), seg=8, rings=5)


def dolphin(z, W, L, H, body):
    _cetacean(z, W, L, H, body, "light_grey")


def orca(z, W, L, H, body):
    _cetacean(z, W, L, H, body, "white", orca=True)


def shark(z, W, L, H, body):
    rz = H * 0.26
    cz = rz
    z.ball(1, loc=(0, -L * 0.06, cz), colour=body, scale=(W * 0.3, L * 0.34, rz), seg=16, rings=10)
    z.ball(1, loc=(0, -L * 0.1, cz - rz * 0.38), colour="white", scale=(W * 0.27, L * 0.3, rz * 0.72), seg=14, rings=8)
    z.cone(rz * 0.75, L * 0.14, loc=(0, -L * 0.42, cz - rz * 0.05), colour=body, rot=(90, 0, 0), seg=12)
    # gill slits
    for i in range(4):
        for s in (1, -1):
            z.box((W * 0.02, L * 0.006, rz * 0.7), loc=(s * W * 0.285, -L * (0.24 - i * 0.025), cz), colour="charcoal")
    _eyes(z, W * 0.17, -L * 0.38, cz + rz * 0.2, rz * 0.08)
    # mouth line
    z.box((W * 0.3, L * 0.03, rz * 0.06), loc=(0, -L * 0.38, cz - rz * 0.55), colour="charcoal")
    # tall triangular dorsal fin, pectorals, tail stock and crescent tail
    _fin(z, L * 0.13, 0, H * 0.48, (0, -L * 0.04, cz + rz * 0.8 + H * 0.2), body, rot=(-15, 0, 0), thick=W * 0.06)
    for s in (1, -1):
        _fin(z, L * 0.1, 0, W * 0.4, (s * W * 0.38, -L * 0.15, cz - rz * 0.45), body, rot=(0, s * 70, 0), thick=rz * 0.1)
    _limb(z, (0, L * 0.18, cz + rz * 0.1), (0, L * 0.4, cz + rz * 0.2), rz * 0.55, body, r2=rz * 0.2, seg=10)
    _fin(z, L * 0.08, 0, H * 0.55, (0, L * 0.44, cz + H * 0.3), body, rot=(-35, 0, 0), thick=W * 0.05)
    _fin(z, L * 0.07, 0, H * 0.3, (0, L * 0.44, max(cz - H * 0.1, H * 0.12)), body, rot=(-145, 0, 0), thick=W * 0.05)


def manta(z, W, L, H, body):
    cz = H * 0.3
    z.ball(1, loc=(0, 0, cz), colour=body, scale=(W * 0.2, L * 0.25, H * 0.3), seg=14, rings=8)
    z.ball(1, loc=(0, 0, cz - H * 0.11), colour="white", scale=(W * 0.17, L * 0.21, H * 0.22), seg=12, rings=6)
    for s in (1, -1):  # wings: flat, swept back toward the tips
        z.ball(1, loc=(s * W * 0.25, L * 0.02, cz + H * (0.05 + s * 0.02)), colour=body, scale=(W * 0.26, L * 0.16, H * 0.07),
               rot=(0, s * -8, s * 18), seg=12, rings=6)
        z.box((W * 0.18, L * 0.05, H * 0.05), loc=(s * W * 0.42, L * 0.07, cz + H * 0.12), colour=body,
              rot=(0, s * -12, s * 30))
        # cephalic fins (horn-like lobes at the mouth)
        z.ball(1, loc=(s * W * 0.07, -L * 0.3, cz + H * 0.02), colour=body, scale=(W * 0.025, L * 0.08, H * 0.12),
               rot=(25, 0, 0), seg=8, rings=5)
        z.ball(1, loc=(s * W * 0.17, -L * 0.04, cz + H * 0.5), colour="white", scale=(W * 0.04, L * 0.06, H * 0.05),
               seg=8, rings=4)
    z.box((W * 0.14, L * 0.04, H * 0.08), loc=(0, -L * 0.25, cz - H * 0.05), colour="black")  # wide mouth
    _eyes(z, W * 0.1, -L * 0.24, cz + H * 0.2, H * 0.05)
    _limb(z, (0, L * 0.2, cz), (0, L * 0.5, cz + H * 0.05), H * 0.06, body, r2=H * 0.015)


def _fish(z, W, L, H, body, deep):
    """Side-flat fish standing upright on its belly fin. Returns body centre z and half-height."""
    rz = H * (0.42 if deep else 0.36)
    cz = H * 0.5
    z.ball(1, loc=(0, -L * 0.08, cz), colour=body, scale=(W * 0.45, L * 0.36, rz), seg=14, rings=9)
    return cz, rz


def clownfish(z, W, L, H, body):
    cz, rz = _fish(z, W, L, H, body, False)
    for y, w in ((-L * 0.3, 0.75), (-L * 0.07, 1.0), (L * 0.18, 0.55)):  # three white bands, black edges
        z.ball(1, loc=(0, y, cz), colour="black", scale=(W * 0.47, L * 0.055, rz * w * 1.02), seg=12, rings=7)
        z.ball(1, loc=(0, y, cz), colour="white", scale=(W * 0.48, L * 0.035, rz * w), seg=12, rings=7)
    _eyes(z, W * 0.28, -L * 0.36, cz + rz * 0.2, rz * 0.13, white=True)
    _fin(z, L * 0.3, 0, H * 0.22, (0, -L * 0.05, cz + rz + H * 0.08), body, thick=W * 0.12)
    z.ball(1, loc=(0, L * 0.38, cz), colour=body, scale=(W * 0.12, L * 0.12, rz * 0.8), seg=10, rings=6)
    z.box((W * 0.13, L * 0.02, rz * 1.4), loc=(0, L * 0.47, cz), colour="black")
    for s in (1, -1):
        z.ball(1, loc=(s * W * 0.45, -L * 0.12, cz - rz * 0.3), colour=body, scale=(W * 0.08, L * 0.08, rz * 0.3),
               rot=(30, 0, 0), seg=8, rings=5)
    z.box((W * 0.1, L * 0.2, H * 0.12), loc=(0, -L * 0.05, H * 0.06), colour=body, taper=1.6)


def blue_tang(z, W, L, H, body):
    cz, rz = _fish(z, W, L, H, "water", True)
    # dark "palette" mark along both sides
    z.ball(1, loc=(0, -L * 0.02, cz + rz * 0.25), colour=body, scale=(W * 0.48, L * 0.26, rz * 0.4),
           rot=(8, 0, 0), seg=12, rings=6)
    z.ball(1, loc=(0, L * 0.08, cz - rz * 0.05), colour=body, scale=(W * 0.49, L * 0.14, rz * 0.4),
           rot=(-30, 0, 0), seg=10, rings=6)
    _eyes(z, W * 0.24, -L * 0.33, cz + rz * 0.25, rz * 0.1, white=False)
    _fin(z, L * 0.5, 0, H * 0.12, (0, -L * 0.02, cz + rz + H * 0.03), body, thick=W * 0.12)
    _fin(z, L * 0.4, 0, H * 0.12, (0, L * 0.02, cz - rz - H * 0.02), body, rot=(180, 0, 0), thick=W * 0.12)
    # yellow tail with a forked edge
    z.ball(1, loc=(0, L * 0.34, cz), colour="yellow", scale=(W * 0.12, L * 0.08, rz * 0.35), seg=8, rings=5)
    for s in (1, -1):
        z.ball(1, loc=(0, L * 0.43, cz + s * rz * 0.3), colour="yellow", scale=(W * 0.08, L * 0.07, rz * 0.35),
               rot=(s * 35, 0, 0), seg=8, rings=5)
    z.ball(1, loc=(0, -L * 0.42, cz - rz * 0.1), colour="water", scale=(W * 0.2, L * 0.04, rz * 0.12), seg=8, rings=4)


def moray(z, W, L, H, body):
    """Long eel in an S curve, head raised with the mouth open."""
    r = H * 0.22
    pts = [(0, L * 0.48, r * 0.7), (W * 0.35, L * 0.3, r), (-W * 0.3, L * 0.05, r), (W * 0.2, -L * 0.18, r * 1.1),
           (0, -L * 0.32, H * 0.6)]
    for i in range(len(pts) - 1):
        r0, r1 = (r * (0.55 + 0.45 * k / (len(pts) - 1)) for k in (i, i + 1))
        _limb(z, pts[i], pts[i + 1], r0, body, r2=r1, seg=10)
        z.ball(r1 * 1.15, loc=pts[i + 1], colour=body, seg=10, rings=6)
    _fin(z, L * 0.5, 0, H * 0.14, (W * 0.05, L * 0.12, r * 1.7), body, thick=W * 0.06)  # long back fin ridge
    hx, hy, hz = pts[-1]
    z.ball(1, loc=(hx, hy - L * 0.06, hz + r * 0.25), colour=body, scale=(r * 0.95, L * 0.09, r * 0.6), seg=10, rings=6)
    z.ball(1, loc=(hx, hy - L * 0.06, hz - r * 0.75), colour=body, scale=(r * 0.85, L * 0.08, r * 0.35),
           rot=(-25, 0, 0), seg=10, rings=6)
    z.ball(1, loc=(hx, hy - L * 0.05, hz - r * 0.25), colour="maroon", scale=(r * 0.7, L * 0.07, r * 0.4), seg=8, rings=5)
    for s in (1, -1):  # teeth
        z.cone(r * 0.08, r * 0.25, loc=(hx + s * r * 0.4, hy - L * 0.11, hz), colour="white", rot=(180, 0, 0), seg=4)
    _eyes(z, r * 0.55, hy - L * 0.08, hz + r * 0.6, r * 0.14, white=True)


def sea_lion(z, W, L, H, body):
    """Propped up on its front flippers, head held high."""
    z.ball(1, loc=(0, L * 0.12, H * 0.16), colour=body, scale=(W * 0.4, L * 0.34, H * 0.16), seg=14, rings=8)
    _limb(z, (0, L * 0.05, H * 0.2), (0, -L * 0.22, H * 0.6), W * 0.34, body, r2=W * 0.22, seg=12)
    z.ball(W * 0.34, loc=(0, L * 0.02, H * 0.25), colour=body, seg=12, rings=8)
    hc = (0, -L * 0.27, H * 0.82)
    z.ball(1, loc=hc, colour=body, scale=(W * 0.2, W * 0.25, H * 0.15), rot=(-15, 0, 0), seg=12, rings=8)
    z.ball(1, loc=(0, hc[1] - W * 0.27, hc[2] - H * 0.04), colour="dark_brown", scale=(W * 0.12, W * 0.14, H * 0.07),
           seg=10, rings=6)
    z.ball(W * 0.035, loc=(0, hc[1] - W * 0.4, hc[2] - H * 0.02), colour="black", seg=6, rings=4)
    _eyes(z, W * 0.12, hc[1] - W * 0.18, hc[2] + H * 0.05, W * 0.035)
    for s in (1, -1):
        z.ball(W * 0.03, loc=(s * W * 0.18, hc[1], hc[2] + H * 0.04), colour="dark_brown", scale=(1, 1, 1.6),
               seg=6, rings=4)
        for k in (0, 1):  # whiskers
            z.box((W * 0.18, W * 0.01, W * 0.01), loc=(s * W * 0.15, hc[1] - W * 0.35, hc[2] - H * (0.04 + k * 0.025)),
                  colour="cream", rot=(0, 0, s * (10 - k * 20)))
        # front flippers planted wide, hind flippers splayed forward under the hips
        _limb(z, (s * W * 0.2, -L * 0.12, H * 0.38), (s * W * 0.42, -L * 0.22, H * 0.03), W * 0.11, body, r2=W * 0.08)
        z.ball(1, loc=(s * W * 0.44, -L * 0.28, H * 0.03), colour="dark_brown", scale=(W * 0.08, L * 0.07, H * 0.03),
               seg=8, rings=5)
        z.ball(1, loc=(s * W * 0.16, L * 0.43, H * 0.04), colour="dark_brown", scale=(W * 0.1, L * 0.08, H * 0.03),
               rot=(0, 0, s * 25), seg=8, rings=5)


def _seal_body(z, W, L, H, body, rz):
    z.ball(1, loc=(0, 0, rz), colour=body, scale=(W * 0.45, L * 0.38, rz), seg=16, rings=9)
    for s in (1, -1):
        z.ball(1, loc=(s * W * 0.12, L * 0.4, rz * 0.4), colour=body, scale=(W * 0.12, L * 0.08, rz * 0.2),
               rot=(0, 0, s * 25), seg=8, rings=5)


def seal(z, W, L, H, body):
    rz = H * 0.42
    _seal_body(z, W, L, H, body, rz)
    hc = (0, -L * 0.36, H * 0.72)
    _limb(z, (0, -L * 0.22, rz), hc, W * 0.32, body, r2=W * 0.28, seg=12)
    z.ball(W * 0.3, loc=hc, colour=body, seg=12, rings=8)
    z.ball(1, loc=(0, hc[1] - W * 0.28, hc[2] - W * 0.05), colour=body, scale=(W * 0.16, W * 0.12, W * 0.12),
           seg=10, rings=6)
    z.ball(W * 0.04, loc=(0, hc[1] - W * 0.4, hc[2]), colour="black", seg=6, rings=4)
    _eyes(z, W * 0.13, hc[1] - W * 0.22, hc[2] + W * 0.1, W * 0.06)
    spots = [(0.2, -0.1), (-0.25, 0.05), (0.1, 0.2), (-0.1, -0.15), (0.3, 0.1), (-0.3, 0.25), (0.0, 0.0),
             (0.15, -0.25), (-0.15, 0.3)]
    for x, y in spots:
        z.ball(W * 0.05, loc=(x * W, y * L, rz * 1.93 - abs(x) * W * 0.5), colour="charcoal", scale=(1, 1, 0.4),
               seg=6, rings=4)
    for s in (1, -1):
        z.ball(1, loc=(s * W * 0.38, -L * 0.15, rz * 0.45), colour=body, scale=(W * 0.12, L * 0.07, rz * 0.12),
               rot=(0, 0, s * -30), seg=8, rings=5)


def walrus(z, W, L, H, body):
    rz = H * 0.36
    _seal_body(z, W, L, H, body, rz)
    hc = (0, -L * 0.3, H * 0.62)
    z.ball(1, loc=(0, -L * 0.16, H * 0.4), colour=body, scale=(W * 0.42, L * 0.18, H * 0.3), seg=14, rings=8)
    z.ball(1, loc=hc, colour=body, scale=(W * 0.24, W * 0.22, H * 0.2), seg=12, rings=8)
    for s in (1, -1):  # whisker pads, tusks, eyes, flippers
        z.ball(1, loc=(s * W * 0.09, hc[1] - W * 0.18, hc[2] - H * 0.07), colour="sand", scale=(W * 0.1, W * 0.08, H * 0.08),
               seg=10, rings=6)
        z.cone(W * 0.035, H * 0.38, loc=(s * W * 0.07, hc[1] - W * 0.22, hc[2] - H * 0.3), colour="white",
               rot=(170, 0, 0), seg=6)
        for k in range(3):
            z.box((W * 0.002 + W * 0.008, W * 0.08, W * 0.008),
                  loc=(s * W * (0.08 + k * 0.03), hc[1] - W * 0.27, hc[2] - H * (0.04 + k * 0.03)), colour="cream")
        z.ball(1, loc=(s * W * 0.38, -L * 0.18, rz * 0.4), colour="brown", scale=(W * 0.12, L * 0.07, rz * 0.12),
               rot=(0, 0, s * -30), seg=8, rings=5)
        z.ball(1, loc=(s * W * 0.18, -L * 0.18, H * 0.48), colour="pink", scale=(W * 0.12, L * 0.06, H * 0.1),
               seg=8, rings=5)
    _eyes(z, W * 0.13, hc[1] - W * 0.08, hc[2] + H * 0.09, W * 0.025)


def manatee(z, W, L, H, body):
    rz = H * 0.45
    z.ball(1, loc=(0, -L * 0.04, rz), colour=body, scale=(W * 0.42, L * 0.33, rz), seg=16, rings=9)
    hc = (0, -L * 0.36, rz * 0.9)
    _limb(z, (0, -L * 0.2, rz), hc, W * 0.3, body, r2=W * 0.22, seg=12)
    z.ball(1, loc=hc, colour=body, scale=(W * 0.2, L * 0.07, rz * 0.5), seg=12, rings=7)
    z.ball(1, loc=(0, hc[1] - L * 0.06, hc[2] - rz * 0.12), colour="light_grey", scale=(W * 0.17, L * 0.04, rz * 0.33),
           seg=10, rings=6)
    for s in (1, -1):
        z.ball(W * 0.025, loc=(s * W * 0.06, hc[1] - L * 0.095, hc[2]), colour="black", seg=6, rings=4)
        z.ball(1, loc=(s * W * 0.38, -L * 0.24, rz * 0.5), colour=body, scale=(W * 0.14, L * 0.06, rz * 0.12),
               rot=(0, 0, s * -35), seg=8, rings=5)
    _eyes(z, W * 0.16, hc[1] - L * 0.02, hc[2] + rz * 0.2, W * 0.02)
    _limb(z, (0, L * 0.22, rz * 0.8), (0, L * 0.34, rz * 0.5), W * 0.3, body, r2=W * 0.2, seg=12)
    z.cyl(W * 0.42, rz * 0.18, loc=(0, L * 0.36, rz * 0.4), colour=body, seg=16)  # round paddle tail


def octopus(z, W, L, H, body):
    import math
    mc = (0, L * 0.12, H * 0.62)
    z.ball(1, loc=mc, colour=body, scale=(W * 0.14, L * 0.18, H * 0.36), rot=(-35, 0, 0), seg=14, rings=9)
    hc = (0, -L * 0.04, H * 0.3)
    z.ball(1, loc=hc, colour=body, scale=(W * 0.13, L * 0.12, H * 0.2), seg=12, rings=8)
    _eyes(z, W * 0.09, -L * 0.13, H * 0.42, W * 0.025, white=True)
    for i in range(8):  # arms spread out on the floor, tips curled up
        a = math.radians(22.5 + i * 45)
        dx, dy = math.sin(a), -math.cos(a)
        r0 = W * 0.06
        p0 = (dx * W * 0.06, hc[1] + dy * L * 0.06, H * 0.18)
        p1 = (dx * W * 0.24, hc[1] + dy * L * 0.24, r0 * 0.7)
        p2 = (dx * W * 0.44, hc[1] + dy * L * 0.42, r0 * 0.4)
        p3 = (dx * W * 0.46, hc[1] + dy * L * 0.46 - 0.0, r0 * 2.2)
        _limb(z, p0, p1, r0, body, r2=r0 * 0.7, seg=8)
        _limb(z, p1, p2, r0 * 0.7, body, r2=r0 * 0.35, seg=8)
        _limb(z, p2, p3, r0 * 0.35, body, r2=r0 * 0.1, seg=6)
        for t in (0.35, 0.7):  # suckers
            q = tuple(p0[k] + (p2[k] - p0[k]) * t for k in range(3))
            z.ball(r0 * 0.3, loc=(q[0], q[1], 0.01), colour="cream", scale=(1, 1, 0.5), seg=6, rings=3)


def jellyfish(z, W, L, H, body):
    import math
    bz = H * 0.62
    z.ball(1, loc=(0, 0, bz), colour=body, scale=(W * 0.5, L * 0.5, H * 0.38), seg=16, rings=8)
    z.cyl(W * 0.47, H * 0.04, loc=(0, 0, bz - H * 0.02), colour="lavender", seg=16)
    for i in range(4):  # four pink rings seen through the bell
        a = math.radians(45 + i * 90)
        z.ball(1, loc=(math.cos(a) * W * 0.17, math.sin(a) * L * 0.17, bz + H * 0.24), colour="pink",
               scale=(W * 0.08, L * 0.08, H * 0.12), seg=8, rings=5)
    for i in range(4):  # frilly oral arms
        a = math.radians(i * 90)
        _limb(z, (math.cos(a) * W * 0.05, math.sin(a) * L * 0.05, bz - H * 0.02),
              (math.cos(a) * W * 0.1, math.sin(a) * L * 0.1, H * 0.02), W * 0.04, "white", r2=W * 0.015, seg=6)
    for i in range(12):  # fine edge tentacles
        a = math.radians(i * 30)
        x, y = math.cos(a) * W * 0.46, math.sin(a) * L * 0.46
        _limb(z, (x, y, bz - H * 0.02), (x * 0.9, y * 0.9, H * 0.18), W * 0.008, "lavender", seg=4)


def sea_otter(z, W, L, H, body):
    """Floating on its back, holding a shell on its chest."""
    rz = H * 0.3
    z.ball(1, loc=(0, L * 0.05, rz), colour=body, scale=(W * 0.45, L * 0.32, rz), seg=14, rings=9)
    hc = (0, -L * 0.33, H * 0.58)
    z.ball(1, loc=hc, colour="cream", scale=(W * 0.32, L * 0.1, H * 0.22), seg=12, rings=8)
    z.ball(1, loc=(0, hc[1] - L * 0.03, hc[2] + H * 0.17), colour="cream", scale=(W * 0.2, L * 0.07, H * 0.1),
           seg=10, rings=6)
    z.ball(W * 0.06, loc=(0, hc[1] - L * 0.09, hc[2] + H * 0.04), colour="black", seg=6, rings=4)
    _eyes(z, W * 0.12, hc[1] - L * 0.08, hc[2] + H * 0.14, W * 0.03)
    for s in (1, -1):
        z.ball(W * 0.06, loc=(s * W * 0.25, hc[1] + L * 0.02, hc[2] + H * 0.12), colour=body, seg=6, rings=4)
        # forepaws on the chest, hind feet sticking up
        _limb(z, (s * W * 0.32, -L * 0.15, rz * 1.4), (s * W * 0.08, -L * 0.08, rz * 2.05), W * 0.07, body, seg=6)
        z.ball(1, loc=(s * W * 0.2, L * 0.36, rz * 1.6), colour="dark_brown", scale=(W * 0.1, L * 0.04, H * 0.18),
               rot=(-25, 0, 0), seg=8, rings=5)
    z.ball(1, loc=(0, -L * 0.06, rz * 1.95), colour="pink", scale=(W * 0.12, L * 0.04, W * 0.04), seg=8, rings=5)
    z.ball(1, loc=(0, L * 0.42, rz * 0.8), colour=body, scale=(W * 0.12, L * 0.1, H * 0.06), seg=8, rings=5)


BUILDERS = {
    "bottlenose_dolphin": dolphin, "orca_calf": orca, "california_sea_lion": sea_lion, "harbour_seal": seal,
    "walrus": walrus, "manatee": manatee, "great_white_shark": shark, "manta_ray": manta, "green_moray": moray,
    "clownfish": clownfish, "blue_tang": blue_tang, "giant_pacific_octopus": octopus, "moon_jellyfish": jellyfish,
    "sea_otter": sea_otter,
}
