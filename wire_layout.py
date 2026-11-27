from pathlib import Path

p = Path("server.py")
txt = p.read_text(encoding="utf-8")

txt = txt.replace(
    "from ai_geometry import estimate_depth_map, refine_masks_with_geometry",
    "from ai_geometry import analyze_room_layout, estimate_depth_map",
)

old_call = """        try:
            depth_m = estimate_depth_map(pil_img)
            f_m, w_m, f_q, w_q = refine_masks_with_geometry(clean_mask(floor_bin, 3), clean_mask(wall_bin, 3), obs_bin, depth_m)
        except Exception as geo_err:
            print(f'[AI] Geometry fallback ({geo_err})')
            f_m = clean_mask(floor_bin, 5)
            w_m = clean_mask(wall_bin, 5)
            f_q = estimate_perspective_quad(f_m, True)
            w_q = estimate_perspective_quad(w_m, False)
        return f_m, w_m, f_q, w_q, f"segformer+depth+3d-plane ({device})\""""

new_call = """        ceil_ids = [cid for cid, name in id2label.items() if "ceiling" in name]
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
            return f_m, w_m, estimate_perspective_quad(f_m, True), estimate_perspective_quad(w_m, False), f"segformer ({device})\""""

if old_call in txt:
    txt = txt.replace(old_call, new_call, 1)

old_ret = """        "floorCoveragePct": round(floor_cov * 100, 1),
        "wallCoveragePct": round(wall_cov * 100, 1),
    }"""

new_ret = """        "floorCoveragePct": round(floor_cov * 100, 1),
        "wallCoveragePct": round(wall_cov * 100, 1),
        "layout": _AI_STATE.get("last_layout", {}),
    }"""

if old_ret in txt:
    txt = txt.replace(old_ret, new_ret, 1)

p.write_text(txt, encoding="utf-8")
print("Wired analyze_room_layout into server.py")