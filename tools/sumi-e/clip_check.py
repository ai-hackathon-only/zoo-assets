# Render the exported rigged GLBs (walk + eat) in the sumi-e ink style, from the files as a game would load them.
# blender -b -noaudio --factory-startup --python tools/sumi-e/clip_check.py -- <repo> <outdir> animals/lion animals/giraffe ...
import bpy, os, sys, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v2", os.path.join(HERE, "style_v2.py"))
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
args = sys.argv[sys.argv.index("--") + 1:]
REPO, OUT, IDS = args[0], args[1], args[2:]
SHOTS = [("walk", f) for f in (0, 4, 8, 12, 16, 20)] + [("eat", f) for f in (0, 12, 24)] + [("idle", 12)]


def load(aid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{REPO}/assets/{aid if "/" in aid else "animals/" + aid}.glb")
    arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
    shapes = {pb.custom_shape for pb in arm.pose.bones if pb.custom_shape}
    for o in shapes: bpy.data.objects.remove(o)
    mesh = next(o for o in bpy.context.scene.objects if o.type == "MESH")
    ad = arm.animation_data_create()
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    return arm, mesh


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for aid in IDS:
        arm, mesh = load(aid)
        img = next((i for i in bpy.data.images if i.size[0] > 0), None)
        acts = {a.name.split("_")[0]: a for a in bpy.data.actions}
        v2.style(mesh, "ink", img)
        tiles = []
        for k, (clip, f) in enumerate(SHOTS):
            act = next(a for n, a in acts.items() if n.startswith(clip))
            arm.animation_data.action = act
            if hasattr(arm.animation_data, "action_slot") and act.slots:
                arm.animation_data.action_slot = act.slots[0]
            bpy.context.scene.frame_set(f)
            out = f"{OUT}/{aid.split("/")[-1]}_{clip}{f}.png"
            if k == 0:
                v2.render(mesh, "ink", "paper", out)
            else:
                bpy.context.scene.render.filepath = out; bpy.ops.render.render(write_still=True)
            px = v2.load_px(out); bg = v2.paper_bg("ink", *px.shape[:2], seed=k)
            px = np.concatenate([np.clip(px[..., :3] * bg[..., :3] / np.array(v2.PAPER["ink"], np.float32), 0, 1),
                                 np.ones_like(px[..., 3:4])], axis=2)
            tiles.append(px)
        rows.append(np.concatenate(tiles, axis=1))
        print("RENDERED", aid, flush=True)
    v2.save_px(np.concatenate(rows[::-1], axis=0), f"{OUT}/clips.png")
    print("SHEET DONE", flush=True)
