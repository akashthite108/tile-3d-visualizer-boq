import base64
import io
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from ai_geometry import analyze_room_layout, estimate_depth_map

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web_prototype"

app = FastAPI(title="Simpolo AI Room Visualizer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_AI_STATE = {"loaded": False, "available": False, "error": None, "processor": None, "model": None, "device": "cpu"}


def load_segformer():
    if _AI_STATE["loaded"]:
        return _AI_STATE["available"]
    _AI_STATE["loaded"] = True
    try:
        import torch
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor

        model_id = "nvidia/segformer-b0-finetuned-ade-512-512"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[AI] Loading {model_id} on {device}...")
        processor = SegformerImageProcessor.from_pretrained(model_id)
        model = SegformerForSemanticSegmentation.from_pretrained(model_id).to(device)
        model.eval()
        _AI_STATE.update(
            {"available": True, "processor": processor, "model": model, "device": device, "error": None}
        )
        print(f"[AI] SegFormer ready on {device}.")
        return True
    except Exception as exc:
        _AI_STATE["available"] = False
        _AI_STATE["error"] = str(exc)
        print(f"[AI] SegFormer unavailable ({exc}). Using geometric fallback + real shadow extraction.")
        return False


def mask_to_png_data_url(mask_u8: np.ndarray) -> str:
    ok, buf = cv2.imencode(".png", mask_u8)
    if not ok:
        raise RuntimeError("PNG encode failed")
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode("ascii")


def clean_mask(binary_u8: np.ndarray, feather_px: int = 5) -> np.ndarray:
    h, w = binary_u8.shape
    k = max(3, int(min(h, w) * 0.008) | 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    cleaned = cv2.morphologyEx(binary_u8, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    if feather_px > 1:
        f = feather_px | 1
        cleaned = cv2.GaussianBlur(cleaned, (f, f), 0)
    return cleaned


def estimate_perspective_quad(mask_u8: np.ndarray, is_floor: bool) -> list[list[float]]:
    h, w = mask_u8.shape
    ys, xs = np.where(mask_u8 > 128)
    if xs.size < (h * w * 0.01):
        if is_floor:
            return [[0.22, 0.62], [0.78, 0.62], [1.05, 1.00], [-0.05, 1.00]]
        return [[0.10, 0.08], [0.90, 0.08], [0.90, 0.64], [0.10, 0.64]]

    y_top = float(np.percentile(ys, 2))
    y_bot = float(np.percentile(ys, 98))
    span_y = max(10.0, y_bot - y_top)

    top_band = xs[ys <= y_top + 0.16 * span_y]
    bot_band = xs[ys >= y_bot - 0.16 * span_y]
    if top_band.size < 10:
        top_band = xs
    if bot_band.size < 10:
        bot_band = xs

    x_tl = float(np.percentile(top_band, 4)) / w
    x_tr = float(np.percentile(top_band, 96)) / w
    x_bl = float(np.percentile(bot_band, 2)) / w
    x_br = float(np.percentile(bot_band, 98)) / w
    yt = y_top / h
    yb = y_bot / h

    if is_floor:
        top_w = max(0.18, x_tr - x_tl)
        bot_w = max(top_w * 1.25, x_br - x_bl)
        cx_bot = (x_bl + x_br) * 0.5
        x_bl = min(x_bl, cx_bot - bot_w * 0.5)
        x_br = max(x_br, cx_bot + bot_w * 0.5)
        return [
            [round(x_tl, 4), round(yt, 4)],
            [round(x_tr, 4), round(yt, 4)],
            [round(x_br, 4), round(yb, 4)],
            [round(x_bl, 4), round(yb, 4)],
        ]

    x_left = min(x_tl, x_bl)
    x_right = max(x_tr, x_br)
    return [
        [round(x_left, 4), round(yt, 4)],
        [round(x_right, 4), round(yt, 4)],
        [round(x_right, 4), round(yb, 4)],
        [round(x_left, 4), round(yb, 4)],
    ]


def extract_shadow_map(rgb_np: np.ndarray, floor_mask: np.ndarray, wall_mask: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2LAB)
    l_ch = lab[:, :, 0].astype(np.float32)
    l_smooth = cv2.bilateralFilter(l_ch, d=9, sigmaColor=24, sigmaSpace=24)

    ratio = np.ones_like(l_smooth, dtype=np.float32)
    combined = np.maximum(floor_mask, wall_mask)

    for mask in (floor_mask, wall_mask):
        idx = mask > 128
        if np.count_nonzero(idx) > 200:
            med = float(np.median(l_smooth[idx]))
            reg_ratio = l_smooth / max(med, 28.0)
            ratio = np.where(idx, reg_ratio, ratio)

    if np.count_nonzero(combined > 128) <= 200:
        med = float(np.median(l_smooth))
        ratio = l_smooth / max(med, 28.0)

    ratio = np.clip(ratio, 0.25, 1.75)
    return np.clip(ratio * 128.0, 0, 255).astype(np.uint8)


def run_segmentation(pil_img: Image.Image) -> tuple[np.ndarray, np.ndarray, str]:
    w, h = pil_img.size
    if load_segformer():
        import torch
        import torch.nn.functional as F

        processor = _AI_STATE["processor"]
        model = _AI_STATE["model"]
        device = _AI_STATE["device"]

        inputs = processor(images=pil_img, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = F.interpolate(outputs.logits, size=(h, w), mode="bilinear", align_corners=False)
            pred = logits.argmax(dim=1)[0].cpu().numpy()

        id2label = {int(k): str(v).lower() for k, v in model.config.id2label.items()}
        floor_ids = [
            cid for cid, name in id2label.items()
            if any(tok in name for tok in ("floor", "sidewalk", "patio", "pavement", "ground"))
            and "rug" not in name and "carpet" not in name
        ]
        wall_ids = [
            cid for cid, name in id2label.items()
            if any(tok in name for tok in ("wall", "column", "pillar"))
        ]

        floor_bin = np.isin(pred, floor_ids).astype(np.uint8) * 255
        wall_bin = np.isin(pred, wall_ids).astype(np.uint8) * 255
        obs_ids = [cid for cid, name in id2label.items() if any(tok in name for tok in ("sofa", "couch", "chair", "armchair", "table", "desk", "bed", "cabinet", "wardrobe", "shelf", "door", "window", "curtain", "rug", "carpet", "ottoman", "stool", "bench", "refrigerator", "sink", "toilet"))]
        obs_bin = np.isin(pred, obs_ids).astype(np.uint8) * 255
        ceil_ids = [cid for cid, name in id2label.items() if "ceiling" in name]
        ceil_bin = np.isin(pred, ceil_ids).astype(np.uint8) * 255
        try:
            depth_m = estimate_depth_map(pil_img)
            layout = analyze_room_layout(
                clean_mask(floor_bin, 3),
                clean_mask(wall_bin, 3),
                clean_mask(ceil_bin, 3),
                obs_bin,
                depth_m,
            )
            _AI_STATE["last_layout"] = {
                "areasM2": layout["areasM2"],
                "areasSqFt": layout["areasSqFt"],
                "corners2d": layout["corners2d"],
                "sideWallMask": mask_to_png_data_url(layout["sideWallMask"]),
                "ceilingMask": mask_to_png_data_url(layout["ceilingMask"]),
                "ceilingQuad": layout["ceilingQuad"],
                "barrierMask": mask_to_png_data_url(layout["barrierMask"]) if layout.get("barrierMask") is not None else None,
            }
            return (
                layout["floorMask"],
                layout["wallMask"],
                layout["floorQuad"],
                layout["wallQuad"],
                f"segformer+depth+3d-layout ({device})",
            )
        except Exception as geo_err:
            print(f"[AI] Geometry fallback ({geo_err})")
            f_m = clean_mask(floor_bin, 5)
            w_m = clean_mask(wall_bin, 5)
            _AI_STATE["last_layout"] = {}
            return f_m, w_m, estimate_perspective_quad(f_m, True), estimate_perspective_quad(w_m, False), f"segformer ({device})"

    floor_bin = np.zeros((h, w), dtype=np.uint8)
    wall_bin = np.zeros((h, w), dtype=np.uint8)
    pts_floor = np.array([[int(w * 0.2), int(h * 0.62)], [int(w * 0.8), int(h * 0.62)], [w, h], [0, h]])
    cv2.fillPoly(floor_bin, [pts_floor], 255)
    cv2.rectangle(wall_bin, (int(w * 0.08), int(h * 0.06)), (int(w * 0.92), int(h * 0.62)), 255, -1)
    return clean_mask(floor_bin, 5), clean_mask(wall_bin, 5), "fallback-geometry"


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "aiLoaded": _AI_STATE["loaded"],
        "aiAvailable": _AI_STATE["available"],
        "device": _AI_STATE["device"],
        "error": _AI_STATE["error"],
    }


@app.post("/api/analyze-room")
async def analyze_room(file: UploadFile = File(...)):
    raw = await file.read()
    pil = Image.open(io.BytesIO(raw)).convert("RGB")

    max_side = 1440
    if max(pil.size) > max_side:
        pil.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    rgb_np = np.array(pil)
    h, w = rgb_np.shape[:2]

    floor_mask, wall_mask, floor_quad, wall_quad, engine = run_segmentation(pil)
    shadow_map = extract_shadow_map(rgb_np, floor_mask, wall_mask)

    floor_cov = float(np.count_nonzero(floor_mask > 128)) / float(w * h)
    wall_cov = float(np.count_nonzero(wall_mask > 128)) / float(w * h)

    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=92)
    photo_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    return {
        "width": w,
        "height": h,
        "engine": engine,
        "photoUrl": photo_url,
        "floorMask": mask_to_png_data_url(floor_mask),
        "wallMask": mask_to_png_data_url(wall_mask),
        "shadowMap": mask_to_png_data_url(shadow_map),
        "floorQuad": floor_quad,
        "wallQuad": wall_quad,
        "floorCoveragePct": round(floor_cov * 100, 1),
        "wallCoveragePct": round(wall_cov * 100, 1),
        "layout": _AI_STATE.get("last_layout", {}),
    }


app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    print(f"Serving Simpolo AI Studio from: {WEB_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
