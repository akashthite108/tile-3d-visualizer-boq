export const SQFT_PER_SQM = 10.7639;

const FLAG_LABELS = {
  'size-missing': 'Tile dimensions missing',
  'rate-missing': 'Rate per sq.ft missing',
  'box-size-unknown': 'Pieces per box not in catalog',
};

export function flagText(flag) {
  return FLAG_LABELS[flag] || String(flag);
}

function positiveNum(v) {
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function nonNegNum(v, fallback = 0) {
  const n = Number(v);
  if (!Number.isFinite(n)) return fallback;
  return Math.max(0, n);
}

export function readTileSpec(sku = {}) {
  const wMm = positiveNum(sku?.dimensionsMm?.width ?? sku?.widthMm);
  const hMm = positiveNum(sku?.dimensionsMm?.height ?? sku?.heightMm);
  const sizeKnown = wMm !== null && hMm !== null;

  const rawRate = sku?.pricing?.ratePerSqFt ?? sku?.ratePerSqFt;
  const rateNum = Number(rawRate);
  const rateKnown = rawRate !== null && rawRate !== undefined && rawRate !== '' && Number.isFinite(rateNum) && rateNum > 0;

  const rawBox = sku?.packing?.piecesPerBox ?? sku?.piecesPerBox;
  const boxNum = Number(rawBox);
  const piecesPerBox = Number.isFinite(boxNum) && boxNum > 0 ? Math.floor(boxNum) : null;

  return {
    widthMm: wMm,
    heightMm: hMm,
    sizeKnown,
    rate: rateKnown ? rateNum : null,
    rateKnown,
    piecesPerBox,
  };
}

export function stripsPerTile(tileSideMm, stripWidthMm = 100, kerfMm = 3) {
  const side = positiveNum(tileSideMm);
  const stripW = positiveNum(stripWidthMm);
  const kerf = nonNegNum(kerfMm, 0);
  if (!side || !stripW) return 0;
  const pitch = stripW + kerf;
  if (pitch <= 0 || side < stripW) return 0;
  return Math.max(0, Math.floor((side + kerf) / pitch));
}

export function groutKgPerSqm(tileWidthMm, tileHeightMm, thicknessMm = 9, jointWidthMm = 2, densityKgPerL = 1.6) {
  const w = positiveNum(tileWidthMm);
  const h = positiveNum(tileHeightMm);
  const joint = nonNegNum(jointWidthMm, 0);
  const thick = nonNegNum(thicknessMm, 0);
  const density = nonNegNum(densityKgPerL, 1.6);
  if (!w || !h || joint <= 0 || thick <= 0 || density <= 0) return 0;

  const jointLengthMmPerSqm = ((1 / w) + (1 / h)) * 1000;
  const volumeLitersPerSqm = (jointLengthMmPerSqm * joint * thick) / 1e6;
  return volumeLitersPerSqm * density;
}

export function adhesiveKg(areaSqM, coverageKgPerSqm = 5) {
  return Math.max(0, nonNegNum(areaSqM, 0)) * nonNegNum(coverageKgPerSqm, 5);
}

export function computeBOQ(options = {}) {
  const room = options.room || {};
  const w = nonNegNum(room.w, 5);
  const d = nonNegNum(room.d, 4);
  const h = nonNegNum(room.h, 3);

  const surfaces = options.surfaces || {};
  const baseWaste = nonNegNum(options.wastagePct, 10);
  const pattern = options.pattern === 'staggered' ? 'staggered' : 'grid';
  const extraStaggeredWaste = nonNegNum(options.staggeredExtraWastePct, 5);
  const effectiveWastePct = baseWaste + (pattern === 'staggered' ? extraStaggeredWaste : 0);
  const wasteFactor = 1 + effectiveWastePct / 100;

  const groutMm = nonNegNum(options.groutMm, 2);
  const groutThickMm = nonNegNum(options.groutThicknessMm, 9);
  const groutDensity = nonNegNum(options.groutDensityKgPerL, 1.6);
  const adhesiveCov = nonNegNum(options.adhesiveCoverageKgPerSqm, 5);
  const bagKg = Math.max(1, nonNegNum(options.bagWeightKg, 20));

  const openings = options.openings || {};
  const backWallArea = Math.max(0, w * h - nonNegNum(openings.backWall, 0));
  const sideWallArea = Math.max(0, d * h - nonNegNum(openings.sideWall, 0));
  const floorArea = Math.max(0, w * d - nonNegNum(openings.floor, 0));

  const surfaceDefs = [
    { role: 'Floor', sku: surfaces.floor, netSqM: floorArea },
    { role: 'Feature Wall', sku: surfaces.backWall, netSqM: backWallArea },
    { role: 'Side Wall', sku: surfaces.sideWall, netSqM: sideWallArea },
  ];

  const grouped = new Map();

  for (const s of surfaceDefs) {
    if (!s.sku) continue;
    const key = String(s.sku.id ?? `${s.sku.series || ''}|${s.sku.name || ''}`);
    if (!grouped.has(key)) {
      grouped.set(key, {
        key,
        sku: s.sku,
        spec: readTileSpec(s.sku),
        roles: [],
        netSqM: 0,
        skirtingLengthM: 0,
      });
    }
    const entry = grouped.get(key);
    entry.roles.push(s.role);
    entry.netSqM += s.netSqM;
  }

  const skirting = options.skirting || {};
  if (skirting.enabled && surfaces.floor) {
    const skirtLen = nonNegNum(skirting.lengthM, 0);
    const key = String(surfaces.floor.id ?? `${surfaces.floor.series || ''}|${surfaces.floor.name || ''}`);
    if (!grouped.has(key)) {
      grouped.set(key, {
        key,
        sku: surfaces.floor,
        spec: readTileSpec(surfaces.floor),
        roles: [],
        netSqM: 0,
        skirtingLengthM: 0,
      });
    }
    const entry = grouped.get(key);
    if (!entry.roles.includes('Skirting')) entry.roles.push('Skirting');
    entry.skirtingLengthM += skirtLen;
  }

  let incomplete = false;
  let totalNetSqM = 0;
  let totalGrossSqM = 0;
  let totalPurchasedSqFt = 0;
  let totalAmount = 0;
  let totalAdhesiveKg = 0;
  let totalGroutKg = 0;

  const lines = [];

  for (const entry of grouped.values()) {
    const { spec, sku, roles, netSqM, skirtingLengthM } = entry;
    const flags = [];
    if (!spec.sizeKnown) flags.push('size-missing');
    if (!spec.rateKnown) flags.push('rate-missing');
    if (spec.sizeKnown && !spec.piecesPerBox) flags.push('box-size-unknown');

    const grossSqM = netSqM * wasteFactor;
    const grossSqFt = grossSqM * SQFT_PER_SQM;
    const adhKg = adhesiveKg(grossSqM, adhesiveCov);

    let pieces = null;
    let boxes = null;
    let purchasedPieces = null;
    let purchasedSqFt = null;
    let amount = null;
    let groutKg = 0;
    let sizeLabel = 'Size unknown';

    if (spec.sizeKnown) {
      sizeLabel = `${spec.widthMm}x${spec.heightMm}mm`;
      const pitchW_m = (spec.widthMm + groutMm) / 1000;
      const pitchH_m = (spec.heightMm + groutMm) / 1000;
      const pitchAreaSqM = Math.max(1e-6, pitchW_m * pitchH_m);
      const areaPieces = grossSqM > 0 ? Math.ceil(grossSqM / pitchAreaSqM - 1e-9) : 0;

      let skirtTiles = 0;
      if (skirtingLengthM > 0) {
        const shortSideMm = Math.min(spec.widthMm, spec.heightMm);
        const longSideMm = Math.max(spec.widthMm, spec.heightMm);
        const perStripLenM = Math.max(0.1, longSideMm / 1000);
        const stripsNeeded = Math.ceil((skirtingLengthM / perStripLenM) * wasteFactor - 1e-9);
        const perTile = stripsPerTile(shortSideMm, 100, 3);
        skirtTiles = perTile > 0 ? Math.ceil(stripsNeeded / perTile - 1e-9) : 0;
      }

      pieces = areaPieces + skirtTiles;

      if (spec.piecesPerBox) {
        boxes = Math.ceil(pieces / spec.piecesPerBox - 1e-9);
        purchasedPieces = boxes * spec.piecesPerBox;
      } else {
        purchasedPieces = pieces;
      }

      const tileAreaSqM = (spec.widthMm / 1000) * (spec.heightMm / 1000);
      purchasedSqFt = purchasedPieces * tileAreaSqM * SQFT_PER_SQM;
      groutKg = groutKgPerSqm(spec.widthMm, spec.heightMm, groutThickMm, groutMm, groutDensity) * netSqM;

      if (spec.rateKnown) {
        amount = Math.round(purchasedSqFt * spec.rate);
      }
    }

    if (!spec.sizeKnown || !spec.rateKnown) {
      incomplete = true;
    }

    totalNetSqM += netSqM;
    totalGrossSqM += grossSqM;
    totalAdhesiveKg += adhKg;
    totalGroutKg += groutKg;
    if (purchasedSqFt !== null) totalPurchasedSqFt += purchasedSqFt;
    if (amount !== null) totalAmount += amount;

    lines.push({
      key: entry.key,
      series: sku.series || '—',
      name: sku.name || entry.key,
      roles,
      sizeLabel,
      netSqM,
      grossSqM,
      grossSqFt,
      pieces,
      boxes,
      purchasedPieces,
      purchasedSqFt,
      rate: spec.rate,
      amount,
      adhesiveKg: adhKg,
      groutKg,
      flags,
    });
  }

  return {
    lines,
    totals: {
      incomplete,
      effectiveWastePct,
      netSqM: totalNetSqM,
      grossSqM: totalGrossSqM,
      purchasedSqFt: totalPurchasedSqFt,
      amount: totalAmount,
      adhesiveKg: totalAdhesiveKg,
      adhesiveBags: Math.ceil(totalAdhesiveKg / bagKg - 1e-9),
      groutKg: totalGroutKg,
      groutAssumedThicknessMm: groutThickMm,
    },
  };
}

export function csvCell(value) {
  let str = String(value ?? '');
  if (/^[=+\-@\t\r]/.test(str)) {
    str = `'${str}`;
  }
  return `"${str.replace(/"/g, '""')}"`;
}

export function boqToCsv(boq) {
  const headers = [
    'Surfaces',
    'Series',
    'SKU Name',
    'Size',
    'Pieces',
    'Boxes',
    'Purchased_SqFt',
    'Rate_INR_SqFt',
    'Amount_INR',
    'Adhesive_Kg',
    'Grout_Kg',
    'Flags',
  ];
  const rows = [headers.map(csvCell).join(',')];

  for (const l of boq.lines || []) {
    rows.push([
      csvCell((l.roles || []).join(' + ')),
      csvCell(l.series),
      csvCell(l.name),
      csvCell(l.sizeLabel),
      csvCell(l.pieces ?? ''),
      csvCell(l.boxes ?? ''),
      csvCell(l.purchasedSqFt !== null && l.purchasedSqFt !== undefined ? l.purchasedSqFt.toFixed(2) : ''),
      csvCell(l.rate ?? ''),
      csvCell(l.amount ?? ''),
      csvCell((l.adhesiveKg || 0).toFixed(2)),
      csvCell((l.groutKg || 0).toFixed(2)),
      csvCell((l.flags || []).join('; ')),
    ].join(','));
  }

  const t = boq.totals || {};
  const statusFlags = t.incomplete ? 'INCOMPLETE' : '';
  rows.push([
    csvCell('TOTAL'),
    csvCell(''),
    csvCell(''),
    csvCell(''),
    csvCell(''),
    csvCell(''),
    csvCell(t.purchasedSqFt !== undefined ? t.purchasedSqFt.toFixed(2) : ''),
    csvCell(''),
    csvCell(t.amount ?? ''),
    csvCell((t.adhesiveKg || 0).toFixed(2)),
    csvCell((t.groutKg || 0).toFixed(2)),
    csvCell(statusFlags),
  ].join(','));

  return rows.join('\n');
}