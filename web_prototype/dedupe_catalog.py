import hashlib
import json
from pathlib import Path
from PIL import Image

WEB_DIR = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw\web_prototype")
FULL_JSON = WEB_DIR / "full_catalog.json"
CLEAN_JSON = WEB_DIR / "clean_catalog.json"

ROOM_KEYWORDS = (
    "room",
    "view",
    "render",
    "mockup",
    "ambience",
    "bath",
    "kitchen",
    "living",
    "bedroom",
    "elevation",
)
SWATCH_TAGS = ("r1", "r2", "r3", "f1", "f2", "600", "1200", "800", "1600")


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def is_likely_room_render(item: dict, img_path: Path) -> bool:
    name_lower = (item.get("name") or img_path.stem).lower()
    if any(kw in name_lower for kw in ROOM_KEYWORDS):
        return True

    try:
        with Image.open(img_path) as im:
            w, h = im.size
            if h > 0 and (w / h) > 1.45 and not any(tag in name_lower for tag in SWATCH_TAGS):
                return True
    except Exception:
        return False

    return False


def main() -> None:
    if not FULL_JSON.exists():
        print(f"Missing {FULL_JSON}")
        return

    data = json.loads(FULL_JSON.read_text(encoding="utf-8"))
    items = data.get("items", [])

    seen_hashes: set[str] = set()
    unique_swatches: list[dict] = []
    missing_files = 0
    duplicates_removed = 0
    room_renders_skipped = 0

    for item in items:
        rel = item.get("pbr", {}).get("maps", {}).get("albedo")
        if not rel:
            missing_files += 1
            continue

        img_path = WEB_DIR / Path(rel)
        if not img_path.exists() or not img_path.is_file():
            missing_files += 1
            continue

        digest = file_md5(img_path)
        if digest in seen_hashes:
            duplicates_removed += 1
            continue
        seen_hashes.add(digest)

        if is_likely_room_render(item, img_path):
            room_renders_skipped += 1
            continue

        unique_swatches.append(item)

    clean_payload = {
        "schemaVersion": "1.3.0",
        "brand": data.get("brand", "Simpolo"),
        "currency": "INR",
        "defaultWastagePercent": data.get("defaultWastagePercent", 10),
        "totalItems": len(unique_swatches),
        "removedStats": {
            "duplicates": duplicates_removed,
            "roomRenders": room_renders_skipped,
            "missingFiles": missing_files,
        },
        "items": unique_swatches,
    }

    serialized = json.dumps(clean_payload, separators=(",", ":"))
    CLEAN_JSON.write_text(serialized, encoding="utf-8")
    FULL_JSON.write_text(serialized, encoding="utf-8")

    print(f"Original items:        {len(items)}")
    print(f"Missing files skipped: {missing_files}")
    print(f"Duplicates removed:    {duplicates_removed}")
    print(f"Room renders filtered: {room_renders_skipped}")
    print(f"Clean unique swatches: {len(unique_swatches)} -> saved to {CLEAN_JSON.name} & {FULL_JSON.name}")


if __name__ == "__main__":
    main()