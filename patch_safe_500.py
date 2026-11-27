from pathlib import Path

p = Path("server.py")
txt = p.read_text(encoding="utf-8")

target = "        depth_m = estimate_depth_map(pil)\n        f_m, w_m, f_q, w_q = refine_masks_with_geometry(clean_mask(floor_bin, 3), clean_mask(wall_bin, 3), obs_bin, depth_m)\n"
replacement = (
    "        try:\n"
    "            depth_m = estimate_depth_map(pil)\n"
    "            f_m, w_m, f_q, w_q = refine_masks_with_geometry(clean_mask(floor_bin, 3), clean_mask(wall_bin, 3), obs_bin, depth_m)\n"
    "        except Exception as geo_err:\n"
    "            print(f'[AI] Geometry fallback ({geo_err})')\n"
    "            f_m = clean_mask(floor_bin, 5)\n"
    "            w_m = clean_mask(wall_bin, 5)\n"
    "            f_q = estimate_perspective_quad(f_m, True)\n"
    "            w_q = estimate_perspective_quad(w_m, False)\n"
)

if target in txt:
    p.write_text(txt.replace(target, replacement, 1), encoding="utf-8")
    print("Added safe HTTP-500 fallback to server.py")
else:
    print("Target block not matched; paste the CMD traceback here for exact fix.")