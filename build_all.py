"""Rebuild every asset in assets.json: GLB + PNG thumbnail in assets/<category>/.

blender -b -noaudio --factory-startup --python build_all.py [-- --only ID ... | --category C | --generator G | --allow-skip]
Each asset row names a generator module in generators/; it must define build(asset, z).
"""
import argparse
import importlib
import json
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from lib import zoo  # noqa: E402


def paths(asset):
    base = os.path.join("assets", asset["category"], asset["id"])
    return base + ".glb", base + ".png"


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--category")
    ap.add_argument("--generator")
    ap.add_argument("--no-thumbs", action="store_true")
    ap.add_argument("--allow-skip", action="store_true",
                    help="while generators are being written: rows without a generator don't fail the build")
    a = ap.parse_args(argv)
    with open(os.path.join(ROOT, "assets.json")) as f:
        rows = json.load(f)["assets"]
    todo = [r for r in rows if (not a.only or r["id"] in a.only)
            and (not a.category or r["category"] == a.category)
            and (not a.generator or r["generator"] == a.generator)]
    built, skipped, failed = 0, [], []
    for r in todo:
        try:
            gen = importlib.import_module("generators." + r["generator"])
        except ModuleNotFoundError:
            skipped.append(r["id"])
            continue
        try:
            zoo.reset()
            zoo.begin(r)
            gen.build(dict(r, id=r.get("variant_of", r["id"])), zoo)  # variants reuse the adult's id-keyed builder
            ob = zoo.finish(r)
            glb, png = paths(r)
            zoo.export_glb(ob, os.path.join(ROOT, glb))
            if not a.no_thumbs:
                zoo.render_thumb(ob, os.path.join(ROOT, png))
            built += 1
        except Exception:
            traceback.print_exc()
            failed.append(r["id"])
    print(f"BUILD built={built} skipped(no generator)={len(skipped)} failed={len(failed)} {failed}")
    if skipped:
        print("SKIPPED (no generator):", " ".join(skipped[:20]), "..." if len(skipped) > 20 else "")
    if failed or (skipped and not a.allow_skip):
        sys.exit(1)


main()
