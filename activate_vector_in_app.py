from pathlib import Path

p = Path("web_prototype/photo_studio.mjs")
src = p.read_text(encoding="utf-8")

activation_block = """
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
"""

if "bindLiveVectorStudio" not in src:
    p.write_text(src + "\n" + activation_block, encoding="utf-8")
    print("Activated live Vector Graph UI and canvas hooks in photo_studio.mjs")
else:
    print("bindLiveVectorStudio already present in photo_studio.mjs")