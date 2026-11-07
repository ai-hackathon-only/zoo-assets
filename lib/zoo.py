"""Shared helpers for every generator: parts, palette UVs, naming, origin, export, thumbnails.

A generator module has `build(asset, z)` that adds parts with z.box/z.cyl/z.ball/z.cone.
build_all.py then calls z.finish() -> one mesh `SM_<category>_<name>`, one material `MAT_palette`.
Units: metres, Z up in Blender (the glTF exporter writes Y up).
"""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

from lib import palette, variants

_RECOLOUR = None   # set by begin() for rare variants
_VARIANT = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETTE_PNG = os.path.join(ROOT, "palette", "palette.png")
MAT_NAME = "MAT_palette"
EMISSIVE_MAT_NAME = "MAT_emissive"

# GOALS.md budgets: (max tris, max bytes)
BUDGETS = {"animals": (5000, 300_000), "keepers": (3000, 300_000), "facilities": (10000, 300_000)}
DEFAULT_BUDGET = (2000, 150_000)


def budget(category):
    return BUDGETS.get(category, DEFAULT_BUDGET)


def reset():
    global _RECOLOUR, _VARIANT
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _RECOLOUR = _VARIANT = None


def begin(asset):
    """Call after reset(), before the generator: switches on the asset's variant (see lib/variants.py)."""
    global _RECOLOUR, _VARIANT
    _VARIANT = asset.get("variant")
    rc = asset.get("params", {}).get("recolour")
    _RECOLOUR = variants.recolour_fn(rc, asset.get("params", {}).get("body")) if _VARIANT == "rare" and rc else None


def material():
    mat = bpy.data.materials.get(MAT_NAME)
    if mat:
        return mat
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.8
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(PALETTE_PNG, check_existing=True)
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def emissive_material(colour=(1.0, 0.95, 0.5, 1.0), strength=5.0):
    mat = bpy.data.materials.get(EMISSIVE_MAT_NAME)
    if mat:
        return mat
    mat = bpy.data.materials.new(EMISSIVE_MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.2
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(PALETTE_PNG, check_existing=True)
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = colour
    elif "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = colour
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def paint(bm, colour, faces=None):
    """Map each face to a small copy of itself inside the colour's swatch (no zero-area UVs)."""
    uv = bm.loops.layers.uv.verify()
    if _RECOLOUR:
        colour = _RECOLOUR(colour)
    cu, cv, half = palette.swatch(colour)
    for f in (faces if faces is not None else bm.faces):
        n = f.normal if f.normal.length > 0 else Vector((0, 0, 1))
        t = (f.verts[1].co - f.verts[0].co).normalized()
        b = n.cross(t)
        c = f.calc_center_median()
        pts = [((l.vert.co - c).dot(t), (l.vert.co - c).dot(b)) for l in f.loops]
        s = max(max(abs(x), abs(y)) for x, y in pts) or 1.0
        for l, (x, y) in zip(f.loops, pts):
            l[uv].uv = (cu + x / s * half * .8, cv + y / s * half * .8)


def _obj(bm, name="part", emissive=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    if emissive:
        ob["is_emissive"] = True
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _place(bm, loc, rot, scale):
    m = Matrix.Translation(loc) @ _rot(rot) @ Matrix.Diagonal((*scale, 1))
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def _rot(rot):
    rx, ry, rz = (math.radians(a) for a in rot)
    return (Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(rx, 4, "X"))


def box(size, loc=(0, 0, 0), colour="grey", rot=(0, 0, 0), taper=1.0, emissive=False):
    """Box of size (x, y, z) centred at loc. taper<1 shrinks the top face (toy wedge shapes)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    if taper != 1.0:
        for v in bm.verts:
            if v.co.z > 0:
                v.co.x *= taper
                v.co.y *= taper
    _place(bm, Vector(loc), rot, size)
    paint(bm, colour)
    return _obj(bm, emissive=emissive)


def cyl(r, h, loc=(0, 0, 0), colour="grey", rot=(0, 0, 0), seg=8, r2=None, emissive=False):
    """Cylinder (or truncated cone with r2) along local Z, centred at loc."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    _place(bm, Vector(loc), rot, (1, 1, 1))
    paint(bm, colour)
    return _obj(bm, emissive=emissive)


def cone(r, h, loc=(0, 0, 0), colour="grey", rot=(0, 0, 0), seg=8, emissive=False):
    return cyl(r, h, loc, colour, rot, seg, r2=0.0, emissive=emissive)


def ball(r, loc=(0, 0, 0), colour="grey", scale=(1, 1, 1), rot=(0, 0, 0), seg=10, rings=6, emissive=False):
    """Low-poly UV sphere of radius r, stretched by scale."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    _place(bm, Vector(loc), rot, scale)
    paint(bm, colour)
    return _obj(bm, emissive=emissive)


def mirror_x(fn, *a, loc=(0, 0, 0), **kw):
    """Make a part and its copy mirrored across X=0 (left/right legs, eyes, ears). Returns both."""
    x, y, z = loc
    return fn(*a, loc=(x, y, z), **kw), fn(*a, loc=(-x, y, z), **kw)


def finish(asset):
    """Join all parts into SM_<category>_<name>, apply transforms, origin at floor centre."""
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not obs:
        raise ValueError(f"{asset['id']}: generator made no parts")
    if _VARIANT == "baby":
        _babyfy(obs, asset)
    bm = bmesh.new()
    has_emissive = any(o.get("is_emissive", False) for o in obs)
    for o in obs:
        is_em = o.get("is_emissive", False)
        tmp = o.data.copy()
        tmp.transform(o.matrix_world)
        if has_emissive:
            bm_part = bmesh.new()
            bm_part.from_mesh(tmp)
            mat_idx = 1 if is_em else 0
            for f in bm_part.faces:
                f.material_index = mat_idx
            bm_part.to_mesh(tmp)
            bm_part.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    for o in obs:
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
    lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
    hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
    shift = Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))
    bmesh.ops.translate(bm, vec=shift, verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    name = object_name(asset)
    ob = _obj(bm, name)
    ob.data.name = name
    ob.data.materials.append(material())
    if has_emissive:
        ob.data.materials.append(emissive_material())
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def _babyfy(obs, asset):
    """Bigger head, shorter legs, then fit back to size_m. Animals face -Y; upright ones (H > L) have the
    head on top. Head parts: centre in the top 35 % of the height and (upright or the front 40 % of length)."""
    bpy.context.view_layer.update()
    def bounds(o):
        ps = [o.matrix_world @ v.co for v in o.data.vertices]
        return (Vector([min(p[i] for p in ps) for i in range(3)]), Vector([max(p[i] for p in ps) for i in range(3)]))
    bb = {o.name: bounds(o) for o in obs}
    lo = Vector([min(b[0][i] for b in bb.values()) for i in range(3)])
    hi = Vector([max(b[1][i] for b in bb.values()) for i in range(3)])
    size = hi - lo
    upright = size.z > size.y * 1.1
    def centre(o):
        a, b = bb[o.name]
        return (a + b) / 2
    head = [o for o in obs if centre(o).z > lo.z + size.z * 0.65
            and (upright or centre(o).y < lo.y + size.y * 0.4)]
    if head:
        hl = Vector([min(bb[o.name][0][i] for o in head) for i in range(3)])
        hh = Vector([max(bb[o.name][1][i] for o in head) for i in range(3)])
        # neck joint: back-bottom of the head for walkers, bottom centre for upright animals
        pivot = Vector(((hl.x + hh.x) / 2, (hl.y + hh.y) / 2 if upright else hh.y, hl.z))
        m = Matrix.Translation(pivot) @ Matrix.Scale(variants.BABY_HEAD, 4) @ Matrix.Translation(-pivot)
        for o in head:
            o.data.transform(o.matrix_world)
            o.matrix_world = Matrix()
            o.data.transform(m)
    # legs: squash everything under the torso line towards the floor, lift the rest by the same amount
    cut = lo.z + size.z * (0.3 if not upright else 0.2)
    drop = (cut - lo.z) * (1 - variants.BABY_LEG)
    for o in obs:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix()
        for v in o.data.vertices:
            if v.co.z < cut:
                v.co.z = lo.z + (v.co.z - lo.z) * variants.BABY_LEG
            else:
                v.co.z -= drop
    # fit back to the baby's size_m height
    zs = [v.co.z for o in obs for v in o.data.vertices]
    k = asset["size_m"][2] / max(max(zs) - min(zs), 1e-6)
    for o in obs:
        o.data.transform(Matrix.Scale(k, 4))


def object_name(asset):
    return f"SM_{asset['category']}_{asset['id']}"


def export_glb(ob, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_texcoords=True, export_normals=True,
                              export_materials="EXPORT", export_animations=False)


def render_thumb(ob, path, res=256):
    """Same rules for every asset: 3/4 view from front-right, ortho, framed on the bounding box."""
    sc = bpy.context.scene
    dims = ob.dimensions
    centre = Vector((0, 0, dims.z / 2))
    radius = max(dims.length / 2, 0.005)
    cam_d = bpy.data.cameras.new("thumb_cam")
    cam_d.type = "ORTHO"
    cam = bpy.data.objects.new("thumb_cam", cam_d)
    sc.collection.objects.link(cam)
    direction = Vector((1.0, -1.4, 0.8)).normalized()
    cam.location = centre + direction * radius * 4
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    # fit: project the 8 bounding-box corners on the camera's right/up axes, 8 % margin
    rm = cam.rotation_euler.to_matrix()
    right, up = rm.col[0], rm.col[1]
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs = [(c - centre).dot(right) for c in corners]
    ys = [(c - centre).dot(up) for c in corners]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    cam.location += right * cx + up * cy
    cam_d.ortho_scale = max(max(xs) - min(xs), max(ys) - min(ys), 0.01) * 1.08
    cam_d.clip_start = radius * 0.1  # default 0.1 m would clip assets under ~5 cm
    cam_d.clip_end = radius * 10
    sc.camera = cam
    sun_d = bpy.data.lights.new("thumb_sun", "SUN")
    sun_d.energy = 3.0
    sun = bpy.data.objects.new("thumb_sun", sun_d)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    sc.collection.objects.link(sun)
    world = bpy.data.worlds.new("thumb_world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.9, 0.92, 0.95, 1)
    bg.inputs["Strength"].default_value = 0.9
    sc.world = world
    # Workbench: no GPU shader cache, same image on every machine, ~0.2 s per thumb.
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "TEXTURE"
    sh.show_shadows = True
    sh.show_cavity = False
    sc.display.render_aa = "8"
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    for o in (cam, sun):
        bpy.data.objects.remove(o)
