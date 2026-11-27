from pathlib import Path

p = Path("web_prototype/photo_studio.mjs")
src = p.read_text(encoding="utf-8")

overlay_fix = """
// --- Dedicated 2D Overlay Canvas Above WebGL Room Canvas ---
(function installDedicatedVectorOverlay() {
  if (typeof window === "undefined") return;

  function getRoomCanvas() {
    const all = Array.from(document.querySelectorAll("canvas")).filter(
      (c) => c.id !== "simpoloVectorOverlayCanvas"
    );
    if (!all.length) return null;
    all.sort((a, b) => b.getBoundingClientRect().width * b.getBoundingClientRect().height - a.getBoundingClientRect().width * a.getBoundingClientRect().height);
    return all[0];
  }

  function ensureOverlayCanvas(roomCanvas) {
    let ov = document.getElementById("simpoloVectorOverlayCanvas");
    const rect = roomCanvas.getBoundingClientRect();
    const parent = roomCanvas.parentElement;
    if (!parent || rect.width < 20 || rect.height < 20) return null;

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
    const roomCanvas = getRoomCanvas();
    if (!roomCanvas) return;
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
    ctx.fillRect(lx, ly - 16, 190, 22);
    ctx.fillStyle = "#ffffff";
    ctx.font = "700 12px sans-serif";
    ctx.fillText(`${surface.toUpperCase()} VECTOR (Drag V1-V4)`, lx + 8, ly - 1);
    ctx.restore();
  }

  function bindDragging() {
    if (window.__simpoloOverlayDragBound) return;
    window.__simpoloOverlayDragBound = true;

    document.addEventListener("pointerdown", (e) => {
      const roomCanvas = getRoomCanvas();
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
      const roomCanvas = getRoomCanvas();
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
"""

if "installDedicatedVectorOverlay" not in src:
    p.write_text(src + "\n" + overlay_fix, encoding="utf-8")
    print("Installed dedicated transparent overlay canvas for V1-V4")