import cv2
import numpy as np
from PIL import Image

_DEPTH_STATE = {"loaded": False, "available": False, "pipe": None, "error": None}
SQFT_PER_SQM = 10.7639104


def load_depth_model():
    if _DEPTH_STATE["loaded"]:
        return _DEPTH_STATE["available"]
    _DEPTH_STATE["loaded"] = True
    try:
        import torch
        from transformers import pipeline

        device = 0 if torch.cuda.is_available() else -1
        pipe = pipeline(
            task="depth-estimation",
            model="depth-anything/Depth-Anything-V2-Small-hf",
            device=device,
        )
        _DEPTH_STATE.update({"available": True, "pipe": pipe, "error": None})
        return True
    except Exception as exc:
        _DEPTH_STATE.update({"available": False, "error": str(exc)})
        return False


def estimate_depth_map(pil_img: Image.Image) -> np.ndarray | None:
    if not load_depth_model():
        return None
    w, h = pil_img.size
    probe = pil_img.copy()
    probe.thumbnail((518, 518), Image.Resampling.BILINEAR)
    out = _DEPTH_STATE["pipe"](probe)
    depth = np.asarray(out["depth"], dtype=np.float32)
    depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_CUBIC)
    d_min, d_max = float(np.percentile(depth, 2)), float(np.percentile(depth, 98))
    span = max(1e-4, d_max - d_min)
    norm = np.clip((depth - d_min) / span, 0.0, 1.0)
    return 0.8 + norm * 4.2


def backproject_normals(depth_rel: np.ndarray):
    h, w = depth_rel.shape
    fx = fy = 0.85 * max(w, h)
    cx, cy = w * 0.5, h * 0.5

    u, v = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    z = depth_rel
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    pts = np.stack([x, y, z], axis=-1)

    dz_dx = cv2.Sobel(z, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    dz_dy = cv2.Sobel(z, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    tx = np.stack([z / fx, np.zeros_like(z), dz_dx], axis=-1)
    ty = np.stack([np.zeros_like(z), z / fy, dz_dy], axis=-1)
    normals = np.cross(tx, ty)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True) + 1e-6
    return pts, normals, fx, fy, cx, cy


def _plane_area_m2(mask_u8: np.ndarray, pts: np.ndarray, normals: np.ndarray, fx: float, fy: float, scale_m: float):
    idx = mask_u8 > 128
    if np.count_nonzero(idx) < 10:
        return 0.0
    z_m = pts[idx, 2] * scale_m
    n_m = normals[idx]
    ray = pts[idx] / (np.linalg.norm(pts[idx], axis=-1, keepdims=True) + 1e-6)
    cos_theta = np.clip(np.abs(np.sum(n_m * ray, axis=-1)), 0.35, 1.0)
    px_area = ((z_m ** 2) / (fx * fy)) / cos_theta
    return round(float(np.sum(px_area)), 2)


def _quad_from_mask(mask_u8: np.ndarray, is_floor: bool, is_ceiling: bool = False):
    h, w = mask_u8.shape
    ys, xs = np.where(mask_u8 > 110)
    if xs.size < (h * w * 0.008):
        if is_floor:
            return [[0.18, 0.62], [0.82, 0.62], [1.06, 1.00], [-0.06, 1.00]]
        if is_ceiling:
            return [[0.14, 0.00], [0.86, 0.00], [0.92, 0.24], [0.08, 0.24]]
        return [[0.08, 0.08], [0.92, 0.08], [0.92, 0.64], [0.08, 0.64]]

    y_top = float(np.percentile(ys, 3)) / h
    y_bot = float(np.percentile(ys, 98)) / h
    span_px = max(8.0, (y_bot - y_top) * h)
    top_xs = xs[ys <= (y_top * h + 0.18 * span_px)]
    bot_xs = xs[ys >= (y_bot * h - 0.18 * span_px)]
    if top_xs.size < 8:
        top_xs = xs
    if bot_xs.size < 8:
        bot_xs = xs

    x_tl = float(np.percentile(top_xs, 5)) / w
    x_tr = float(np.percentile(top_xs, 95)) / w
    x_bl = float(np.percentile(bot_xs, 2)) / w
    x_br = float(np.percentile(bot_xs, 98)) / w

    if is_floor:
        top_w = max(0.20, x_tr - x_tl)
        bot_w = max(top_w * 1.25, x_br - x_bl)
        cx_b = 0.5 * (x_bl + x_br)
        return [
            [round(x_tl, 4), round(y_top, 4)],
            [round(x_tr, 4), round(y_top, 4)],
            [round(max(x_br, cx_b + 0.5 * bot_w), 4), round(y_bot, 4)],
            [round(min(x_bl, cx_b - 0.5 * bot_w), 4), round(y_bot, 4)],
        ]

    xl = min(x_tl, x_bl)
    xr = max(x_tr, x_br)
    return [
        [round(xl, 4), round(y_top, 4)],
        [round(xr, 4), round(y_top, 4)],
        [round(xr, 4), round(y_bot, 4)],
        [round(xl, 4), round(y_bot, 4)],
    ]


def _edge_and_corner_sketch(gray_u8: np.ndarray, obs_u8: np.ndarray):
    """Detects structural edges, line segments, and corners to act as paint barriers."""
    h, w = gray_u8.shape
    denoised = cv2.bilateralFilter(gray_u8, d=7, sigmaColor=35, sigmaSpace=35)
    edges = cv2.Canny(denoised, threshold1=45, threshold2=130, apertureSize=3)

    # Strengthen straight architectural lines (baseboards, wall-ceiling lines, door frames)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    lines, _, _, _ = lsd.detect(denoised)
    line_img = np.zeros((h, w), dtype=np.uint8)
    if lines is not None:
        for seg in lines:
            x1, y1, x2, y2 = seg[0]
            if np.hypot(x2 - x1, y2 - y1) > min(h, w) * 0.08:
                cv2.line(
                    line_img,
                    (int(round(x1)), int(round(y1))),
                    (int(round(x2)), int(round(y2))),
                    255,
                    2,
                )

    # Detect corner keypoints
    corners_pts = cv2.goodFeaturesToTrack(
        denoised, maxCorners=120, qualityLevel=0.02, minDistance=max(10, int(min(h, w) * 0.03))
    )
    corners_2d = []
    if corners_pts is not None:
        for pt in corners_pts:
            cx_i, cy_i = float(pt[0][0]), float(pt[0][1])
            corners_2d.append([round(cx_i / w, 4), round(cy_i / h, 4)])

    # Combine edges, structural lines, and obstacle boundaries into a hard barrier
    obs_edge = cv2.Canny((obs_u8 > 128).astype(np.uint8) * 255, 50, 150)
    barrier = cv2.bitwise_or(edges, line_img)
    barrier = cv2.bitwise_or(barrier, obs_edge)
    barrier = cv2.dilate(barrier, np.ones((2, 2), np.uint8), iterations=1)
    return barrier, corners_2d


def _snap_region_to_edges(prior_u8: np.ndarray, barrier_u8: np.ndarray, obs_u8: np.ndarray) -> np.ndarray:
    """Keeps interior predictions and snaps outer edges cleanly to structural barriers without spilling."""
    h, w = prior_u8.shape
    obs_block = cv2.dilate((obs_u8 > 128).astype(np.uint8) * 255, np.ones((5, 5), np.uint8), iterations=1)
    allowed = (obs_block == 0).astype(np.uint8)

    seed = ((prior_u8 > 140) & (allowed > 0)).astype(np.uint8)
    if np.count_nonzero(seed) < 25:
        return np.where(allowed > 0, prior_u8, 0).astype(np.uint8)

    # Expand slightly into open space while stopping at strong edges/corners & obstacles
    open_space = ((barrier_u8 == 0) & (allowed > 0)).astype(np.uint8)
    grown = cv2.dilate(seed, np.ones((5, 5), np.uint8), iterations=2)
    bounded = np.where((grown > 0) & ((prior_u8 > 95) | (open_space > 0)), 255, 0).astype(np.uint8)
    bounded = np.where(allowed > 0, bounded, 0).astype(np.uint8)

    # Crisp edge mask (minimal blur so corners/lines stay sharp)
    return cv2.GaussianBlur(bounded, (3, 3), 0)


def analyze_room_layout(
    floor_prior_u8: np.ndarray,
    wall_prior_u8: np.ndarray,
    ceiling_prior_u8: np.ndarray,
    obstacle_u8: np.ndarray,
    depth_rel: np.ndarray | None,
    known_width_m: float = 4.8,
    rgb_u8: np.ndarray | None = None,
):
    h, w = floor_prior_u8.shape
    if rgb_u8 is not None and rgb_u8.shape[:2] == (h, w):
        gray = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2GRAY)
    else:
        gray = np.maximum.reduce([floor_prior_u8, wall_prior_u8, ceiling_prior_u8])

    barrier_u8, corners_2d = _edge_and_corner_sketch(gray, obstacle_u8)

    floor_clean_u8 = _snap_region_to_edges(floor_prior_u8, barrier_u8, obstacle_u8)
    wall_clean_u8 = _snap_region_to_edges(wall_prior_u8, barrier_u8, obstacle_u8)
    ceil_clean_u8 = _snap_region_to_edges(ceiling_prior_u8, barrier_u8, obstacle_u8)

    # Strict mutual exclusivity: never paint both floor and wall or over obstacles
    both = (floor_clean_u8 > 128) & (wall_clean_u8 > 128)
    floor_clean_u8 = np.where(both & (floor_clean_u8 < wall_clean_u8), 0, floor_clean_u8).astype(np.uint8)
    wall_clean_u8 = np.where(both & (wall_clean_u8 <= floor_clean_u8), 0, wall_clean_u8).astype(np.uint8)

    side_wall_u8 = np.zeros((h, w), dtype=np.uint8)
    areas_m2 = {"floor": 0.0, "wall": 0.0, "sideWall": 0.0, "ceiling": 0.0}
    areas_sqft = {"floor": 0.0, "wall": 0.0, "sideWall": 0.0, "ceiling": 0.0}

    if depth_rel is not None:
        pts, normals, fx, fy, cx, cy = backproject_normals(depth_rel)
        span_rel_x = max(0.35, float(np.percentile(pts[:, :, 0], 90) - np.percentile(pts[:, :, 0], 10)))
        scale_m = known_width_m / span_rel_x

        areas_m2["floor"] = _plane_area_m2(floor_clean_u8, pts, normals, fx, fy, scale_m)
        areas_m2["wall"] = _plane_area_m2(wall_clean_u8, pts, normals, fx, fy, scale_m)
        areas_m2["ceiling"] = _plane_area_m2(ceil_clean_u8, pts, normals, fx, fy, scale_m)

        wys, wxs = np.where(wall_clean_u8 > 128)
        if wxs.size > 40:
            side_sel = np.abs(normals[wys, wxs, 0]) > 0.52
            sw_raw = np.zeros((h, w), dtype=np.uint8)
            sw_raw[wys[side_sel], wxs[side_sel]] = 255
            side_wall_u8 = _snap_region_to_edges(sw_raw, barrier_u8, obstacle_u8)
            areas_m2["sideWall"] = _plane_area_m2(side_wall_u8, pts, normals, fx, fy, scale_m)

    for k, val in areas_m2.items():
        areas_sqft[k] = round(val * SQFT_PER_SQM, 1)

    return {
        "floorMask": floor_clean_u8,
        "wallMask": wall_clean_u8,
        "sideWallMask": side_wall_u8,
        "ceilingMask": ceil_clean_u8,
        "barrierMask": barrier_u8,
        "floorQuad": _quad_from_mask(floor_clean_u8, is_floor=True),
        "wallQuad": _quad_from_mask(wall_clean_u8, is_floor=False),
        "ceilingQuad": _quad_from_mask(ceil_clean_u8, is_floor=False, is_ceiling=True),
        "corners2d": corners_2d,
        "areasM2": areas_m2,
        "areasSqFt": areas_sqft,
    }