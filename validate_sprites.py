#!/usr/bin/env python3
"""Check ink sprite sheets: python3 validate_sprites.py. Pure Python, no Blender.
Every asset has sprites/<category>/<id>.png, it matches sprites.json (PNG header size = tile x tile*frames),
and the budgets hold (<=150 KB per sheet, <=90 MB total). Exit 1 on any failure."""
import json, os, struct, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PER, TOTAL = 150_000, 90_000_000

def run():
    errs = []
    assets = json.load(open(f"{ROOT}/assets.json"))["assets"]
    p = f"{ROOT}/sprites.json"
    if not os.path.exists(p):
        return ["sprites.json missing"], 0
    sj = json.load(open(p)); tile = sj["tile"]; sa = sj["assets"]; total = 0
    for r in assets:
        i = r["id"]; e = sa.get(i)
        f = f"{ROOT}/sprites/{r['category']}/{i}.png"
        if e is None: errs.append(f"{i}: not in sprites.json"); continue
        if not os.path.exists(f): errs.append(f"{i}: sheet {f} missing"); continue
        n = os.path.getsize(f); total += n
        if n > PER: errs.append(f"{i}: {n} B > {PER} B")
        with open(f, "rb") as fh: h = fh.read(24)
        if h[:8] != b"\x89PNG\r\n\x1a\n": errs.append(f"{i}: not a PNG"); continue
        w, ht = struct.unpack(">II", h[16:24])
        frames = e.get("tiles", 0)
        if ht != tile: errs.append(f"{i}: height {ht} != tile {tile}")
        if frames and w != tile * frames: errs.append(f"{i}: width {w} != {tile}*{frames}")
        if not frames: errs.append(f"{i}: no frame count in sprites.json")
    if total > TOTAL: errs.append(f"total {total} B > {TOTAL} B")
    return errs, total

if __name__ == "__main__":
    errs, total = run()
    for e in errs[:50]: print("FAIL", e)
    print(f"VALIDATE-SPRITES fail={len(errs)} total_bytes={total}")
    sys.exit(1 if errs else 0)
