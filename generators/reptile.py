"""Reptiles and amphibians (crocodilians, turtles/tortoises, lizards, snakes, frogs, axolotl).

Params come from the asset row `params`:
  body: palette colour (olive, charcoal, leaf, lime, grey, tan, sky, pink)
  belly: optional underside colour (cream, sand, yellow)
  marks: list of features, e.g.:
    "scutes", "blunt_snout", "thin_snout", "dome_shell", "flippers",
    "long_tail", "dorsal_spikes", "curled_tail", "casque", "coiled",
    "net_pattern", "hood_up", "black_spots", "gills"
All models face -Y in Blender (glTF +Z), matching the thumbnail camera.
"""
import math


def build(a, z):
    aid = a["id"]
    p = a.get("params", {})
    marks = set(p.get("marks", []))
    body = p.get("body", "olive")
    W, L, H = a["size_m"]

    if aid in ("nile_crocodile", "american_alligator", "gharial"):
        _build_crocodilian(a, z, W, L, H, body, marks)
    elif aid in ("galapagos_tortoise", "green_sea_turtle"):
        _build_turtle(a, z, W, L, H, body, marks)
    elif aid in ("komodo_dragon", "green_iguana", "chameleon"):
        _build_lizard(a, z, W, L, H, body, marks)
    elif aid in ("reticulated_python", "king_cobra"):
        _build_snake(a, z, W, L, H, body, marks)
    elif aid == "poison_dart_frog":
        _build_frog(a, z, W, L, H, body, marks)
    elif aid == "axolotl":
        _build_axolotl(a, z, W, L, H, body, marks)
    else:
        _build_generic_reptile(a, z, W, L, H, body, marks)


def _build_crocodilian(a, z, W, L, H, body, marks):
    belly = "sand" if body == "olive" else "cream"

    # Torso (low and broad)
    torso_h = H * 0.40
    torso_z = H * 0.46
    z.ball(1, loc=(0, 0, torso_z), scale=(W * 0.38, L * 0.22, torso_h), colour=body, seg=11, rings=7)
    z.ball(1, loc=(0, L * 0.02, torso_z - H * 0.10), scale=(W * 0.33, L * 0.19, torso_h * 0.60), colour=belly, seg=8, rings=5)

    # Scutes along back - tall enough to hit target height H
    scute_top = H * 0.94
    scute_h = scute_top - torso_z
    for yi in (-0.12, -0.04, 0.04, 0.12):
        for xi in (-W * 0.10, W * 0.10):
            z.box((W * 0.07, L * 0.03, scute_h), loc=(xi, L * yi, torso_z + scute_h * 0.45), colour="dark_brown", taper=0.2)

    # Tail tapering into +Y (length within 30% of L)
    tail_len = L * 0.32
    z.cyl(H * 0.32, tail_len * 0.6, loc=(0, L * 0.20, H * 0.38), rot=(90, 0, 0), colour=body, seg=8, r2=H * 0.20)
    z.cone(H * 0.20, tail_len * 0.6, loc=(0, L * 0.20 + tail_len * 0.55, H * 0.34), rot=(90, 0, 0), colour=body, seg=7)
    for yi in (0.16, 0.24, 0.32):
        z.box((W * 0.04, L * 0.03, H * 0.22), loc=(0, L * yi, H * 0.48), colour="dark_brown", taper=0.2)

    # Neck
    z.cyl(H * 0.30, L * 0.14, loc=(0, -L * 0.17, H * 0.42), rot=(90, 0, 0), colour=body, seg=8)

    # Head cranium
    z.ball(1, loc=(0, -L * 0.26, H * 0.46), scale=(W * 0.28, L * 0.08, H * 0.25), colour=body, seg=8, rings=5)

    # Raised eye mounds & eyes (facing front/side, reaches near top of head)
    z.mirror_x(z.ball, H * 0.12, loc=(W * 0.14, -L * 0.25, H * 0.72), colour=body, seg=6, rings=4)
    z.mirror_x(z.ball, H * 0.05, loc=(W * 0.15, -L * 0.27, H * 0.74), colour="yellow", seg=5, rings=3)
    z.mirror_x(z.ball, H * 0.03, loc=(W * 0.16, -L * 0.28, H * 0.74), colour="black", seg=4, rings=3)

    # Snout variations (front extends to about -L*0.48, total length ~ 0.95*L)
    if "thin_snout" in marks:  # Gharial
        z.cyl(H * 0.09, L * 0.24, loc=(0, -L * 0.36, H * 0.40), rot=(90, 0, 0), colour=body, seg=7)
        z.ball(H * 0.12, loc=(0, -L * 0.50, H * 0.41), colour="dark_brown", scale=(1.2, 1.0, 1.0), seg=6, rings=4)
    elif "blunt_snout" in marks:  # American Alligator (wide U-shaped snout)
        z.box((W * 0.34, L * 0.20, H * 0.22), loc=(0, -L * 0.34, H * 0.40), colour=body, taper=0.82)
        z.ball(H * 0.10, loc=(0, -L * 0.44, H * 0.40), colour="charcoal", scale=(1.6, 0.8, 1.0), seg=6, rings=4)
    else:  # Nile Crocodile (tapered V-shaped snout)
        z.box((W * 0.28, L * 0.22, H * 0.22), loc=(0, -L * 0.35, H * 0.40), colour=body, taper=0.55)
        # Subtle protruding white teeth studs
        z.mirror_x(z.cone, H * 0.03, H * 0.08, loc=(W * 0.10, -L * 0.35, H * 0.48), rot=(180, 0, 0), colour="cream", seg=4)
        z.mirror_x(z.cone, H * 0.03, H * 0.08, loc=(W * 0.06, -L * 0.42, H * 0.48), rot=(180, 0, 0), colour="cream", seg=4)

    # Splayed legs - cylinders end cleanly above foot box floor to avoid coplanar bottom faces
    for side in (-1, 1):
        # Front leg
        z.cyl(H * 0.13, W * 0.28, loc=(side * W * 0.32, -L * 0.10, H * 0.34), rot=(0, side * 60, -side * 15), colour=body, seg=6)
        z.cyl(H * 0.10, H * 0.20, loc=(side * W * 0.44, -L * 0.12, H * 0.16), colour=body, seg=7)
        z.box((W * 0.12, L * 0.10, H * 0.08), loc=(side * W * 0.44, -L * 0.14, H * 0.04), colour="dark_brown", taper=0.7)
        # Rear leg
        z.cyl(H * 0.14, W * 0.30, loc=(side * W * 0.32, L * 0.14, H * 0.34), rot=(0, side * 60, side * 20), colour=body, seg=6)
        z.cyl(H * 0.10, H * 0.20, loc=(side * W * 0.45, L * 0.14, H * 0.16), colour=body, seg=7)
        z.box((W * 0.12, L * 0.10, H * 0.08), loc=(side * W * 0.45, L * 0.12, H * 0.04), colour="dark_brown", taper=0.7)


def _build_turtle(a, z, W, L, H, body, marks):
    if "dome_shell" in marks:  # Galapagos giant tortoise
        # High dome carapace reaching near H
        z.ball(1, loc=(0, 0, H * 0.54), scale=(W * 0.45, L * 0.40, H * 0.44), colour=body, seg=11, rings=7)
        # Carapace rim / margin (non-coplanar, slightly inset and rounded)
        z.ball(1, loc=(0, 0, H * 0.26), scale=(W * 0.46, L * 0.42, H * 0.08), colour="dark_brown", seg=9, rings=4)
        # Plastron (belly)
        z.ball(1, loc=(0, 0, H * 0.20), scale=(W * 0.37, L * 0.35, H * 0.06), colour="sand", seg=8, rings=4)

        # Wrinkled neck reaching up & forward
        z.cyl(H * 0.13, L * 0.26, loc=(0, -L * 0.36, H * 0.46), rot=(55, 0, 0), colour="grey", seg=7)
        # Head with blunt snout
        z.ball(1, loc=(0, -L * 0.48, H * 0.58), scale=(W * 0.13, L * 0.12, H * 0.13), colour="grey", seg=8, rings=6)
        z.mirror_x(z.ball, H * 0.03, loc=(W * 0.10, -L * 0.50, H * 0.62), colour="black", seg=5, rings=3)
        z.cone(H * 0.06, L * 0.08, loc=(0, -L * 0.57, H * 0.54), rot=(-90, 0, 0), colour="tan", seg=5)

        # 4 Sturdy columnar pillar legs - cylinders end at Z=0.06, foot caps rest on floor
        z.mirror_x(z.cyl, W * 0.13, H * 0.24, loc=(W * 0.32, -L * 0.22, H * 0.18), colour="grey", seg=7)
        z.mirror_x(z.cyl, W * 0.13, H * 0.24, loc=(W * 0.32, L * 0.22, H * 0.18), colour="grey", seg=7)
        # Feet caps
        z.mirror_x(z.box, (W * 0.16, L * 0.10, H * 0.08), loc=(W * 0.32, -L * 0.24, H * 0.04), colour="charcoal")
        z.mirror_x(z.box, (W * 0.16, L * 0.10, H * 0.08), loc=(W * 0.32, L * 0.22, H * 0.04), colour="charcoal")
        # Tail
        z.cone(H * 0.06, L * 0.14, loc=(0, L * 0.42, H * 0.26), rot=(90, 0, 0), colour="grey", seg=5)

    else:  # Green sea turtle (streamlined flippers)
        # Streamlined shell with full height H
        z.ball(1, loc=(0, L * 0.04, H * 0.54), scale=(W * 0.38, L * 0.36, H * 0.38), colour=body, seg=11, rings=7)
        # Shell rim
        z.ball(1, loc=(0, L * 0.04, H * 0.30), scale=(W * 0.40, L * 0.38, H * 0.06), colour="sand", seg=9, rings=4)
        z.ball(1, loc=(0, L * 0.04, H * 0.24), scale=(W * 0.34, L * 0.32, H * 0.06), colour="cream", seg=8, rings=4)

        # Turtle head
        z.ball(1, loc=(0, -L * 0.38, H * 0.44), scale=(W * 0.14, L * 0.15, H * 0.14), colour=body, seg=8, rings=5)
        z.mirror_x(z.ball, H * 0.04, loc=(W * 0.11, -L * 0.40, H * 0.48), colour="black", seg=5, rings=3)
        z.cone(H * 0.06, L * 0.07, loc=(0, -L * 0.48, H * 0.40), rot=(-90, 0, 0), colour="sand", seg=5)

        # Front flippers (wing-like, sweeping back)
        for side in (-1, 1):
            z.box((W * 0.38, L * 0.16, H * 0.05), loc=(side * W * 0.38, -L * 0.10, H * 0.28),
                  rot=(10, side * 22, -side * 35), colour=body, taper=0.45)
            # Rear flippers (smaller paddle flippers)
            z.box((W * 0.18, L * 0.16, H * 0.04), loc=(side * W * 0.24, L * 0.34, H * 0.24),
                  rot=(0, -side * 15, side * 30), colour=body, taper=0.55)

        # Small tail
        z.cone(H * 0.05, L * 0.12, loc=(0, L * 0.44, H * 0.28), rot=(90, 0, 0), colour=body, seg=5)


def _build_lizard(a, z, W, L, H, body, marks):
    if "curled_tail" in marks:  # Chameleon
        # Narrow, high laterally compressed body
        z.ball(1, loc=(0, -L * 0.06, H * 0.54), scale=(W * 0.26, L * 0.22, H * 0.36), colour=body, seg=10, rings=6)
        # Head with tall casque
        z.ball(1, loc=(0, -L * 0.22, H * 0.58), scale=(W * 0.25, L * 0.10, H * 0.22), colour=body, seg=8, rings=5)
        # Casque crest sweeping backward & upward, reaches full H
        z.box((W * 0.16, L * 0.12, H * 0.24), loc=(0, -L * 0.20, H * 0.84), rot=(-25, 0, 0), colour="leaf", taper=0.3)
        # Projecting turret cone eyes
        for side in (-1, 1):
            z.cone(H * 0.10, W * 0.16, loc=(side * W * 0.22, -L * 0.24, H * 0.62), rot=(0, side * 90, 0), colour=body, seg=6)
            z.ball(H * 0.035, loc=(side * W * 0.32, -L * 0.24, H * 0.62), colour="black", seg=4, rings=3)

        # Prehensile coiled tail (spiral in Y-Z plane)
        z.cyl(H * 0.08, L * 0.16, loc=(0, L * 0.18, H * 0.48), rot=(55, 0, 0), colour=body, seg=6)
        z.cyl(H * 0.07, L * 0.16, loc=(0, L * 0.26, H * 0.34), rot=(115, 0, 0), colour=body, seg=6)
        z.cyl(H * 0.06, L * 0.14, loc=(0, L * 0.22, H * 0.22), rot=(175, 0, 0), colour=body, seg=6)
        z.cone(H * 0.05, L * 0.12, loc=(0, L * 0.14, H * 0.24), rot=(-120, 0, 0), colour="leaf", seg=5)

        # Thin angular legs grasping a perch branch
        z.mirror_x(z.cyl, W * 0.08, H * 0.35, loc=(W * 0.22, -L * 0.12, H * 0.28), rot=(15, -15, 0), colour=body, seg=5)
        z.mirror_x(z.cyl, W * 0.08, H * 0.35, loc=(W * 0.22, L * 0.08, H * 0.28), rot=(-15, -15, 0), colour=body, seg=5)
        # Perch branch
        z.cyl(W * 0.14, L * 0.85, loc=(0, 0, H * 0.08), rot=(90, 0, 0), colour="brown", seg=6)

    elif "dorsal_spikes" in marks:  # Green iguana
        # Slender athletic lizard
        z.ball(1, loc=(0, -L * 0.05, H * 0.44), scale=(W * 0.32, L * 0.20, H * 0.26), colour=body, seg=10, rings=6)
        # Tail (total length well within 30% of L = 1.5)
        tail_l = L * 0.34
        z.cyl(H * 0.14, tail_l * 0.6, loc=(0, L * 0.20, H * 0.40), rot=(88, 0, 6), colour=body, seg=7, r2=H * 0.09)
        z.cone(H * 0.09, tail_l * 0.6, loc=(0, L * 0.20 + tail_l * 0.55, H * 0.36), rot=(90, 0, 12), colour="lime", seg=6)

        # Tall dorsal comb spikes reaching full H
        for yi in (-0.18, -0.12, -0.06, 0.0, 0.06, 0.12):
            z.cone(W * 0.05, H * 0.36, loc=(0, L * yi, H * 0.76), rot=(-10, 0, 0), colour="lime", seg=4)

        # Head & dewlap flap
        z.box((W * 0.32, L * 0.18, H * 0.26), loc=(0, -L * 0.28, H * 0.50), colour=body, taper=0.6)
        z.box((W * 0.06, L * 0.14, H * 0.20), loc=(0, -L * 0.26, H * 0.28), colour="lime", taper=0.4)  # dewlap
        z.mirror_x(z.ball, H * 0.05, loc=(W * 0.14, -L * 0.28, H * 0.58), colour="orange", seg=5, rings=3)
        z.mirror_x(z.ball, H * 0.025, loc=(W * 0.15, -L * 0.29, H * 0.58), colour="black", seg=4, rings=3)

        # Splayed legs
        for side in (-1, 1):
            z.cyl(H * 0.10, W * 0.26, loc=(side * W * 0.28, -L * 0.10, H * 0.34), rot=(0, side * 60, -side * 10), colour=body, seg=5)
            z.cyl(H * 0.08, H * 0.22, loc=(side * W * 0.38, -L * 0.12, H * 0.16), colour=body, seg=5)
            z.box((W * 0.10, L * 0.08, H * 0.06), loc=(side * W * 0.38, -L * 0.13, H * 0.03), colour=body)
            z.cyl(H * 0.10, W * 0.28, loc=(side * W * 0.28, L * 0.10, H * 0.34), rot=(0, side * 60, side * 15), colour=body, seg=5)
            z.cyl(H * 0.08, H * 0.22, loc=(side * W * 0.38, L * 0.12, H * 0.16), colour=body, seg=5)
            z.box((W * 0.10, L * 0.08, H * 0.06), loc=(side * W * 0.38, L * 0.11, H * 0.03), colour=body)

    else:  # Komodo dragon (W=0.6, L=2.8, H=0.6)
        # Muscular, heavy lizard body (height tuned to target H = 0.6)
        z.ball(1, loc=(0, 0, H * 0.48), scale=(W * 0.36, L * 0.22, H * 0.36), colour=body, seg=11, rings=7)
        # Back ridge scutes for height
        for yi in (-0.12, 0.0, 0.12):
            z.cone(W * 0.06, H * 0.22, loc=(0, L * yi, H * 0.78), rot=(-5, 0, 0), colour="charcoal", seg=5)

        # Tail - kept within overall length target
        tail_l = L * 0.28
        z.cyl(H * 0.24, tail_l * 0.55, loc=(0, L * 0.20, H * 0.42), rot=(86, 0, 5), colour=body, seg=8, r2=H * 0.16)
        z.cone(H * 0.16, tail_l * 0.55, loc=(0, L * 0.20 + tail_l * 0.50, H * 0.38), rot=(88, 0, 10), colour=body, seg=7)

        # Neck and heavy head
        z.cyl(H * 0.26, L * 0.14, loc=(0, -L * 0.18, H * 0.50), rot=(90, 0, 0), colour=body, seg=8)
        z.box((W * 0.32, L * 0.22, H * 0.30), loc=(0, -L * 0.32, H * 0.56), colour=body, taper=0.6)
        # Yellow predatory eyes
        z.mirror_x(z.ball, H * 0.06, loc=(W * 0.15, -L * 0.30, H * 0.70), colour="yellow", seg=5, rings=3)
        z.mirror_x(z.ball, H * 0.03, loc=(W * 0.16, -L * 0.31, H * 0.70), colour="black", seg=4, rings=3)
        # Red forked tongue extending from snout
        z.box((W * 0.04, L * 0.12, H * 0.015), loc=(0, -L * 0.44, H * 0.44), colour="red")
        z.mirror_x(z.box, (W * 0.02, L * 0.04, H * 0.01), loc=(W * 0.02, -L * 0.50, H * 0.44), rot=(0, 0, 25), colour="red")

        # Powerful muscular splayed legs - cylinders end above foot box
        for side in (-1, 1):
            z.cyl(H * 0.14, W * 0.28, loc=(side * W * 0.32, -L * 0.10, H * 0.38), rot=(0, side * 55, -side * 10), colour=body, seg=6)
            z.cyl(H * 0.11, H * 0.20, loc=(side * W * 0.44, -L * 0.12, H * 0.18), colour=body, seg=7)
            z.box((W * 0.14, L * 0.10, H * 0.08), loc=(side * W * 0.44, -L * 0.15, H * 0.04), colour="charcoal")
            z.cyl(H * 0.14, W * 0.30, loc=(side * W * 0.32, L * 0.12, H * 0.38), rot=(0, side * 55, side * 15), colour=body, seg=6)
            z.cyl(H * 0.11, H * 0.20, loc=(side * W * 0.44, L * 0.12, H * 0.18), colour=body, seg=7)
            z.box((W * 0.14, L * 0.10, H * 0.08), loc=(side * W * 0.44, L * 0.10, H * 0.04), colour="charcoal")


def _build_snake(a, z, W, L, H, body, marks):
    if "hood_up" in marks:  # King cobra (W=0.8, L=0.8, H=1.0)
        # Coiled base rings on floor
        r_base = W * 0.36
        for step in range(10):
            ang = step * (2 * math.pi / 10)
            x = math.cos(ang) * r_base
            y = math.sin(ang) * r_base + L * 0.06
            z.ball(H * 0.08, loc=(x, y, H * 0.08), colour=body, seg=6, rings=4)

        # Rising vertical S-curve neck reaching near top H
        z.cyl(H * 0.08, H * 0.32, loc=(0, -L * 0.08, H * 0.30), rot=(-12, 0, 0), colour=body, seg=7)
        z.cyl(H * 0.07, H * 0.32, loc=(0, -L * 0.14, H * 0.58), rot=(-15, 0, 0), colour=body, seg=7)

        # Flared hood
        z.box((W * 0.44, L * 0.05, H * 0.30), loc=(0, -L * 0.15, H * 0.65), rot=(-15, 0, 0), colour=body, taper=0.72)
        # Non-coplanar yellow and black hood markings (offset slightly in Y)
        z.box((W * 0.24, L * 0.05, H * 0.18), loc=(0, -L * 0.15 + 0.026, H * 0.65), rot=(-15, 0, 0), colour="yellow", taper=0.6)
        z.box((W * 0.10, L * 0.05, H * 0.08), loc=(0, -L * 0.15 + 0.052, H * 0.65), rot=(-15, 0, 0), colour="black")

        # Head atop hood reaching H = 0.96m
        z.box((W * 0.18, L * 0.20, H * 0.14), loc=(0, -L * 0.22, H * 0.88), colour=body, taper=0.6)
        z.mirror_x(z.ball, H * 0.03, loc=(W * 0.08, -L * 0.22, H * 0.91), colour="black", seg=5, rings=3)
        # Forked red tongue
        z.box((W * 0.03, L * 0.12, H * 0.015), loc=(0, -L * 0.32, H * 0.86), colour="red")
        z.mirror_x(z.box, (W * 0.015, L * 0.04, H * 0.01), loc=(W * 0.015, -L * 0.38, H * 0.86), rot=(0, 0, 25), colour="red")

    else:  # Reticulated python (coiled spiral, W=1.2, L=1.2, H=0.3)
        # Multi-tiered spiral coils reaching H ~ 0.28m
        r_outer = W * 0.38
        for i in range(14):
            ang = i * (2 * math.pi / 14)
            x = math.cos(ang) * r_outer
            y = math.sin(ang) * r_outer
            col = "tan" if i % 2 == 0 else "dark_brown"
            z.ball(H * 0.24, loc=(x, y, H * 0.24), colour=col, seg=6, rings=5)

        r_inner = W * 0.20
        for i in range(8):
            ang = i * (2 * math.pi / 8) + 0.3
            x = math.cos(ang) * r_inner
            y = math.sin(ang) * r_inner
            col = "dark_brown" if i % 2 == 0 else "tan"
            z.ball(H * 0.22, loc=(x, y, H * 0.44), colour=col, seg=6, rings=5)

        # Head raised on top coil facing -Y reaching ~ 0.28m (scaled with H)
        z.box((W * 0.16, L * 0.22, H * 0.22), loc=(0, -L * 0.16, H * 0.68), colour=body, taper=0.65)
        # Diamond markings on head
        z.box((W * 0.06, L * 0.10, H * 0.04), loc=(0, -L * 0.16, H * 0.80), colour="dark_brown", taper=0.3)
        z.mirror_x(z.ball, H * 0.05, loc=(W * 0.07, -L * 0.16, H * 0.74), colour="orange", seg=5, rings=3)
        z.mirror_x(z.ball, H * 0.025, loc=(W * 0.075, -L * 0.17, H * 0.74), colour="black", seg=4, rings=3)
        z.box((W * 0.03, L * 0.10, H * 0.015), loc=(0, -L * 0.28, H * 0.62), colour="red")


def _build_frog(a, z, W, L, H, body, marks):
    # Blue poison dart frog (W=0.06, L=0.06, H=0.04)
    # Squat rounded body
    z.ball(1, loc=(0, L * 0.04, H * 0.44), scale=(W * 0.34, L * 0.36, H * 0.34), colour=body, seg=10, rings=6)

    # Big bulbous frog eyes
    z.mirror_x(z.ball, H * 0.28, loc=(W * 0.24, -L * 0.16, H * 0.74), colour=body, seg=7, rings=5)
    z.mirror_x(z.ball, H * 0.18, loc=(W * 0.26, -L * 0.20, H * 0.76), colour="black", seg=6, rings=4)

    # Black spots on back (slightly offset so non-coplanar)
    z.box((W * 0.10, L * 0.08, H * 0.04), loc=(0, -L * 0.02, H * 0.72), colour="black", taper=0.5)
    z.mirror_x(z.box, (W * 0.08, L * 0.08, H * 0.04), loc=(W * 0.16, L * 0.10, H * 0.66), colour="black", taper=0.5)
    z.box((W * 0.08, L * 0.08, H * 0.04), loc=(0, L * 0.22, H * 0.60), colour="black", taper=0.5)

    # Folded muscular hind legs
    for side in (-1, 1):
        z.ball(1, loc=(side * W * 0.36, L * 0.14, H * 0.34), scale=(W * 0.16, L * 0.24, H * 0.20),
               rot=(20, side * 20, 0), colour="black", seg=6, rings=4)
        z.box((W * 0.10, L * 0.12, H * 0.03), loc=(side * W * 0.38, L * 0.05, H * 0.04), colour="black")
        # Front arms propping frog up
        z.cyl(H * 0.08, H * 0.38, loc=(side * W * 0.24, -L * 0.14, H * 0.22),
              rot=(15, -side * 15, 0), colour="black", seg=5)
        z.box((W * 0.08, L * 0.08, H * 0.02), loc=(side * W * 0.24, -L * 0.22, H * 0.03), colour="black")


def _build_axolotl(a, z, W, L, H, body, marks):
    # Cute aquatic salamander with smiling face and external gill frills (W=0.08, L=0.25, H=0.06)
    # Broad flat head
    z.ball(1, loc=(0, -L * 0.26, H * 0.44), scale=(W * 0.44, L * 0.16, H * 0.34), colour=body, seg=10, rings=6)
    # Beady dark eyes
    z.mirror_x(z.ball, H * 0.11, loc=(W * 0.30, -L * 0.28, H * 0.58), colour="black", seg=5, rings=3)
    # Smiling mouth groove (subtly recessed)
    z.box((W * 0.22, L * 0.03, H * 0.02), loc=(0, -L * 0.36, H * 0.36), colour="red")

    # 6 feathery external gill branches reaching full H
    for i, (dz, pitch) in enumerate(((0.22, -20), (0.06, 0), (-0.10, 20))):
        for side in (-1, 1):
            z.cyl(H * 0.07, W * 0.36, loc=(side * W * 0.38, -L * 0.20, H * (0.50 + dz)),
                  rot=(0, side * (75 + pitch), side * 10), colour="red", seg=5)
            # Secondary gill frill tip
            z.ball(H * 0.09, loc=(side * W * 0.54, -L * 0.20, H * (0.52 + dz)), colour="pink", scale=(0.8, 1.2, 0.8), seg=5, rings=3)

    # Torso
    z.ball(1, loc=(0, -L * 0.04, H * 0.44), scale=(W * 0.30, L * 0.22, H * 0.30), colour=body, seg=8, rings=5)

    # Tail with paddle fin
    z.ball(1, loc=(0, L * 0.24, H * 0.48), scale=(W * 0.10, L * 0.26, H * 0.44), colour=body, seg=8, rings=5)

    # 4 small splayed legs
    for side in (-1, 1):
        z.cyl(H * 0.08, W * 0.24, loc=(side * W * 0.30, -L * 0.12, H * 0.20), rot=(0, side * 50, -side * 10), colour=body, seg=5)
        z.cyl(H * 0.08, W * 0.24, loc=(side * W * 0.30, L * 0.10, H * 0.20), rot=(0, side * 50, side * 15), colour=body, seg=5)


def _build_generic_reptile(a, z, W, L, H, body, marks):
    z.ball(1, loc=(0, 0, H * 0.4), scale=(W * 0.3, L * 0.3, H * 0.25), colour=body)
    z.cone(H * 0.15, L * 0.4, loc=(0, L * 0.4, H * 0.35), rot=(90, 0, 0), colour=body)
    z.box((W * 0.25, L * 0.2, H * 0.15), loc=(0, -L * 0.3, H * 0.4), colour=body, taper=0.6)
