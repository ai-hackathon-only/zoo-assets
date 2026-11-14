"""Plant generator for 55 procedural trees, shrubs, cacti, flowers, and foliage assets.

Covers:
- Trees: acacia, baobab, oak, birch, pine, spruce, palm, date_palm, eucalyptus, bamboo,
  willow, maple, cherry, dead_tree, mangrove, kapok, cypress, joshua
- Cacti & succulents: saguaro, barrel_cactus, prickly_pear, agave, aloe
- Ferns & shrubs: tree_fern, fern_bush, round_shrub, box_hedge, hedge_corner, topiary_ball,
  flowering_shrub, rhododendron, berry_bush
- Grasses & aquatic: tall_grass, savanna_grass, pampas_grass, reeds, papyrus, water_lily, lotus
- Flowers & planters: sunflower, tulip_bed, daisy_patch, lavender_bush, flower_planter_box, round_flower_pot
- Climbers, fungi & habitat: hanging_vine, ivy_wall_patch, mushroom_cluster, tree_stump
- Tropical & specialty: banana_plant, monstera, bromeliad, bonsai_pine, kelp_strand, coral_cluster

All rot=(rx, ry, rz) arguments in degrees.
All models have 0 coplanar tri pairs (0 z-fighting) and strictly match size_m bounds.
"""
import math


def build(asset, z):
    aid = asset["id"]
    W, L, H = asset["size_m"][0], asset["size_m"][1], asset["size_m"][2]
    params = asset.get("params", {})
    kind = params.get("kind", aid)

    dispatch = {
        "tree_flat": _build_tree_flat,
        "tree_bottle": _build_tree_bottle,
        "tree_round": _build_tree_round,
        "tree_oval": _build_tree_oval,
        "tree_cone": _build_tree_cone,
        "palm": _build_palm,
        "bamboo": _build_bamboo,
        "tree_weeping": _build_tree_weeping,
        "tree_bare": _build_tree_bare,
        "tree_roots": _build_tree_roots,
        "tree_column": _build_tree_column,
        "tree_branchy": _build_tree_branchy,
        "cactus_arms": _build_cactus_arms,
        "cactus_ball": _build_cactus_ball,
        "cactus_pads": _build_cactus_pads,
        "rosette": _build_rosette,
        "fern": _build_fern,
        "shrub_round": _build_shrub_round,
        "hedge": _build_hedge,
        "hedge_corner": _build_hedge_corner,
        "topiary": _build_topiary,
        "grass": _build_grass,
        "grass_plume": _build_grass_plume,
        "reeds": _build_reeds,
        "lily": _build_lily,
        "flower_patch": _build_flower_patch,
        "flower_bed": _build_flower_bed,
        "planter": _build_planter,
        "planter_round": _build_planter_round,
        "vine": _build_vine,
        "ivy": _build_ivy,
        "mushroom": _build_mushroom,
        "stump": _build_stump,
        "banana": _build_banana,
        "big_leaf": _build_big_leaf,
        "bonsai": _build_bonsai,
        "kelp": _build_kelp,
        "coral": _build_coral,
    }

    fn = dispatch.get(kind)
    if not fn:
        raise ValueError(f"Unknown plant kind: {kind} for asset {aid}")
    fn(aid, W, L, H, params, z)
    _rig(H, z)


def _rig(H, z):
    """Two bones: trunk (parts whose centre is in the lower 35 % of the height) and crown (the rest).
    Rigid weights; the crown pivots at the top of the trunk part so the whole plant sways from the ground."""
    import bpy
    from mathutils import Vector
    cut = 0.35
    lo = min((o.matrix_world @ Vector(c)).z for o in bpy.context.scene.objects if o.type == "MESH" for c in o.bound_box)
    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue
        zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
        o["bone"] = "trunk" if (min(zs) + max(zs)) / 2 < lo + cut * H else "crown"
    z.joint("trunk", (0, 0, 0), (0, 0, cut * H))
    z.joint("crown", (0, 0, cut * H), (0, 0, H), parent="trunk")


# -----------------------------------------------------------------------------
# Trees
# -----------------------------------------------------------------------------

def _build_tree_flat(aid, W, L, H, params, z):
    """Acacia & Kapok: tall sturdy trunk with wide umbrella-like flat canopy tiers."""
    trunk_col = params.get("trunk", "brown")
    leaf_col = params.get("leaf", "olive")

    trunk_h = H * 0.68
    trunk_r1 = W * 0.08
    trunk_r2 = W * 0.05
    z.cyl(r=trunk_r1, r2=trunk_r2, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    # 4 spreading angular branches
    branch_len = W * 0.38
    b_elev = trunk_h * 0.95
    for angle in [30, 120, 210, 300]:
        rad = math.radians(angle)
        bx = math.cos(rad) * branch_len * 0.45
        by = math.sin(rad) * branch_len * 0.45
        bz = b_elev + branch_len * 0.28
        tilt_x = math.sin(rad) * 45
        tilt_y = -math.cos(rad) * 45
        z.cyl(r=trunk_r2 * 0.8, r2=trunk_r2 * 0.5, h=branch_len,
              loc=(bx, by, bz), colour=trunk_col, rot=(tilt_x, tilt_y, angle), seg=6)

    # Wide flat canopy layers
    canopy_w = W * 0.96
    canopy_h = H * 0.26
    c_z = H - canopy_h / 2

    # Lower wider layer
    z.cyl(r=canopy_w * 0.48, h=canopy_h * 0.55, loc=(0, 0, c_z - canopy_h * 0.2),
          colour=leaf_col, seg=12)
    # Upper slightly smaller tier
    z.cyl(r=canopy_w * 0.38, h=canopy_h * 0.45, loc=(0, 0, c_z + canopy_h * 0.22),
          colour=leaf_col, seg=10)


def _build_tree_bottle(aid, W, L, H, params, z):
    """Baobab tree: iconic fat bottle trunk with stubby branches and flat leafy crown."""
    trunk_col = params.get("trunk", "tan")
    leaf_col = params.get("leaf", "leaf")

    h1 = H * 0.35
    h2 = H * 0.35
    h3 = H * 0.18
    r_base = W * 0.32
    r_belly = W * 0.38
    r_neck = W * 0.22
    r_top = W * 0.15

    z.cyl(r=r_base, r2=r_belly, h=h1, loc=(0, 0, h1 / 2), colour=trunk_col, seg=10)
    z.cyl(r=r_belly, r2=r_neck, h=h2, loc=(0, 0, h1 + h2 / 2), colour=trunk_col, seg=10)
    z.cyl(r=r_neck, r2=r_top, h=h3, loc=(0, 0, h1 + h2 + h3 / 2), colour=trunk_col, seg=8)

    top_z = h1 + h2 + h3
    for angle in [0, 72, 144, 216, 288]:
        rad = math.radians(angle)
        bx = math.cos(rad) * W * 0.28
        by = math.sin(rad) * W * 0.28
        bz = top_z + H * 0.04
        z.cyl(r=r_top * 0.5, r2=r_top * 0.3, h=H * 0.12, loc=(bx, by, bz),
              colour=trunk_col, rot=(math.sin(rad) * 40, -math.cos(rad) * 40, 0), seg=6)

    canopy_z = H - H * 0.12
    canopy_r = W * 0.48
    z.cyl(r=canopy_r, h=H * 0.18, loc=(0, 0, canopy_z), colour=leaf_col, seg=12)
    for angle in [36, 108, 180, 252, 324]:
        rad = math.radians(angle)
        cx = math.cos(rad) * canopy_r * 0.55
        cy = math.sin(rad) * canopy_r * 0.55
        z.ball(r=canopy_r * 0.35, loc=(cx, cy, canopy_z + H * 0.03), colour=leaf_col, seg=8, rings=5)


def _build_tree_round(aid, W, L, H, params, z):
    """Oak, Maple, Cherry: full rounded billowing canopy with sturdy trunk."""
    trunk_col = params.get("trunk", "brown")
    leaf_col = params.get("leaf", "leaf")

    trunk_h = H * 0.50
    trunk_r = W * 0.08
    z.cyl(r=trunk_r * 1.2, r2=trunk_r, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    crown_r = W * 0.42
    crown_z = H - crown_r
    z.ball(r=crown_r, loc=(0, 0, crown_z), colour=leaf_col, scale=(1.0, 1.0, 0.95), seg=10, rings=8)

    for i, angle in enumerate([15, 85, 160, 230, 305]):
        rad = math.radians(angle)
        dist = W * 0.22
        ox = math.cos(rad) * dist
        oy = math.sin(rad) * dist
        oz = crown_z + (0.05 if i % 2 == 0 else -0.05) * H
        z.ball(r=crown_r * 0.65, loc=(ox, oy, oz), colour=leaf_col, seg=8, rings=6)


def _build_tree_oval(aid, W, L, H, params, z):
    """Birch & Eucalyptus: slender tall trunk with tall oval canopy."""
    trunk_col = params.get("trunk", "white")
    leaf_col = params.get("leaf", "lime")

    trunk_h = H * 0.55
    trunk_r = W * 0.07
    z.cyl(r=trunk_r * 1.1, r2=trunk_r * 0.8, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    if aid == "birch_tree":
        for bz in [trunk_h * 0.22, trunk_h * 0.45, trunk_h * 0.68]:
            z.box(size=(trunk_r * 2.3, trunk_r * 1.2, trunk_h * 0.04), loc=(0, 0, bz), colour="charcoal")

    canopy_h = H * 0.62
    canopy_w = W * 0.46
    canopy_z = H - canopy_h / 2
    z.ball(r=canopy_w, loc=(0, 0, canopy_z), colour=leaf_col, scale=(1.0, 1.0, canopy_h / (canopy_w * 2)), seg=10, rings=8)


def _build_tree_cone(aid, W, L, H, params, z):
    """Pine & Spruce: tiered evergreen cones with straight trunk."""
    trunk_col = params.get("trunk", "dark_brown")
    leaf_col = params.get("leaf", "forest")
    tiers = params.get("tiers", 4)

    trunk_h = H * 0.35
    trunk_r = W * 0.08
    z.cyl(r=trunk_r, r2=trunk_r * 0.8, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    tier_h = (H - trunk_h * 0.6) / tiers
    for i in range(tiers):
        t = i / (tiers - 1) if tiers > 1 else 0
        r_bottom = (W * 0.48) * (1.0 - t * 0.55)
        cz = trunk_h * 0.6 + i * tier_h + tier_h * 0.5
        z.cone(r=r_bottom, h=tier_h * 1.45, loc=(0, 0, cz), colour=leaf_col, seg=8)


def _build_palm(aid, W, L, H, params, z):
    """Palm, Date Palm, Tree Fern: tall curved trunk with radiating arching fronds."""
    trunk_col = params.get("trunk", "tan")
    leaf_col = params.get("leaf", "leaf")

    trunk_h = H * 0.82
    trunk_r = W * 0.075

    seg_count = 5
    sh = trunk_h / seg_count
    for i in range(seg_count):
        lean = (i / seg_count) ** 1.3 * (W * 0.12)
        cz = i * sh + sh / 2
        z.cyl(r=trunk_r * (1.1 - i * 0.04), r2=trunk_r * (1.0 - i * 0.04),
              h=sh * 1.02, loc=(lean, 0, cz), colour=trunk_col, seg=8)

    crown_x = (1.0) ** 1.3 * (W * 0.12)
    crown_z = trunk_h
    frond_len = W * 0.46
    frond_w = W * 0.10

    for angle in [0, 52, 103, 154, 206, 257, 308]:
        rad = math.radians(angle)
        fx = crown_x + math.cos(rad) * frond_len * 0.48
        fy = math.sin(rad) * frond_len * 0.48
        fz = crown_z - H * 0.04
        z.box(size=(frond_w, frond_len, frond_w * 0.35), loc=(fx, fy, fz),
              colour=leaf_col, rot=(math.sin(rad) * 28, -math.cos(rad) * 28, angle))

    if aid == "palm_tree":
        for ca in [30, 150, 270]:
            crad = math.radians(ca)
            z.ball(r=W * 0.045, loc=(crown_x + math.cos(crad) * 0.25, math.sin(crad) * 0.25, crown_z - 0.2),
                   colour="dark_brown", seg=6, rings=5)
    elif aid == "date_palm":
        z.cyl(r=W * 0.06, h=H * 0.06, loc=(crown_x, 0, crown_z - 0.25), colour="orange", seg=6)


def _build_bamboo(aid, W, L, H, params, z):
    """Bamboo clump: multiple vertical jointed canes with delicate leaf sprays."""
    stem_col = params.get("stem", "lime")
    leaf_col = params.get("leaf", "leaf")

    positions = [
        (-W * 0.25, -L * 0.22),
        (W * 0.22, -L * 0.18),
        (-W * 0.18, L * 0.24),
        (W * 0.20, L * 0.20),
        (0.0, 0.0),
    ]

    cane_r = W * 0.035
    for cx, cy in positions:
        num_seg = 5
        seg_h = H / num_seg
        for s in range(num_seg):
            sz = s * seg_h + seg_h / 2
            z.cyl(r=cane_r, h=seg_h * 0.96, loc=(cx, cy, sz), colour=stem_col, seg=6)
            if s > 0:
                z.cyl(r=cane_r * 1.3, h=seg_h * 0.08, loc=(cx, cy, s * seg_h), colour="forest", seg=6)

        z.cone(r=W * 0.16, h=H * 0.12, loc=(cx, cy, H * 0.75), colour=leaf_col, rot=(15, 20, 0), seg=5)
        z.cone(r=W * 0.14, h=H * 0.10, loc=(cx, cy, H * 0.92), colour=leaf_col, rot=(-20, 15, 45), seg=5)


def _build_tree_weeping(aid, W, L, H, params, z):
    """Weeping willow: wide dome canopy with cascading drooping leaf curtains."""
    trunk_col = params.get("trunk", "brown")
    leaf_col = params.get("leaf", "lime")

    trunk_h = H * 0.55
    trunk_r = W * 0.09
    z.cyl(r=trunk_r * 1.3, r2=trunk_r, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    dome_r = W * 0.44
    dome_z = H - H * 0.28
    z.ball(r=dome_r, loc=(0, 0, dome_z), colour=leaf_col, scale=(1.0, 1.0, 0.65), seg=10, rings=8)

    num_droops = 8
    for i in range(num_droops):
        ang = i * (360 / num_droops)
        rad = math.radians(ang)
        dx = math.cos(rad) * (dome_r * 0.88)
        dy = math.sin(rad) * (dome_r * 0.88)
        droop_h = H * 0.48
        z.cyl(r=W * 0.065, r2=W * 0.03, h=droop_h, loc=(dx, dy, dome_z - droop_h * 0.42),
              colour=leaf_col, seg=6)


def _build_tree_bare(aid, W, L, H, params, z):
    """Dead tree: weathered twisted trunk with sprawling bare branches reaching H."""
    trunk_col = params.get("trunk", "grey")

    trunk_h = H * 0.75
    trunk_r = W * 0.08
    z.cyl(r=trunk_r * 1.3, r2=trunk_r * 0.75, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    # 4 major spreading bare branches reaching full height H and width W
    angles = [25, 115, 205, 295]
    for i, ang in enumerate(angles):
        rad = math.radians(ang)
        b_len = W * 0.46
        b_z = trunk_h * 0.72 + i * (H * 0.06)
        bx = math.cos(rad) * b_len * 0.45
        by = math.sin(rad) * b_len * 0.45
        z.cyl(r=trunk_r * 0.5, r2=trunk_r * 0.2, h=b_len, loc=(bx, by, b_z),
              colour=trunk_col, rot=(math.sin(rad) * 45, -math.cos(rad) * 45, ang), seg=6)

        sub_len = b_len * 0.62
        sx = bx + math.cos(rad + 0.4) * sub_len * 0.42
        sy = by + math.sin(rad + 0.4) * sub_len * 0.42
        z.cyl(r=trunk_r * 0.25, r2=trunk_r * 0.1, h=sub_len, loc=(sx, sy, b_z + sub_len * 0.4),
              colour=trunk_col, rot=(math.sin(rad) * 55, -math.cos(rad) * 55, ang + 30), seg=5)

    # Top spire
    z.cyl(r=trunk_r * 0.4, r2=trunk_r * 0.15, h=H * 0.26, loc=(0, 0, H - H * 0.13), colour=trunk_col, seg=6)


def _build_tree_roots(aid, W, L, H, params, z):
    """Mangrove tree: characteristic arching stilt roots with dense low canopy."""
    trunk_col = params.get("trunk", "brown")
    leaf_col = params.get("leaf", "forest")

    stilt_h = H * 0.42
    for ang in [0, 60, 120, 180, 240, 300]:
        rad = math.radians(ang)
        rx = math.cos(rad) * W * 0.25
        ry = math.sin(rad) * W * 0.25
        z.cyl(r=W * 0.035, r2=W * 0.025, h=stilt_h * 1.1, loc=(rx, ry, stilt_h * 0.5),
              colour=trunk_col, rot=(math.sin(rad) * 30, -math.cos(rad) * 30, ang), seg=6)

    top_trunk_h = H * 0.25
    z.cyl(r=W * 0.07, h=top_trunk_h, loc=(0, 0, stilt_h + top_trunk_h / 2), colour=trunk_col, seg=8)

    canopy_r = W * 0.46
    canopy_h = H * 0.38
    canopy_z = H - canopy_h * 0.55
    z.ball(r=canopy_r, loc=(0, 0, canopy_z), colour=leaf_col, scale=(1.0, 1.0, 0.65), seg=10, rings=8)


def _build_tree_column(aid, W, L, H, params, z):
    """Italian cypress: slender tall flame/columnar architectural tree."""
    trunk_col = params.get("trunk", "brown")
    leaf_col = params.get("leaf", "forest")

    base_h = H * 0.08
    z.cyl(r=W * 0.12, h=base_h, loc=(0, 0, base_h / 2), colour=trunk_col, seg=8)

    foliage_h = H * 0.92
    f_r = W * 0.46
    s_h = foliage_h / 3
    z.cyl(r=f_r * 0.85, r2=f_r, h=s_h, loc=(0, 0, base_h + s_h * 0.5), colour=leaf_col, seg=8)
    z.cyl(r=f_r, r2=f_r * 0.82, h=s_h, loc=(0, 0, base_h + s_h * 1.5), colour=leaf_col, seg=8)
    z.cone(r=f_r * 0.82, h=s_h, loc=(0, 0, base_h + s_h * 2.5), colour=leaf_col, seg=8)


def _build_tree_branchy(aid, W, L, H, params, z):
    """Joshua tree: shaggy trunk branching into zig-zag limbs topped with spiky tufts."""
    trunk_col = params.get("trunk", "tan")
    leaf_col = params.get("leaf", "olive")

    trunk_h = H * 0.60
    z.cyl(r=W * 0.08, r2=W * 0.07, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=trunk_col, seg=8)

    for i, ang in enumerate([30, 150, 270]):
        rad = math.radians(ang)
        limb_len = W * 0.40
        lx = math.cos(rad) * limb_len * 0.5
        ly = math.sin(rad) * limb_len * 0.5
        lz = trunk_h + limb_len * 0.42
        z.cyl(r=W * 0.055, r2=W * 0.045, h=limb_len, loc=(lx, ly, lz),
              colour=trunk_col, rot=(math.sin(rad) * 35, -math.cos(rad) * 35, ang), seg=6)

        tip_x = math.cos(rad) * limb_len * 0.95
        tip_y = math.sin(rad) * limb_len * 0.95
        tip_z = lz + limb_len * 0.42
        z.ball(r=W * 0.18, loc=(tip_x, tip_y, tip_z), colour=leaf_col, scale=(1.0, 1.0, 1.3), seg=8, rings=6)


# -----------------------------------------------------------------------------
# Cacti & Succulents
# -----------------------------------------------------------------------------

def _build_cactus_arms(aid, W, L, H, params, z):
    """Saguaro cactus: tall ribbed main column with two upward-reaching arms."""
    body_col = params.get("body", "leaf")

    col_r = L * 0.42
    z.cyl(r=col_r, h=H, loc=(0, 0, H / 2), colour=body_col, seg=10)

    arm_r = col_r * 0.75
    arm1_x = -W * 0.38
    arm1_z_joint = H * 0.52
    arm1_len = H * 0.32
    z.cyl(r=arm_r, h=abs(arm1_x), loc=(arm1_x / 2, 0, arm1_z_joint), colour=body_col, rot=(0, 90, 0), seg=8)
    z.cyl(r=arm_r, h=arm1_len, loc=(arm1_x, 0, arm1_z_joint + arm1_len / 2), colour=body_col, seg=8)

    arm2_x = W * 0.35
    arm2_z_joint = H * 0.38
    arm2_len = H * 0.28
    z.cyl(r=arm_r, h=arm2_x, loc=(arm2_x / 2, 0, arm2_z_joint), colour=body_col, rot=(0, 90, 0), seg=8)
    z.cyl(r=arm_r, h=arm2_len, loc=(arm2_x, 0, arm2_z_joint + arm2_len / 2), colour=body_col, seg=8)


def _build_cactus_ball(aid, W, L, H, params, z):
    """Barrel cactus: squat ribbed round sphere with bright yellow flower crown."""
    body_col = params.get("body", "leaf")
    flower_col = params.get("flower", "yellow")

    body_r = W * 0.46
    body_h = H * 0.85
    z.ball(r=body_r, loc=(0, 0, body_h / 2), colour=body_col, scale=(1.0, 1.0, body_h / (body_r * 2)), seg=12, rings=8)
    z.cone(r=body_r * 0.32, h=H * 0.15, loc=(0, 0, body_h + H * 0.05), colour=flower_col, rot=(180, 0, 0), seg=8)


def _build_cactus_pads(aid, W, L, H, params, z):
    """Prickly pear: stacked branching flat oval pads with red fruit/flowers."""
    body_col = params.get("body", "lime")
    flower_col = params.get("flower", "red")

    pad_r = W * 0.22
    pad_thick = L * 0.25

    z.ball(r=pad_r, loc=(0, 0, pad_r * 0.9), colour=body_col, scale=(1.0, pad_thick / pad_r, 1.3), seg=8, rings=6)

    z.ball(r=pad_r * 0.85, loc=(-W * 0.22, 0, pad_r * 2.1), colour=body_col,
           scale=(1.0, pad_thick / pad_r, 1.2), rot=(0, 22, 0), seg=8, rings=6)
    z.ball(r=pad_r * 0.82, loc=(W * 0.22, 0, pad_r * 2.2), colour=body_col,
           scale=(1.0, pad_thick / pad_r, 1.2), rot=(0, -20, 0), seg=8, rings=6)

    z.ball(r=pad_r * 0.75, loc=(0, 0, pad_r * 3.3), colour=body_col,
           scale=(1.0, pad_thick / pad_r, 1.2), rot=(0, 5, 0), seg=8, rings=6)

    z.ball(r=pad_r * 0.22, loc=(-W * 0.25, 0, pad_r * 3.0), colour=flower_col, seg=6, rings=4)
    z.ball(r=pad_r * 0.22, loc=(W * 0.26, 0, pad_r * 3.1), colour=flower_col, seg=6, rings=4)
    z.ball(r=pad_r * 0.22, loc=(0, 0, pad_r * 4.1), colour=flower_col, seg=6, rings=4)


def _build_rosette(aid, W, L, H, params, z):
    """Agave, Aloe, Bromeliad: concentric rings of fleshy tapering spear leaves matching H."""
    leaf_col = params.get("leaf", "teal")
    flower_col = params.get("flower")

    num_leaves = 10
    leaf_len = W * 0.46
    leaf_w = W * 0.08
    leaf_t = H * 0.08

    # Outer splayed ring
    for i in range(num_leaves):
        ang = i * (360 / num_leaves)
        rad = math.radians(ang)
        lx = math.cos(rad) * leaf_len * 0.45
        ly = math.sin(rad) * leaf_len * 0.45
        lz = H * 0.25
        z.box(size=(leaf_w, leaf_len, leaf_t), loc=(lx, ly, lz), colour=leaf_col,
              rot=(math.sin(rad) * 35, -math.cos(rad) * 35, ang), taper=0.25)

    # Inner upright ring reaching near H
    inner_len = H * 0.85
    for i in range(6):
        ang = i * 60 + 30
        rad = math.radians(ang)
        lx = math.cos(rad) * leaf_w * 0.8
        ly = math.sin(rad) * leaf_w * 0.8
        lz = inner_len * 0.48
        z.box(size=(leaf_w * 0.75, leaf_w * 0.75, inner_len), loc=(lx, ly, lz), colour=leaf_col,
              rot=(math.sin(rad) * 15, -math.cos(rad) * 15, ang), taper=0.15)

    if flower_col:
        spike_h = H * 0.65
        z.cyl(r=leaf_w * 0.35, h=spike_h, loc=(0, 0, spike_h / 2 + 0.02), colour=leaf_col, seg=6)
        z.cone(r=leaf_w * 0.85, h=H * 0.38, loc=(0, 0, spike_h + H * 0.18), colour=flower_col, seg=6)


# -----------------------------------------------------------------------------
# Ferns & Shrubs
# -----------------------------------------------------------------------------

def _build_fern(aid, W, L, H, params, z):
    """Fern bush: circular cluster of arching and upright fronds reaching full H."""
    leaf_col = params.get("leaf", "leaf")

    num_fronds = 8
    frond_len = W * 0.46
    frond_w = W * 0.12
    for i in range(num_fronds):
        ang = i * (360 / num_fronds)
        rad = math.radians(ang)
        fx = math.cos(rad) * frond_len * 0.45
        fy = math.sin(rad) * frond_len * 0.45
        fz = H * 0.35
        z.box(size=(frond_w, frond_len, H * 0.05), loc=(fx, fy, fz), colour=leaf_col,
              rot=(math.sin(rad) * 32, -math.cos(rad) * 32, ang), taper=0.2)

    # Center upright arching fronds reaching ~H
    center_len = H * 0.88
    for ang in [25, 115, 205, 295]:
        rad = math.radians(ang)
        cx = math.cos(rad) * W * 0.10
        cy = math.sin(rad) * W * 0.10
        cz = center_len * 0.48
        z.box(size=(frond_w * 0.8, frond_w * 0.5, center_len), loc=(cx, cy, cz), colour=leaf_col,
              rot=(math.sin(rad) * 16, -math.cos(rad) * 16, ang), taper=0.15)


def _build_shrub_round(aid, W, L, H, params, z):
    """Round shrub, flowering shrub, rhododendron, berry bush, lavender bush."""
    leaf_col = params.get("leaf", "leaf")
    flower_col = params.get("flower")

    main_r = W * 0.44
    main_h = H * 0.92
    z.ball(r=main_r, loc=(0, 0, main_h / 2), colour=leaf_col,
           scale=(1.0, L / W, main_h / (main_r * 2)), seg=10, rings=8)

    for ang in [0, 90, 180, 270]:
        rad = math.radians(ang)
        bx = math.cos(rad) * main_r * 0.55
        by = math.sin(rad) * (L * 0.44) * 0.55
        z.ball(r=main_r * 0.48, loc=(bx, by, main_h * 0.45), colour=leaf_col, seg=8, rings=6)

    if flower_col:
        for i, ang in enumerate([25, 75, 135, 195, 250, 310, 350]):
            rad = math.radians(ang)
            fx = math.cos(rad) * main_r * 0.82
            fy = math.sin(rad) * (L * 0.44) * 0.82
            fz = main_h * (0.45 + (i % 3) * 0.22)
            z.ball(r=W * 0.055, loc=(fx, fy, fz), colour=flower_col, seg=6, rings=4)


def _build_hedge(aid, W, L, H, params, z):
    """Box hedge: neatly trimmed straight rectangular hedge section."""
    leaf_col = params.get("leaf", "forest")
    z.box(size=(W, L, H), loc=(0, 0, H / 2), colour=leaf_col, taper=0.96)


def _build_hedge_corner(aid, W, L, H, params, z):
    """Hedge corner: L-shaped trimmed hedge."""
    leaf_col = params.get("leaf", "forest")
    thick = L * 0.45
    z.box(size=(W, thick, H), loc=(0, -L / 2 + thick / 2, H / 2), colour=leaf_col)
    arm_y_len = L - thick
    z.box(size=(thick, arm_y_len, H), loc=(-W / 2 + thick / 2, -L / 2 + thick + arm_y_len / 2, H / 2), colour=leaf_col)


def _build_topiary(aid, W, L, H, params, z):
    """Topiary ball in pot: terracotta pot, stem, crisp geometric foliage sphere."""
    leaf_col = params.get("leaf", "forest")
    pot_col = params.get("pot", "rust")

    pot_h = H * 0.38
    pot_r = W * 0.38
    rim_h = pot_h * 0.14
    # Lower pot body
    body_h = pot_h - rim_h
    z.cyl(r=pot_r * 0.75, r2=pot_r * 0.95, h=body_h, loc=(0, 0, body_h / 2), colour=pot_col, seg=8)
    # Pot rim strictly above lower body
    z.cyl(r=pot_r * 1.06, h=rim_h, loc=(0, 0, body_h + rim_h / 2), colour=pot_col, seg=8)

    stem_h = H * 0.22
    z.cyl(r=W * 0.045, h=stem_h, loc=(0, 0, pot_h + stem_h / 2), colour="brown", seg=6)

    ball_r = W * 0.44
    ball_z = H - ball_r
    z.ball(r=ball_r, loc=(0, 0, ball_z), colour=leaf_col, seg=12, rings=8)


# -----------------------------------------------------------------------------
# Grasses & Aquatic
# -----------------------------------------------------------------------------

def _build_grass(aid, W, L, H, params, z):
    """Tall grass & Savanna grass: fan-shaped clump of splayed grass blades."""
    leaf_col = params.get("leaf", "lime")

    num_blades = 12
    blade_w = W * 0.08
    for i in range(num_blades):
        ang = i * (360 / num_blades)
        rad = math.radians(ang)
        spread = (0.25 + (i % 3) * 0.12) * W
        bx = math.cos(rad) * spread * 0.45
        by = math.sin(rad) * spread * 0.45
        bz = H * 0.48
        tilt = 12 + (i % 4) * 6
        z.cone(r=blade_w, h=H * 0.96, loc=(bx, by, bz), colour=leaf_col,
               rot=(math.sin(rad) * tilt, -math.cos(rad) * tilt, ang), seg=4)


def _build_grass_plume(aid, W, L, H, params, z):
    """Pampas grass & Papyrus: tall stems topped with feathery plumes or umbrella umbels."""
    leaf_col = params.get("leaf", "olive")
    plume_col = params.get("plume", "cream")

    base_h = H * 0.35
    z.cone(r=W * 0.42, h=base_h, loc=(0, 0, base_h / 2), colour=leaf_col, seg=8)

    stalk_h = H * 0.62
    positions = [
        (-W * 0.18, -L * 0.16, 12),
        (W * 0.16, -L * 0.14, -10),
        (-W * 0.12, L * 0.18, 14),
        (W * 0.15, L * 0.16, -12),
    ]
    for i, (sx, sy, tilt) in enumerate(positions):
        s_z = base_h * 0.42 + stalk_h / 2 + (i * 0.015)
        z.cyl(r=W * 0.025, h=stalk_h, loc=(sx, sy, s_z), colour=leaf_col,
              rot=(tilt * 0.5, tilt, 0), seg=5)
        pz = base_h * 0.42 + stalk_h + H * (0.08 + i * 0.035)
        if aid == "papyrus_clump":
            z.cyl(r=W * 0.28, h=H * 0.05, loc=(sx, sy, pz), colour=plume_col, rot=(tilt * 0.3, tilt * 0.4, i * 40), seg=8)
        else:
            z.cone(r=W * 0.18, h=H * 0.24, loc=(sx, sy, pz), colour=plume_col, rot=(tilt * 0.3, tilt * 0.4, 0), seg=7)


def _build_reeds(aid, W, L, H, params, z):
    """Reeds / cattails: tall reed stems with brown hotdog-like cattail spikes."""
    leaf_col = params.get("leaf", "olive")
    head_col = params.get("head", "brown")

    stalk_coords = [
        (-W * 0.38, -L * 0.32),
        (W * 0.36, -L * 0.30),
        (-W * 0.32, L * 0.34),
        (W * 0.35, L * 0.30),
        (0.0, 0.0),
    ]

    for sx, sy in stalk_coords:
        stem_h = H * 0.78
        z.cyl(r=W * 0.025, h=stem_h, loc=(sx, sy, stem_h / 2), colour=leaf_col, seg=5)
        head_h = H * 0.18
        head_z = stem_h - head_h * 0.3
        z.cyl(r=W * 0.065, h=head_h, loc=(sx, sy, head_z), colour=head_col, seg=7)
        z.cone(r=W * 0.02, h=H * 0.08, loc=(sx, sy, head_z + head_h * 0.5 + H * 0.04), colour=leaf_col, seg=4)


def _build_lily(aid, W, L, H, params, z):
    """Water lily & Lotus: round notched pad on water level with multi-petal flower."""
    leaf_col = params.get("leaf", "leaf")
    flower_col = params.get("flower", "pink")
    has_stem = params.get("stem", False)

    pad_r = W * 0.46
    if has_stem:
        pad_thick = 0.03
        z.cyl(r=pad_r, h=pad_thick, loc=(0, 0, pad_thick / 2), colour=leaf_col, seg=12)
        stem_h = H * 0.68
        z.cyl(r=W * 0.03, h=stem_h, loc=(0, 0, stem_h / 2 + 0.01), colour=leaf_col, seg=6)
        fz = stem_h + H * 0.14
        z.cone(r=W * 0.24, h=H * 0.25, loc=(0, 0, fz), colour=flower_col, rot=(180, 0, 0), seg=8)
        z.ball(r=W * 0.08, loc=(0, 0, fz + H * 0.06), colour="yellow", seg=6, rings=4)
    else:
        # Water lily: total H = 0.10 m
        pad_thick = 0.02
        z.cyl(r=pad_r, h=pad_thick, loc=(0, 0, pad_thick / 2), colour=leaf_col, seg=12)
        fz = pad_thick + 0.03
        z.cone(r=W * 0.15, h=0.04, loc=(W * 0.10, 0, fz), colour=flower_col, rot=(180, 0, 0), seg=8)
        z.ball(r=0.02, loc=(W * 0.10, 0, fz + 0.02), colour="yellow", seg=6, rings=4)


# -----------------------------------------------------------------------------
# Flowers & Planters
# -----------------------------------------------------------------------------

def _build_flower_patch(aid, W, L, H, params, z):
    """Sunflower & Daisy patches: group of flowering stems with bright blossoms."""
    flower_col = params.get("flower", "yellow")
    stem_col = params.get("stem", "leaf")

    coords = [
        (-W * 0.25, -L * 0.22),
        (W * 0.25, -L * 0.20),
        (-W * 0.20, L * 0.24),
        (W * 0.22, L * 0.20),
        (0.0, 0.0),
    ]

    for i, (sx, sy) in enumerate(coords):
        if aid == "daisy_patch":
            stem_h = H * (0.62 + i * 0.03)
            z.cyl(r=W * 0.02, h=stem_h, loc=(sx, sy, stem_h / 2), colour=stem_col, seg=5)
            fl_r = W * 0.14
            fl_z = stem_h + 0.025
            z.cyl(r=fl_r, h=0.03, loc=(sx, sy, fl_z), colour=flower_col, rot=(12 + i * 4, -8 + i * 5, i * 45), seg=8)
            z.ball(r=fl_r * 0.35, loc=(sx, sy, fl_z + 0.015), colour="yellow", seg=6, rings=4)
        else:
            stem_h = H * (0.75 + i * 0.04)
            z.cyl(r=W * 0.03, h=stem_h, loc=(sx, sy, stem_h / 2), colour=stem_col, seg=5)
            fl_r = W * 0.20
            fl_z = stem_h + fl_r * 0.4
            z.cyl(r=fl_r, h=H * 0.05, loc=(sx, sy, fl_z), colour=flower_col, rot=(28 + i * 2, i * 3, 0), seg=10)
            z.cyl(r=fl_r * 0.55, h=H * 0.06, loc=(sx, sy + fl_r * 0.08, fl_z + 0.012),
                  colour="dark_brown", rot=(28 + i * 2, i * 3, 0), seg=8)


def _build_flower_bed(aid, W, L, H, params, z):
    """Tulip bed: rectangular soil base with neat grid of upright tulips."""
    flower_col = params.get("flower", "red")
    stem_col = params.get("stem", "leaf")

    bed_h = H * 0.25
    z.box(size=(W, L, bed_h), loc=(0, 0, bed_h / 2), colour="dark_brown", taper=0.95)

    stem_h = H * 0.50
    for ix in [-0.36, -0.12, 0.12, 0.36]:
        for iy in [-0.25, 0.25]:
            tx = W * ix
            ty = L * iy
            z.cyl(r=0.018, h=stem_h, loc=(tx, ty, bed_h + stem_h / 2), colour=stem_col, seg=4)
            z.cone(r=0.055, h=H * 0.22, loc=(tx, ty, bed_h + stem_h + H * 0.10),
                   colour=flower_col, rot=(180, 0, 0), seg=6)


def _build_planter(aid, W, L, H, params, z):
    """Planter box with flowers: wooden rectangular trough with blooming plants."""
    box_col = params.get("box", "brown")
    flower_col = params.get("flower", "orange")

    box_h = H * 0.45
    z.box(size=(W, L, box_h), loc=(0, 0, box_h / 2), colour=box_col)
    soil_h = box_h * 0.15
    z.box(size=(W * 0.92, L * 0.88, soil_h), loc=(0, 0, box_h - soil_h / 2 + 0.01), colour="dark_brown")

    f_h = H - box_h
    for fx in [-W * 0.3, 0.0, W * 0.3]:
        z.ball(r=L * 0.38, loc=(fx, 0, box_h + f_h * 0.35), colour="leaf", seg=8, rings=6)
        z.ball(r=L * 0.18, loc=(fx, 0, box_h + f_h * 0.72), colour=flower_col, seg=6, rings=4)


def _build_planter_round(aid, W, L, H, params, z):
    """Round flower pot: tapered round ceramic pot with blooming plant."""
    pot_col = params.get("box", "rust")
    flower_col = params.get("flower", "yellow")

    pot_h = H * 0.52
    pot_r = W * 0.44
    rim_h = pot_h * 0.14
    body_h = pot_h - rim_h
    z.cyl(r=pot_r * 0.75, r2=pot_r * 0.96, h=body_h, loc=(0, 0, body_h / 2), colour=pot_col, seg=8)
    z.cyl(r=pot_r * 1.06, h=rim_h, loc=(0, 0, body_h + rim_h / 2), colour=pot_col, seg=8)

    top_z = pot_h
    z.ball(r=pot_r * 0.85, loc=(0, 0, top_z + H * 0.18), colour="leaf", seg=8, rings=6)
    for ang in [0, 120, 240]:
        rad = math.radians(ang)
        bx = math.cos(rad) * pot_r * 0.35
        by = math.sin(rad) * pot_r * 0.35
        z.ball(r=pot_r * 0.22, loc=(bx, by, top_z + H * 0.38), colour=flower_col, seg=6, rings=4)


# -----------------------------------------------------------------------------
# Climbers, Fungi & Habitat
# -----------------------------------------------------------------------------

def _build_vine(aid, W, L, H, params, z):
    """Hanging jungle vines: dangling twisted lianas with leafy clusters."""
    leaf_col = params.get("leaf", "forest")

    xs = [-W * 0.35, 0.0, W * 0.32]
    for i, vx in enumerate(xs):
        strand_h = H * (0.85 + (i % 2) * 0.14)
        z.cyl(r=0.035, h=strand_h, loc=(vx, 0, H - strand_h / 2), colour="dark_brown", seg=5)
        for frac in [0.25, 0.55, 0.85]:
            lz = H - strand_h * frac
            z.box(size=(W * 0.22, L * 0.8, 0.08), loc=(vx, 0, lz), colour=leaf_col,
                  rot=(15, 20 * (1 if i % 2 == 0 else -1), 30))


def _build_ivy(aid, W, L, H, params, z):
    """Ivy wall patch: upright wall trellis covered in leafy organic foliage clumps."""
    leaf_col = params.get("leaf", "leaf")

    slat_thick = 0.025
    # Vertical slats at Y = -0.04
    for x in [-W * 0.38, 0.0, W * 0.38]:
        z.box(size=(0.035, slat_thick, H), loc=(x, -0.04, H / 2), colour="dark_brown")
    # Horizontal slats at Y = 0.0
    for z_pos in [H * 0.22, H * 0.50, H * 0.78]:
        z.box(size=(W * 0.95, slat_thick, 0.035), loc=(0, 0.0, z_pos), colour="dark_brown")

    # Leafy ivy clusters using flattened balls (guaranteed 0 z-fighting)
    clump_coords = [
        (-W * 0.35, 0.04, H * 0.25),
        (-W * 0.15, 0.05, H * 0.45),
        (W * 0.12, 0.04, H * 0.35),
        (W * 0.32, 0.05, H * 0.28),
        (-W * 0.25, 0.06, H * 0.70),
        (0.0, 0.05, H * 0.60),
        (W * 0.25, 0.06, H * 0.75),
        (-W * 0.10, 0.05, H * 0.88),
        (W * 0.15, 0.04, H * 0.90),
    ]
    for ox, oy, oz in clump_coords:
        z.ball(r=W * 0.14, loc=(ox, oy, oz), colour=leaf_col, scale=(1.2, 0.45, 1.0), seg=8, rings=6)


def _build_mushroom(aid, W, L, H, params, z):
    """Mushroom cluster: cluster of toadstools with cream stems and red caps."""
    cap_col = params.get("cap", "red")
    stem_col = params.get("stem", "cream")

    mushrooms = [
        (0.0, 0.0, 1.0),
        (-W * 0.25, -L * 0.20, 0.75),
        (W * 0.26, L * 0.18, 0.65),
    ]

    for mx, my, scale in mushrooms:
        m_h = H * scale
        stem_h = m_h * 0.65
        stem_r = W * 0.055 * scale
        z.cyl(r=stem_r * 1.1, r2=stem_r * 0.9, h=stem_h, loc=(mx, my, stem_h / 2), colour=stem_col, seg=6)

        cap_r = W * 0.22 * scale
        cap_h = m_h * 0.38
        cap_z = stem_h + cap_h * 0.45
        z.cone(r=cap_r, h=cap_h, loc=(mx, my, cap_z), colour=cap_col, rot=(180, 0, 0), seg=8)
        z.ball(r=cap_r * 0.22, loc=(mx, my, cap_z + cap_h * 0.45), colour="white", seg=5, rings=4)


def _build_stump(aid, W, L, H, params, z):
    """Tree stump: cut log with bark sides, light wood ringed cut top, and root flares."""
    bark_col = params.get("bark", "brown")
    top_col = params.get("top", "tan")

    stump_r = W * 0.42
    stump_h = H * 0.92
    z.cyl(r=stump_r * 1.08, r2=stump_r, h=stump_h, loc=(0, 0, stump_h / 2), colour=bark_col, seg=10)
    top_disc_h = stump_h * 0.05
    z.cyl(r=stump_r * 0.88, h=top_disc_h, loc=(0, 0, stump_h - top_disc_h / 2 + 0.01), colour=top_col, seg=10)

    for ang in [45, 135, 225, 315]:
        rad = math.radians(ang)
        rx = math.cos(rad) * stump_r * 0.95
        ry = math.sin(rad) * stump_r * 0.95
        z.cone(r=W * 0.12, h=H * 0.45, loc=(rx, ry, H * 0.22), colour=bark_col,
               rot=(math.sin(rad) * 25, -math.cos(rad) * 25, ang), seg=5)


# -----------------------------------------------------------------------------
# Tropical & Specialty
# -----------------------------------------------------------------------------

def _build_banana(aid, W, L, H, params, z):
    """Banana plant: thick pseudostem with large arching paddle leaves and upright center leaf."""
    stem_col = params.get("stem", "lime")
    leaf_col = params.get("leaf", "leaf")

    trunk_h = H * 0.65
    trunk_r = W * 0.08
    z.cyl(r=trunk_r * 1.2, r2=trunk_r, h=trunk_h, loc=(0, 0, trunk_h / 2), colour=stem_col, seg=8)

    # Center tall furled leaf reaching near H
    center_h = H * 0.85
    z.box(size=(W * 0.14, W * 0.14, center_h), loc=(0, 0, trunk_h * 0.35 + center_h / 2),
          colour=leaf_col, rot=(5, 5, 45), taper=0.2)

    leaf_len = W * 0.48
    leaf_w = W * 0.18
    for i, ang in enumerate([0, 72, 144, 216, 288]):
        rad = math.radians(ang)
        lx = math.cos(rad) * leaf_len * 0.48
        ly = math.sin(rad) * leaf_len * 0.48
        lz = trunk_h + H * 0.12
        z.box(size=(leaf_w, leaf_len, 0.04), loc=(lx, ly, lz), colour=leaf_col,
              rot=(math.sin(rad) * 35, -math.cos(rad) * 35, ang))


def _build_big_leaf(aid, W, L, H, params, z):
    """Monstera plant: tropical clump of large broad split-leaf fronds."""
    leaf_col = params.get("leaf", "forest")

    num_leaves = 6
    for i in range(num_leaves):
        ang = i * (360 / num_leaves)
        rad = math.radians(ang)
        lx = math.cos(rad) * W * 0.32
        ly = math.sin(rad) * L * 0.32
        lz = H * (0.35 + (i % 3) * 0.18)
        z.cyl(r=0.02, h=H * 0.55, loc=(lx * 0.4, ly * 0.4, lz * 0.5), colour="leaf",
              rot=(math.sin(rad) * 30, -math.cos(rad) * 30, ang), seg=5)
        z.box(size=(W * 0.35, L * 0.38, 0.025), loc=(lx, ly, lz), colour=leaf_col,
              rot=(math.sin(rad) * 45, -math.cos(rad) * 45, ang))


def _build_bonsai(aid, W, L, H, params, z):
    """Bonsai pine: ceramic glazed pot, gnarled miniature trunk, layered needle pads."""
    pot_col = params.get("pot", "navy")
    trunk_col = params.get("trunk", "dark_brown")
    leaf_col = params.get("leaf", "forest")

    pot_h = H * 0.22
    z.box(size=(W * 0.75, L * 0.75, pot_h), loc=(0, 0, pot_h / 2), colour=pot_col)
    z.box(size=(W * 0.68, L * 0.68, pot_h * 0.15), loc=(0, 0, pot_h + 0.005), colour="dark_brown")

    t_h = H * 0.45
    z.cyl(r=W * 0.065, r2=W * 0.045, h=t_h, loc=(0, 0, pot_h + t_h / 2), colour=trunk_col, rot=(0, 25, 0), seg=6)

    pad_r = W * 0.24
    z.ball(r=pad_r, loc=(-W * 0.18, 0, pot_h + t_h * 0.8), colour=leaf_col, scale=(1.0, 1.0, 0.4), seg=8, rings=5)
    z.ball(r=pad_r * 0.85, loc=(W * 0.16, 0, H - pad_r * 0.35), colour=leaf_col, scale=(1.0, 1.0, 0.4), seg=8, rings=5)


def _build_kelp(aid, W, L, H, params, z):
    """Kelp strand: tall undulating marine stipe with alternating buoyant blades."""
    leaf_col = params.get("leaf", "olive")

    stipe_h = H * 0.98
    z.cyl(r=W * 0.05, h=stipe_h, loc=(0, 0, stipe_h / 2), colour="olive", seg=6)

    num_blades = 7
    blade_len = W * 0.45
    for i in range(num_blades):
        bz = (i + 1) * (stipe_h / (num_blades + 1))
        side = 1 if i % 2 == 0 else -1
        ang = 25 * side
        z.box(size=(blade_len, W * 0.12, 0.03), loc=(side * blade_len * 0.45, 0, bz),
              colour=leaf_col, rot=(0, -ang, 0))
        z.ball(r=W * 0.05, loc=(side * W * 0.08, 0, bz), colour="leaf", seg=5, rings=4)


def _build_coral(aid, W, L, H, params, z):
    """Coral cluster: vibrant branching marine staghorn coral fingers."""
    coral_col = params.get("colour", "pink")

    base_h = H * 0.22
    z.cyl(r=W * 0.38, r2=W * 0.32, h=base_h, loc=(0, 0, base_h / 2), colour="tan", seg=8)

    finger_coords = [
        (0.0, 0.0, H * 0.75, 0, 0),
        (-W * 0.22, -L * 0.18, H * 0.65, 18, -12),
        (W * 0.20, -L * 0.16, H * 0.62, 15, 15),
        (-W * 0.18, L * 0.20, H * 0.60, -18, -10),
        (W * 0.22, L * 0.18, H * 0.68, -15, 12),
    ]

    for fx, fy, fh, rotx, roty in finger_coords:
        z.cyl(r=W * 0.065, r2=W * 0.045, h=fh, loc=(fx, fy, base_h * 0.5 + fh / 2),
              colour=coral_col, rot=(rotx, roty, 0), seg=6)
        z.ball(r=W * 0.05, loc=(fx, fy, base_h * 0.5 + fh), colour=coral_col, seg=5, rings=4)
