from pathlib import Path

p = Path("web_prototype/photo_studio.mjs")
src = p.read_text(encoding="utf-8")

hook_code = """
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
"""

if "attachVectorCanvasInteractions" not in src:
    src = src + "\n" + hook_code

p.write_text(src, encoding="utf-8")
print("Wired canvas pointer + strict vector clip helpers into photo_studio.mjs")