from pathlib import Path

p = Path("web_prototype/photo_studio.mjs")
src = p.read_text(encoding="utf-8")

helper_code = """
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
"""

if "renderScanPreview" not in src:
    src = src + "\n" + helper_code

p.write_text(src, encoding="utf-8")
print("Added scan preview helpers to photo_studio.mjs")