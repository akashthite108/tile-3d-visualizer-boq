import json
import os
import shutil
from pathlib import Path

RAW_ROOT = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw")
CATALOG_PATH = RAW_ROOT / "catalog.v1.json"
WEB_DIR = RAW_ROOT / "web_prototype"
WEB_ASSETS_DIR = WEB_DIR / "web_assets"
OUT_JSON = WEB_DIR / "full_catalog.json"


def link_or_copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(src, dst)  # Zero extra disk space on same NTFS drive
    except OSError:
        shutil.copy2(src, dst)


def main():
    if not CATALOG_PATH.exists():
        print(f"Missing {CATALOG_PATH}")
        return

    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    raw_items = data.get("items", [])
    print(f"Loaded {len(raw_items)} items from {CATALOG_PATH.name}...")

    WEB_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    out_items = []
    missing_files = 0

    for idx, item in enumerate(raw_items):
        src_rel = item.get("sourceFile") or item.get("pbr", {}).get("maps", {}).get("albedo")
        if not src_rel:
            missing_files += 1
            continue

        src_file = RAW_ROOT / Path(src_rel)
        if not src_file.exists() or not src_file.is_file():
            missing_files += 1
            continue

        item_id = item.get("id") or f"sku_{idx:05d}"
        ext = src_file.suffix.lower() or ".jpg"
        series_slug = (item.get("series") or "misc").strip().lower().replace(" ", "_")
        rel_asset = Path("web_assets") / series_slug / f"{item_id}{ext}"
        dst_file = WEB_DIR / rel_asset

        link_or_copy(src_file, dst_file)

        cloned = json.loads(json.dumps(item))
        cloned["id"] = item_id
        cloned.setdefault("name", src_file.stem)
        cloned.setdefault("series", series_slug)
        cloned.setdefault("finish", "Matt / Gloss")
        cloned.setdefault("lookAndFeel", "General")
        cloned.setdefault("dimensionsMm", {"width": 600, "height": 1200})

        cloned.setdefault("pbr", {})
        cloned["pbr"].setdefault("maps", {})
        cloned["pbr"]["maps"]["albedo"] = rel_asset.as_posix()

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

        out_items.append(cloned)

    payload = {
        "schemaVersion": "1.2.0",
        "brand": data.get("brand", "Simpolo"),
        "currency": "INR",
        "defaultWastagePercent": data.get("defaultWastagePercent", 10),
        "totalItems": len(out_items),
        "items": out_items,
    }

    OUT_JSON.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT_JSON} with {len(out_items)} usable items ({missing_files} missing/skipped).")
    print(f"Assets prepared in {WEB_ASSETS_DIR}")


if __name__ == "__main__":
    main()