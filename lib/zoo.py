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

from lib import palette

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETTE_PNG = os.path.join(ROOT, "palette", "palette.png")
MAT_NAME = "MAT_palette"

# GOALS.md budgets: (max tris, max bytes)
BUDGETS = {"animals": (5000, 300_000), "keepers": (3000, 300_000), "facilities": (10000, 300_000)}
DEFAULT_BUDGET = (2000, 150_000)


def budget(category):
    return BUDGETS.get(category, DEFAULT_BUDGET)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


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


def paint(bm, colour, faces=None):
    """Map each face to a small copy of itself inside the colour's swatch (no zero-area UVs)."""
    uv = bm.loops.layers.uv.verify()
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


def _obj(bm, name="part"):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _place(bm, loc, rot, scale):
    m = Matrix.Translation(loc) @ _rot(rot) @ Matrix.Diagonal((*scale, 1))
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def _rot(rot):
    rx, ry, rz = (math.radians(a) for a in rot)
    return (Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(rx, 4, "X"))


def box(size, loc=(0, 0, 0), colour="grey", rot=(0, 0, 0), taper=1.0):
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
    return _obj(bm)


def cyl(r, h, loc=(0, 0, 0), colour="grey", rot=(0, 0, 0), seg=8, r2=None):
    """Cylinder (or truncated cone with r2) along local Z, centred at loc."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    _place(bm, Vector(loc), rot, (1, 1, 1))
    paint(bm, colour)
    return _obj(bm)


def cone(r, h, loc=(0, 0, 0), colour="grey", rot=(0, 0, 0), seg=8):
    return cyl(r, h, loc, colour, rot, seg, r2=0.0)


def ball(r, loc=(0, 0, 0), colour="grey", scale=(1, 1, 1), rot=(0, 0, 0), seg=10, rings=6):
    """Low-poly UV sphere of radius r, stretched by scale."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    _place(bm, Vector(loc), rot, scale)
    paint(bm, colour)
    return _obj(bm)


def mirror_x(fn, *a, loc=(0, 0, 0), **kw):
    """Make a part and its copy mirrored across X=0 (left/right legs, eyes, ears). Returns both."""
    x, y, z = loc
    return fn(*a, loc=(x, y, z), **kw), fn(*a, loc=(-x, y, z), **kw)


def finish(asset):
    """Join all parts into SM_<category>_<name>, apply transforms, origin at floor centre."""
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not obs:
        raise ValueError(f"{asset['id']}: generator made no parts")
    bm = bmesh.new()
    for o in obs:
        tmp = o.data.copy()
        tmp.transform(o.matrix_world)
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
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


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
    radius = max(dims.length / 2, 0.05)
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
