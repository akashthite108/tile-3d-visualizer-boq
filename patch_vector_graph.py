from pathlib import Path

p = Path("web_prototype/photo_studio.mjs")
src = p.read_text(encoding="utf-8")

vector_block = """
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
"""

if "VectorRegionController" not in src:
    src = src + "\n" + vector_block

p.write_text(src, encoding="utf-8")
print("Added VectorRegionController to photo_studio.mjs")