# Style test for zoo-assets: re-render existing GLBs in different looks (post-process only, no generator changes).
# blender -b -noaudio --factory-startup --python style_test.py -- <repo> <outdir>
import bpy, sys, math, os
import numpy as np
from mathutils import Vector

REPO, OUT = sys.argv[sys.argv.index("--") + 1:][:2]
ASSETS = ["animals/giraffe", "animals/lion", "animals/giant_panda", "plants/acacia_tree", "vehicles/animal_transport_truck"]
STYLES = ["original", "cel", "voxel", "clay", "faceted", "wood", "paper", "hologram", "pixel", "bronze", "night"]
RES = 320


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def load(asset):
    bpy.ops.import_scene.gltf(filepath=f"{REPO}/assets/{asset}.glb")
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return ob


def palette_tex(nt):
    for n in nt.nodes:
        if n.type == "TEX_IMAGE":
            return n
    return None


def mat(name, build):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(build(nt), out.inputs["Surface"])
    return m


def tex_node(nt, img):
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = "Closest"
    return t


def set_mat(ob, m):
    ob.data.materials.clear()
    ob.data.materials.append(m)


def mod(ob, kind, **kw):
    md = ob.modifiers.new(kind.lower(), kind)
    for k, v in kw.items():
        setattr(md, k, v)
    return md


def face_colors(ob, img):
    w, h = img.size; px = np.array(img.pixels[:]).reshape(h, w, 4)
    me = ob.data; uv = me.uv_layers.active.data; out = []
    for poly in me.polygons:
        u = sum(uv[i].uv.x for i in poly.loop_indices) / poly.loop_total
        v = sum(uv[i].uv.y for i in poly.loop_indices) / poly.loop_total
        c = px[min(h - 1, max(0, int(v * h))), min(w - 1, max(0, int(u * w)))].copy()
        c[:3] = np.where(c[:3] <= 0.04045, c[:3] / 12.92, ((c[:3] + 0.055) / 1.055) ** 2.4)  # sRGB -> linear
        out.append(c)
    return out


def write_corner_colors(me, cols):
    a = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
    for poly, c in zip(me.polygons, cols):
        for li in poly.loop_indices:
            a.data[li].color = c


def attr_color(nt):
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = "col"; return a.outputs["Color"]


def lines(color, thick):
    sc = bpy.context.scene; sc.render.use_freestyle = True; vl = sc.view_layers[0]; vl.use_freestyle = True
    fs = vl.freestyle_settings; ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("lines")
    ls.linestyle = ls.linestyle or bpy.data.linestyles.new("ink"); ls.linestyle.color = color; ls.linestyle.thickness = thick
    ls.select_by_visibility = True; ls.select_crease = True; ls.select_silhouette = True; ls.select_border = True
    fs.crease_angle = math.radians(140)


def apply_style(ob, style, img):
    L = lambda nt, a, b: nt.links.new(a, b)
    if style == "cel":
        def b(nt):
            t = tex_node(nt, img); d = nt.nodes.new("ShaderNodeBsdfDiffuse"); s2r = nt.nodes.new("ShaderNodeShaderToRGB")
            ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
            ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.5, 1); ramp.color_ramp.elements[1].position = 0.25
            mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1
            em = nt.nodes.new("ShaderNodeEmission")
            L(nt, d.outputs[0], s2r.inputs[0]); L(nt, s2r.outputs[0], ramp.inputs[0])
            L(nt, t.outputs[0], mul.inputs[6]); L(nt, ramp.outputs[0], mul.inputs[7]); L(nt, mul.outputs[2], em.inputs[0])
            return em.outputs[0]
        set_mat(ob, mat("cel", b))
        lines((0.03, 0.03, 0.05), 2.0)
    elif style == "voxel":
        from mathutils.kdtree import KDTree
        cols = face_colors(ob, img); kd = KDTree(len(ob.data.polygons))
        for i, poly in enumerate(ob.data.polygons): kd.insert(poly.center, i)
        kd.balance()
        mod(ob, "REMESH", mode="BLOCKS", octree_depth=6, use_remove_disconnected=False)
        bpy.ops.object.modifier_apply(modifier="remesh")
        write_corner_colors(ob.data, [cols[kd.find(p.center)[1]] for p in ob.data.polygons])
        def b(nt):
            p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.7
            L(nt, attr_color(nt), p.inputs["Base Color"]); return p.outputs[0]
        set_mat(ob, mat("voxel", b))
    elif style == "clay":
        write_corner_colors(ob.data, face_colors(ob, img))
        mod(ob, "SUBSURF", levels=2, render_levels=2)
        for p in ob.data.polygons: p.use_smooth = True
        def b(nt):
            hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 0.85
            hsv.inputs["Value"].default_value = 1.0
            p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.85
            p.inputs["Subsurface Weight"].default_value = 0.15
            n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 40
            bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.03
            L(nt, attr_color(nt), hsv.inputs["Color"]); L(nt, hsv.outputs[0], p.inputs["Base Color"])
            L(nt, n.outputs[0], bump.inputs["Height"]); L(nt, bump.outputs[0], p.inputs["Normal"])
            return p.outputs[0]
        set_mat(ob, mat("clay", b))
    elif style == "faceted":
        mod(ob, "DECIMATE", ratio=0.55)
        for p in ob.data.polygons: p.use_smooth = False
        def b(nt):
            t = tex_node(nt, img); p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.35
            p.inputs["Coat Weight"].default_value = 0.4
            L(nt, t.outputs[0], p.inputs["Base Color"]); return p.outputs[0]
        set_mat(ob, mat("facet", b))
    elif style == "wood":
        mod(ob, "BEVEL", width=0.01 * max(ob.dimensions), segments=2)
        def b(nt):
            t = tex_node(nt, img); w = nt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = 6
            w.inputs["Distortion"].default_value = 6; w.wave_type = "RINGS"
            mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = 0.35
            wood = nt.nodes.new("ShaderNodeMix"); wood.data_type = "RGBA"; wood.inputs[0].default_value = 0.45
            wood.inputs[7].default_value = (0.55, 0.36, 0.2, 1)
            p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.4
            L(nt, t.outputs[0], wood.inputs[6]); L(nt, wood.outputs[2], mix.inputs[6]); L(nt, w.outputs[0], mix.inputs[7])
            L(nt, mix.outputs[2], p.inputs["Base Color"]); return p.outputs[0]
        set_mat(ob, mat("wood", b))
    elif style == "paper":
        mod(ob, "DECIMATE", decimate_type="DISSOLVE", angle_limit=math.radians(12))
        mod(ob, "TRIANGULATE")
        for p in ob.data.polygons: p.use_smooth = False
        def b(nt):
            t = tex_node(nt, img); mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs[0].default_value = 0.3
            mix.inputs[7].default_value = (0.95, 0.93, 0.88, 1)
            d = nt.nodes.new("ShaderNodeBsdfDiffuse"); L(nt, t.outputs[0], mix.inputs[6]); L(nt, mix.outputs[2], d.inputs[0])
            return d.outputs[0]
        set_mat(ob, mat("paper", b))
        lines((0.25, 0.2, 0.15), 2.0)
    elif style == "hologram":
        mod(ob, "WIREFRAME", thickness=0.004 * max(ob.dimensions), use_replace=True)
        def b(nt):
            e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (0.2, 0.8, 1.0, 1); e.inputs[1].default_value = 3
            return e.outputs[0]
        set_mat(ob, mat("holo", b))
    elif style == "bronze":
        def b(nt):
            p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Base Color"].default_value = (0.55, 0.33, 0.14, 1)
            p.inputs["Metallic"].default_value = 1; p.inputs["Roughness"].default_value = 0.3
            return p.outputs[0]
        set_mat(ob, mat("bronze", b))
        mod(ob, "BEVEL", width=0.006 * max(ob.dimensions), segments=2)
    elif style == "night":
        def b(nt):
            t = tex_node(nt, img); p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.6
            L(nt, t.outputs[0], p.inputs["Base Color"]); return p.outputs[0]
        set_mat(ob, mat("night", b))
    elif style == "plush":
        mod(ob, "SUBSURF", levels=2, render_levels=2)
        for p in ob.data.polygons: p.use_smooth = True
        def b(nt):
            t = tex_node(nt, img); hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 0.75
            hsv.inputs["Value"].default_value = 1.2
            p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 1
            p.inputs["Sheen Weight"].default_value = 1; p.inputs["Sheen Roughness"].default_value = 0.3
            n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 400
            bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
            L(nt, t.outputs[0], hsv.inputs["Color"]); L(nt, hsv.outputs[0], p.inputs["Base Color"])
            L(nt, n.outputs[0], bump.inputs["Height"]); L(nt, bump.outputs[0], p.inputs["Normal"])
            return p.outputs[0]
        set_mat(ob, mat("plush", b))


def setup_render(ob, style):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard" if style in ("cel", "hologram", "pixel", "paper") else "AgX"
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bgcol = {"hologram": (0.01, 0.02, 0.05, 1), "night": (0.01, 0.015, 0.04, 1), "paper": (0.93, 0.9, 0.84, 1),
             "bronze": (0.25, 0.25, 0.27, 1)}.get(style, (0.82, 0.86, 0.9, 1))
    bg.inputs[0].default_value = bgcol; bg.inputs[1].default_value = 0.6 if style != "night" else 0.3
    # camera: 3/4 view fitted to bounds
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    ctr = sum(corners, Vector()) / 8; size = max((c - ctr).length for c in corners)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    d = Vector((1.0, -1.25, 0.8)).normalized()
    if style == "pixel":
        cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.6
    else:
        cam.data.lens = 50
    cam.location = ctr + d * size * 2.5
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30)); sun.data.energy = 3.5 if style != "night" else 0.4
    sun.data.angle = math.radians(8)
    if style == "night":
        sun.data.color = (0.5, 0.6, 1.0)
        for i, (x, y, c) in enumerate([(1, -1, (1, 0.6, 0.3)), (-1.2, 0.4, (1, 0.75, 0.4))]):
            lt = bpy.data.objects.new(f"lamp{i}", bpy.data.lights.new(f"lamp{i}", "POINT")); sc.collection.objects.link(lt)
            lt.location = ctr + Vector((x, y, 0.6)) * size; lt.data.color = c; lt.data.energy = 600 * size * size
    if style not in ("hologram", "night"):
        fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", "SUN")); sc.collection.objects.link(fill)
        fill.rotation_euler = (math.radians(70), 0, math.radians(200)); fill.data.energy = 0.8
    if style not in ("hologram", "paper"):  # ground with shadow catcher
        bpy.ops.mesh.primitive_plane_add(size=size * 12, location=(ctr.x, ctr.y, min(c.z for c in corners)))
        g = bpy.context.object; g.is_shadow_catcher = True
        gm = bpy.data.materials.new("ground"); gm.use_nodes = True
        gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = bgcol
        g.data.materials.append(gm)
    if style == "pixel":
        sc.render.resolution_x = sc.render.resolution_y = 64
        sc.render.filter_size = 0.0


def sheet(paths, rows, cols, out):
    tile = RES
    canvas = np.ones((rows * tile, cols * tile, 4), dtype=np.float32)
    for (r, c), p in paths.items():
        im = bpy.data.images.load(p); w, h = im.size
        px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        if w != tile:  # nearest-neighbour upscale (pixel style)
            k = tile // w; px = px.repeat(k, 0).repeat(k, 1)
        y0 = (rows - 1 - r) * tile  # Blender images are bottom-up
        canvas[y0:y0 + tile, c * tile:(c + 1) * tile] = px
    img = bpy.data.images.new("sheet", cols * tile, rows * tile, alpha=True)
    img.pixels[:] = canvas.ravel(); img.filepath_raw = out; img.file_format = "PNG"; img.save()


if __name__ == "__main__":
    paths = {}
    os.makedirs(OUT, exist_ok=True)
    for r, asset in enumerate(ASSETS):
        for c, style in enumerate(STYLES):
            out = f"{OUT}/{asset.split('/')[1]}__{style}.png"
            reset()
            ob = load(asset)
            img = next((i for i in bpy.data.images if i.size[0] > 0), None)
            if style == "original":
                sc = bpy.context.scene
            apply_style(ob, style, img)
            setup_render(ob, style)
            bpy.context.scene.render.filepath = out
            bpy.ops.render.render(write_still=True)
            paths[(r, c)] = out
            print("RENDERED", out, flush=True)
    sheet(paths, len(ASSETS), len(STYLES), f"{OUT}/contact_sheet.png")
    print("SHEET DONE", flush=True)
