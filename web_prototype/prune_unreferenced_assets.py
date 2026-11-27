import json
from pathlib import Path

RAW_ROOT = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw")
WEB_DIR = RAW_ROOT / "web_prototype"
FULL_JSON = WEB_DIR / "full_catalog.json"
ASSETS_DIR = WEB_DIR / "web_assets"


def main() -> None:
    if not FULL_JSON.exists():
        print(f"Missing {FULL_JSON}")
        return
    if not ASSETS_DIR.exists():
        print(f"Missing {ASSETS_DIR}")
        return

    data = json.loads(FULL_JSON.read_text(encoding="utf-8"))
    items = data.get("items", [])

    referenced_files: set[Path] = set()
    for item in items:
        albedo = item.get("pbr", {}).get("maps", {}).get("albedo", "")
        if not albedo:
            continue
        resolved = (WEB_DIR / Path(albedo)).resolve()
        if resolved.exists() and resolved.is_file():
            referenced_files.add(resolved)

    all_files = [p.resolve() for p in ASSETS_DIR.rglob("*") if p.is_file()]
    removed_files = 0
    freed_bytes = 0

    for file_path in all_files:
        if file_path not in referenced_files:
            try:
                size = file_path.stat().st_size
                file_path.unlink()
                removed_files += 1
                freed_bytes += size
            except OSError as exc:
                print(f"Could not delete {file_path}: {exc}")

    # Remove empty subdirectories inside web_assets (bottom-up)
    removed_dirs = 0
    for dir_path in sorted([d for d in ASSETS_DIR.rglob("*") if d.is_dir()], key=lambda p: len(p.parts), reverse=True):
        try:
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
                removed_dirs += 1
        except OSError:
            pass

    remaining_files = sum(1 for p in ASSETS_DIR.rglob("*") if p.is_file())
    freed_mb = freed_bytes / (1024 * 1024)

    print(f"Referenced SKUs in catalog: {len(items)}")
    print(f"Files before prune:         {len(all_files)}")
    print(f"Deleted unreferenced files: {removed_files} ({freed_mb:.2f} MB freed)")
    print(f"Removed empty folders:      {removed_dirs}")
    print(f"Files remaining in assets:  {remaining_files}")


if __name__ == "__main__":
    main()