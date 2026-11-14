# Render ink sprite strips for a list of assets from the GLBs on main.
# blender -b -noaudio --factory-startup --python tools/sumi-e/sprite_shard.py -- <repo> <outdir> <shard.json> <id> [<id> ...]
# Writes <outdir>/<category>/<id>.png (greyscale strip, 128 px tiles) and <outdir>/shard-<tag>.json.
import bpy, os, sys, json, math, importlib.util
from mathutils import Vector
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v2", os.path.join(HERE, "style_v2.py"))
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
args = sys.argv[sys.argv.index("--") + 1:]
EIGHT_DIR = "--8dir" in args
if EIGHT_DIR: args.remove("--8dir")
REPO, OUT, SHARD, IDS = args[0], args[1], args[2], args[3:]
TILE, SS = (96 if EIGHT_DIR else 128), 2                 # tile size, supersampling factor
LOCO = ("walk", "run", "drive", "swim", "fly", "hop", "crawl", "slither", "gallop", "sway")
LEVELS = 24                       # grey levels kept, keeps the PNG small
ELEV = math.radians(35)
CAM_DIRS = [Vector((math.sin(i * math.pi / 4) * math.cos(ELEV), -math.cos(i * math.pi / 4) * math.cos(ELEV), math.sin(ELEV))) for i in range(8)]

v2.RES = TILE * SS
_ls = v2.lineset
v2.lineset = lambda fs, coll, name, color, thick, **kw: _ls(fs, coll, name, color, thick * 0.8, **kw)  # thinner at 256 px, ~2 px after downsampling


def frames_for(clip):
    base = clip.split("_")[0]
    if base in LOCO: return 6
    if base == "idle": return 2
    return 3


def load(cat, aid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{REPO}/assets/{cat}/{aid}.glb")
    arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
    if arm:
        for o in {pb.custom_shape for pb in arm.pose.bones if pb.custom_shape}: bpy.data.objects.remove(o)
        ad = arm.animation_data_create()
        for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1: bpy.ops.object.join()
    return arm, bpy.context.view_layer.objects.active


def shoot(ob, first, out, seed, cam_dir=None, ctr=None, size=None):
    sc = bpy.context.scene
    if first:
        v2.render(ob, "ink", "paper", out, cam_dir=cam_dir)
    else:
        if cam_dir is not None and sc.camera:
            sc.camera.location = ctr + cam_dir * size * 2.5
            sc.camera.rotation_euler = (ctr - sc.camera.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    px = v2.load_px(out)
    bg = v2.paper_bg("ink", *px.shape[:2], seed=seed)
    rgb = np.clip(px[..., :3] * bg[..., :3] / np.array(v2.PAPER["ink"], np.float32), 0, 1)
    g = rgb.mean(axis=2)
    g = g.reshape(TILE, SS, TILE, SS).mean(axis=(1, 3))      # 2x2 box downsample
    return np.round(g * (LEVELS - 1)) / (LEVELS - 1)


def save_gray(g, path):
    h, w = g.shape
    im = bpy.data.images.new("s", w, h, alpha=False, float_buffer=False)
    im.colorspace_settings.name = "Non-Color"
    rgba = np.repeat(g[..., None], 4, axis=2); rgba[..., 3] = 1
    im.pixels[:] = rgba.ravel()
    s = bpy.context.scene.render.image_settings
    s.file_format = "PNG"; s.color_mode = "BW"; s.color_depth = "8"; s.compression = 100
    s.color_management = "OVERRIDE"; s.view_settings.view_transform = "Standard"
    im.save_render(path)
    bpy.data.images.remove(im)


if __name__ == "__main__":
    meta = json.load(open(SHARD)) if os.path.exists(SHARD) else {}
    result = {}
    tmp = f"{OUT}/_tmp_{os.getpid()}.png"
    os.makedirs(OUT, exist_ok=True)
    for ref in IDS:
        cat, aid = ref.split("/")
        arm, ob = load(cat, aid)
        img = next((i for i in bpy.data.images if i.size[0] > 0), None)
        v2.style(ob, "ink", img)
        acts = sorted(bpy.data.actions, key=lambda a: a.name)
        clips, tiles, n = {}, [], 0
        plan = []
        if arm and acts:
            for a in acts:
                name = a.name.split("_")[-1] if a.name.startswith(("AR_", "ACT_")) else a.name
                plan.append((name, a))
        else:
            plan.append(("idle", None))
        seen = set()
        if EIGHT_DIR:
            plan = [(n, a) for n, a in plan if n.split("_")[0] in LOCO or n.split("_")[0] == "idle"] or [("idle", None)]
            corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
            ctr = sum(corners, Vector()) / 8
            size = max((c - ctr).length for c in corners)
            dir_tiles = [[] for _ in range(8)]
            n_frames = 0
            for name, act in plan:
                if name in seen: continue
                seen.add(name)
                k = frames_for(name)
                if act is not None:
                    arm.animation_data.action = act
                    if hasattr(arm.animation_data, "action_slot") and act.slots:
                        arm.animation_data.action_slot = act.slots[0]
                    f0, f1 = act.frame_range
                    if f1 <= f0: k = 1
                    fr = [f0 + (f1 - f0) * i / k for i in range(k)]
                else:
                    fr = [1]; k = 1
                clips[name] = {"start": n_frames, "frames": len(fr)}
                for f in fr:
                    bpy.context.scene.frame_set(int(round(f)))
                    for d_idx, cdir in enumerate(CAM_DIRS):
                        first = (n_frames == 0 and d_idx == 0)
                        dir_tiles[d_idx].append(shoot(ob, first, tmp, n_frames * 8 + d_idx, cdir, ctr, size))
                    n_frames += 1
            rows = [np.concatenate(dir_tiles[d], axis=1) for d in range(8)]
            strip = np.concatenate(rows[::-1], axis=0)   # bottom-up: row 0 (S) at top of PNG
            n_tiles = n_frames
        else:
            for name, act in plan:
                if name in seen: continue
                seen.add(name)
                k = frames_for(name)
                if act is not None:
                    arm.animation_data.action = act
                    if hasattr(arm.animation_data, "action_slot") and act.slots:
                        arm.animation_data.action_slot = act.slots[0]
                    f0, f1 = act.frame_range
                    if f1 <= f0: k = 1
                    fr = [f0 + (f1 - f0) * i / k for i in range(k)]   # loop: skip the duplicate last frame
                else:
                    fr = [1]; k = 1
                clips[name] = {"start": len(tiles), "frames": len(fr)}
                for f in fr:
                    bpy.context.scene.frame_set(int(round(f)))
                    tiles.append(shoot(ob, not tiles, tmp, len(tiles)))
            strip = np.concatenate(tiles, axis=1)   # rows stay bottom-up, as Blender expects
            n_tiles = len(tiles)
        d = f"{OUT}/{cat}"; os.makedirs(d, exist_ok=True)
        save_gray(strip, f"{d}/{aid}.png")
        result[aid] = {"category": cat, "tiles": n_tiles, "clips": clips}
        print("SPRITE", ref, n_tiles, flush=True)
    tag = os.path.basename(SHARD)
    json.dump(result, open(f"{OUT}/shard-{tag}", "w"))
    if os.path.exists(tmp): os.remove(tmp)
