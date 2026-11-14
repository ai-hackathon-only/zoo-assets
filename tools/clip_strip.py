"""Frame strip of one clip of one GLB (motion review evidence).
Usage: blender -b -noaudio --factory-startup --python tools/clip_strip.py -- <glb> <clip> <frames> <out.png> [view: side|front]
Renders <frames> evenly spaced frames of the clip, ortho, and joins them left to right."""
import bpy, sys, numpy as np
from mathutils import Vector
glb, clip, n, out = sys.argv[sys.argv.index('--')+1:][:4]
view = (sys.argv[sys.argv.index('--')+1:] + ['side'])[4]
n = int(n)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
act = bpy.data.actions.get(clip) or next((a for a in bpy.data.actions if a.name.split('|')[-1] == clip), None)
assert act, f"no clip {clip}; have {[a.name for a in bpy.data.actions]}"
arm.animation_data_create().action = act
f0, f1 = act.frame_range
pts = [(o.matrix_world @ Vector(c)) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
ctr = (lo + hi) / 2; size = max(hi - lo) * 1.35
cam = bpy.data.cameras.new("c"); cam.type = 'ORTHO'; cam.ortho_scale = size
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
if view == 'side': co.location = (ctr.x + 40, ctr.y, ctr.z); co.rotation_euler = (1.5708, 0, 1.5708)
else: co.location = (ctr.x, ctr.y - 40, ctr.z); co.rotation_euler = (1.5708, 0, 0)
cam.clip_end = 200
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", 'SUN')); sun.rotation_euler = (0.8, 0.2, 0.4); sc.collection.objects.link(sun)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.88, 1)
sc.render.engine = 'BLENDER_EEVEE'; R = 360; sc.render.resolution_x = R; sc.render.resolution_y = R
tiles = []
for i in range(n):
    sc.frame_set(round(f0 + (f1 - f0) * i / n))  # n frames, last one excluded (loops back to first)
    sc.render.filepath = f"/tmp/s1/_f{i}.png"; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(sc.render.filepath); a = np.array(im.pixels[:]).reshape(R, R, 4); tiles.append(a)
strip = np.concatenate(tiles, axis=1)
img = bpy.data.images.new("strip", R * n, R, alpha=True); img.pixels = strip.ravel().tolist()
img.filepath_raw = out; img.file_format = 'PNG'; img.save()
print("STRIP", out, "frames", n, "range", f0, f1)
