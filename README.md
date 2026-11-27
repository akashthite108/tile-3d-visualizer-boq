# Tile 3D Visualizer & BOQ Studio (`tile-3d-visualizer-boq`)

A web-based **3D Room Visualizer** and **Bill of Quantities (BOQ)** estimator for browsing tile, stone, and marble SKUs, inspecting surface textures up close, and previewing layouts in a 3D room before procurement.

## Features
- **Material-Only Catalog Filtering:** Excludes furniture, carpets, and full-room catalogue renders (such as `basaltino` scene images, kept separate for inspiration) so floors, walls, and BOQ calculations use actual surface materials.
- **Click-to-Zoom Texture Inspector:** Open any material card in an expanded modal with up to `6x` zoom, pan/drag inspection, and full SKU specifications before applying to 3D.
- **Photorealistic 3D Room (Three.js):** Supports room dimensions (`Width`, `Depth`, `Height`), `Floor` / `Feature Wall` / `Side Wall` assignment, surface finish presets (`Satin / Carving`, `High-Gloss Polish`, `Soft Matt`, `Rustic`), laying patterns (`Grid`, `Staggered`), grout thickness/tone, `100mm` skirting, `R1/R2/R3` sibling face cycling, and `180°` face rotation variation.
- **Live INR BOQ Estimator:** Calculates area with wastage, estimated piece count, per-sq.ft pricing, clipboard summary copy, and downloadable `.csv` export.

## Repository Structure
```text
├── .gitignore
├── README.md
├── make_web_app.py
└── web_prototype/
    ├── index.html
    ├── full_catalog.json
    ├── filter_furniture_skus.py
    └── prune_unreferenced_assets.py
