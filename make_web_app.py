import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUT_HTML = BASE_DIR / "web_prototype" / "index.html"
OUT_HTML.parent.mkdir(parents=True, exist_ok=True)

BOQ_CANDIDATES = [
    OUT_HTML.parent / "boq.mjs",
    BASE_DIR / "boq.mjs",
]
BOQ_DST = OUT_HTML.parent / "boq.mjs"

for cand in BOQ_CANDIDATES:
    if cand.exists() and cand.resolve() != BOQ_DST.resolve():
        try:
            if BOQ_DST.exists():
                BOQ_DST.unlink()
            os.link(cand, BOQ_DST)
        except OSError:
            shutil.copy2(cand, BOQ_DST)
        break

if not BOQ_DST.exists():
    print(f"WARNING: {BOQ_DST} not found. Place boq.mjs in web_prototype/ before running the server.")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Simpolo — Full Catalog &amp; 3D Space Visualizer</title>
  <style>
    :root {
      --bg: #f6f5f2;
      --surface: #ffffff;
      --ink: #18181b;
      --muted: #52525b;
      --line: #e4e2dc;
      --accent: #9a5b13;
      --accent-dark: #78440b;
      --warn: #b45309;
      --dark-panel: #18191c;
    }
    * { box-sizing: border-box; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
    html { scroll-behavior: smooth; }
    body { margin: 0; background: var(--bg); color: var(--ink); }

    header {
      position: sticky; top: 0; z-index: 40;
      background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--line);
    }
    .nav-wrap {
      max-width: 1280px; margin: 0 auto; padding: 12px 20px;
      display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
    }
    .brand { display: flex; align-items: baseline; gap: 10px; text-decoration: none; color: var(--ink); }
    .brand-name { font-size: 22px; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; }
    .brand-sub { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); font-weight: 600; }
    nav { display: flex; gap: 18px; flex-wrap: wrap; }
    nav a {
      text-decoration: none; color: var(--ink); font-size: 13px; font-weight: 500;
      padding: 6px 2px; border-bottom: 2px solid transparent;
    }
    nav a:hover { color: var(--accent); border-bottom-color: var(--accent); }
    .cta-btn {
      background: var(--accent); color: #fff; border: none; border-radius: 6px;
      padding: 8px 14px; font-size: 12.5px; font-weight: 600; cursor: pointer; text-decoration: none;
    }
    .cta-btn:hover { background: var(--accent-dark); }

    .hero {
      position: relative; background: #1c1d21; color: #fff; overflow: hidden;
      min-height: 320px; display: flex; align-items: center;
    }
    .hero-bg {
      position: absolute; inset: 0; background-size: cover; background-position: center;
      opacity: 0.32; transition: background-image 0.3s ease;
    }
    .hero-inner {
      position: relative; z-index: 2; max-width: 1280px; width: 100%;
      margin: 0 auto; padding: 40px 20px;
    }
    .eyebrow { font-size: 11.5px; letter-spacing: 0.14em; text-transform: uppercase; color: #f59e0b; font-weight: 700; }
    .hero h1 { font-size: clamp(26px, 3.8vw, 40px); line-height: 1.15; margin: 8px 0 10px; max-width: 720px; }
    .hero p { color: #e4e4e7; max-width: 620px; margin: 0 0 16px; font-size: 14px; line-height: 1.55; }
    .hero-pills { display: flex; gap: 8px; flex-wrap: wrap; }
    .pill-btn {
      background: rgba(255,255,255,0.12); color: #fff; border: 1px solid rgba(255,255,255,0.25);
      border-radius: 999px; padding: 6px 12px; font-size: 12px; cursor: pointer;
    }
    .pill-btn.active, .pill-btn:hover { background: var(--accent); border-color: var(--accent); }

    .section { max-width: 1280px; margin: 0 auto; padding: 36px 20px; }
    .sec-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
    .sec-head h2 { margin: 0; font-size: 22px; font-weight: 700; }
    .sec-head span { font-size: 13px; color: var(--muted); }

    .toolbar {
      display: grid; grid-template-columns: 1fr 220px 220px; gap: 10px; margin-bottom: 14px;
    }
    @media (max-width: 780px) { .toolbar { grid-template-columns: 1fr; } }
    .toolbar input, .toolbar select {
      padding: 8px 10px; border-radius: 6px; border: 1px solid #d4d4d8;
      background: var(--surface); color: var(--ink); font-size: 13px; width: 100%;
    }

    .filter-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
    .tab-btn {
      background: var(--surface); color: var(--ink); border: 1px solid var(--line);
      border-radius: 999px; padding: 6px 13px; font-size: 12px; font-weight: 500; cursor: pointer;
    }
    .tab-btn.active { background: var(--ink); color: #fff; border-color: var(--ink); }

    .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
    .card {
      background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
      overflow: hidden; display: flex; flex-direction: column; transition: transform 0.14s ease, box-shadow 0.14s ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
    .card-thumb-wrap { position: relative; cursor: zoom-in; overflow: hidden; background: #e7e5e4; }
    .card-thumb { width: 100%; height: 140px; object-fit: cover; display: block; transition: transform 0.2s ease; }
    .card-thumb-wrap:hover .card-thumb { transform: scale(1.04); }
    .zoom-badge {
      position: absolute; bottom: 6px; right: 6px;
      background: rgba(24, 24, 27, 0.78); color: #fff;
      font-size: 10.5px; padding: 3px 7px; border-radius: 4px; pointer-events: none;
    }
    .card-body { padding: 11px 13px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .card-series { font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); font-weight: 700; }
    .card-title { font-size: 13.5px; font-weight: 700; margin: 3px 0; word-break: break-word; }
    .card-meta { font-size: 11.5px; color: var(--muted); margin-bottom: 9px; }
    .card-actions { display: grid; grid-template-columns: 1fr auto; gap: 6px; }
    .card-btn {
      width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid var(--ink);
      background: transparent; color: var(--ink); font-size: 12px; font-weight: 600; cursor: pointer;
    }
    .card-btn:hover { background: var(--ink); color: #fff; }
    .inspect-btn {
      padding: 7px 9px; border-radius: 6px; border: 1px solid var(--line);
      background: var(--bg); color: var(--ink); font-size: 12px; font-weight: 600; cursor: pointer;
    }
    .inspect-btn:hover { border-color: var(--accent); color: var(--accent); }

    .load-more-wrap { display: flex; justify-content: center; margin-top: 20px; }
    .load-more-btn {
      padding: 9px 22px; border-radius: 8px; border: 1px solid var(--ink);
      background: var(--surface); color: var(--ink); font-weight: 600; font-size: 13px; cursor: pointer;
    }
    .load-more-btn:hover { background: var(--ink); color: #fff; }

    .studio-band { background: #efede8; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .studio-grid { display: grid; grid-template-columns: 355px 1fr; gap: 20px; align-items: start; }
    @media (max-width: 920px) { .studio-grid { grid-template-columns: 1fr; } }

    .controls-card { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px; }
    .controls-card h3 { margin: 14px 0 6px; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); border-top: 1px solid var(--line); padding-top: 10px; }
    .controls-card h3:first-child { margin-top: 0; border-top: none; padding-top: 0; }
    label { display: block; font-size: 12px; color: var(--ink); font-weight: 500; margin-top: 7px; margin-bottom: 3px; }
    select, input[type="number"], input[type="range"] { width: 100%; }
    select, input[type="number"] {
      padding: 6px 8px; border-radius: 6px; border: 1px solid #d4d4d8;
      background: #fff; color: var(--ink); font-size: 12.5px;
    }
    input[type="color"] { width: 100%; height: 30px; border: 1px solid #d4d4d8; border-radius: 6px; padding: 2px; background: #fff; }
    .g-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .g-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
    .check-row { display: flex; align-items: center; justify-content: space-between; font-size: 12px; margin-top: 8px; }
    .check-row input { width: auto; }
    .face-note { font-size: 11px; color: var(--muted); margin-top: 6px; line-height: 1.4; }

    .viewer-wrap {
      background: var(--dark-panel); border-radius: 10px; overflow: hidden;
      border: 1px solid #27272a; min-height: 540px; position: relative;
    }
    #canvasHost { width: 100%; height: 540px; }
    .viewer-hint {
      position: absolute; bottom: 12px; left: 12px;
      background: rgba(15, 23, 42, 0.78); color: #e2e8f0;
      font-size: 11.5px; padding: 6px 10px; border-radius: 6px; pointer-events: none;
    }

    .boq-panel { margin-top: 10px; background: #faf9f6; border: 1px solid var(--line); border-radius: 8px; padding: 10px; font-size: 12px; }
    .boq-row { display: flex; justify-content: space-between; gap: 8px; line-height: 1.5; }
    .boq-line { padding-bottom: 6px; margin-bottom: 6px; border-bottom: 1px dashed var(--line); }
    .boq-flag { color: var(--warn); font-size: 11px; font-weight: 600; margin-top: 2px; }
    .boq-consumables { color: var(--muted); font-size: 11px; margin-top: 6px; line-height: 1.45; }
    .boq-total { margin-top: 6px; padding-top: 6px; border-top: 1px solid #d4d4d8; font-weight: 700; color: var(--accent-dark); }
    .boq-incomplete { color: var(--warn); font-size: 11px; font-weight: 600; margin-top: 4px; }
    .boq-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }
    .copy-btn {
      width: 100%; padding: 8px; border-radius: 6px; border: none;
      background: var(--accent); color: #fff; font-weight: 600; font-size: 12.5px; cursor: pointer;
    }
    .copy-btn:hover { background: var(--accent-dark); }
    .csv-btn {
      width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--ink);
      background: #fff; color: var(--ink); font-weight: 600; font-size: 12.5px; cursor: pointer;
    }
    .csv-btn:hover { background: var(--ink); color: #fff; }

    /* Texture Inspector Modal */
    .modal-backdrop {
      position: fixed; inset: 0; z-index: 100;
      background: rgba(15, 23, 42, 0.78); backdrop-filter: blur(4px);
      display: none; align-items: center; justify-content: center; padding: 20px;
    }
    .modal-backdrop.open { display: flex; }
    .modal-box {
      background: var(--surface); border-radius: 12px; max-width: 920px; width: 100%;
      overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,0.45);
      display: grid; grid-template-columns: 1.35fr 1fr;
    }
    @media (max-width: 780px) { .modal-box { grid-template-columns: 1fr; } }
    .modal-stage {
      position: relative; background: #18191c; height: 460px; overflow: hidden;
      cursor: grab; display: flex; align-items: center; justify-content: center; user-select: none;
    }
    .modal-stage:active { cursor: grabbing; }
    .modal-stage img {
      max-width: 100%; max-height: 100%; object-fit: contain;
      transform-origin: center center; pointer-events: none;
    }
    .modal-stage-hint {
      position: absolute; bottom: 10px; left: 10px;
      background: rgba(15, 23, 42, 0.78); color: #e2e8f0;
      font-size: 11px; padding: 5px 8px; border-radius: 6px; pointer-events: none;
    }
    .modal-info {
      padding: 20px; display: flex; flex-direction: column; justify-content: space-between; gap: 14px;
    }
    .modal-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
    .modal-close {
      background: var(--bg); border: 1px solid var(--line); border-radius: 6px;
      width: 30px; height: 30px; font-size: 16px; cursor: pointer; color: var(--ink);
    }
    .modal-close:hover { background: var(--ink); color: #fff; }
    .modal-specs { font-size: 12.5px; color: var(--muted); line-height: 1.7; margin-top: 8px; }
    .modal-specs strong { color: var(--ink); }
    .zoom-ctrl { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line); }
    .zoom-ctrl-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 6px; }

    footer { background: #18181b; color: #d4d4d8; padding: 28px 20px; }
    .foot-wrap { max-width: 1280px; margin: 0 auto; display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; font-size: 12.5px; }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <header>
    <div class="nav-wrap">
      <a class="brand" href="#">
        <span class="brand-name">Simpolo</span>
        <span class="brand-sub">Full Catalog &amp; 3D Studio</span>
      </a>
      <nav>
        <a href="#collections">Catalog</a>
        <a href="#visualizer">3D Visualizer</a>
        <a href="#boq">BOQ Estimator</a>
      </nav>
      <a class="cta-btn" href="#visualizer">Open 3D Room</a>
    </div>
  </header>

  <section class="hero">
    <div class="hero-bg" id="heroBg"></div>
    <div class="hero-inner">
      <div class="eyebrow">Simpolo Surface Library</div>
      <h1 id="heroTitle">Explore Every Series in 3D</h1>
      <p id="heroDesc">Search and filter across your full Simpolo catalog in web_assets, inspect textures up to 6x zoom, test staggered or grid layouts with custom grout lines, and generate a piece-count BOQ.</p>
      <div class="hero-pills" id="heroSeriesPills"></div>
    </div>
  </section>

  <section class="section" id="collections">
    <div class="sec-head">
      <h2>Simpolo Catalog</h2>
      <span id="catalogCount">Loading full_catalog.json...</span>
    </div>

    <div class="toolbar">
      <input id="searchInput" type="search" placeholder="Search SKU name, series, size (e.g. 600x1200)..." />
      <select id="seriesFilter"><option value="All">All Series</option></select>
      <select id="sizeFilter"><option value="All">All Sizes</option></select>
    </div>

    <div class="filter-bar" id="lookTabs"></div>
    <div class="cards" id="skuCards"></div>
    <div class="load-more-wrap">
      <button class="load-more-btn" id="loadMoreBtn" style="display:none;">Load More SKUs</button>
    </div>
  </section>

  <div class="studio-band" id="visualizer">
    <section class="section">
      <div class="sec-head">
        <h2>3D Room Visualizer &amp; BOQ</h2>
        <span>Apply any catalog SKU to Floor, Feature Wall, or Side Wall</span>
      </div>

      <div class="studio-grid">
        <div class="controls-card">
          <h3>Room Dimensions (m)</h3>
          <div class="g-3">
            <div><label for="roomW">Width</label><input id="roomW" type="number" min="2" max="20" step="0.1" value="5.0" /></div>
            <div><label for="roomD">Depth</label><input id="roomD" type="number" min="2" max="20" step="0.1" value="4.0" /></div>
            <div><label for="roomH">Height</label><input id="roomH" type="number" min="2.2" max="6" step="0.1" value="3.0" /></div>
          </div>

          <h3>Surface &amp; SKU</h3>
          <label for="surfaceSelect">Target Surface</label>
          <select id="surfaceSelect">
            <option value="floor">Floor</option>
            <option value="backWall">Feature Wall (Back)</option>
            <option value="sideWall">Side Wall (Left)</option>
          </select>

          <label for="skuSelect">Active Surface SKU</label>
          <select id="skuSelect"></select>

          <label for="finishPreset">Surface Finish Preset</label>
          <select id="finishPreset">
            <option value="catalog">Catalog Default</option>
            <option value="satin">Satin / Carving</option>
            <option value="gloss">High-Gloss Polish</option>
            <option value="matt">Soft Matt</option>
            <option value="rustic">Rustic / Textured</option>
          </select>
          <div class="face-note" id="faceInfo">Shader faces: detecting...</div>

          <h3>Shader Pattern, Grout &amp; Openings</h3>
          <div class="g-2">
            <div>
              <label for="patternSelect">Layout</label>
              <select id="patternSelect">
                <option value="grid">Straight Grid</option>
                <option value="staggered">Staggered (50%)</option>
              </select>
            </div>
            <div>
              <label for="groutMm">Grout (mm)</label>
              <input id="groutMm" type="number" min="0" max="15" step="0.5" value="2.0" />
            </div>
          </div>

          <div class="g-2">
            <div><label for="groutColor">Grout Tone</label><input id="groutColor" type="color" value="#e2dfd9" /></div>
            <div><label for="wastagePct">Wastage (%)</label><input id="wastagePct" type="number" min="0" max="30" step="1" value="10" /></div>
          </div>

          <div class="g-2">
            <div><label for="openBack">Back Wall Openings (m&sup2;)</label><input id="openBack" type="number" min="0" max="50" step="0.1" value="0" /></div>
            <div><label for="openSide">Side Wall Openings (m&sup2;)</label><input id="openSide" type="number" min="0" max="50" step="0.1" value="0" /></div>
          </div>

          <label class="check-row" for="toggleCycleFaces">
            <span>Shader Sibling Face Cycling</span>
            <input id="toggleCycleFaces" type="checkbox" checked />
          </label>

          <label class="check-row" for="toggleTileRotate">
            <span>Per-Tile Rotation Variation</span>
            <input id="toggleTileRotate" type="checkbox" checked />
          </label>

          <label class="check-row" for="toggleSkirting">
            <span>100mm Floor Skirting</span>
            <input id="toggleSkirting" type="checkbox" checked />
          </label>

          <label for="skirtingMode">Skirting Perimeter Basis</label>
          <select id="skirtingMode">
            <option value="4wall">Full 4-Wall Room (2 &times; (W + D))</option>
            <option value="2wall">2 Rendered Walls Only (W + D)</option>
          </select>

          <label for="reliefSlider">Surface Relief: <span id="reliefVal">1.00</span></label>
          <input id="reliefSlider" type="range" min="0" max="2.5" step="0.05" value="1.0" />

          <label for="lightSlider">Daylight Intensity: <span id="lightVal">1.35</span></label>
          <input id="lightSlider" type="range" min="0.4" max="2.5" step="0.05" value="1.35" />

          <h3 id="boq">BOQ Estimate (INR)</h3>
          <div class="boq-panel" id="boqSummary">Loading BOQ...</div>
          <div class="boq-actions">
            <button class="copy-btn" id="exportBoqBtn">Copy Summary</button>
            <button class="csv-btn" id="exportCsvBtn">Export CSV</button>
          </div>
        </div>

        <div class="viewer-wrap">
          <div id="canvasHost"></div>
          <div class="viewer-hint">GPU Shader Tile Material &bull; Left-drag: Orbit &bull; Right-drag: Pan &bull; Scroll: Zoom</div>
        </div>
      </div>
    </section>
  </div>

  <!-- Click-to-Zoom Texture Inspector Modal -->
  <div class="modal-backdrop" id="inspectorModal" aria-hidden="true">
    <div class="modal-box">
      <div class="modal-stage" id="modalStage">
        <img id="modalImg" src="" alt="Texture preview" />
        <div class="modal-stage-hint">Scroll or slide to zoom (up to 6x) &bull; Drag to pan</div>
      </div>
      <div class="modal-info">
        <div>
          <div class="modal-head">
            <div>
              <div class="card-series" id="modalSeries"></div>
              <h3 style="margin:4px 0 0; font-size:18px;" id="modalTitle"></h3>
            </div>
            <button class="modal-close" id="modalCloseBtn" title="Close">&times;</button>
          </div>
          <div class="modal-specs" id="modalSpecs"></div>
          <div class="zoom-ctrl">
            <div class="zoom-ctrl-row">
              <span>Zoom: <strong id="modalZoomLabel">1.0x</strong></span>
              <button class="inspect-btn" id="modalResetZoom">Reset</button>
            </div>
            <input id="modalZoomSlider" type="range" min="1" max="6" step="0.1" value="1" />
          </div>
        </div>
        <button class="copy-btn" id="modalApplyBtn">Apply to Active 3D Surface</button>
      </div>
    </div>
  </div>

  <footer>
    <div class="foot-wrap">
      <div><strong>SIMPOLO</strong> &mdash; Full Catalog 3D Visualizer</div>
      <div>Serving local textures from <code>web_assets/</code></div>
    </div>
  </footer>

  <script type="module">
    import * as THREE from "three";
    import { OrbitControls } from "three/addons/controls/OrbitControls.js";
    import { computeBOQ, flagText, boqToCsv, readTileSpec } from "./boq.mjs";

    const PAGE_SIZE = 48;
    const FACE_TEX_SIZE = 512;

    const FINISH_PRESETS = {
      satin: { roughness: 0.34, metalness: 0.02, clearcoat: 0.22, clearcoatRoughness: 0.28 },
      gloss: { roughness: 0.08, metalness: 0.03, clearcoat: 0.85, clearcoatRoughness: 0.06 },
      matt: { roughness: 0.65, metalness: 0.01, clearcoat: 0.05, clearcoatRoughness: 0.55 },
      rustic: { roughness: 0.82, metalness: 0.01, clearcoat: 0.0, clearcoatRoughness: 0.70 },
    };

    let catalogItems = [];
    let filteredItems = [];
    let visibleCount = PAGE_SIZE;
    let activeLook = "All";

    const siblingIndex = new Map();
    const arrayTexCache = new Map();
    const imagePromiseCache = new Map();

    function escHtml(v) {
      return String(v ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function numInput(id, fallback, min = -Infinity, max = Infinity, writeBack = false) {
      const el = document.getElementById(id);
      const raw = parseFloat(el?.value);
      const val = Math.min(max, Math.max(min, Number.isFinite(raw) ? raw : fallback));
      if (writeBack && el) el.value = String(val);
      return val;
    }

    function normalizeDesignKey(item) {
      const raw = String(item.name || "").toLowerCase().replace(/_/g, " ");
      const stripped = raw
        .replace(/\b(r[1-9]|f[1-9]|face[\s-]*[1-9]|closeup[\s-]*[0-9]+)\b/gi, " ")
        .replace(/[^a-z0-9]+/g, " ")
        .trim();
      const spec = readTileSpec(item);
      const dim = `${spec.widthMm || 600}x${spec.heightMm || 1200}`;
      return `${item.series || ""}|${dim}|${stripped}`;
    }

    function rebuildSiblingIndex(items) {
      siblingIndex.clear();
      const grouped = new Map();
      for (const it of items) {
        if (!it.pbr?.maps?.albedo) continue;
        const key = normalizeDesignKey(it);
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(it);
      }
      for (const [key, list] of grouped.entries()) {
        const seen = new Set();
        const unique = [];
        for (const m of list) {
          const src = m.pbr.maps.albedo;
          if (!seen.has(src)) {
            seen.add(src);
            unique.push(m);
          }
        }
        unique.sort((a, b) => String(a.name || "").localeCompare(String(b.name || "")));
        siblingIndex.set(key, unique);
      }
    }

    function getSiblingFaces(sku) {
      if (!sku) return [];
      const key = normalizeDesignKey(sku);
      const matches = siblingIndex.get(key);
      return matches && matches.length ? matches : [sku];
    }

    function loadHtmlImage(src) {
      if (imagePromiseCache.has(src)) return imagePromiseCache.get(src);
      const p = new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => resolve(img);
        img.onerror = () => resolve(null);
        img.src = src;
      });
      imagePromiseCache.set(src, p);
      return p;
    }

    async function getSiblingArrayTexture(sku) {
      const faces = getSiblingFaces(sku);
      const srcs = faces.map((f) => f.pbr?.maps?.albedo).filter(Boolean);
      const cacheKey = srcs.length ? srcs.join("|") : `__single__${sku.id}`;
      if (arrayTexCache.has(cacheKey)) return arrayTexCache.get(cacheKey);

      const depth = Math.max(1, srcs.length);
      const layerBytes = FACE_TEX_SIZE * FACE_TEX_SIZE * 4;
      const data = new Uint8Array(layerBytes * depth);

      const scratch = document.createElement("canvas");
      scratch.width = FACE_TEX_SIZE;
      scratch.height = FACE_TEX_SIZE;
      const sctx = scratch.getContext("2d");

      const fallbackHex = sku.pbr?.baseHex || "#d6d3cd";
      const imgs = await Promise.all(srcs.map(loadHtmlImage));

      for (let layer = 0; layer < depth; layer++) {
        sctx.clearRect(0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE);
        const img = imgs[layer];
        if (img) {
          sctx.drawImage(img, 0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE);
        } else {
          sctx.fillStyle = fallbackHex;
          sctx.fillRect(0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE);
        }
        const rgba = sctx.getImageData(0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE).data;
        data.set(rgba, layer * layerBytes);
      }

      const arrTex = new THREE.DataArrayTexture(data, FACE_TEX_SIZE, FACE_TEX_SIZE, depth);
      arrTex.format = THREE.RGBAFormat;
      arrTex.type = THREE.UnsignedByteType;
      arrTex.colorSpace = THREE.SRGBColorSpace;
      arrTex.magFilter = THREE.LinearFilter;
      arrTex.minFilter = THREE.LinearMipmapLinearFilter;
      arrTex.generateMipmaps = true;
      arrTex.wrapS = THREE.ClampToEdgeWrapping;
      arrTex.wrapT = THREE.ClampToEdgeWrapping;
      arrTex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      arrTex.needsUpdate = true;

      const entry = { tex: arrTex, count: depth, names: faces.map((f) => f.name) };
      arrayTexCache.set(cacheKey, entry);
      return entry;
    }

    const host = document.getElementById("canvasHost");
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#232730");

    const camera = new THREE.PerspectiveCamera(48, host.clientWidth / host.clientHeight, 0.1, 100);
    camera.position.set(0.6, 2.3, 5.6);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(host.clientWidth, host.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.1, 0);
    controls.enableDamping = true;

    scene.add(new THREE.HemisphereLight("#ffffff", "#64748b", 0.75));
    const dirLight = new THREE.DirectionalLight("#fff7ed", 1.35);
    dirLight.position.set(3.5, 6.0, 4.5);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(1024, 1024);
    scene.add(dirLight);

    const floorMesh = new THREE.Mesh(new THREE.PlaneGeometry(5, 4), new THREE.MeshStandardMaterial({ color: "#d6d3cd" }));
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.receiveShadow = true;
    scene.add(floorMesh);

    const backWallMesh = new THREE.Mesh(new THREE.PlaneGeometry(5, 3), new THREE.MeshStandardMaterial({ color: "#e5e7eb" }));
    backWallMesh.receiveShadow = true;
    scene.add(backWallMesh);

    const sideWallMesh = new THREE.Mesh(new THREE.PlaneGeometry(4, 3), new THREE.MeshStandardMaterial({ color: "#cbd5e1" }));
    sideWallMesh.rotation.y = Math.PI / 2;
    sideWallMesh.receiveShadow = true;
    scene.add(sideWallMesh);

    const surfaceState = {
      floor: { label: "Floor", mesh: floorMesh, widthM: 5.0, heightM: 4.0, skuId: null, pattern: "grid", groutMm: 2.0, groutHex: "#e2dfd9", finish: "catalog", renderSeq: 0 },
      backWall: { label: "Feature Wall", mesh: backWallMesh, widthM: 5.0, heightM: 3.0, skuId: null, pattern: "grid", groutMm: 2.0, groutHex: "#e2dfd9", finish: "catalog", renderSeq: 0 },
      sideWall: { label: "Side Wall", mesh: sideWallMesh, widthM: 4.0, heightM: 3.0, skuId: null, pattern: "grid", groutMm: 2.0, groutHex: "#e2dfd9", finish: "catalog", renderSeq: 0 }
    };

    function getSurfaceSku(surfKey) {
      const cfg = surfaceState[surfKey];
      return catalogItems.find((i) => i.id === cfg?.skuId) || null;
    }

    function resolveFinishProps(sku, presetKey) {
      if (presetKey && FINISH_PRESETS[presetKey]) return FINISH_PRESETS[presetKey];
      const pbr = sku?.pbr || {};
      return {
        roughness: pbr.roughness ?? 0.28,
        metalness: pbr.metalness ?? 0.02,
        clearcoat: pbr.clearcoat ?? 0.25,
        clearcoatRoughness: pbr.clearcoatRoughness ?? 0.16,
      };
    }

    function applyFinishToMaterial(surfKey) {
      const cfg = surfaceState[surfKey];
      const sku = getSurfaceSku(surfKey);
      const mat = cfg?.mesh?.material;
      if (!mat || !sku) return;
      const f = resolveFinishProps(sku, cfg.finish);
      mat.roughness = f.roughness;
      mat.metalness = f.metalness;
      if ("clearcoat" in mat) mat.clearcoat = f.clearcoat;
      if ("clearcoatRoughness" in mat) mat.clearcoatRoughness = f.clearcoatRoughness;
      mat.needsUpdate = false;
    }

    function applyGpuTileShader(mat, uniforms) {
      mat.onBeforeCompile = (shader) => {
        Object.assign(shader.uniforms, uniforms);
        mat.userData.shaderUniforms = shader.uniforms;

        shader.vertexShader = shader.vertexShader
          .replace(
            "#include <common>",
            `#include <common>
             varying vec2 vTileSurfaceMeters;
             uniform vec2 uSurfaceMeters;`
          )
          .replace(
            "#include <uv_vertex>",
            `#include <uv_vertex>
             vTileSurfaceMeters = uv * uSurfaceMeters;`
          );

        shader.fragmentShader = shader.fragmentShader
          .replace(
            "#include <common>",
            `#include <common>
             varying vec2 vTileSurfaceMeters;
             uniform highp sampler2DArray uFaceTex;
             uniform float uFaceCount;
             uniform vec2 uTileSizeM;
             uniform float uGroutM;
             uniform float uStaggered;
             uniform float uCycleFaces;
             uniform float uRotateEnabled;
             uniform float uRelief;
             uniform vec3 uGroutColor;

             float tileHash21(vec2 p) {
               p = fract(p * vec2(123.34, 456.21));
               p += dot(p, p + 45.32);
               return fract(p.x * p.y);
             }

             vec2 rotateTileUv(vec2 uvCoord, float turns) {
               vec2 centered = uvCoord - 0.5;
               if (turns < 0.5) return uvCoord;
               if (turns < 1.5) return vec2(-centered.y, centered.x) + 0.5;
               if (turns < 2.5) return vec2(-centered.x, -centered.y) + 0.5;
               return vec2(centered.y, -centered.x) + 0.5;
             }`
          )
          .replace(
            "#include <map_fragment>",
            `vec2 pitchM = max(uTileSizeM + vec2(uGroutM), vec2(0.05));
             float rowIdx = floor(vTileSurfaceMeters.y / pitchM.y);
             float staggerShift = (uStaggered > 0.5 && mod(abs(rowIdx), 2.0) > 0.5) ? pitchM.x * 0.5 : 0.0;
             float shiftedX = vTileSurfaceMeters.x + staggerShift;
             float colIdx = floor(shiftedX / pitchM.x);
             vec2 cellId = vec2(colIdx, rowIdx);

             vec2 localPosM = vec2(
               shiftedX - colIdx * pitchM.x,
               vTileSurfaceMeters.y - rowIdx * pitchM.y
             );

             float halfGrout = max(uGroutM * 0.5, 0.0);
             float edgeDistX = min(localPosM.x, pitchM.x - localPosM.x);
             float edgeDistY = min(localPosM.y, pitchM.y - localPosM.y);
             float edgeDist = min(edgeDistX, edgeDistY);
             float aaWidth = max(fwidth(edgeDist), 0.0005);
             float simpoloGroutMask = (uGroutM > 0.00001)
               ? (1.0 - smoothstep(max(halfGrout - aaWidth, 0.0), halfGrout + aaWidth, edgeDist))
               : 0.0;

             vec2 innerUv = clamp(
               (localPosM - vec2(halfGrout)) / max(pitchM - vec2(uGroutM), vec2(0.01)),
               vec2(0.002),
               vec2(0.998)
             );

             float hFace = tileHash21(cellId + vec2(17.3, 9.1));
             float hRot = tileHash21(cellId + vec2(53.7, 29.4));

             float layerIdx = 0.0;
             if (uCycleFaces > 0.5 && uFaceCount > 1.5) {
               layerIdx = clamp(floor(hFace * uFaceCount), 0.0, uFaceCount - 1.0);
             }

             // Restrict rectangular tiles to 0 or 180 degrees to prevent texture stretching
             float isSquareTile = step(abs(uTileSizeM.x - uTileSizeM.y), 0.01);
             float rotTurns = 0.0;
             if (uRotateEnabled > 0.5) {
               rotTurns = (isSquareTile > 0.5) ? floor(hRot * 4.0) : (floor(hRot * 2.0) * 2.0);
             }
             vec2 sampledUv = rotateTileUv(innerUv, rotTurns);

             vec4 texSample = texture(uFaceTex, vec3(sampledUv, layerIdx));
             vec3 tileLinear = texSample.rgb;
             vec3 groutLinear = uGroutColor;
             vec3 finalAlbedo = mix(tileLinear, groutLinear, simpoloGroutMask);

             float luma = dot(tileLinear, vec3(0.299, 0.587, 0.114));
             float grainDelta = (luma - 0.5) * 0.18 * uRelief;
             finalAlbedo = clamp(finalAlbedo + vec3(grainDelta) * (1.0 - simpoloGroutMask), 0.0, 1.0);

             diffuseColor.rgb *= finalAlbedo;`
          )
          .replace(
            "#include <roughnessmap_fragment>",
            `#include <roughnessmap_fragment>
             roughnessFactor = mix(roughnessFactor, 0.92, simpoloGroutMask);`
          );
      };
      mat.customProgramCacheKey = () => "simpolo-gpu-tile-shader-v2";
    }

    function updateFaceBadge() {
      const target = document.getElementById("surfaceSelect").value;
      const sku = getSurfaceSku(target);
      if (!sku) return;
      const cycle = document.getElementById("toggleCycleFaces").checked;
      const rot = document.getElementById("toggleTileRotate").checked;
      const spec = readTileSpec(sku);
      const isSq = spec.sizeKnown && Math.abs(spec.widthMm - spec.heightMm) <= 10;
      const rotLabel = !rot ? "OFF" : (isSq ? "0/90/180/270°" : "0/180°");
      const faces = getSiblingFaces(sku).map((f) => f.name);
      document.getElementById("faceInfo").textContent =
        `Shader faces (${faces.length}): ${faces.slice(0, 4).join(", ")}${faces.length > 4 ? "…" : ""} • Cycle: ${cycle ? "ON" : "OFF"} • Rot: ${rotLabel}`;
    }

    function syncShaderUniformsOnly() {
      const cycle = document.getElementById("toggleCycleFaces").checked ? 1.0 : 0.0;
      const rot = document.getElementById("toggleTileRotate").checked ? 1.0 : 0.0;
      const relief = numInput("reliefSlider", 1.0, 0, 2.5);
      document.getElementById("reliefVal").textContent = relief.toFixed(2);

      Object.keys(surfaceState).forEach((k) => {
        const cfg = surfaceState[k];
        const u = cfg.mesh.material?.userData?.shaderUniforms;
        if (!u) return;
        u.uSurfaceMeters.value.set(cfg.widthM, cfg.heightM);
        u.uGroutM.value = cfg.groutMm / 1000;
        u.uStaggered.value = cfg.pattern === "staggered" ? 1.0 : 0.0;
        u.uGroutColor.value.set(cfg.groutHex);
        u.uCycleFaces.value = cycle;
        u.uRotateEnabled.value = rot;
        u.uRelief.value = relief;
      });
      updateFaceBadge();
    }

    async function renderSurfaceMaterial(surfKey) {
      const cfg = surfaceState[surfKey];
      const sku = getSurfaceSku(surfKey);
      if (!sku) return;

      const mySeq = ++cfg.renderSeq;
      const spec = readTileSpec(sku);
      const tileW_m = (spec.widthMm || 600) / 1000;
      const tileH_m = (spec.heightMm || 1200) / 1000;
      const arrEntry = await getSiblingArrayTexture(sku);
      if (mySeq !== cfg.renderSeq) return; // Ignore stale async response

      const finish = resolveFinishProps(sku, cfg.finish);
      const mat = new THREE.MeshPhysicalMaterial({
        color: new THREE.Color("#ffffff"),
        roughness: finish.roughness,
        metalness: finish.metalness,
        clearcoat: finish.clearcoat,
        clearcoatRoughness: finish.clearcoatRoughness,
      });

      const uniforms = {
        uFaceTex: { value: arrEntry.tex },
        uFaceCount: { value: arrEntry.count },
        uSurfaceMeters: { value: new THREE.Vector2(cfg.widthM, cfg.heightM) },
        uTileSizeM: { value: new THREE.Vector2(tileW_m, tileH_m) },
        uGroutM: { value: cfg.groutMm / 1000 },
        uStaggered: { value: cfg.pattern === "staggered" ? 1.0 : 0.0 },
        uCycleFaces: { value: document.getElementById("toggleCycleFaces").checked ? 1.0 : 0.0 },
        uRotateEnabled: { value: document.getElementById("toggleTileRotate").checked ? 1.0 : 0.0 },
        uRelief: { value: numInput("reliefSlider", 1.0, 0, 2.5) },
        uGroutColor: { value: new THREE.Color(cfg.groutHex) },
      };

      applyGpuTileShader(mat, uniforms);

      if (cfg.mesh.material?.dispose) cfg.mesh.material.dispose();
      cfg.mesh.material = mat;
      updateFaceBadge();
    }

    function rebuildRoomGeometry(forceMaterials = false) {
      const w = numInput("roomW", 5.0, 2, 20, true);
      const d = numInput("roomD", 4.0, 2, 20, true);
      const h = numInput("roomH", 3.0, 2.2, 6, true);

      surfaceState.floor.widthM = w; surfaceState.floor.heightM = d;
      floorMesh.geometry.dispose();
      floorMesh.geometry = new THREE.PlaneGeometry(w, d);

      surfaceState.backWall.widthM = w; surfaceState.backWall.heightM = h;
      backWallMesh.geometry.dispose();
      backWallMesh.geometry = new THREE.PlaneGeometry(w, h);
      backWallMesh.position.set(0, h / 2, -d / 2);

      surfaceState.sideWall.widthM = d; surfaceState.sideWall.heightM = h;
      sideWallMesh.geometry.dispose();
      sideWallMesh.geometry = new THREE.PlaneGeometry(d, h);
      sideWallMesh.position.set(-w / 2, h / 2, 0);

      Object.keys(surfaceState).forEach((k) => {
        if (forceMaterials || !surfaceState[k].mesh.material?.userData?.shaderUniforms) {
          renderSurfaceMaterial(k);
        }
      });
      syncShaderUniformsOnly();
      updateBoqSummary();
    }

    function currentBOQ() {
      const w = numInput("roomW", 5.0, 2, 20, true);
      const d = numInput("roomD", 4.0, 2, 20, true);
      const h = numInput("roomH", 3.0, 2.2, 6, true);
      const skirtMode = document.getElementById("skirtingMode").value;
      const skirtLengthM = skirtMode === "4wall" ? 2 * (w + d) : (w + d);

      return computeBOQ({
        room: { w, d, h },
        surfaces: {
          floor: getSurfaceSku("floor"),
          backWall: getSurfaceSku("backWall"),
          sideWall: getSurfaceSku("sideWall"),
        },
        wastagePct: numInput("wastagePct", 10, 0, 30, true),
        pattern: document.getElementById("patternSelect").value,
        groutMm: numInput("groutMm", 2.0, 0, 15, true),
        openings: {
          backWall: numInput("openBack", 0, 0, 50, true),
          sideWall: numInput("openSide", 0, 0, 50, true),
        },
        skirting: {
          enabled: document.getElementById("toggleSkirting").checked,
          lengthM: skirtLengthM,
        },
      });
    }

    function updateBoqSummary() {
      const boqEl = document.getElementById("boqSummary");
      if (!getSurfaceSku("floor") || !getSurfaceSku("backWall") || !getSurfaceSku("sideWall")) {
        boqEl.textContent = "Waiting for catalog SKUs...";
        return;
      }
      const boq = currentBOQ();
      const { lines, totals } = boq;
      const pattern = document.getElementById("patternSelect").value;
      const groutMm = numInput("groutMm", 2.0, 0, 15, true);

      let html = lines.map((l) => {
        const qtyText = l.pieces !== null
          ? `${l.purchasedSqFt.toFixed(1)} sq.ft (${l.pieces} pcs${l.boxes !== null ? `, ${l.boxes} box` : ""})`
          : "Quantity unavailable";
        const rateText = l.rate !== null ? ` @ ₹${l.rate}` : "";
        const amtText = l.amount !== null ? `₹${l.amount.toLocaleString("en-IN")}` : "—";
        const flagsHtml = (l.flags || []).length
          ? `<div class="boq-flag">${(l.flags || []).map((f) => escHtml(flagText(f))).join(" • ")}</div>`
          : "";
        return `<div class="boq-line">
          <div class="boq-row"><strong>${escHtml((l.roles || []).join(" + "))}:</strong><span>${escHtml(l.series)} (${escHtml(l.sizeLabel)})</span></div>
          <div class="boq-row"><span>${escHtml(pattern)} &bull; ${groutMm}mm</span><span>${escHtml(qtyText)}${escHtml(rateText)}</span></div>
          <div class="boq-row"><span>Line Total:</span><span>${escHtml(amtText)}</span></div>
          ${flagsHtml}
        </div>`;
      }).join("");

      html += `<div class="boq-consumables">
        Adhesive: ~${totals.adhesiveKg.toFixed(1)} kg (${totals.adhesiveBags} bags @ 20kg) &bull;
        Grout: ~${totals.groutKg.toFixed(2)} kg (assumes ${totals.groutAssumedThicknessMm}mm bed depth)
      </div>`;

      html += `<div class="boq-total">
        <div class="boq-row"><span>Gross (${totals.effectiveWastePct}% eff. waste):</span><span>${totals.grossSqM.toFixed(1)} m&sup2;</span></div>
        <div class="boq-row"><span>Est. Material (excl. GST):</span><span>₹${(totals.amount || 0).toLocaleString("en-IN")}</span></div>
      </div>`;

      if (totals.incomplete) {
        html += `<div class="boq-incomplete">Total is incomplete — one or more SKUs have missing size or rate data.</div>`;
      }

      boqEl.innerHTML = html;
    }

    function ensureSkuInDropdown(sku) {
      const sel = document.getElementById("skuSelect");
      if (![...sel.options].some((o) => o.value === sku.id)) {
        const opt = document.createElement("option");
        opt.value = sku.id;
        opt.textContent = `${sku.series} — ${sku.name}`;
        sel.appendChild(opt);
      }
    }

    // ---- Texture Inspector Modal Logic ----
    const inspectorModal = document.getElementById("inspectorModal");
    const modalStage = document.getElementById("modalStage");
    const modalImg = document.getElementById("modalImg");
    const modalZoomSlider = document.getElementById("modalZoomSlider");
    const modalZoomLabel = document.getElementById("modalZoomLabel");
    let modalSku = null;
    let modalZoom = 1;
    let modalPanX = 0;
    let modalPanY = 0;
    let isDraggingModal = false;
    let dragStartX = 0;
    let dragStartY = 0;

    function updateModalTransform() {
      modalImg.style.transform = `translate(${modalPanX}px, ${modalPanY}px) scale(${modalZoom})`;
      modalZoomSlider.value = String(modalZoom);
      modalZoomLabel.textContent = `${modalZoom.toFixed(1)}x`;
    }

    function resetModalZoom() {
      modalZoom = 1;
      modalPanX = 0;
      modalPanY = 0;
      updateModalTransform();
    }

    function openInspector(sku) {
      if (!sku) return;
      modalSku = sku;
      const spec = readTileSpec(sku);
      const faces = getSiblingFaces(sku);
      document.getElementById("modalSeries").textContent = sku.series || "Simpolo";
      document.getElementById("modalTitle").textContent = sku.name || sku.id;
      modalImg.src = sku.pbr?.maps?.albedo || "";
      modalImg.alt = sku.name || "Tile texture";
      document.getElementById("modalSpecs").innerHTML = `
        <div><strong>Dimensions:</strong> ${spec.sizeKnown ? `${spec.widthMm} &times; ${spec.heightMm} mm` : "Unknown"}</div>
        <div><strong>Look &amp; Feel:</strong> ${escHtml(sku.lookAndFeel || "—")}</div>
        <div><strong>Finish:</strong> ${escHtml(sku.finish || "Catalog Default")}</div>
        <div><strong>Rate:</strong> ${spec.rateKnown ? `₹${spec.rate}/sq.ft` : "On request"}</div>
        <div><strong>Sibling Faces:</strong> ${faces.length} detected</div>
      `;
      resetModalZoom();
      inspectorModal.classList.add("open");
      inspectorModal.setAttribute("aria-hidden", "false");
    }

    function closeInspector() {
      inspectorModal.classList.remove("open");
      inspectorModal.setAttribute("aria-hidden", "true");
    }

    modalZoomSlider.addEventListener("input", () => {
      modalZoom = parseFloat(modalZoomSlider.value) || 1;
      if (modalZoom <= 1) { modalPanX = 0; modalPanY = 0; }
      updateModalTransform();
    });

    modalStage.addEventListener("wheel", (e) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.35 : -0.35;
      modalZoom = Math.min(6, Math.max(1, modalZoom + delta));
      if (modalZoom <= 1) { modalPanX = 0; modalPanY = 0; }
      updateModalTransform();
    }, { passive: false });

    modalStage.addEventListener("pointerdown", (e) => {
      if (modalZoom <= 1) return;
      isDraggingModal = true;
      dragStartX = e.clientX - modalPanX;
      dragStartY = e.clientY - modalPanY;
      modalStage.setPointerCapture(e.pointerId);
    });

    modalStage.addEventListener("pointermove", (e) => {
      if (!isDraggingModal) return;
      modalPanX = e.clientX - dragStartX;
      modalPanY = e.clientY - dragStartY;
      updateModalTransform();
    });

    modalStage.addEventListener("pointerup", () => { isDraggingModal = false; });
    modalStage.addEventListener("pointercancel", () => { isDraggingModal = false; });
    document.getElementById("modalResetZoom").addEventListener("click", resetModalZoom);
    document.getElementById("modalCloseBtn").addEventListener("click", closeInspector);
    inspectorModal.addEventListener("click", (e) => { if (e.target === inspectorModal) closeInspector(); });
    window.addEventListener("keydown", (e) => { if (e.key === "Escape") closeInspector(); });

    document.getElementById("modalApplyBtn").addEventListener("click", () => {
      if (!modalSku) return;
      ensureSkuInDropdown(modalSku);
      document.getElementById("skuSelect").value = modalSku.id;
      applySkuChangeToActiveSurface();
      closeInspector();
      document.getElementById("visualizer").scrollIntoView({ behavior: "smooth" });
    });

    // ---- Catalog Rendering ----
    function applyFilterAndRender(resetCount = true) {
      if (resetCount) visibleCount = PAGE_SIZE;
      const q = document.getElementById("searchInput").value.trim().toLowerCase();
      const sVal = document.getElementById("seriesFilter").value;
      const szVal = document.getElementById("sizeFilter").value;

      filteredItems = catalogItems.filter((item) => {
        if (activeLook !== "All" && item.lookAndFeel !== activeLook) return false;
        if (sVal !== "All" && item.series !== sVal) return false;
        const spec = readTileSpec(item);
        const sizeStr = spec.sizeKnown ? `${spec.widthMm}x${spec.heightMm}` : "";
        if (szVal !== "All" && sizeStr !== szVal) return false;
        if (q) {
          const hay = `${item.name || ""} ${item.series || ""} ${item.finish || ""} ${sizeStr}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      document.getElementById("catalogCount").textContent =
        `Showing ${Math.min(visibleCount, filteredItems.length)} of ${filteredItems.length} matching (${catalogItems.length} total)`;

      const slice = filteredItems.slice(0, visibleCount);
      document.getElementById("skuCards").innerHTML = slice.map((item) => {
        const spec = readTileSpec(item);
        const dimLabel = spec.sizeKnown ? `${spec.widthMm}x${spec.heightMm}mm` : "Size unknown";
        const rateLabel = spec.rateKnown ? `₹${spec.rate}/sq.ft` : "Rate on request";
        return `<div class="card">
          <div class="card-thumb-wrap" data-inspect-sku="${escHtml(item.id)}">
            <img class="card-thumb" src="${escHtml(item.pbr?.maps?.albedo || "")}" alt="${escHtml(item.name)}" loading="lazy" />
            <span class="zoom-badge">6x Zoom</span>
          </div>
          <div class="card-body">
            <div>
              <div class="card-series">${escHtml(item.series)}</div>
              <div class="card-title">${escHtml(item.name)}</div>
              <div class="card-meta">${escHtml(dimLabel)} &bull; ${escHtml(rateLabel)}</div>
            </div>
            <div class="card-actions">
              <button class="card-btn" data-apply-sku="${escHtml(item.id)}">Apply in 3D</button>
              <button class="inspect-btn" data-inspect-sku="${escHtml(item.id)}" title="Inspect Texture">Zoom</button>
            </div>
          </div>
        </div>`;
      }).join("");

      document.querySelectorAll("[data-apply-sku]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const sku = catalogItems.find((i) => i.id === btn.dataset.applySku);
          if (!sku) return;
          ensureSkuInDropdown(sku);
          document.getElementById("skuSelect").value = sku.id;
          applySkuChangeToActiveSurface();
          document.getElementById("visualizer").scrollIntoView({ behavior: "smooth" });
        });
      });

      document.querySelectorAll("[data-inspect-sku]").forEach((el) => {
        el.addEventListener("click", () => {
          const sku = catalogItems.find((i) => i.id === el.dataset.inspectSku);
          if (sku) openInspector(sku);
        });
      });

      const moreBtn = document.getElementById("loadMoreBtn");
      moreBtn.style.display = visibleCount < filteredItems.length ? "inline-block" : "none";
      moreBtn.textContent = `Load More (${filteredItems.length - visibleCount} remaining)`;
    }

    function populateFiltersAndHero() {
      const seriesList = [...new Set(catalogItems.map((i) => i.series).filter(Boolean))].sort();
      const sizeList = [...new Set(catalogItems.map((i) => {
        const sp = readTileSpec(i);
        return sp.sizeKnown ? `${sp.widthMm}x${sp.heightMm}` : null;
      }).filter(Boolean))].sort();
      const lookList = ["All", ...new Set(catalogItems.map((i) => i.lookAndFeel).filter(Boolean))];

      document.getElementById("seriesFilter").innerHTML =
        `<option value="All">All Series (${seriesList.length})</option>` +
        seriesList.map((s) => `<option value="${escHtml(s)}">${escHtml(s)}</option>`).join("");

      document.getElementById("sizeFilter").innerHTML =
        `<option value="All">All Sizes</option>` +
        sizeList.map((sz) => `<option value="${escHtml(sz)}">${escHtml(sz)} mm</option>`).join("");

      document.getElementById("lookTabs").innerHTML = lookList.map((lk) =>
        `<button class="tab-btn ${lk === activeLook ? "active" : ""}" data-look="${escHtml(lk)}">${escHtml(lk)}</button>`
      ).join("");

      document.querySelectorAll("#lookTabs .tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          activeLook = btn.dataset.look;
          populateFiltersAndHero();
          applyFilterAndRender(true);
        });
      });

      const pillsEl = document.getElementById("heroSeriesPills");
      pillsEl.innerHTML = seriesList.slice(0, 8).map((s, idx) =>
        `<button class="pill-btn ${idx === 0 ? "active" : ""}" data-series="${escHtml(s)}">${escHtml(s)}</button>`
      ).join("");

      pillsEl.querySelectorAll(".pill-btn").forEach((p) => {
        p.addEventListener("click", () => {
          const sName = p.dataset.series;
          const match = catalogItems.find((i) => i.series === sName);
          if (match) {
            document.getElementById("heroTitle").textContent = `${match.series} Collection`;
            document.getElementById("heroDesc").textContent =
              `${catalogItems.length.toLocaleString()} indexed Simpolo items ready to filter and preview live on your floor or walls.`;
            if (match.pbr?.maps?.albedo) {
              document.getElementById("heroBg").style.backgroundImage = `url("${match.pbr.maps.albedo}")`;
            }
          }
          document.getElementById("seriesFilter").value = sName;
          pillsEl.querySelectorAll(".pill-btn").forEach((b) => b.classList.toggle("active", b.dataset.series === sName));
          applyFilterAndRender(true);
        });
      });
    }

    const surfaceSelect = document.getElementById("surfaceSelect");
    const skuSelect = document.getElementById("skuSelect");
    const finishPresetSelect = document.getElementById("finishPreset");
    const patternSelect = document.getElementById("patternSelect");
    const groutMmInput = document.getElementById("groutMm");
    const groutColorInput = document.getElementById("groutColor");

    function syncControlsFromActiveSurface() {
      const cfg = surfaceState[surfaceSelect.value];
      if (!cfg) return;
      if (cfg.skuId) skuSelect.value = cfg.skuId;
      finishPresetSelect.value = cfg.finish;
      patternSelect.value = cfg.pattern;
      groutMmInput.value = cfg.groutMm;
      groutColorInput.value = cfg.groutHex;
      updateFaceBadge();
    }

    async function applySkuChangeToActiveSurface() {
      const key = surfaceSelect.value;
      const cfg = surfaceState[key];
      if (!cfg) return;
      cfg.skuId = skuSelect.value;
      await renderSurfaceMaterial(key);
      updateBoqSummary();
    }

    function applyUniformChangeToActiveSurface() {
      const key = surfaceSelect.value;
      const cfg = surfaceState[key];
      if (!cfg) return;
      cfg.pattern = patternSelect.value;
      cfg.groutMm = numInput("groutMm", 2.0, 0, 15, true);
      cfg.groutHex = groutColorInput.value;
      syncShaderUniformsOnly();
      updateBoqSummary();
    }

    fetch("full_catalog.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(async (data) => {
        catalogItems = data.items || [];
        rebuildSiblingIndex(catalogItems);

        skuSelect.innerHTML = catalogItems.slice(0, 200)
          .map((item) => `<option value="${escHtml(item.id)}">${escHtml(item.series)} — ${escHtml(item.name)}</option>`)
          .join("");

        if (catalogItems.length > 0) {
          const s0 = catalogItems[0];
          const s1 = catalogItems[Math.min(1, catalogItems.length - 1)];
          const s2 = catalogItems[Math.min(2, catalogItems.length - 1)];
          [s0, s1, s2].forEach(ensureSkuInDropdown);

          surfaceState.floor.skuId = s0.id;
          surfaceState.backWall.skuId = s1.id;
          surfaceState.sideWall.skuId = s2.id;

          if (s0.pbr?.maps?.albedo) {
            document.getElementById("heroBg").style.backgroundImage = `url("${s0.pbr.maps.albedo}")`;
          }
          document.getElementById("heroTitle").textContent = `${catalogItems.length.toLocaleString()} Simpolo Surfaces in 3D`;

          populateFiltersAndHero();
          applyFilterAndRender(true);
          syncControlsFromActiveSurface();
          rebuildRoomGeometry(true);
        }
      })
      .catch((err) => {
        document.getElementById("catalogCount").textContent =
          "Could not load full_catalog.json. Ensure you are running via a local HTTP server from web_prototype/.";
        console.error(err);
      });

    document.getElementById("searchInput").addEventListener("input", () => applyFilterAndRender(true));
    document.getElementById("seriesFilter").addEventListener("change", () => applyFilterAndRender(true));
    document.getElementById("sizeFilter").addEventListener("change", () => applyFilterAndRender(true));
    document.getElementById("loadMoreBtn").addEventListener("click", () => {
      visibleCount += PAGE_SIZE;
      applyFilterAndRender(false);
    });

    surfaceSelect.addEventListener("change", syncControlsFromActiveSurface);
    skuSelect.addEventListener("change", applySkuChangeToActiveSurface);
    finishPresetSelect.addEventListener("change", () => {
      const key = surfaceSelect.value;
      surfaceState[key].finish = finishPresetSelect.value;
      applyFinishToMaterial(key);
    });

    patternSelect.addEventListener("change", applyUniformChangeToActiveSurface);
    groutMmInput.addEventListener("input", applyUniformChangeToActiveSurface);
    groutColorInput.addEventListener("input", applyUniformChangeToActiveSurface);

    ["toggleCycleFaces", "toggleTileRotate"].forEach((id) => {
      document.getElementById(id).addEventListener("change", syncShaderUniformsOnly);
    });
    document.getElementById("reliefSlider").addEventListener("input", syncShaderUniformsOnly);

    ["roomW", "roomD", "roomH"].forEach((id) => {
      document.getElementById(id).addEventListener("input", () => rebuildRoomGeometry(false));
    });
    ["wastagePct", "openBack", "openSide"].forEach((id) => {
      document.getElementById(id).addEventListener("input", updateBoqSummary);
    });
    document.getElementById("toggleSkirting").addEventListener("change", updateBoqSummary);
    document.getElementById("skirtingMode").addEventListener("change", updateBoqSummary);

    const lightSlider = document.getElementById("lightSlider");
    const lightVal = document.getElementById("lightVal");
    lightSlider.addEventListener("input", () => {
      dirLight.intensity = parseFloat(lightSlider.value);
      lightVal.textContent = dirLight.intensity.toFixed(2);
    });

    document.getElementById("exportBoqBtn").addEventListener("click", () => {
      navigator.clipboard?.writeText(document.getElementById("boqSummary").innerText);
      const btn = document.getElementById("exportBoqBtn");
      btn.textContent = "Copied!";
      setTimeout(() => { btn.textContent = "Copy Summary"; }, 1800);
    });

    document.getElementById("exportCsvBtn").addEventListener("click", () => {
      const csv = boqToCsv(currentBOQ());
      const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8;" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "Simpolo_3D_Room_BOQ.csv";
      a.click();
    });

    window.addEventListener("resize", () => {
      if (!host.clientWidth || !host.clientHeight) return;
      camera.aspect = host.clientWidth / host.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(host.clientWidth, host.clientHeight);
    });

    (function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    })();
  </script>
</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print("Wrote", OUT_HTML)