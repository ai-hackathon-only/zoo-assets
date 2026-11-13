"""Check every GLB listed in assets.json. Exit code 1 if any check fails.

blender -b -noaudio --factory-startup --python validate.py [-- --only ID ... | --category C] [--write] [--allow-missing]
Runs SKILLS/blender/el4cteo/blender-asset-qa/scripts/qa_check.py (profile game) on each asset, plus:
scale vs size_m, origin at floor centre, transforms applied, tri + file-size budgets, total size <= 120 MB,
palette texture + UVs, <= 2 materials, SM_/MAT_ names, file names match assets.json.
--write stores tris, bytes and paths back into assets.json.
"""
import argparse
import json
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "SKILLS/blender/el4cteo/blender-asset-qa/scripts"))
import qa_check  # noqa: E402

from lib import rig, zoo  # noqa: E402

TOTAL_MAX = 120 * 1024 * 1024
H_TOL, L_TOL, ORIGIN_TOL = 0.20, 0.30, 0.02  # height +-20 %, longest side +-30 %, origin 2 cm


def check(r):
    errs = []
    glb = os.path.join("assets", r["category"], r["id"] + ".glb")
    png = glb[:-4] + ".png"
    path = os.path.join(ROOT, glb)
    if not os.path.exists(path):
        return ["missing " + glb], None
    size = os.path.getsize(path)
    max_tris, max_bytes = zoo.budget(r["category"])
    max_tris = min(max_tris, r.get("budget_tris", max_tris))
    if size > max_bytes:
        errs.append(f"file {size} B > {max_bytes} B")
    if not os.path.exists(os.path.join(ROOT, png)):
        errs.append("missing thumbnail " + png)
    zoo.reset()
    bpy.ops.import_scene.gltf(filepath=path)
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    shapes = {pb.custom_shape for a in arms for pb in a.pose.bones if pb.custom_shape}  # importer's bone display
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH" and o not in shapes]
    for o in shapes:
        bpy.data.objects.remove(o)
    want = zoo.object_name(r)
    if arms:  # rigged asset (round 3): one armature, the standard clips, rigid weights
        if len(arms) != 1:
            errs.append(f"{len(arms)} armatures, want 1")
        clips = sorted(act.name for act in bpy.data.actions)
        missing = [c for c in rig.CLIPS if not any(n.startswith(c) for n in clips)]
        if missing:
            errs.append(f"rig: missing clips {missing} (have {clips})")
        for o in obs:
            loose = sum(1 for v in o.data.vertices if len([g for g in v.groups if g.weight > 0.5]) != 1)
            if loose:
                errs.append(f"rig: {loose} vertices not on exactly one bone")
    names = [o.name for o in obs]
    if names != [want]:
        errs.append(f"objects {names}, want exactly [{want}]")
    if not obs:
        return errs, None
    qa = qa_check.run(objects=names, profile="game")
    errs += ["qa: " + e for e in qa["errors"]]
    tris = sum(m.get("tris", 0) for m in qa["objects"].values())
    if tris > max_tris:
        errs.append(f"tris {tris} > {max_tris}")
    mats = {s.material.name for o in obs for s in o.material_slots if s.material}
    if len(mats) > 2 or any(not m.startswith("MAT_") for m in mats):
        errs.append(f"materials {sorted(mats)} (want <= 2, MAT_ prefix)")
    imgs = {n.image.name for m in bpy.data.materials if m.node_tree for n in m.node_tree.nodes
            if n.type == "TEX_IMAGE" and n.image}
    if not imgs or not all(i.startswith("palette") for i in imgs):
        errs.append(f"textures {sorted(imgs)} (want only the palette)")
    for o in obs:
        if not o.data.uv_layers:
            errs.append(f"{o.name}: no UVs")
        if any(abs(v) > 1e-4 for v in o.location) or any(abs(v) > 1e-4 for v in o.rotation_euler) \
                or any(abs(v - 1) > 1e-4 for v in o.scale):
            errs.append(f"{o.name}: transforms not applied")
    xs, ys, zs = zip(*[(o.matrix_world @ v.co)[:] for o in obs for v in o.data.vertices])
    lo, hi = (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    tol = min(ORIGIN_TOL, 0.1 * max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))  # relative for tiny assets
    if abs(cx) > tol or abs(cy) > tol or abs(lo[2]) > tol:
        errs.append(f"origin not at floor centre (centre {cx:.3f},{cy:.3f}, floor {lo[2]:.3f})")
    sx, sy, sz = r["size_m"]
    h, ln = hi[2] - lo[2], max(hi[0] - lo[0], hi[1] - lo[1])
    if abs(h - sz) > sz * H_TOL:
        errs.append(f"height {h:.2f} m, size_m says {sz} (+-{int(H_TOL * 100)} %)")
    want_l = max(sx, sy)
    if abs(ln - want_l) > want_l * L_TOL:
        errs.append(f"longest side {ln:.2f} m, size_m says {want_l} (+-{int(L_TOL * 100)} %)")
    if r.get("category") == "facilities":
        GRID_M = 2.0
        EDGE_M = 0.5
        TOL_M = 0.001
        dx, dy = hi[0] - lo[0], hi[1] - lo[1]
        if abs(cx) > TOL_M or abs(cy) > TOL_M or abs(lo[2]) > TOL_M:
            errs.append(f"facilities origin not at floor centre within 1 mm (cx={cx:.4f}, cy={cy:.4f}, z0={lo[2]:.4f})")
        for axis_name, dim in [("dx", dx), ("dy", dy)]:
            err_2m = abs(dim - round(dim / GRID_M) * GRID_M)
            err_edge = abs(dim - EDGE_M)
            if (err_2m > TOL_M or round(dim / GRID_M) < 1) and err_edge > TOL_M:
                errs.append(f"facilities modular grid check: {axis_name} {dim:.4f} m not multiple of {GRID_M} m or {EDGE_M} m edge within 1 mm")
        if abs(dx - sx) > TOL_M:
            errs.append(f"facilities dx {dx:.4f} m does not match size_m[0] {sx:.4f} m within 1 mm")
        if abs(dy - sy) > TOL_M:
            errs.append(f"facilities dy {dy:.4f} m does not match size_m[1] {sy:.4f} m within 1 mm")
    return errs, {"tris": tris, "bytes": size, "glb": glb, "thumb": png}


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--category")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--allow-missing", action="store_true", help="skip rows whose GLB is not built yet")
    a = ap.parse_args(argv)
    jpath = os.path.join(ROOT, "assets.json")
    with open(jpath) as f:
        data = json.load(f)
    rows = [r for r in data["assets"] if (not a.only or r["id"] in a.only)
            and (not a.category or r["category"] == a.category)]
    ids = [r["id"] for r in data["assets"]]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    bad, ok, missing, total = {}, 0, 0, 0
    if dupes:
        bad["assets.json"] = [f"duplicate ids {dupes}"]
    for r in rows:
        if a.allow_missing and not os.path.exists(os.path.join(ROOT, "assets", r["category"], r["id"] + ".glb")):
            missing += 1
            continue
        errs, stats = check(r)
        if stats:
            total += stats["bytes"]
            if a.write:
                r.update(stats)
        if errs:
            bad[r["id"]] = errs
        else:
            ok += 1
    if total > TOTAL_MAX:
        bad["total"] = [f"all GLBs {total} B > {TOTAL_MAX} B"]
    for k, v in bad.items():
        for e in v:
            print(f"FAIL {k}: {e}")
    print(f"VALIDATE pass={ok} fail={len(bad)} not_built={missing} total_bytes={total}")
    if a.write:
        with open(jpath, "w") as f:
            json.dump(data, f, indent=1)
            f.write("\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
