import zipfile
from pathlib import Path
import build_catalog

ROOT_DIR = Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw")


def extract_all_zips(root: Path):
    zip_files = sorted(root.rglob("*.zip"))
    print(f"Found {len(zip_files)} .zip files.")

    for zp in zip_files:
        target_dir = zp.parent
        try:
            with zipfile.ZipFile(zp, "r") as zf:
                zf.extractall(target_dir)
            print(f"  Extracted: {zp.relative_to(root)}")
        except zipfile.BadZipFile:
            print(f"  Skipped corrupted zip: {zp.relative_to(root)}")
        except Exception as e:
            print(f"  Error extracting {zp.relative_to(root)}: {e}")


if __name__ == "__main__":
    extract_all_zips(ROOT_DIR)
    build_catalog.main()