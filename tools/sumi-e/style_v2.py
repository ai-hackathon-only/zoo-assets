# Enhanced cel/toon and paper/sketch variants for zoo-assets (post-process on existing GLBs).
# blender -b -noaudio --factory-startup --python style_v2.py -- <repo> <outdir>
import bpy, sys, os, math, importlib.util
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v1", os.path.join(HERE, "style_test.py"))
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
REPO, OUT = v1.REPO, v1.OUT
RES = v1.RES
ASSETS = ["animals/giraffe", "animals/lion", "animals/giant_panda", "plants/acacia_tree",
          "vehicles/animal_transport_truck", "keepers/keeper_aquatic_feeder_03"]
STYLES = [  # (key, label, family)
    ("cel", "cel v1 (last run)", "cel"),
    ("cel3", "3-tone + rim light", "cel"),
    ("anime", "anime: tinted shadow + highlight", "cel"),
    ("manga", "manga: halftone dots", "cel"),
    ("sticker", "sticker: white border", "cel"),
    ("paper", "paper v1 (last run)", "paper"),
    ("pencil", "pencil + hatching", "paper"),
    ("watercolor", "watercolor", "paper"),
    ("ink", "ink brush (sumi-e)", "paper"),
    ("crayon", "crayon", "paper"),
]
BG = {"cel": (0.82, 0.86, 0.9), "cel3": (0.85, 0.9, 0.95), "anime": (0.86, 0.9, 1.0), "manga": (1, 1, 1),
      "sticker": (0.98, 0.86, 0.72)}
PAPER = {"paper": (0.93, 0.9, 0.84), "pencil": (0.95, 0.94, 0.9), "watercolor": (0.97, 0.95, 0.9),
         "ink": (0.93, 0.89, 0.8), "crayon": (0.99, 0.97, 0.92)}


# ---------- node helpers ----------
def N(nt, kind, **inp):
    n = nt.nodes.new(kind)
    for k, v in inp.items():
        n.inputs[k].default_value = v
    return n


def L(nt, a, b):
    nt.links.new(a, b)


def math_node(nt, op, a=None, b=None, va=None, vb=None):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op
    if va is not None: m.inputs[0].default_value = va
    if vb is not None: m.inputs[1].default_value = vb
    if a is not None: L(nt, a, m.inputs[0])
    if b is not None: L(nt, b, m.inputs[1])
    return m.outputs[0]


def mix_rgb(nt, blend, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = blend
    for sock, val in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(val, (int, float)): sock.default_value = val
        elif isinstance(val, tuple): sock.default_value = val
        else: L(nt, val, sock)
    return m.outputs[2]


def light(nt):
    """Diffuse lighting as a 0..1 value (EEVEE Shader to RGB)."""
    d = N(nt, "ShaderNodeBsdfDiffuse"); s = nt.nodes.new("ShaderNodeShaderToRGB"); L(nt, d.outputs[0], s.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); L(nt, s.outputs[0], bw.inputs[0]); return bw.outputs[0]


def ramp(nt, val, stops, interp="CONSTANT"):
    r = nt.nodes.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = interp
    els = r.color_ramp.elements
    while len(els) < len(stops): els.new(0.5)
    for e, (pos, col) in zip(els, stops):
        e.position = pos; e.color = (*col, 1)
    L(nt, val, r.inputs[0]); return r.outputs[0]


def tex(nt, img):
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Closest"; return t.outputs[0]


def screen(nt, scale):
    """Screen-space coordinates (window), scaled so 1 unit = 1/scale of the frame."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    v = nt.nodes.new("ShaderNodeVectorMath"); v.operation = "SCALE"; v.inputs[3].default_value = scale
    L(nt, tc.outputs["Window"], v.inputs[0]); return v.outputs[0]


def sep(nt, vec):
    s = nt.nodes.new("ShaderNodeSeparateXYZ"); L(nt, vec, s.inputs[0]); return s.outputs[0], s.outputs[1]


def emit(nt, col):
    e = nt.nodes.new("ShaderNodeEmission"); L(nt, col, e.inputs[0]); return e.outputs[0]


def material(name, build):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); L(nt, build(nt), out.inputs["Surface"]); return m


# ---------- freestyle ----------
def freestyle(ob):
    sc = bpy.context.scene; sc.render.use_freestyle = True; vl = sc.view_layers[0]; vl.use_freestyle = True
    fs = vl.freestyle_settings; fs.crease_angle = math.radians(140)
    for ls in list(fs.linesets): fs.linesets.remove(ls)
    return fs


def lineset(fs, coll, name, color, thick, kinds=("silhouette", "border", "crease"), noise=0.0, seed=0,
            taper=False, pos="CENTER"):
    ls = fs.linesets.new(name); ls.select_by_visibility = True
    ls.select_by_collection = True; ls.collection = coll
    for k in ("silhouette", "border", "crease", "external_contour"):
        setattr(ls, f"select_{k}", k in kinds)
    st = bpy.data.linestyles.new(name); ls.linestyle = st
    st.color = color; st.thickness = thick; st.thickness_position = pos
    st.caps = "ROUND"
    if noise:
        g = st.geometry_modifiers.new("noise", "PERLIN_NOISE_1D"); g.frequency = 25; g.amplitude = noise * 0.6; g.seed = seed
    if taper:
        t = st.thickness_modifiers.new("taper", "ALONG_STROKE"); t.mapping = "CURVE"; t.value_min = 0.2; t.value_max = 1.6
        c = t.curve; pts = c.curves[0].points
        pts[0].location = (0, 0); pts[1].location = (1, 0); pts.new(0.35, 1.0); c.update()
    return ls


# ---------- styles ----------
def style(ob, key, img):
    coll = bpy.data.collections.new("model"); bpy.context.scene.collection.children.link(coll)
    for c in ob.users_collection: c.objects.unlink(ob)
    coll.objects.link(ob)
    if key == "cel":
        v1.apply_style(ob, "cel", img)  # v1 helper adds its own lineset (selects everything); rebuild below
        fs = freestyle(ob); lineset(fs, coll, "ink", (0.03, 0.03, 0.05), 2.0)
        return
    if key == "paper":
        v1.apply_style(ob, "paper", img)
        fs = freestyle(ob); lineset(fs, coll, "ink", (0.25, 0.2, 0.15), 2.0)
        return
    fs = freestyle(ob)
    if key == "cel3":
        def b(nt):
            hsv = N(nt, "ShaderNodeHueSaturation", Saturation=1.25); L(nt, tex(nt, img), hsv.inputs["Color"])
            shade = ramp(nt, light(nt), [(0, (0.42, 0.45, 0.62)), (0.12, (0.72, 0.74, 0.86)), (0.45, (1, 1, 1))])
            col = mix_rgb(nt, "MULTIPLY", 1, hsv.outputs[0], shade)
            lw = N(nt, "ShaderNodeLayerWeight", Blend=0.35)
            rim = math_node(nt, "GREATER_THAN", lw.outputs["Facing"], vb=0.72)
            return emit(nt, mix_rgb(nt, "ADD", rim, col, (0.35, 0.35, 0.3, 1)))
        ob.data.materials.clear(); ob.data.materials.append(material("cel3", b))
        lineset(fs, coll, "outer", (0.04, 0.03, 0.06), 3.2, kinds=("silhouette", "border"))
        lineset(fs, coll, "inner", (0.15, 0.12, 0.18), 1.2, kinds=("crease",))
    elif key == "anime":
        def b(nt):
            hsv = N(nt, "ShaderNodeHueSaturation", Saturation=1.35, Value=1.05); L(nt, tex(nt, img), hsv.inputs["Color"])
            shade = ramp(nt, light(nt), [(0, (0.62, 0.5, 0.8)), (0.2, (1, 1, 1))])
            col = mix_rgb(nt, "MULTIPLY", 1, hsv.outputs[0], shade)
            g = N(nt, "ShaderNodeBsdfGlossy", Roughness=0.15); s = nt.nodes.new("ShaderNodeShaderToRGB")
            L(nt, g.outputs[0], s.inputs[0]); bw = nt.nodes.new("ShaderNodeRGBToBW"); L(nt, s.outputs[0], bw.inputs[0])
            hi = math_node(nt, "GREATER_THAN", bw.outputs[0], vb=0.55)
            return emit(nt, mix_rgb(nt, "MIX", math_node(nt, "MULTIPLY", hi, vb=0.8), col, (1, 1, 1, 1)))
        ob.data.materials.clear(); ob.data.materials.append(material("anime", b))
        lineset(fs, coll, "outer", (0.28, 0.16, 0.12), 2.2)
    elif key == "manga":
        def b(nt):
            lum = nt.nodes.new("ShaderNodeRGBToBW"); L(nt, tex(nt, img), lum.inputs[0])
            v = math_node(nt, "MULTIPLY", light(nt), math_node(nt, "POWER", lum.outputs[0], vb=0.6))
            x, y = sep(nt, screen(nt, RES / 5))
            fx = math_node(nt, "SUBTRACT", math_node(nt, "FRACT", x), vb=0.5)
            fy = math_node(nt, "SUBTRACT", math_node(nt, "FRACT", y), vb=0.5)
            dist = math_node(nt, "SQRT", math_node(nt, "ADD", math_node(nt, "MULTIPLY", fx, fx), math_node(nt, "MULTIPLY", fy, fy)))
            radius = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", va=1.0, b=v), vb=0.75)
            dot = math_node(nt, "LESS_THAN", dist, radius)
            black = math_node(nt, "LESS_THAN", v, vb=0.06)
            ink = math_node(nt, "MAXIMUM", dot, black)
            return emit(nt, mix_rgb(nt, "MIX", ink, (1, 1, 1, 1), (0.02, 0.02, 0.02, 1)))
        ob.data.materials.clear(); ob.data.materials.append(material("manga", b))
        lineset(fs, coll, "outer", (0, 0, 0), 2.8, kinds=("silhouette", "border"))
        lineset(fs, coll, "inner", (0, 0, 0), 1.3, kinds=("crease",))
    elif key == "sticker":
        def b(nt):
            hsv = N(nt, "ShaderNodeHueSaturation", Saturation=1.3); L(nt, tex(nt, img), hsv.inputs["Color"])
            shade = ramp(nt, light(nt), [(0, (0.7, 0.72, 0.85)), (0.2, (1, 1, 1))])
            return emit(nt, mix_rgb(nt, "MULTIPLY", 1, hsv.outputs[0], shade))
        ob.data.materials.clear(); ob.data.materials.append(material("sticker", b))
        lineset(fs, coll, "ink", (0.1, 0.07, 0.1), 2.0)
    elif key == "pencil":
        def b(nt):
            lum = nt.nodes.new("ShaderNodeRGBToBW"); L(nt, tex(nt, img), lum.inputs[0])
            v = math_node(nt, "MULTIPLY", light(nt), math_node(nt, "POWER", lum.outputs[0], vb=0.5))
            x, y = sep(nt, screen(nt, RES / 4))
            diag = math_node(nt, "FRACT", math_node(nt, "ADD", x, y))
            cross = math_node(nt, "FRACT", math_node(nt, "SUBTRACT", x, y))
            h1 = math_node(nt, "MULTIPLY", math_node(nt, "LESS_THAN", diag, vb=0.28), math_node(nt, "LESS_THAN", v, vb=0.55))
            h2 = math_node(nt, "MULTIPLY", math_node(nt, "LESS_THAN", cross, vb=0.28), math_node(nt, "LESS_THAN", v, vb=0.28))
            ink = math_node(nt, "MINIMUM", math_node(nt, "ADD", h1, h2), vb=1)
            tint = mix_rgb(nt, "MIX", 0.12, (0.97, 0.96, 0.92, 1), tex(nt, img))
            return emit(nt, mix_rgb(nt, "MIX", math_node(nt, "MULTIPLY", ink, vb=0.7), tint, (0.25, 0.25, 0.27, 1)))
        ob.data.materials.clear(); ob.data.materials.append(material("pencil", b))
        lineset(fs, coll, "p1", (0.22, 0.22, 0.25), 1.3, noise=1.6, seed=1)
        lineset(fs, coll, "p2", (0.35, 0.35, 0.38), 0.9, noise=2.4, seed=7)
    elif key == "watercolor":
        def b(nt):
            hsv = N(nt, "ShaderNodeHueSaturation", Saturation=1.1, Value=1.0); L(nt, tex(nt, img), hsv.inputs["Color"])
            shade = ramp(nt, light(nt), [(0, (0.6, 0.7, 0.85)), (0.5, (1, 1, 1))], interp="EASE")
            col = mix_rgb(nt, "MULTIPLY", 1, hsv.outputs[0], shade)
            n = N(nt, "ShaderNodeTexNoise", Scale=2.5, Detail=4.0)
            L(nt, nt.nodes.new("ShaderNodeTexCoord").outputs["Object"], n.inputs["Vector"])
            blot = mix_rgb(nt, "MULTIPLY", 0.35, col, n.outputs["Color"])
            lw = N(nt, "ShaderNodeLayerWeight", Blend=0.25)
            edge = math_node(nt, "MULTIPLY", math_node(nt, "GREATER_THAN", lw.outputs["Facing"], vb=0.82), vb=0.35)
            pale = mix_rgb(nt, "MIX", 0.08, blot, (1, 1, 1, 1))
            return emit(nt, mix_rgb(nt, "MULTIPLY", edge, pale, (0.55, 0.5, 0.6, 1)))
        ob.data.materials.clear(); ob.data.materials.append(material("watercolor", b))
        lineset(fs, coll, "soft", (0.38, 0.3, 0.28), 1.0, noise=1.2, seed=3)
    elif key == "ink":
        def b(nt):
            lum = nt.nodes.new("ShaderNodeRGBToBW"); L(nt, tex(nt, img), lum.inputs[0])
            v = math_node(nt, "MULTIPLY", light(nt), math_node(nt, "POWER", lum.outputs[0], vb=0.7))
            wash = ramp(nt, v, [(0, (0.12, 0.12, 0.13)), (0.12, (0.5, 0.5, 0.5)), (0.4, (0.8, 0.79, 0.76)),
                                (0.7, (0.95, 0.93, 0.88))], interp="EASE")
            return emit(nt, wash)
        ob.data.materials.clear(); ob.data.materials.append(material("ink", b))
        lineset(fs, coll, "brush", (0.03, 0.03, 0.03), 5.5, kinds=("silhouette", "border"), taper=True, noise=0.8, seed=5)
        lineset(fs, coll, "fine", (0.1, 0.1, 0.1), 1.6, kinds=("crease",), taper=True)
    elif key == "crayon":
        def b(nt):
            hsv = N(nt, "ShaderNodeHueSaturation", Saturation=1.5, Value=1.05); L(nt, tex(nt, img), hsv.inputs["Color"])
            shade = ramp(nt, light(nt), [(0, (0.72, 0.68, 0.8)), (0.25, (1, 1, 1))])
            col = mix_rgb(nt, "MULTIPLY", 1, hsv.outputs[0], shade)
            n = N(nt, "ShaderNodeTexNoise", Scale=RES * 0.9, Detail=1.0); L(nt, screen(nt, 1.0), n.inputs["Vector"])
            x, y = sep(nt, screen(nt, RES / 3))
            stroke = N(nt, "ShaderNodeTexWave", Scale=1.0, Distortion=3.0)
            L(nt, screen(nt, 3.0), stroke.inputs["Vector"])
            grain = math_node(nt, "GREATER_THAN", math_node(nt, "ADD", n.outputs["Fac"],
                                                         math_node(nt, "MULTIPLY", stroke.outputs["Fac"], vb=0.08)), vb=0.68)
            return emit(nt, mix_rgb(nt, "MIX", grain, col, (0.99, 0.97, 0.92, 1)))
        ob.data.materials.clear(); ob.data.materials.append(material("crayon", b))
        lineset(fs, coll, "c1", (0.2, 0.12, 0.1), 3.0, noise=1.2, seed=2)


def render(ob, key, family, out):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x = sc.render.resolution_y = RES
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = key == "sticker"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bgc = BG.get(key, PAPER.get(key, (0.9, 0.9, 0.9)))
    w.node_tree.nodes["Background"].inputs[0].default_value = (*bgc, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0 if family == "paper" else 0.6
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    ctr = sum(corners, Vector()) / 8; size = max((c - ctr).length for c in corners)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 50; cam.location = ctr + Vector((1.0, -1.25, 0.8)).normalized() * size * 2.5
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30)); sun.data.energy = 3.5; sun.data.angle = math.radians(5)
    if family == "cel" and key != "sticker":  # flat ground for a cast shadow
        bpy.ops.mesh.primitive_plane_add(size=size * 12, location=(ctr.x, ctr.y, min(c.z for c in corners)))
        g = bpy.context.object
        def gb(nt):
            shade = ramp(nt, light(nt), [(0, tuple(c * 0.8 for c in bgc)), (0.2, bgc)]); return emit(nt, shade)
        g.data.materials.append(material("ground", gb))
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


def paper_bg(key, h, w, seed):
    rng = np.random.default_rng(seed)
    base = np.array(PAPER[key], dtype=np.float32)
    grain = rng.normal(0, 0.018, (h, w, 1)).astype(np.float32)
    fib = np.cumsum(rng.normal(0, 0.004, (h, w, 1)), axis=1).astype(np.float32)  # faint horizontal fibres
    fib -= fib.mean(axis=1, keepdims=True)
    img = np.clip(base + grain * 0.7 + fib * 0.25, 0, 1)
    return np.concatenate([img, np.ones((h, w, 1), np.float32)], axis=2)


def grow(mask, r):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out = np.maximum(out, np.roll(np.roll(mask, dy, 0), dx, 1))
    return out


def sticker(px, key):
    a = px[..., 3]; h, w = a.shape
    border = grow((a > 0.5).astype(np.float32), 7)
    shadow = np.roll(np.roll(grow(border, 2), -5, 0), 4, 1) * 0.25  # rows are bottom-up: -5 = down
    bg = np.ones((h, w, 3), np.float32) * np.array(BG[key], np.float32)
    out = bg * (1 - shadow[..., None])
    out = out * (1 - border[..., None]) + border[..., None]  # white die-cut border
    out = px[..., :3] * a[..., None] + out * (1 - a[..., None])
    return np.concatenate([out, np.ones((h, w, 1), np.float32)], axis=2)


def load_px(path):
    im = bpy.data.images.load(path); w, h = im.size
    return np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)


def save_px(px, path):
    h, w = px.shape[:2]
    im = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    im.pixels[:] = px.ravel(); im.filepath_raw = path; im.file_format = "PNG"; im.save()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tiles = {}
    for r, asset in enumerate(ASSETS):
        for c, (key, label, family) in enumerate(STYLES):
            out = f"{OUT}/{asset.split('/')[1]}__{key}.png"
            v1.reset(); ob = v1.load(asset)
            img = next((i for i in bpy.data.images if i.size[0] > 0), None)
            style(ob, key, img)
            render(ob, key, family, out)
            px = load_px(out)
            if key == "sticker":
                px = sticker(px, key); save_px(px, out)
            if family == "paper":  # composite on a paper texture
                bg = paper_bg(key, *px.shape[:2], seed=r * 31 + c)
                rel = bg[..., :3] / np.array(PAPER[key], np.float32)  # grain relative to the paper colour
                px = np.concatenate([np.clip(px[..., :3] * rel, 0, 1), np.ones_like(px[..., 3:4])], axis=2)
                save_px(px, out)
            tiles[(r, c)] = px
            print("RENDERED", out, flush=True)
    rows, cols = len(ASSETS), len(STYLES)
    canvas = np.ones((rows * RES, cols * RES, 4), np.float32)
    for (r, c), px in tiles.items():
        y0 = (rows - 1 - r) * RES; canvas[y0:y0 + RES, c * RES:(c + 1) * RES] = px
    save_px(canvas, f"{OUT}/contact_sheet_v2.png")
    with open(f"{OUT}/index.html", "w") as f:
        f.write("<!doctype html><meta charset=utf-8><title>Zoo styles v2</title><style>body{font:14px system-ui;margin:16px;"
                "background:#222;color:#eee}table{border-collapse:collapse}td,th{padding:2px;text-align:center}"
                "img{width:220px;display:block}th{font-weight:600;max-width:220px}</style><h1>Cel and paper variants</h1><table><tr>")
        f.write("".join(f"<th>{lab}</th>" for _, lab, _ in STYLES) + "</tr>")
        for asset in ASSETS:
            n = asset.split("/")[1]
            f.write("<tr>" + "".join(f"<td><img src='{n}__{k}.png'></td>" for k, _, _ in STYLES) + "</tr>")
        f.write("</table>")
    print("SHEET DONE", flush=True)
