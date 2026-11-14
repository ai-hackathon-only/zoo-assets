#!/usr/bin/env python3
"""Render ink sprite strips for every asset: python3 build_sprites.py [--jobs N] [--only cat/id ...]
Uses tools/sumi-e/sprite_shard.py in N parallel headless Blender processes, then writes sprites.json."""
import json, os, subprocess, sys, glob, argparse, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--only", nargs="*")
ap.add_argument("--blender", default=os.environ.get("BLENDER", "blender"))
a = ap.parse_args()
assets = json.load(open(f"{ROOT}/assets.json"))
assets = assets["assets"] if isinstance(assets, dict) else assets
refs = [f"{x['category']}/{x['id']}" for x in assets]
if a.only: refs = [r for r in refs if r in a.only]
out = f"{ROOT}/sprites"; os.makedirs(out, exist_ok=True)
tmpd = f"{out}/_shards"; shutil.rmtree(tmpd, ignore_errors=True); os.makedirs(tmpd)
procs = []
for j in range(a.jobs):
    mine = refs[j::a.jobs]
    if not mine: continue
    shard = f"{tmpd}/{j}.json"; open(shard, "w").write("{}")
    log = open(f"{tmpd}/{j}.log", "w")
    procs.append(subprocess.Popen([a.blender, "-b", "-noaudio", "--factory-startup", "--python",
        f"{ROOT}/tools/sumi-e/sprite_shard.py", "--", ROOT, tmpd + f"/out{j}", shard, *mine], stdout=log, stderr=subprocess.STDOUT))
bad = sum(p.wait() != 0 for p in procs)
meta = {}
for f in glob.glob(f"{tmpd}/out*/shard-*.json"):
    meta.update(json.load(open(f)))
for d in glob.glob(f"{tmpd}/out*/*/"):
    cat = os.path.basename(d.rstrip("/")); os.makedirs(f"{out}/{cat}", exist_ok=True)
    for p in glob.glob(d + "*.png"):
        if not os.path.basename(p).startswith("_tmp"): shutil.move(p, f"{out}/{cat}/{os.path.basename(p)}")
old = json.load(open(f"{ROOT}/sprites.json"))["assets"] if os.path.exists(f"{ROOT}/sprites.json") and a.only else {}
old.update(meta)
for k, v in old.items():
    v["bytes"] = os.path.getsize(f"{out}/{v['category']}/{k}.png")
json.dump({"tile": 128, "fps": 8, "assets": dict(sorted(old.items()))}, open(f"{ROOT}/sprites.json", "w"), indent=1)
missing = [r for r in refs if r.split("/")[1] not in old]
print(f"{len(meta)} sheets, {len(missing)} missing, {bad} failed shards, {sum(v['bytes'] for v in old.values())/1e6:.1f} MB")
if not missing and not bad: shutil.rmtree(tmpd)
