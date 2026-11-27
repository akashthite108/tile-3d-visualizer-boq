import json
import re
from pathlib import Path

# Change this path to your working folder (for example: Path(r"D:\3D_Visualizer_Assets\Simpolo_Raw"))
ROOT_DIR = Path(".").resolve()
OUTPUT_JSON = ROOT_DIR / "catalog.v1.json"

SKIP_FOLDERS = {"_master_sheets", "_rejects_room_renders", "web_assets"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

# Default profiles keyed by normalized folder/series name
SERIES_PROFILES = {
    "marmorica": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Marble",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.14, "metalness": 0.0, "clearcoat": 0.65, "clearcoatRoughness": 0.12, "bumpScale": 0.002},
    },
    "impero": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Marble",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 800, "height": 1600, "thickness": 9.0},
        "pbr": {"roughness": 0.12, "metalness": 0.0, "clearcoat": 0.7, "clearcoatRoughness": 0.1, "bumpScale": 0.0015},
    },
    "ottimo": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Marble",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 800, "height": 1600, "thickness": 9.0},
        "pbr": {"roughness": 0.14, "metalness": 0.0, "clearcoat": 0.65, "clearcoatRoughness": 0.12, "bumpScale": 0.002},
    },
    "venitto": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Marble",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.15, "metalness": 0.0, "clearcoat": 0.6, "clearcoatRoughness": 0.14, "bumpScale": 0.002},
    },
    "prozzo_800x1600": {
        "category": "Vitrified Tile",
        "subCategory": "Large Format GVT",
        "lookAndFeel": "Stone",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 800, "height": 1600, "thickness": 9.0},
        "pbr": {"roughness": 0.18, "metalness": 0.0, "clearcoat": 0.5, "clearcoatRoughness": 0.15, "bumpScale": 0.002},
    },
    "cordial_60x120": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Stone",
        "finish": "Satin",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.28, "metalness": 0.0, "clearcoat": 0.35, "clearcoatRoughness": 0.22, "bumpScale": 0.0025},
    },
    "prozzo_nova": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Stone",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.2, "metalness": 0.0, "clearcoat": 0.45, "clearcoatRoughness": 0.16, "bumpScale": 0.002},
    },
    "prozzo_rejoice": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Stone",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.2, "metalness": 0.0, "clearcoat": 0.45, "clearcoatRoughness": 0.16, "bumpScale": 0.002},
    },
    "ricco_2_0": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Stone",
        "finish": "Satin",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.26, "metalness": 0.0, "clearcoat": 0.35, "clearcoatRoughness": 0.2, "bumpScale": 0.0025},
    },
    "competitive_2_0": {
        "category": "Vitrified Tile",
        "subCategory": "Glazed Vitrified Tile (GVT)",
        "lookAndFeel": "Stone",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 600, "thickness": 9.0},
        "pbr": {"roughness": 0.22, "metalness": 0.0, "clearcoat": 0.4, "clearcoatRoughness": 0.18, "bumpScale": 0.002},
    },
    "alchimia": {
        "category": "Vitrified Tile",
        "subCategory": "Matte / Stone Series",
        "lookAndFeel": "Concrete",
        "finish": "Matte",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.65, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.004},
    },
    "pozzolano": {
        "category": "Vitrified Tile",
        "subCategory": "Matte / Concrete Series",
        "lookAndFeel": "Concrete",
        "finish": "Matte",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.68, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.004},
    },
    "basaltino": {
        "category": "Vitrified Tile",
        "subCategory": "Basalt / Stone Series",
        "lookAndFeel": "Stone",
        "finish": "Matte",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.6, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.0045},
    },
    "soul": {
        "category": "Vitrified Tile",
        "subCategory": "Minimalist Stone / Matte",
        "lookAndFeel": "Stone",
        "finish": "Matte",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
        "pbr": {"roughness": 0.58, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.0035},
    },
    "glyphstone": {
        "category": "Elevation & Wall Tile",
        "subCategory": "3D / Textured Relief",
        "lookAndFeel": "Stone",
        "finish": "Textured",
        "allowedSurfaces": ["wall"],
        "dimensionsMm": {"width": 300, "height": 600, "thickness": 10.0},
        "pbr": {"roughness": 0.55, "metalness": 0.0, "clearcoat": 0.05, "clearcoatRoughness": 0.4, "bumpScale": 0.009},
    },
    "impatto": {
        "category": "Elevation & Wall Tile",
        "subCategory": "Structured / Relief",
        "lookAndFeel": "Stone",
        "finish": "Textured",
        "allowedSurfaces": ["wall"],
        "dimensionsMm": {"width": 300, "height": 600, "thickness": 10.0},
        "pbr": {"roughness": 0.55, "metalness": 0.0, "clearcoat": 0.05, "clearcoatRoughness": 0.4, "bumpScale": 0.008},
    },
    "sparko": {
        "category": "Wall & Decor Tile",
        "subCategory": "Decorative / Highlight",
        "lookAndFeel": "Decor",
        "finish": "Glossy",
        "allowedSurfaces": ["wall"],
        "dimensionsMm": {"width": 300, "height": 600, "thickness": 9.0},
        "pbr": {"roughness": 0.2, "metalness": 0.05, "clearcoat": 0.5, "clearcoatRoughness": 0.15, "bumpScale": 0.004},
    },
    "piatto": {
        "category": "Wall & Decor Tile",
        "subCategory": "Designer Wall Tile",
        "lookAndFeel": "Decor",
        "finish": "Satin",
        "allowedSurfaces": ["wall"],
        "dimensionsMm": {"width": 300, "height": 600, "thickness": 9.0},
        "pbr": {"roughness": 0.35, "metalness": 0.0, "clearcoat": 0.25, "clearcoatRoughness": 0.25, "bumpScale": 0.004},
    },
    "spectra": {
        "category": "Wall & Bath Tile",
        "subCategory": "Wall / Backsplash",
        "lookAndFeel": "Decor",
        "finish": "Glossy",
        "allowedSurfaces": ["wall"],
        "dimensionsMm": {"width": 300, "height": 600, "thickness": 8.5},
        "pbr": {"roughness": 0.18, "metalness": 0.0, "clearcoat": 0.55, "clearcoatRoughness": 0.12, "bumpScale": 0.0025},
    },
    "tiny_tiles": {
        "category": "Wall & Bath Tile",
        "subCategory": "Small Format / Mosaic",
        "lookAndFeel": "Decor",
        "finish": "Glossy",
        "allowedSurfaces": ["wall"],
        "dimensionsMm": {"width": 300, "height": 300, "thickness": 8.0},
        "pbr": {"roughness": 0.2, "metalness": 0.0, "clearcoat": 0.5, "clearcoatRoughness": 0.15, "bumpScale": 0.004},
    },
    "rockdeck": {
        "category": "Outdoor & Parking Tile",
        "subCategory": "Heavy Duty / Anti-Skid",
        "lookAndFeel": "Rustic",
        "finish": "Rustic",
        "allowedSurfaces": ["floor"],
        "dimensionsMm": {"width": 300, "height": 300, "thickness": 12.0},
        "pbr": {"roughness": 0.85, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.01},
    },
    "courtyard": {
        "category": "Outdoor & Parking Tile",
        "subCategory": "Outdoor / Deck",
        "lookAndFeel": "Rustic",
        "finish": "Rustic",
        "allowedSurfaces": ["floor"],
        "dimensionsMm": {"width": 400, "height": 400, "thickness": 12.0},
        "pbr": {"roughness": 0.85, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.01},
    },
    "copos": {
        "category": "Outdoor & Parking Tile",
        "subCategory": "Outdoor / Anti-Skid",
        "lookAndFeel": "Rustic",
        "finish": "Rustic",
        "allowedSurfaces": ["floor"],
        "dimensionsMm": {"width": 300, "height": 300, "thickness": 12.0},
        "pbr": {"roughness": 0.82, "metalness": 0.0, "clearcoat": 0.0, "clearcoatRoughness": 0.0, "bumpScale": 0.009},
    },
    "supra": {
        "category": "Vitrified Tile",
        "subCategory": "Vitrified Series",
        "lookAndFeel": "Stone",
        "finish": "Glossy",
        "allowedSurfaces": ["floor", "wall"],
        "dimensionsMm": {"width": 600, "height": 600, "thickness": 9.0},
        "pbr": {"roughness": 0.22, "metalness": 0.0, "clearcoat": 0.45, "clearcoatRoughness": 0.16, "bumpScale": 0.002},
    },
}

DEFAULT_PROFILE = {
    "category": "Vitrified Tile",
    "subCategory": "Standard Series",
    "lookAndFeel": "Stone",
    "finish": "Glossy",
    "allowedSurfaces": ["floor", "wall"],
    "dimensionsMm": {"width": 600, "height": 1200, "thickness": 9.5},
    "pbr": {"roughness": 0.25, "metalness": 0.0, "clearcoat": 0.35, "clearcoatRoughness": 0.2, "bumpScale": 0.0025},
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def normalize_series_folder(folder_name: str) -> str:
    name = folder_name.lower().strip()
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"_202\d$", "", name)  # merge year suffixes like prozzo_nova_2024 -> prozzo_nova
    return name


def main():
    items = []
    pdfs_found = []

    for folder in sorted(ROOT_DIR.iterdir()):
        if not folder.is_dir() or folder.name in SKIP_FOLDERS:
            continue

        norm_series = normalize_series_folder(folder.name)
        profile = SERIES_PROFILES.get(norm_series, DEFAULT_PROFILE)
        w_mm = profile["dimensionsMm"]["width"]
        h_mm = profile["dimensionsMm"]["height"]
        area_sq_ft = (w_mm * h_mm) / 92903.04  # 1 sq. ft. = 92903.04 sq. mm

        for file_path in sorted(folder.rglob("*")):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            if ext == ".pdf":
                pdfs_found.append(str(file_path.relative_to(ROOT_DIR)))
                continue
            if ext not in IMAGE_EXTS:
                continue

            design_slug = slugify(file_path.stem)
            sku_id = f"simpolo-{slugify(norm_series)}-{w_mm}x{h_mm}-{design_slug}"
            rel_path = file_path.relative_to(ROOT_DIR).as_posix()

            items.append({
                "id": sku_id,
                "brand": "Simpolo",
                "series": folder.name,
                "name": file_path.stem.replace("_", " ").replace("-", " ").title(),
                "skuCode": f"SIM-{slugify(norm_series).upper()}-{design_slug[:12].upper()}",
                "category": profile["category"],
                "subCategory": profile["subCategory"],
                "lookAndFeel": profile["lookAndFeel"],
                "finish": profile["finish"],
                "allowedSurfaces": profile["allowedSurfaces"],
                "dimensionsMm": {
                    "width": w_mm,
                    "height": h_mm,
                    "thickness": profile["dimensionsMm"]["thickness"],
                    "approxSqFtPerPiece": round(area_sq_ft, 2),
                },
                "pricing": {
                    "ratePerSqFt": None,
                    "gstPercent": 18,
                    "priceType": "indicative_pending",
                },
                "layoutDefaults": {
                    "pattern": "grid",
                    "rotationDeg": 0,
                    "groutWidthMm": 2.0,
                    "groutHex": "#E6E4DF",
                },
                "pbr": {
                    "baseHex": "#FFFFFF",
                    "roughness": profile["pbr"]["roughness"],
                    "metalness": profile["pbr"]["metalness"],
                    "clearcoat": profile["pbr"]["clearcoat"],
                    "clearcoatRoughness": profile["pbr"]["clearcoatRoughness"],
                    "bumpScale": profile["pbr"]["bumpScale"],
                    "maps": {
                        "albedo": rel_path,
                        "normal": None,
                        "roughness": None,
                    },
                },
                "sourceFile": rel_path,
            })

    catalog = {
        "schemaVersion": "1.0.0",
        "brand": "Simpolo",
        "currency": "INR",
        "defaultWastagePercent": 10,
        "totalItems": len(items),
        "brochurePdfsDetected": pdfs_found,
        "items": items,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"Generated {OUTPUT_JSON} with {len(items)} tile/material entries and {len(pdfs_found)} PDFs noted.")


if __name__ == "__main__":
    main()