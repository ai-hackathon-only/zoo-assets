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
    seen_ids = {}  # id -> source
    duplicates = []
    category_counts = {}

    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                base = json.load(f)
            base_items = base if isinstance(base, list) else base.get("assets", [])
            for item in base_items:
                item_id = item.get("id")
                if not item_id:
                    print(f"Error: Item missing 'id' in {output_path}: {item}", file=sys.stderr)
                    sys.exit(1)
                if item_id in seen_ids:
                    duplicates.append((item_id, output_path, seen_ids[item_id]))
                seen_ids[item_id] = output_path
                combined_assets.append(item)
                cat = item.get("category", "unknown")
                category_counts[cat] = category_counts.get(cat, 0) + 1
        except Exception as e:
            print(f"Error reading existing {output_path}: {e}", file=sys.stderr)
            sys.exit(1)

    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {fpath}: {e}", file=sys.stderr)
            sys.exit(1)

        items = data if isinstance(data, list) else data.get("assets", data.get("facilities", []))
        for item in items:
            item_id = item.get("id")
            if not item_id:
                print(f"Error: Item missing 'id' in {fpath}: {item}", file=sys.stderr)
                sys.exit(1)
            if item_id in seen_ids:
                duplicates.append((item_id, fpath, seen_ids[item_id]))
            seen_ids[item_id] = fpath
            combined_assets.append(item)
            cat = item.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

    if duplicates:
        print(f"Error: Found {len(duplicates)} duplicate ID(s) across catalog files:", file=sys.stderr)
        for dup_id, source1, source2 in duplicates:
            print(f"  - '{dup_id}' in '{source1}' conflicts with '{source2}'", file=sys.stderr)
        sys.exit(1)

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
