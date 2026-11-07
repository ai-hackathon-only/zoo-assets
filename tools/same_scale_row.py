"""Render GLBs side by side at one shared scale (side view, ortho). Usage:
blender -b -noaudio --factory-startup --python tools/same_scale_row.py -- <id> <id> ...  (writes /tmp/s1/same_scale.png)"""
import bpy, sys
from mathutils import Vector
ids = sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
x = 0.0
for i in ids:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"assets/animals/{i}.glb")
    new = [o for o in bpy.data.objects if o not in before]
    xs = [ (o.matrix_world @ Vector(c)).y for o in new if o.type=='MESH' for c in o.bound_box]
    w = max(xs)-min(xs)
    for o in new:
        if o.parent is None: o.location.y += x - min(xs)
    x += w + 0.6
sc = bpy.context.scene
cam = bpy.data.cameras.new("c"); cam.type='ORTHO'; cam.ortho_scale = x + 0.5
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
co.location = (40, x/2, 2.9); co.rotation_euler = (1.5708, 0, 1.5708)
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", 'SUN')); sun.rotation_euler=(0.8,0.2,0.4); sc.collection.objects.link(sun)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(0.9,0.9,0.88,1)
sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1600; sc.render.resolution_y=int(1600*6.2/(x+0.5))+1
sc.render.filepath="/tmp/s1/same_scale.png"; bpy.ops.render.render(write_still=True)
print("ROW", x)
