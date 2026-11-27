\# Tile 3D Visualizer \& BOQ Studio (`tile-3d-visualizer-boq`)



A zero-build, browser-based \*\*3D Room Visualizer\*\* and \*\*Bill of Quantities (BOQ)\*\* estimator for browsing tile, stone, and marble SKUs, inspecting surface textures up close, and previewing layouts in a 3D room before procurement.



\## Features

\- \*\*Material-Only Catalog Filtering:\*\* Search by SKU name, series, dimensions, and look-and-feel across `full\_catalog.json`.

\- \*\*Click-to-Zoom Texture Inspector:\*\* Open any material card in an expanded modal with up to `6x` scroll/slider zoom, drag-to-pan inspection, and full SKU specs before applying to 3D.

\- \*\*GPU-Accelerated 3D Room (Three.js):\*\* Custom WebGL2 `DataArrayTexture` shader supporting room dimensions (`Width`, `Depth`, `Height`), `Floor` / `Feature Wall` / `Side Wall` assignment, surface finish presets (`Satin / Carving`, `High-Gloss Polish`, `Soft Matt`, `Rustic`), laying patterns (`Grid`, `Staggered`), live grout thickness and tone, sibling face cycling (`R1/R2/R3`), and stretch-free tile rotation (`0°/180°` for rectangular slabs, `0°/90°/180°/270°` for square tiles).

\- \*\*Live INR BOQ Estimator (`boq.mjs`):\*\* Groups shared SKUs before box rounding, calculates net/gross area with wastage (+5% extra on staggered layouts), `100mm` skirting strip cuts with 3 mm saw kerf, adhesive bags (`20 kg`), grout weight (`kg`), clipboard summary copy, and Excel-safe `.csv` export.



\## Repository Structure

```text

├── .gitignore

├── README.md

├── make\_web\_app.py

└── web\_prototype/

&#x20;   ├── index.html

&#x20;   ├── boq.mjs

&#x20;   ├── full\_catalog.json

&#x20;   ├── filter\_furniture\_skus.py

&#x20;   ├── prune\_unreferenced\_assets.py

&#x20;   └── web\_assets/               # Local texture assets (gitignored)

