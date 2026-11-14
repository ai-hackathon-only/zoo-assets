"""Insect generator: 10 procedural invertebrate species.

size_m = [width, length, height].
The models face -Y (DECISION in Plan & roles).
"""
import math
from mathutils import Vector


def build(a, z):
    W, L, H = a["size_m"]
    p = a.get("params", {})
    marks = set(p.get("marks", []))
    fur = p.get("body", "black")
    iid = a["id"]
    from generators.sea import _YTagger, _declare_joints
    z0, z = z, _YTagger(z, (W, L, H))

    if iid == "monarch_butterfly":
        _build_butterfly(a, z, W, L, H, "orange", marks)
    elif iid == "atlas_moth":
        _build_moth(a, z, W, L, H, "rust", marks)
    elif iid == "goliath_beetle":
        _build_beetle(a, z, W, L, H, "white", marks)
    elif iid == "leafcutter_ant":
        _build_ant(a, z, W, L, H, "rust", marks)
    elif iid == "honey_bee":
        _build_bee(a, z, W, L, H, "yellow", marks)
    elif iid == "emperor_scorpion":
        _build_scorpion(a, z, W, L, H, "black", marks)
    elif iid == "mexican_redknee_tarantula":
        _build_tarantula(a, z, W, L, H, "black", marks)
    elif iid == "giant_african_snail":
        _build_snail(a, z, W, L, H, "brown", marks)
    elif iid == "stick_insect":
        _build_stick_insect(a, z, W, L, H, "tan", marks)
    elif iid == "praying_mantis":
        _build_mantis(a, z, W, L, H, "pink", marks)
    else:
        _build_generic_bug(a, z, W, L, H, fur, marks)
    _declare_joints(z0)


def _build_butterfly(a, z, W, L, H, col, marks):
    z.ball(1, loc=(0, -L * 0.28, H * 0.35), scale=(W * 0.045, L * 0.09, H * 0.16), colour="black", seg=8, rings=6)
    z.ball(1, loc=(0, -L * 0.08, H * 0.33), scale=(W * 0.055, L * 0.16, H * 0.18), colour="black", seg=8, rings=6)
    z.ball(1, loc=(0, L * 0.22, H * 0.30), scale=(W * 0.040, L * 0.28, H * 0.14), colour="charcoal", seg=8, rings=6)

    z.mirror_x(z.box, (W * 0.015, L * 0.02, H * 0.45), loc=(W * 0.025, -L * 0.38, H * 0.65), rot=(20, 15, -15), colour="black")

    for dy in (-0.18, -0.06, 0.06):
        z.mirror_x(z.box, (W * 0.015, L * 0.02, H * 0.25), loc=(W * 0.045, L * dy, H * 0.13), rot=(0, 20, 0), colour="black")

    z.mirror_x(z.box, (W * 0.36, L * 0.34, H * 0.035), loc=(W * 0.26, -L * 0.05, H * 0.60), rot=(-4, -32, 22), colour=col, taper=0.85)
    z.mirror_x(z.box, (W * 0.12, L * 0.30, H * 0.040), loc=(W * 0.42, -L * 0.04, H * 0.70), rot=(-6, -34, 18), colour="black", taper=0.8)

    z.mirror_x(z.box, (W * 0.26, L * 0.26, H * 0.032), loc=(W * 0.18, L * 0.20, H * 0.50), rot=(6, -24, -12), colour=col, taper=0.85)


def _build_moth(a, z, W, L, H, col, marks):
    z.ball(1, loc=(0, -L * 0.30, H * 0.38), scale=(W * 0.035, L * 0.08, H * 0.20), colour="dark_brown", seg=8, rings=6)
    z.ball(1, loc=(0, -L * 0.08, H * 0.36), scale=(W * 0.050, L * 0.18, H * 0.22), colour="brown", seg=8, rings=6)
    z.ball(1, loc=(0, L * 0.20, H * 0.32), scale=(W * 0.040, L * 0.25, H * 0.18), colour="rust", seg=8, rings=6)

    z.mirror_x(z.box, (W * 0.045, L * 0.02, H * 0.15), loc=(W * 0.045, -L * 0.36, H * 0.65), rot=(20, 25, -35), colour="tan")

    for dy in (-0.18, -0.06, 0.06):
        z.mirror_x(z.box, (W * 0.015, L * 0.02, H * 0.25), loc=(W * 0.04, L * dy, H * 0.13), rot=(0, 25, 0), colour="dark_brown")

    z.mirror_x(z.box, (W * 0.38, L * 0.36, H * 0.04), loc=(W * 0.26, -L * 0.05, H * 0.50), rot=(2, -15, 14), colour="rust", taper=0.85)
    z.mirror_x(z.box, (W * 0.10, L * 0.14, H * 0.045), loc=(W * 0.44, -L * 0.18, H * 0.60), rot=(3, -16, 24), colour="dark_brown")
    z.mirror_x(z.box, (W * 0.05, L * 0.05, H * 0.048), loc=(W * 0.22, -L * 0.04, H * 0.52), rot=(2, -15, 45), colour="cream")

    z.mirror_x(z.box, (W * 0.24, L * 0.24, H * 0.035), loc=(W * 0.18, L * 0.20, H * 0.42), rot=(6, -10, -6), colour="rust", taper=0.85)


def _build_beetle(a, z, W, L, H, col, marks):
    # Goliath beetle: size_m=[0.06, 0.11, 0.05]
    # Carapace (elytra)
    z.ball(1, loc=(0, L * 0.14, H * 0.56), scale=(W * 0.40, L * 0.38, H * 0.30), colour="white", seg=12, rings=8)
    # Pentagonal cylinders tilted to prevent coplanar tri pairs
    z.mirror_x(z.cyl, W * 0.05, L * 0.42, loc=(W * 0.18, L * 0.16, H * 0.62), rot=(84, 2, 7), colour="black", seg=5)
    z.cyl(W * 0.055, L * 0.44, loc=(0, L * 0.16, H * 0.64), rot=(84, 0, 0), colour="black", seg=5)

    # Pronotum
    z.box((W * 0.70, L * 0.22, H * 0.38), loc=(0, -L * 0.22, H * 0.55), colour="black", taper=0.85)

    # Head and horn
    z.ball(1, loc=(0, -L * 0.38, H * 0.48), scale=(W * 0.16, L * 0.10, H * 0.14), colour="black", seg=8, rings=6)
    z.cyl(W * 0.05, L * 0.22, loc=(0, -L * 0.52, H * 0.48), rot=(90, 0, 0), colour="charcoal", seg=6)
    z.mirror_x(z.cyl, W * 0.04, L * 0.12, loc=(W * 0.07, -L * 0.60, H * 0.52), rot=(90, 0, 30), colour="charcoal", seg=5)

    # 6 legs reaching H=0.05
    for dy, rz in [(-0.25, -25), (-0.05, 5), (0.18, 35)]:
        z.mirror_x(z.cyl, W * 0.035, W * 0.32, loc=(W * 0.36, L * dy, H * 0.44), rot=(0, -65, rz + 3), colour="black", seg=6)
        z.mirror_x(z.cyl, W * 0.03, H * 0.52, loc=(W * 0.46, L * dy, H * 0.24), rot=(0, 16, rz - 3), colour="black", seg=5)


def _build_ant(a, z, W, L, H, col, marks):
    # Leafcutter ant: size_m=[0.01, 0.02, 0.01]
    z.ball(1, loc=(0, L * 0.30, H * 0.38), scale=(W * 0.26, L * 0.28, H * 0.26), colour="rust", seg=8, rings=6)
    z.cyl(W * 0.08, L * 0.12, loc=(0, L * 0.08, H * 0.36), rot=(88, 3, 0), colour="dark_brown", seg=6)
    z.ball(1, loc=(0, -L * 0.06, H * 0.36), scale=(W * 0.20, L * 0.20, H * 0.20), colour="rust", seg=8, rings=6)
    z.ball(1, loc=(0, -L * 0.30, H * 0.36), scale=(W * 0.26, L * 0.18, H * 0.24), colour="rust", seg=8, rings=6)
    z.mirror_x(z.cone, W * 0.06, L * 0.12, loc=(W * 0.10, -L * 0.44, H * 0.32), rot=(-85, 0, 15), colour="dark_brown", seg=4)

    z.mirror_x(z.cyl, W * 0.02, L * 0.18, loc=(W * 0.12, -L * 0.38, H * 0.48), rot=(20, 25, -20), colour="dark_brown", seg=4)

    for dy, rz in [(-0.16, -30), (-0.04, 0), (0.10, 30)]:
        z.mirror_x(z.cyl, W * 0.025, W * 0.32, loc=(W * 0.26, L * dy, H * 0.35), rot=(0, -70, rz + 2), colour="dark_brown", seg=5)
        z.mirror_x(z.cyl, W * 0.022, H * 0.36, loc=(W * 0.40, L * dy, H * 0.18), rot=(0, 20, rz + 8), colour="dark_brown", seg=5)

    # Leaf carried cleanly above thorax
    z.box((W * 0.10, L * 0.60, H * 0.44), loc=(0, -L * 0.06, H * 0.68), rot=(22, -18, 14), colour="leaf", taper=0.65)


def _build_bee(a, z, W, L, H, col, marks):
    z.ball(1, loc=(0, L * 0.22, H * 0.46), scale=(W * 0.32, L * 0.36, H * 0.36), colour="yellow", seg=10, rings=8)
    z.box((W * 0.68, L * 0.09, H * 0.72), loc=(0, L * 0.14, H * 0.46), colour="black")
    z.box((W * 0.62, L * 0.08, H * 0.66), loc=(0, L * 0.28, H * 0.46), colour="black")

    z.ball(1, loc=(0, -L * 0.14, H * 0.48), scale=(W * 0.30, L * 0.24, H * 0.36), colour="brown", seg=10, rings=8)

    z.ball(1, loc=(0, -L * 0.36, H * 0.44), scale=(W * 0.24, L * 0.16, H * 0.30), colour="charcoal", seg=8, rings=6)
    z.mirror_x(z.ball, 1, loc=(W * 0.14, -L * 0.38, H * 0.48), scale=(W * 0.08, L * 0.08, H * 0.14), colour="black", seg=6, rings=4)

    z.mirror_x(z.box, (W * 0.26, L * 0.52, H * 0.035), loc=(W * 0.16, L * 0.12, H * 0.68), rot=(4, -12, -6), colour="light_grey")

    for dy in (-0.22, -0.12, -0.02):
        z.mirror_x(z.box, (W * 0.04, L * 0.04, H * 0.36), loc=(W * 0.18, L * dy, H * 0.18), rot=(0, 20, 0), colour="black")


def _build_scorpion(a, z, W, L, H, col, marks):
    z.box((W * 0.48, L * 0.35, H * 0.24), loc=(0, -L * 0.02, H * 0.32), colour="black", taper=0.9)

    z.mirror_x(z.box, (W * 0.22, L * 0.15, H * 0.12), loc=(W * 0.28, -L * 0.24, H * 0.32), rot=(0, 0, -25), colour="charcoal")
    z.mirror_x(z.box, (W * 0.16, L * 0.18, H * 0.16), loc=(W * 0.34, -L * 0.38, H * 0.32), rot=(0, 0, 15), colour="black")
    z.mirror_x(z.cone, W * 0.05, L * 0.14, loc=(W * 0.32, -L * 0.48, H * 0.32), rot=(-90, 0, 0), colour="black", seg=4)

    for dy, rz in [(-0.14, -25), (-0.04, -10), (0.06, 10), (0.16, 25)]:
        z.mirror_x(z.box, (W * 0.30, L * 0.03, H * 0.05), loc=(W * 0.32, L * dy, H * 0.30), rot=(0, -20, rz), colour="black")
        z.mirror_x(z.box, (W * 0.04, L * 0.03, H * 0.30), loc=(W * 0.45, L * dy, H * 0.15), rot=(0, 25, rz), colour="charcoal")

    tail_segs = [
        (0, L * 0.20, H * 0.32, 0.08, 0.09, 0.09),
        (0, L * 0.26, H * 0.44, 0.07, 0.08, 0.08),
        (0, L * 0.24, H * 0.60, 0.06, 0.07, 0.08),
        (0, L * 0.15, H * 0.72, 0.06, 0.07, 0.07),
        (0, L * 0.04, H * 0.78, 0.05, 0.06, 0.07),
    ]
    for x, y, zpos, sx, sy, sz in tail_segs:
        z.ball(1, loc=(x, y, zpos), scale=(W * sx, L * sy, H * sz), colour="black", seg=6, rings=4)

    z.ball(1, loc=(0, -L * 0.05, H * 0.80), scale=(W * 0.05, L * 0.05, H * 0.06), colour="dark_brown", seg=6, rings=4)
    z.cone(W * 0.02, H * 0.10, loc=(0, -L * 0.09, H * 0.76), rot=(45, 0, 0), colour="yellow", seg=4)


def _build_tarantula(a, z, W, L, H, col, marks):
    # Mexican red-knee tarantula: size_m=[0.14, 0.14, 0.05]
    z.ball(1, loc=(0, -L * 0.10, H * 0.44), scale=(W * 0.22, L * 0.20, H * 0.24), colour="black", seg=10, rings=8)
    z.ball(1, loc=(0, L * 0.20, H * 0.52), scale=(W * 0.26, L * 0.28, H * 0.34), colour="dark_brown", seg=10, rings=8)

    z.mirror_x(z.box, (W * 0.05, L * 0.10, H * 0.14), loc=(W * 0.07, -L * 0.26, H * 0.34), rot=(15, 0, 12), colour="black")
    z.mirror_x(z.cyl, W * 0.025, L * 0.16, loc=(W * 0.14, -L * 0.30, H * 0.30), rot=(90, 0, -22), colour="black", seg=6)

    # 8 arched legs reaching H=0.05
    for dy, rz in [(-0.16, -35), (-0.06, -15), (0.06, 15), (0.16, 35)]:
        z.mirror_x(z.cyl, W * 0.025, W * 0.28, loc=(W * 0.20, L * dy, H * 0.52), rot=(0, -68, rz), colour="black", seg=6)
        z.mirror_x(z.ball, 1, loc=(W * 0.30, L * dy, H * 0.68), scale=(W * 0.035, L * 0.035, H * 0.045), colour="orange", seg=6, rings=4)
        z.mirror_x(z.cyl, W * 0.022, H * 0.70, loc=(W * 0.40, L * dy, H * 0.35), rot=(0, 25, rz + 4), colour="black", seg=6)


def _build_snail(a, z, W, L, H, col, marks):
    z.box((W * 0.46, L * 0.80, H * 0.16), loc=(0, -L * 0.04, H * 0.08), colour="tan", taper=0.85)

    z.ball(1, loc=(0, -L * 0.38, H * 0.25), scale=(W * 0.20, L * 0.16, H * 0.18), colour="tan", seg=8, rings=6)
    z.mirror_x(z.cyl, W * 0.03, H * 0.32, loc=(W * 0.12, -L * 0.44, H * 0.42), rot=(25, 15, -15), colour="tan", seg=6)
    z.mirror_x(z.ball, 1, loc=(W * 0.16, -L * 0.48, H * 0.54), scale=(W * 0.04, L * 0.04, H * 0.04), colour="black", seg=6, rings=4)
    z.mirror_x(z.cyl, W * 0.02, H * 0.14, loc=(W * 0.08, -L * 0.46, H * 0.22), rot=(45, 10, -5), colour="tan", seg=6)

    z.cyl(W * 0.44, L * 0.28, loc=(0, -L * 0.02, H * 0.52), rot=(75, 0, 0), colour="brown", seg=8, r2=W * 0.34)
    z.cyl(W * 0.35, L * 0.24, loc=(0, L * 0.14, H * 0.60), rot=(70, 0, 15), colour="dark_brown", seg=7, r2=W * 0.24)
    z.cyl(W * 0.25, L * 0.20, loc=(0, L * 0.28, H * 0.66), rot=(65, 0, -10), colour="brown", seg=6, r2=W * 0.14)
    z.cone(W * 0.15, L * 0.18, loc=(0, L * 0.40, H * 0.70), rot=(60, 0, 5), colour="tan", seg=5)


def _build_stick_insect(a, z, W, L, H, col, marks):
    z.cyl(W * 0.14, L * 0.75, loc=(0, 0, H * 0.50), rot=(90, 0, 0), colour="tan", seg=6)

    for ypos in (-L * 0.25, -L * 0.08, L * 0.10, L * 0.25):
        z.ball(1, loc=(0, ypos, H * 0.52), scale=(W * 0.18, L * 0.04, H * 0.20), colour="brown", seg=6, rings=4)

    z.ball(1, loc=(0, -L * 0.42, H * 0.52), scale=(W * 0.14, L * 0.08, H * 0.16), colour="tan", seg=6, rings=4)
    z.mirror_x(z.cyl, W * 0.02, L * 0.24, loc=(W * 0.05, -L * 0.50, H * 0.65), rot=(60, 15, -15), colour="dark_brown", seg=4)

    for dy, rz in [(-L * 0.22, -35), (0, 0), (L * 0.22, 35)]:
        z.mirror_x(z.cyl, W * 0.035, W * 0.55, loc=(W * 0.30, dy, H * 0.58), rot=(0, -70, rz), colour="tan", seg=4)
        z.mirror_x(z.cyl, W * 0.03, H * 0.70, loc=(W * 0.46, dy, H * 0.35), rot=(0, 20, rz), colour="brown", seg=4)


def _build_mantis(a, z, W, L, H, col, marks):
    z.ball(1, loc=(0, L * 0.22, H * 0.42), scale=(W * 0.35, L * 0.28, H * 0.26), colour="pink", seg=10, rings=8)
    z.box((W * 0.24, L * 0.30, H * 0.05), loc=(0, L * 0.22, H * 0.54), rot=(0, 0, 5), colour="cream", taper=0.8)

    z.cyl(W * 0.08, H * 0.55, loc=(0, -L * 0.06, H * 0.55), rot=(25, 0, 0), colour="white", seg=6)

    z.cone(W * 0.22, H * 0.22, loc=(0, -L * 0.20, H * 0.78), rot=(180, 0, 0), colour="pink", seg=3)
    z.mirror_x(z.ball, 1, loc=(W * 0.16, -L * 0.20, H * 0.82), scale=(W * 0.08, L * 0.08, H * 0.12), colour="lime", seg=6, rings=4)

    for dy_mult, rz in [(0.05, -15), (0.22, 25)]:
        dy = L * dy_mult
        z.mirror_x(z.box, (W * 0.32, L * 0.16, H * 0.04), loc=(W * 0.32, dy, H * 0.40), rot=(10, -25, rz), colour="pink", taper=0.6)
        z.mirror_x(z.box, (W * 0.04, L * 0.04, H * 0.42), loc=(W * 0.44, dy, H * 0.20), rot=(0, 20, rz), colour="white")

    z.mirror_x(z.box, (W * 0.05, L * 0.16, H * 0.08), loc=(W * 0.08, -L * 0.14, H * 0.50), rot=(55, 0, 15), colour="white")
    z.mirror_x(z.cone, W * 0.04, L * 0.18, loc=(W * 0.06, -L * 0.24, H * 0.40), rot=(-60, 0, 10), colour="pink", seg=4)


def _build_generic_bug(a, z, W, L, H, fur, marks):
    z.ball(1, loc=(0, L * 0.15, H * 0.45), scale=(W * 0.35, L * 0.35, H * 0.30), colour=fur, seg=8, rings=6)
    z.ball(1, loc=(0, -L * 0.25, H * 0.42), scale=(W * 0.25, L * 0.20, H * 0.22), colour="black", seg=8, rings=6)
    for dy in (-0.15, 0, 0.15):
        z.mirror_x(z.box, (W * 0.05, L * 0.04, H * 0.36), loc=(W * 0.25, L * dy, H * 0.18), rot=(0, 20, 0), colour="black")
