from pathlib import Path

p = Path("server.py")
lines = p.read_text(encoding="utf-8").splitlines()

idx = next((i for i, l in enumerate(lines) if "obs_ids = [" in l), None)
if idx is not None:
    end = next(j for j in range(idx + 1, len(lines)) if lines[j].lstrip().startswith("return "))
    ind = "        "
    block = [
        ind + lines[idx].lstrip(),
        ind + "obs_bin = np.isin(pred, obs_ids).astype(np.uint8) * 255",
        ind + "depth_m = estimate_depth_map(pil)",
        ind + "f_m, w_m, f_q, w_q = refine_masks_with_geometry(clean_mask(floor_bin, 3), clean_mask(wall_bin, 3), obs_bin, depth_m)",
        ind + 'return f_m, w_m, f_q, w_q, f"segformer+depth+3d-plane ({device})"',
    ]
    lines = lines[:idx] + block + lines[end + 1 :]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Fixed obs_ids block in server.py")
else:
    print("obs_ids block not found; checking syntax directly")