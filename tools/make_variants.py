#!/usr/bin/env python3
"""Add <id>_baby and <id>_rare rows to assets.json for the species in SPECIES (idempotent).

python3 tools/make_variants.py   then rebuild them:
blender -b -noaudio --factory-startup --python build_all.py -- --only $(python3 tools/make_variants.py --ids)
"""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from lib.variants import BABY_SCALE  # noqa: E402

# adult id -> rare recolour (preset in lib/variants.py or a {colour: colour} map) and its label
SPECIES = {
    # quadruped
    "african_elephant": ("albino", "albino"), "brown_bear": ("albino", "albino"), "giant_panda": ({"black": "brown"}, "brown (Qinling)"),
    "grey_wolf": ("melanistic", "melanistic"), "red_panda": ("albino", "albino"), "white_rhino": ("albino", "albino"),
    "hippo": ("albino", "albino"),
    # bigcat
    "lion": ("albino", "white"), "bengal_tiger": ("golden", "golden tabby"), "leopard": ("melanistic", "melanistic"),
    "cheetah": ({"black": "brown"}, "king pattern"), "cougar": ("melanistic", "melanistic"),
    # hoofed
    "giraffe": ("albino", "leucistic"), "plains_zebra": ({"black": "brown"}, "golden"), "dromedary": ("albino", "white"),
    "american_bison": ("albino", "white"), "red_deer": ("albino", "albino"), "reindeer": ("albino", "white"),
    # primate
    "chimpanzee": ("albino", "albino"), "western_gorilla": ("albino", "albino"), "ring_tailed_lemur": ("melanistic", "melanistic"),
    "japanese_macaque": ("albino", "albino"), "bornean_orangutan": ("golden", "golden"),
    # bird
    "african_penguin": ("albino", "albino"), "greater_flamingo": ("albino", "white"), "ostrich": ("albino", "albino"),
    "scarlet_macaw": ("blue", "blue"), "indian_peafowl": ("albino", "white"), "emu": ("albino", "white"),
    # reptile
    "nile_crocodile": ("albino", "albino"), "american_alligator": ("albino", "leucistic"), "green_iguana": ("blue", "blue"),
    "reticulated_python": ("albino", "albino"),
}


def main():
    path = os.path.join(ROOT, "assets.json")
    with open(path) as f:
        data = json.load(f)
    rows = data["assets"]
    by_id = {r["id"]: r for r in rows}
    if "--ids" in sys.argv:
        print(" ".join(f"{s}_{v}" for s in SPECIES for v in ("baby", "rare")))
        return
    added = 0
    for sid, (rc, label) in SPECIES.items():
        adult = by_id[sid]
        for v in ("baby", "rare"):
            vid = f"{sid}_{v}"
            r = {k: copy.deepcopy(adult[k]) for k in ("category", "generator", "budget_tris", "params", "size_m")}
            r = {"id": vid, "category": r["category"],
                 "name": f"{adult['name']} ({'baby' if v == 'baby' else label})",
                 "size_m": r["size_m"], "generator": r["generator"], "budget_tris": r["budget_tris"],
                 "params": r["params"], "variant_of": sid, "variant": v}
            if v == "baby":
                r["size_m"] = [round(x * BABY_SCALE, 3) for x in adult["size_m"]]
            else:
                r["params"]["recolour"] = rc
            if vid in by_id:
                by_id[vid].clear()
                by_id[vid].update(r)
            else:
                rows.insert(rows.index(by_id[sid]) + (1 if v == "baby" else 2), r)
                by_id[vid] = r
                added += 1
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    print(f"variants: {len(SPECIES)} species, {2 * len(SPECIES)} rows ({added} new), assets.json now {len(rows)} rows")


main()
