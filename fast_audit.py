import json
import re
from collections import Counter
from pathlib import Path

WEB_DIR = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw\web_prototype")
CATALOG_FILE = WEB_DIR / "full_catalog.json"
REPORT_FILE = WEB_DIR / "fast_audit_report.json"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (text or "").strip().lower()).strip("_")


def tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) >= 3}


def main() -> None:
    if not CATALOG_FILE.exists():
        print(f"Missing {CATALOG_FILE}")
        return

    data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    items = data.get("items", [])

    id_counts = Counter(item.get("id") for item in items)
    duplicate_ids = {k: v for k, v in id_counts.items() if v > 1}

    missing_paths = []
    series_folder_mismatches = []
    name_filename_warnings = []
    referenced_assets = set()

    for idx, item in enumerate(items):
        sku_id = item.get("id", f"<no-id-{idx}>")
        name = item.get("name", "")
        series = item.get("series", "")
        albedo = item.get("pbr", {}).get("maps", {}).get("albedo", "")

        if not albedo:
            missing_paths.append({"id": sku_id, "name": name, "albedo": albedo, "reason": "empty albedo"})
            continue

        abs_img = WEB_DIR / Path(albedo)
        if not abs_img.exists() or not abs_img.is_file():
            missing_paths.append({"id": sku_id, "name": name, "albedo": albedo, "reason": "file missing"})
            continue

        referenced_assets.add(abs_img.resolve())

        parts = Path(albedo).parts
        if len(parts) >= 3 and parts[0] == "web_assets":
            folder_series = parts[1].lower()
            expected_series = slugify(series)
            if expected_series and folder_series != expected_series:
                series_folder_mismatches.append({
                    "id": sku_id,
                    "series": series,
                    "folderSeries": folder_series,
                    "albedo": albedo,
                })

        name_toks = tokens(name)
        stem_toks = tokens(abs_img.stem)
        if name_toks and stem_toks and name_toks.isdisjoint(stem_toks):
            name_filename_warnings.append({
                "id": sku_id,
                "name": name,
                "file": abs_img.name,
            })

    assets_root = WEB_DIR / "web_assets"
    all_asset_files = [p.resolve() for p in assets_root.rglob("*") if p.is_file()] if assets_root.exists() else []
    orphan_files = [str(p.relative_to(WEB_DIR)) for p in all_asset_files if p not in referenced_assets]

    report = {
        "totalItemsAudited": len(items),
        "totalFilesInWebAssets": len(all_asset_files),
        "duplicateIdCount": len(duplicate_ids),
        "missingFileCount": len(missing_paths),
        "seriesFolderMismatchCount": len(series_folder_mismatches),
        "nameFilenameWarningCount": len(name_filename_warnings),
        "orphanAssetFileCount": len(orphan_files),
        "samples": {
            "duplicateIds": dict(list(duplicate_ids.items())[:10]),
            "missingPaths": missing_paths[:10],
            "seriesFolderMismatches": series_folder_mismatches[:10],
            "nameFilenameWarnings": name_filename_warnings[:15],
            "orphanFiles": orphan_files[:15],
        },
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    print(f"\nSaved report to {REPORT_FILE}")


if __name__ == "__main__":
    main()