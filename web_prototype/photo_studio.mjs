import { readTileSpec } from "./boq.mjs";

const PAGE_SIZE = 36;
const TILE_TEX_SIZE = 512;

const STUDIO_CSS = `
  #ph-root {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: #f4f3ef;
    color: #18181b;
    flex-direction: column;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    line-height: 1.4;
  }
  #ph-root.is-open {
    display: flex;
  }
  #ph-root *, #ph-root *::before, #ph-root *::after {
    box-sizing: border-box;
  }

  .ph-bar {
    height: 54px;
    padding: 0 16px;
    background: #141518;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    border-bottom: 1px solid #272930;
    flex-shrink: 0;
  }
  .ph-bar-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .ph-back {
    background: #23252c;
    color: #ffffff;
    border: 1px solid #3f434e;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  }
  .ph-back:hover {
    background: #9a5b13;
    border-color: #9a5b13;
  }
  .ph-brand {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .ph-bar-note {
    font-size: 12px;
    color: #e4bc7e;
  }

  .ph-grid {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: 300px minmax(0, 1fr) 300px;
  }
  @media (max-width: 1024px) {
    #ph-root {
      overflow-y: auto;
    }
    .ph-grid {
      flex: none;
      grid-template-columns: 1fr;
    }
  }

  .ph-panel {
    background: #ffffff;
    display: flex;
    flex-direction: column;
    min-height: 0;
    border-right: 1px solid #e4e2dc;
  }
  .ph-panel:last-child {
    border-right: none;
    border-left: 1px solid #e4e2dc;
  }
  @media (max-width: 1024px) {
    .ph-panel, .ph-panel:last-child {
      border: none;
      border-bottom: 1px solid #e4e2dc;
    }
  }

  .ph-panel-head {
    padding: 12px 14px;
    background: #faf9f6;
    border-bottom: 1px solid #e4e2dc;
    flex-shrink: 0;
  }
  .ph-label-xs {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #52525b;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
  }
  .ph-panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 12px 14px;
  }

  .ph-surf-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .ph-surf-btn {
    width: 100%;
    display: grid;
    grid-template-columns: 40px minmax(0, 1fr);
    gap: 10px;
    align-items: center;
    padding: 7px 9px;
    border: 1.5px solid #e4e2dc;
    border-radius: 8px;
    background: #ffffff;
    text-align: left;
    cursor: pointer;
  }
  .ph-surf-btn.is-active {
    border-color: #9a5b13;
    background: #fdf7ef;
  }
  .ph-surf-thumb {
    width: 40px;
    height: 40px;
    border-radius: 5px;
    object-fit: cover;
    background: #e5e3dc;
  }
  .ph-surf-role {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: #9a5b13;
  }
  .ph-surf-name {
    font-size: 12px;
    font-weight: 700;
    color: #18181b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .ph-surf-sub {
    font-size: 11px;
    color: #52525b;
  }

  .ph-filters {
    padding: 10px 14px;
    border-bottom: 1px solid #e4e2dc;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-shrink: 0;
  }
  .ph-input, .ph-select {
    width: 100%;
    padding: 7px 9px;
    border: 1px solid #d4d4d8;
    border-radius: 6px;
    font-size: 12px;
    background: #ffffff;
    color: #18181b;
  }
  .ph-row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .ph-row-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
  }

  .ph-swatches {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .ph-swatch {
    border: 1px solid #e4e2dc;
    border-radius: 7px;
    overflow: hidden;
    background: #ffffff;
    cursor: pointer;
  }
  .ph-swatch:hover {
    border-color: #18181b;
  }
  .ph-swatch.is-applied {
    border: 2px solid #9a5b13;
  }
  .ph-swatch img {
    width: 100%;
    height: 70px;
    object-fit: cover;
    display: block;
    background: #e7e5e0;
  }
  .ph-swatch-info {
    padding: 6px 7px;
  }
  .ph-swatch-ser {
    font-size: 9.5px;
    font-weight: 700;
    text-transform: uppercase;
    color: #9a5b13;
  }
  .ph-swatch-title {
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .ph-swatch-dim {
    font-size: 10px;
    color: #52525b;
  }

  .ph-stage {
    position: relative;
    background: #141518;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 440px;
    padding: 16px;
    overflow: hidden;
  }
  .ph-drop {
    max-width: 480px;
    width: 100%;
    padding: 36px 24px;
    border: 1.5px dashed rgba(228, 188, 126, 0.55);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.03);
    color: #ffffff;
    text-align: center;
  }
  .ph-drop h2 {
    margin: 0 0 8px;
    font-size: 22px;
  }
  .ph-drop p {
    margin: 0 0 18px;
    font-size: 13px;
    color: #cbd5e1;
  }
  .ph-btn-light {
    background: #ffffff;
    color: #141518;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
  }
  .ph-btn-light:hover {
    background: #e4bc7e;
  }
  .ph-btn-sm {
    background: #faf9f6;
    color: #18181b;
    border: 1px solid #d4d4d8;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
  }
  .ph-btn-sm.is-active {
    background: #18181b;
    color: #ffffff;
    border-color: #18181b;
  }
  .ph-btn-block {
    width: 100%;
    margin-top: 10px;
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #18181b;
    background: #ffffff;
    color: #18181b;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  }

  .ph-frame {
    position: relative;
    display: none;
    max-width: 100%;
    max-height: 100%;
    user-select: none;
  }
  .ph-frame.is-ready {
    display: inline-block;
  }
  #phCanvas {
    display: block;
    max-width: 100%;
    max-height: calc(100vh - 130px);
    width: auto;
    height: auto;
  }
  .ph-hud {
    position: absolute;
    top: 12px;
    left: 12px;
    right: 12px;
    z-index: 20;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    pointer-events: none;
  }
  .ph-hud-group {
    display: inline-flex;
    gap: 4px;
    background: rgba(20, 21, 24, 0.85);
    padding: 4px;
    border-radius: 7px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    pointer-events: auto;
  }
  .ph-hud-btn {
    background: transparent;
    color: #e2e8f0;
    border: none;
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
  }
  .ph-hud-btn.is-active, .ph-hud-btn:hover {
    background: #9a5b13;
    color: #ffffff;
  }
  .ph-ai-tag {
    background: rgba(20, 21, 24, 0.85);
    color: #e4bc7e;
    border: 1px solid rgba(228, 188, 126, 0.35);
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
    pointer-events: auto;
  }

  .ph-quad-svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
  .ph-handle {
    position: absolute;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #ffffff;
    border: 3px solid #9a5b13;
    transform: translate(-50%, -50%);
    cursor: grab;
    z-index: 15;
  }
  .ph-split {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #ffffff;
    z-index: 12;
    pointer-events: none;
    display: none;
  }
  .ph-split-knob {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #141518;
    color: #ffffff;
    border: 2px solid #ffffff;
    display: grid;
    place-items: center;
    font-size: 12px;
    cursor: ew-resize;
    pointer-events: auto;
  }

  .ph-loader {
    position: absolute;
    inset: 0;
    z-index: 30;
    background: rgba(14, 15, 18, 0.8);
    display: none;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 8px;
    color: #ffffff;
    font-size: 13px;
  }
  .ph-loader.is-show {
    display: flex;
  }

  .ph-group {
    padding-bottom: 12px;
    margin-bottom: 12px;
    border-bottom: 1px solid #e4e2dc;
  }
  .ph-group:last-child {
    border-bottom: none;
    margin-bottom: 0;
  }
  .ph-field {
    font-size: 11.5px;
    font-weight: 600;
    color: #27272a;
    display: flex;
    justify-content: space-between;
    margin: 8px 0 4px;
  }
  .ph-range {
    width: 100%;
    accent-color: #9a5b13;
  }
  .ph-grout-dots {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
  }
  .ph-gdot {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid #d4d4d8;
    cursor: pointer;
    padding: 0;
  }
  .ph-gdot.is-active {
    border-color: #18181b;
  }
`;

function esc(v) {
  return String(v ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function computeHomography(quad) {
  const dst = [[0, 0], [1, 0], [1, 1], [0, 1]];
  const A = [];
  const b = [];
  for (let i = 0; i < 4; i++) {
    const [x, y] = quad[i];
    const [u, v] = dst[i];
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]);
    b.push(u);
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y]);
    b.push(v);
  }
  for (let col = 0; col < 8; col++) {
    let piv = col;
    for (let r = col + 1; r < 8; r++) {
      if (Math.abs(A[r][col]) > Math.abs(A[piv][col])) piv = r;
    }
    [A[col], A[piv]] = [A[piv], A[col]];
    [b[col], b[piv]] = [b[piv], b[col]];
    const d = Math.abs(A[col][col]) < 1e-10 ? 1e-10 : A[col][col];
    for (let c = col; c < 8; c++) A[col][c] /= d;
    b[col] /= d;
    for (let r = 0; r < 8; r++) {
      if (r === col) continue;
      const f = A[r][col];
      for (let c = col; c < 8; c++) A[r][c] -= f * A[col][c];
      b[r] -= f * b[col];
    }
  }
  return new Float32Array([b[0], b[3], b[6], b[1], b[4], b[7], b[2], b[5], 1.0]);
}

function hexRgb(hex) {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex || "#e2dfd9");
  return m ? [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255] : [0.89, 0.87, 0.85];
}

function mount() {
  if (document.getElementById("ph-root")) return;

  const styleEl = document.createElement("style");
  styleEl.textContent = STUDIO_CSS;
  document.head.appendChild(styleEl);

  const root = document.createElement("div");
  root.id = "ph-root";
  root.innerHTML = `
    <div class="ph-bar">
      <div class="ph-bar-left">
        <button type="button" class="ph-back" id="phCloseBtn">&larr; Back</button>
        <span class="ph-brand">Simpolo AI Room Visualizer</span>
      </div>
      <span class="ph-bar-note">01. Upload Room Photo &bull; 02. Pick Slab &bull; 03. Preview Instantly</span>
    </div>

    <div class="ph-grid">
      <aside class="ph-panel">
        <div class="ph-panel-head">
          <div class="ph-label-xs">
            <span>Target Surface</span>
            <button type="button" class="ph-btn-sm" id="phClearBtn">Clear</button>
          </div>
          <div class="ph-surf-list">
            <button type="button" class="ph-surf-btn is-active" data-surf="floor" id="phSurf_floor">
              <img class="ph-surf-thumb" id="phThumb_floor" src="" alt="" />
              <div style="min-width:0;">
                <div class="ph-surf-role">Floor</div>
                <div class="ph-surf-name" id="phName_floor">None applied</div>
                <div class="ph-surf-sub" id="phSub_floor">Select a material below</div>
              </div>
            </button>
            <button type="button" class="ph-surf-btn" data-surf="wall" id="phSurf_wall">
              <img class="ph-surf-thumb" id="phThumb_wall" src="" alt="" />
              <div style="min-width:0;">
                <div class="ph-surf-role">Wall</div>
                <div class="ph-surf-name" id="phName_wall">None applied</div>
                <div class="ph-surf-sub" id="phSub_wall">Select a material below</div>
              </div>
            </button>
          </div>
        </div>

        <div class="ph-filters">
          <input type="search" class="ph-input" id="phSearch" placeholder="Search 12,035 SKUs, marble, granite..." />
          <div class="ph-row-2">
            <select class="ph-select" id="phSeries"><option value="All">All Series</option></select>
            <select class="ph-select" id="phSize"><option value="All">All Sizes</option></select>
          </div>
          <div class="ph-label-xs" style="margin-bottom:0;">
            <span id="phCount">Loading...</span>
            <span style="color:#9a5b13;" id="phTargetLabel">Target: Floor</span>
          </div>
        </div>

        <div class="ph-panel-body">
          <div class="ph-swatches" id="phSwatches"></div>
          <button type="button" class="ph-btn-block" id="phMoreBtn" style="display:none;">Load More</button>
        </div>
      </aside>

      <section class="ph-stage">
        <input type="file" id="phFile" accept="image/*" style="display:none;" />

        <div class="ph-hud">
          <div class="ph-hud-group" id="phTools" style="display:none;">
            <button type="button" class="ph-hud-btn" id="phReuploadBtn">New Photo</button>
            <button type="button" class="ph-hud-btn is-active" id="phCompareBtn">Split Compare</button>
            <button type="button" class="ph-hud-btn" id="phQuadBtn">Corners</button>
            <button type="button" class="ph-hud-btn" id="phSaveBtn">Save PNG</button>
          </div>
          <div class="ph-ai-tag" id="phAiStatus">AI: Local Ready</div>
        </div>

        <div class="ph-drop" id="phDrop">
          <h2>Upload Room or Site Photo</h2>
          <p>Drop a room image here, choose a file, or press <strong>Ctrl + V</strong> to paste. AI segments floor &amp; walls automatically while keeping real room shadows.</p>
          <button type="button" class="ph-btn-light" id="phBrowseBtn">Upload Room Photo</button>
        </div>

        <div class="ph-frame" id="phFrame">
          <canvas id="phCanvas"></canvas>
          <svg class="ph-quad-svg" id="phQuadSvg" style="display:none;">
            <polygon id="phQuadPoly" fill="rgba(228,188,126,0.15)" stroke="#e4bc7e" stroke-width="2" stroke-dasharray="6 4"></polygon>
          </svg>
          <div class="ph-handle" data-h="0" style="display:none;"></div>
          <div class="ph-handle" data-h="1" style="display:none;"></div>
          <div class="ph-handle" data-h="2" style="display:none;"></div>
          <div class="ph-handle" data-h="3" style="display:none;"></div>
          <div class="ph-split" id="phSplit">
            <div class="ph-split-knob" id="phSplitKnob">&#8596;</div>
          </div>
        </div>

        <div class="ph-loader" id="phLoader">Analyzing room photo with AI...</div>
      </section>

      <aside class="ph-panel">
        <div class="ph-panel-head">
          <div class="ph-label-xs" style="margin-bottom:0;"><span>Perspective &amp; Realism</span></div>
        </div>
        <div class="ph-panel-body">
          <div class="ph-group">
            <div class="ph-label-xs"><span>Surface Dimensions (m)</span></div>
            <div class="ph-row-2">
              <div>
                <div class="ph-field"><span>Width</span></div>
                <input type="number" class="ph-input" id="phW" min="1" max="20" step="0.2" value="4.8" />
              </div>
              <div>
                <div class="ph-field"><span>Depth / Ht</span></div>
                <input type="number" class="ph-input" id="phH" min="1" max="20" step="0.2" value="4.2" />
              </div>
            </div>

            <div class="ph-field"><span>Pattern</span></div>
            <div class="ph-row-2">
              <button type="button" class="ph-btn-sm is-active" data-pat="grid">Grid</button>
              <button type="button" class="ph-btn-sm" data-pat="staggered">Staggered</button>
            </div>

            <div class="ph-field"><span>Rotation</span></div>
            <div class="ph-row-3">
              <button type="button" class="ph-btn-sm is-active" data-rot="0">0&deg;</button>
              <button type="button" class="ph-btn-sm" data-rot="45">45&deg;</button>
              <button type="button" class="ph-btn-sm" data-rot="90">90&deg;</button>
            </div>
          </div>

          <div class="ph-group">
            <div class="ph-label-xs"><span>Grout &amp; Lighting</span></div>
            <div class="ph-field"><span>Grout Width</span><span id="phGroutTxt">2.0 mm</span></div>
            <input type="range" class="ph-range" id="phGrout" min="0" max="8" step="0.5" value="2.0" />

            <div class="ph-field"><span>Grout Color</span></div>
            <div class="ph-grout-dots">
              <button type="button" class="ph-gdot" data-g="#f5f5f4" style="background:#f5f5f4;"></button>
              <button type="button" class="ph-gdot is-active" data-g="#e2dfd9" style="background:#e2dfd9;"></button>
              <button type="button" class="ph-gdot" data-g="#a8a59e" style="background:#a8a59e;"></button>
              <button type="button" class="ph-gdot" data-g="#52504c" style="background:#52504c;"></button>
              <input type="color" id="phGroutPicker" value="#e2dfd9" style="margin-left:auto;width:30px;height:24px;border:1px solid #d4d4d8;" />
            </div>

            <div class="ph-field"><span>Room Shadows</span><span id="phShTxt">90%</span></div>
            <input type="range" class="ph-range" id="phShadow" min="0" max="1.4" step="0.05" value="0.9" />

            <div class="ph-field"><span>Polish Sheen</span><span id="phGlTxt">45%</span></div>
            <input type="range" class="ph-range" id="phGloss" min="0" max="1.2" step="0.05" value="0.45" />
          </div>

          <div class="ph-group">
            <div class="ph-label-xs"><span>Mask Brush</span></div>
            <div class="ph-row-3">
              <button type="button" class="ph-btn-sm is-active" data-br="off">Off</button>
              <button type="button" class="ph-btn-sm" data-br="add">+ Add</button>
              <button type="button" class="ph-btn-sm" data-br="erase">- Erase</button>
            </div>
            <div class="ph-field"><span>Brush Size</span><span id="phBrTxt">28 px</span></div>
            <input type="range" class="ph-range" id="phBrush" min="8" max="90" step="2" value="28" />
          </div>
        </div>
      </aside>
    </div>
  `;
  document.body.appendChild(root);

  function openStudio() {
    root.classList.add("is-open");
    document.body.style.overflow = "hidden";
    updateQuad();
  }
  function closeStudio() {
    root.classList.remove("is-open");
    document.body.style.overflow = "";
  }

  document.getElementById("phCloseBtn").addEventListener("click", closeStudio);
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && root.classList.contains("is-open")) closeStudio();
  });

  // Add trigger button in top bar without disturbing existing layout
  const header = document.querySelector("header .nav-wrap, header");
  if (header) {
    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.textContent = "My Room Photo (AI)";
    trigger.style.cssText =
      "background:#18181b;color:#f59e0b;border:1px solid #3f3f46;border-radius:6px;padding:7px 12px;font-size:12px;font-weight:700;cursor:pointer;";
    trigger.addEventListener("click", openStudio);
    header.appendChild(trigger);
  }

  // WebGL2 setup
  const canvas = document.getElementById("phCanvas");
  const gl = canvas.getContext("webgl2", { preserveDrawingBuffer: true });
  const VS = `#version 300 es
    in vec2 aPos;
    out vec2 vUv;
    void main() {
      vUv = vec2(aPos.x * 0.5 + 0.5, 0.5 - aPos.y * 0.5);
      gl_Position = vec4(aPos, 0.0, 1.0);
    }
  `;
  const FS = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 outColor;
    uniform sampler2D uOrig, uShadow, uFloorMask, uFloorTex, uWallMask, uWallTex;
    uniform float uShadowStr, uCompare, uSplitX;
    uniform float uFloorOn, uFloorGroutM, uFloorStag, uFloorRot, uFloorGloss;
    uniform mat3 uFloorInvH;
    uniform vec2 uFloorM, uFloorTile;
    uniform vec3 uFloorGrout;
    uniform float uWallOn, uWallGroutM, uWallStag, uWallRot, uWallGloss;
    uniform mat3 uWallInvH;
    uniform vec2 uWallM, uWallTile;
    uniform vec3 uWallGrout;

    float h21(vec2 p) {
      p = fract(p * vec2(123.34, 456.21));
      p += dot(p, p + 45.32);
      return fract(p.x * p.y);
    }

    vec3 shadeTile(vec2 uv, vec3 orig, float lightM, sampler2D tex, mat3 invH, vec2 planeM, vec2 tileM, float groutM, float stagOn, vec3 groutC, float rot, float gloss) {
      vec3 q = invH * vec3(uv, 1.0);
      if (q.z <= 0.0001) return orig;
      vec2 m = (q.xy / q.z) * planeM;
      float cs = cos(rot), sn = sin(rot);
      vec2 p = mat2(cs, -sn, sn, cs) * m;
      vec2 pitch = max(tileM + vec2(groutM), vec2(0.05));
      float row = floor(p.y / pitch.y);
      float shift = (stagOn > 0.5 && mod(abs(row), 2.0) > 0.5) ? pitch.x * 0.5 : 0.0;
      float sx = p.x + shift;
      float col = floor(sx / pitch.x);
      vec2 loc = vec2(sx - col * pitch.x, p.y - row * pitch.y);
      float hg = max(groutM * 0.5, 0.0);
      float ed = min(min(loc.x, pitch.x - loc.x), min(loc.y, pitch.y - loc.y));
      float aa = max(fwidth(ed), 0.0006);
      float gm = groutM > 0.00001 ? (1.0 - smoothstep(max(hg - aa, 0.0), hg + aa, ed)) : 0.0;
      vec2 iuv = clamp((loc - vec2(hg)) / max(pitch - vec2(groutM), vec2(0.01)), vec2(0.003), vec2(0.997));
      float flp = step(0.5, h21(vec2(col, row) + vec2(19.1, 7.7)));
      vec2 suv = mix(iuv, 1.0 - iuv, flp);
      vec2 ct = vec2(sx, p.y) / pitch;
      vec3 tc = textureGrad(tex, suv, dFdx(ct) * mix(1.0, -1.0, flp), dFdy(ct) * mix(1.0, -1.0, flp)).rgb;
      vec3 colOut = mix(tc, groutC, gm) * mix(1.0, lightM, uShadowStr);
      float luma = dot(orig, vec3(0.299, 0.587, 0.114));
      return clamp(colOut + vec3(smoothstep(0.68, 0.98, luma) * gloss * 0.45) * (1.0 - gm), 0.0, 1.0);
    }

    void main() {
      vec3 orig = texture(uOrig, vUv).rgb;
      if (uCompare > 0.5 && vUv.x < uSplitX) { outColor = vec4(orig, 1.0); return; }
      float lm = texture(uShadow, vUv).r * 2.0;
      vec3 res = orig;
      if (uWallOn > 0.5) {
        float wm = texture(uWallMask, vUv).r;
        if (wm > 0.01) res = mix(res, shadeTile(vUv, orig, lm, uWallTex, uWallInvH, uWallM, uWallTile, uWallGroutM, uWallStag, uWallGrout, uWallRot, uWallGloss), wm);
      }
      if (uFloorOn > 0.5) {
        float fm = texture(uFloorMask, vUv).r;
        if (fm > 0.01) res = mix(res, shadeTile(vUv, orig, lm, uFloorTex, uFloorInvH, uFloorM, uFloorTile, uFloorGroutM, uFloorStag, uFloorGrout, uFloorRot, uFloorGloss), fm);
      }
      outColor = vec4(res, 1.0);
    }
  `;

  function makeShader(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  }
  const prog = gl.createProgram();
  gl.attachShader(prog, makeShader(gl.VERTEX_SHADER, VS));
  gl.attachShader(prog, makeShader(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog);
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
  const aPos = gl.getAttribLocation(prog, "aPos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  function makeTex(unit, mips) {
    const t = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, mips ? gl.LINEAR_MIPMAP_LINEAR : gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([128,128,128,255]));
    return t;
  }
  const tOrig = makeTex(0, false), tSh = makeTex(1, false), tFm = makeTex(2, false), tFt = makeTex(3, true), tWm = makeTex(4, false), tWt = makeTex(5, true);

  function pushTex(tex, unit, src, mips) {
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
    if (mips) gl.generateMipmap(gl.TEXTURE_2D);
  }

  let items = [], byId = new Map(), filtered = [], visible = PAGE_SIZE;
  let ready = false, activeSurf = "floor", compareOn = true, splitX = 0.35, showQuad = false, brush = "off", shStr = 0.9;
  const mCan = { floor: document.createElement("canvas"), wall: document.createElement("canvas") };
  const surfCfg = {
    floor: { sku: null, quad: [[0.2,0.62],[0.8,0.62],[1.05,1.0],[-0.05,1.0]], w: 4.8, h: 4.2, pat: "grid", grout: 2.0, ghex: "#e2dfd9", rot: 0, gloss: 0.45 },
    wall:  { sku: null, quad: [[0.1,0.08],[0.9,0.08],[0.9,0.62],[0.1,0.62]], w: 4.8, h: 3.0, pat: "grid", grout: 2.0, ghex: "#e2dfd9", rot: 0, gloss: 0.35 },
  };
  const U = (n) => gl.getUniformLocation(prog, n);

  function draw() {
    if (!ready) return;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.useProgram(prog);
    gl.uniform1i(U("uOrig"), 0); gl.uniform1i(U("uShadow"), 1); gl.uniform1i(U("uFloorMask"), 2);
    gl.uniform1i(U("uFloorTex"), 3); gl.uniform1i(U("uWallMask"), 4); gl.uniform1i(U("uWallTex"), 5);
    gl.uniform1f(U("uShadowStr"), shStr);
    gl.uniform1f(U("uCompare"), compareOn ? 1.0 : 0.0);
    gl.uniform1f(U("uSplitX"), splitX);

    const f = surfCfg.floor, fs = f.sku ? readTileSpec(f.sku) : null;
    gl.uniform1f(U("uFloorOn"), f.sku ? 1.0 : 0.0);
    gl.uniformMatrix3fv(U("uFloorInvH"), false, computeHomography(f.quad));
    gl.uniform2f(U("uFloorM"), f.w, f.h);
    gl.uniform2f(U("uFloorTile"), (fs?.widthMm || 600) / 1000, (fs?.heightMm || 1200) / 1000);
    gl.uniform1f(U("uFloorGroutM"), f.grout / 1000);
    gl.uniform1f(U("uFloorStag"), f.pat === "staggered" ? 1.0 : 0.0);
    gl.uniform3fv(U("uFloorGrout"), hexRgb(f.ghex));
    gl.uniform1f(U("uFloorRot"), (f.rot * Math.PI) / 180);
    gl.uniform1f(U("uFloorGloss"), f.gloss);

    const w = surfCfg.wall, ws = w.sku ? readTileSpec(w.sku) : null;
    gl.uniform1f(U("uWallOn"), w.sku ? 1.0 : 0.0);
    gl.uniformMatrix3fv(U("uWallInvH"), false, computeHomography(w.quad));
    gl.uniform2f(U("uWallM"), w.w, w.h);
    gl.uniform2f(U("uWallTile"), (ws?.widthMm || 600) / 1000, (ws?.heightMm || 1200) / 1000);
    gl.uniform1f(U("uWallGroutM"), w.grout / 1000);
    gl.uniform1f(U("uWallStag"), w.pat === "staggered" ? 1.0 : 0.0);
    gl.uniform3fv(U("uWallGrout"), hexRgb(w.ghex));
    gl.uniform1f(U("uWallRot"), (w.rot * Math.PI) / 180);
    gl.uniform1f(U("uWallGloss"), w.gloss);

    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }

  function loadImage(src) {
    return new Promise((res, rej) => {
      const im = new Image(); im.crossOrigin = "anonymous";
      im.onload = () => res(im); im.onerror = rej; im.src = src;
    });
  }

  async function pickSku(sku) {
    surfCfg[activeSurf].sku = sku;
    if (sku?.pbr?.maps?.albedo) {
      const im = await loadImage(sku.pbr.maps.albedo);
      const sc = document.createElement("canvas"); sc.width = TILE_TEX_SIZE; sc.height = TILE_TEX_SIZE;
      sc.getContext("2d").drawImage(im, 0, 0, TILE_TEX_SIZE, TILE_TEX_SIZE);
      pushTex(activeSurf === "floor" ? tFt : tWt, activeSurf === "floor" ? 3 : 5, sc, true);
    }
    syncUI();
    draw();
  }

  function syncUI() {
    ["floor", "wall"].forEach((k) => {
      const s = surfCfg[k];
      document.getElementById(`phSurf_${k}`).classList.toggle("is-active", k === activeSurf);
      document.getElementById(`phThumb_${k}`).src = s.sku?.pbr?.maps?.albedo || "";
      document.getElementById(`phName_${k}`).textContent = s.sku ? s.sku.name : "None applied";
      const sp = s.sku ? readTileSpec(s.sku) : null;
      document.getElementById(`phSub_${k}`).textContent = s.sku ? `${s.sku.series} • ${sp.sizeKnown ? `${sp.widthMm}×${sp.heightMm}` : "N/A"}` : "Select a material below";
    });
    const c = surfCfg[activeSurf];
    document.getElementById("phTargetLabel").textContent = `Target: ${activeSurf === "floor" ? "Floor" : "Wall"}`;
    document.getElementById("phW").value = String(c.w);
    document.getElementById("phH").value = String(c.h);
    document.getElementById("phGrout").value = String(c.grout);
    document.getElementById("phGroutTxt").textContent = `${c.grout.toFixed(1)} mm`;
    document.getElementById("phGroutPicker").value = c.ghex;
    document.getElementById("phGloss").value = String(c.gloss);
    document.getElementById("phGlTxt").textContent = `${Math.round(c.gloss * 100)}%`;
    document.querySelectorAll("[data-pat]").forEach((b) => b.classList.toggle("is-active", b.dataset.pat === c.pat));
    document.querySelectorAll("[data-rot]").forEach((b) => b.classList.toggle("is-active", Number(b.dataset.rot) === c.rot));
    document.querySelectorAll("[data-g]").forEach((b) => b.classList.toggle("is-active", b.dataset.g.toLowerCase() === c.ghex.toLowerCase()));
    document.querySelectorAll("[data-id]").forEach((el) => el.classList.toggle("is-applied", el.dataset.id === c.sku?.id));
    updateQuad();
  }

  function updateQuad() {
    const svg = document.getElementById("phQuadSvg");
    const poly = document.getElementById("phQuadPoly");
    const hs = document.querySelectorAll(".ph-handle");
    const vis = ready && showQuad;
    svg.style.display = vis ? "block" : "none";
    hs.forEach((h) => (h.style.display = vis ? "block" : "none"));
    if (!vis) return;
    const r = canvas.getBoundingClientRect();
    const q = surfCfg[activeSurf].quad;
    poly.setAttribute("points", q.map(([x, y]) => `${x * r.width},${y * r.height}`).join(" "));
    hs.forEach((h, i) => { h.style.left = `${q[i][0] * 100}%`; h.style.top = `${q[i][1] * 100}%`; });
  }

  function updateSplit() {
    const sp = document.getElementById("phSplit");
    sp.style.display = ready && compareOn ? "block" : "none";
    sp.style.left = `${splitX * 100}%`;
    document.getElementById("phCompareBtn").classList.toggle("is-active", compareOn);
  }

  async function uploadPhoto(file) {
    if (!file) return;
    const loader = document.getElementById("phLoader");
    loader.classList.add("is-show");
    try {
      const fd = new FormData(); fd.append("file", file);
      const res = await fetch("/api/analyze-room", { method: "POST", body: fd });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      const [imOrig, imSh, imFm, imWm] = await Promise.all([
        loadImage(d.photoUrl), loadImage(d.shadowMap), loadImage(d.floorMask), loadImage(d.wallMask),
      ]);
      canvas.width = d.width; canvas.height = d.height;
      pushTex(tOrig, 0, imOrig, false);
      pushTex(tSh, 1, imSh, false);
      ["floor", "wall"].forEach((k) => {
        mCan[k].width = d.width; mCan[k].height = d.height;
        const cx = mCan[k].getContext("2d"); cx.clearRect(0, 0, d.width, d.height);
        cx.drawImage(k === "floor" ? imFm : imWm, 0, 0, d.width, d.height);
      });
      pushTex(tFm, 2, mCan.floor, false);
      pushTex(tWm, 4, mCan.wall, false);
      surfCfg.floor.quad = d.floorQuad;
      surfCfg.wall.quad = d.wallQuad;
      ready = true;
      document.getElementById("phDrop").style.display = "none";
      document.getElementById("phFrame").classList.add("is-ready");
      document.getElementById("phTools").style.display = "inline-flex";
      const l=d.layout||{}; const a=l.areasSqFt||{}; const c=(l.corners2d||[]).length; document.getElementById("phAiStatus").textContent = `AI: ${d.engine} • Flr ${a.floor||0} sf • Wall ${a.wall||0} sf • Side ${a.sideWall||0} sf • Ceil ${a.ceiling||0} sf • ${c} corners`;
      if (!surfCfg.floor.sku && items.length) await pickSku(items[0]);
      else draw();
      updateSplit(); updateQuad();
    } catch (e) {
      alert("Run 'python server.py' first so /api/analyze-room is available.\n" + e.message);
    } finally {
      loader.classList.remove("is-show");
    }
  }

  const fin = document.getElementById("phFile");
  document.getElementById("phBrowseBtn").addEventListener("click", () => fin.click());
  document.getElementById("phReuploadBtn").addEventListener("click", () => fin.click());
  fin.addEventListener("change", () => { if (fin.files?.[0]) uploadPhoto(fin.files[0]); fin.value = ""; });

  const drop = document.getElementById("phDrop");
  drop.addEventListener("dragover", (e) => e.preventDefault());
  drop.addEventListener("drop", (e) => { e.preventDefault(); if (e.dataTransfer?.files?.[0]) uploadPhoto(e.dataTransfer.files[0]); });
  window.addEventListener("paste", (e) => {
    if (!root.classList.contains("is-open")) return;
    const it = [...(e.clipboardData?.items || [])].find((x) => x.type.startsWith("image/"));
    if (it) uploadPhoto(it.getAsFile());
  });

  let hIdx = -1;
  document.querySelectorAll(".ph-handle").forEach((h) => {
    h.addEventListener("pointerdown", (e) => { e.stopPropagation(); hIdx = Number(h.dataset.h); h.setPointerCapture(e.pointerId); });
    h.addEventListener("pointermove", (e) => {
      if (hIdx < 0) return;
      const r = canvas.getBoundingClientRect();
      surfCfg[activeSurf].quad[hIdx] = [
        Math.min(1.3, Math.max(-0.3, (e.clientX - r.left) / r.width)),
        Math.min(1.3, Math.max(-0.3, (e.clientY - r.top) / r.height)),
      ];
      updateQuad(); draw();
    });
    h.addEventListener("pointerup", () => { hIdx = -1; });
  });

  let dragSp = false;
  const knob = document.getElementById("phSplitKnob");
  knob.addEventListener("pointerdown", (e) => { e.stopPropagation(); dragSp = true; knob.setPointerCapture(e.pointerId); });
  knob.addEventListener("pointermove", (e) => {
    if (!dragSp) return;
    const r = canvas.getBoundingClientRect();
    splitX = Math.min(0.98, Math.max(0.02, (e.clientX - r.left) / r.width));
    updateSplit(); draw();
  });
  knob.addEventListener("pointerup", () => { dragSp = false; });

  let paint = false;
  function brushAt(e) {
    if (brush === "off" || !ready) return;
    const r = canvas.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * canvas.width;
    const y = ((e.clientY - r.top) / r.height) * canvas.height;
    const rad = Number(document.getElementById("phBrush").value) * (canvas.width / r.width);
    const mc = mCan[activeSurf], cx = mc.getContext("2d");
    const g = cx.createRadialGradient(x, y, rad * 0.3, x, y, rad);
    const c = brush === "add" ? "255,255,255" : "0,0,0";
    g.addColorStop(0, `rgba(${c},1)`); g.addColorStop(1, `rgba(${c},0)`);
    cx.fillStyle = g; cx.beginPath(); cx.arc(x, y, rad, 0, Math.PI * 2); cx.fill();
    pushTex(activeSurf === "floor" ? tFm : tWm, activeSurf === "floor" ? 2 : 4, mc, false);
    draw();
  }
  canvas.addEventListener("pointerdown", (e) => { if (brush !== "off") { paint = true; canvas.setPointerCapture(e.pointerId); brushAt(e); } });
  canvas.addEventListener("pointermove", (e) => { if (paint) brushAt(e); });
  canvas.addEventListener("pointerup", () => { paint = false; });

  document.querySelectorAll("[data-surf]").forEach((b) => b.addEventListener("click", () => { activeSurf = b.dataset.surf; syncUI(); }));
  document.getElementById("phClearBtn").addEventListener("click", () => { surfCfg[activeSurf].sku = null; syncUI(); draw(); });
  document.getElementById("phCompareBtn").addEventListener("click", () => { compareOn = !compareOn; updateSplit(); draw(); });
  document.getElementById("phQuadBtn").addEventListener("click", (e) => { showQuad = !showQuad; e.currentTarget.classList.toggle("is-active", showQuad); updateQuad(); });
  document.getElementById("phSaveBtn").addEventListener("click", () => {
    if (!ready) return;
    const prev = compareOn; compareOn = false; draw();
    const a = document.createElement("a"); a.href = canvas.toDataURL("image/png"); a.download = "Simpolo_AI_Room.png"; a.click();
    compareOn = prev; draw();
  });

  document.getElementById("phW").addEventListener("input", (e) => { surfCfg[activeSurf].w = Math.max(0.5, parseFloat(e.target.value) || 4.8); draw(); });
  document.getElementById("phH").addEventListener("input", (e) => { surfCfg[activeSurf].h = Math.max(0.5, parseFloat(e.target.value) || 4.2); draw(); });
  document.querySelectorAll("[data-pat]").forEach((b) => b.addEventListener("click", () => { surfCfg[activeSurf].pat = b.dataset.pat; syncUI(); draw(); }));
  document.querySelectorAll("[data-rot]").forEach((b) => b.addEventListener("click", () => { surfCfg[activeSurf].rot = Number(b.dataset.rot) || 0; syncUI(); draw(); }));
  document.getElementById("phGrout").addEventListener("input", (e) => { surfCfg[activeSurf].grout = parseFloat(e.target.value) || 0; document.getElementById("phGroutTxt").textContent = `${surfCfg[activeSurf].grout.toFixed(1)} mm`; draw(); });
  function setG(hex) { surfCfg[activeSurf].ghex = hex; syncUI(); draw(); }
  document.querySelectorAll("[data-g]").forEach((b) => b.addEventListener("click", () => setG(b.dataset.g)));
  document.getElementById("phGroutPicker").addEventListener("input", (e) => setG(e.target.value));
  document.getElementById("phShadow").addEventListener("input", (e) => { shStr = parseFloat(e.target.value); document.getElementById("phShTxt").textContent = `${Math.round(shStr * 100)}%`; draw(); });
  document.getElementById("phGloss").addEventListener("input", (e) => { surfCfg[activeSurf].gloss = parseFloat(e.target.value); document.getElementById("phGlTxt").textContent = `${Math.round(surfCfg[activeSurf].gloss * 100)}%`; draw(); });
  document.querySelectorAll("[data-br]").forEach((b) => b.addEventListener("click", () => {
    brush = b.dataset.br;
    document.querySelectorAll("[data-br]").forEach((x) => x.classList.toggle("is-active", x.dataset.br === brush));
    canvas.style.cursor = brush === "off" ? "default" : "crosshair";
  }));
  document.getElementById("phBrush").addEventListener("input", (e) => { document.getElementById("phBrTxt").textContent = `${e.target.value} px`; });
  window.addEventListener("resize", updateQuad);

  function renderSwatches(reset = true) {
    if (reset) visible = PAGE_SIZE;
    const q = document.getElementById("phSearch").value.trim().toLowerCase();
    const sv = document.getElementById("phSeries").value;
    const szv = document.getElementById("phSize").value;
    filtered = items.filter((it) => {
      if (sv !== "All" && it.series !== sv) return false;
      const sp = readTileSpec(it);
      const sz = sp.sizeKnown ? `${sp.widthMm}x${sp.heightMm}` : "";
      if (szv !== "All" && sz !== szv) return false;
      if (q && !`${it.name || ""} ${it.series || ""} ${sz}`.toLowerCase().includes(q)) return false;
      return true;
    });
    const activeId = surfCfg[activeSurf].sku?.id;
    document.getElementById("phCount").textContent = `${filtered.length.toLocaleString()} SKUs`;
    document.getElementById("phSwatches").innerHTML = filtered.slice(0, visible).map((it) => {
      const sp = readTileSpec(it);
      return `<div class="ph-swatch ${it.id === activeId ? "is-applied" : ""}" data-id="${esc(it.id)}">
        <img src="${esc(it.pbr?.maps?.albedo || "")}" alt="${esc(it.name)}" loading="lazy" />
        <div class="ph-swatch-info">
          <div class="ph-swatch-ser">${esc(it.series)}</div>
          <div class="ph-swatch-title">${esc(it.name)}</div>
          <div class="ph-swatch-dim">${sp.sizeKnown ? `${sp.widthMm}×${sp.heightMm}` : "N/A"}</div>
        </div>
      </div>`;
    }).join("");
    const mb = document.getElementById("phMoreBtn");
    mb.style.display = visible < filtered.length ? "block" : "none";
    mb.textContent = `Load More (${(filtered.length - visible).toLocaleString()} left)`;
  }

  document.getElementById("phSwatches").addEventListener("click", (e) => {
    const c = e.target.closest("[data-id]");
    if (c && byId.get(c.dataset.id)) pickSku(byId.get(c.dataset.id));
  });
  document.getElementById("phSearch").addEventListener("input", () => renderSwatches(true));
  document.getElementById("phSeries").addEventListener("change", () => renderSwatches(true));
  document.getElementById("phSize").addEventListener("change", () => renderSwatches(true));
  document.getElementById("phMoreBtn").addEventListener("click", () => { visible += PAGE_SIZE; renderSwatches(false); });

  fetch("full_catalog.json")
    .then((r) => r.json())
    .then((d) => {
      items = d.items || [];
      byId = new Map(items.map((i) => [i.id, i]));
      const sers = [...new Set(items.map((i) => i.series).filter(Boolean))].sort();
      const szs = [...new Set(items.map((i) => { const sp = readTileSpec(i); return sp.sizeKnown ? `${sp.widthMm}x${sp.heightMm}` : null; }).filter(Boolean))].sort();
      document.getElementById("phSeries").innerHTML = `<option value="All">All Series (${sers.length})</option>` + sers.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
      document.getElementById("phSize").innerHTML = `<option value="All">All Sizes</option>` + szs.map((z) => `<option value="${esc(z)}">${esc(z)} mm</option>`).join("");
      renderSwatches(true);
    });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
else mount();


let scanPreviewOn = false;
let lastScanLayout = null;
const scanOverlayCanvas = document.createElement("canvas");
const scanOverlayCtx = scanOverlayCanvas.getContext("2d");

function drawMaskContours(ctx, maskImg, strokeStyle, fillStyle) {
  if (!maskImg || !maskImg.complete || !maskImg.naturalWidth) return;
  const w = ctx.canvas.width;
  const h = ctx.canvas.height;
  const tmp = document.createElement("canvas");
  tmp.width = w;
  tmp.height = h;
  const tctx = tmp.getContext("2d");
  tctx.drawImage(maskImg, 0, 0, w, h);
  const { data } = tctx.getImageData(0, 0, w, h);

  ctx.save();
  ctx.fillStyle = fillStyle;
  ctx.strokeStyle = strokeStyle;
  ctx.lineWidth = 2;

  for (let y = 1; y < h - 1; y += 2) {
    for (let x = 1; x < w - 1; x += 2) {
      const idx = (y * w + x) * 4;
      const a = data[idx];
      if (a > 128) {
        ctx.fillRect(x, y, 2, 2);
        const right = data[(y * w + (x + 2)) * 4];
        const down = data[((y + 2) * w + x) * 4];
        if (right <= 128 || down <= 128) {
          ctx.fillStyle = strokeStyle;
          ctx.fillRect(x, y, 2.5, 2.5);
          ctx.fillStyle = fillStyle;
        }
      }
    }
  }
  ctx.restore();
}

export function renderScanPreview(mainCanvas, layoutData, maskImages = {}) {
  if (!mainCanvas || !scanPreviewOn) return;
  const w = mainCanvas.width;
  const h = mainCanvas.height;
  if (!w || !h) return;
  scanOverlayCanvas.width = w;
  scanOverlayCanvas.height = h;
  scanOverlayCtx.clearRect(0, 0, w, h);

  // 1. Region boundaries (Floor, Wall, Side Wall, Ceiling)
  drawMaskContours(scanOverlayCtx, maskImages.floor, "#22c55e", "rgba(34, 197, 94, 0.14)");
  drawMaskContours(scanOverlayCtx, maskImages.wall, "#38bdf8", "rgba(56, 189, 248, 0.12)");
  drawMaskContours(scanOverlayCtx, maskImages.sideWall, "#f59e0b", "rgba(245, 158, 11, 0.12)");
  drawMaskContours(scanOverlayCtx, maskImages.ceiling, "#c084fc", "rgba(192, 132, 252, 0.10)");

  // 2. Structural edge / barrier lines
  if (maskImages.barrier) {
    drawMaskContours(scanOverlayCtx, maskImages.barrier, "rgba(250, 204, 21, 0.85)", "rgba(0, 0, 0, 0)");
  }

  // 3. Detected corners
  const corners = (layoutData && layoutData.corners2d) || [];
  scanOverlayCtx.save();
  for (const pt of corners) {
    const px = (Array.isArray(pt) ? pt[0] : pt.x) * w;
    const py = (Array.isArray(pt) ? pt[1] : pt.y) * h;
    scanOverlayCtx.beginPath();
    scanOverlayCtx.arc(px, py, 4.5, 0, Math.PI * 2);
    scanOverlayCtx.fillStyle = "#facc15";
    scanOverlayCtx.fill();
    scanOverlayCtx.lineWidth = 1.5;
    scanOverlayCtx.strokeStyle = "#09090b";
    scanOverlayCtx.stroke();
  }

  // Legend badge in top-left of preview
  scanOverlayCtx.fillStyle = "rgba(9, 9, 11, 0.78)";
  scanOverlayCtx.fillRect(12, 12, 315, 26);
  scanOverlayCtx.fillStyle = "#f4f4f5";
  scanOverlayCtx.font = "600 12px sans-serif";
  scanOverlayCtx.fillText("SCAN PREVIEW: Green=Floor  Blue=Wall  Amber=Side  Gold=Edges/Corners", 20, 29);
  scanOverlayCtx.restore();

  const mctx = mainCanvas.getContext("2d");
  if (mctx) {
    mctx.drawImage(scanOverlayCanvas, 0, 0);
  }
}

export function setScanPreview(enabled) {
  scanPreviewOn = Boolean(enabled);
}


// --- Editable Vector Graph + Strict Projection Boundary ---
export class VectorRegionController {
  constructor(points = []) {
    // Array of { x, y } in normalized [0..1] image space
    this.points = points.length
      ? points.map((pt) => ({ x: pt[0] ?? pt.x, y: pt[1] ?? pt.y }))
      : [
          { x: 0.2, y: 0.65 },
          { x: 0.8, y: 0.65 },
          { x: 0.98, y: 0.96 },
          { x: 0.02, y: 0.96 },
        ];
    this.activeIdx = -1;
    this.hoverIdx = -1;
    this.strictClipOnly = true;
  }

  setPolygon(pts) {
    if (!Array.isArray(pts) || pts.length < 3) return;
    this.points = pts.map((pt) => ({
      x: Math.max(0, Math.min(1, Array.isArray(pt) ? pt[0] : pt.x)),
      y: Math.max(0, Math.min(1, Array.isArray(pt) ? pt[1] : pt.y)),
    }));
  }

  toQuadArray() {
    return this.points.map((pt) => [Number(pt.x.toFixed(4)), Number(pt.y.toFixed(4))]);
  }

  hitTest(nx, ny, radiusNorm = 0.022) {
    for (let i = 0; i < this.points.length; i++) {
      const dx = this.points[i].x - nx;
      const dy = this.points[i].y - ny;
      if (Math.hypot(dx, dy) <= radiusNorm) return i;
    }
    return -1;
  }

  beginDrag(nx, ny) {
    this.activeIdx = this.hitTest(nx, ny);
    return this.activeIdx !== -1;
  }

  dragTo(nx, ny) {
    if (this.activeIdx < 0 || this.activeIdx >= this.points.length) return false;
    this.points[this.activeIdx] = {
      x: Math.max(-0.1, Math.min(1.1, nx)),
      y: Math.max(-0.1, Math.min(1.1, ny)),
    };
    return true;
  }

  endDrag() {
    const changed = this.activeIdx !== -1;
    this.activeIdx = -1;
    return changed;
  }

  // Draws vector graph (edges, corner vertices, labels) on top of canvas
  drawGraph(ctx, w, h, label = "ACTIVE REGION") {
    if (!ctx || this.points.length < 3) return;
    const pxPts = this.points.map((pt) => ({ x: pt.x * w, y: pt.y * h }));

    ctx.save();
    // Translucent interior tint showing exact included area
    ctx.beginPath();
    ctx.moveTo(pxPts[0].x, pxPts[0].y);
    for (let i = 1; i < pxPts.length; i++) ctx.lineTo(pxPts[i].x, pxPts[i].y);
    ctx.closePath();
    ctx.fillStyle = "rgba(16, 185, 129, 0.10)";
    ctx.fill();

    // Vector boundary edges
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = "#10b981";
    ctx.setLineDash([7, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Corner / vertex nodes
    pxPts.forEach((pt, idx) => {
      const isHot = idx === this.activeIdx || idx === this.hoverIdx;
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, isHot ? 8 : 6, 0, Math.PI * 2);
      ctx.fillStyle = isHot ? "#facc15" : "#ffffff";
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = "#065f46";
      ctx.stroke();

      ctx.fillStyle = "#ecfdf5";
      ctx.font = "600 11px sans-serif";
      ctx.fillText(`V${idx + 1}`, pt.x + 9, pt.y - 6);
    });

    // Tag near first vertex
    ctx.fillStyle = "rgba(6, 78, 59, 0.88)";
    ctx.fillRect(pxPts[0].x, Math.max(8, pxPts[0].y - 26), 145, 20);
    ctx.fillStyle = "#ffffff";
    ctx.font = "600 11px sans-serif";
    ctx.fillText(`${label} (Drag V1-V${pxPts.length})`, pxPts[0].x + 6, Math.max(22, pxPts[0].y - 12));
    ctx.restore();
  }

  // Builds a strict binary/alpha clip canvas so material projection NEVER spills outside
  buildStrictClipCanvas(w, h, aiMaskImg = null) {
    const clipCan = document.createElement("canvas");
    clipCan.width = w;
    clipCan.height = h;
    const cctx = clipCan.getContext("2d");
    cctx.clearRect(0, 0, w, h);

    if (this.points.length >= 3) {
      cctx.save();
      cctx.beginPath();
      cctx.moveTo(this.points[0].x * w, this.points[0].y * h);
      for (let i = 1; i < this.points.length; i++) {
        cctx.lineTo(this.points[i].x * w, this.points[i].y * h);
      }
      cctx.closePath();
      cctx.fillStyle = "#ffffff";
      cctx.fill();
      cctx.restore();
    }

    // If strictClipOnly is true, polygon is the hard boundary;
    // otherwise intersect with AI mask so furniture/doors stay cut out inside the polygon.
    if (!this.strictClipOnly && aiMaskImg && aiMaskImg.complete && aiMaskImg.naturalWidth) {
      cctx.globalCompositeOperation = "destination-in";
      cctx.drawImage(aiMaskImg, 0, 0, w, h);
      cctx.globalCompositeOperation = "source-over";
    }
    return clipCan;
  }
}


// --- Canvas Pointer + AI Quad Sync + Strict Vector Clip Hook ---
const _vectorBySurface = {
  floor: new VectorRegionController([
    [0.18, 0.62],
    [0.82, 0.62],
    [1.06, 1.0],
    [-0.06, 1.0],
  ]),
  wall: new VectorRegionController([
    [0.08, 0.08],
    [0.92, 0.08],
    [0.92, 0.64],
    [0.08, 0.64],
  ]),
};
let _vectorEditEnabled = true;
let _vectorCanvasRef = null;
let _vectorRedrawFn = null;

export function getActiveVectorRegion(surface = "floor") {
  return _vectorBySurface[surface] || _vectorBySurface.floor;
}

export function setVectorEditMode(enabled) {
  _vectorEditEnabled = Boolean(enabled);
  if (_vectorRedrawFn) _vectorRedrawFn();
}

export function syncVectorPolygonsFromAnalysis(analysisData) {
  if (!analysisData) return;
  if (Array.isArray(analysisData.floorQuad) && analysisData.floorQuad.length >= 3) {
    _vectorBySurface.floor.setPolygon(analysisData.floorQuad);
  }
  if (Array.isArray(analysisData.wallQuad) && analysisData.wallQuad.length >= 3) {
    _vectorBySurface.wall.setPolygon(analysisData.wallQuad);
  }
  if (_vectorRedrawFn) _vectorRedrawFn();
}

export function applyStrictVectorClipToCanvas(targetCanvas, surface = "floor", aiMaskImg = null) {
  if (!targetCanvas) return targetCanvas;
  const ctrl = getActiveVectorRegion(surface);
  if (!ctrl || ctrl.points.length < 3) return targetCanvas;

  const w = targetCanvas.width;
  const h = targetCanvas.height;
  if (!w || !h) return targetCanvas;

  const clipCan = ctrl.buildStrictClipCanvas(w, h, aiMaskImg);
  const outCan = document.createElement("canvas");
  outCan.width = w;
  outCan.height = h;
  const octx = outCan.getContext("2d");

  octx.drawImage(targetCanvas, 0, 0);
  octx.globalCompositeOperation = "destination-in";
  octx.drawImage(clipCan, 0, 0);
  octx.globalCompositeOperation = "source-over";
  return outCan;
}

export function renderVectorGraphOverlay(mainCanvas, surface = "floor", label = null) {
  if (!mainCanvas || !_vectorEditEnabled) return;
  const ctx = mainCanvas.getContext("2d");
  if (!ctx) return;
  const ctrl = getActiveVectorRegion(surface);
  const tag = label || `${surface.toUpperCase()} VECTOR`;
  ctrl.drawGraph(ctx, mainCanvas.width, mainCanvas.height, tag);
}

export function attachVectorCanvasInteractions(canvas, getSurfaceFn, onRedrawFn) {
  if (!canvas || canvas._vectorBound) return;
  canvas._vectorBound = true;
  _vectorCanvasRef = canvas;
  _vectorRedrawFn = onRedrawFn || null;

  const toNorm = (evt) => {
    const rect = canvas.getBoundingClientRect();
    const nx = (evt.clientX - rect.left) / Math.max(1, rect.width);
    const ny = (evt.clientY - rect.top) / Math.max(1, rect.height);
    return { nx, ny };
  };

  canvas.addEventListener("pointerdown", (evt) => {
    if (!_vectorEditEnabled) return;
    const ctrl = getActiveVectorRegion(getSurfaceFn ? getSurfaceFn() : "floor");
    const { nx, ny } = toNorm(evt);
    if (ctrl.beginDrag(nx, ny)) {
      canvas.setPointerCapture?.(evt.pointerId);
      canvas.style.cursor = "grabbing";
      if (_vectorRedrawFn) _vectorRedrawFn();
    }
  });

  canvas.addEventListener("pointermove", (evt) => {
    const ctrl = getActiveVectorRegion(getSurfaceFn ? getSurfaceFn() : "floor");
    const { nx, ny } = toNorm(evt);
    if (ctrl.activeIdx !== -1) {
      if (ctrl.dragTo(nx, ny) && _vectorRedrawFn) {
        _vectorRedrawFn();
      }
      return;
    }
    const hit = _vectorEditEnabled ? ctrl.hitTest(nx, ny) : -1;
    ctrl.hoverIdx = hit;
    canvas.style.cursor = hit !== -1 ? "grab" : "default";
    if (hit !== -1 && _vectorRedrawFn) {
      _vectorRedrawFn();
    }
  });

  const finishDrag = (evt) => {
    const ctrl = getActiveVectorRegion(getSurfaceFn ? getSurfaceFn() : "floor");
    if (ctrl.endDrag()) {
      canvas.releasePointerCapture?.(evt.pointerId);
      canvas.style.cursor = "default";
      if (_vectorRedrawFn) _vectorRedrawFn();
    }
  };

  canvas.addEventListener("pointerup", finishDrag);
  canvas.addEventListener("pointercancel", finishDrag);
}


// --- Auto-Bind Vector Graph + Strict Clip to Live Photo Studio ---
(function bindLiveVectorStudio() {
  if (typeof window === "undefined" || window.__simpoloVectorLiveBound) return;
  window.__simpoloVectorLiveBound = true;

  let _strictClipFlag = true;

  function findStudioCanvas() {
    const candidates = Array.from(document.querySelectorAll("canvas"));
    if (!candidates.length) return null;
    candidates.sort((a, b) => (b.width * b.height) - (a.width * a.height));
    return candidates[0];
  }

  function findActiveSurface() {
    const activeBtn = document.querySelector("[data-surface].active, .surface-btn.active, [aria-pressed='true'][data-surface]");
    if (activeBtn && activeBtn.dataset.surface) return activeBtn.dataset.surface;
    const sel = document.querySelector("select[id*='surface' i], select[name*='surface' i]");
    if (sel && /wall/i.test(sel.value)) return "wall";
    const textMatch = Array.from(document.querySelectorAll("button, label")).find(
      (el) => /wall/i.test(el.textContent || "") && (el.classList.contains("active") || el.dataset.active === "true")
    );
    return textMatch ? "wall" : "floor";
  }

  function ensureVectorControls(canvas, onChange) {
    if (document.getElementById("simpoloVectorHud")) return;
    const hud = document.createElement("div");
    hud.id = "simpoloVectorHud";
    hud.style.cssText = [
      "position:fixed",
      "bottom:16px",
      "left:50%",
      "transform:translateX(-50%)",
      "z-index:9999",
      "display:flex",
      "gap:8px",
      "align-items:center",
      "padding:8px 12px",
      "border-radius:10px",
      "background:rgba(9,9,11,0.88)",
      "color:#f4f4f5",
      "font:600 12px/1.2 sans-serif",
      "border:1px solid rgba(255,255,255,0.16)",
      "box-shadow:0 8px 24px rgba(0,0,0,0.45)",
    ].join(";");

    const btnToggle = document.createElement("button");
    btnToggle.type = "button";
    btnToggle.textContent = "Vector Graph: ON";
    btnToggle.style.cssText = "padding:6px 10px;border-radius:6px;border:0;cursor:pointer;background:#10b981;color:#06281e;font-weight:700;";

    const btnClip = document.createElement("button");
    btnClip.type = "button";
    btnClip.textContent = "Strict Clip: ON";
    btnClip.style.cssText = "padding:6px 10px;border-radius:6px;border:1px solid rgba(255,255,255,0.22);cursor:pointer;background:#18181b;color:#f4f4f5;";

    const btnReset = document.createElement("button");
    btnReset.type = "button";
    btnReset.textContent = "Reset Corners";
    btnReset.style.cssText = "padding:6px 10px;border-radius:6px;border:1px solid rgba(255,255,255,0.22);cursor:pointer;background:#18181b;color:#f4f4f5;";

    let graphVisible = true;
    btnToggle.addEventListener("click", () => {
      graphVisible = !graphVisible;
      setVectorEditMode(graphVisible);
      btnToggle.textContent = graphVisible ? "Vector Graph: ON" : "Vector Graph: OFF";
      btnToggle.style.background = graphVisible ? "#10b981" : "#3f3f46";
      btnToggle.style.color = graphVisible ? "#06281e" : "#e4e4e7";
      onChange();
    });

    btnClip.addEventListener("click", () => {
      _strictClipFlag = !_strictClipFlag;
      const surf = findActiveSurface();
      const ctrl = getActiveVectorRegion(surf);
      if (ctrl) ctrl.strictClipOnly = _strictClipFlag;
      btnClip.textContent = _strictClipFlag ? "Strict Clip: ON" : "Strict Clip: AI+Poly";
      onChange();
    });

    btnReset.addEventListener("click", () => {
      const surf = findActiveSurface();
      const ctrl = getActiveVectorRegion(surf);
      if (ctrl) {
        ctrl.setPolygon(
          surf === "wall"
            ? [[0.08, 0.08], [0.92, 0.08], [0.92, 0.64], [0.08, 0.64]]
            : [[0.18, 0.62], [0.82, 0.62], [1.06, 1.0], [-0.06, 1.0]]
        );
      }
      onChange();
    });

    hud.append(btnToggle, btnClip, btnReset);
    document.body.appendChild(hud);
  }

  function hookAnalyzeRoomFetch() {
    if (typeof window.fetch !== "function" || window.__simpoloFetchHooked) return;
    window.__simpoloFetchHooked = true;
    const origFetch = window.fetch.bind(window);
    window.fetch = async (...args) => {
      const res = await origFetch(...args);
      const url = typeof args[0] === "string" ? args[0] : (args[0]?.url || "");
      if (url.includes("/api/analyze-room") && res.ok) {
        res.clone().json().then((data) => {
          syncVectorPolygonsFromAnalysis(data);
        }).catch(() => {});
      }
      return res;
    };
  }

  function hookCanvasOverlayLoop() {
    const canvas = findStudioCanvas();
    if (!canvas) return false;
    if (canvas.__simpoloVectorHooked) return true;
    canvas.__simpoloVectorHooked = true;

    let redrawScheduled = false;
    const scheduleOverlay = () => {
      if (redrawScheduled) return;
      redrawScheduled = true;
      requestAnimationFrame(() => {
        redrawScheduled = false;
        const surf = findActiveSurface();
        renderVectorGraphOverlay(canvas, surf);
      });
    };

    attachVectorCanvasInteractions(canvas, findActiveSurface, scheduleOverlay);
    ensureVectorControls(canvas, scheduleOverlay);

    // Draw overlay whenever canvas size changes or after UI clicks/pointer moves
    const observer = new MutationObserver(scheduleOverlay);
    observer.observe(canvas, { attributes: true, attributeFilter: ["width", "height", "style"] });
    document.addEventListener("click", () => setTimeout(scheduleOverlay, 30), true);
    setInterval(scheduleOverlay, 400);
    scheduleOverlay();
    return true;
  }

  hookAnalyzeRoomFetch();
  const bootTimer = setInterval(() => {
    if (hookCanvasOverlayLoop()) {
      clearInterval(bootTimer);
    }
  }, 250);
  setTimeout(() => clearInterval(bootTimer), 15000);
})();


// --- GLSL Fragment Shader Polygon Containment Helper (V1..V4 in [0..1] UV space) ---
export const GLSL_POLY_CLIP_SNIPPET = `
bool insidePoly4(vec2 uv, vec2 p0, vec2 p1, vec2 p2, vec2 p3) {
  vec2 poly[4];
  poly[0] = p0;
  poly[1] = p1;
  poly[2] = p2;
  poly[3] = p3;
  bool inside = false;
  int j = 3;
  for (int i = 0; i < 4; i++) {
    vec2 a = poly[i];
    vec2 b = poly[j];
    bool cond = ((a.y > uv.y) != (b.y > uv.y)) &&
                (uv.x < (b.x - a.x) * (uv.y - a.y) / max(1e-6, (b.y - a.y)) + a.x);
    if (cond) inside = !inside;
    j = i;
  }
  return inside;
}
`;

export function uploadPolyUniforms4(gl, program, points = []) {
  if (!gl || !program) return;
  const pts = (points && points.length >= 4 ? points.slice(0, 4) : [
    { x: 0.18, y: 0.62 },
    { x: 0.82, y: 0.62 },
    { x: 1.06, y: 1.0 },
    { x: -0.06, y: 1.0 },
  ]).map((pt) => [
    Array.isArray(pt) ? pt[0] : pt.x,
    Array.isArray(pt) ? pt[1] : pt.y,
  ]);

  const flat = new Float32Array(pts.flat());
  const loc = gl.getUniformLocation(program, "uPolyPts[0]") || gl.getUniformLocation(program, "uPolyPts");
  if (loc) {
    gl.uniform2fv(loc, flat);
  }
}

// Strict polygon clip for any 2D/WebGL output canvas right before compositing onto main view
export function clipCanvasToDraggedPolygon(sourceCanvas, surface = "floor", aiMaskImg = null) {
  if (!sourceCanvas || !sourceCanvas.width || !sourceCanvas.height) return sourceCanvas;
  const ctrl = typeof getActiveVectorRegion === "function" ? getActiveVectorRegion(surface) : null;
  if (!ctrl || !Array.isArray(ctrl.points) || ctrl.points.length < 3) return sourceCanvas;

  const w = sourceCanvas.width;
  const h = sourceCanvas.height;
  const out = document.createElement("canvas");
  out.width = w;
  out.height = h;
  const octx = out.getContext("2d");

  octx.save();
  octx.beginPath();
  octx.moveTo(ctrl.points[0].x * w, ctrl.points[0].y * h);
  for (let i = 1; i < ctrl.points.length; i++) {
    octx.lineTo(ctrl.points[i].x * w, ctrl.points[i].y * h);
  }
  octx.closePath();
  octx.clip();
  octx.drawImage(sourceCanvas, 0, 0, w, h);
  octx.restore();

  if (ctrl.strictClipOnly === false && aiMaskImg && aiMaskImg.complete && aiMaskImg.naturalWidth) {
    octx.globalCompositeOperation = "destination-in";
    octx.drawImage(aiMaskImg, 0, 0, w, h);
    octx.globalCompositeOperation = "source-over";
  }
  return out;
}


// --- Dedicated 2D Overlay Canvas Strictly for My Room Photo (AI) ---
(function installPhotoAiOnlyOverlay() {
  if (typeof window === "undefined") return;

  function isElementVisible(el) {
    if (!el) return false;
    const style = getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || parseFloat(style.opacity) === 0) {
      return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 80 && rect.height > 80;
  }

  function findPhotoAiCanvas() {
    // Look for a visible canvas inside a container associated with Room Photo / Photo Studio
    const all = Array.from(document.querySelectorAll("canvas")).filter(
      (c) => c.id !== "simpoloVectorOverlayCanvas" && isElementVisible(c)
    );
    if (!all.length) return null;

    // Prefer a canvas inside a section/panel mentioning "photo" or "room photo" and NOT "3d"
    const scored = all.map((c) => {
      let score = 0;
      let cur = c;
      for (let depth = 0; depth < 6 && cur; depth++) {
        const txt = ((cur.id || "") + " " + (cur.className || "") + " " + (cur.dataset?.view || "") + " " + (cur.dataset?.mode || "")).toLowerCase();
        const headingText = (cur.textContent || "").slice(0, 240).toLowerCase();
        if (/photo|upload room|split compare|mask brush/.test(txt) || /my room photo|split compare|mask brush/.test(headingText)) {
          score += 10;
        }
        if (/3d\s*view|threejs|orbit|babylon/.test(txt)) {
          score -= 10;
        }
        cur = cur.parentElement;
      }
      const r = c.getBoundingClientRect();
      return { canvas: c, score, area: r.width * r.height };
    });

    scored.sort((a, b) => (b.score - a.score) || (b.area - a.area));
    // Only return if it clearly belongs to Photo AI (score > 0), otherwise null so 3D view stays clean
    return scored[0] && scored[0].score > 0 ? scored[0].canvas : null;
  }

  function removeOverlayIfInactive() {
    const ov = document.getElementById("simpoloVectorOverlayCanvas");
    if (ov) ov.style.display = "none";
  }

  function ensureOverlayCanvas(roomCanvas) {
    let ov = document.getElementById("simpoloVectorOverlayCanvas");
    const rect = roomCanvas.getBoundingClientRect();
    const parent = roomCanvas.parentElement;
    if (!parent || rect.width < 40 || rect.height < 40) return null;

    const pStyle = getComputedStyle(parent);
    if (pStyle.position === "static") {
      parent.style.position = "relative";
    }

    if (!ov) {
      ov = document.createElement("canvas");
      ov.id = "simpoloVectorOverlayCanvas";
      ov.style.position = "absolute";
      ov.style.pointerEvents = "none";
      ov.style.zIndex = "25";
      parent.appendChild(ov);
    }

    ov.style.display = "block";
    const dpr = window.devicePixelRatio || 1;
    const cssW = Math.round(rect.width);
    const cssH = Math.round(rect.height);
    const left = roomCanvas.offsetLeft;
    const top = roomCanvas.offsetTop;

    ov.style.left = `${left}px`;
    ov.style.top = `${top}px`;
    ov.style.width = `${cssW}px`;
    ov.style.height = `${cssH}px`;

    if (ov.width !== Math.round(cssW * dpr) || ov.height !== Math.round(cssH * dpr)) {
      ov.width = Math.round(cssW * dpr);
      ov.height = Math.round(cssH * dpr);
    }
    return ov;
  }

  function drawOverlayNow() {
    const roomCanvas = findPhotoAiCanvas();
    if (!roomCanvas) {
      removeOverlayIfInactive();
      return;
    }
    const ov = ensureOverlayCanvas(roomCanvas);
    if (!ov) return;
    const ctx = ov.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, ov.width, ov.height);

    const hudBtn = document.querySelector("#simpoloVectorHud button");
    const isOff = hudBtn && /OFF/i.test(hudBtn.textContent || "");
    if (isOff) return;

    const isWall = Array.from(document.querySelectorAll("button, div, span")).some(
      (el) => el.children.length === 0 && /target:\s*wall/i.test(el.textContent || "")
    );
    const surface = isWall ? "wall" : "floor";
    const ctrl = typeof getActiveVectorRegion === "function" ? getActiveVectorRegion(surface) : null;
    if (!ctrl || !Array.isArray(ctrl.points) || ctrl.points.length < 3) return;

    const w = ov.width;
    const h = ov.height;
    const pts = ctrl.points.map((pt) => ({ x: pt.x * w, y: pt.y * h }));

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
    ctx.closePath();
    ctx.fillStyle = "rgba(16, 185, 129, 0.14)";
    ctx.fill();

    ctx.lineWidth = Math.max(2.5, w * 0.003);
    ctx.strokeStyle = "#10b981";
    ctx.setLineDash([10, 6]);
    ctx.stroke();
    ctx.setLineDash([]);

    pts.forEach((pt, idx) => {
      const r = Math.max(7, w * 0.008);
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, r, 0, Math.PI * 2);
      ctx.fillStyle = idx === ctrl.activeIdx ? "#facc15" : "#ffffff";
      ctx.fill();
      ctx.lineWidth = 3;
      ctx.strokeStyle = "#064e3b";
      ctx.stroke();

      ctx.font = `700 ${Math.max(12, Math.round(w * 0.014))}px sans-serif`;
      ctx.fillStyle = "#064e3b";
      ctx.fillText(`V${idx + 1}`, pt.x + r + 5, pt.y - 3);
      ctx.fillStyle = "#ffffff";
      ctx.fillText(`V${idx + 1}`, pt.x + r + 4, pt.y - 4);
    });

    const lx = Math.max(12, pts[0].x);
    const ly = Math.max(28, pts[0].y - 14);
    ctx.fillStyle = "rgba(6, 78, 59, 0.92)";
    ctx.fillRect(lx, ly - 16, 200, 22);
    ctx.fillStyle = "#ffffff";
    ctx.font = "700 12px sans-serif";
    ctx.fillText(`${surface.toUpperCase()} VECTOR (Drag V1-V4)`, lx + 8, ly - 1);
    ctx.restore();
  }

  function bindDragging() {
    if (window.__simpoloOverlayDragBound) return;
    window.__simpoloOverlayDragBound = true;

    document.addEventListener("pointerdown", (e) => {
      const roomCanvas = findPhotoAiCanvas();
      if (!roomCanvas) return;
      const rect = roomCanvas.getBoundingClientRect();
      if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) return;

      const isWall = Array.from(document.querySelectorAll("button, div, span")).some(
        (el) => el.children.length === 0 && /target:\s*wall/i.test(el.textContent || "")
      );
      const ctrl = typeof getActiveVectorRegion === "function" ? getActiveVectorRegion(isWall ? "wall" : "floor") : null;
      if (!ctrl) return;

      const nx = (e.clientX - rect.left) / Math.max(1, rect.width);
      const ny = (e.clientY - rect.top) / Math.max(1, rect.height);
      if (ctrl.beginDrag(nx, ny, 0.035)) {
        e.stopPropagation();
        drawOverlayNow();
      }
    }, true);

    document.addEventListener("pointermove", (e) => {
      const roomCanvas = findPhotoAiCanvas();
      if (!roomCanvas) return;
      const isWall = Array.from(document.querySelectorAll("button, div, span")).some(
        (el) => el.children.length === 0 && /target:\s*wall/i.test(el.textContent || "")
      );
      const ctrl = typeof getActiveVectorRegion === "function" ? getActiveVectorRegion(isWall ? "wall" : "floor") : null;
      if (!ctrl || ctrl.activeIdx === -1) return;

      const rect = roomCanvas.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / Math.max(1, rect.width);
      const ny = (e.clientY - rect.top) / Math.max(1, rect.height);
      if (ctrl.dragTo(nx, ny)) {
        e.stopPropagation();
        drawOverlayNow();
      }
    }, true);

    const stopDrag = () => {
      const ctrl = typeof getActiveVectorRegion === "function" ? getActiveVectorRegion("floor") : null;
      const ctrlW = typeof getActiveVectorRegion === "function" ? getActiveVectorRegion("wall") : null;
      if (ctrl) ctrl.endDrag();
      if (ctrlW) ctrlW.endDrag();
      drawOverlayNow();
    };
    document.addEventListener("pointerup", stopDrag, true);
    document.addEventListener("pointercancel", stopDrag, true);
  }

  bindDragging();
  setInterval(drawOverlayNow, 150);
  window.addEventListener("resize", drawOverlayNow);
})();
