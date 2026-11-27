import json
import re
from pathlib import Path

RAW_ROOT = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw")
WEB_DIR = RAW_ROOT / "web_prototype"
FULL_JSON = WEB_DIR / "full_catalog.json"
BACKUP_JSON = WEB_DIR / "full_catalog.unfiltered_backup.json"
EXCLUDED_JSON = WEB_DIR / "excluded_furniture_lifestyle.json"

HARD_JUNK_KEYWORDS = {
    "basaltino",
    "sofa", "chair", "armchair", "couch", "table", "coffee table",
    "side table", "dining", "bed", "wardrobe", "vanity", "basin",
    "faucet", "toilet", "shower", "bathtub", "rug", "carpet",
    "lamp", "chandelier", "mirror", "shelf", "stool", "bench",
    "living", "bedroom", "bathroom", "kitchen", "ambience", "ambiance",
    "mockup", "lifestyle", "render",
}

SOFT_SCENE_KEYWORDS = {
    "room", "lounge", "lobby", "terrace", "balcony", "outdoor",
    "interior", "scene", "view", "setup", "curtain", "drape",
    "plant", "planter", "cushion", "pillow",
}

TILE_STRONG_HINTS = (
    "600x1200", "600x600", "800x1600", "800x800", "1200x1200",
    "1200x2400", "300x600", "300x450", "400x400", "200x1200",
    "r1", "r2", "r3", "f1", "f2", "tile", "slab",
    "vitrified", "porcelain", "ceramic", "gvt", "pgvt",
)


def tokenize_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def matches_furniture_or_scene(item: dict) -> tuple[bool, str]:
    blob = " ".join([
        str(item.get("name") or ""),
        str(item.get("series") or ""),
        str(item.get("sourceFile") or ""),
        str(item.get("lookAndFeel") or ""),
        str(item.get("finish") or ""),
    ])
    norm = f" {tokenize_phrase(blob)} "

    for kw in HARD_JUNK_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", norm):
            return True, f"keyword:{kw}"

    has_tile_tag = any(tag in norm for tag in TILE_STRONG_HINTS)
    if not has_tile_tag:
        for kw in SOFT_SCENE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", norm):
                return True, f"scene_keyword:{kw}"

    return False, ""


def main() -> None:
    if not BACKUP_JSON.exists() and not FULL_JSON.exists():
        print("Missing catalog JSON")
        return

    # Always start from the clean unfiltered backup so re-runs are deterministic
    source_file = BACKUP_JSON if BACKUP_JSON.exists() else FULL_JSON
    data = json.loads(source_file.read_text(encoding="utf-8"))
    items = data.get("items", [])

    if not BACKUP_JSON.exists():
        BACKUP_JSON.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")

    kept_tiles = []
    excluded_items = []
    reason_counts: dict[str, int] = {}

    for item in items:
        is_junk, reason = matches_furniture_or_scene(item)
        if is_junk:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            excluded_items.append({"reason": reason, "item": item})
        else:
            kept_tiles.append(item)

    EXCLUDED_JSON.write_text(
        json.dumps({"count": len(excluded_items), "reasons": reason_counts, "items": excluded_items}, indent=2),
        encoding="utf-8",
    )

    updated = dict(data)
    updated["totalItems"] = len(kept_tiles)
    updated["items"] = kept_tiles
    FULL_JSON.write_text(json.dumps(updated, separators=(",", ":")), encoding="utf-8")

    print(f"Source items:          {len(items)}")
    print(f"Excluded (furniture/sc): {len(excluded_items)}")
    print(f"Remaining tile SKUs:   {len(kept_tiles)}")
    print("Top exclusion reasons:", sorted(reason_counts.items(), key=lambda x: -x[1])[:12])


if __name__ == "__main__":
    main()