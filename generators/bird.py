"""Bird generator: 16 avian species across penguins, ratites, waders, raptors, tropical, and waterbirds.

size_m = [width, length beak-to-tail, height].
The bird faces -Y (DECISION in Plan & roles).
"""
import math
from mathutils import Vector
from generators.quadruped import _limb


def build(a, z):
    W, L, H = a["size_m"]
    p = a.get("params", {})
    marks = set(p.get("marks", []))
    fur = p.get("body", "brown")
    bid = a["id"]

    if bid in ("african_penguin", "emperor_penguin"):
        _build_penguin(a, z, W, L, H, fur, marks, bid)
    elif bid in ("ostrich", "emu"):
        _build_ratite(a, z, W, L, H, fur, marks, bid)
    elif bid in ("greater_flamingo", "white_stork", "red_crowned_crane"):
        _build_wader(a, z, W, L, H, fur, marks, bid)
    elif bid in ("pelican", "shoebill"):
        _build_waterbird(a, z, W, L, H, fur, marks, bid)
    elif bid in ("bald_eagle", "snowy_owl"):
        _build_raptor_owl(a, z, W, L, H, fur, marks, bid)
    elif bid == "indian_peafowl":
        _build_peafowl(a, z, W, L, H, fur, marks)
    elif bid == "scarlet_macaw":
        _build_macaw(a, z, W, L, H, fur, marks)
    elif bid == "toco_toucan":
        _build_toucan(a, z, W, L, H, fur, marks)
    elif bid == "kookaburra":
        _build_kookaburra(a, z, W, L, H, fur, marks)
    elif bid == "kiwi":
        _build_kiwi(a, z, W, L, H, fur, marks)
    else:
        _build_generic_bird(a, z, W, L, H, fur, marks)


def _build_penguin(a, z, W, L, H, fur, marks, bid):
    # Upright stance on webbed feet
    foot_col = "black" if bid == "emperor_penguin" else "charcoal"
    z.mirror_x(z.box, (W * 0.22, L * 0.36, H * 0.04), loc=(W * 0.22, -L * 0.10, H * 0.02), colour=foot_col, taper=0.7)

    # Torso
    bz = H * 0.44
    z.ball(1, loc=(0, L * 0.02, bz), scale=(W * 0.44, L * 0.36, H * 0.40), colour="black", seg=12, rings=8)
    # White belly
    belly_col = "cream" if bid == "emperor_penguin" else "white"
    z.ball(1, loc=(0, -L * 0.14, bz - H * 0.02), scale=(W * 0.36, L * 0.26, H * 0.36), colour=belly_col, seg=10, rings=6)

    # Flippers angled down and back
    for side in (-1, 1):
        z.box((W * 0.07, L * 0.24, H * 0.36), loc=(side * W * 0.42, L * 0.04, bz + H * 0.02),
              colour="black", rot=(25, side * 16, -side * 12), taper=0.5)

    # Head & Neck
    hz = H * 0.82
    z.ball(1, loc=(0, -L * 0.04, hz), scale=(W * 0.28, L * 0.28, H * 0.16), colour="black", seg=10, rings=6)

    # Tail stub
    z.box((W * 0.14, L * 0.14, H * 0.04), loc=(0, L * 0.32, H * 0.12), colour="black", rot=(-30, 0, 0), taper=0.4)

    if bid == "african_penguin":
        # Black horseshoe chest band
        z.cyl(W * 0.32, H * 0.045, loc=(0, -L * 0.18, H * 0.58), rot=(70, 0, 0), colour="black", seg=10)
        # Pink facial patch around eye
        z.mirror_x(z.ball, H * 0.035, loc=(W * 0.14, -L * 0.20, hz + H * 0.01), colour="pink", seg=5, rings=3)
        # Black beak
        z.cone(W * 0.10, L * 0.26, loc=(0, -L * 0.28, hz - H * 0.02), rot=(-90, 0, 0), colour="black", seg=6)
    else:
        # Emperor penguin yellow/gold neck patches
        z.mirror_x(z.ball, 1, loc=(W * 0.22, -L * 0.04, hz - H * 0.02),
                   scale=(W * 0.08, L * 0.12, H * 0.10), colour="gold", seg=6, rings=4)
        # Upper chest yellow glow
        z.ball(1, loc=(0, -L * 0.16, H * 0.68), scale=(W * 0.24, L * 0.16, H * 0.08), colour="yellow", seg=8, rings=4)
        # Sleek slender beak with orange mandible streak
        z.cone(W * 0.08, L * 0.30, loc=(0, -L * 0.29, hz - H * 0.02), rot=(-90, 0, 0), colour="black", seg=6)
        z.box((W * 0.04, L * 0.22, H * 0.02), loc=(0, -L * 0.28, hz - H * 0.04), colour="orange")

    # Eyes
    z.mirror_x(z.ball, H * 0.022, loc=(W * 0.15, -L * 0.18, hz + H * 0.04), colour="charcoal", seg=5, rings=3)


def _build_ratite(a, z, W, L, H, fur, marks, bid):
    # Ostrich and Emu
    is_ostrich = (bid == "ostrich")
    leg_col = "skin_2" if is_ostrich else "grey"
    neck_col = "skin_2" if is_ostrich else "charcoal"

    # Legs
    for side in (-1, 1):
        lx = side * W * 0.22
        # Thigh
        _limb(z, (lx, 0, H * 0.52), (lx, 0, H * 0.36), W * 0.11, fur, r2=W * 0.08)
        # Shank
        _limb(z, (lx, 0, H * 0.36), (lx, -L * 0.02, H * 0.04), W * 0.055, leg_col)
        # Foot
        z.box((W * 0.14, L * 0.22, H * 0.035), loc=(lx, -L * 0.08, H * 0.02), colour=leg_col, taper=0.6)

    # Torso
    bz = H * 0.56
    z.ball(1, loc=(0, 0, bz), scale=(W * 0.44, L * 0.36, H * 0.22), colour=fur, seg=12, rings=8)

    if is_ostrich:
        # Fluffy white wing plumes on sides
        z.mirror_x(z.ball, 1, loc=(W * 0.40, L * 0.04, bz + H * 0.02),
                   scale=(W * 0.10, L * 0.24, H * 0.16), colour="white", seg=8, rings=5)
        # White tail plume
        z.ball(1, loc=(0, L * 0.40, bz + H * 0.04), scale=(W * 0.22, L * 0.18, H * 0.16), colour="white", seg=8, rings=5)
    else:
        # Emu: shaggy brown body
        z.ball(1, loc=(0, 0, bz + H * 0.04), scale=(W * 0.46, L * 0.38, H * 0.18), colour="dark_brown", seg=8, rings=5)
        z.ball(1, loc=(0, L * 0.28, bz - H * 0.02), scale=(W * 0.26, L * 0.20, H * 0.16), colour="brown", seg=8, rings=5)

    # Long neck
    p0 = (0, -L * 0.26, bz + H * 0.04)
    p1 = (0, -L * 0.32, H * 0.78)
    p2 = (0, -L * 0.28, H * 0.94)
    _limb(z, p0, p1, W * 0.065, neck_col)
    _limb(z, p1, p2, W * 0.05, neck_col)

    # Small head
    hz = H * 0.96
    z.ball(1, loc=(0, -L * 0.30, hz), scale=(W * 0.12, L * 0.14, H * 0.06), colour=neck_col, seg=8, rings=5)
    # Broad flat bill
    beak_col = "tan" if is_ostrich else "charcoal"
    z.box((W * 0.14, L * 0.16, H * 0.035), loc=(0, -L * 0.42, hz - H * 0.01), colour=beak_col, taper=0.6)
    # Eyes
    z.mirror_x(z.ball, W * 0.035, loc=(W * 0.10, -L * 0.30, hz + H * 0.01), colour="black")


def _build_wader(a, z, W, L, H, fur, marks, bid):
    # flamingo, stork, crane
    is_flamingo = (bid == "greater_flamingo")
    is_stork = (bid == "white_stork")
    is_crane = (bid == "red_crowned_crane")

    leg_col = "pink" if is_flamingo else ("red" if is_stork else "charcoal")
    leg_top = H * 0.44 if is_flamingo else H * 0.52

    # Long legs
    for side in (-1, 1):
        lx = side * W * 0.20
        _limb(z, (lx, 0, leg_top), (lx, -L * 0.02, H * 0.03), W * 0.04, leg_col)
        # Splayed feet
        z.box((W * 0.12, L * 0.18, H * 0.025), loc=(lx, -L * 0.06, H * 0.015), colour=leg_col, taper=0.6)

    # Torso
    bz = H * 0.52 if is_flamingo else H * 0.60
    z.ball(1, loc=(0, L * 0.02, bz), scale=(W * 0.38, L * 0.32, H * 0.18), colour=fur, seg=12, rings=8)

    # Wings on flanks
    if is_flamingo:
        z.mirror_x(z.ball, 1, loc=(W * 0.36, L * 0.04, bz + H * 0.01),
                   scale=(W * 0.08, L * 0.26, H * 0.14), colour="red", seg=8, rings=5)
    elif is_stork:
        # Jet black flight feathers at rear
        z.ball(1, loc=(0, L * 0.30, bz), scale=(W * 0.30, L * 0.20, H * 0.14), colour="black", seg=8, rings=5)
    elif is_crane:
        # Black secondary plumes cascading over rear
        z.ball(1, loc=(0, L * 0.28, bz - H * 0.02), scale=(W * 0.32, L * 0.22, H * 0.16), colour="black", seg=8, rings=5)

    # Neck & Head
    if is_flamingo:
        # S-curve neck
        n0 = (0, -L * 0.20, bz + H * 0.02)
        n1 = (0, -L * 0.30, H * 0.68)
        n2 = (0, -L * 0.22, H * 0.82)
        n3 = (0, -L * 0.28, H * 0.92)
        _limb(z, n0, n1, W * 0.045, "pink")
        _limb(z, n1, n2, W * 0.04, "pink")
        _limb(z, n2, n3, W * 0.04, "pink")
        # Head
        hz = H * 0.96
        z.ball(1, loc=(0, -L * 0.30, hz), scale=(W * 0.11, L * 0.13, H * 0.06), colour="pink", seg=8, rings=5)
        # Flamingo curved beak: pink base + black tip pointing downward
        z.box((W * 0.09, L * 0.11, H * 0.05), loc=(0, -L * 0.40, hz - H * 0.02), colour="pink", taper=0.7)
        z.cone(W * 0.045, L * 0.10, loc=(0, -L * 0.44, hz - H * 0.06), rot=(-55, 0, 0), colour="black", seg=5)
        z.mirror_x(z.ball, W * 0.02, loc=(W * 0.09, -L * 0.30, hz + H * 0.015), colour="yellow")
    elif is_stork:
        # Upright white neck
        n0 = (0, -L * 0.20, bz + H * 0.04)
        n1 = (0, -L * 0.24, H * 0.90)
        _limb(z, n0, n1, W * 0.065, "white")
        # Head
        hz = H * 0.95
        z.ball(1, loc=(0, -L * 0.25, hz), scale=(W * 0.12, L * 0.16, H * 0.10), colour="white", seg=8, rings=5)
        # Long sharp red dagger beak
        z.cone(W * 0.06, L * 0.34, loc=(0, -L * 0.48, hz - H * 0.02), rot=(-90, 0, 0), colour="red", seg=6)
        z.mirror_x(z.ball, W * 0.025, loc=(W * 0.10, -L * 0.26, hz + H * 0.02), colour="black")
    else:
        # Red crowned crane
        n0 = (0, -L * 0.20, bz + H * 0.04)
        n1 = (0, -L * 0.26, H * 0.94)
        _limb(z, n0, n1, W * 0.06, "white")
        # Black foreneck patch
        z.cyl(W * 0.05, H * 0.20, loc=(0, -L * 0.25, H * 0.88), rot=(15, 0, 0), colour="black", seg=6)
        # Head
        hz = H * 1.00
        z.ball(1, loc=(0, -L * 0.28, hz), scale=(W * 0.12, L * 0.16, H * 0.09), colour="white", seg=8, rings=5)
        # Red cap on crown
        z.cyl(W * 0.08, H * 0.025, loc=(0, -L * 0.28, hz + H * 0.08), colour="red", seg=8)
        # Dagger beak
        z.cone(W * 0.055, L * 0.32, loc=(0, -L * 0.50, hz - H * 0.02), rot=(-90, 0, 0), colour="olive", seg=6)
        z.mirror_x(z.ball, W * 0.025, loc=(W * 0.10, -L * 0.29, hz + H * 0.02), colour="black")


def _build_waterbird(a, z, W, L, H, fur, marks, bid):
    # pelican and shoebill
    if bid == "pelican":
        # Short pink webbed feet
        z.mirror_x(z.box, (W * 0.22, L * 0.28, H * 0.04), loc=(W * 0.22, -L * 0.06, H * 0.02), colour="pink", taper=0.7)
        # Sturdy legs
        z.mirror_x(z.cyl, W * 0.07, H * 0.24, loc=(W * 0.22, -L * 0.02, H * 0.14), colour="pink", seg=6)
        # Bulky white torso
        bz = H * 0.46
        z.ball(1, loc=(0, L * 0.06, bz), scale=(W * 0.44, L * 0.36, H * 0.26), colour="white", seg=12, rings=8)
        # Folded wings with grey primaries
        z.mirror_x(z.ball, 1, loc=(W * 0.42, L * 0.08, bz + H * 0.04),
                   scale=(W * 0.08, L * 0.32, H * 0.18), colour="light_grey", seg=8, rings=5)
        # Thick neck
        n0 = (0, -L * 0.20, bz + H * 0.10)
        n1 = (0, -L * 0.28, H * 0.82)
        _limb(z, n0, n1, W * 0.12, "white", seg=8)
        # Head
        hz = H * 0.88
        z.ball(1, loc=(0, -L * 0.28, hz), scale=(W * 0.18, L * 0.22, H * 0.14), colour="white", seg=8, rings=6)
        # Long yellow upper bill
        z.box((W * 0.16, L * 0.44, H * 0.045), loc=(0, -L * 0.52, hz - H * 0.02), colour="yellow", taper=0.7)
        # Hook at bill tip
        z.cone(W * 0.04, L * 0.06, loc=(0, -L * 0.72, hz - H * 0.05), rot=(-45, 0, 0), colour="red", seg=4)
        # Massive throat pouch
        z.ball(1, loc=(0, -L * 0.46, hz - H * 0.16), scale=(W * 0.15, L * 0.32, H * 0.15), colour="orange", seg=10, rings=6)
        z.mirror_x(z.ball, W * 0.03, loc=(W * 0.14, -L * 0.28, hz + H * 0.04), colour="black")
    else:
        # Shoebill
        # Long dark grey legs
        leg_top = H * 0.48
        for side in (-1, 1):
            lx = side * W * 0.22
            _limb(z, (lx, 0, leg_top), (lx, -L * 0.02, H * 0.03), W * 0.05, "charcoal")
            z.box((W * 0.16, L * 0.22, H * 0.03), loc=(lx, -L * 0.08, H * 0.015), colour="charcoal", taper=0.6)
        # Torso
        bz = H * 0.58
        z.ball(1, loc=(0, L * 0.04, bz), scale=(W * 0.42, L * 0.34, H * 0.24), colour="grey", seg=12, rings=8)
        # Folded slate wings
        z.mirror_x(z.ball, 1, loc=(W * 0.40, L * 0.06, bz + H * 0.02),
                   scale=(W * 0.08, L * 0.30, H * 0.18), colour="charcoal", seg=8, rings=5)
        # Thick neck
        n0 = (0, -L * 0.20, bz + H * 0.08)
        n1 = (0, -L * 0.24, H * 0.88)
        _limb(z, n0, n1, W * 0.11, "grey", seg=8)
        # Head with tuft crest
        hz = H * 0.94
        z.ball(1, loc=(0, -L * 0.24, hz), scale=(W * 0.22, L * 0.22, H * 0.16), colour="grey", seg=8, rings=6)
        z.cone(W * 0.08, L * 0.14, loc=(0, -L * 0.10, hz + H * 0.08), rot=(45, 0, 0), colour="grey", seg=5)
        # Enormous shoe-shaped bill
        z.ball(1, loc=(0, -L * 0.40, hz - H * 0.06), scale=(W * 0.22, L * 0.26, H * 0.14), colour="cream", seg=10, rings=6)
        z.cone(W * 0.07, L * 0.10, loc=(0, -L * 0.54, hz - H * 0.12), rot=(-45, 0, 0), colour="charcoal", seg=5)
        # Piercing pale yellow eyes
        z.mirror_x(z.ball, W * 0.035, loc=(W * 0.18, -L * 0.26, hz + H * 0.04), colour="yellow")


def _build_raptor_owl(a, z, W, L, H, fur, marks, bid):
    if bid == "bald_eagle":
        # Perched talons
        z.mirror_x(z.ball, W * 0.09, loc=(W * 0.24, -L * 0.04, H * 0.06), colour="gold", scale=(1, 1.4, 0.6))
        # Torso
        bz = H * 0.44
        z.ball(1, loc=(0, 0, bz), scale=(W * 0.40, L * 0.30, H * 0.28), colour="dark_brown", rot=(-20, 0, 0), seg=12, rings=8)
        # Folded dark wings
        z.mirror_x(z.box, (W * 0.10, L * 0.32, H * 0.32), loc=(W * 0.38, L * 0.04, bz + H * 0.04),
                   colour="dark_brown", rot=(-25, 0, 0), taper=0.6)
        # Snow white tail extending back
        z.box((W * 0.26, L * 0.34, H * 0.04), loc=(0, L * 0.32, H * 0.26), colour="white", rot=(-30, 0, 0), taper=0.7)
        # Gleaming white head & neck
        hz = H * 0.74
        z.ball(1, loc=(0, -L * 0.16, hz), scale=(W * 0.22, L * 0.22, H * 0.16), colour="white", seg=10, rings=6)
        # Sharp hooked golden beak
        z.cone(W * 0.08, L * 0.24, loc=(0, -L * 0.34, hz - H * 0.04), rot=(-65, 0, 0), colour="gold", seg=6)
        # Fierce yellow eyes
        z.mirror_x(z.ball, W * 0.035, loc=(W * 0.16, -L * 0.18, hz + H * 0.04), colour="yellow")
    else:
        # Snowy owl
        # White feathered legs/talons
        z.mirror_x(z.ball, W * 0.10, loc=(W * 0.20, -L * 0.02, H * 0.06), colour="white", scale=(1, 1.2, 0.6))
        # Plump barrel body
        bz = H * 0.40
        z.ball(1, loc=(0, 0, bz), scale=(W * 0.44, L * 0.38, H * 0.34), colour="white", seg=12, rings=8)
        # Folded white wings with charcoal flecks
        z.mirror_x(z.ball, 1, loc=(W * 0.40, L * 0.02, bz), scale=(W * 0.08, L * 0.30, H * 0.26),
                   colour="white", rot=(-15, 0, 0), seg=8, rings=5)
        z.mirror_x(z.box, (W * 0.04, L * 0.16, H * 0.03), loc=(W * 0.42, 0, bz + H * 0.06), colour="charcoal")
        z.mirror_x(z.box, (W * 0.04, L * 0.16, H * 0.03), loc=(W * 0.42, 0, bz - H * 0.06), colour="charcoal")
        # Short white tail
        z.box((W * 0.24, L * 0.20, H * 0.04), loc=(0, L * 0.28, H * 0.18), colour="white", rot=(-35, 0, 0), taper=0.8)
        # Large round head
        hz = H * 0.78
        z.ball(1, loc=(0, -L * 0.04, hz), scale=(W * 0.38, L * 0.32, H * 0.20), colour="white", seg=12, rings=7)
        # Facial discs
        z.mirror_x(z.cyl, W * 0.12, H * 0.02, loc=(W * 0.14, -L * 0.26, hz), rot=(90, 0, 0), colour="white", seg=8)
        # Big forward-facing golden yellow eyes
        z.mirror_x(z.ball, W * 0.06, loc=(W * 0.14, -L * 0.28, hz), colour="yellow", seg=6, rings=4)
        z.mirror_x(z.ball, W * 0.03, loc=(W * 0.14, -L * 0.30, hz), colour="black", seg=5, rings=3)
        # Small hooked dark beak
        z.cone(W * 0.045, L * 0.09, loc=(0, -L * 0.30, hz - H * 0.04), rot=(-70, 0, 0), colour="charcoal", seg=5)


def _build_peafowl(a, z, W, L, H, fur, marks):
    # Indian peafowl
    # Legs
    for side in (-1, 1):
        lx = side * W * 0.18
        _limb(z, (lx, 0, H * 0.44), (lx, -L * 0.01, H * 0.02), W * 0.035, "tan")
    # Royal navy breast & torso
    bz = H * 0.52
    z.ball(1, loc=(0, -L * 0.12, bz), scale=(W * 0.32, L * 0.18, H * 0.22), colour="navy", seg=10, rings=6)
    # Elegant upright navy neck
    n0 = (0, -L * 0.18, bz + H * 0.06)
    n1 = (0, -L * 0.24, H * 0.88)
    _limb(z, n0, n1, W * 0.065, "navy", seg=7)
    # Head
    hz = H * 0.94
    z.ball(1, loc=(0, -L * 0.25, hz), scale=(W * 0.10, L * 0.12, H * 0.08), colour="navy", seg=8, rings=5)
    # Beak
    z.cone(W * 0.04, L * 0.12, loc=(0, -L * 0.34, hz - H * 0.01), rot=(-90, 0, 0), colour="cream", seg=5)
    # Crown crest
    z.cone(W * 0.04, H * 0.10, loc=(0, -L * 0.24, hz + H * 0.08), colour="gold", seg=4)
    # Folded wings with buff/brown stripes
    z.mirror_x(z.ball, 1, loc=(W * 0.30, -L * 0.08, bz), scale=(W * 0.06, L * 0.18, H * 0.14), colour="tan", seg=6, rings=4)
    # Spectacular long train (fan_tail) trailing back
    z.box((W * 0.44, L * 0.65, H * 0.07), loc=(0, L * 0.42, H * 0.30), colour="forest", rot=(-14, 0, 0), taper=0.7)
    # Eyespots (ocelli) as single raised spheres with different positions and angles
    for (ox, oy, oz) in (
        (0, L * 0.28, H * 0.36), (W * 0.12, L * 0.44, H * 0.32), (-W * 0.12, L * 0.44, H * 0.32),
        (0, L * 0.58, H * 0.28), (W * 0.14, L * 0.70, H * 0.24), (-W * 0.14, L * 0.70, H * 0.24)
    ):
        z.ball(W * 0.06, loc=(ox, oy, oz), colour="teal", scale=(1, 1, 0.4), seg=6, rings=4)


def _build_macaw(a, z, W, L, H, fur, marks):
    # Scarlet macaw
    # Feet
    z.mirror_x(z.box, (W * 0.12, L * 0.16, H * 0.03), loc=(W * 0.18, -L * 0.04, H * 0.015), colour="charcoal", taper=0.6)
    # Red body
    bz = H * 0.56
    z.ball(1, loc=(0, -L * 0.06, bz), scale=(W * 0.34, L * 0.22, H * 0.24), colour="red", seg=10, rings=6)
    # Tri-colored layered wings: 3 distinct wings angled on flanks
    for side in (-1, 1):
        wx = side * W * 0.35
        z.box((W * 0.06, L * 0.22, H * 0.14), loc=(wx, -L * 0.02, bz + H * 0.04), colour="red", rot=(-14, side * 5, 0), taper=0.8)
        z.box((W * 0.06, L * 0.20, H * 0.12), loc=(side * (W * 0.36), L * 0.05, bz - H * 0.03), colour="gold", rot=(-19, side * 8, 0), taper=0.8)
        z.box((W * 0.06, L * 0.22, H * 0.16), loc=(side * (W * 0.37), L * 0.12, bz - H * 0.10), colour="sky", rot=(-25, side * 12, 0), taper=0.8)
    # Long trailing red and blue tail
    z.box((W * 0.14, L * 0.48, H * 0.03), loc=(0, L * 0.32, H * 0.22), colour="red", rot=(-32, 0, 0), taper=0.3)
    # Head
    hz = H * 0.80
    z.ball(1, loc=(0, -L * 0.14, hz), scale=(W * 0.22, L * 0.20, H * 0.14), colour="red", seg=8, rings=5)
    # Bare white facial patch
    z.mirror_x(z.ball, 1, loc=(W * 0.15, -L * 0.18, hz), scale=(W * 0.02, L * 0.06, H * 0.06), colour="white", seg=5, rings=3)
    # Parrot curved bill
    z.cone(W * 0.075, L * 0.16, loc=(0, -L * 0.26, hz - H * 0.02), rot=(-65, 0, 0), colour="cream", seg=6)
    z.cone(W * 0.05, L * 0.08, loc=(0, -L * 0.21, hz - H * 0.07), rot=(-35, 0, 0), colour="black", seg=5)
    z.mirror_x(z.ball, W * 0.02, loc=(W * 0.16, -L * 0.18, hz + H * 0.02), colour="black")


def _build_toucan(a, z, W, L, H, fur, marks):
    # Toco toucan
    # Perched feet
    z.mirror_x(z.ball, W * 0.10, loc=(W * 0.22, -L * 0.04, H * 0.06), colour="grey", scale=(1, 1.3, 0.5))
    # Sleek black body
    bz = H * 0.50
    z.ball(1, loc=(0, L * 0.06, bz), scale=(W * 0.36, L * 0.26, H * 0.24), colour="black", seg=10, rings=7)
    # White throat/chest bib
    z.ball(1, loc=(0, -L * 0.08, bz + H * 0.04), scale=(W * 0.28, L * 0.16, H * 0.20), colour="white", seg=8, rings=5)
    z.cyl(W * 0.26, H * 0.02, loc=(0, -L * 0.06, bz - H * 0.08), colour="red", seg=8)
    # Folded black wings & tail
    z.mirror_x(z.box, (W * 0.07, L * 0.22, H * 0.22), loc=(W * 0.36, L * 0.08, bz), colour="black", rot=(-20, 0, 0))
    z.box((W * 0.18, L * 0.22, H * 0.03), loc=(0, L * 0.30, H * 0.25), colour="black", rot=(-35, 0, 0), taper=0.8)
    # Head
    hz = H * 0.74
    z.ball(1, loc=(0, -L * 0.06, hz), scale=(W * 0.24, L * 0.20, H * 0.16), colour="black", seg=8, rings=6)
    # Blue eye ring
    z.mirror_x(z.ball, W * 0.06, loc=(W * 0.16, -L * 0.08, hz), colour="sky", seg=5, rings=3)
    z.mirror_x(z.ball, W * 0.03, loc=(W * 0.18, -L * 0.08, hz), colour="black")
    # ENORMOUS orange beak with black tip
    z.cyl(H * 0.15, L * 0.40, loc=(0, -L * 0.30, hz - H * 0.02), rot=(-90, 0, 0), colour="orange", r2=H * 0.07, seg=8)
    z.cone(H * 0.07, L * 0.12, loc=(0, -L * 0.52, hz - H * 0.03), rot=(-90, 0, 0), colour="black", seg=6)


def _build_kookaburra(a, z, W, L, H, fur, marks):
    # Chunky cream body
    bz = H * 0.42
    z.ball(1, loc=(0, 0, bz), scale=(W * 0.42, L * 0.32, H * 0.28), colour="cream", seg=10, rings=7)
    # Feet
    z.mirror_x(z.ball, W * 0.10, loc=(W * 0.22, -L * 0.02, H * 0.06), colour="tan", scale=(1, 1.3, 0.5))
    # Brown wings with sky-blue spots
    z.mirror_x(z.ball, 1, loc=(W * 0.40, L * 0.02, bz), scale=(W * 0.08, L * 0.26, H * 0.22), colour="dark_brown", seg=8, rings=5)
    z.mirror_x(z.ball, W * 0.05, loc=(W * 0.44, -L * 0.04, bz + H * 0.06), colour="sky")
    # Tail
    z.box((W * 0.22, L * 0.20, H * 0.03), loc=(0, L * 0.28, H * 0.20), colour="rust", rot=(-30, 0, 0), taper=0.8)
    # Large head with prominent brown eye stripe
    hz = H * 0.72
    z.ball(1, loc=(0, -L * 0.08, hz), scale=(W * 0.34, L * 0.26, H * 0.20), colour="cream", seg=8, rings=6)
    # Eye stripe
    z.box((W * 0.72, L * 0.30, H * 0.08), loc=(0, -L * 0.08, hz), colour="dark_brown")
    # Eyes
    z.mirror_x(z.ball, W * 0.04, loc=(W * 0.24, -L * 0.12, hz), colour="black")
    # Heavy dagger bill
    z.box((W * 0.20, L * 0.26, H * 0.09), loc=(0, -L * 0.30, hz - H * 0.03), colour="tan", taper=0.5)


def _build_kiwi(a, z, W, L, H, fur, marks):
    # Pear-shaped round brown body
    bz = H * 0.48
    z.ball(1, loc=(0, L * 0.06, bz), scale=(W * 0.44, L * 0.36, H * 0.38), colour="brown", seg=12, rings=8)
    # Short stout legs
    for side in (-1, 1):
        lx = side * W * 0.22
        _limb(z, (lx, 0, H * 0.30), (lx, -L * 0.02, H * 0.03), W * 0.07, "tan")
        z.box((W * 0.12, L * 0.16, H * 0.03), loc=(lx, -L * 0.06, H * 0.015), colour="tan", taper=0.6)
    # Small head seamlessly tapering
    hz = H * 0.52
    z.ball(1, loc=(0, -L * 0.18, hz), scale=(W * 0.20, L * 0.18, H * 0.16), colour="brown", seg=8, rings=5)
    # Long thin downward probe beak
    _limb(z, (0, -L * 0.24, hz - H * 0.04), (0, -L * 0.48, H * 0.12), W * 0.035, "cream", r2=W * 0.015)
    # Tiny dark eyes
    z.mirror_x(z.ball, W * 0.025, loc=(W * 0.12, -L * 0.22, hz + H * 0.04), colour="black")


def _build_generic_bird(a, z, W, L, H, fur, marks):
    bz = H * 0.45
    z.ball(1, loc=(0, 0, bz), scale=(W * 0.40, L * 0.32, H * 0.28), colour=fur)
    z.cone(W * 0.10, L * 0.25, loc=(0, -L * 0.30, H * 0.70), rot=(-90, 0, 0), colour="yellow")
