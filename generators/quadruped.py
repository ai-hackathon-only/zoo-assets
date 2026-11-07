"""Four-legged mammals (elephant, rhino, hippo, bear, ...). Params come from the asset row `params`.

params (all optional, metres or fractions of size_m):
  body: body colour; belly: belly colour; leg: leg length / height (0.45);
  neck: neck length / height (0.1); head: head size / body length (0.32); tail: tail length / length (0.25);
  extras: list of features, e.g. ["trunk", "tusks", "big_ears", "horn", "mane", "stripes", "spots"]
"""


def build(a, z):
    L, W, H = a["size_m"][1], a["size_m"][0], a["size_m"][2]
    p = a.get("params", {})
    body, belly = p.get("body", "grey"), p.get("belly", p.get("body", "grey"))
    leg_h = H * p.get("leg", 0.45)
    body_h = (H - leg_h) * 0.75
    body_l = L * 0.7
    bz = leg_h + body_h / 2
    z.ball(1, loc=(0, 0, bz), colour=body, scale=(W / 2, body_l / 2, body_h / 2))
    lr = min(W, body_l) * 0.14
    for x in (W * 0.28, -W * 0.28):
        for y in (body_l * 0.3, -body_l * 0.3):
            z.cyl(lr, leg_h + body_h * 0.2, loc=(x, y, (leg_h + body_h * 0.2) / 2), colour=belly)
    hs = body_l * p.get("head", 0.32)
    hy, hz = body_l / 2 + hs * 0.3, H - hs / 2
    z.ball(hs / 2, loc=(0, hy, hz), colour=body, scale=(0.9, 1.1, 1))
    for x in (hs * 0.25, -hs * 0.25):
        z.ball(hs * 0.07, loc=(x, hy + hs * 0.45, hz + hs * 0.12), colour="black", seg=6, rings=4)
    tl = L * p.get("tail", 0.25) * 0.5
    z.cyl(lr * 0.3, tl, loc=(0, -body_l / 2 - tl * 0.35, bz + body_h * 0.1), colour=body, rot=(60, 0, 0), seg=5)
