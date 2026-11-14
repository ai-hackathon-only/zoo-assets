"""Render missing frame strips across all RIGS.md skeletons in one headless Blender invocation.
Usage: blender -b -noaudio --factory-startup --python tools/render_all_strips.py"""
import bpy, os, numpy as np
from mathutils import Vector

JOBS = [
    ("assets/animals/african_elephant.glb", "walk", 6, "docs/motion/quadruped/african_elephant_walk.png", "side"),
    ("assets/animals/african_elephant.glb", "eat", 3, "docs/motion/quadruped/african_elephant_eat.png", "side"),
    ("assets/animals/giraffe.glb", "walk", 6, "docs/motion/hoofed/giraffe_walk.png", "side"),
    ("assets/animals/giraffe.glb", "eat", 3, "docs/motion/hoofed/giraffe_eat.png", "side"),
    ("assets/animals/lion.glb", "walk", 6, "docs/motion/bigcat/lion_walk.png", "side"),
    ("assets/animals/lion.glb", "eat", 3, "docs/motion/bigcat/lion_eat.png", "side"),
    ("assets/animals/meerkat.glb", "walk", 6, "docs/motion/upright/meerkat_walk.png", "side"),
    ("assets/animals/meerkat.glb", "eat", 3, "docs/motion/upright/meerkat_eat.png", "side"),
    ("assets/animals/reticulated_python.glb", "slither", 6, "docs/motion/snake/reticulated_python_slither.png", "side"),
    ("assets/animals/monarch_butterfly.glb", "crawl", 6, "docs/motion/insect/monarch_butterfly_crawl.png", "side"),
    ("assets/animals/emperor_scorpion.glb", "crawl", 6, "docs/motion/arachnid/emperor_scorpion_crawl.png", "side"),
    ("assets/animals/giant_african_snail.glb", "crawl", 6, "docs/motion/mollusc/giant_african_snail_crawl.png", "side"),
    ("assets/visitors/visitor_wheelchair_user_22.glb", "walk", 6, "docs/motion/human_onepiece/visitor_wheelchair_user_22_walk.png", "side"),
    ("assets/vehicles/keeper_golf_cart.glb", "drive", 6, "docs/motion/vehicle/keeper_golf_cart_drive.png", "side"),
    ("assets/facilities/fence_wood_rail_straight.glb", "idle", 3, "docs/motion/facility/fence_wood_rail_straight_idle.png", "side"),
    ("assets/landscape/boulder_small.glb", "idle", 3, "docs/motion/static/boulder_small_idle.png", "side"),
    ("assets/keepers/keeper_elephant_keeper_09.glb", "walk", 6, "docs/motion/human/keeper_elephant_keeper_09_walk.png", "side"),
    ("assets/animals/clownfish.glb", "swim", 6, "docs/motion/fish/clownfish_swim.png", "side"),
]

R = 360
pid = os.getpid()

for glb, clip, n, out, view in JOBS:
    if os.path.exists(out):
        print("SKIP", out)
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    sc = bpy.context.scene
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = bpy.data.actions.get(clip) or next((a for a in bpy.data.actions if a.name.split('|')[-1] == clip), None)
    assert act, f"no clip {clip} in {glb}"
    arm.animation_data_create().action = act
    f0, f1 = act.frame_range
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('SM_')] or [o for o in bpy.data.objects if o.type == 'MESH']
    pts = [(o.matrix_world @ Vector(c)) for o in meshes for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (lo + hi) / 2
    size = max(hi - lo) * 1.35
    cam = bpy.data.cameras.new("c")
    cam.type = 'ORTHO'
    cam.ortho_scale = size
    co = bpy.data.objects.new("c", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    if view == 'side':
        co.location = (ctr.x + 40, ctr.y, ctr.z)
        co.rotation_euler = (1.5708, 0, 1.5708)
    else:
        co.location = (ctr.x, ctr.y - 40, ctr.z)
        co.rotation_euler = (1.5708, 0, 0)
    cam.clip_end = 200
    sun = bpy.data.objects.new("s", bpy.data.lights.new("s", 'SUN'))
    sun.rotation_euler = (0.8, 0.2, 0.4)
    sc.collection.objects.link(sun)
    sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.88, 1)
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = R
    sc.render.resolution_y = R
    tiles = []
    for i in range(n):
        sc.frame_set(round(f0 + (f1 - f0) * i / n))
        tmp = f"/tmp/render_all_{pid}_f{i}.png"
        sc.render.filepath = tmp
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(tmp)
        a = np.array(im.pixels[:]).reshape(R, R, 4)
        tiles.append(a)
    strip = np.concatenate(tiles, axis=1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    img = bpy.data.images.new("strip", R * n, R, alpha=True)
    img.pixels = strip.ravel().tolist()
    img.filepath_raw = out
    img.file_format = 'PNG'
    img.save()
    print("STRIP", out, "frames", n, "range", f0, f1)
