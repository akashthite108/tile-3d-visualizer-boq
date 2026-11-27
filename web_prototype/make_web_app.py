import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR if BASE_DIR.name.lower() == "web_prototype" else (BASE_DIR / "web_prototype")
OUT_HTML = WEB_DIR / "index.html"
OUT_HTML.parent.mkdir(parents=True, exist_ok=True)

BOQ_CANDIDATES = [
    WEB_DIR / "boq.mjs",
    BASE_DIR / "boq.mjs",
    BASE_DIR.parent / "boq.mjs",
]
BOQ_DST = WEB_DIR / "boq.mjs"

for cand in BOQ_CANDIDATES:
    if cand.exists() and cand.resolve() != BOQ_DST.resolve():
        try:
            if BOQ_DST.exists():
                BOQ_DST.unlink()
            os.link(cand, BOQ_DST)
        except OSError:
            shutil.copy2(cand, BOQ_DST)
        break

if not BOQ_DST.exists():
    print(f"WARNING: {BOQ_DST} not found. Place boq.mjs in web_prototype/ before running the server.")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Simpolo — Vitrified Tiles, 3D Virtual Space Creator &amp; BOQ Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #ffffff;
      --bg-soft: #f6f5f2;
      --bg-warm: #efede8;
      --obsidian: #111214;
      --obsidian-2: #191b1f;
      --ink: #111214;
      --ink-2: #3d4047;
      --muted: #6e717a;
      --line: #e6e4df;
      --line-strong: #cfccc4;
      --brand-red: #c41e24;
      --accent: #9c6b30;
      --accent-hover: #7d5422;
      --accent-soft: #faf5ee;
      --accent-ring: rgba(156, 107, 48, 0.22);
      --warn: #b45309;
      --warn-bg: #fffbeb;
      --stage-elev: rgba(17, 18, 20, 0.8);
      --font-sans: "Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
      --font-serif: "Cormorant Garamond", Georgia, serif;
      --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
      --topbar-h: 70px;
    }

    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0;
      background: var(--bg); color: var(--ink);
      font-family: var(--font-sans);
      -webkit-font-smoothing: antialiased;
    }
    button, input, select { font-family: inherit; }
    .mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
    .serif { font-family: var(--font-serif); }

    ::-webkit-scrollbar { width: 7px; height: 7px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #ccc9c0; border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: #9c988e; }

    /* ==================== OFFICIAL SIMPOLO-STYLE HEADER ==================== */
    .topbar {
      position: sticky; top: 0; z-index: 80;
      height: var(--topbar-h);
      background: rgba(255, 255, 255, 0.97);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--line);
      padding: 0 28px;
      display: flex; align-items: center; justify-content: space-between; gap: 18px;
    }
    @media (max-width: 820px) { .topbar { padding: 0 14px; } }

    .brand {
      display: inline-flex; align-items: center; gap: 10px;
      text-decoration: none; color: var(--ink); flex-shrink: 0;
    }
    .brand-wordmark {
      font-size: 23px; font-weight: 800; letter-spacing: 0.22em;
      text-transform: uppercase; line-height: 1; display: inline-flex; align-items: center;
    }
    .brand-dot {
      width: 6px; height: 6px; background: var(--brand-red);
      display: inline-block; margin-left: 2px; margin-bottom: 10px;
    }
    .brand-tag {
      font-size: 9.5px; letter-spacing: 0.16em; text-transform: uppercase;
      color: var(--muted); font-weight: 600; border-left: 1px solid var(--line-strong);
      padding-left: 10px; display: none;
    }
    @media (min-width: 1180px) { .brand-tag { display: inline-block; } }

    .main-nav {
      display: flex; align-items: center; gap: 6px; height: 100%;
    }
    .nav-item {
      position: relative; height: 100%; display: flex; align-items: center;
    }
    .nav-link {
      background: transparent; border: none; color: var(--ink);
      font-size: 12.5px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
      padding: 8px 13px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
      border-bottom: 2px solid transparent; height: 100%; transition: all 0.16s ease;
      white-space: nowrap;
    }
    .nav-link:hover { color: var(--accent); }
    .nav-link.active { color: var(--ink); border-bottom-color: var(--ink); }
    .nav-count {
      font-size: 10px; font-weight: 700; padding: 2px 6px;
      background: var(--bg-soft); color: var(--muted); border: 1px solid var(--line);
    }

    /* Mega Menu Dropdown (Simpolo Tiles Navigation) */
    .mega-menu {
      position: absolute; top: 100%; left: -120px; width: 700px;
      background: #ffffff; border: 1px solid var(--line);
      box-shadow: 0 24px 48px rgba(0, 0, 0, 0.14);
      padding: 24px 26px; display: none; grid-template-columns: 1.2fr 1fr 1fr; gap: 24px;
      z-index: 90;
    }
    .nav-item:hover .mega-menu, .nav-item.open .mega-menu { display: grid; }
    @media (max-width: 960px) { .nav-item:hover .mega-menu { display: none; } }
    .mega-col-title {
      font-size: 10.5px; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase;
      color: var(--accent); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--line);
    }
    .mega-links { display: flex; flex-direction: column; gap: 5px; }
    .mega-links.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 5px 12px; }
    .mega-btn {
      background: transparent; border: none; text-align: left; padding: 5px 0;
      font-size: 12.5px; font-weight: 500; color: var(--ink-2); cursor: pointer;
      transition: color 0.14s ease, transform 0.14s ease; text-transform: capitalize;
    }
    .mega-btn:hover { color: var(--ink); transform: translateX(3px); font-weight: 600; }

    .topbar-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
    .room-chip {
      font-size: 11px; font-weight: 600; color: var(--ink-2);
      background: var(--bg-soft); border: 1px solid var(--line);
      padding: 7px 10px; display: none;
    }
    @media (min-width: 1240px) { .room-chip { display: inline-flex; } }
    .quote-pill {
      display: inline-flex; align-items: center; gap: 8px;
      background: var(--obsidian); color: #fff; border: 1px solid var(--obsidian);
      padding: 9px 14px; font-size: 11.5px; font-weight: 700; letter-spacing: 0.06em;
      text-transform: uppercase; cursor: pointer; transition: all 0.16s ease;
    }
    .quote-pill:hover { background: var(--accent); border-color: var(--accent); }
    .quote-pill-amt { color: #f3d09b; }

    /* Shared Architectural Buttons */
    .sim-btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      padding: 12px 26px; font-size: 11.5px; font-weight: 700;
      letter-spacing: 0.14em; text-transform: uppercase; cursor: pointer;
      transition: all 0.2s ease; text-decoration: none; border-radius: 0;
    }
    .sim-btn-dark { background: var(--obsidian); color: #fff; border: 1px solid var(--obsidian); }
    .sim-btn-dark:hover { background: var(--accent); border-color: var(--accent); }
    .sim-btn-outline { background: transparent; color: var(--ink); border: 1px solid var(--ink); }
    .sim-btn-outline:hover { background: var(--ink); color: #fff; }
    .sim-btn-white { background: #fff; color: var(--ink); border: 1px solid #fff; }
    .sim-btn-white:hover { background: transparent; color: #fff; }
    .sim-btn-ghost-white { background: rgba(255,255,255,0.08); color: #fff; border: 1px solid rgba(255,255,255,0.45); backdrop-filter: blur(6px); }
    .sim-btn-ghost-white:hover { background: #fff; color: var(--ink); border-color: #fff; }

    /* ==================== VIEWS ==================== */
    .app-view { display: none; }
    .app-view.active { display: block; }

    /* ==================== VIEW 0: OFFICIAL SIMPOLO-STYLE HOMEPAGE ==================== */
    /* 1. Full-Bleed Interactive Hero Slider */
    .sim-hero {
      position: relative; width: 100%; height: calc(100vh - var(--topbar-h));
      min-height: 540px; max-height: 780px; background: var(--obsidian); overflow: hidden;
    }
    .hero-slide {
      position: absolute; inset: 0; opacity: 0; pointer-events: none;
      transition: opacity 0.85s ease;
    }
    .hero-slide.active { opacity: 1; pointer-events: auto; z-index: 2; }
    .hero-slide-img {
      position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
      transform: scale(1.03); transition: transform 6s ease;
    }
    .hero-slide.active .hero-slide-img { transform: scale(1.0); }
    .hero-scrim {
      position: absolute; inset: 0;
      background: linear-gradient(90deg, rgba(12,13,16,0.86) 0%, rgba(12,13,16,0.52) 48%, rgba(12,13,16,0.22) 100%),
                  linear-gradient(0deg, rgba(12,13,16,0.75) 0%, rgba(12,13,16,0.0) 40%);
    }
    .hero-content {
      position: relative; z-index: 4; max-width: 1320px; height: 100%;
      margin: 0 auto; padding: 0 36px;
      display: flex; flex-direction: column; justify-content: center; align-items: flex-start;
      color: #fff;
    }
    .hero-kicker {
      font-size: 11px; font-weight: 700; letter-spacing: 0.24em; text-transform: uppercase;
      color: #e4bc7e; margin-bottom: 14px; display: inline-flex; align-items: center; gap: 10px;
    }
    .hero-kicker::before { content: ""; width: 28px; height: 1px; background: #e4bc7e; }
    .hero-title {
      font-family: var(--font-serif); font-weight: 600;
      font-size: clamp(42px, 6vw, 76px); line-height: 1.03; margin: 0 0 14px;
      max-width: 720px; letter-spacing: -0.01em;
    }
    .hero-subtitle {
      font-size: clamp(14px, 1.4vw, 17px); color: rgba(255,255,255,0.84);
      max-width: 540px; line-height: 1.6; margin: 0 0 28px; font-weight: 400;
    }
    .hero-cta-row { display: flex; flex-wrap: wrap; gap: 12px; }

    .hero-nav-arrows {
      position: absolute; right: 36px; bottom: 34px; z-index: 10; display: flex; gap: 8px;
    }
    .hero-arrow {
      width: 44px; height: 44px; border: 1px solid rgba(255,255,255,0.35);
      background: rgba(17,18,20,0.45); backdrop-filter: blur(6px);
      color: #fff; font-size: 18px; cursor: pointer; transition: all 0.16s ease;
    }
    .hero-arrow:hover { background: #fff; color: var(--ink); border-color: #fff; }

    .hero-dots {
      position: absolute; left: 36px; bottom: 38px; z-index: 10;
      display: flex; gap: 10px; align-items: center;
    }
    .hero-dot {
      display: flex; flex-direction: column; gap: 6px; background: transparent;
      border: none; color: rgba(255,255,255,0.55); cursor: pointer; padding: 0; text-align: left;
      transition: color 0.2s ease;
    }
    .hero-dot-bar { width: 46px; height: 2px; background: rgba(255,255,255,0.28); transition: all 0.25s ease; }
    .hero-dot-label { font-size: 10px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
    .hero-dot.active { color: #fff; }
    .hero-dot.active .hero-dot-bar { width: 72px; background: #e4bc7e; }
    @media (max-width: 720px) { .hero-dot-label { display: none; } }

    /* Shared Homepage Section Wrapper */
    .home-sec { max-width: 1320px; margin: 0 auto; padding: 78px 32px; }
    @media (max-width: 720px) { .home-sec { padding: 52px 18px; } }
    .sec-eyebrow {
      font-size: 11px; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase;
      color: var(--accent); margin-bottom: 10px; display: inline-flex; align-items: center; gap: 10px;
    }
    .sec-eyebrow::before { content: ""; width: 22px; height: 1px; background: var(--accent); }
    .sec-heading {
      font-family: var(--font-serif); font-size: clamp(32px, 4vw, 48px);
      font-weight: 600; line-height: 1.1; margin: 0 0 14px; color: var(--ink);
    }
    .sec-copy { font-size: 14.5px; color: var(--ink-2); line-height: 1.7; max-width: 600px; margin: 0; }

    /* 2. About / 49 Years Editorial Band */
    .about-grid {
      display: grid; grid-template-columns: 1.05fr 1fr; gap: 56px; align-items: center;
    }
    @media (max-width: 920px) { .about-grid { grid-template-columns: 1fr; gap: 36px; } }
    .legacy-badge {
      display: flex; align-items: flex-end; gap: 18px; margin-bottom: 20px;
      padding-bottom: 20px; border-bottom: 1px solid var(--line);
    }
    .legacy-num {
      font-family: var(--font-serif); font-size: 76px; font-weight: 700;
      line-height: 0.85; color: var(--ink);
    }
    .legacy-meta { display: flex; flex-direction: column; gap: 4px; }
    .legacy-label { font-size: 12px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent); }
    .legacy-sub { font-size: 13px; color: var(--muted); }

    .about-stats {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 26px 0 28px;
    }
    .stat-tile { border-left: 2px solid var(--line-strong); padding-left: 14px; }
    .stat-val { font-size: 22px; font-weight: 800; color: var(--ink); }
    .stat-lbl { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }

    .about-mosaic {
      display: grid; grid-template-columns: 1.25fr 1fr; grid-template-rows: 220px 180px; gap: 12px;
    }
    .mosaic-item {
      position: relative; overflow: hidden; background: var(--bg-soft); cursor: pointer;
    }
    .mosaic-item.tall { grid-row: span 2; }
    .mosaic-item img {
      width: 100%; height: 100%; object-fit: cover; display: block;
      transition: transform 0.55s ease;
    }
    .mosaic-item:hover img { transform: scale(1.06); }
    .mosaic-cap {
      position: absolute; left: 12px; bottom: 12px;
      background: rgba(17,18,20,0.75); color: #fff; padding: 5px 10px;
      font-size: 10.5px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    }

    /* 3. Explore Premium Tiles Collection (Locations / Effects / Sizes) */
    .explore-band { background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .explore-head {
      display: flex; justify-content: space-between; align-items: flex-end; gap: 20px;
      flex-wrap: wrap; margin-bottom: 32px;
    }
    .explore-tabs {
      display: inline-flex; border-bottom: 1px solid var(--line-strong); gap: 28px;
    }
    .explore-tab {
      background: transparent; border: none; border-bottom: 2px solid transparent;
      padding: 10px 2px; font-size: 12.5px; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--muted); cursor: pointer;
      transition: all 0.16s ease; margin-bottom: -1px;
    }
    .explore-tab:hover { color: var(--ink); }
    .explore-tab.active { color: var(--ink); border-bottom-color: var(--ink); }

    .explore-grid {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
    }
    @media (max-width: 900px) { .explore-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 560px) { .explore-grid { grid-template-columns: 1fr; } }

    .explore-card {
      position: relative; height: 270px; overflow: hidden; cursor: pointer;
      background: var(--obsidian); border: 1px solid var(--line);
    }
    .explore-card img {
      width: 100%; height: 100%; object-fit: cover; display: block;
      transition: transform 0.6s ease; opacity: 0.88;
    }
    .explore-card:hover img { transform: scale(1.07); opacity: 0.96; }
    .explore-card-overlay {
      position: absolute; inset: 0;
      background: linear-gradient(0deg, rgba(12,13,16,0.86) 0%, rgba(12,13,16,0.12) 60%);
      padding: 22px; display: flex; flex-direction: column; justify-content: flex-end; color: #fff;
    }
    .explore-card-kicker {
      font-size: 10px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: #e4bc7e;
    }
    .explore-card-title {
      font-family: var(--font-serif); font-size: 28px; font-weight: 600; margin: 4px 0 4px; line-height: 1.1;
    }
    .explore-card-sub {
      font-size: 12px; color: rgba(255,255,255,0.78); display: flex; justify-content: space-between; align-items: center;
    }

    /* 4. Latest Vitrified Tiles Collection (Portrait Showcase) */
    .collections-grid {
      display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px;
    }
    @media (max-width: 1120px) { .collections-grid { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 640px) { .collections-grid { grid-template-columns: repeat(2, 1fr); } }
    .col-card {
      position: relative; height: 340px; overflow: hidden; cursor: pointer;
      background: var(--obsidian);
    }
    .col-card img {
      width: 100%; height: 100%; object-fit: cover; display: block;
      transition: transform 0.65s ease;
    }
    .col-card:hover img { transform: scale(1.08); }
    .col-card-grad {
      position: absolute; inset: 0;
      background: linear-gradient(0deg, rgba(10,11,14,0.88) 0%, rgba(10,11,14,0.1) 55%);
      padding: 20px 18px; display: flex; flex-direction: column; justify-content: flex-end; color: #fff;
    }
    .col-card-label { font-size: 9.5px; letter-spacing: 0.18em; text-transform: uppercase; color: #e4bc7e; font-weight: 700; }
    .col-card-name { font-size: 18px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; margin: 4px 0 3px; }
    .col-card-meta { font-size: 11px; color: rgba(255,255,255,0.72); }

    /* 5. Transform Your Spaces Effortlessly! (Obsidian Visualizer Band) */
    .visualizer-band {
      background: var(--obsidian); color: #fff;
      border-top: 1px solid #24262c; border-bottom: 1px solid #24262c;
    }
    .viz-grid {
      display: grid; grid-template-columns: 1fr 1.25fr; gap: 48px; align-items: center;
    }
    @media (max-width: 960px) { .viz-grid { grid-template-columns: 1fr; } }
    .viz-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 600px) { .viz-cards { grid-template-columns: 1fr; } }
    .viz-portal {
      background: var(--obsidian-2); border: 1px solid rgba(255,255,255,0.12);
      padding: 26px 24px; cursor: pointer; transition: all 0.22s ease;
      display: flex; flex-direction: column; justify-content: space-between; min-height: 220px;
    }
    .viz-portal:hover { border-color: #e4bc7e; transform: translateY(-3px); background: #202228; }
    .viz-portal-kicker { font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: #e4bc7e; }
    .viz-portal-title { font-family: var(--font-serif); font-size: 30px; font-weight: 600; margin: 8px 0 8px; line-height: 1.1; }
    .viz-portal-desc { font-size: 13px; color: #b5b8c2; line-height: 1.55; margin: 0 0 18px; }
    .viz-portal-cta {
      font-size: 11px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;
      color: #fff; display: inline-flex; align-items: center; gap: 8px;
    }

    /* 6. Start Your Journey 4-Card Strip */
    .journey-grid {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 28px;
    }
    @media (max-width: 920px) { .journey-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 520px) { .journey-grid { grid-template-columns: 1fr; } }
    .journey-card {
      background: var(--bg-soft); border: 1px solid var(--line);
      padding: 24px 22px; cursor: pointer; transition: all 0.18s ease;
      display: flex; flex-direction: column; justify-content: space-between; min-height: 160px;
    }
    .journey-card:hover { background: var(--obsidian); color: #fff; border-color: var(--obsidian); }
    .journey-card:hover .journey-sub { color: #b8bbc4; }
    .journey-num { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: 0.14em; }
    .journey-title { font-family: var(--font-serif); font-size: 25px; font-weight: 600; margin: 8px 0 6px; }
    .journey-sub { font-size: 12.5px; color: var(--muted); line-height: 1.5; }

    /* Official-style Dark Footer */
    .sim-footer {
      background: #0d0e10; color: #b5b8c0; padding: 56px 32px 28px;
      border-top: 1px solid #22242a;
    }
    .footer-inner {
      max-width: 1320px; margin: 0 auto;
      display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.2fr; gap: 36px;
      padding-bottom: 36px; border-bottom: 1px solid #22242a;
    }
    @media (max-width: 920px) { .footer-inner { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 540px) { .footer-inner { grid-template-columns: 1fr; } }
    .footer-title {
      font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase;
      color: #fff; margin: 0 0 14px;
    }
    .footer-links { display: flex; flex-direction: column; gap: 8px; }
    .footer-btn {
      background: transparent; border: none; color: #a1a5b0; text-align: left;
      padding: 0; font-size: 13px; cursor: pointer; transition: color 0.14s ease;
    }
    .footer-btn:hover { color: #e4bc7e; }
    .footer-bottom {
      max-width: 1320px; margin: 22px auto 0;
      display: flex; justify-content: space-between; gap: 14px; flex-wrap: wrap;
      font-size: 11.5px; color: #7a7e88;
    }

    /* ==================== VIEW 1: VIRTUAL SPACE CREATOR (3D ROOM STUDIO) ==================== */
    .studio-shell {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr) 340px;
      height: calc(100vh - var(--topbar-h));
      min-height: 620px;
      overflow: hidden;
    }
    @media (max-width: 1180px) { .studio-shell { grid-template-columns: 290px minmax(0, 1fr) 310px; } }
    @media (max-width: 960px) { .studio-shell { grid-template-columns: 1fr; height: auto; overflow: visible; } }

    .dock {
      background: #ffffff; display: flex; flex-direction: column;
      height: 100%; overflow: hidden;
    }
    .dock-left { border-right: 1px solid var(--line); }
    .dock-right { border-left: 1px solid var(--line); }
    @media (max-width: 960px) { .dock { height: auto; border: none; border-bottom: 1px solid var(--line); } }

    .dock-head {
      padding: 12px 14px; border-bottom: 1px solid var(--line);
      background: var(--bg-soft); flex-shrink: 0;
    }
    .dock-title {
      font-size: 10.5px; font-weight: 800; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--muted);
      display: flex; align-items: center; justify-content: space-between;
    }
    .dock-scroll { flex: 1; overflow-y: auto; padding: 12px 14px 18px; }

    .surface-stack { display: grid; grid-template-columns: 1fr; gap: 7px; margin-top: 8px; }
    .surf-card {
      display: grid; grid-template-columns: 44px minmax(0, 1fr) auto; gap: 10px; align-items: center;
      padding: 7px 9px; border: 1.5px solid var(--line); background: #fff;
      cursor: pointer; text-align: left; width: 100%; transition: all 0.14s ease;
    }
    .surf-card:hover { border-color: var(--line-strong); background: var(--bg-soft); }
    .surf-card.active {
      border-color: var(--ink); background: var(--accent-soft);
      box-shadow: inset 3px 0 0 var(--accent);
    }
    .surf-thumb { width: 44px; height: 44px; object-fit: cover; background: #e5e3dc; border: 1px solid rgba(0,0,0,0.08); }
    .surf-role { font-size: 9.5px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); }
    .surf-sku { font-size: 12px; font-weight: 700; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .surf-meta { font-size: 10.5px; color: var(--muted); }
    .surf-dot { width: 8px; height: 8px; border-radius: 99px; border: 1.5px solid var(--line-strong); }
    .surf-card.active .surf-dot { background: var(--ink); border-color: var(--ink); }

    .mini-filters {
      padding: 10px 14px; border-bottom: 1px solid var(--line);
      display: flex; flex-direction: column; gap: 7px; flex-shrink: 0; background: #fff;
    }
    .input, .select {
      width: 100%; padding: 7px 10px; border: 1px solid var(--line-strong);
      background: #fff; color: var(--ink); font-size: 12.5px; outline: none;
      transition: border-color 0.14s ease;
    }
    .input:focus, .select:focus { border-color: var(--ink); }
    .g-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
    .g-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
    .swatch-count { font-size: 11px; color: var(--muted); display: flex; justify-content: space-between; align-items: center; }

    .swatch-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .swatch-card {
      border: 1px solid var(--line); overflow: hidden; background: #fff;
      cursor: pointer; position: relative; transition: all 0.14s ease; display: flex; flex-direction: column;
    }
    .swatch-card:hover { border-color: var(--ink); transform: translateY(-1px); }
    .swatch-card.applied { border: 2px solid var(--accent); }
    .swatch-img-wrap { position: relative; height: 74px; background: #e6e4de; overflow: hidden; }
    .swatch-img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .swatch-zoom-btn {
      position: absolute; top: 5px; right: 5px; width: 24px; height: 24px; border: none;
      background: rgba(17,18,20,0.75); color: #fff; cursor: pointer;
      display: grid; place-items: center; font-size: 11px; opacity: 0; transition: opacity 0.14s ease;
    }
    .swatch-card:hover .swatch-zoom-btn { opacity: 1; }
    .swatch-zoom-btn:hover { background: var(--accent); }
    .swatch-body { padding: 6px 7px; }
    .swatch-series { font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); }
    .swatch-name { font-size: 11px; font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px; }
    .swatch-size { font-size: 10px; color: var(--muted); margin-top: 1px; }

    .btn-ghost {
      width: 100%; padding: 8px 10px; border: 1px solid var(--line-strong);
      background: #fff; color: var(--ink); font-size: 11.5px; font-weight: 700;
      letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer; transition: all 0.14s ease;
    }
    .btn-ghost:hover { border-color: var(--ink); background: var(--bg-soft); }
    .btn-primary {
      width: 100%; padding: 9px 12px; border: 1px solid var(--accent);
      background: var(--accent); color: #fff; font-size: 11.5px; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; transition: all 0.14s ease;
    }
    .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
    .btn-dark {
      width: 100%; padding: 9px 12px; border: 1px solid var(--obsidian);
      background: var(--obsidian); color: #fff; font-size: 11.5px; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; transition: all 0.14s ease;
    }
    .btn-dark:hover { background: #2c2f36; }

    /* Center 3D Stage */
    .viewport-stage {
      position: relative; background: var(--obsidian);
      height: 100%; min-height: 520px; overflow: hidden;
    }
    #canvasHost { width: 100%; height: 100%; }

    .hud-top-left {
      position: absolute; top: 14px; left: 14px; z-index: 10;
      display: flex; flex-wrap: wrap; gap: 6px; max-width: calc(100% - 150px);
    }
    .hud-top-right { position: absolute; top: 14px; right: 14px; z-index: 10; display: flex; gap: 6px; }
    .hud-group {
      display: inline-flex; align-items: center; gap: 2px;
      background: var(--stage-elev); backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.14); padding: 3px;
    }
    .hud-btn {
      background: transparent; color: #d4d7df; border: none;
      padding: 6px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
      cursor: pointer; transition: all 0.14s ease; white-space: nowrap;
    }
    .hud-btn:hover { color: #fff; background: rgba(255,255,255,0.1); }
    .hud-btn.active { background: #fff; color: var(--ink); }

    .hud-bottom {
      position: absolute; bottom: 14px; left: 14px; right: 14px; z-index: 10;
      display: flex; align-items: flex-end; justify-content: space-between; gap: 12px;
      pointer-events: none;
    }
    .hud-telemetry {
      background: var(--stage-elev); backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.14);
      padding: 10px 14px; color: #f1f5f9; pointer-events: auto; max-width: 460px;
    }
    .hud-tel-title { font-size: 12.5px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .hud-tel-tag {
      font-size: 9.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em;
      background: var(--accent); color: #fff; padding: 2px 7px;
    }
    .hud-tel-sub { font-size: 11px; color: #a1a8b8; margin-top: 4px; }
    .hud-hint {
      background: var(--stage-elev); backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #cbd5e1; font-size: 11px; padding: 6px 10px; display: none;
    }
    @media (min-width: 1240px) { .hud-hint { display: block; } }

    /* Right Inspector */
    .insp-tabs {
      display: grid; grid-template-columns: repeat(3, 1fr);
      border-bottom: 1px solid var(--line); background: var(--bg-soft); flex-shrink: 0;
    }
    .insp-tab {
      border: none; border-bottom: 2px solid transparent; background: transparent;
      color: var(--muted); padding: 11px 6px; font-size: 11px; font-weight: 700;
      letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer;
    }
    .insp-tab:hover { color: var(--ink); }
    .insp-tab.active { color: var(--ink); border-bottom-color: var(--ink); background: #fff; }
    .insp-pane { display: none; }
    .insp-pane.active { display: block; }

    .ctrl-section { padding-bottom: 14px; margin-bottom: 14px; border-bottom: 1px solid var(--line); }
    .ctrl-section:last-child { border-bottom: none; margin-bottom: 0; }
    .ctrl-heading {
      font-size: 10px; font-weight: 800; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--muted); margin: 0 0 8px;
    }
    .field-label {
      display: flex; justify-content: space-between; align-items: center;
      font-size: 11.5px; font-weight: 600; color: var(--ink-2); margin: 8px 0 4px;
    }
    .preset-pills { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
    .preset-chip {
      border: 1px solid var(--line-strong); background: var(--bg-soft); color: var(--ink-2);
      font-size: 10.5px; font-weight: 700; padding: 4px 8px; cursor: pointer;
    }
    .preset-chip:hover { border-color: var(--ink); color: var(--ink); background: #fff; }

    .seg-control {
      display: grid; grid-template-columns: 1fr 1fr; border: 1px solid var(--line-strong);
    }
    .seg-btn {
      border: none; background: var(--bg-soft); color: var(--ink-2);
      padding: 7px 8px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; cursor: pointer;
    }
    .seg-btn.active { background: var(--obsidian); color: #fff; }

    .grout-row { display: flex; align-items: center; gap: 7px; margin-top: 6px; }
    .grout-dot {
      width: 24px; height: 24px; border-radius: 50%; cursor: pointer;
      border: 2px solid var(--line-strong); padding: 0; flex-shrink: 0;
    }
    .grout-dot.active { border-color: var(--ink); box-shadow: 0 0 0 2px var(--accent-ring); }
    input[type="color"].color-pill {
      width: 32px; height: 26px; padding: 1px; border: 1px solid var(--line-strong);
      background: #fff; cursor: pointer; margin-left: auto;
    }

    .finish-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
    .finish-card {
      border: 1.5px solid var(--line); background: #fff; padding: 8px 9px;
      text-align: left; cursor: pointer; transition: all 0.14s ease;
    }
    .finish-card:hover { border-color: var(--line-strong); }
    .finish-card.active { border-color: var(--ink); background: var(--accent-soft); }
    .finish-name { font-size: 11.5px; font-weight: 700; color: var(--ink); }
    .finish-desc { font-size: 10px; color: var(--muted); margin-top: 2px; }

    .switch-row {
      display: flex; align-items: center; justify-content: space-between; gap: 10px;
      padding: 7px 0; font-size: 12px; font-weight: 500; color: var(--ink);
    }
    .switch { position: relative; width: 36px; height: 20px; flex-shrink: 0; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider-pill {
      position: absolute; inset: 0; background: #d4d2cc; border-radius: 99px;
      cursor: pointer; transition: 0.18s ease;
    }
    .slider-pill::before {
      content: ""; position: absolute; width: 14px; height: 14px; left: 3px; top: 3px;
      background: #fff; border-radius: 50%; transition: 0.18s ease;
    }
    .switch input:checked + .slider-pill { background: var(--obsidian); }
    .switch input:checked + .slider-pill::before { transform: translateX(16px); }
    input[type="range"].range { width: 100%; accent-color: var(--obsidian); cursor: pointer; }

    .boq-card {
      background: var(--bg-soft); border: 1px solid var(--line); padding: 12px; font-size: 12px;
    }
    .boq-line { padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px dashed var(--line-strong); }
    .boq-row { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; line-height: 1.5; }
    .boq-flag {
      color: var(--warn); background: var(--warn-bg); border: 1px solid #fde68a;
      font-size: 10.5px; font-weight: 600; padding: 3px 6px; margin-top: 4px;
    }
    .boq-consumables { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 8px; }
    .cons-box { background: #fff; border: 1px solid var(--line); padding: 7px 8px; }
    .cons-label { font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 700; }
    .cons-val { font-size: 12px; font-weight: 700; color: var(--ink); margin-top: 2px; }
    .boq-total-box { margin-top: 10px; padding-top: 9px; border-top: 1.5px solid var(--line-strong); }
    .boq-grand { font-size: 14.5px; font-weight: 800; color: var(--ink); }

    /* ==================== VIEW 2: DIGITAL SHOWROOM (FULL CATALOG) ==================== */
    .container { max-width: 1340px; margin: 0 auto; padding: 28px 24px 64px; }
    .catalog-banner {
      position: relative; overflow: hidden; background: var(--obsidian); color: #fff;
      padding: 36px 34px 30px; margin-bottom: 22px;
    }
    .catalog-banner-bg {
      position: absolute; inset: 0; background-size: cover; background-position: center;
      opacity: 0.25; transition: background-image 0.35s ease;
    }
    .catalog-banner-inner { position: relative; z-index: 2; }
    .catalog-banner h1 { font-family: var(--font-serif); margin: 6px 0 8px; font-size: clamp(28px, 3.6vw, 42px); font-weight: 600; }
    .catalog-banner p { margin: 0 0 18px; font-size: 13.5px; color: #d4d7df; max-width: 680px; line-height: 1.55; }
    .series-pills { display: flex; flex-wrap: wrap; gap: 6px; }
    .pill-btn {
      background: rgba(255,255,255,0.08); color: #f1f5f9;
      border: 1px solid rgba(255,255,255,0.22); padding: 6px 12px;
      font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
      cursor: pointer; transition: all 0.14s ease;
    }
    .pill-btn:hover { background: rgba(255,255,255,0.2); }
    .pill-btn.active { background: #fff; border-color: #fff; color: var(--ink); }

    .catalog-toolbar {
      position: sticky; top: calc(var(--topbar-h) + 6px); z-index: 30;
      background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(10px);
      border: 1px solid var(--line); padding: 14px 16px; margin-bottom: 18px;
    }
    .toolbar-grid { display: grid; grid-template-columns: 1fr 240px 200px auto; gap: 10px; align-items: center; }
    @media (max-width: 900px) { .toolbar-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 580px) { .toolbar-grid { grid-template-columns: 1fr; } }
    .filter-bar { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
    .tab-btn {
      background: var(--bg-soft); color: var(--ink-2); border: 1px solid var(--line);
      padding: 5px 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer;
    }
    .tab-btn.active { background: var(--obsidian); color: #fff; border-color: var(--obsidian); }

    .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
    .card {
      background: #fff; border: 1px solid var(--line); overflow: hidden;
      display: flex; flex-direction: column; transition: transform 0.16s ease, box-shadow 0.16s ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 12px 26px rgba(0,0,0,0.08); }
    .card-thumb-wrap { position: relative; height: 170px; background: #e7e5e0; overflow: hidden; cursor: zoom-in; }
    .card-thumb { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }
    .card-thumb-wrap:hover .card-thumb { transform: scale(1.06); }
    .zoom-badge {
      position: absolute; bottom: 8px; right: 8px;
      background: rgba(17,18,20,0.8); color: #fff;
      font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 8px;
    }
    .card-body { padding: 13px 14px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .card-series { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); }
    .card-title { font-size: 14px; font-weight: 700; margin: 4px 0; color: var(--ink); word-break: break-word; }
    .card-meta { font-size: 11.5px; color: var(--muted); margin-bottom: 11px; }
    .quick-apply-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; }
    .qa-btn {
      padding: 6px 4px; border: 1px solid var(--line-strong); background: var(--bg-soft);
      color: var(--ink); font-size: 10.5px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
      cursor: pointer; transition: all 0.14s ease;
    }
    .qa-btn:hover { background: var(--obsidian); color: #fff; border-color: var(--obsidian); }

    .load-more-wrap { display: flex; justify-content: center; margin-top: 28px; }

    /* ==================== VIEW 3: TILES CALCULATOR (BOQ SHEET) ==================== */
    .boq-sheet-card {
      background: #fff; border: 1px solid var(--line); padding: 30px;
    }
    .boq-sheet-head {
      display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap;
      padding-bottom: 20px; border-bottom: 1px solid var(--line); margin-bottom: 22px;
    }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
    @media (max-width: 820px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
    .kpi-box { background: var(--bg-soft); border: 1px solid var(--line); padding: 16px 18px; }
    .kpi-label { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }
    .kpi-val { font-size: 22px; font-weight: 800; color: var(--ink); margin-top: 5px; }
    .kpi-sub { font-size: 11px; color: var(--muted); margin-top: 3px; }

    .boq-table-wrap { overflow-x: auto; }
    table.boq-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
    table.boq-table th {
      text-align: left; font-size: 10px; font-weight: 800; text-transform: uppercase;
      letter-spacing: 0.1em; color: var(--muted); padding: 11px 12px;
      border-bottom: 2px solid var(--obsidian); background: var(--bg-soft); white-space: nowrap;
    }
    table.boq-table td { padding: 13px 12px; border-bottom: 1px solid var(--line); vertical-align: middle; }
    table.boq-table th.num, table.boq-table td.num { text-align: right; }
    .tbl-sku { display: flex; align-items: center; gap: 10px; }
    .tbl-thumb { width: 40px; height: 40px; object-fit: cover; border: 1px solid var(--line); }

    /* ==================== 6X TEXTURE INSPECTOR MODAL ==================== */
    .modal-backdrop {
      position: fixed; inset: 0; z-index: 120;
      background: rgba(12, 13, 16, 0.84); backdrop-filter: blur(6px);
      display: none; align-items: center; justify-content: center; padding: 20px;
    }
    .modal-backdrop.open { display: flex; }
    .modal-box {
      background: #fff; max-width: 960px; width: 100%;
      overflow: hidden; box-shadow: 0 28px 70px rgba(0,0,0,0.5);
      display: grid; grid-template-columns: 1.4fr 1fr;
    }
    @media (max-width: 780px) { .modal-box { grid-template-columns: 1fr; } }
    .modal-stage {
      position: relative; background: var(--obsidian); height: 480px; overflow: hidden;
      cursor: grab; display: flex; align-items: center; justify-content: center; user-select: none;
    }
    .modal-stage:active { cursor: grabbing; }
    .modal-stage img { max-width: 100%; max-height: 100%; object-fit: contain; transform-origin: center center; pointer-events: none; }
    .modal-stage-hint {
      position: absolute; bottom: 12px; left: 12px;
      background: var(--stage-elev); color: #e2e8f0;
      font-size: 11px; padding: 5px 10px; pointer-events: none;
    }
    .modal-info { padding: 24px; display: flex; flex-direction: column; justify-content: space-between; gap: 16px; }
    .modal-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
    .modal-close {
      background: var(--bg-soft); border: 1px solid var(--line);
      width: 34px; height: 34px; font-size: 18px; cursor: pointer; color: var(--ink);
    }
    .modal-close:hover { background: var(--obsidian); color: #fff; }
    .spec-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; }
    .spec-cell { background: var(--bg-soft); border: 1px solid var(--line); padding: 9px 11px; }
    .spec-k { font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); font-weight: 800; }
    .spec-v { font-size: 12.5px; font-weight: 700; color: var(--ink); margin-top: 3px; }
    .zoom-ctrl { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--line); }

    /* Toast */
    .toast {
      position: fixed; bottom: 22px; right: 22px; z-index: 140;
      background: var(--obsidian); color: #fff; padding: 11px 18px;
      font-size: 12px; font-weight: 600; letter-spacing: 0.04em;
      box-shadow: 0 12px 30px rgba(0,0,0,0.3);
      transform: translateY(20px); opacity: 0; pointer-events: none;
      transition: all 0.2s ease; border-left: 3px solid #e4bc7e;
    }
    .toast.show { transform: translateY(0); opacity: 1; }

    /* Print Quotation */
    @media print {
      .topbar, #viewHome, #viewStudio, #viewCatalog, .modal-backdrop, .toast, .no-print { display: none !important; }
      #viewBoq { display: block !important; }
      body { background: #fff; }
      .container { padding: 0; max-width: 100%; }
      .boq-sheet-card { border: none; padding: 0; }
    }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <!-- ==================== OFFICIAL SIMPOLO-STYLE HEADER ==================== -->
  <header class="topbar">
    <a class="brand" href="#" id="brandHome">
      <span class="brand-wordmark">SIMPOLO<span class="brand-dot"></span></span>
      <span class="brand-tag">Tiles &amp; Virtual Space</span>
    </a>

    <nav class="main-nav" aria-label="Main navigation">
      <div class="nav-item">
        <button class="nav-link active" data-view="viewHome">Home</button>
      </div>
      <div class="nav-item" id="navTilesItem">
        <button class="nav-link" data-view="viewCatalog">
          Tiles <span class="nav-count mono" id="navCatalogBadge">...</span>
        </button>
        <div class="mega-menu" id="tilesMegaMenu">
          <div>
            <div class="mega-col-title">Collections</div>
            <div class="mega-links two-col" id="megaCollectionsList"></div>
          </div>
          <div>
            <div class="mega-col-title">By Space (3D Room)</div>
            <div class="mega-links">
              <button class="mega-btn" data-launch-room="5,4,3">Living Room Tiles</button>
              <button class="mega-btn" data-launch-room="3,2.4,2.8">Bathroom Tiles</button>
              <button class="mega-btn" data-launch-room="4,3.5,3">Bedroom Tiles</button>
              <button class="mega-btn" data-launch-room="3.8,3,3">Kitchen Tiles</button>
              <button class="mega-btn" data-launch-room="4.5,2.2,3">Balcony Tiles</button>
              <button class="mega-btn" data-launch-room="8,6,3.4">Commercial / Lobby</button>
            </div>
          </div>
          <div>
            <div class="mega-col-title">Look &amp; Feel</div>
            <div class="mega-links" id="megaLookList"></div>
          </div>
        </div>
      </div>
      <div class="nav-item">
        <button class="nav-link" data-view="viewStudio">Digital Visualizer</button>
      </div>
      <div class="nav-item">
        <button class="nav-link" data-view="viewBoq">Tiles Calculator</button>
      </div>
    </nav>

    <div class="topbar-right">
      <div class="room-chip mono" id="topRoomBadge">5.0 × 4.0 × 3.0 m</div>
      <button class="quote-pill" id="topQuoteBtn" title="Open Tiles Calculator & BOQ Sheet">
        <span>BOQ</span>
        <span class="quote-pill-amt mono" id="topBoqTotal">₹0</span>
      </button>
    </div>
  </header>

  <!-- ==================== VIEW 0: SIMPOLO-STYLE HOMEPAGE ==================== -->
  <div class="app-view active" id="viewHome">
    <!-- 1. Full-Bleed Collection Hero Carousel -->
    <section class="sim-hero" aria-label="Featured Collections">
      <div id="heroSlidesHost"></div>
      <div class="hero-dots" id="heroDots"></div>
      <div class="hero-nav-arrows">
        <button class="hero-arrow" id="heroPrev" aria-label="Previous slide">&#8592;</button>
        <button class="hero-arrow" id="heroNext" aria-label="Next slide">&#8594;</button>
      </div>
    </section>

    <!-- 2. Legacy / About Simpolo Editorial Section -->
    <section class="home-sec">
      <div class="about-grid">
        <div>
          <div class="sec-eyebrow">About Simpolo</div>
          <div class="legacy-badge">
            <div class="legacy-num">49</div>
            <div class="legacy-meta">
              <div class="legacy-label">Years of Craftsmanship</div>
              <div class="legacy-sub">Vitrified Tiles &amp; Architectural Surfaces Since 1977</div>
            </div>
          </div>
          <h2 class="sec-heading">The Leading Vitrified Tiles &amp; Surface Studio</h2>
          <p class="sec-copy">
            Curated collections bringing together architectural beauty, innovation, and strength. Explore every indexed surface from your local catalog at up to 6x grain magnification, preview realistic grout and staggered laying patterns in our GPU-accelerated 3D Virtual Space Creator, and export procurement-ready INR Bills of Quantities.
          </p>
          <div class="about-stats">
            <div class="stat-tile">
              <div class="stat-val mono" id="homeTotalSkus">—</div>
              <div class="stat-lbl">Indexed SKUs</div>
            </div>
            <div class="stat-tile">
              <div class="stat-val mono" id="homeTotalSeries">—</div>
              <div class="stat-lbl">Tile Collections</div>
            </div>
            <div class="stat-tile">
              <div class="stat-val mono">WebGL2</div>
              <div class="stat-lbl">3D GPU Tiling</div>
            </div>
          </div>
          <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <button class="sim-btn sim-btn-dark" data-view="viewStudio">Launch Virtual Space</button>
            <button class="sim-btn sim-btn-outline" data-view="viewCatalog">Explore Full Catalog</button>
          </div>
        </div>

        <div class="about-mosaic" id="aboutMosaic"></div>
      </div>
    </section>

    <!-- 3. Explore Premium Tiles Collection (Locations / Effects / Sizes) -->
    <section class="explore-band">
      <div class="home-sec">
        <div class="explore-head">
          <div>
            <div class="sec-eyebrow">Curated Discovery</div>
            <h2 class="sec-heading" style="margin-bottom:0;">Explore Premium Tiles Collection</h2>
          </div>
          <div class="explore-tabs" id="exploreTabs">
            <button class="explore-tab active" data-explore="locations">Locations</button>
            <button class="explore-tab" data-explore="effects">Effects</button>
            <button class="explore-tab" data-explore="sizes">Sizes</button>
          </div>
        </div>
        <div class="explore-grid" id="exploreGrid"></div>
      </div>
    </section>

    <!-- 4. Latest Vitrified Tiles Collection (Portrait Showcase) -->
    <section class="home-sec">
      <div class="explore-head">
        <div>
          <div class="sec-eyebrow">Latest Collection</div>
          <h2 class="sec-heading" style="margin-bottom:0;">Latest Vitrified Tiles Collection</h2>
        </div>
        <button class="sim-btn sim-btn-outline" data-view="viewCatalog">View All Collections</button>
      </div>
      <div class="collections-grid" id="homeCollectionsGrid"></div>
    </section>

    <!-- 5. Transform Your Spaces Effortlessly! (Dark Obsidian Visualizer Band) -->
    <section class="visualizer-band">
      <div class="home-sec">
        <div class="viz-grid">
          <div>
            <div class="sec-eyebrow" style="color:#e4bc7e;">Simpolo Tiles Design At Your Fingertips</div>
            <h2 class="sec-heading" style="color:#fff;">Transform Your Spaces Effortlessly!</h2>
            <p class="sec-copy" style="color:#b8bcc7; margin-bottom:28px;">
              Simpolo's Digital Showroom and Virtual Space Creator offer a seamless way to select tiles and design rooms in ultra-realistic 3D. Compare floor and wall combinations live, test straight or staggered joints with custom grout tones, inspect sibling faces, and calculate exact box counts and adhesive requirements instantly.
            </p>
            <button class="sim-btn sim-btn-white" data-view="viewStudio">Open Virtual Space Creator</button>
          </div>

          <div class="viz-cards">
            <div class="viz-portal" data-view="viewCatalog">
              <div>
                <div class="viz-portal-kicker">Simpolo</div>
                <div class="viz-portal-title">Digital Showroom</div>
                <p class="viz-portal-desc">Search all 12,000+ indexed materials by series, look, and slab size with 6x pan-and-zoom texture inspection.</p>
              </div>
              <div class="viz-portal-cta">Discover Showroom &#8594;</div>
            </div>

            <div class="viz-portal" data-view="viewStudio">
              <div>
                <div class="viz-portal-kicker">Simpolo</div>
                <div class="viz-portal-title">Virtual Space Creator</div>
                <p class="viz-portal-desc">Preview tiles live in a 3D cutaway room with camera presets, lighting moods, surface finishes, and PNG snapshot export.</p>
              </div>
              <div class="viz-portal-cta">Launch 3D Creator &#8594;</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. Start Your Premium Tiles Journey -->
    <section class="home-sec">
      <div class="sec-eyebrow">Seamless Workflow</div>
      <h2 class="sec-heading">Start Your Surface &amp; Procurement Journey</h2>
      <div class="journey-grid">
        <div class="journey-card" data-view="viewCatalog">
          <div class="journey-num mono">01</div>
          <div>
            <div class="journey-title">Full Catalogues</div>
            <div class="journey-sub">Browse all 21 Simpolo collections with instant search &amp; 6x surface zoom.</div>
          </div>
        </div>
        <div class="journey-card" data-view="viewStudio">
          <div class="journey-num mono">02</div>
          <div>
            <div class="journey-title">Virtual Space 3D</div>
            <div class="journey-sub">Apply floor, feature wall, and side wall slabs with realistic grout &amp; finish presets.</div>
          </div>
        </div>
        <div class="journey-card" data-view="viewBoq">
          <div class="journey-num mono">03</div>
          <div>
            <div class="journey-title">Tiles Calculator</div>
            <div class="journey-sub">Auto-calculate piece counts, boxes, 100mm skirting cuts, adhesive bags, and grout kg.</div>
          </div>
        </div>
        <div class="journey-card" id="journeyExportCsv">
          <div class="journey-num mono">04</div>
          <div>
            <div class="journey-title">Procurement Export</div>
            <div class="journey-sub">Download Excel-ready BOQ `.csv` files or print clean client quotations with GST.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 7. Official-style Dark Footer -->
    <footer class="sim-footer">
      <div class="footer-inner">
        <div>
          <div class="brand-wordmark" style="color:#fff; margin-bottom:14px;">SIMPOLO<span class="brand-dot"></span></div>
          <p style="font-size:13px; line-height:1.65; margin:0; max-width:340px;">
            Interactive Vitrified Tiles Showroom, GPU 3D Virtual Space Creator, and Bill of Quantities Studio powered by your local indexed Simpolo surface library.
          </p>
        </div>
        <div>
          <div class="footer-title">Quick Links</div>
          <div class="footer-links">
            <button class="footer-btn" data-view="viewHome">Home</button>
            <button class="footer-btn" data-view="viewCatalog">Digital Showroom (Tiles)</button>
            <button class="footer-btn" data-view="viewStudio">Virtual Space Creator</button>
            <button class="footer-btn" data-view="viewBoq">Tiles &amp; BOQ Calculator</button>
          </div>
        </div>
        <div>
          <div class="footer-title">Featured Collections</div>
          <div class="footer-links" id="footerCollections"></div>
        </div>
        <div>
          <div class="footer-title">Local Studio Runtime</div>
          <p style="font-size:12.5px; line-height:1.65; margin:0;">
            Serving local PBR textures directly from <code style="color:#e4bc7e;">web_assets/</code> and catalog specifications from <code style="color:#e4bc7e;">full_catalog.json</code>.
          </p>
        </div>
      </div>
      <div class="footer-bottom">
        <div>Simpolo Interactive 3D Visualizer &amp; BOQ Studio</div>
        <div>WebGL2 GPU Tile Shader &bull; Live INR Procurement Estimator</div>
      </div>
    </footer>
  </div>

  <!-- ==================== VIEW 1: VIRTUAL SPACE CREATOR (3D ROOM STUDIO) ==================== -->
  <main class="app-view" id="viewStudio">
    <div class="studio-shell">
      <!-- LEFT DOCK -->
      <aside class="dock dock-left">
        <div class="dock-head">
          <div class="dock-title">
            <span>Target Surface</span>
            <span style="color:var(--accent); font-size:9.5px;">Select to edit</span>
          </div>
          <div class="surface-stack">
            <button class="surf-card active" data-surface="floor" id="surfCard_floor">
              <img class="surf-thumb" id="surfThumb_floor" src="" alt="" />
              <div style="min-width:0;">
                <div class="surf-role">Floor</div>
                <div class="surf-sku" id="surfName_floor">Loading...</div>
                <div class="surf-meta mono" id="surfMeta_floor">—</div>
              </div>
              <span class="surf-dot"></span>
            </button>
            <button class="surf-card" data-surface="backWall" id="surfCard_backWall">
              <img class="surf-thumb" id="surfThumb_backWall" src="" alt="" />
              <div style="min-width:0;">
                <div class="surf-role">Feature Wall</div>
                <div class="surf-sku" id="surfName_backWall">Loading...</div>
                <div class="surf-meta mono" id="surfMeta_backWall">—</div>
              </div>
              <span class="surf-dot"></span>
            </button>
            <button class="surf-card" data-surface="sideWall" id="surfCard_sideWall">
              <img class="surf-thumb" id="surfThumb_sideWall" src="" alt="" />
              <div style="min-width:0;">
                <div class="surf-role">Side Wall</div>
                <div class="surf-sku" id="surfName_sideWall">Loading...</div>
                <div class="surf-meta mono" id="surfMeta_sideWall">—</div>
              </div>
              <span class="surf-dot"></span>
            </button>
          </div>
        </div>

        <div class="mini-filters">
          <input class="input" id="studioSearch" type="search" placeholder="Search 12,000+ SKUs, series, size..." />
          <div class="g-2">
            <select class="select" id="studioSeries"><option value="All">All Series</option></select>
            <select class="select" id="studioSize"><option value="All">All Sizes</option></select>
          </div>
          <div class="swatch-count">
            <span id="studioSwatchCount">Loading library...</span>
            <span style="color:var(--accent); font-weight:700;" id="activeTargetHint">Applying to: Floor</span>
          </div>
        </div>

        <div class="dock-scroll">
          <div class="swatch-grid" id="studioSwatchGrid"></div>
          <div style="margin-top:12px;">
            <button class="btn-ghost" id="studioLoadMore" style="display:none;">Load More Swatches</button>
          </div>
        </div>
      </aside>

      <!-- CENTER 3D VIEWPORT -->
      <section class="viewport-stage" id="viewportStage">
        <div id="canvasHost"></div>

        <div class="hud-top-left">
          <div class="hud-group" aria-label="Camera Presets">
            <button class="hud-btn active" data-cam="iso">Corner Iso</button>
            <button class="hud-btn" data-cam="floor">Floor</button>
            <button class="hud-btn" data-cam="back">Feature Wall</button>
            <button class="hud-btn" data-cam="side">Side Wall</button>
          </div>
          <div class="hud-group" aria-label="Lighting Mood">
            <button class="hud-btn active" data-mood="daylight">Daylight</button>
            <button class="hud-btn" data-mood="warm">Warm</button>
            <button class="hud-btn" data-mood="studio">Studio</button>
          </div>
        </div>

        <div class="hud-top-right">
          <div class="hud-group">
            <button class="hud-btn" id="btnSnapshot" title="Save PNG screenshot">Snapshot</button>
            <button class="hud-btn" id="btnFullscreen" title="Toggle Fullscreen">Fullscreen</button>
          </div>
        </div>

        <div class="hud-bottom">
          <div class="hud-telemetry">
            <div class="hud-tel-title">
              <span class="hud-tel-tag" id="hudSurfaceTag">Floor</span>
              <span id="hudSkuName">Loading surface...</span>
            </div>
            <div class="hud-tel-sub mono" id="hudFaceInfo">Detecting GPU shader faces...</div>
          </div>
          <div class="hud-hint">Left-drag: Orbit &bull; Right-drag: Pan &bull; Scroll: Zoom</div>
        </div>
      </section>

      <!-- RIGHT DOCK -->
      <aside class="dock dock-right">
        <div class="insp-tabs">
          <button class="insp-tab active" data-tab="tabLayout">Layout</button>
          <button class="insp-tab" data-tab="tabFinish">Finish</button>
          <button class="insp-tab" data-tab="tabBoq">Live BOQ</button>
        </div>

        <div class="dock-scroll">
          <!-- TAB 1: LAYOUT -->
          <div class="insp-pane active" id="tabLayout">
            <div class="ctrl-section">
              <div class="ctrl-heading">Room Dimensions (m)</div>
              <div class="preset-pills">
                <button class="preset-chip" data-room-preset="5,4,3">Living 5×4</button>
                <button class="preset-chip" data-room-preset="4,3.5,3">Bedroom 4×3.5</button>
                <button class="preset-chip" data-room-preset="3,2.4,2.8">Bath 3×2.4</button>
                <button class="preset-chip" data-room-preset="8,6,3.4">Lobby 8×6</button>
              </div>
              <div class="g-3">
                <div>
                  <label class="field-label" for="roomW">Width</label>
                  <input class="input mono" id="roomW" type="number" min="2" max="20" step="0.1" value="5.0" />
                </div>
                <div>
                  <label class="field-label" for="roomD">Depth</label>
                  <input class="input mono" id="roomD" type="number" min="2" max="20" step="0.1" value="4.0" />
                </div>
                <div>
                  <label class="field-label" for="roomH">Height</label>
                  <input class="input mono" id="roomH" type="number" min="2.2" max="6" step="0.1" value="3.0" />
                </div>
              </div>
            </div>

            <div class="ctrl-section">
              <div class="ctrl-heading">Tile Laying &amp; Grout</div>
              <div class="field-label"><span>Layout Pattern</span></div>
              <div class="seg-control">
                <button class="seg-btn active" data-pattern="grid">Straight Grid</button>
                <button class="seg-btn" data-pattern="staggered">Staggered 50%</button>
              </div>

              <label class="field-label" for="groutMm">
                <span>Grout Joint Width</span>
                <span class="mono" id="groutMmVal">2.0 mm</span>
              </label>
              <input class="range" id="groutMm" type="range" min="0" max="10" step="0.5" value="2.0" />

              <div class="field-label"><span>Grout Tone</span></div>
              <div class="grout-row">
                <button class="grout-dot" data-grout-hex="#f5f5f4" style="background:#f5f5f4;" title="Snow White"></button>
                <button class="grout-dot active" data-grout-hex="#e2dfd9" style="background:#e2dfd9;" title="Warm Ivory"></button>
                <button class="grout-dot" data-grout-hex="#b5b2aa" style="background:#b5b2aa;" title="Stone Grey"></button>
                <button class="grout-dot" data-grout-hex="#78756e" style="background:#78756e;" title="Cement"></button>
                <button class="grout-dot" data-grout-hex="#2d2e32" style="background:#2d2e32;" title="Charcoal"></button>
                <input class="color-pill" id="groutColor" type="color" value="#e2dfd9" title="Custom Grout Color" />
              </div>
            </div>

            <div class="ctrl-section">
              <div class="ctrl-heading">Openings, Skirting &amp; Wastage</div>
              <div class="g-2">
                <div>
                  <label class="field-label" for="openBack">Back Openings (m²)</label>
                  <input class="input mono" id="openBack" type="number" min="0" max="50" step="0.1" value="0" />
                </div>
                <div>
                  <label class="field-label" for="openSide">Side Openings (m²)</label>
                  <input class="input mono" id="openSide" type="number" min="0" max="50" step="0.1" value="0" />
                </div>
              </div>

              <label class="field-label" for="wastagePct">
                <span>Base Wastage Allowance</span>
                <span class="mono" id="wastagePctVal">10%</span>
              </label>
              <input class="range" id="wastagePct" type="range" min="0" max="25" step="1" value="10" />

              <div class="switch-row" style="margin-top:6px;">
                <span>100mm Floor Skirting</span>
                <label class="switch">
                  <input id="toggleSkirting" type="checkbox" checked />
                  <span class="slider-pill"></span>
                </label>
              </div>
              <select class="select" id="skirtingMode" style="margin-top:4px;">
                <option value="4wall">Full 4-Wall Room Perimeter — 2×(W+D)</option>
                <option value="2wall">2 Rendered Walls Only — (W+D)</option>
              </select>
            </div>
          </div>

          <!-- TAB 2: FINISH -->
          <div class="insp-pane" id="tabFinish">
            <div class="ctrl-section">
              <div class="ctrl-heading">Surface Finish Preset</div>
              <div class="finish-grid">
                <button class="finish-card active" data-finish="catalog">
                  <div class="finish-name">Catalog Default</div>
                  <div class="finish-desc">Indexed PBR values</div>
                </button>
                <button class="finish-card" data-finish="gloss">
                  <div class="finish-name">High-Gloss</div>
                  <div class="finish-desc">Mirror clearcoat</div>
                </button>
                <button class="finish-card" data-finish="satin">
                  <div class="finish-name">Satin / Carving</div>
                  <div class="finish-desc">Soft architectural sheen</div>
                </button>
                <button class="finish-card" data-finish="matt">
                  <div class="finish-name">Soft Matt</div>
                  <div class="finish-desc">Low glare velvet</div>
                </button>
                <button class="finish-card" data-finish="rustic" style="grid-column: span 2;">
                  <div class="finish-name">Rustic / Textured Stone</div>
                  <div class="finish-desc">High roughness, zero clearcoat for outdoor / slate look</div>
                </button>
              </div>
            </div>

            <div class="ctrl-section">
              <div class="ctrl-heading">GPU Shader Realism</div>
              <div class="switch-row">
                <span>Sibling Face Cycling (R1/R2/R3)</span>
                <label class="switch">
                  <input id="toggleCycleFaces" type="checkbox" checked />
                  <span class="slider-pill"></span>
                </label>
              </div>
              <div class="switch-row">
                <span>Stretch-Free Tile Rotation</span>
                <label class="switch">
                  <input id="toggleTileRotate" type="checkbox" checked />
                  <span class="slider-pill"></span>
                </label>
              </div>

              <label class="field-label" for="reliefSlider">
                <span>Surface Grain Relief</span>
                <span class="mono" id="reliefVal">1.00</span>
              </label>
              <input class="range" id="reliefSlider" type="range" min="0" max="2.5" step="0.05" value="1.0" />
            </div>

            <div class="ctrl-section">
              <div class="ctrl-heading">Scene Lighting</div>
              <label class="field-label" for="lightSlider">
                <span>Key Light Intensity</span>
                <span class="mono" id="lightVal">1.35</span>
              </label>
              <input class="range" id="lightSlider" type="range" min="0.4" max="2.5" step="0.05" value="1.35" />

              <label class="field-label" for="exposureSlider">
                <span>Camera Exposure</span>
                <span class="mono" id="exposureVal">1.05</span>
              </label>
              <input class="range" id="exposureSlider" type="range" min="0.6" max="1.6" step="0.05" value="1.05" />
            </div>
          </div>

          <!-- TAB 3: LIVE BOQ -->
          <div class="insp-pane" id="tabBoq">
            <div class="switch-row" style="padding-top:0; margin-bottom:8px;">
              <span style="font-weight:600;">Include 18% GST Preview</span>
              <label class="switch">
                <input id="toggleGst" type="checkbox" />
                <span class="slider-pill"></span>
              </label>
            </div>
            <div class="boq-card" id="boqSummary">Loading BOQ...</div>
            <div class="g-2" style="margin-top:10px;">
              <button class="btn-primary" id="exportBoqBtn">Copy Summary</button>
              <button class="btn-dark" id="exportCsvBtn">Export CSV</button>
            </div>
            <div style="margin-top:8px;">
              <button class="btn-ghost" id="openFullBoqBtn">Open Full BOQ &amp; Print Quote</button>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </main>

  <!-- ==================== VIEW 2: DIGITAL SHOWROOM (FULL CATALOG) ==================== -->
  <section class="app-view" id="viewCatalog">
    <div class="container">
      <div class="catalog-banner">
        <div class="catalog-banner-bg" id="catHeroBg"></div>
        <div class="catalog-banner-inner">
          <div class="sec-eyebrow" style="color:#e4bc7e;">Simpolo Digital Showroom</div>
          <h1 id="catHeroTitle">Explore Every Surface Series</h1>
          <p id="catHeroDesc">Filter across your complete indexed catalog, inspect textures up to 6x zoom, and assign any slab directly to your 3D room's Floor, Feature Wall, or Side Wall.</p>
          <div class="series-pills" id="heroSeriesPills"></div>
        </div>
      </div>

      <div class="catalog-toolbar">
        <div class="toolbar-grid">
          <input class="input" id="searchInput" type="search" placeholder="Search SKU name, series, finish, or size (e.g. 600x1200)..." />
          <select class="select" id="seriesFilter"><option value="All">All Series</option></select>
          <select class="select" id="sizeFilter"><option value="All">All Sizes</option></select>
          <span class="mono" style="font-size:12px; color:var(--muted); white-space:nowrap;" id="catalogCount">Loading...</span>
        </div>
        <div class="filter-bar" id="lookTabs"></div>
      </div>

      <div class="cards" id="skuCards"></div>
      <div class="load-more-wrap">
        <button class="sim-btn sim-btn-outline" id="loadMoreBtn" style="display:none;">Load More SKUs</button>
      </div>
    </div>
  </section>

  <!-- ==================== VIEW 3: TILES CALCULATOR (BOQ SHEET) ==================== -->
  <section class="app-view" id="viewBoq">
    <div class="container">
      <div class="boq-sheet-card">
        <div class="boq-sheet-head">
          <div>
            <div class="sec-eyebrow">Simpolo Tiles Calculator &amp; BOQ</div>
            <h1 class="serif" style="margin:4px 0 4px; font-size:34px; font-weight:600;">Procurement Bill of Quantities</h1>
            <div style="font-size:12.5px; color:var(--muted);" id="boqSheetSubtitle">Room dimensions &amp; layout details</div>
          </div>
          <div class="no-print" style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
            <label style="display:inline-flex; align-items:center; gap:7px; font-size:12px; font-weight:700; margin-right:6px;">
              <input id="toggleGstFull" type="checkbox" /> +18% GST
            </label>
            <button class="sim-btn sim-btn-outline" style="padding:9px 16px;" id="fullCopyBtn">Copy Summary</button>
            <button class="sim-btn sim-btn-dark" style="padding:9px 16px;" id="fullCsvBtn">Download CSV</button>
            <button class="sim-btn sim-btn-dark" style="padding:9px 16px; background:var(--accent); border-color:var(--accent);" id="fullPrintBtn">Print / Save PDF</button>
          </div>
        </div>

        <div class="kpi-grid" id="boqFullKpis"></div>
        <div class="boq-table-wrap" id="boqFullTableWrap"></div>
      </div>
    </div>
  </section>

  <!-- ==================== 6X TEXTURE INSPECTOR MODAL ==================== -->
  <div class="modal-backdrop" id="inspectorModal" aria-hidden="true">
    <div class="modal-box">
      <div class="modal-stage" id="modalStage">
        <img id="modalImg" src="" alt="Texture preview" />
        <div class="modal-stage-hint">Scroll or slide to zoom (up to 6x) &bull; Drag to pan</div>
      </div>
      <div class="modal-info">
        <div>
          <div class="modal-head">
            <div>
              <div class="card-series" id="modalSeries"></div>
              <h3 class="serif" style="margin:4px 0 0; font-size:26px; font-weight:600;" id="modalTitle"></h3>
            </div>
            <button class="modal-close" id="modalCloseBtn" title="Close">&times;</button>
          </div>
          <div class="spec-grid" id="modalSpecs"></div>
          <div class="zoom-ctrl">
            <div class="field-label" style="margin-top:0;">
              <span>Magnification: <strong class="mono" id="modalZoomLabel">1.0x</strong></span>
              <button class="preset-chip" id="modalResetZoom">Reset 1x</button>
            </div>
            <input class="range" id="modalZoomSlider" type="range" min="1" max="6" step="0.1" value="1" />
          </div>
        </div>
        <div>
          <div class="ctrl-heading" style="margin-bottom:6px;">Apply Directly to 3D Room</div>
          <div class="g-3">
            <button class="btn-primary" data-modal-apply="floor">Floor</button>
            <button class="btn-dark" data-modal-apply="backWall">Feature Wall</button>
            <button class="btn-dark" data-modal-apply="sideWall">Side Wall</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="toast" id="toastEl"></div>

  <script type="module">
    import * as THREE from "three";
    import { OrbitControls } from "three/addons/controls/OrbitControls.js";
    import { computeBOQ, flagText, boqToCsv, readTileSpec } from "./boq.mjs";

    const CATALOG_PAGE_SIZE = 48;
    const STUDIO_PAGE_SIZE = 36;
    const FACE_TEX_SIZE = 512;

    const FINISH_PRESETS = {
      satin:  { roughness: 0.34, metalness: 0.02, clearcoat: 0.22, clearcoatRoughness: 0.28 },
      gloss:  { roughness: 0.08, metalness: 0.03, clearcoat: 0.85, clearcoatRoughness: 0.06 },
      matt:   { roughness: 0.65, metalness: 0.01, clearcoat: 0.05, clearcoatRoughness: 0.55 },
      rustic: { roughness: 0.82, metalness: 0.01, clearcoat: 0.00, clearcoatRoughness: 0.70 },
    };

    const LIGHTING_MOODS = {
      daylight: { bg: "#111214", hemiSky: "#ffffff", hemiGround: "#64748b", hemiInt: 0.82, dirColor: "#fff8f0", dirInt: 1.35, exp: 1.05 },
      warm:     { bg: "#181412", hemiSky: "#fff1dc", hemiGround: "#59483b", hemiInt: 0.75, dirColor: "#ffd6a0", dirInt: 1.45, exp: 1.02 },
      studio:   { bg: "#0e1014", hemiSky: "#e2e8f0", hemiGround: "#334155", hemiInt: 0.96, dirColor: "#f8fafc", dirInt: 1.20, exp: 1.12 },
    };

    // Flagship Simpolo Hero Copy matching official simpolo.com collections
    const FLAGSHIP_HERO_META = [
      { key: "glyphstone", title: "Glyphstone Collection", sub: "Inspired By Petroglyphs — architectural carved textures engineered for timeless statement walls and floors." },
      { key: "venitto",    title: "Venitto Collection",    sub: "Unique Terrazzo Designs — high-abrasion vitrified surfaces crafted for bold residential and commercial spaces." },
      { key: "alchimia",   title: "Alchimia Collection",   sub: "Blend of Raw Potential & Artistry — refined mineral grains balanced with contemporary European sensibility." },
      { key: "sparko",     title: "Sparko Collection",     sub: "Make Your Home Look Expensive — luminous crystalline finishes designed to elevate modern interiors." },
      { key: "marmorica",  title: "Marmorica Collection",  sub: "Exclusive Marble Inspired Collection — natural veining fidelity paired with zero-porosity vitrified performance." },
    ];

    const ROOM_LOCATIONS = [
      { name: "Living Room Tiles",  dims: "5,4,3",     kicker: "5.0 × 4.0 m Preset", seriesPref: "marmorica" },
      { name: "Bathroom Tiles",     dims: "3,2.4,2.8", kicker: "3.0 × 2.4 m Preset", seriesPref: "alchimia" },
      { name: "Bedroom Tiles",      dims: "4,3.5,3",   kicker: "4.0 × 3.5 m Preset", seriesPref: "venitto" },
      { name: "Kitchen Tiles",      dims: "3.8,3,3",   kicker: "3.8 × 3.0 m Preset", seriesPref: "sparko" },
      { name: "Balcony Tiles",      dims: "4.5,2.2,3", kicker: "4.5 × 2.2 m Preset", seriesPref: "courtyard" },
      { name: "Outdoor & Deck",     dims: "8,6,3.4",   kicker: "8.0 × 6.0 m Preset", seriesPref: "rockdeck" },
    ];

    let catalogItems = [];
    let catalogById = new Map();
    let seriesMap = new Map();
    let filteredCatalog = [];
    let catalogVisible = CATALOG_PAGE_SIZE;
    let filteredStudio = [];
    let studioVisible = STUDIO_PAGE_SIZE;
    let activeLook = "All";
    let activeSurfaceKey = "floor";
    let includeGst = false;
    let currentViewId = "viewHome";

    let heroSlides = [];
    let heroIndex = 0;
    let heroTimer = null;

    const siblingIndex = new Map();
    const arrayTexCache = new Map();
    const imagePromiseCache = new Map();

    // ---- Utilities ----
    function escHtml(v) {
      return String(v ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function formatSeriesTitle(s) {
      return String(s || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
    }

    let toastTimer = null;
    function showToast(msg) {
      const el = document.getElementById("toastEl");
      el.textContent = msg;
      el.classList.add("show");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => el.classList.remove("show"), 2200);
    }

    function numInput(id, fallback, min = -Infinity, max = Infinity, writeBack = false) {
      const el = document.getElementById(id);
      const raw = parseFloat(el?.value);
      const val = Math.min(max, Math.max(min, Number.isFinite(raw) ? raw : fallback));
      if (writeBack && el) el.value = String(val);
      return val;
    }

    function normalizeDesignKey(item) {
      const raw = String(item.name || "").toLowerCase().replace(/_/g, " ");
      const stripped = raw
        .replace(/\b(r[1-9]|f[1-9]|face[\s-]*[1-9]|closeup[\s-]*[0-9]+)\b/gi, " ")
        .replace(/[^a-z0-9]+/g, " ")
        .trim();
      const spec = readTileSpec(item);
      const dim = `${spec.widthMm || 600}x${spec.heightMm || 1200}`;
      return `${item.series || ""}|${dim}|${stripped}`;
    }

    function rebuildSiblingIndex(items) {
      siblingIndex.clear();
      const grouped = new Map();
      for (const it of items) {
        if (!it.pbr?.maps?.albedo) continue;
        const key = normalizeDesignKey(it);
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(it);
      }
      for (const [key, list] of grouped.entries()) {
        const seen = new Set();
        const unique = [];
        for (const m of list) {
          const src = m.pbr.maps.albedo;
          if (!seen.has(src)) { seen.add(src); unique.push(m); }
        }
        unique.sort((a, b) => String(a.name || "").localeCompare(String(b.name || "")));
        siblingIndex.set(key, unique);
      }
    }

    function getSiblingFaces(sku) {
      if (!sku) return [];
      const matches = siblingIndex.get(normalizeDesignKey(sku));
      return matches && matches.length ? matches : [sku];
    }

    function loadHtmlImage(src) {
      if (imagePromiseCache.has(src)) return imagePromiseCache.get(src);
      const p = new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => resolve(img);
        img.onerror = () => resolve(null);
        img.src = src;
      });
      imagePromiseCache.set(src, p);
      return p;
    }

    function pickSampleImageForSeries(seriesKey, fallbackIdx = 0) {
      const list = seriesMap.get(seriesKey);
      if (list && list.length) {
        const found = list.find((i) => i.pbr?.maps?.albedo);
        if (found) return found.pbr.maps.albedo;
      }
      const fb = catalogItems[fallbackIdx % Math.max(1, catalogItems.length)];
      return fb?.pbr?.maps?.albedo || "";
    }

    // ==================== HOMEPAGE BUILDERS ====================
    function buildHomeHero() {
      const slides = [];
      for (const meta of FLAGSHIP_HERO_META) {
        const list = seriesMap.get(meta.key);
        if (list && list.length) {
          const sample = list.find((i) => i.pbr?.maps?.albedo) || list[0];
          slides.push({
            series: meta.key,
            title: meta.title,
            sub: meta.sub,
            count: list.length,
            img: sample.pbr?.maps?.albedo || "",
            skuId: sample.id,
          });
        }
      }
      if (!slides.length && catalogItems.length) {
        const firstSeries = [...seriesMap.keys()].slice(0, 5);
        firstSeries.forEach((s) => {
          const list = seriesMap.get(s);
          slides.push({
            series: s,
            title: `${formatSeriesTitle(s)} Collection`,
            sub: `${list.length} architectural tile surfaces ready to inspect at 6x zoom and preview live in 3D.`,
            count: list.length,
            img: list[0]?.pbr?.maps?.albedo || "",
            skuId: list[0]?.id,
          });
        });
      }

      heroSlides = slides;
      document.getElementById("heroSlidesHost").innerHTML = slides.map((sl, idx) => `
        <div class="hero-slide ${idx === 0 ? "active" : ""}" data-slide-idx="${idx}">
          <img class="hero-slide-img" src="${escHtml(sl.img)}" alt="${escHtml(sl.title)}" />
          <div class="hero-scrim"></div>
          <div class="hero-content">
            <div class="hero-kicker">Simpolo Flagship Series &bull; ${sl.count.toLocaleString()} Surfaces</div>
            <h1 class="hero-title">${escHtml(sl.title)}</h1>
            <p class="hero-subtitle">${escHtml(sl.sub)}</p>
            <div class="hero-cta-row">
              <button class="sim-btn sim-btn-white" data-hero-discover="${escHtml(sl.series)}">Discover More</button>
              <button class="sim-btn sim-btn-ghost-white" data-hero-try3d="${escHtml(sl.skuId)}">Try in 3D Space</button>
            </div>
          </div>
        </div>
      `).join("");

      document.getElementById("heroDots").innerHTML = slides.map((sl, idx) => `
        <button class="hero-dot ${idx === 0 ? "active" : ""}" data-dot-idx="${idx}">
          <span class="hero-dot-bar"></span>
          <span class="hero-dot-label">${escHtml(formatSeriesTitle(sl.series))}</span>
        </button>
      `).join("");

      document.getElementById("heroSlidesHost").addEventListener("click", (e) => {
        const disc = e.target.closest("[data-hero-discover]");
        if (disc) { openCatalogForSeries(disc.dataset.heroDiscover); return; }
        const tryBtn = e.target.closest("[data-hero-try3d]");
        if (tryBtn) {
          assignSkuToSurface("floor", tryBtn.dataset.heroTry3d);
          switchView("viewStudio");
        }
      });

      document.getElementById("heroDots").addEventListener("click", (e) => {
        const dot = e.target.closest("[data-dot-idx]");
        if (dot) setHeroSlide(parseInt(dot.dataset.dotIdx, 10));
      });

      startHeroTimer();
    }

    function setHeroSlide(idx) {
      if (!heroSlides.length) return;
      heroIndex = (idx + heroSlides.length) % heroSlides.length;
      document.querySelectorAll(".hero-slide").forEach((el, i) => el.classList.toggle("active", i === heroIndex));
      document.querySelectorAll(".hero-dot").forEach((el, i) => el.classList.toggle("active", i === heroIndex));
      startHeroTimer();
    }

    function startHeroTimer() {
      clearInterval(heroTimer);
      heroTimer = setInterval(() => {
        if (currentViewId === "viewHome" && heroSlides.length > 1) {
          setHeroSlide(heroIndex + 1);
        }
      }, 6500);
    }

    function buildAboutMosaic() {
      const picks = ["marmorica", "glyphstone", "venitto"].map((s, idx) => {
        const list = seriesMap.get(s);
        const item = list?.[Math.min(2, (list?.length || 1) - 1)] || catalogItems[idx];
        return { series: item?.series || s, img: item?.pbr?.maps?.albedo || "", id: item?.id };
      });
      document.getElementById("aboutMosaic").innerHTML = picks.map((p, idx) => `
        <div class="mosaic-item ${idx === 0 ? "tall" : ""}" data-mosaic-series="${escHtml(p.series)}">
          <img src="${escHtml(p.img)}" alt="${escHtml(p.series)}" loading="lazy" />
          <span class="mosaic-cap">${escHtml(formatSeriesTitle(p.series))}</span>
        </div>
      `).join("");

      document.getElementById("aboutMosaic").addEventListener("click", (e) => {
        const m = e.target.closest("[data-mosaic-series]");
        if (m) openCatalogForSeries(m.dataset.mosaicSeries);
      });
    }

    function renderExploreGrid(mode) {
      const grid = document.getElementById("exploreGrid");
      if (mode === "locations") {
        grid.innerHTML = ROOM_LOCATIONS.map((loc, idx) => `
          <div class="explore-card" data-exp-room="${escHtml(loc.dims)}" data-exp-series="${escHtml(loc.seriesPref)}">
            <img src="${escHtml(pickSampleImageForSeries(loc.seriesPref, idx * 7))}" alt="${escHtml(loc.name)}" loading="lazy" />
            <div class="explore-card-overlay">
              <div class="explore-card-kicker">${escHtml(loc.kicker)}</div>
              <div class="explore-card-title">${escHtml(loc.name)}</div>
              <div class="explore-card-sub"><span>Open in Virtual Space 3D</span><span>&#8594;</span></div>
            </div>
          </div>
        `).join("");
      } else if (mode === "effects") {
        const looks = new Map();
        for (const it of catalogItems) {
          const lk = it.lookAndFeel || "Architectural";
          if (!looks.has(lk)) looks.set(lk, { count: 0, img: it.pbr?.maps?.albedo || "" });
          looks.get(lk).count++;
        }
        const entries = [...looks.entries()].sort((a, b) => b[1].count - a[1].count).slice(0, 6);
        grid.innerHTML = entries.map(([lk, info]) => `
          <div class="explore-card" data-exp-look="${escHtml(lk)}">
            <img src="${escHtml(info.img)}" alt="${escHtml(lk)}" loading="lazy" />
            <div class="explore-card-overlay">
              <div class="explore-card-kicker">Surface Effect</div>
              <div class="explore-card-title">${escHtml(lk)}</div>
              <div class="explore-card-sub"><span class="mono">${info.count.toLocaleString()} SKUs</span><span>Explore &#8594;</span></div>
            </div>
          </div>
        `).join("");
      } else {
        const sizes = new Map();
        for (const it of catalogItems) {
          const sp = readTileSpec(it);
          if (!sp.sizeKnown) continue;
          const sz = `${sp.widthMm}x${sp.heightMm}`;
          if (!sizes.has(sz)) sizes.set(sz, { count: 0, img: it.pbr?.maps?.albedo || "" });
          sizes.get(sz).count++;
        }
        const entries = [...sizes.entries()].sort((a, b) => b[1].count - a[1].count).slice(0, 6);
        grid.innerHTML = entries.map(([sz, info]) => `
          <div class="explore-card" data-exp-size="${escHtml(sz)}">
            <img src="${escHtml(info.img)}" alt="${escHtml(sz)} mm" loading="lazy" />
            <div class="explore-card-overlay">
              <div class="explore-card-kicker">Slab Format</div>
              <div class="explore-card-title mono" style="font-family:var(--font-mono); font-size:24px;">${escHtml(sz)} mm</div>
              <div class="explore-card-sub"><span class="mono">${info.count.toLocaleString()} SKUs</span><span>Browse &#8594;</span></div>
            </div>
          </div>
        `).join("");
      }
    }

    document.getElementById("exploreTabs").addEventListener("click", (e) => {
      const btn = e.target.closest("[data-explore]");
      if (!btn) return;
      document.querySelectorAll("[data-explore]").forEach((b) => b.classList.toggle("active", b === btn));
      renderExploreGrid(btn.dataset.explore);
    });

    document.getElementById("exploreGrid").addEventListener("click", (e) => {
      const card = e.target.closest(".explore-card");
      if (!card) return;
      if (card.dataset.expRoom) {
        launchRoomWithPreset(card.dataset.expRoom, card.dataset.expSeries);
      } else if (card.dataset.expLook) {
        activeLook = card.dataset.expLook;
        document.getElementById("seriesFilter").value = "All";
        document.getElementById("sizeFilter").value = "All";
        syncLookTabHighlight();
        renderFullCatalog(true);
        switchView("viewCatalog");
      } else if (card.dataset.expSize) {
        activeLook = "All";
        document.getElementById("seriesFilter").value = "All";
        document.getElementById("sizeFilter").value = card.dataset.expSize;
        syncLookTabHighlight();
        renderFullCatalog(true);
        switchView("viewCatalog");
      }
    });

    function buildHomeCollectionsAndMenus() {
      const preferredOrder = ["venitto", "glyphstone", "alchimia", "sparko", "marmorica", "impero", "spectra", "ricco_2_0", "rockdeck", "courtyard"];
      const allSeries = [...seriesMap.keys()].sort();
      const ordered = [
        ...preferredOrder.filter((s) => seriesMap.has(s)),
        ...allSeries.filter((s) => !preferredOrder.includes(s)),
      ];

      // 10 Portrait Collection Cards on Home
      const showcase = ordered.slice(0, 10);
      document.getElementById("homeCollectionsGrid").innerHTML = showcase.map((s) => {
        const list = seriesMap.get(s);
        const img = pickSampleImageForSeries(s);
        return `
          <div class="col-card" data-col-series="${escHtml(s)}">
            <img src="${escHtml(img)}" alt="${escHtml(s)}" loading="lazy" />
            <div class="col-card-grad">
              <div class="col-card-label">Collection</div>
              <div class="col-card-name">${escHtml(formatSeriesTitle(s))}</div>
              <div class="col-card-meta mono">${list.length.toLocaleString()} Designs &rarr;</div>
            </div>
          </div>
        `;
      }).join("");

      document.getElementById("homeCollectionsGrid").addEventListener("click", (e) => {
        const c = e.target.closest("[data-col-series]");
        if (c) openCatalogForSeries(c.dataset.colSeries);
      });

      // Top Mega Menu Collections + Footer Collections
      const megaHtml = ordered.slice(0, 12).map((s) =>
        `<button class="mega-btn" data-mega-series="${escHtml(s)}">${escHtml(formatSeriesTitle(s))}</button>`
      ).join("") + `<button class="mega-btn" style="color:var(--accent); font-weight:700;" data-mega-series="All">All ${allSeries.length} Collections &rarr;</button>`;
      document.getElementById("megaCollectionsList").innerHTML = megaHtml;

      document.getElementById("footerCollections").innerHTML = ordered.slice(0, 6).map((s) =>
        `<button class="footer-btn" data-mega-series="${escHtml(s)}">${escHtml(formatSeriesTitle(s))} Collection</button>`
      ).join("");

      const lookList = [...new Set(catalogItems.map((i) => i.lookAndFeel).filter(Boolean))].slice(0, 8);
      document.getElementById("megaLookList").innerHTML = lookList.map((lk) =>
        `<button class="mega-btn" data-mega-look="${escHtml(lk)}">${escHtml(lk)}</button>`
      ).join("");

      document.body.addEventListener("click", (e) => {
        const ms = e.target.closest("[data-mega-series]");
        if (ms) { openCatalogForSeries(ms.dataset.megaSeries); return; }
        const ml = e.target.closest("[data-mega-look]");
        if (ml) {
          activeLook = ml.dataset.megaLook;
          document.getElementById("seriesFilter").value = "All";
          syncLookTabHighlight();
          renderFullCatalog(true);
          switchView("viewCatalog");
          return;
        }
        const lr = e.target.closest("[data-launch-room]");
        if (lr) { launchRoomWithPreset(lr.dataset.launchRoom); }
      });
    }

    function openCatalogForSeries(seriesName) {
      activeLook = "All";
      document.getElementById("sizeFilter").value = "All";
      document.getElementById("searchInput").value = "";
      document.getElementById("seriesFilter").value = seriesName || "All";
      document.querySelectorAll("#heroSeriesPills .pill-btn").forEach((b) =>
        b.classList.toggle("active", b.dataset.series === (seriesName || "All"))
      );
      if (seriesName && seriesName !== "All") {
        const count = seriesMap.get(seriesName)?.length || 0;
        document.getElementById("catHeroTitle").textContent = `${formatSeriesTitle(seriesName)} Collection (${count.toLocaleString()})`;
        const img = pickSampleImageForSeries(seriesName);
        if (img) document.getElementById("catHeroBg").style.backgroundImage = `url("${img}")`;
      } else {
        document.getElementById("catHeroTitle").textContent = `${catalogItems.length.toLocaleString()} Simpolo Surfaces`;
      }
      syncLookTabHighlight();
      renderFullCatalog(true);
      switchView("viewCatalog");
    }

    function launchRoomWithPreset(dimsCsv, preferredSeries = null) {
      const [w, d, h] = dimsCsv.split(",");
      document.getElementById("roomW").value = w;
      document.getElementById("roomD").value = d;
      document.getElementById("roomH").value = h;
      if (preferredSeries && seriesMap.has(preferredSeries)) {
        const list = seriesMap.get(preferredSeries);
        if (list[0]) assignSkuToSurface("floor", list[0].id, true);
        if (list[1]) assignSkuToSurface("backWall", list[1].id, true);
        document.getElementById("studioSeries").value = preferredSeries;
        renderStudioSwatches(true);
      }
      switchView("viewStudio");
      rebuildRoomGeometry(false);
      moveCameraToPreset("iso");
      showToast(`3D Space set to ${w}m × ${d}m × ${h}m`);
    }

    // ==================== THREE.JS SCENE & GPU TILE SHADER ====================
    const host = document.getElementById("canvasHost");
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(LIGHTING_MOODS.daylight.bg);

    const camera = new THREE.PerspectiveCamera(44, 1.5, 0.1, 100);
    camera.position.set(4.8, 3.3, 6.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.15, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.minDistance = 1.4;
    controls.maxDistance = 26;

    const hemiLight = new THREE.HemisphereLight("#ffffff", "#64748b", 0.82);
    scene.add(hemiLight);
    const dirLight = new THREE.DirectionalLight("#fff8f0", 1.35);
    dirLight.position.set(4.5, 7.2, 5.2);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(1024, 1024);
    scene.add(dirLight);
    const fillLight = new THREE.DirectionalLight("#dbeafe", 0.35);
    fillLight.position.set(-5, 3, 4);
    scene.add(fillLight);

    const floorMesh = new THREE.Mesh(new THREE.PlaneGeometry(5, 4), new THREE.MeshStandardMaterial({ color: "#d6d3cd" }));
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.receiveShadow = true;
    scene.add(floorMesh);

    const backWallMesh = new THREE.Mesh(new THREE.PlaneGeometry(5, 3), new THREE.MeshStandardMaterial({ color: "#e5e7eb" }));
    backWallMesh.receiveShadow = true;
    scene.add(backWallMesh);

    const sideWallMesh = new THREE.Mesh(new THREE.PlaneGeometry(4, 3), new THREE.MeshStandardMaterial({ color: "#cbd5e1" }));
    sideWallMesh.rotation.y = Math.PI / 2;
    sideWallMesh.receiveShadow = true;
    scene.add(sideWallMesh);

    const shellMat = new THREE.MeshStandardMaterial({ color: "#212329", roughness: 0.9, metalness: 0.04 });
    const floorSlab = new THREE.Mesh(new THREE.BoxGeometry(5, 0.12, 4), shellMat);
    const backSlab = new THREE.Mesh(new THREE.BoxGeometry(5, 3, 0.12), shellMat);
    const sideSlab = new THREE.Mesh(new THREE.BoxGeometry(0.12, 3, 4), shellMat);
    scene.add(floorSlab, backSlab, sideSlab);

    const skirtingMat = new THREE.MeshStandardMaterial({ color: "#cfc9be", roughness: 0.35, metalness: 0.02 });
    const skirtBack = new THREE.Mesh(new THREE.BoxGeometry(5, 0.1, 0.016), skirtingMat);
    const skirtSide = new THREE.Mesh(new THREE.BoxGeometry(0.016, 0.1, 4), skirtingMat);
    scene.add(skirtBack, skirtSide);

    function resizeRenderer() {
      const w = host.clientWidth;
      const h = host.clientHeight;
      if (!w || !h) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
      renderer.domElement.style.width = "100%";
      renderer.domElement.style.height = "100%";
    }
    new ResizeObserver(resizeRenderer).observe(host);

    let camAnim = null;
    function moveCameraToPreset(preset) {
      const w = numInput("roomW", 5.0, 2, 20);
      const d = numInput("roomD", 4.0, 2, 20);
      const h = numInput("roomH", 3.0, 2.2, 6);
      const span = Math.max(w, d);

      let toPos, toTarget;
      if (preset === "floor") {
        toPos = new THREE.Vector3(0.4, span * 1.15, d * 0.65);
        toTarget = new THREE.Vector3(0, 0.05, 0);
      } else if (preset === "back") {
        toPos = new THREE.Vector3(0, h * 0.52, d * 0.72 + 2.2);
        toTarget = new THREE.Vector3(0, h * 0.48, -d * 0.45);
      } else if (preset === "side") {
        toPos = new THREE.Vector3(w * 0.65 + 2.0, h * 0.52, 0.2);
        toTarget = new THREE.Vector3(-w * 0.45, h * 0.48, 0);
      } else {
        toPos = new THREE.Vector3(w * 0.78 + 1.2, h * 0.85 + 0.9, d * 0.95 + 1.8);
        toTarget = new THREE.Vector3(-w * 0.08, h * 0.36, -d * 0.08);
      }
      camAnim = { startPos: camera.position.clone(), startTarget: controls.target.clone(), endPos: toPos, endTarget: toTarget, t: 0 };
      document.querySelectorAll("[data-cam]").forEach((b) => b.classList.toggle("active", b.dataset.cam === preset));
    }

    const surfaceState = {
      floor:    { label: "Floor",        mesh: floorMesh,    widthM: 5.0, heightM: 4.0, skuId: null, pattern: "grid", groutMm: 2.0, groutHex: "#e2dfd9", finish: "catalog", renderSeq: 0 },
      backWall: { label: "Feature Wall", mesh: backWallMesh, widthM: 5.0, heightM: 3.0, skuId: null, pattern: "grid", groutMm: 2.0, groutHex: "#e2dfd9", finish: "catalog", renderSeq: 0 },
      sideWall: { label: "Side Wall",    mesh: sideWallMesh, widthM: 4.0, heightM: 3.0, skuId: null, pattern: "grid", groutMm: 2.0, groutHex: "#e2dfd9", finish: "catalog", renderSeq: 0 },
    };

    function getSurfaceSku(surfKey) { return catalogById.get(surfaceState[surfKey]?.skuId) || null; }

    function resolveFinishProps(sku, presetKey) {
      if (presetKey && FINISH_PRESETS[presetKey]) return FINISH_PRESETS[presetKey];
      const pbr = sku?.pbr || {};
      return {
        roughness: pbr.roughness ?? 0.28,
        metalness: pbr.metalness ?? 0.02,
        clearcoat: pbr.clearcoat ?? 0.25,
        clearcoatRoughness: pbr.clearcoatRoughness ?? 0.16,
      };
    }

    function applyFinishToMaterial(surfKey) {
      const cfg = surfaceState[surfKey];
      const sku = getSurfaceSku(surfKey);
      const mat = cfg?.mesh?.material;
      if (!mat || !sku) return;
      const f = resolveFinishProps(sku, cfg.finish);
      mat.roughness = f.roughness;
      mat.metalness = f.metalness;
      if ("clearcoat" in mat) mat.clearcoat = f.clearcoat;
      if ("clearcoatRoughness" in mat) mat.clearcoatRoughness = f.clearcoatRoughness;
    }

    async function getSiblingArrayTexture(sku) {
      const faces = getSiblingFaces(sku);
      const srcs = faces.map((f) => f.pbr?.maps?.albedo).filter(Boolean);
      const cacheKey = srcs.length ? srcs.join("|") : `__single__${sku.id}`;
      if (arrayTexCache.has(cacheKey)) return arrayTexCache.get(cacheKey);

      const depth = Math.max(1, srcs.length);
      const layerBytes = FACE_TEX_SIZE * FACE_TEX_SIZE * 4;
      const data = new Uint8Array(layerBytes * depth);
      const scratch = document.createElement("canvas");
      scratch.width = FACE_TEX_SIZE;
      scratch.height = FACE_TEX_SIZE;
      const sctx = scratch.getContext("2d");

      const fallbackHex = sku.pbr?.baseHex || "#d6d3cd";
      const imgs = await Promise.all(srcs.map(loadHtmlImage));

      for (let layer = 0; layer < depth; layer++) {
        sctx.clearRect(0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE);
        const img = imgs[layer];
        if (img) sctx.drawImage(img, 0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE);
        else { sctx.fillStyle = fallbackHex; sctx.fillRect(0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE); }
        data.set(sctx.getImageData(0, 0, FACE_TEX_SIZE, FACE_TEX_SIZE).data, layer * layerBytes);
      }

      const arrTex = new THREE.DataArrayTexture(data, FACE_TEX_SIZE, FACE_TEX_SIZE, depth);
      arrTex.format = THREE.RGBAFormat;
      arrTex.type = THREE.UnsignedByteType;
      arrTex.colorSpace = THREE.SRGBColorSpace;
      arrTex.magFilter = THREE.LinearFilter;
      arrTex.minFilter = THREE.LinearMipmapLinearFilter;
      arrTex.generateMipmaps = true;
      arrTex.wrapS = THREE.ClampToEdgeWrapping;
      arrTex.wrapT = THREE.ClampToEdgeWrapping;
      arrTex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      arrTex.needsUpdate = true;

      const entry = { tex: arrTex, count: depth, names: faces.map((f) => f.name) };
      arrayTexCache.set(cacheKey, entry);
      return entry;
    }

    function applyGpuTileShader(mat, uniforms) {
      mat.onBeforeCompile = (shader) => {
        Object.assign(shader.uniforms, uniforms);
        mat.userData.shaderUniforms = shader.uniforms;

        shader.vertexShader = shader.vertexShader
          .replace("#include <common>", `#include <common>\nvarying vec2 vTileSurfaceMeters;\nuniform vec2 uSurfaceMeters;`)
          .replace("#include <uv_vertex>", `#include <uv_vertex>\nvTileSurfaceMeters = uv * uSurfaceMeters;`);

        shader.fragmentShader = shader.fragmentShader
          .replace(
            "#include <common>",
            `#include <common>
             varying vec2 vTileSurfaceMeters;
             uniform highp sampler2DArray uFaceTex;
             uniform float uFaceCount;
             uniform vec2 uTileSizeM;
             uniform float uGroutM;
             uniform float uStaggered;
             uniform float uCycleFaces;
             uniform float uRotateEnabled;
             uniform float uRelief;
             uniform vec3 uGroutColor;

             float tileHash21(vec2 p) {
               p = fract(p * vec2(123.34, 456.21));
               p += dot(p, p + 45.32);
               return fract(p.x * p.y);
             }
             vec2 rotateTileUv(vec2 uvCoord, float turns) {
               vec2 centered = uvCoord - 0.5;
               if (turns < 0.5) return uvCoord;
               if (turns < 1.5) return vec2(-centered.y, centered.x) + 0.5;
               if (turns < 2.5) return vec2(-centered.x, -centered.y) + 0.5;
               return vec2(centered.y, -centered.x) + 0.5;
             }`
          )
          .replace(
            "#include <map_fragment>",
            `vec2 pitchM = max(uTileSizeM + vec2(uGroutM), vec2(0.05));
             float rowIdx = floor(vTileSurfaceMeters.y / pitchM.y);
             float staggerShift = (uStaggered > 0.5 && mod(abs(rowIdx), 2.0) > 0.5) ? pitchM.x * 0.5 : 0.0;
             float shiftedX = vTileSurfaceMeters.x + staggerShift;
             float colIdx = floor(shiftedX / pitchM.x);
             vec2 cellId = vec2(colIdx, rowIdx);

             vec2 localPosM = vec2(shiftedX - colIdx * pitchM.x, vTileSurfaceMeters.y - rowIdx * pitchM.y);
             float halfGrout = max(uGroutM * 0.5, 0.0);
             float edgeDist = min(min(localPosM.x, pitchM.x - localPosM.x), min(localPosM.y, pitchM.y - localPosM.y));
             float aaWidth = max(fwidth(edgeDist), 0.0005);
             float simpoloGroutMask = (uGroutM > 0.00001)
               ? (1.0 - smoothstep(max(halfGrout - aaWidth, 0.0), halfGrout + aaWidth, edgeDist))
               : 0.0;

             vec2 innerUv = clamp((localPosM - vec2(halfGrout)) / max(pitchM - vec2(uGroutM), vec2(0.01)), vec2(0.002), vec2(0.998));
             float hFace = tileHash21(cellId + vec2(17.3, 9.1));
             float hRot = tileHash21(cellId + vec2(53.7, 29.4));

             float layerIdx = (uCycleFaces > 0.5 && uFaceCount > 1.5) ? clamp(floor(hFace * uFaceCount), 0.0, uFaceCount - 1.0) : 0.0;
             float isSquareTile = step(abs(uTileSizeM.x - uTileSizeM.y), 0.01);
             float rotTurns = (uRotateEnabled > 0.5) ? ((isSquareTile > 0.5) ? floor(hRot * 4.0) : (floor(hRot * 2.0) * 2.0)) : 0.0;
             vec2 sampledUv = rotateTileUv(innerUv, rotTurns);

             vec3 tileLinear = texture(uFaceTex, vec3(sampledUv, layerIdx)).rgb;
             vec3 finalAlbedo = mix(tileLinear, uGroutColor, simpoloGroutMask);
             float luma = dot(tileLinear, vec3(0.299, 0.587, 0.114));
             finalAlbedo = clamp(finalAlbedo + vec3((luma - 0.5) * 0.18 * uRelief) * (1.0 - simpoloGroutMask), 0.0, 1.0);
             diffuseColor.rgb *= finalAlbedo;`
          )
          .replace("#include <roughnessmap_fragment>", `#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.92, simpoloGroutMask);`);
      };
      mat.customProgramCacheKey = () => "simpolo-gpu-tile-shader-v4";
    }

    function updateSurfaceCardsAndHud() {
      Object.keys(surfaceState).forEach((k) => {
        const cfg = surfaceState[k];
        const sku = getSurfaceSku(k);
        document.getElementById(`surfCard_${k}`).classList.toggle("active", k === activeSurfaceKey);
        if (!sku) return;
        const spec = readTileSpec(sku);
        document.getElementById(`surfThumb_${k}`).src = sku.pbr?.maps?.albedo || "";
        document.getElementById(`surfName_${k}`).textContent = sku.name || sku.id;
        document.getElementById(`surfMeta_${k}`).textContent =
          `${sku.series || "—"} • ${spec.sizeKnown ? `${spec.widthMm}×${spec.heightMm}` : "Size N/A"}`;
      });

      const cfg = surfaceState[activeSurfaceKey];
      const sku = getSurfaceSku(activeSurfaceKey);
      document.getElementById("activeTargetHint").textContent = `Applying to: ${cfg.label}`;
      document.getElementById("hudSurfaceTag").textContent = cfg.label;
      if (sku) {
        const spec = readTileSpec(sku);
        const faces = getSiblingFaces(sku);
        const cycle = document.getElementById("toggleCycleFaces").checked;
        const rot = document.getElementById("toggleTileRotate").checked;
        const isSq = spec.sizeKnown && Math.abs(spec.widthMm - spec.heightMm) <= 10;
        const rotLabel = !rot ? "OFF" : (isSq ? "0/90/180/270°" : "0/180°");
        document.getElementById("hudSkuName").textContent = `${formatSeriesTitle(sku.series)} — ${sku.name}`;
        document.getElementById("hudFaceInfo").textContent =
          `${spec.sizeKnown ? `${spec.widthMm}×${spec.heightMm}mm` : "Size unknown"} • ${faces.length} GPU face${faces.length > 1 ? "s" : ""} • Cycle ${cycle ? "ON" : "OFF"} • Rot ${rotLabel}`;
      }

      document.querySelectorAll(".swatch-card").forEach((el) => {
        el.classList.toggle("applied", el.dataset.swatchId === cfg.skuId);
      });
    }

    function syncShaderUniformsOnly() {
      const cycle = document.getElementById("toggleCycleFaces").checked ? 1.0 : 0.0;
      const rot = document.getElementById("toggleTileRotate").checked ? 1.0 : 0.0;
      const relief = numInput("reliefSlider", 1.0, 0, 2.5);
      document.getElementById("reliefVal").textContent = relief.toFixed(2);

      Object.keys(surfaceState).forEach((k) => {
        const cfg = surfaceState[k];
        const u = cfg.mesh.material?.userData?.shaderUniforms;
        if (!u) return;
        u.uSurfaceMeters.value.set(cfg.widthM, cfg.heightM);
        u.uGroutM.value = cfg.groutMm / 1000;
        u.uStaggered.value = cfg.pattern === "staggered" ? 1.0 : 0.0;
        u.uGroutColor.value.set(cfg.groutHex);
        u.uCycleFaces.value = cycle;
        u.uRotateEnabled.value = rot;
        u.uRelief.value = relief;
      });
      updateSurfaceCardsAndHud();
    }

    async function renderSurfaceMaterial(surfKey) {
      const cfg = surfaceState[surfKey];
      const sku = getSurfaceSku(surfKey);
      if (!sku) return;

      const mySeq = ++cfg.renderSeq;
      const spec = readTileSpec(sku);
      const tileW_m = (spec.widthMm || 600) / 1000;
      const tileH_m = (spec.heightMm || 1200) / 1000;
      const arrEntry = await getSiblingArrayTexture(sku);
      if (mySeq !== cfg.renderSeq) return;

      const finish = resolveFinishProps(sku, cfg.finish);
      const mat = new THREE.MeshPhysicalMaterial({
        color: new THREE.Color("#ffffff"),
        roughness: finish.roughness,
        metalness: finish.metalness,
        clearcoat: finish.clearcoat,
        clearcoatRoughness: finish.clearcoatRoughness,
      });

      applyGpuTileShader(mat, {
        uFaceTex: { value: arrEntry.tex },
        uFaceCount: { value: arrEntry.count },
        uSurfaceMeters: { value: new THREE.Vector2(cfg.widthM, cfg.heightM) },
        uTileSizeM: { value: new THREE.Vector2(tileW_m, tileH_m) },
        uGroutM: { value: cfg.groutMm / 1000 },
        uStaggered: { value: cfg.pattern === "staggered" ? 1.0 : 0.0 },
        uCycleFaces: { value: document.getElementById("toggleCycleFaces").checked ? 1.0 : 0.0 },
        uRotateEnabled: { value: document.getElementById("toggleTileRotate").checked ? 1.0 : 0.0 },
        uRelief: { value: numInput("reliefSlider", 1.0, 0, 2.5) },
        uGroutColor: { value: new THREE.Color(cfg.groutHex) },
      });

      if (cfg.mesh.material?.dispose) cfg.mesh.material.dispose();
      cfg.mesh.material = mat;
      if (surfKey === "floor" && sku.pbr?.baseHex) skirtingMat.color.set(sku.pbr.baseHex);
      updateSurfaceCardsAndHud();
    }

    function rebuildRoomGeometry(forceMaterials = false) {
      const w = numInput("roomW", 5.0, 2, 20, true);
      const d = numInput("roomD", 4.0, 2, 20, true);
      const h = numInput("roomH", 3.0, 2.2, 6, true);
      const t = 0.12;

      document.getElementById("topRoomBadge").textContent = `${w.toFixed(1)} × ${d.toFixed(1)} × ${h.toFixed(1)} m`;

      surfaceState.floor.widthM = w; surfaceState.floor.heightM = d;
      floorMesh.geometry.dispose();
      floorMesh.geometry = new THREE.PlaneGeometry(w, d);

      surfaceState.backWall.widthM = w; surfaceState.backWall.heightM = h;
      backWallMesh.geometry.dispose();
      backWallMesh.geometry = new THREE.PlaneGeometry(w, h);
      backWallMesh.position.set(0, h / 2, -d / 2);

      surfaceState.sideWall.widthM = d; surfaceState.sideWall.heightM = h;
      sideWallMesh.geometry.dispose();
      sideWallMesh.geometry = new THREE.PlaneGeometry(d, h);
      sideWallMesh.position.set(-w / 2, h / 2, 0);

      floorSlab.geometry.dispose();
      floorSlab.geometry = new THREE.BoxGeometry(w + t, t, d + t);
      floorSlab.position.set(-t / 2, -t / 2 - 0.002, -t / 2);

      backSlab.geometry.dispose();
      backSlab.geometry = new THREE.BoxGeometry(w + t, h, t);
      backSlab.position.set(-t / 2, h / 2, -d / 2 - t / 2 - 0.002);

      sideSlab.geometry.dispose();
      sideSlab.geometry = new THREE.BoxGeometry(t, h, d + t);
      sideSlab.position.set(-w / 2 - t / 2 - 0.002, h / 2, -t / 2);

      const showSkirt = document.getElementById("toggleSkirting").checked;
      skirtBack.visible = showSkirt;
      skirtSide.visible = showSkirt;
      skirtBack.geometry.dispose();
      skirtBack.geometry = new THREE.BoxGeometry(w, 0.1, 0.016);
      skirtBack.position.set(0, 0.05, -d / 2 + 0.009);
      skirtSide.geometry.dispose();
      skirtSide.geometry = new THREE.BoxGeometry(0.016, 0.1, d);
      skirtSide.position.set(-w / 2 + 0.009, 0.05, 0);

      Object.keys(surfaceState).forEach((k) => {
        if (forceMaterials || !surfaceState[k].mesh.material?.userData?.shaderUniforms) renderSurfaceMaterial(k);
      });
      syncShaderUniformsOnly();
      updateBoqAll();
    }

    // ==================== BOQ COMPUTATION ====================
    function currentBOQ() {
      const w = numInput("roomW", 5.0, 2, 20, true);
      const d = numInput("roomD", 4.0, 2, 20, true);
      const h = numInput("roomH", 3.0, 2.2, 6, true);
      const skirtMode = document.getElementById("skirtingMode").value;
      const skirtLengthM = skirtMode === "4wall" ? 2 * (w + d) : (w + d);
      const activeCfg = surfaceState[activeSurfaceKey];

      return computeBOQ({
        room: { w, d, h },
        surfaces: {
          floor: getSurfaceSku("floor"),
          backWall: getSurfaceSku("backWall"),
          sideWall: getSurfaceSku("sideWall"),
        },
        wastagePct: numInput("wastagePct", 10, 0, 25, true),
        pattern: activeCfg.pattern,
        groutMm: activeCfg.groutMm,
        openings: {
          backWall: numInput("openBack", 0, 0, 50, true),
          sideWall: numInput("openSide", 0, 0, 50, true),
        },
        skirting: { enabled: document.getElementById("toggleSkirting").checked, lengthM: skirtLengthM },
      });
    }

    function updateBoqAll() {
      const boqEl = document.getElementById("boqSummary");
      if (!getSurfaceSku("floor") || !getSurfaceSku("backWall") || !getSurfaceSku("sideWall")) {
        boqEl.textContent = "Waiting for catalog SKUs...";
        return;
      }

      const boq = currentBOQ();
      const { lines, totals } = boq;
      const baseAmt = totals.amount || 0;
      const gstAmt = Math.round(baseAmt * 0.18);
      const finalAmt = includeGst ? baseAmt + gstAmt : baseAmt;

      document.getElementById("topBoqTotal").textContent = `₹${finalAmt.toLocaleString("en-IN")}`;

      let html = lines.map((l) => {
        const qtyText = l.pieces !== null
          ? `${l.purchasedSqFt.toFixed(1)} sq.ft • ${l.pieces} pcs${l.boxes !== null ? ` (${l.boxes} box)` : ""}`
          : "Quantity unavailable";
        const rateText = l.rate !== null ? `₹${l.rate}/sq.ft` : "Rate N/A";
        const amtText = l.amount !== null ? `₹${l.amount.toLocaleString("en-IN")}` : "—";
        const flagsHtml = (l.flags || []).length
          ? `<div class="boq-flag">${(l.flags || []).map((f) => escHtml(flagText(f))).join(" • ")}</div>`
          : "";
        return `<div class="boq-line">
          <div class="boq-row"><strong>${escHtml((l.roles || []).join(" + "))}</strong><span class="mono" style="font-weight:700;">${escHtml(amtText)}</span></div>
          <div class="boq-row" style="color:var(--muted); font-size:11px;"><span>${escHtml(l.series)} — ${escHtml(l.name)}</span><span>${escHtml(l.sizeLabel)}</span></div>
          <div class="boq-row mono" style="font-size:11px; color:var(--ink-2);"><span>${escHtml(qtyText)}</span><span>${escHtml(rateText)}</span></div>
          ${flagsHtml}
        </div>`;
      }).join("");

      html += `<div class="boq-consumables">
        <div class="cons-box"><div class="cons-label">Tile Adhesive</div><div class="cons-val mono">${totals.adhesiveKg.toFixed(1)} kg (${totals.adhesiveBags} bags)</div></div>
        <div class="cons-box"><div class="cons-label">Epoxy / Grout</div><div class="cons-val mono">${totals.groutKg.toFixed(2)} kg</div></div>
      </div>`;

      html += `<div class="boq-total-box">
        <div class="boq-row" style="font-size:11.5px; color:var(--muted);">
          <span>Gross Area (${totals.effectiveWastePct}% waste)</span>
          <span class="mono">${totals.grossSqM.toFixed(1)} m² (${totals.purchasedSqFt.toFixed(1)} sq.ft)</span>
        </div>
        ${includeGst ? `<div class="boq-row" style="font-size:11.5px; color:var(--muted);"><span>Subtotal + 18% GST</span><span class="mono">₹${baseAmt.toLocaleString("en-IN")} + ₹${gstAmt.toLocaleString("en-IN")}</span></div>` : ""}
        <div class="boq-row boq-grand" style="margin-top:4px;">
          <span>${includeGst ? "Est. Total (incl. 18% GST)" : "Est. Material (excl. GST)"}</span>
          <span class="mono">₹${finalAmt.toLocaleString("en-IN")}</span>
        </div>
      </div>`;

      if (totals.incomplete) {
        html += `<div class="boq-flag" style="margin-top:8px;">Estimate incomplete — one or more SKUs lack catalog dimensions or rate data.</div>`;
      }
      boqEl.innerHTML = html;

      // Executive BOQ Sheet
      const w = numInput("roomW", 5.0, 2, 20);
      const d = numInput("roomD", 4.0, 2, 20);
      const h = numInput("roomH", 3.0, 2.2, 6);
      const activeCfg = surfaceState[activeSurfaceKey];
      document.getElementById("boqSheetSubtitle").textContent =
        `Room ${w.toFixed(1)}m × ${d.toFixed(1)}m × ${h.toFixed(1)}m • Layout: ${activeCfg.pattern} • Grout: ${activeCfg.groutMm}mm • Effective Wastage: ${totals.effectiveWastePct}%`;

      document.getElementById("boqFullKpis").innerHTML = `
        <div class="kpi-box"><div class="kpi-label">${includeGst ? "Grand Total (Incl. 18% GST)" : "Material Total (Excl. GST)"}</div><div class="kpi-val mono" style="color:var(--accent-hover);">₹${finalAmt.toLocaleString("en-IN")}</div><div class="kpi-sub">${totals.incomplete ? "Some SKU rates/sizes missing" : "Rounded to full pieces/boxes"}</div></div>
        <div class="kpi-box"><div class="kpi-label">Purchased Area</div><div class="kpi-val mono">${totals.purchasedSqFt.toFixed(1)} sq.ft</div><div class="kpi-sub mono">Net ${totals.netSqM.toFixed(1)} m² / Gross ${totals.grossSqM.toFixed(1)} m²</div></div>
        <div class="kpi-box"><div class="kpi-label">Adhesive Requirement</div><div class="kpi-val mono">${totals.adhesiveBags} Bags</div><div class="kpi-sub mono">~${totals.adhesiveKg.toFixed(1)} kg @ 20 kg/bag</div></div>
        <div class="kpi-box"><div class="kpi-label">Grout Requirement</div><div class="kpi-val mono">${totals.groutKg.toFixed(2)} kg</div><div class="kpi-sub mono">${totals.groutAssumedThicknessMm}mm bed depth</div></div>
      `;

      const rowsHtml = lines.map((l) => {
        const skuObj = catalogById.get(l.key);
        const thumb = skuObj?.pbr?.maps?.albedo || "";
        return `<tr>
          <td><strong>${escHtml((l.roles || []).join(" + "))}</strong></td>
          <td><div class="tbl-sku"><img class="tbl-thumb" src="${escHtml(thumb)}" alt="" /><div><div style="font-weight:700;">${escHtml(l.name)}</div><div style="font-size:11px; color:var(--muted);">${escHtml(l.series)}</div></div></div></td>
          <td class="mono">${escHtml(l.sizeLabel)}</td>
          <td class="num mono">${l.netSqM.toFixed(2)} m²</td>
          <td class="num mono">${l.pieces !== null ? l.pieces : "—"}</td>
          <td class="num mono">${l.boxes !== null ? l.boxes : "—"}</td>
          <td class="num mono">${l.purchasedSqFt !== null ? l.purchasedSqFt.toFixed(1) : "—"}</td>
          <td class="num mono">${l.rate !== null ? `₹${l.rate}` : "—"}</td>
          <td class="num mono" style="font-weight:700;">${l.amount !== null ? `₹${l.amount.toLocaleString("en-IN")}` : "—"}</td>
        </tr>`;
      }).join("");

      document.getElementById("boqFullTableWrap").innerHTML = `
        <table class="boq-table">
          <thead><tr><th>Surfaces</th><th>Material / Series</th><th>Size</th><th class="num">Net Area</th><th class="num">Pieces</th><th class="num">Boxes</th><th class="num">Order Sq.Ft</th><th class="num">Rate (₹)</th><th class="num">Amount (₹)</th></tr></thead>
          <tbody>
            ${rowsHtml}
            ${includeGst ? `<tr><td colspan="8" style="text-align:right; color:var(--muted); font-weight:600;">GST (18%)</td><td class="num mono" style="font-weight:600;">₹${gstAmt.toLocaleString("en-IN")}</td></tr>` : ""}
            <tr style="background:var(--bg-soft);">
              <td colspan="6" style="font-weight:800;">TOTAL ESTIMATE ${includeGst ? "(INCL. 18% GST)" : "(EXCL. GST)"}</td>
              <td class="num mono" style="font-weight:700;">${totals.purchasedSqFt.toFixed(1)}</td>
              <td></td>
              <td class="num mono" style="font-weight:800; font-size:14px; color:var(--accent-hover);">₹${finalAmt.toLocaleString("en-IN")}</td>
            </tr>
          </tbody>
        </table>
      `;
    }

    // ==================== CONTROLS, SWATCHES & CATALOG ====================
    function syncInspectorFromSurface() {
      const cfg = surfaceState[activeSurfaceKey];
      document.querySelectorAll("[data-pattern]").forEach((b) => b.classList.toggle("active", b.dataset.pattern === cfg.pattern));
      document.getElementById("groutMm").value = String(cfg.groutMm);
      document.getElementById("groutMmVal").textContent = `${cfg.groutMm.toFixed(1)} mm`;
      document.getElementById("groutColor").value = cfg.groutHex;
      document.querySelectorAll("[data-grout-hex]").forEach((b) => b.classList.toggle("active", b.dataset.groutHex.toLowerCase() === cfg.groutHex.toLowerCase()));
      document.querySelectorAll("[data-finish]").forEach((b) => b.classList.toggle("active", b.dataset.finish === cfg.finish));
      updateSurfaceCardsAndHud();
    }

    async function assignSkuToSurface(surfKey, skuId, silent = false) {
      const sku = catalogById.get(skuId);
      if (!sku || !surfaceState[surfKey]) return;
      activeSurfaceKey = surfKey;
      surfaceState[surfKey].skuId = sku.id;
      syncInspectorFromSurface();
      await renderSurfaceMaterial(surfKey);
      updateBoqAll();
      if (!silent) showToast(`Applied ${sku.name} to ${surfaceState[surfKey].label}`);
    }

    function renderStudioSwatches(resetCount = true) {
      if (resetCount) studioVisible = STUDIO_PAGE_SIZE;
      const q = document.getElementById("studioSearch").value.trim().toLowerCase();
      const sVal = document.getElementById("studioSeries").value;
      const szVal = document.getElementById("studioSize").value;

      filteredStudio = catalogItems.filter((item) => {
        if (sVal !== "All" && item.series !== sVal) return false;
        const spec = readTileSpec(item);
        const sizeStr = spec.sizeKnown ? `${spec.widthMm}x${spec.heightMm}` : "";
        if (szVal !== "All" && sizeStr !== szVal) return false;
        if (q) {
          const hay = `${item.name || ""} ${item.series || ""} ${item.finish || ""} ${sizeStr}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      const slice = filteredStudio.slice(0, studioVisible);
      const activeId = surfaceState[activeSurfaceKey]?.skuId;

      document.getElementById("studioSwatchCount").textContent = `${filteredStudio.length.toLocaleString()} matching SKUs`;
      document.getElementById("studioSwatchGrid").innerHTML = slice.map((item) => {
        const spec = readTileSpec(item);
        const dim = spec.sizeKnown ? `${spec.widthMm}×${spec.heightMm}` : "Size N/A";
        return `<div class="swatch-card ${item.id === activeId ? "applied" : ""}" data-swatch-id="${escHtml(item.id)}">
          <div class="swatch-img-wrap">
            <img class="swatch-img" src="${escHtml(item.pbr?.maps?.albedo || "")}" alt="${escHtml(item.name)}" loading="lazy" />
            <button class="swatch-zoom-btn" data-zoom-id="${escHtml(item.id)}" title="Inspect 6x">&#128269;</button>
          </div>
          <div class="swatch-body">
            <div class="swatch-series">${escHtml(item.series)}</div>
            <div class="swatch-name" title="${escHtml(item.name)}">${escHtml(item.name)}</div>
            <div class="swatch-size mono">${escHtml(dim)}</div>
          </div>
        </div>`;
      }).join("");

      const moreBtn = document.getElementById("studioLoadMore");
      moreBtn.style.display = studioVisible < filteredStudio.length ? "block" : "none";
      moreBtn.textContent = `Load More (${(filteredStudio.length - studioVisible).toLocaleString()} remaining)`;
    }

    document.getElementById("studioSwatchGrid").addEventListener("click", (e) => {
      const zoomBtn = e.target.closest("[data-zoom-id]");
      if (zoomBtn) { e.stopPropagation(); openInspector(catalogById.get(zoomBtn.dataset.zoomId)); return; }
      const card = e.target.closest("[data-swatch-id]");
      if (card) assignSkuToSurface(activeSurfaceKey, card.dataset.swatchId);
    });

    function syncLookTabHighlight() {
      document.querySelectorAll("#lookTabs .tab-btn").forEach((b) =>
        b.classList.toggle("active", b.dataset.look === activeLook)
      );
    }

    function renderFullCatalog(resetCount = true) {
      if (resetCount) catalogVisible = CATALOG_PAGE_SIZE;
      const q = document.getElementById("searchInput").value.trim().toLowerCase();
      const sVal = document.getElementById("seriesFilter").value;
      const szVal = document.getElementById("sizeFilter").value;

      filteredCatalog = catalogItems.filter((item) => {
        if (activeLook !== "All" && item.lookAndFeel !== activeLook) return false;
        if (sVal !== "All" && item.series !== sVal) return false;
        const spec = readTileSpec(item);
        const sizeStr = spec.sizeKnown ? `${spec.widthMm}x${spec.heightMm}` : "";
        if (szVal !== "All" && sizeStr !== szVal) return false;
        if (q) {
          const hay = `${item.name || ""} ${item.series || ""} ${item.finish || ""} ${sizeStr}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      document.getElementById("catalogCount").textContent =
        `${Math.min(catalogVisible, filteredCatalog.length).toLocaleString()} / ${filteredCatalog.length.toLocaleString()} SKUs`;

      const slice = filteredCatalog.slice(0, catalogVisible);
      document.getElementById("skuCards").innerHTML = slice.map((item) => {
        const spec = readTileSpec(item);
        const dimLabel = spec.sizeKnown ? `${spec.widthMm}×${spec.heightMm} mm` : "Size unknown";
        const rateLabel = spec.rateKnown ? `₹${spec.rate}/sq.ft` : "Rate on request";
        return `<div class="card">
          <div class="card-thumb-wrap" data-cat-zoom="${escHtml(item.id)}">
            <img class="card-thumb" src="${escHtml(item.pbr?.maps?.albedo || "")}" alt="${escHtml(item.name)}" loading="lazy" />
            <span class="zoom-badge">6x Zoom</span>
          </div>
          <div class="card-body">
            <div>
              <div class="card-series">${escHtml(item.series)}</div>
              <div class="card-title">${escHtml(item.name)}</div>
              <div class="card-meta mono">${escHtml(dimLabel)} &bull; ${escHtml(rateLabel)}</div>
            </div>
            <div class="quick-apply-row">
              <button class="qa-btn" data-cat-apply="floor" data-sku="${escHtml(item.id)}">+ Floor</button>
              <button class="qa-btn" data-cat-apply="backWall" data-sku="${escHtml(item.id)}">+ Back</button>
              <button class="qa-btn" data-cat-apply="sideWall" data-sku="${escHtml(item.id)}">+ Side</button>
            </div>
          </div>
        </div>`;
      }).join("");

      const moreBtn = document.getElementById("loadMoreBtn");
      moreBtn.style.display = catalogVisible < filteredCatalog.length ? "inline-flex" : "none";
      moreBtn.textContent = `Load More (${(filteredCatalog.length - catalogVisible).toLocaleString()} remaining)`;
    }

    document.getElementById("skuCards").addEventListener("click", (e) => {
      const z = e.target.closest("[data-cat-zoom]");
      if (z) { openInspector(catalogById.get(z.dataset.catZoom)); return; }
      const btn = e.target.closest("[data-cat-apply]");
      if (btn) {
        assignSkuToSurface(btn.dataset.catApply, btn.dataset.sku);
        switchView("viewStudio");
      }
    });

    function populateFilters() {
      const seriesList = [...seriesMap.keys()].sort();
      const sizeList = [...new Set(catalogItems.map((i) => {
        const sp = readTileSpec(i);
        return sp.sizeKnown ? `${sp.widthMm}x${sp.heightMm}` : null;
      }).filter(Boolean))].sort();
      const lookList = ["All", ...new Set(catalogItems.map((i) => i.lookAndFeel).filter(Boolean))];

      const seriesHtml =
        `<option value="All">All Series (${seriesList.length})</option>` +
        seriesList.map((s) => `<option value="${escHtml(s)}">${escHtml(formatSeriesTitle(s))} (${seriesMap.get(s).length})</option>`).join("");
      const sizeHtml =
        `<option value="All">All Sizes</option>` +
        sizeList.map((sz) => `<option value="${escHtml(sz)}">${escHtml(sz)} mm</option>`).join("");

      document.getElementById("seriesFilter").innerHTML = seriesHtml;
      document.getElementById("studioSeries").innerHTML = seriesHtml;
      document.getElementById("sizeFilter").innerHTML = sizeHtml;
      document.getElementById("studioSize").innerHTML = sizeHtml;

      document.getElementById("lookTabs").innerHTML = lookList.map((lk) =>
        `<button class="tab-btn ${lk === activeLook ? "active" : ""}" data-look="${escHtml(lk)}">${escHtml(lk)}</button>`
      ).join("");

      document.getElementById("lookTabs").addEventListener("click", (e) => {
        const btn = e.target.closest("[data-look]");
        if (!btn) return;
        activeLook = btn.dataset.look;
        syncLookTabHighlight();
        renderFullCatalog(true);
      });

      const pillsEl = document.getElementById("heroSeriesPills");
      pillsEl.innerHTML =
        `<button class="pill-btn active" data-series="All">All (${catalogItems.length.toLocaleString()})</button>` +
        seriesList.map((s) =>
          `<button class="pill-btn" data-series="${escHtml(s)}">${escHtml(formatSeriesTitle(s))} (${seriesMap.get(s).length})</button>`
        ).join("");

      pillsEl.addEventListener("click", (e) => {
        const p = e.target.closest("[data-series]");
        if (p) openCatalogForSeries(p.dataset.series);
      });
    }

    // ==================== 6X TEXTURE INSPECTOR MODAL ====================
    const inspectorModal = document.getElementById("inspectorModal");
    const modalStage = document.getElementById("modalStage");
    const modalImg = document.getElementById("modalImg");
    const modalZoomSlider = document.getElementById("modalZoomSlider");
    const modalZoomLabel = document.getElementById("modalZoomLabel");
    let modalSku = null, modalZoom = 1, modalPanX = 0, modalPanY = 0;
    let isDraggingModal = false, dragStartX = 0, dragStartY = 0;

    function updateModalTransform() {
      modalImg.style.transform = `translate(${modalPanX}px, ${modalPanY}px) scale(${modalZoom})`;
      modalZoomSlider.value = String(modalZoom);
      modalZoomLabel.textContent = `${modalZoom.toFixed(1)}x`;
    }
    function resetModalZoom() { modalZoom = 1; modalPanX = 0; modalPanY = 0; updateModalTransform(); }

    function openInspector(sku) {
      if (!sku) return;
      modalSku = sku;
      const spec = readTileSpec(sku);
      const faces = getSiblingFaces(sku);
      document.getElementById("modalSeries").textContent = formatSeriesTitle(sku.series || "Simpolo");
      document.getElementById("modalTitle").textContent = sku.name || sku.id;
      modalImg.src = sku.pbr?.maps?.albedo || "";
      document.getElementById("modalSpecs").innerHTML = `
        <div class="spec-cell"><div class="spec-k">Dimensions</div><div class="spec-v mono">${spec.sizeKnown ? `${spec.widthMm} × ${spec.heightMm} mm` : "Unknown"}</div></div>
        <div class="spec-cell"><div class="spec-k">Rate</div><div class="spec-v mono">${spec.rateKnown ? `₹${spec.rate}/sq.ft` : "On request"}</div></div>
        <div class="spec-cell"><div class="spec-k">Look &amp; Feel</div><div class="spec-v">${escHtml(sku.lookAndFeel || "—")}</div></div>
        <div class="spec-cell"><div class="spec-k">GPU Faces</div><div class="spec-v mono">${faces.length} variant${faces.length > 1 ? "s" : ""}</div></div>
      `;
      resetModalZoom();
      inspectorModal.classList.add("open");
      inspectorModal.setAttribute("aria-hidden", "false");
    }

    function closeInspector() {
      inspectorModal.classList.remove("open");
      inspectorModal.setAttribute("aria-hidden", "true");
    }

    modalZoomSlider.addEventListener("input", () => {
      modalZoom = parseFloat(modalZoomSlider.value) || 1;
      if (modalZoom <= 1) { modalPanX = 0; modalPanY = 0; }
      updateModalTransform();
    });
    modalStage.addEventListener("wheel", (e) => {
      e.preventDefault();
      modalZoom = Math.min(6, Math.max(1, modalZoom + (e.deltaY < 0 ? 0.35 : -0.35)));
      if (modalZoom <= 1) { modalPanX = 0; modalPanY = 0; }
      updateModalTransform();
    }, { passive: false });
    modalStage.addEventListener("pointerdown", (e) => {
      if (modalZoom <= 1) return;
      isDraggingModal = true;
      dragStartX = e.clientX - modalPanX;
      dragStartY = e.clientY - modalPanY;
      modalStage.setPointerCapture(e.pointerId);
    });
    modalStage.addEventListener("pointermove", (e) => {
      if (!isDraggingModal) return;
      modalPanX = e.clientX - dragStartX;
      modalPanY = e.clientY - dragStartY;
      updateModalTransform();
    });
    modalStage.addEventListener("pointerup", () => { isDraggingModal = false; });
    modalStage.addEventListener("pointercancel", () => { isDraggingModal = false; });
    document.getElementById("modalResetZoom").addEventListener("click", resetModalZoom);
    document.getElementById("modalCloseBtn").addEventListener("click", closeInspector);
    inspectorModal.addEventListener("click", (e) => { if (e.target === inspectorModal) closeInspector(); });
    window.addEventListener("keydown", (e) => { if (e.key === "Escape") closeInspector(); });
    document.querySelectorAll("[data-modal-apply]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (!modalSku) return;
        assignSkuToSurface(btn.dataset.modalApply, modalSku.id);
        closeInspector();
        switchView("viewStudio");
      });
    });

    // ==================== NAVIGATION & UI BINDINGS ====================
    function switchView(viewId) {
      currentViewId = viewId;
      document.querySelectorAll(".app-view").forEach((v) => v.classList.toggle("active", v.id === viewId));
      document.querySelectorAll(".nav-link[data-view]").forEach((b) => b.classList.toggle("active", b.dataset.view === viewId));
      if (viewId === "viewStudio") {
        requestAnimationFrame(() => {
          resizeRenderer();
          renderer.render(scene, camera);
        });
      }
      window.scrollTo({ top: 0, behavior: "instant" });
    }

    document.body.addEventListener("click", (e) => {
      const target = e.target.closest("[data-view]");
      if (target) switchView(target.dataset.view);
    });
    document.getElementById("brandHome").addEventListener("click", (e) => { e.preventDefault(); switchView("viewHome"); });
    document.getElementById("topQuoteBtn").addEventListener("click", () => switchView("viewBoq"));
    document.getElementById("openFullBoqBtn").addEventListener("click", () => switchView("viewBoq"));
    document.getElementById("heroPrev").addEventListener("click", () => setHeroSlide(heroIndex - 1));
    document.getElementById("heroNext").addEventListener("click", () => setHeroSlide(heroIndex + 1));

    document.querySelectorAll("[data-tab]").forEach((b) => {
      b.addEventListener("click", () => {
        document.querySelectorAll("[data-tab]").forEach((t) => t.classList.toggle("active", t === b));
        document.querySelectorAll(".insp-pane").forEach((p) => p.classList.toggle("active", p.id === b.dataset.tab));
      });
    });

    document.querySelectorAll("[data-surface]").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeSurfaceKey = btn.dataset.surface;
        syncInspectorFromSurface();
      });
    });

    document.querySelectorAll("[data-cam]").forEach((btn) =>
      btn.addEventListener("click", () => moveCameraToPreset(btn.dataset.cam))
    );

    document.querySelectorAll("[data-mood]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const m = LIGHTING_MOODS[btn.dataset.mood];
        if (!m) return;
        document.querySelectorAll("[data-mood]").forEach((b) => b.classList.toggle("active", b === btn));
        scene.background.set(m.bg);
        hemiLight.color.set(m.hemiSky);
        hemiLight.groundColor.set(m.hemiGround);
        hemiLight.intensity = m.hemiInt;
        dirLight.color.set(m.dirColor);
        dirLight.intensity = m.dirInt;
        renderer.toneMappingExposure = m.exp;
        document.getElementById("lightSlider").value = String(m.dirInt);
        document.getElementById("lightVal").textContent = m.dirInt.toFixed(2);
        document.getElementById("exposureSlider").value = String(m.exp);
        document.getElementById("exposureVal").textContent = m.exp.toFixed(2);
      });
    });

    document.getElementById("btnSnapshot").addEventListener("click", () => {
      renderer.render(scene, camera);
      const a = document.createElement("a");
      a.href = renderer.domElement.toDataURL("image/png");
      a.download = "Simpolo_Virtual_Space_Render.png";
      a.click();
      showToast("3D room snapshot saved as PNG");
    });

    document.getElementById("btnFullscreen").addEventListener("click", () => {
      const stage = document.getElementById("viewportStage");
      if (!document.fullscreenElement) stage.requestFullscreen?.();
      else document.exitFullscreen?.();
    });

    document.querySelectorAll("[data-room-preset]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const [w, d, h] = btn.dataset.roomPreset.split(",");
        document.getElementById("roomW").value = w;
        document.getElementById("roomD").value = d;
        document.getElementById("roomH").value = h;
        rebuildRoomGeometry(false);
        moveCameraToPreset("iso");
      });
    });

    document.querySelectorAll("[data-pattern]").forEach((btn) => {
      btn.addEventListener("click", () => {
        surfaceState[activeSurfaceKey].pattern = btn.dataset.pattern;
        syncInspectorFromSurface();
        syncShaderUniformsOnly();
        updateBoqAll();
      });
    });

    document.getElementById("groutMm").addEventListener("input", (e) => {
      const val = parseFloat(e.target.value) || 0;
      surfaceState[activeSurfaceKey].groutMm = val;
      document.getElementById("groutMmVal").textContent = `${val.toFixed(1)} mm`;
      syncShaderUniformsOnly();
      updateBoqAll();
    });

    function setGroutColor(hex) {
      surfaceState[activeSurfaceKey].groutHex = hex;
      document.getElementById("groutColor").value = hex;
      document.querySelectorAll("[data-grout-hex]").forEach((b) =>
        b.classList.toggle("active", b.dataset.groutHex.toLowerCase() === hex.toLowerCase())
      );
      syncShaderUniformsOnly();
    }
    document.querySelectorAll("[data-grout-hex]").forEach((b) =>
      b.addEventListener("click", () => setGroutColor(b.dataset.groutHex))
    );
    document.getElementById("groutColor").addEventListener("input", (e) => setGroutColor(e.target.value));

    document.querySelectorAll("[data-finish]").forEach((btn) => {
      btn.addEventListener("click", () => {
        surfaceState[activeSurfaceKey].finish = btn.dataset.finish;
        applyFinishToMaterial(activeSurfaceKey);
        syncInspectorFromSurface();
      });
    });

    ["toggleCycleFaces", "toggleTileRotate"].forEach((id) =>
      document.getElementById(id).addEventListener("change", syncShaderUniformsOnly)
    );
    document.getElementById("reliefSlider").addEventListener("input", syncShaderUniformsOnly);
    document.getElementById("lightSlider").addEventListener("input", (e) => {
      dirLight.intensity = parseFloat(e.target.value);
      document.getElementById("lightVal").textContent = dirLight.intensity.toFixed(2);
    });
    document.getElementById("exposureSlider").addEventListener("input", (e) => {
      renderer.toneMappingExposure = parseFloat(e.target.value);
      document.getElementById("exposureVal").textContent = renderer.toneMappingExposure.toFixed(2);
    });

    ["roomW", "roomD", "roomH"].forEach((id) =>
      document.getElementById(id).addEventListener("input", () => rebuildRoomGeometry(false))
    );
    document.getElementById("wastagePct").addEventListener("input", (e) => {
      document.getElementById("wastagePctVal").textContent = `${e.target.value}%`;
      updateBoqAll();
    });
    ["openBack", "openSide"].forEach((id) => document.getElementById(id).addEventListener("input", updateBoqAll));
    document.getElementById("toggleSkirting").addEventListener("change", () => rebuildRoomGeometry(false));
    document.getElementById("skirtingMode").addEventListener("change", updateBoqAll);

    function syncGstToggle(checked) {
      includeGst = checked;
      document.getElementById("toggleGst").checked = checked;
      document.getElementById("toggleGstFull").checked = checked;
      updateBoqAll();
    }
    document.getElementById("toggleGst").addEventListener("change", (e) => syncGstToggle(e.target.checked));
    document.getElementById("toggleGstFull").addEventListener("change", (e) => syncGstToggle(e.target.checked));

    document.getElementById("studioSearch").addEventListener("input", () => renderStudioSwatches(true));
    document.getElementById("studioSeries").addEventListener("change", () => renderStudioSwatches(true));
    document.getElementById("studioSize").addEventListener("change", () => renderStudioSwatches(true));
    document.getElementById("studioLoadMore").addEventListener("click", () => {
      studioVisible += STUDIO_PAGE_SIZE;
      renderStudioSwatches(false);
    });

    document.getElementById("searchInput").addEventListener("input", () => renderFullCatalog(true));
    document.getElementById("seriesFilter").addEventListener("change", () => renderFullCatalog(true));
    document.getElementById("sizeFilter").addEventListener("change", () => renderFullCatalog(true));
    document.getElementById("loadMoreBtn").addEventListener("click", () => {
      catalogVisible += CATALOG_PAGE_SIZE;
      renderFullCatalog(false);
    });

    function copyBoqText() {
      navigator.clipboard?.writeText(document.getElementById("boqSummary").innerText);
      showToast("BOQ summary copied to clipboard");
    }
    function downloadBoqCsv() {
      const csv = boqToCsv(currentBOQ());
      const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8;" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "Simpolo_3D_Room_BOQ.csv";
      a.click();
      showToast("Exported Simpolo_3D_Room_BOQ.csv");
    }

    document.getElementById("exportBoqBtn").addEventListener("click", copyBoqText);
    document.getElementById("fullCopyBtn").addEventListener("click", copyBoqText);
    document.getElementById("exportCsvBtn").addEventListener("click", downloadBoqCsv);
    document.getElementById("fullCsvBtn").addEventListener("click", downloadBoqCsv);
    document.getElementById("journeyExportCsv").addEventListener("click", downloadBoqCsv);
    document.getElementById("fullPrintBtn").addEventListener("click", () => window.print());

    // ==================== BOOT CATALOG ====================
    fetch("full_catalog.json")
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(async (data) => {
        catalogItems = data.items || [];
        catalogById = new Map(catalogItems.map((i) => [i.id, i]));
        seriesMap = new Map();
        for (const it of catalogItems) {
          const key = it.series || "other";
          if (!seriesMap.has(key)) seriesMap.set(key, []);
          seriesMap.get(key).push(it);
        }
        rebuildSiblingIndex(catalogItems);

        document.getElementById("navCatalogBadge").textContent = catalogItems.length.toLocaleString();
        document.getElementById("homeTotalSkus").textContent = catalogItems.length.toLocaleString();
        document.getElementById("homeTotalSeries").textContent = String(seriesMap.size);

        if (catalogItems.length > 0) {
          const s0 = seriesMap.get("marmorica")?.[0] || catalogItems[0];
          const s1 = seriesMap.get("glyphstone")?.[0] || catalogItems[Math.min(1, catalogItems.length - 1)];
          const s2 = seriesMap.get("alchimia")?.[0] || catalogItems[Math.min(2, catalogItems.length - 1)];

          surfaceState.floor.skuId = s0.id;
          surfaceState.backWall.skuId = s1.id;
          surfaceState.sideWall.skuId = s2.id;

          if (s0.pbr?.maps?.albedo) {
            document.getElementById("catHeroBg").style.backgroundImage = `url("${s0.pbr.maps.albedo}")`;
          }
          document.getElementById("catHeroTitle").textContent = `${catalogItems.length.toLocaleString()} Simpolo Surfaces`;

          buildHomeHero();
          buildAboutMosaic();
          renderExploreGrid("locations");
          buildHomeCollectionsAndMenus();

          populateFilters();
          syncInspectorFromSurface();
          renderStudioSwatches(true);
          renderFullCatalog(true);
          rebuildRoomGeometry(true);
          moveCameraToPreset("iso");
        }
      })
      .catch((err) => {
        document.getElementById("studioSwatchCount").textContent = "Failed to load full_catalog.json";
        document.getElementById("catalogCount").textContent = "Run via local HTTP server in web_prototype/";
        console.error(err);
      });

    // ==================== RENDER LOOP ====================
    (function animate() {
      requestAnimationFrame(animate);
      if (currentViewId !== "viewStudio" || !host.clientWidth || !host.clientHeight) return;
      if (camAnim) {
        camAnim.t = Math.min(1, camAnim.t + 0.06);
        const ease = 1 - Math.pow(1 - camAnim.t, 3);
        camera.position.lerpVectors(camAnim.startPos, camAnim.endPos, ease);
        controls.target.lerpVectors(camAnim.startTarget, camAnim.endTarget, ease);
        if (camAnim.t >= 1) camAnim = null;
      }
      controls.update();
      renderer.render(scene, camera);
    })();
  </script>
</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print("Wrote", OUT_HTML)