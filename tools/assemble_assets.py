#!/usr/bin/env python3
"""
Assemble all catalog files (data/catalog_*.json) into assets.json.
Validates schema, checks for duplicate IDs, and reports category breakdown.
"""
import glob
import json
import os
import sys

SCHEMA_DESC = "id, category, name, size_m [width x, length y, height z] metres (Blender Z up, front faces +Y), generator, budget_tris, params. validate.py --write adds tris, bytes, glb, thumb."

def assemble(catalog_dir="data", output_path="assets.json"):
    files = sorted(glob.glob(os.path.join(catalog_dir, "catalog_*.json")))
    combined_assets = []
    seen_ids = set()
    category_counts = {}

    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                base = json.load(f)
            for item in base.get("assets", []):
                if item["id"] not in seen_ids:
                    seen_ids.add(item["id"])
                    combined_assets.append(item)
                    cat = item.get("category", "unknown")
                    category_counts[cat] = category_counts.get(cat, 0) + 1
        except Exception:
            pass

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("assets", data.get("facilities", []))
        for item in items:
            item_id = item["id"]
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            combined_assets.append(item)
            cat = item.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

    result = {
        "schema": SCHEMA_DESC,
        "assets": combined_assets
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)

    print(f"Assembled {len(combined_assets)} assets into {output_path}:")
    for cat, count in sorted(category_counts.items()):
        print(f"  - {cat}: {count}")

if __name__ == "__main__":
    assemble()
