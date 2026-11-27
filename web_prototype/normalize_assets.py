import json
from pathlib import Path
from PIL import Image

WEB_DIR = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw\web_prototype")
ASSETS_DIR = WEB_DIR / "assets"
CATALOG_JSON = WEB_DIR / "sample_catalog.json"

BROWSER_NATIVE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
CONVERTIBLE_EXTS = {".tif", ".tiff", ".bmp", ".gif", ".tga"}


def convert_to_jpg(src_path: Path) -> Path:
    dst_path = src_path.with_suffix(".jpg")
    with Image.open(src_path) as img:
        # Handle multi-frame TIFFs by taking frame 0
        if getattr(img, "n_frames", 1) > 1:
            img.seek(0)
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
            rgb_img = bg
        else:
            rgb_img = img.convert("RGB")

        rgb_img.save(dst_path, format="JPEG", quality=90, optimize=True)
    return dst_path


def main():
    if not ASSETS_DIR.exists():
        print(f"Assets folder not found: {ASSETS_DIR}")
        return

    # Map old relative asset paths (posix, e.g. "assets/foo.tif") -> new relative path ("assets/foo.jpg")
    path_remap: dict[str, str] = {}
    converted_count = 0

    for file_path in sorted(ASSETS_DIR.iterdir()):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        old_rel = Path("assets", file_path.name).as_posix()

        needs_conversion = ext in CONVERTIBLE_EXTS or ext not in BROWSER_NATIVE_EXTS
        if not needs_conversion:
            # Verify image integrity with Pillow
            try:
                with Image.open(file_path) as im:
                    im.verify()
                continue
            except Exception:
                needs_conversion = True

        if needs_conversion:
            try:
                new_path = convert_to_jpg(file_path)
                new_rel = Path("assets", new_path.name).as_posix()
                path_remap[old_rel] = new_rel
                converted_count += 1
                print(f"Converted: {old_rel} -> {new_rel}")

                # Remove original non-jpg file if path changed
                if file_path.resolve() != new_path.resolve() and file_path.exists():
                    file_path.unlink()
            except Exception as e:
                print(f"Failed to convert {old_rel}: {e}")

    if CATALOG_JSON.exists() and path_remap:
        data = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        updated_refs = 0

        for item in data.get("items", []):
            maps = item.get("pbr", {}).get("maps", {})
            for key in ("albedo", "normal", "roughness"):
                val = maps.get(key)
                if val in path_remap:
                    maps[key] = path_remap[val]
                    updated_refs += 1
            if item.get("sourceFile") in path_remap:
                item["sourceFile"] = path_remap[item["sourceFile"]]

        CATALOG_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Updated {updated_refs} texture reference(s) in {CATALOG_JSON}.")
    else:
        print(f"Done. Converted {converted_count} file(s); no catalog path updates needed.")


if __name__ == "__main__":
    main()