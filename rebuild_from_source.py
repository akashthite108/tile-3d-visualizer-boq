import hashlib
import json
import os
import re
import shutil
from pathlib import Path

RAW_ROOT = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw")
CATALOG_V1 = RAW_ROOT / "catalog.v1.json"
WEB_DIR = RAW_ROOT / "web_prototype"
WEB_ASSETS_DIR = WEB_DIR / "web_assets"
OUT_CATALOG = WEB_DIR / "full_catalog.json"


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", (text or "").strip().lower()).strip("_")
    return cleaned or "misc"


def prettify_stem(stem: str) -> str:
    spaced = re.sub(r"[_-]+", " ", stem).strip()
    return re.sub(r"\s+", " ", spaced) or stem


def extract_series_from_rel_path(rel_path: str, fallback_series: str) -> str:
    parts = Path(rel_path).parts
    if parts:
        first = slugify(parts[0])
        if first and first not in {"simpolo_raw", "extracted", "assets", "web_assets"}:
            return first
    return slugify(fallback_series)


def path_unique_id(rel_posix: str) -> str:
    digest = hashlib.sha256(rel_posix.encode("utf-8")).hexdigest()[:12]
    return f"sku_{digest}"


def link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def main() -> None:
    if not CATALOG_V1.exists():
        print(f"Missing {CATALOG_V1}")
        return

    raw_data = json.loads(CATALOG_V1.read_text(encoding="utf-8"))
    raw_items = raw_data.get("items", [])

    WEB_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    seen_source_paths: set[str] = set()
    seen_ids: set[str] = set()
    rebuilt_items: list[dict] = []
    skipped_missing = 0
    skipped_duplicate_source = 0

    for idx, item in enumerate(raw_items):
        src_rel = item.get("sourceFile") or item.get("pbr", {}).get("maps", {}).get("albedo") or ""
        if not src_rel:
            skipped_missing += 1
            continue

        norm_rel = Path(src_rel).as_posix().lstrip("./")
        src_abs = RAW_ROOT / Path(norm_rel)
        if not src_abs.exists() or not src_abs.is_file():
            skipped_missing += 1
            continue

        source_key = norm_rel.lower()
        if source_key in seen_source_paths:
            skipped_duplicate_source += 1
            continue
        seen_source_paths.add(source_key)

        series_slug = extract_series_from_rel_path(norm_rel, item.get("series", "misc"))
        unique_id = path_unique_id(f"{source_key}#{idx}")
        while unique_id in seen_ids:
            unique_id = f"{unique_id}_x"
        seen_ids.add(unique_id)

        ext = src_abs.suffix.lower() or ".jpg"
        dest_rel = Path("web_assets") / series_slug / f"{unique_id}{ext}"
        dest_abs = WEB_DIR / dest_rel
        link_or_copy(src_abs, dest_abs)

        clean_name = prettify_stem(src_abs.stem)

        cloned = json.loads(json.dumps(item))
        cloned["id"] = unique_id
        cloned["name"] = clean_name
        cloned["series"] = series_slug
        cloned["sourceFile"] = norm_rel
        cloned.setdefault("finish", "Matt / Gloss")
        cloned.setdefault("lookAndFeel", "General")
        cloned.setdefault("dimensionsMm", {"width": 600, "height": 1200})

        cloned.setdefault("pbr", {})
        cloned["pbr"].setdefault("maps", {})
        cloned["pbr"]["maps"]["albedo"] = dest_rel.as_posix()

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

        rebuilt_items.append(cloned)

    payload = {
        "schemaVersion": "1.4.0",
        "brand": raw_data.get("brand", "Simpolo"),
        "currency": "INR",
        "defaultWastagePercent": raw_data.get("defaultWastagePercent", 10),
        "totalItems": len(rebuilt_items),
        "rebuildStats": {
            "sourceItems": len(raw_items),
            "skippedMissing": skipped_missing,
            "skippedDuplicateSource": skipped_duplicate_source,
        },
        "items": rebuilt_items,
    }

    OUT_CATALOG.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Rebuilt {len(rebuilt_items)} clean SKUs into {OUT_CATALOG}")
    print(f"Skipped missing: {skipped_missing} | Skipped duplicate source paths: {skipped_duplicate_source}")


if __name__ == "__main__":
    main()