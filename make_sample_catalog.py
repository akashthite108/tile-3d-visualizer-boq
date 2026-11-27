import json
import shutil
from pathlib import Path

RAW_ROOT = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw")
CATALOG_PATH = RAW_ROOT / "catalog.v1.json"
OUT_DIR = RAW_ROOT / "web_prototype"
ASSETS_DIR = OUT_DIR / "assets"
MAX_SAMPLES = 15


def main():
    if not CATALOG_PATH.exists():
        print(f"Missing {CATALOG_PATH}. Run extract_and_build.py first.")
        return

    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not items:
        print("No items found in catalog.v1.json.")
        return

    # Pick 1 item per series first for variety, then fill up to MAX_SAMPLES
    seen_series = set()
    selected = []
    leftovers = []

    for item in items:
        series_key = (item.get("series") or "").lower()
        if series_key not in seen_series and len(selected) < MAX_SAMPLES:
            seen_series.add(series_key)
            selected.append(item)
        else:
            leftovers.append(item)

    for item in leftovers:
        if len(selected) >= MAX_SAMPLES:
            break
        selected.append(item)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    sample_items = []

    for item in selected:
        src_rel = item.get("sourceFile") or (item.get("pbr", {}).get("maps", {}).get("albedo"))
        if not src_rel:
            continue
        src_file = RAW_ROOT / Path(src_rel)
        if not src_file.exists():
            continue

        dest_rel = Path("assets") / f"{item['id']}{src_file.suffix.lower()}"
        dest_file = OUT_DIR / dest_rel
        shutil.copy2(src_file, dest_file)

        cloned = json.loads(json.dumps(item))
        cloned["pbr"]["maps"]["albedo"] = dest_rel.as_posix()

        # Ensure layoutDefaults & indicative INR pricing exist for BOQ calculations
        cloned.setdefault("layoutDefaults", {
            "pattern": "grid",
            "rotationDeg": 0,
            "groutWidthMm": 2.0,
            "groutHex": "#E2DFD9",
        })
        if not cloned.get("pricing") or cloned["pricing"].get("ratePerSqFt") is None:
            is_large = (cloned.get("dimensionsMm", {}).get("width", 600) >= 800)
            cloned["pricing"] = {
                "ratePerSqFt": 145 if is_large else 95,
                "gstPercent": 18,
                "priceType": "indicative",
            }

        sample_items.append(cloned)

    sample_catalog = {
        "schemaVersion": "1.1.0",
        "brand": data.get("brand", "Simpolo"),
        "currency": "INR",
        "defaultWastagePercent": 10,
        "totalItems": len(sample_items),
        "items": sample_items,
    }

    out_json = OUT_DIR / "sample_catalog.json"
    out_json.write_text(json.dumps(sample_catalog, indent=2), encoding="utf-8")
    print(f"Updated {out_json} with {len(sample_items)} SKUs.")


if __name__ == "__main__":
    main()