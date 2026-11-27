from pathlib import Path

p = Path("server.py")
txt = p.read_text(encoding="utf-8")

txt = txt.replace("depth_m = estimate_depth_map(pil)", "depth_m = estimate_depth_map(pil_img)")

old_block = (
    "        depth_m = estimate_depth_map(pil_img)\n"
    "        f_m, w_m, f_q, w_q = refine_masks_with_geometry(clean_mask(floor_bin, 3), clean_mask(wall_bin, 3), obs_bin, depth_m)\n"
)
safe_block = (
    "        try:\n"
    "            depth_m = estimate_depth_map(pil_img)\n"
    "            f_m, w_m, f_q, w_q = refine_masks_with_geometry(clean_mask(floor_bin, 3), clean_mask(wall_bin, 3), obs_bin, depth_m)\n"
    "        except Exception as geo_err:\n"
    "            print(f'[AI] Geometry fallback ({geo_err})')\n"
    "            f_m = clean_mask(floor_bin, 5)\n"
    "            w_m = clean_mask(wall_bin, 5)\n"
    "            f_q = estimate_perspective_quad(f_m, True)\n"
    "            w_q = estimate_perspective_quad(w_m, False)\n"
)
if old_block in txt:
    txt = txt.replace(old_block, safe_block, 1)

p.write_text(txt, encoding="utf-8")
print("Fixed pil_img reference in server.py")