#!/usr/bin/env python3
"""Check ink sprite sheets: python3 validate_sprites.py. Pure Python, no Blender.
Every asset has sprites/<category>/<id>.png, it matches sprites.json (PNG header size = tile x tile*frames),
and the budgets hold (<=150 KB per sheet, <=90 MB total). Exit 1 on any failure."""
import json, os, struct, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PER, TOTAL = 150_000, 90_000_000
PER_8DIR, TOTAL_8DIR = 350_000, 60_000_000
CATS_8DIR = ("animals", "keepers", "visitors")

def _check_set(assets, json_path, img_dir, per_lim, total_lim, rows=1):
    errs = []
    if not os.path.exists(json_path):
        return [f"{os.path.basename(json_path)} missing"], 0
    sj = json.load(open(json_path)); tile = sj["tile"]; sa = sj["assets"]; total = 0
    for r in assets:
        i = r["id"]; e = sa.get(i)
        f = f"{img_dir}/{r['category']}/{i}.png"
        if e is None: errs.append(f"{i}: not in {os.path.basename(json_path)}"); continue
        if not os.path.exists(f): errs.append(f"{i}: sheet {f} missing"); continue
        n = os.path.getsize(f); total += n
        if n > per_lim: errs.append(f"{i}: {n} B > {per_lim} B")
        with open(f, "rb") as fh: h = fh.read(24)
        if h[:8] != b"\x89PNG\r\n\x1a\n": errs.append(f"{i}: not a PNG"); continue
        w, ht = struct.unpack(">II", h[16:24])
        frames = e.get("tiles", 0)
        if ht != tile * rows: errs.append(f"{i}: height {ht} != {tile}*{rows}")
        if frames and w != tile * frames: errs.append(f"{i}: width {w} != {tile}*{frames}")
        if not frames: errs.append(f"{i}: no frame count in {os.path.basename(json_path)}")
    if total > total_lim: errs.append(f"total {total} B > {total_lim} B")
    return errs, total

def run():
    assets = json.load(open(f"{ROOT}/assets.json"))["assets"]
    errs, total = _check_set(assets, f"{ROOT}/sprites.json", f"{ROOT}/sprites", PER, TOTAL, rows=1)
    if os.path.exists(f"{ROOT}/sprites_8dir.json"):
        sub = [r for r in assets if r["category"] in CATS_8DIR]
        e8, _ = _check_set(sub, f"{ROOT}/sprites_8dir.json", f"{ROOT}/sprites_8dir", PER_8DIR, TOTAL_8DIR, rows=8)
        errs.extend(f"[8dir] {x}" for x in e8)
    return errs, total

if __name__ == "__main__":
    errs, total = run()
    for e in errs[:50]: print("FAIL", e)
    print(f"VALIDATE-SPRITES fail={len(errs)} total_bytes={total}")
    sys.exit(1 if errs else 0)
