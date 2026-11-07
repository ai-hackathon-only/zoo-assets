"""Human character generator: procedural low-poly models for zoo keepers and visitors.
Produces stylized toy-like characters with modular uniforms, outfits, hair, hats, skin tones, and tools.
Facing: All models face -Y (Blender front, glTF +Z) to match the thumbnail camera.
"""
import math
from mathutils import Vector

# Palette color mappings
SKIN_MAP = {
    "fair": "skin_1",
    "tan": "skin_2",
    "medium": "skin_3",
    "dark": "skin_5",
}

HAIR_MAP = {
    "black": "black",
    "dark": "dark_brown",
    "brown": "brown",
    "blonde": "sand",
    "red": "rust",
    "grey": "light_grey",
    "white": "white",
}

OUTFIT_MAP = {
    "khaki": ("tan", "dark_brown"),
    "olive": ("olive", "charcoal"),
    "navy": ("navy", "navy"),
    "teal_scrubs": ("teal", "teal"),
    "green": ("leaf", "tan"),
    "camo_khaki": ("olive", "tan"),
    "heavy_work": ("charcoal", "dark_brown"),
    "parka_blue": ("water", "navy"),
    "charcoal": ("charcoal", "black"),
    "white_apron": ("white", "navy"),
    "orange_vest": ("orange", "navy"),
    "blue_overalls": ("navy", "navy"),
    "ranger_tan": ("tan", "forest"),
    "yellow_polo": ("yellow", "charcoal"),
    "waders_blue": ("water", "water"),
    "green_smock": ("forest", "tan"),
    "khaki_vest": ("tan", "charcoal"),
    "casual_polo": ("water", "sand"),
    "summer_dress": ("yellow", "yellow"),
    "tshirt_shorts": ("red", "navy"),
    "overalls": ("navy", "navy"),
    "safari_kids": ("sand", "tan"),
    "onesie_yellow": ("yellow", "yellow"),
    "hoodie_jeans": ("charcoal", "navy"),
    "graphic_tee": ("purple", "charcoal"),
    "cardigan": ("maroon", "tan"),
    "blouse_skirt": ("lavender", "navy"),
    "cargo_hiking": ("forest", "tan"),
    "activewear": ("teal", "charcoal"),
    "camo_vest": ("olive", "dark_brown"),
    "boho_jacket": ("rust", "tan"),
    "scout_uniform": ("sand", "forest"),
    "hi_vis_yellow": ("yellow", "navy"),
    "vest_khaki": ("sand", "charcoal"),
    "shopping_chic": ("pink", "white"),
    "running_shorts": ("orange", "charcoal"),
    "denim_jacket": ("navy", "tan"),
    "outdoor_vest": ("forest", "dark_brown"),
    "casual_jacket": ("charcoal", "navy"),
    "casual_shirt": ("sky", "tan"),
    "explorer_hat": ("sand", "tan"),
}

KEEPER_HAIR_OVERRIDE = {
    "keeper_vet_surgeon_05": "sand",
    "keeper_vet_assistant_06": "black",
    "keeper_primate_caregiver_04": "brown",
    "keeper_aviary_curator_07": "rust",
    "keeper_herpetologist_08": "dark_brown",
    "keeper_nocturnal_keeper_12": "black",
    "keeper_nursery_nurse_13": "sand",
    "keeper_botanist_curator_19": "brown",
    "keeper_apprentice_keeper_20": "tan",
}


def build(asset, z):
    sx, sy, sz = asset["size_m"]
    p = asset.get("params", {})
    role = p.get("role_type", "keeper" if asset["category"] == "keepers" else "visitor")
    build_type = p.get("build", "athletic")
    skin_raw = p.get("skin_tone", "medium")
    skin_col = SKIN_MAP.get(skin_raw, "skin_2")
    
    uniform_key = p.get("uniform") or p.get("outfit", "khaki")
    top_col, bot_col = OUTFIT_MAP.get(uniform_key, ("tan", "charcoal"))
    tool = p.get("tool") or p.get("accessory", "none")

    is_child = role in ("child", "toddler") or "child" in asset["id"] or "toddler" in asset["id"] or "kid" in asset["id"]
    is_senior = role == "senior"
    is_wheelchair = "wheelchair" in asset["id"] or tool == "wheelchair"
    is_shoulder_kid = "shoulder_kid" in asset["id"] or tool == "kid_rider"

    target_w = sx
    target_l = sy
    target_h = sz

    if is_wheelchair:
        _build_wheelchair_user(z, target_w, target_l, target_h, skin_col, top_col, bot_col)
        return

    if is_shoulder_kid:
        _build_shoulder_kid(z, target_w, target_l, target_h, skin_col, top_col, bot_col)
        return

    H = target_h
    W = target_w * 0.85
    L = target_l * 0.75

    if build_type == "stocky":
        W *= 1.08
        L *= 1.08
    elif build_type == "slim":
        W *= 0.92
        L *= 0.92
    elif is_child:
        W *= 0.95
        L *= 0.95

    # 1. Shoes / Feet (facing -Y)
    shoe_h = H * 0.06
    shoe_w = W * 0.30
    shoe_l = L * 0.60
    shoe_col = "dark_brown" if role == "keeper" else "charcoal"
    leg_x = W * 0.23
    for x in (leg_x, -leg_x):
        z.box((shoe_w, shoe_l, shoe_h), loc=(x, -shoe_l * 0.15, shoe_h / 2), colour=shoe_col)

    # 2. Legs / Pants
    leg_top = H * 0.44
    leg_h = leg_top - shoe_h * 0.7
    leg_w = W * 0.26
    leg_l = L * 0.40
    leg_z_center = shoe_h * 0.7 + leg_h / 2
    for x in (leg_x, -leg_x):
        z.box((leg_w, leg_l, leg_h), loc=(x, 0, leg_z_center), colour=bot_col)

    # 3. Torso / Shirt
    torso_bottom = leg_top - H * 0.015
    torso_top = H * 0.72
    torso_h = torso_top - torso_bottom
    torso_w = W * 0.78
    torso_l = L * 0.65
    z.box((torso_w, torso_l, torso_h), loc=(0, 0, torso_bottom + torso_h / 2), colour=top_col)

    # Apron / Vest accent if applicable
    if "apron" in uniform_key or "vest" in uniform_key:
        z.box((torso_w * 0.90, torso_l * 1.08, torso_h * 0.80),
              loc=(0, 0, torso_bottom + torso_h * 0.45), colour=top_col)

    # 4. Arms & Hands
    arm_top = torso_top - H * 0.02
    arm_h = H * 0.28
    arm_w = W * 0.20
    arm_l = L * 0.26
    shoulder_x = torso_w * 0.50 + arm_w * 0.38

    for side, x in ((-1, -shoulder_x), (1, shoulder_x)):
        sleeve_h = arm_h * 0.55
        z.box((arm_w, arm_l, sleeve_h), loc=(x, 0, arm_top - sleeve_h / 2), colour=top_col)
        
        forearm_h = arm_h * 0.48
        forearm_col = top_col if "long" in uniform_key or "parka" in uniform_key or "jacket" in uniform_key else skin_col
        z.box((arm_w * 0.88, arm_l * 0.88, forearm_h),
              loc=(x, -arm_l * 0.08, arm_top - sleeve_h * 0.95 - forearm_h / 2), colour=forearm_col)
        
        hand_h = H * 0.06
        z.box((arm_w * 0.82, arm_l * 0.82, hand_h),
              loc=(x, -arm_l * 0.12, arm_top - arm_h - hand_h * 0.4), colour=skin_col)

    # 5. Neck & Head
    neck_h = H * 0.06
    neck_r = min(W, L) * 0.16
    z.cyl(neck_r, neck_h, loc=(0, 0, torso_top - H * 0.01 + neck_h / 2), colour=skin_col, seg=6)

    head_bottom = torso_top + neck_h * 0.7
    head_size = H * 0.19 if not is_child else H * 0.23
    head_w = W * 0.52
    head_l = L * 0.55
    head_h = head_size
    head_center_z = head_bottom + head_h / 2
    z.box((head_w, head_l, head_h), loc=(0, 0, head_center_z), colour=skin_col)

    # Facial features: Eyes embedded facing -Y
    eye_z = head_center_z + head_h * 0.08
    eye_y = -head_l * 0.48
    eye_x = head_w * 0.22
    for x in (eye_x, -eye_x):
        z.box((head_w * 0.14, head_l * 0.10, head_h * 0.10), loc=(x, eye_y, eye_z), colour="black")

    # 6. Hair / Hat (varied hats and visible hair styles)
    hat_z = head_bottom + head_h * 0.75
    hair_col = KEEPER_HAIR_OVERRIDE.get(
        asset["id"],
        "light_grey" if is_senior else ("dark_brown" if skin_raw in ("tan", "dark") else "sand")
    )

    aid = asset["id"]
    is_safari_hat = aid in (
        "keeper_safari_lead_01", "keeper_security_ranger_16", "keeper_elephant_keeper_09",
        "keeper_education_guide_17", "keeper_grounds_landscaper_14"
    ) or "ranger_tan" in uniform_key
    is_cap = aid in (
        "keeper_carnivore_specialist_02", "keeper_aquatic_feeder_03", "keeper_ungulate_feeder_10",
        "keeper_maintenance_tech_15", "keeper_penguin_keeper_18", "keeper_arctic_curator_11",
        "visitor_child_cap_05"
    ) or "scout" in uniform_key or "cap" in aid
    is_sunhat = "sunhat" in aid or "sunvisor" in aid or "summer_dress" in uniform_key

    if is_safari_hat:
        brim_w = head_w * 1.55
        brim_l = head_l * 1.55
        brim_h = H * 0.025
        z.box((brim_w, brim_l, brim_h), loc=(0, 0, hat_z), colour=top_col)
        crown_w = head_w * 0.90
        crown_l = head_l * 0.90
        crown_h = H * 0.08
        z.box((crown_w, crown_l, crown_h), loc=(0, 0, hat_z + crown_h / 2), colour=top_col)
    elif is_cap:
        cap_h = H * 0.08
        z.box((head_w * 1.05, head_l * 1.05, cap_h), loc=(0, 0, hat_z + cap_h / 2), colour=top_col)
        visor_l = head_l * 0.50
        z.box((head_w * 0.95, visor_l, H * 0.025), loc=(0, -head_l * 0.60, hat_z + H * 0.01), colour=top_col)
    elif is_sunhat:
        brim_w = head_w * 1.6
        brim_l = head_l * 1.6
        z.box((brim_w, brim_l, H * 0.025), loc=(0, 0, hat_z), colour="cream")
        z.box((head_w * 0.92, head_l * 0.92, H * 0.07), loc=(0, 0, hat_z + H * 0.035), colour="cream")
    else:
        # Natural visible hair cap resting on top and back (+Y) of head
        hair_h = head_h * 0.40
        hair_l = head_l * 0.85
        z.box((head_w * 1.05, hair_l, hair_h), loc=(0, head_l * 0.10, hat_z + hair_h / 2), colour=hair_col)

    # 7. Tools and Accessories
    _add_tool(z, tool, H, W, L, torso_w, torso_top, arm_top, arm_h, shoulder_x, skin_col, top_col)


def _add_tool(z, tool, H, W, L, torso_w, torso_top, arm_top, arm_h, shoulder_x, skin_col, top_col):
    hx = shoulder_x
    hy = -L * 0.22
    hz = arm_top - arm_h

    if tool in ("clipboard", "field_notebook", "sketchbook", "clipboard_whistle"):
        z.box((0.18, 0.04, 0.22), loc=(hx * 0.88, hy - 0.08, hz + 0.05), colour="brown")
        z.box((0.15, 0.05, 0.18), loc=(hx * 0.88, hy - 0.08, hz + 0.05), colour="white")
    elif tool in ("meat_tongs", "snake_hook"):
        z.box((0.04, 0.32, 0.04), loc=(hx * 0.88, hy - 0.12, hz), colour="light_grey")
    elif tool in ("fish_bucket", "feed_pail"):
        z.cyl(0.12, 0.22, loc=(hx, hy - 0.05, hz - 0.16), colour="grey", seg=8)
        z.box((0.03, 0.03, 0.20), loc=(hx, hy - 0.05, hz - 0.03), colour="light_grey")
    elif tool in ("puzzle_box", "toolbox", "scanner"):
        col = "charcoal" if tool == "scanner" else ("rust" if tool == "toolbox" else "sand")
        z.box((0.20, 0.16, 0.16), loc=(hx, hy - 0.05, hz), colour=col)
    elif tool == "med_kit":
        # Bright red emergency medical kit with white handle - high contrast against teal scrubs
        z.box((0.22, 0.16, 0.16), loc=(hx, hy - 0.05, hz), colour="red")
        z.box((0.08, 0.04, 0.03), loc=(hx, hy - 0.05, hz + 0.09), colour="white")
    elif tool in ("shovel", "pitchfork", "rake", "broom", "pruning_shears", "ice_pick"):
        pole_h = H * 0.55
        z.cyl(0.025, pole_h, loc=(hx, hy - 0.05, pole_h / 2), colour="sand", seg=6)
        tool_head_col = "light_grey" if tool != "broom" else "tan"
        z.box((0.18, 0.08, 0.12), loc=(hx, hy - 0.05, pole_h * 0.95), colour=tool_head_col)
    elif tool in ("seed_scoop", "nursing_bottle", "radio_holster", "megaphone", "red_flashlight"):
        z.box((0.08, 0.10, 0.14), loc=(hx * 0.88, hy - 0.05, hz + 0.02), colour="orange" if "red" in tool else "sand")
    elif tool == "camera":
        z.box((0.14, 0.10, 0.10), loc=(0, -L * 0.42, torso_top - H * 0.10), colour="black")
        z.cyl(0.04, 0.06, loc=(0, -L * 0.49, torso_top - H * 0.10), colour="charcoal", rot=(90, 0, 0), seg=6)
    elif tool == "balloon":
        string_h = H * 0.38
        z.cyl(0.015, string_h, loc=(hx, hy, hz + string_h / 2), colour="white", seg=4)
        z.ball(0.14, loc=(hx, hy, hz + string_h + 0.11), colour="red", scale=(1, 1, 1.2), seg=8, rings=6)
    elif tool == "ice_cream":
        z.cone(0.04, 0.12, loc=(hx, hy - 0.05, hz + 0.08), colour="tan", seg=6)
        z.ball(0.05, loc=(hx, hy - 0.05, hz + 0.16), colour="pink", seg=8, rings=5)
    elif tool in ("binoculars_toy", "binoculars_neck"):
        for bx in (-0.04, 0.04):
            z.cyl(0.03, 0.10, loc=(bx, -L * 0.42, torso_top - H * 0.08), colour="forest", rot=(90, 0, 0), seg=6)
    elif tool in ("cane", "umbrella"):
        cane_h = H * 0.48
        z.cyl(0.025, cane_h, loc=(hx, hy, cane_h / 2), colour="dark_brown" if tool == "cane" else "navy", seg=6)
    elif tool in ("heavy_pack", "backpack"):
        # Backpack worn on back (+Y)
        z.box((W * 0.65, L * 0.42, H * 0.28), loc=(0, L * 0.50, torso_top - H * 0.14), colour="forest")
    elif tool in ("smartphone", "digital_recorder"):
        z.box((0.07, 0.025, 0.13), loc=(hx * 0.85, hy - 0.08, hz + 0.06), colour="charcoal")
    elif tool in ("gift_bags", "tote_bag"):
        z.box((0.20, 0.14, 0.22), loc=(hx, hy - 0.06, hz - 0.16), colour="pink" if tool == "gift_bags" else "cream")
    elif tool == "water_flask":
        z.cyl(0.04, 0.16, loc=(hx, hy, hz), colour="sky", seg=6)
    elif tool in ("pretzel", "map_sheet", "compass"):
        z.box((0.12, 0.04, 0.12), loc=(hx * 0.85, hy - 0.08, hz + 0.04), colour="tan" if tool == "pretzel" else "cream")
    elif tool == "stroller_handle":
        z.box((W * 0.80, 0.04, 0.04), loc=(0, -L * 0.48, hz + 0.08), colour="charcoal")
    elif tool == "tripod_rig":
        z.cyl(0.03, H * 0.50, loc=(hx, hy - 0.06, H * 0.25), colour="charcoal", seg=6)


def _build_wheelchair_user(z, W, L, H, skin_col, top_col, bot_col):
    # Wheelchair base & wheels (facing -Y)
    wheel_r = H * 0.28
    wheel_w = 0.06
    for side in (-1, 1):
        wx = side * (W * 0.42)
        z.cyl(wheel_r, wheel_w, loc=(wx, L * 0.05, wheel_r), colour="charcoal", rot=(0, 90, 0), seg=10)
        # Hub sphere
        z.ball(0.06, loc=(wx + side * 0.02, L * 0.05, wheel_r), colour="light_grey", seg=6, rings=4)

    # Seat frame
    seat_z = wheel_r * 1.05
    seat_w = W * 0.68
    seat_l = L * 0.52
    seat_h = 0.07
    z.box((seat_w, seat_l, seat_h), loc=(0, 0, seat_z), colour="navy")
    # Backrest at +Y (back)
    back_h = H * 0.38
    z.box((seat_w * 0.92, 0.06, back_h), loc=(0, seat_l * 0.42, seat_z + seat_h * 0.3 + back_h / 2), colour="navy")

    # Seated legs pointing forward (-Y)
    leg_l = seat_l * 0.85
    leg_w = seat_w * 0.28
    leg_h = 0.13
    seat_top_z = seat_z + seat_h / 2
    for side in (-1, 1):
        lx = side * (seat_w * 0.22)
        z.box((leg_w, leg_l, leg_h), loc=(lx, -seat_l * 0.30, seat_top_z + leg_h / 2), colour=bot_col)
        # Feet hanging down
        z.box((leg_w * 0.95, 0.14, 0.18), loc=(lx, -seat_l * 0.72, seat_z - 0.10), colour="dark_brown")

    # Seated torso (embedded into seat)
    torso_h = H * 0.34
    torso_w = seat_w * 0.78
    torso_l = seat_l * 0.46
    z.box((torso_w, torso_l, torso_h), loc=(0, seat_l * 0.12, seat_top_z - 0.04 + torso_h / 2), colour=top_col)

    # Head
    head_size = H * 0.18
    head_z = seat_top_z + torso_h + head_size * 0.45
    head_w = torso_w * 0.60
    head_l = torso_l * 0.68
    z.box((head_w, head_l, head_size), loc=(0, seat_l * 0.10, head_z), colour=skin_col)
    
    # Eyes facing -Y
    eye_y = seat_l * 0.10 - head_l * 0.48
    for side in (-1, 1):
        z.box((head_w * 0.14, head_l * 0.10, head_size * 0.10), loc=(side * (head_w * 0.22), eye_y, head_z + 0.02), colour="black")
    
    # Hair cap extends distinctly past back of head (+Y)
    hair_h = head_size * 0.38
    hair_l = head_l * 0.85
    z.box((head_w * 1.05, hair_l, hair_h), loc=(0, seat_l * 0.10 + head_l * 0.15, head_z + hair_h / 2), colour="dark_brown")


def _build_shoulder_kid(z, W, L, H, skin_col, top_col, bot_col):
    adult_h = H * 0.78
    adult_w = W * 0.95
    adult_l = L * 0.75

    shoe_h = adult_h * 0.06
    for x in (adult_w * 0.24, -adult_w * 0.24):
        z.box((adult_w * 0.28, adult_l * 0.55, shoe_h), loc=(x, -adult_l * 0.12, shoe_h / 2), colour="dark_brown")

    leg_h = adult_h * 0.42
    for x in (adult_w * 0.24, -adult_w * 0.24):
        z.box((adult_w * 0.26, adult_l * 0.40, leg_h), loc=(x, 0, shoe_h * 0.7 + leg_h / 2), colour=bot_col)

    torso_bottom = shoe_h * 0.7 + leg_h - adult_h * 0.02
    torso_h = adult_h * 0.32
    torso_w = adult_w * 0.80
    torso_l = adult_l * 0.65
    z.box((torso_w, torso_l, torso_h), loc=(0, 0, torso_bottom + torso_h / 2), colour=top_col)

    # Adult arms
    arm_top = torso_bottom + torso_h - adult_h * 0.02
    arm_h = adult_h * 0.28
    arm_w = adult_w * 0.18
    arm_l = adult_l * 0.28
    for side, x in ((-1, -adult_w * 0.45), (1, adult_w * 0.45)):
        z.box((arm_w, arm_l, arm_h), loc=(x, 0, arm_top - arm_h / 2), colour=top_col)

    # Adult head
    head_size = adult_h * 0.18
    head_z = torso_bottom + torso_h + head_size * 0.50
    head_w = adult_w * 0.52
    head_l = adult_l * 0.52
    z.box((head_w, head_l, head_size), loc=(0, 0, head_z), colour=skin_col)

    # Eyes facing -Y
    eye_y = -head_l * 0.48
    for x in (head_w * 0.22, -head_w * 0.22):
        z.box((head_w * 0.14, head_l * 0.10, head_size * 0.10), loc=(x, eye_y, head_z + 0.02), colour="black")

    # Adult Hair cap at back (+Y)
    hair_h = head_size * 0.38
    hair_l = head_l * 0.85
    z.box((head_w * 1.05, hair_l, hair_h), loc=(0, head_l * 0.15, head_z + hair_h / 2), colour="dark_brown")

    # Toddler on shoulders! (facing -Y)
    kid_bottom = torso_bottom + torso_h + adult_h * 0.06
    kid_torso_h = H * 0.13
    kid_w = adult_w * 0.42
    kid_l = adult_l * 0.44
    for x in (adult_w * 0.28, -adult_w * 0.28):
        z.box((kid_w * 0.35, kid_l * 0.85, kid_torso_h * 0.55), loc=(x, -kid_l * 0.20, kid_bottom), colour="navy")

    z.box((kid_w, kid_l, kid_torso_h), loc=(0, kid_l * 0.08, kid_bottom + kid_torso_h / 2), colour="yellow")
    
    kid_head_h = H * 0.11
    kid_head_z = kid_bottom + kid_torso_h + kid_head_h / 2
    kid_head_w = kid_w * 0.72
    kid_head_l = kid_l * 0.72
    z.box((kid_head_w, kid_head_l, kid_head_h), loc=(0, kid_l * 0.04, kid_head_z), colour=skin_col)
    
    # Kid eyes facing -Y
    kid_eye_y = kid_l * 0.04 - kid_head_l * 0.48
    for x in (kid_head_w * 0.22, -kid_head_w * 0.22):
        z.box((kid_head_w * 0.14, kid_head_l * 0.10, kid_head_h * 0.10), loc=(x, kid_eye_y, kid_head_z + 0.02), colour="black")

    # Kid hair cap extends distinctly past back of kid head (+Y)
    kid_hair_h = kid_head_h * 0.40
    kid_hair_l = kid_head_l * 0.85
    z.box((kid_head_w * 1.05, kid_hair_l, kid_hair_h), loc=(0, kid_l * 0.04 + kid_head_l * 0.15, kid_head_z + kid_hair_h / 2), colour="sand")
