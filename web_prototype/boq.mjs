// boq.mjs - pure Bill-of-Quantities maths for the tile visualizer.
// No DOM, no Three.js. Safe to unit test with plain Node.
//
// Design rules:
//  * Never invent data. Missing size or rate is flagged, not defaulted.
//  * Areas are summed per SKU BEFORE rounding to pieces (one ceil per SKU).
//  * Pieces use tile + grout pitch, not bare tile area.
//  * Skirting is cut in strips from floor tiles (linear, with saw kerf).

export const SQFT_PER_SQM = 10.7639;

export const DEFAULTS = Object.freeze({
  staggeredExtraWastePct: 5, // extra cut loss for 50% offset layouts
  skirtingHeightMm: 100,
  kerfMm: 3,                 // saw blade loss per cut
  defaultThicknessMm: 9,     // only used for grout estimate; flagged as assumed
  adhesiveKgPerSqm: 5,
  adhesiveBagKg: 20,
  groutDensity: 1.6,         // kg per litre
  groutWasteFactor: 1.15,
});

const isPosNum = (v) => typeof v === 'number' && Number.isFinite(v) && v > 0;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const ceilSafe = (x) => Math.ceil(x - 1e-9);

/** Read a catalog item without inventing anything. */
export function readTileSpec(sku) {
  const w = Number(sku?.dimensionsMm?.width);
  const h = Number(sku?.dimensionsMm?.height);
  const sizeKnown = isPosNum(w) && isPosNum(h);
  const rate = Number(sku?.pricing?.ratePerSqFt);
  const ppb = Number(sku?.packing?.piecesPerBox);
  const thick = Number(sku?.thicknessMm);
  return {
    sizeKnown,
    widthMm: sizeKnown ? w : null,
    heightMm: sizeKnown ? h : null,
    shortMm: sizeKnown ? Math.min(w, h) : null,
    longMm: sizeKnown ? Math.max(w, h) : null,
    rateKnown: isPosNum(rate),
    rate: isPosNum(rate) ? rate : null,
    piecesPerBox: isPosNum(ppb) ? Math.floor(ppb) : null,
    thicknessMm: isPosNum(thick) ? thick : DEFAULTS.defaultThicknessMm,
    thicknessAssumed: !isPosNum(thick),
  };
}

/** Strips of `skirtH` that can be cut from the short side of one tile. */
export function stripsPerTile(shortMm, skirtH, kerf) {
  return Math.max(0, Math.floor((shortMm + kerf) / (skirtH + kerf)));
}

/** Grout kg per m2 of tiled area. All dimensions in mm. */
export function groutKgPerSqm(L, W, thicknessMm, jointMm, density = DEFAULTS.groutDensity) {
  if (!(jointMm > 0)) return 0;
  return ((L + W) / (L * W)) * thicknessMm * jointMm * density;
}

/**
 * @param {object} p
 * @param {{w:number,d:number,h:number}} p.room metres
 * @param {{floor:object,backWall:object,sideWall:object}} p.surfaces catalog items
 * @param {number} [p.wastagePct=10]
 * @param {'grid'|'staggered'} [p.pattern='grid']
 * @param {number} [p.groutMm=2]
 * @param {{backWall?:number,sideWall?:number}} [p.openings] m2 to deduct per wall
 * @param {{enabled:boolean,lengthM:number,heightMm?:number}} [p.skirting]
 * @param {object} [p.options] overrides for DEFAULTS
 */
export function computeBOQ({
  room, surfaces, wastagePct = 10, pattern = 'grid', groutMm = 2,
  openings = {}, skirting = null, options = {},
}) {
  const o = { ...DEFAULTS, ...options };
  const waste = clamp(Number(wastagePct) || 0, 0, 100)
    + (pattern === 'staggered' ? o.staggeredExtraWastePct : 0);
  const grout = Math.max(0, Number(groutMm) || 0);

  const open = (k) => Math.max(0, Number(openings?.[k]) || 0);
  const net = {
    floor: Math.max(0, room.w * room.d),
    backWall: Math.max(0, room.w * room.h - open('backWall')),
    sideWall: Math.max(0, room.d * room.h - open('sideWall')),
  };
  const roleLabel = { floor: 'Floor', backWall: 'Feature Wall', sideWall: 'Side Wall' };

  // group by SKU so one SKU = one order line = one rounding
  const groups = new Map();
  const groupFor = (sku) => {
    const key = String(sku?.id ?? `${sku?.series}|${sku?.name}`);
    if (!groups.has(key)) {
      groups.set(key, { key, sku, spec: readTileSpec(sku), roles: [], netSqM: 0, skirtTiles: 0, skirtStrips: 0 });
    }
    return groups.get(key);
  };

  for (const k of ['floor', 'backWall', 'sideWall']) {
    const g = groupFor(surfaces[k]);
    g.roles.push(roleLabel[k]);
    g.netSqM += net[k];
  }

  const assumptions = [];
  if (pattern === 'staggered') {
    assumptions.push(`Staggered layout adds ${o.staggeredExtraWastePct}% extra wastage.`);
  }

  if (skirting?.enabled && skirting.lengthM > 0) {
    const g = groupFor(surfaces.floor);
    const skirtH = skirting.heightMm ?? o.skirtingHeightMm;
    if (g.spec.sizeKnown) {
      const per = stripsPerTile(g.spec.shortMm, skirtH, o.kerfMm);
      if (per > 0) {
        const stripsNeeded = ceilSafe((skirting.lengthM / (g.spec.longMm / 1000)) * (1 + waste / 100));
        g.skirtStrips = stripsNeeded;
        g.skirtTiles = ceilSafe(stripsNeeded / per);
        g.roles.push(`Skirting (${skirtH}mm)`);
        assumptions.push(`Skirting: ${per} strips of ${skirtH}mm per ${g.spec.shortMm}mm tile after ${o.kerfMm}mm kerf.`);
      } else {
        g.roles.push('Skirting (cannot cut)');
      }
    } else {
      g.roles.push(`Skirting (${skirtH}mm)`);
    }
  }

  const lines = [];
  let tiledNetSqM = 0;
  let groutKg = 0;
  let groutAssumedThickness = false;

  for (const g of groups.values()) {
    const s = g.spec;
    const flags = [];
    const line = {
      key: g.key, sku: g.sku, roles: g.roles, netSqM: g.netSqM,
      sizeLabel: s.sizeKnown ? `${s.widthMm}x${s.heightMm}mm` : 'size unknown',
      pieces: null, boxes: null, purchasedPieces: null, purchasedSqFt: null,
      rate: s.rate, amount: null, flags,
    };

    if (!s.sizeKnown) {
      flags.push('size-missing');
    } else {
      const pitchM2 = ((s.widthMm + grout) / 1000) * ((s.heightMm + grout) / 1000);
      const areaPieces = g.netSqM > 0 ? ceilSafe((g.netSqM * (1 + waste / 100)) / pitchM2) : 0;
      const pieces = areaPieces + g.skirtTiles;
      const boxes = s.piecesPerBox ? ceilSafe(pieces / s.piecesPerBox) : null;
      const purchasedPieces = boxes ? boxes * s.piecesPerBox : pieces;
      const tileM2 = (s.widthMm / 1000) * (s.heightMm / 1000);
      line.pieces = pieces;
      line.boxes = boxes;
      line.purchasedPieces = purchasedPieces;
      line.purchasedSqFt = purchasedPieces * tileM2 * SQFT_PER_SQM;
      if (!s.piecesPerBox) flags.push('box-size-unknown');

      tiledNetSqM += g.netSqM;
      const perSqm = groutKgPerSqm(s.widthMm, s.heightMm, s.thicknessMm, grout, o.groutDensity);
      groutKg += perSqm * g.netSqM * o.groutWasteFactor;
      if (s.thicknessAssumed && grout > 0) groutAssumedThickness = true;

      if (s.rateKnown) line.amount = Math.round(line.purchasedSqFt * s.rate);
      else flags.push('rate-missing');
    }
    lines.push(line);
  }

  if (groutAssumedThickness) {
    assumptions.push(`Tile thickness not in catalog; grout assumes ${o.defaultThicknessMm}mm.`);
  }

  const adhesiveKg = tiledNetSqM * o.adhesiveKgPerSqm;
  const extras = {
    adhesiveKg,
    adhesiveBags: ceilSafe(adhesiveKg / o.adhesiveBagKg),
    adhesiveBagKg: o.adhesiveBagKg,
    groutKg,
  };

  const priced = lines.filter((l) => l.amount !== null);
  const totals = {
    purchasedSqFt: lines.reduce((a, l) => a + (l.purchasedSqFt ?? 0), 0),
    amount: priced.reduce((a, l) => a + l.amount, 0),
    incomplete: lines.some((l) => l.flags.includes('size-missing') || l.flags.includes('rate-missing')),
    effectiveWastePct: waste,
  };

  return { lines, extras, totals, assumptions };
}

/** Human-readable flag text for the UI. */
export function flagText(flag) {
  return {
    'size-missing': 'Tile size missing in catalog - quantity not calculated',
    'rate-missing': 'Rate missing in catalog - excluded from total',
    'box-size-unknown': 'Pieces per box unknown - not rounded to full boxes',
  }[flag] ?? flag;
}

/** Spreadsheet-safe CSV cell (blocks formula injection). */
export function csvCell(v) {
  let s = String(v ?? '');
  if (/^[=+\-@\t\r]/.test(s)) s = `'${s}`;
  return `"${s.replace(/"/g, '""')}"`;
}

export function boqToCsv(boq) {
  const head = 'Surfaces,Series,SKU Name,Size,Net_SqM,Pieces,Boxes,Purchased_SqFt,Rate_INR_SqFt,Total_INR,Flags';
  const rows = boq.lines.map((l) => [
    csvCell(l.roles.join(' + ')), csvCell(l.sku?.series), csvCell(l.sku?.name), csvCell(l.sizeLabel),
    l.netSqM.toFixed(2), l.pieces ?? '', l.boxes ?? '',
    l.purchasedSqFt === null ? '' : l.purchasedSqFt.toFixed(2),
    l.rate ?? '', l.amount ?? '', csvCell(l.flags.join('; ')),
  ].join(','));
  const t = boq.totals;
  rows.push([csvCell('TOTAL'), '', '', '', '', '', '', t.purchasedSqFt.toFixed(2), '', t.amount,
    csvCell(t.incomplete ? 'INCOMPLETE - see flags' : '')].join(','));
  rows.push([csvCell('Adhesive kg'), '', '', '', '', '', '', '', '', boq.extras.adhesiveKg.toFixed(1), ''].join(','));
  rows.push([csvCell('Grout kg'), '', '', '', '', '', '', '', '', boq.extras.groutKg.toFixed(2), ''].join(','));
  return [head, ...rows].join('\n');
}