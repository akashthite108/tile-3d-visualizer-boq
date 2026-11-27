from pathlib import Path

p = Path("web_prototype/photo_studio.mjs")
src = p.read_text(encoding="utf-8")

shader_clip_block = """
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
"""

if "GLSL_POLY_CLIP_SNIPPET" not in src:
    src = src + "\n" + shader_clip_block

p.write_text(src, encoding="utf-8")
print("Added GLSL polygon clip snippet and strict polygon compositor to photo_studio.mjs")