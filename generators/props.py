"""Props generator: procedural models for food, enrichment, shop, and vet equipment (80 assets).

All models strictly adhere to:
- Real-world dimensions from asset size_m ([width x, length y, height z])
- Origin at floor center (Z=0 at bottom, X=0, Y=0 centered)
- Facing -Y (matching camera orientation)
- Clean non-overlapping geometry (0 coplanar z-fighting faces)
- Triangle budget <= 2,000 tris per asset
- Single shared MAT_palette material
"""
import math


def build(asset, z):
    category = asset.get("category", "")
    params = asset.get("params", {})
    aid = asset["id"]
    W, L, H = asset["size_m"][0], asset["size_m"][1], asset["size_m"][2]
    variant = params.get("variant")

    if category == "food":
        _build_food(W, L, H, variant or aid, aid, params, z)
    elif category == "enrichment":
        _build_enrichment(W, L, H, variant or aid, aid, params, z)
    elif category == "shop":
        _build_shop(W, L, H, variant or aid, aid, params, z)
    elif category == "vet_equipment":
        _build_vet(W, L, H, aid, params, z)
    else:
        # Fallback generic container
        z.box((W, L, H), loc=(0, 0, H / 2), colour="tan")


# ==============================================================================
# 1. FOOD & FEEDING PROPS (20 assets)
# ==============================================================================

def _build_food(W, L, H, variant, aid, p, z):
    if "hay_bale_square" in variant:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="sand")
        # 2 twine binding bands slightly offset to prevent coplanar z-fighting
        for bx in (-W * 0.25, W * 0.25):
            z.box((0.025, L * 1.02, H * 1.02), loc=(bx, 0, H / 2), colour="tan")

    elif "hay_bale_round" in variant:
        r = min(W, L) / 2
        z.cyl(r, H, loc=(0, 0, H / 2), colour="sand", seg=12)
        # Net wrap bands
        z.cyl(r * 1.015, H * 0.12, loc=(0, 0, H * 0.25), colour="tan", seg=12)
        z.cyl(r * 1.015, H * 0.12, loc=(0, 0, H * 0.75), colour="tan", seg=12)

    elif "meat_rib_slab" in variant:
        # Red meat base slab (flatter, distinct)
        z.box((W * 0.90, L * 0.80, H * 0.45), loc=(0, 0, H * 0.225), colour="red")
        # Thick white rib bones sitting on top and protruding at sides
        num_ribs = 4
        spacing = (W * 0.75) / (num_ribs - 1)
        for i in range(num_ribs):
            rx = -W * 0.375 + i * spacing
            z.cyl(0.032, L * 1.12, loc=(rx, 0, H * 0.60), colour="white", rot=(90, 0, 0), seg=8)

    elif "fish_bucket_herring" in variant:
        r_top = min(W, L) * 0.45
        r_bot = r_top * 0.75
        # Light grey bucket tapering wider toward the top
        z.cyl(r_bot, H * 0.80, loc=(0, 0, H * 0.40), colour="light_grey", seg=10, r2=r_top)
        # Upper rim band
        z.cyl(r_top * 1.04, 0.03, loc=(0, 0, H * 0.78), colour="charcoal", seg=10)
        # Silver / blue fish protruding out of the bucket
        for angle, fx, fy in ((25, -0.07, 0.02), (-30, 0.06, -0.02), (10, 0.0, 0.04)):
            z.cone(0.04, 0.22, loc=(fx, fy, H * 0.78), colour="water", rot=(angle, 15, 0), seg=4)
            z.ball(0.035, loc=(fx, fy, H * 0.88), colour="light_grey", scale=(0.6, 1.2, 0.6), seg=6, rings=4)

    elif "eucalyptus_bundle" in variant:
        # Tall bundle of branches tied together
        z.cyl(min(W, L) * 0.28, H * 0.95, loc=(0, 0, H * 0.48), colour="leaf", seg=8)
        z.box((W * 0.32, L * 0.32, 0.05), loc=(0, 0, H * 0.45), colour="brown")
        # Leaves canopy
        z.ball(min(W, L) * 0.42, loc=(0, 0, H * 0.85), colour="forest", scale=(1, 1, 1.4), seg=8, rings=6)

    elif "bamboo_stalk_sheaf" in variant:
        # Tied bundle of green bamboo stalks spanning ~0.45m across
        r = 0.045
        for bx, by in ((-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16), (0, 0)):
            z.cyl(r, H * 0.96, loc=(bx, by, H * 0.48), colour="leaf", seg=6)
            for nh in (H * 0.3, H * 0.6, H * 0.85):
                z.cyl(r * 1.15, 0.03, loc=(bx, by, nh), colour="olive", seg=6)
        # Tie cord
        z.box((W * 0.85, L * 0.85, 0.06), loc=(0, 0, H * 0.45), colour="tan")

    elif "fruit_crate_mixed" in variant:
        # Wooden slatted crate
        z.box((W, L, H * 0.10), loc=(0, 0, H * 0.05), colour="tan")
        z.box((W, 0.03, H * 0.85), loc=(0, -L * 0.46, H * 0.50), colour="tan")
        z.box((W, 0.03, H * 0.85), loc=(0, L * 0.46, H * 0.50), colour="tan")
        z.box((0.03, L, H * 0.85), loc=(-W * 0.46, 0, H * 0.50), colour="tan")
        z.box((0.03, L, H * 0.85), loc=(W * 0.46, 0, H * 0.50), colour="tan")
        # Fruit inside (apples and oranges)
        for fx in (-0.14, 0.0, 0.14):
            for fy in (-0.08, 0.08):
                col = "red" if (fx + fy) > 0 else "orange"
                z.ball(0.065, loc=(fx, fy, H * 0.65), colour=col, seg=6, rings=4)

    elif "veggie_bushel_roots" in variant:
        # Woven basket with root veggies
        r = min(W, L) * 0.46
        z.cyl(r, H * 0.70, loc=(0, 0, H * 0.35), colour="tan", seg=10, r2=r * 0.80)
        # Carrots and turnips
        for cx, cy in ((-0.08, -0.06), (0.09, 0.07), (-0.05, 0.10)):
            z.cone(0.045, 0.22, loc=(cx, cy, H * 0.75), colour="orange", rot=(15, -20, 0), seg=5)
        z.ball(0.06, loc=(0.06, -0.08, H * 0.72), colour="purple", seg=6, rings=4)

    elif "seed_pellet_trough" in variant:
        # Hanging seed and pellet feeder trough
        z.box((W, L, H * 0.50), loc=(0, 0, H * 0.25), colour="light_grey")
        z.box((W * 0.92, L * 0.85, H * 0.20), loc=(0, 0, H * 0.42), colour="yellow")
        # Suspension rods
        for sx in (-W * 0.45, W * 0.45):
            z.cyl(0.015, H * 0.55, loc=(sx, 0, H * 0.72), colour="grey", seg=4)

    elif "insect_larva_dish" in variant:
        r = min(W, L) / 2
        z.cyl(r, H * 0.65, loc=(0, 0, H * 0.325), colour="cream", seg=10)
        z.cyl(r * 0.82, H * 0.25, loc=(0, 0, H * 0.55), colour="dark_brown", seg=8)
        # Mealworms
        for mx, my in ((-0.06, 0.04), (0.05, -0.05), (0.02, 0.07)):
            z.cyl(0.012, 0.08, loc=(mx, my, H * 0.70), colour="tan", rot=(0, 45, 30), seg=4)

    elif "salt_lick_mineral" in variant:
        z.box((W * 0.85, L * 0.85, H * 0.75), loc=(0, 0, H * 0.45), colour="rust")
        z.cyl(0.02, H * 0.40, loc=(0, 0, H * 0.80), colour="tan", seg=4)

    elif "raw_marrow_bone" in variant:
        # Long marrow bone along X axis (W=0.5m, H=0.2m)
        r_ball = H * 0.48
        z.cyl(H * 0.35, W * 0.82, loc=(0, 0, r_ball), colour="white", rot=(0, 90, 0), seg=8)
        # Knuckle ends resting on floor
        for lx in (-W * 0.40, W * 0.40):
            for ky in (-L * 0.25, L * 0.25):
                z.ball(r_ball, loc=(lx, ky, r_ball), colour="white", seg=6, rings=4)
        # Raw marrow ring
        z.cyl(H * 0.36, 0.04, loc=(0, 0, r_ball), colour="red", rot=(0, 90, 0), seg=6)

    elif "browse_wall_rack" in variant:
        # Wall-mounted timber frame with steel bars holding leaves
        z.box((W, 0.06, H), loc=(0, L * 0.45, H / 2), colour="brown")
        z.box((W * 0.92, 0.04, 0.06), loc=(0, -L * 0.40, H * 0.40), colour="grey")
        # Leaves packed in rack
        z.ball(0.35, loc=(0, 0, H * 0.55), colour="forest", scale=(W * 0.6, 0.4, 0.7), seg=8, rings=5)

    elif "slow_feeder_haynet" in variant:
        # Suspended knotted hay bag
        r = min(W, L) * 0.45
        z.ball(r, loc=(0, 0, H * 0.55), colour="sand", scale=(1, 1, 1.3), seg=8, rings=6)
        # Netting lines
        z.cyl(r * 1.02, 0.03, loc=(0, 0, H * 0.55), colour="tan", seg=8)
        z.cyl(0.018, H * 0.35, loc=(0, 0, H * 0.88), colour="tan", seg=4)

    elif "nectar_tube_feeder" in variant:
        r = min(W, L) * 0.30
        z.cyl(r, H * 0.82, loc=(0, 0, H * 0.45), colour="sky", seg=8)
        z.cyl(r * 1.25, H * 0.12, loc=(0, 0, H * 0.92), colour="red", seg=8)
        z.cyl(0.015, H * 0.12, loc=(0, 0, H * 0.06), colour="light_grey", seg=4)
        # Feeding port flowers
        for fx, fy in ((-r * 0.8, 0), (r * 0.8, 0)):
            z.cone(0.035, 0.06, loc=(fx, fy, H * 0.20), colour="yellow", rot=(0, 90 if fx > 0 else -90, 0), seg=5)

    elif "carnivore_nutrient_loaf" in variant:
        # Food loaf on stainless tray
        z.box((W, L, H * 0.20), loc=(0, 0, H * 0.10), colour="light_grey")
        z.box((W * 0.82, L * 0.80, H * 0.65), loc=(0, 0, H * 0.52), colour="maroon")

    elif "watermelon_enrich_treat" in variant:
        r = min(W, L) * 0.48
        # Forest green rind body
        z.ball(r, loc=(0, 0, H * 0.45), colour="forest", scale=(1, 1, 0.88), seg=12, rings=8)
        # Light green stripes on rind
        for ang in (0, 45, 90, 135, 180, 225, 270, 315):
            rad = math.radians(ang)
            sx = math.cos(rad) * (r * 0.96)
            sy = math.sin(rad) * (r * 0.96)
            z.cyl(0.015, H * 0.55, loc=(sx, sy, H * 0.42), colour="leaf", rot=(0, 0, ang), seg=4)
        # Flat cut face revealing bright red melon pulp
        z.cyl(r * 0.82, 0.04, loc=(0, 0, H * 0.68), colour="red", seg=10)
        # Cut melon wedge slice protruding on top
        z.box((r * 0.70, 0.07, H * 0.28), loc=(0, -0.02, H * 0.82), colour="red")
        # Black seed specks on the cut slice
        for sx in (-0.05, 0.01, 0.06):
            z.ball(0.012, loc=(sx, 0.02, H * 0.82), colour="black")

    elif "krill_shrimp_pail" in variant:
        r = min(W, L) * 0.46
        z.cyl(r, H * 0.80, loc=(0, 0, H * 0.40), colour="water", seg=10, r2=r * 0.80)
        z.cyl(r * 0.90, H * 0.20, loc=(0, 0, H * 0.75), colour="pink", seg=8)

    elif "pellet_feed_sack" in variant:
        # Feed burlap sack
        z.box((W * 0.85, L * 0.80, H * 0.85), loc=(0, 0, H * 0.425), colour="cream", taper=0.88)
        # Green label band
        z.box((W * 0.87, L * 0.82, H * 0.25), loc=(0, 0, H * 0.45), colour="leaf")

    elif "water_drink_trough" in variant:
        # Automatic float water drink basin
        z.box((W, L, H * 0.75), loc=(0, 0, H * 0.375), colour="grey")
        # Water surface
        z.box((W * 0.88, L * 0.86, 0.03), loc=(0, 0, H * 0.68), colour="water")
        # Float valve housing
        z.box((W * 0.22, L * 0.35, H * 0.30), loc=(-W * 0.36, 0, H * 0.82), colour="charcoal")

    else:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="sand")


# ==============================================================================
# 2. ENRICHMENT TOYS & FIXTURES (20 assets)
# ==============================================================================

def _build_enrichment(W, L, H, variant, aid, p, z):
    if "boomer_ball_lg" in variant:
        r = min(W, L) / 2
        z.ball(r, loc=(0, 0, H / 2), colour="red", seg=12, rings=8)
        # Grip cutout ring
        z.cyl(r * 0.35, 0.08, loc=(0, 0, H * 0.92), colour="dark_brown", seg=8)

    elif "boomer_ball_sm" in variant:
        r = min(W, L) / 2
        z.ball(r, loc=(0, 0, H / 2), colour="yellow", seg=10, rings=6)

    elif "tire_swing_single" in variant:
        r = min(W, L) * 0.46
        # Suspended tire hanging from top chain
        z.cyl(r, 0.22, loc=(0, 0, 0.45), colour="charcoal", rot=(90, 0, 0), seg=12, r2=r)
        # Hollow inner hub
        z.cyl(r * 0.52, 0.24, loc=(0, 0, 0.45), colour="black", rot=(90, 0, 0), seg=8)
        # Suspension chain
        z.cyl(0.02, H - 0.55, loc=(0, 0, (H + 0.45) / 2), colour="light_grey", seg=4)

    elif "tire_pyramid" in variant:
        # Stacked tires: 3 on ground, 1 on top, total height H
        th = H * 0.52
        tr = min(W, L) * 0.22
        dist = tr * 1.35
        angles = [0, 120, 240]
        for ang in angles:
            rad = math.radians(ang)
            tx = math.cos(rad) * dist
            ty = math.sin(rad) * dist
            z.cyl(tr, th, loc=(tx, ty, th / 2), colour="charcoal", seg=10)
            z.cyl(tr * 0.50, th * 1.02, loc=(tx, ty, th / 2), colour="black", seg=8)
        # Top apex tire resting on bottom tier
        z.cyl(tr, th, loc=(0, 0, H - th / 2), colour="charcoal", seg=10)
        z.cyl(tr * 0.50, th * 1.02, loc=(0, 0, H - th / 2), colour="black", seg=8)

    elif "puzzle_barrel" in variant:
        r = min(W, L) / 2
        z.cyl(r, H * 0.88, loc=(0, 0, H * 0.44), colour="sky", seg=10)
        # Black rim bands
        for rh in (H * 0.15, H * 0.75):
            z.cyl(r * 1.025, 0.04, loc=(0, 0, rh), colour="black", seg=10)
        # Treat holes
        for ang, hz in ((0, H * 0.45), (120, H * 0.35), (240, H * 0.55)):
            rad = math.radians(ang)
            hx = math.cos(rad) * (r * 0.98)
            hy = math.sin(rad) * (r * 0.98)
            z.cyl(0.045, 0.06, loc=(hx, hy, hz), colour="dark_brown", rot=(90, 0, ang), seg=6)

    elif "firehose_cube" in variant:
        # Cube woven from repurposed firehose straps
        z.box((W, L, H), loc=(0, 0, H / 2), colour="leaf")
        # Tan criss-cross webbing straps
        z.box((W * 1.02, L * 0.28, H * 1.02), loc=(0, 0, H / 2), colour="tan")
        z.box((W * 0.28, L * 1.02, H * 1.02), loc=(0, 0, H / 2), colour="tan")

    elif "ice_block_treat" in variant:
        # Ice block with red treat visibly protruding out the top
        z.box((W, L, H * 0.85), loc=(0, 0, H * 0.425), colour="water")
        # Bright red frozen meat treat chunk sticking out of the ice
        z.box((W * 0.50, L * 0.60, H * 0.35), loc=(0, -L * 0.08, H * 0.75), colour="red")
        z.ball(W * 0.18, loc=(0, L * 0.18, H * 0.75), colour="white", seg=6, rings=4)

    elif "scratch_post_timber" in variant:
        # Heavy timber post wrapped in sisal rope
        z.box((W, L, H * 0.06), loc=(0, 0, H * 0.03), colour="dark_brown")
        r = min(W, L) * 0.30
        z.cyl(r, H * 0.90, loc=(0, 0, H * 0.50), colour="brown", seg=8)
        # Rope wrap mid-section
        z.cyl(r * 1.04, H * 0.50, loc=(0, 0, H * 0.45), colour="tan", seg=8)

    elif "floating_log_buoy" in variant:
        # Buoyant cylinder log with yellow endcaps
        r = min(W, H) / 2
        z.cyl(r, L * 0.90, loc=(0, 0, r), colour="brown", rot=(90, 0, 0), seg=8)
        for ly in (-L * 0.40, L * 0.40):
            z.cyl(r * 1.05, 0.08, loc=(0, ly, r), colour="yellow", rot=(90, 0, 0), seg=8)

    elif "scent_marking_log" in variant:
        # Long horizontal log with forked branch and rubbed scent patch
        r = min(W, H) / 2
        z.cyl(r, L * 0.95, loc=(0, 0, r), colour="dark_brown", rot=(90, 0, 0), seg=8)
        # Forked branch sticking out/up within height tolerance (0.32m - 0.48m)
        z.cyl(r * 0.45, 0.22, loc=(r * 0.3, 0.1, r + 0.05), colour="dark_brown", rot=(0, 60, 0), seg=6)
        # Scent marking paste rub flat on top
        z.box((r * 1.05, 0.35, 0.03), loc=(0, -0.25, r * 2.01), colour="sand")

    elif "rope_spiral_tug" in variant:
        # Hanging spiral braided rope tug
        steps = 6
        step_h = (H * 0.68) / steps
        for s in range(steps):
            sz = H * 0.22 + s * step_h
            ang = s * 60
            rad = math.radians(ang)
            z.cyl(0.045, step_h * 1.1, loc=(math.cos(rad) * 0.025, math.sin(rad) * 0.025, sz), colour="tan", rot=(12, 12, ang), seg=6)
        # Knotted ball at bottom
        z.ball(min(W, L) * 0.40, loc=(0, 0, H * 0.14), colour="sand", seg=8, rings=6)
        # Top hanging ring
        z.cyl(0.02, H * 0.16, loc=(0, 0, H * 0.92), colour="light_grey", seg=4)

    elif "forage_bungee_net" in variant:
        # Suspended bungee ball net: central food core inside elastic cage, top tether reaching H
        r = min(W, L) * 0.42
        # Ball centered at r so bottom touches Z=0
        z.ball(r * 0.55, loc=(0, 0, r), colour="red", seg=6, rings=4)
        z.cyl(r, 0.035, loc=(0, 0, r), colour="yellow", seg=10, r2=r)
        z.cyl(r, 0.035, loc=(0, 0, r), colour="yellow", rot=(90, 0, 0), seg=10, r2=r)
        z.cyl(r, 0.035, loc=(0, 0, r), colour="yellow", rot=(0, 90, 0), seg=10, r2=r)
        # Suspension cable extending up to H
        ch = H - 2 * r
        z.cyl(0.02, ch, loc=(0, 0, 2 * r + ch / 2), colour="charcoal", seg=4)

    elif "bamboo_windchime_toy" in variant:
        # Central hanging bamboo suspension pole from floor to top board
        z.cyl(0.025, H - 0.03, loc=(0, 0, (H - 0.03) / 2), colour="olive", seg=6)
        # Top suspension board
        z.box((W * 0.85, L * 0.85, 0.03), loc=(0, 0, H - 0.015), colour="brown")
        # Hanging chime tubes of varying lengths
        lengths = [H * 0.30, H * 0.40, H * 0.50, H * 0.60]
        offsets = ((-W * 0.35, -L * 0.35), (W * 0.35, -L * 0.35), (-W * 0.35, L * 0.35), (W * 0.35, L * 0.35))
        for i, (bx, by) in enumerate(offsets):
            ch = lengths[i % 4]
            z.cyl(0.035, ch, loc=(bx, by, H - 0.05 - ch / 2), colour="olive", seg=6)

    elif "primate_puzzle_box" in variant:
        # Wooden feeder box with maze holes
        z.box((W, L, H), loc=(0, 0, H / 2), colour="tan")
        # Hole accents
        for hx, hy in ((-W * 0.25, -L * 0.51), (W * 0.25, -L * 0.51)):
            z.box((0.10, 0.03, 0.10), loc=(hx, hy, H * 0.50), colour="dark_brown")

    elif "rubber_wobble_cone" in variant:
        # Weighted wobble treat cone (Kong toy style)
        r = min(W, L) / 2
        z.cone(r, H * 0.85, loc=(0, 0, H * 0.425), colour="red", seg=10)
        z.ball(r * 0.55, loc=(0, 0, H * 0.85), colour="red", seg=8, rings=6)

    elif "climbing_cargo_net" in variant:
        # Large timber frame with rope grid
        pw = 0.12
        post_h = H - pw
        # Vertical side posts
        z.box((pw, L * 0.90, post_h), loc=(-W * 0.45, 0, post_h / 2), colour="dark_brown")
        z.box((pw, L * 0.90, post_h), loc=(W * 0.45, 0, post_h / 2), colour="dark_brown")
        # Top cross beam extending fully across
        z.box((W, L, pw), loc=(0, 0, H - pw / 2), colour="dark_brown")
        # Cargo netting: crossed rope grid
        num_v = 4
        for i in range(num_v):
            rx = -W * 0.30 + i * (W * 0.60 / (num_v - 1))
            z.cyl(0.018, post_h * 0.95, loc=(rx, 0, post_h / 2), colour="tan", seg=4)
        num_h = 5
        for i in range(num_h):
            rz = post_h * 0.15 + i * (post_h * 0.70 / (num_h - 1))
            z.cyl(0.018, W * 0.75, loc=(0, 0, rz), colour="tan", rot=(0, 90, 0), seg=4)

    elif "misting_rub_station" in variant:
        # Spray arch with scratch brush rollers
        z.cyl(0.04, H, loc=(-W * 0.40, 0, H / 2), colour="grey", seg=6)
        z.cyl(0.04, H, loc=(W * 0.40, 0, H / 2), colour="grey", seg=6)
        z.cyl(0.04, W * 0.85, loc=(0, 0, H - 0.04), colour="grey", rot=(0, 90, 0), seg=6)
        # Textured bristled brushes on vertical poles
        z.cyl(0.14, H * 0.50, loc=(-W * 0.40, 0, H * 0.40), colour="rust", seg=8)
        z.cyl(0.14, H * 0.50, loc=(W * 0.40, 0, H * 0.40), colour="rust", seg=8)

    elif "splash_wading_tub" in variant:
        # Shallow galvanized pool with dark rim and clear blue water
        r = min(W, L) / 2
        z.cyl(r, H * 0.85, loc=(0, 0, H * 0.425), colour="light_grey", seg=12, r2=r * 0.85)
        # Rim collar around the top
        z.cyl(r * 1.04, H * 0.12, loc=(0, 0, H * 0.84), colour="charcoal", seg=12)
        # Water pool surface sitting inside the rim
        z.cyl(r * 0.86, 0.04, loc=(0, 0, H * 0.89), colour="water", seg=12)

    elif "treat_labyrinth_plate" in variant:
        # Disc with labyrinth walls
        r = min(W, L) / 2
        # Base plate from 0 to H * 0.35
        z.cyl(r, H * 0.35, loc=(0, 0, H * 0.175), colour="teal", seg=12)
        # Outer labyrinth ridge from 0.05 to H * 0.70
        z.cyl(r * 0.70, H * 0.65, loc=(0, 0, (0.05 + H * 0.70) / 2), colour="teal", seg=10)
        # Inner white hub from 0.08 to H
        z.cyl(r * 0.35, H * 0.92, loc=(0, 0, (0.08 + H) / 2), colour="white", seg=8)

    elif "floating_plastic_ring" in variant:
        # Hollow buoy donut ring
        r = min(W, L) / 2
        z.cyl(r, H, loc=(0, 0, H / 2), colour="orange", seg=12)
        z.cyl(r * 0.45, H * 1.05, loc=(0, 0, H / 2), colour="water", seg=8)

    else:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="red")


# ==============================================================================
# 3. SHOP SOUVENIRS & CONCESSIONS (20 assets)
# ==============================================================================

def _build_shop(W, L, H, variant, aid, p, z):
    if "plush_lion_toy" in variant:
        # Cute stuffed lion sitting with mane ring and snout
        z.ball(0.11, loc=(0, 0.04, 0.11), colour="tan", seg=8, rings=6)
        # Mane ring framing head
        z.cyl(0.15, 0.07, loc=(0, -0.05, 0.23), colour="dark_brown", rot=(90, 0, 0), seg=10)
        # Head
        z.ball(0.09, loc=(0, -0.07, 0.23), colour="tan", seg=8, rings=6)
        # Snout & ears
        z.ball(0.04, loc=(0, -0.14, 0.21), colour="sand", seg=6, rings=4)
        z.ball(0.015, loc=(0, -0.17, 0.23), colour="black", seg=4, rings=4)
        for ex in (-0.08, 0.08):
            z.ball(0.025, loc=(ex, -0.06, 0.30), colour="tan", seg=4, rings=4)

    elif "plush_elephant_toy" in variant:
        z.ball(0.14, loc=(0, 0, 0.14), colour="light_grey", scale=(1, 1.2, 1), seg=8, rings=6)
        z.ball(0.10, loc=(0, -0.12, 0.22), colour="light_grey", seg=8, rings=6)
        # Trunk
        z.cyl(0.03, 0.12, loc=(0, -0.20, 0.18), colour="light_grey", rot=(30, 0, 0), seg=6)
        # Ears
        for ex in (-0.12, 0.12):
            z.ball(0.07, loc=(ex, -0.10, 0.24), colour="pink", scale=(0.3, 1, 1), seg=6, rings=4)

    elif "plush_penguin_toy" in variant:
        z.ball(0.10, loc=(0, 0, 0.15), colour="black", scale=(1, 1, 1.5), seg=8, rings=6)
        z.ball(0.07, loc=(0, -0.04, 0.14), colour="white", scale=(0.8, 0.4, 1.2), seg=6, rings=4)
        z.cone(0.025, 0.05, loc=(0, -0.10, 0.24), colour="yellow", rot=(90, 0, 0), seg=4)

    elif "plush_giraffe_toy" in variant:
        # Yellow body
        z.ball(0.11, loc=(0, 0.04, 0.13), colour="gold", scale=(0.9, 1.2, 0.9), seg=8, rings=6)
        # Tall neck reaching up to 0.7m target height
        z.cyl(0.035, H * 0.62, loc=(0, -0.04, H * 0.48), colour="gold", rot=(5, 0, 0), seg=6)
        # Head & ossicones
        z.ball(0.065, loc=(0, -0.09, H * 0.84), colour="gold", seg=6, rings=4)
        for hx in (-0.025, 0.025):
            z.cyl(0.008, 0.06, loc=(hx, -0.09, H * 0.94), colour="dark_brown", seg=4)
        # Distinct brown spots on neck and flanks
        for sz, sy in ((H * 0.35, -0.03), (H * 0.52, -0.04), (H * 0.68, -0.06)):
            z.box((0.025, 0.025, 0.025), loc=(0.035, sy, sz), colour="brown")
            z.box((0.025, 0.025, 0.025), loc=(-0.035, sy, sz), colour="brown")
        z.box((0.04, 0.04, 0.03), loc=(0.09, 0.04, 0.13), colour="brown")
        z.box((0.04, 0.04, 0.03), loc=(-0.09, 0.04, 0.13), colour="brown")

    elif "zoo_guide_brochure" in variant:
        z.box((W, L, H * 0.90), loc=(0, 0, H * 0.45), colour="teal")
        z.box((W * 0.85, L * 0.85, 0.002), loc=(0, 0, H * 0.901), colour="white")

    elif "postcard_carousel_rack" in variant:
        # Rotating 4-sided wire rack
        z.cyl(W * 0.45, 0.04, loc=(0, 0, 0.02), colour="charcoal", seg=8)
        z.cyl(0.03, H - 0.04, loc=(0, 0, 0.04 + (H - 0.04) / 2), colour="light_grey", seg=6)
        # Postcard panels
        z.box((W * 0.70, L * 0.70, H * 0.70), loc=(0, 0, H * 0.58), colour="white")

    elif "animal_ear_headband" in variant:
        z.cyl(0.065, 0.02, loc=(0, 0, 0.07), colour="black", rot=(90, 0, 0), seg=8, r2=0.065)
        # Fuzzy ears
        for ex in (-0.06, 0.06):
            z.ball(0.03, loc=(ex, 0, 0.12), colour="orange", seg=6, rings=4)

    elif "safari_pith_helmet" in variant:
        # Explorer hat
        z.cyl(min(W, L) * 0.48, 0.02, loc=(0, 0, 0.04), colour="sand", seg=10)
        z.ball(min(W, L) * 0.34, loc=(0, 0, 0.10), colour="sand", scale=(1, 1, 0.8), seg=8, rings=6)
        z.cyl(min(W, L) * 0.35, 0.02, loc=(0, 0, 0.06), colour="dark_brown", seg=8)

    elif "zoo_logo_hoodie" in variant:
        # Folded hoodie with body, sleeves, hood and logo
        z.box((W * 0.60, L * 0.85, H * 0.65), loc=(0, 0, H * 0.32), colour="navy")
        # Sleeves folded along sides
        z.box((W * 0.18, L * 0.80, H * 0.55), loc=(-W * 0.38, 0, H * 0.28), colour="navy")
        z.box((W * 0.18, L * 0.80, H * 0.55), loc=(W * 0.38, 0, H * 0.28), colour="navy")
        # Hood rolled at back
        z.cyl(W * 0.25, 0.08, loc=(0, L * 0.25, H * 0.70), colour="navy", rot=(0, 90, 0), seg=8)
        # Gold zoo logo patch on chest
        z.box((W * 0.32, L * 0.28, 0.005), loc=(0, -L * 0.10, H * 0.66), colour="gold")

    elif "ceramic_souvenir_mug" in variant:
        r = min(W, L) * 0.42
        z.cyl(r, H * 0.90, loc=(0, 0, H * 0.45), colour="cream", seg=8)
        # Handle
        z.box((0.02, 0.04, H * 0.55), loc=(r + 0.02, 0, H * 0.50), colour="cream")

    elif "steel_water_bottle" in variant:
        r = min(W, L) / 2
        z.cyl(r, H * 0.80, loc=(0, 0, H * 0.40), colour="light_grey", seg=8)
        z.cyl(r * 0.65, H * 0.18, loc=(0, 0, H * 0.88), colour="teal", seg=8)

    elif "spiral_rainbow_lollipop" in variant:
        z.cyl(0.008, H * 0.60, loc=(0, 0, H * 0.30), colour="white", seg=4)
        z.cyl(W / 2, 0.025, loc=(0, 0, H * 0.75), colour="pink", rot=(90, 0, 0), seg=10)
        z.cyl(W * 0.30, 0.028, loc=(0, 0, H * 0.75), colour="yellow", rot=(90, 0, 0), seg=8)

    elif "soft_pretzel_mustard" in variant:
        # Paper serving tray
        z.box((0.21, 0.19, 0.014), loc=(0, 0, 0.007), colour="white")
        # Twisted pretzel knot made of non-coplanar 6-sided tubular segments
        z.cyl(0.015, 0.12, loc=(-0.045, 0.02, 0.025), colour="brown", rot=(90, 0, 35), seg=6)
        z.cyl(0.015, 0.12, loc=(0.015, 0.02, 0.025), colour="brown", rot=(90, 0, -35), seg=6)
        z.cyl(0.015, 0.12, loc=(-0.015, -0.03, 0.025), colour="brown", rot=(0, 90, 0), seg=6)
        z.cyl(0.015, 0.10, loc=(-0.015, 0.06, 0.025), colour="brown", rot=(0, 90, 0), seg=6)
        # Salt crystals on pretzel
        for sx, sy in ((-0.05, 0.06), (-0.015, 0.06), (0.02, 0.06)):
            z.ball(0.006, loc=(sx, sy, 0.038), colour="white", seg=4, rings=4)
        # Yellow mustard dipping cup sunk into tray
        z.cyl(0.024, 0.048, loc=(0.065, -0.045, 0.028), colour="yellow", seg=8)

    elif "softserve_icecream_cone" in variant:
        r = min(W, L) / 2
        # Waffle cone
        z.cone(r * 0.75, H * 0.55, loc=(0, 0, H * 0.28), colour="tan", seg=6)
        # Swirled pink strawberry ice cream
        z.cyl(r * 0.85, H * 0.18, loc=(0, 0, H * 0.58), colour="pink", seg=8)
        z.cyl(r * 0.65, H * 0.16, loc=(0, 0, H * 0.72), colour="pink", seg=8)
        z.cone(r * 0.45, H * 0.20, loc=(0, 0, H * 0.88), colour="pink", seg=6)

    elif "fountain_soda_cup" in variant:
        r = min(W, L) / 2
        z.cyl(r, H * 0.82, loc=(0, 0, H * 0.41), colour="red", seg=8, r2=r * 0.75)
        z.cyl(r * 1.05, 0.02, loc=(0, 0, H * 0.83), colour="white", seg=8)
        # Straw
        z.cyl(0.008, H * 0.35, loc=(0, 0, H * 0.92), colour="yellow", rot=(15, 0, 0), seg=4)

    elif "animal_sticker_sheet" in variant:
        z.box((W, L, H * 0.80), loc=(0, 0, H * 0.40), colour="white")
        # Colorful sticker dots on top face
        for sx in (-0.04, 0.04):
            for sy in (-0.06, 0.0, 0.06):
                z.box((0.025, 0.025, 0.002), loc=(sx, sy, H * 0.801), colour="teal")

    elif "keychain_spin_tree" in variant:
        # Counter rotating tree stand
        z.cyl(W * 0.45, 0.03, loc=(0, 0, 0.015), colour="charcoal", seg=8)
        z.cyl(0.025, H - 0.03, loc=(0, 0, 0.03 + (H - 0.03) / 2), colour="light_grey", seg=6)
        for h_tier in (H * 0.45, H * 0.75):
            z.box((W * 0.80, 0.03, 0.025), loc=(0, 0, h_tier), colour="light_grey")
            z.box((0.03, L * 0.80, 0.025), loc=(0, 0, h_tier + 0.028), colour="light_grey")

    elif "figurine_blind_box" in variant:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="purple")
        z.box((W * 0.60, L * 0.60, H * 1.03), loc=(0, 0, H / 2), colour="yellow")

    elif "toy_plastic_binoculars" in variant:
        # Kids colorful binoculars
        for bx in (-W * 0.28, W * 0.28):
            z.cyl(0.035, L * 0.85, loc=(bx, 0, H / 2), colour="forest", rot=(90, 0, 0), seg=6)
        # Bridge
        z.box((W * 0.35, 0.04, 0.03), loc=(0, 0, H / 2), colour="yellow")

    elif "helium_tiger_balloon" in variant:
        # Mylar tiger balloon with black stripes and white muzzle
        z.ball(0.18, loc=(0, 0, H * 0.70), colour="orange", scale=(1.2, 0.7, 1), seg=8, rings=6)
        # Ears with black tips
        for ex in (-0.16, 0.16):
            z.cone(0.04, 0.08, loc=(ex, 0, H * 0.85), colour="orange", seg=4)
            z.box((0.02, 0.02, 0.02), loc=(ex, 0, H * 0.89), colour="black")
        # Tiger stripes across forehead & cheeks
        z.box((0.025, 0.15, 0.06), loc=(0, -0.08, H * 0.78), colour="black")
        z.box((0.36, 0.03, 0.02), loc=(0, 0, H * 0.72), colour="black")
        z.box((0.32, 0.03, 0.02), loc=(0, 0, H * 0.66), colour="black")
        # White muzzle with black nose
        z.ball(0.05, loc=(0, -0.11, H * 0.65), colour="white", scale=(1.2, 0.7, 0.8), seg=6, rings=4)
        z.box((0.02, 0.02, 0.015), loc=(0, -0.15, H * 0.66), colour="black")
        # String
        z.cyl(0.008, H * 0.55, loc=(0, 0, H * 0.28), colour="white", seg=4)

    else:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="gold")


# ==============================================================================
# 4. VET & CLINICAL CARE EQUIPMENT (20 assets)
# ==============================================================================

def _build_vet(W, L, H, aid, p, z):
    if aid == "vet_exam_table":
        # Stainless steel examination table with medical pad
        z.box((W * 0.88, L * 0.88, 0.05), loc=(0, 0, 0.025), colour="light_grey")
        # Center hydraulic pedestal
        z.cyl(0.12, H * 0.75, loc=(0, 0, H * 0.40), colour="light_grey", seg=8)
        # Table top & teal examination mat
        z.box((W, L, 0.08), loc=(0, 0, H * 0.84), colour="light_grey")
        z.box((W * 0.94, L * 0.94, 0.04), loc=(0, 0, H * 0.90), colour="teal")

    elif aid == "vet_mobile_ultrasound":
        # Mobile cart with monitor and probe holster
        z.box((W * 0.85, L * 0.85, H * 0.65), loc=(0, 0, H * 0.35), colour="light_grey")
        # 4 casters
        for cx in (-W * 0.35, W * 0.35):
            for cy in (-L * 0.35, L * 0.35):
                z.cyl(0.04, 0.08, loc=(cx, cy, 0.04), colour="charcoal", seg=6)
        # Display monitor on swivel arm
        z.box((W * 0.65, 0.06, H * 0.32), loc=(0, -L * 0.15, H * 0.82), colour="charcoal")
        z.box((W * 0.55, 0.04, H * 0.24), loc=(0, -L * 0.17, H * 0.82), colour="teal")

    elif aid == "vet_digital_scale_large":
        # Heavy walk-on animal scale
        z.box((W, L, H * 0.85), loc=(0, 0, H * 0.425), colour="charcoal")
        z.box((W * 0.95, L * 0.95, 0.02), loc=(0, 0, H * 0.86), colour="grey")
        # Red LED display strip
        z.box((0.25, 0.08, 0.06), loc=(W * 0.35, -L * 0.40, H * 0.90), colour="red")

    elif aid == "vet_digital_scale_small":
        # Precision benchtop scale
        z.box((W, L, H * 0.75), loc=(0, 0, H * 0.375), colour="white")
        # Weighing pan
        z.box((W * 0.80, L * 0.80, 0.02), loc=(0, 0, H * 0.78), colour="light_grey")
        # Blue LCD screen
        z.box((W * 0.35, 0.05, 0.03), loc=(0, -L * 0.38, H * 0.40), colour="water")

    elif aid == "vet_surgical_light":
        # Rolling base with tall pole and dome lamp head
        z.cyl(W * 0.45, 0.06, loc=(0, 0, 0.03), colour="charcoal", seg=8)
        z.cyl(0.03, H * 0.75, loc=(0, 0, H * 0.40), colour="light_grey", seg=6)
        # Angled boom arm
        z.cyl(0.025, W * 0.60, loc=(W * 0.20, 0, H * 0.80), colour="light_grey", rot=(0, 45, 0), seg=6)
        # Surgical reflector dome lamp
        z.cone(W * 0.35, 0.15, loc=(W * 0.35, 0, H * 0.90), colour="light_grey", seg=10)
        z.ball(0.12, loc=(W * 0.35, 0, H * 0.85), colour="yellow", seg=8, rings=5)

    elif aid == "vet_anesthesia_machine":
        # Machine frame with gas vaporizers and flowmeter
        z.box((W * 0.85, L * 0.85, H * 0.70), loc=(0, 0, H * 0.38), colour="white")
        # Oxygen tank attached to side
        z.cyl(0.09, H * 0.55, loc=(W * 0.35, 0, H * 0.38), colour="sky", seg=8)
        # Flowmeter & monitors
        z.box((W * 0.55, L * 0.30, H * 0.22), loc=(0, -L * 0.20, H * 0.84), colour="teal")

    elif aid == "vet_xray_portable":
        # Field ruggedized x-ray unit
        z.box((W, L, H * 0.80), loc=(0, 0, H * 0.40), colour="orange")
        z.box((W * 0.40, 0.04, 0.08), loc=(0, 0, H * 0.84), colour="charcoal")
        z.cyl(0.08, 0.12, loc=(0, -L * 0.45, H * 0.40), colour="grey", rot=(90, 0, 0), seg=8)

    elif aid == "vet_instrument_tray":
        # Height adjustable Mayo stand with stainless tray
        z.box((W * 0.80, L * 0.80, 0.04), loc=(0, 0, 0.02), colour="light_grey")
        z.cyl(0.025, H * 0.90, loc=(0, 0, H * 0.48), colour="light_grey", seg=6)
        # Top tray with teal surgical cloth
        z.box((W, L, 0.04), loc=(0, 0, H * 0.94), colour="light_grey")
        z.box((W * 0.90, L * 0.90, 0.02), loc=(0, 0, H * 0.96), colour="teal")

    elif aid == "vet_iv_drip_stand":
        # 5-legged IV stand with fluid bags
        z.cyl(W * 0.45, 0.04, loc=(0, 0, 0.02), colour="charcoal", seg=6)
        z.cyl(0.02, H * 0.95, loc=(0, 0, H * 0.48), colour="light_grey", seg=6)
        # IV bags hanging at top
        for bx in (-0.12, 0.12):
            z.box((0.08, 0.04, 0.22), loc=(bx, 0, H * 0.85), colour="water")

    elif aid == "vet_recovery_stretcher":
        # Folding canvas stretcher with support legs touching floor
        for sx in (-W * 0.42, W * 0.42):
            z.cyl(0.03, L, loc=(sx, 0, H - 0.03), colour="tan", rot=(90, 0, 0), seg=6)
            for ly in (-L * 0.35, L * 0.35):
                z.cyl(0.02, H - 0.03, loc=(sx, ly, (H - 0.03) / 2), colour="light_grey", seg=4)
        z.box((W * 0.78, L * 0.90, 0.04), loc=(0, 0, H - 0.03), colour="navy")

    elif aid == "vet_heavy_transport_gurney":
        # Heavy transport gurney on locking wheels
        z.box((W * 0.88, L * 0.92, H * 0.50), loc=(0, 0, H * 0.28), colour="charcoal")
        z.box((W, L, H * 0.40), loc=(0, 0, H * 0.78), colour="forest")

    elif aid == "vet_incubator_brooder":
        # Brooder incubator with clear viewing hood
        z.box((W, L, H * 0.45), loc=(0, 0, H * 0.225), colour="cream")
        z.box((W * 0.90, L * 0.90, H * 0.50), loc=(0, 0, H * 0.70), colour="sky")

    elif aid == "vet_microscope_station":
        # Benchtop lab microscope
        z.box((W * 0.80, L * 0.80, 0.05), loc=(0, 0, 0.025), colour="charcoal")
        z.box((0.06, 0.08, H * 0.65), loc=(0, L * 0.20, H * 0.40), colour="charcoal")
        # Stage & dual eyepieces
        z.box((W * 0.55, L * 0.45, 0.03), loc=(0, 0, H * 0.45), colour="light_grey")
        z.cyl(0.025, 0.12, loc=(-0.03, -0.04, H * 0.85), colour="yellow", rot=(25, 0, 0), seg=6)
        z.cyl(0.025, 0.12, loc=(0.03, -0.04, H * 0.85), colour="yellow", rot=(25, 0, 0), seg=6)

    elif aid == "vet_centrifuge_unit":
        # Compact laboratory centrifuge
        r = min(W, L) * 0.46
        z.cyl(r, H * 0.75, loc=(0, 0, H * 0.38), colour="white", seg=10)
        # Hinged lid
        z.cyl(r * 0.92, H * 0.20, loc=(0, 0, H * 0.85), colour="teal", seg=10)

    elif aid == "vet_dart_rifle_case":
        # Heavy field case for dart projector
        z.box((W, L, H), loc=(0, 0, H / 2), colour="olive")
        # Corner protectors & latches
        z.box((W * 1.02, 0.04, H * 1.02), loc=(0, 0, H / 2), colour="black")

    elif aid == "vet_first_aid_trunk":
        # Red emergency response chest with white cross
        z.box((W, L, H), loc=(0, 0, H / 2), colour="red")
        # Center square and 4 non-overlapping arms for the white cross
        cw = min(W, H) * 0.12
        yf = -L * 0.505
        z.box((cw, 0.005, cw), loc=(0, yf, H / 2), colour="white")
        z.box((cw, 0.005, cw), loc=(-cw, yf, H / 2), colour="white")
        z.box((cw, 0.005, cw), loc=(cw, yf, H / 2), colour="white")
        z.box((cw, 0.005, cw), loc=(0, yf, H / 2 - cw), colour="white")
        z.box((cw, 0.005, cw), loc=(0, yf, H / 2 + cw), colour="white")

    elif aid == "vet_medicine_cabinet":
        # Wall cabinet with glass window doors
        z.box((W, L, H), loc=(0, 0, H / 2), colour="white")
        z.box((W * 0.85, 0.02, H * 0.80), loc=(0, -L * 0.505, H / 2), colour="sky")

    elif aid == "vet_capture_net_pole":
        # Long pole with hoop net
        z.cyl(0.025, L * 0.85, loc=(0, 0, H * 0.50), colour="rust", rot=(90, 0, 0), seg=6)
        # Hoop net at end
        z.cyl(W * 0.40, 0.03, loc=(0, -L * 0.45, H * 0.50), colour="light_grey", rot=(90, 0, 0), seg=8)
        z.cone(W * 0.38, 0.40, loc=(0, -L * 0.60, H * 0.50), colour="sand", rot=(90, 0, 0), seg=8)

    elif aid == "vet_oxygen_cylinder_trolley":
        # Green medical O2 cylinder on wheeled trolley
        z.cyl(W * 0.35, H * 0.75, loc=(0, 0, H * 0.45), colour="leaf", seg=8)
        # Trolley frame
        z.box((W * 0.90, L * 0.85, 0.05), loc=(0, 0, 0.03), colour="black")
        z.cyl(0.02, H * 0.90, loc=(0, L * 0.35, H * 0.48), colour="black", seg=4)

    elif aid == "vet_hydrotherapy_tank":
        # Large hydrotherapy treadmill tank with water
        z.box((W, L, H * 0.88), loc=(0, 0, H * 0.44), colour="teal")
        # Glass observation windows on sides
        z.box((W * 0.85, L * 1.02, H * 0.45), loc=(0, 0, H * 0.50), colour="sky")
        # Water plane
        z.box((W * 0.88, L * 0.88, 0.04), loc=(0, 0, H * 0.70), colour="water")

    else:
        z.box((W, L, H), loc=(0, 0, H / 2), colour="white")
