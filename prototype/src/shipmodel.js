/**
 * Mô hình 3D của tàu — dùng chung cho trang xem trước (WebGL) và bộ dựng ảnh
 * tĩnh trong `tools/render_ship.mjs` (rasterizer phần mềm, không cần trình duyệt).
 *
 * Quy ước: mũi tàu hướng -Z, +Y là "lên" (bề dày), +X sang phải.
 * Nhìn từ trên xuống (camera ở +Y, up = -Z) sẽ ra đúng hình chiếu đứng.
 */
import * as THREE from 'three';

export const PALETTE = {
  orange: 0xf07c24,
  orangeLight: 0xffa33f,
  orangeDark: 0xa8421c,
  cream: 0xffe8c6,
  creamShade: 0xefd0a2,
  navy: 0x0c1528,
  navySoft: 0x27334f,
  metal: 0x9fb2cc,
  glass: 0x35d9ff,
  glassDark: 0x093f63,
  flame: 0xff9a3a,
  flameCore: 0xfff4cd,
  trim: 0xffd166,
  red: 0xff5a6a,
  green: 0x5cffa8,
};

const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({
  color, roughness: 0.56, metalness: 0.2, ...opts,
});

const glow = (color, intensity = 1, opts = {}) => new THREE.MeshStandardMaterial({
  color, emissive: color, emissiveIntensity: intensity, roughness: 0.35, metalness: 0.05, ...opts,
});

/* ---------------------------------------------------------------- thân tàu */
const PROFILE = [
  [0, 1], [0.74, 0.82], [1, 0], [0.74, -0.82], [0, -1], [-0.74, -0.82], [-1, 0], [-0.74, 0.82],
];

/** Mặt cắt từ mũi (-Z) tới đuôi (+Z): [z, nửa rộng, nửa cao, lệch Y] */
const SECTIONS = [
  [-2.34, 0.02, 0.02, 0.012],
  [-2.10, 0.12, 0.09, 0.012],
  [-1.78, 0.25, 0.17, 0.010],
  [-1.30, 0.40, 0.24, 0.006],
  [-0.72, 0.50, 0.33, 0],
  [0.02, 0.54, 0.36, 0],
  [0.72, 0.50, 0.32, 0],
  [1.10, 0.43, 0.24, 0],
  [1.34, 0.34, 0.19, 0],
];

/** Vật liệu theo dải quanh mặt cắt: vai trên, hông, hông dưới, bụng. */
const HULL_FACE_MAT = [1, 0, 2, 3, 3, 2, 0, 1];

const hullMats = () => [
  mat(PALETTE.cream, { roughness: 0.6 }),   // 0 hông trên
  mat(PALETTE.orange),                       // 1 sống lưng
  mat(PALETTE.orangeDark, { roughness: 0.62 }), // 2 hông dưới
  mat(PALETTE.navy, { roughness: 0.7 }),    // 3 bụng
];

function ringsFromSections() {
  return SECTIONS.map(([z, hw, hh, yOff]) => PROFILE.map(([px, py]) => new THREE.Vector3(px * hw, py * hh + yOff, z)));
}

/** Nội suy mặt cắt thân tại cao độ z bất kỳ. */
function hullAt(z) {
  const zz = Math.max(SECTIONS[0][0], Math.min(SECTIONS.at(-1)[0], z));
  for (let i = 0; i < SECTIONS.length - 1; i++) {
    const a = SECTIONS[i];
    const b = SECTIONS[i + 1];
    if (zz <= b[0]) {
      const t = (zz - a[0]) / (b[0] - a[0] || 1);
      return {
        hw: a[1] + (b[1] - a[1]) * t,
        hh: a[2] + (b[2] - a[2]) * t,
        yOff: a[3] + (b[3] - a[3]) * t,
      };
    }
  }
  const last = SECTIONS.at(-1);
  return { hw: last[1], hh: last[2], yOff: last[3] };
}

function buildHull() {
  const pos = [];
  const push = (a, b, c) => pos.push(a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z);
  const rings = ringsFromSections();
  // Xếp theo từng dải k để nhóm vật liệu nằm liền mạch (k * perRing).
  for (let k = 0; k < PROFILE.length; k++) {
    const k2 = (k + 1) % PROFILE.length;
    for (let i = 0; i < rings.length - 1; i++) {
      const A = rings[i];
      const B = rings[i + 1];
      push(A[k], B[k], B[k2]);
      push(A[k], B[k2], A[k2]);
    }
  }
  const nose = new THREE.Vector3(0, SECTIONS[0][3], SECTIONS[0][0] - 0.02);
  const tail = new THREE.Vector3(0, SECTIONS.at(-1)[3], SECTIONS.at(-1)[0] + 0.02);
  for (let k = 0; k < PROFILE.length; k++) {
    const k2 = (k + 1) % PROFILE.length;
    push(nose, rings[0][k2], rings[0][k]);
    push(tail, rings.at(-1)[k], rings.at(-1)[k2]);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.computeVertexNormals();

  // Nhóm theo dải để tô màu: vai sáng, hông cam, bụng tối.
  const perRing = (rings.length - 1) * 6;
  for (let k = 0; k < PROFILE.length; k++) g.addGroup(k * perRing, perRing, HULL_FACE_MAT[k]);
  // hai nắp mũi/đuôi
  const capStart = PROFILE.length * perRing;
  g.addGroup(capStart, pos.length / 3 - capStart, 2);
  return g;
}

/** Dải phẳng bám theo sống lưng, uốn theo độ cao thân. */
function dorsalStrip(halfW, lift, z0, z1, color, segments = 26) {
  const pos = [];
  const pt = (z, side) => {
    const h = hullAt(z);
    const x = side * Math.min(halfW, h.hw * 0.85);
    // bề mặt octagon gần đỉnh: y ≈ hh * (1 - 0.24 * |x| / hw)
    const y = h.yOff + h.hh * (1 - 0.24 * Math.abs(x) / Math.max(0.001, h.hw)) + lift;
    return new THREE.Vector3(x, y, z);
  };
  for (let i = 0; i < segments; i++) {
    const za = z0 + (z1 - z0) * (i / segments);
    const zb = z0 + (z1 - z0) * ((i + 1) / segments);
    const a0 = pt(za, -1); const a1 = pt(za, 1);
    const b0 = pt(zb, -1); const b1 = pt(zb, 1);
    pos.push(a0.x, a0.y, a0.z, b0.x, b0.y, b0.z, b1.x, b1.y, b1.z);
    pos.push(a0.x, a0.y, a0.z, b1.x, b1.y, b1.z, a1.x, a1.y, a1.z);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.computeVertexNormals();
  return new THREE.Mesh(g, mat(color, { roughness: 0.6 }));
}

/* ------------------------------------------------------------------- cánh */
const SPAN = 1.66;

function wingOutline(span = SPAN) {
  return [
    [0, 1.04], [span * 0.3, 0.72], [span * 0.62, 0.34], [span * 0.8, 0.16],
    [span, 0.06], [span * 0.99, -0.28], [span * 0.8, -0.58], [span * 0.46, -0.86],
    [span * 0.18, -1.02], [0, -1.12],
  ];
}

function shapeFromPoints(pts, sign = 1) {
  const s = new THREE.Shape();
  pts.forEach(([x, y], i) => (i === 0 ? s.moveTo(x * sign, y) : s.lineTo(x * sign, y)));
  s.closePath();
  return s;
}

function wingGeometry(sign, span = SPAN) {
  const geo = new THREE.ExtrudeGeometry(shapeFromPoints(wingOutline(span), sign), {
    depth: 0.14, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.022, bevelSegments: 2,
  });
  geo.rotateX(-Math.PI / 2); // mặt phẳng cánh nằm ngang, +Y của shape → -Z (về phía mũi)
  geo.translate(0, -0.055, 0);
  geo.computeVertexNormals();
  return geo;
}

/** Dải kem chạy dọc mép trước cánh (nằm trên mặt cánh). */
function leadingBand(sign, span = SPAN) {
  const outer = wingOutline(span).slice(0, 4);
  const bandGeo = (from, to) => {
    const a = outer.map(([x, y]) => [x, y - from]);
    const b = outer.map(([x, y]) => [x, y - to]).reverse();
    const g = new THREE.ShapeGeometry(shapeFromPoints([...a, ...b], sign));
    g.rotateX(-Math.PI / 2);
    return g;
  };
  const group = new THREE.Group();
  const cream = new THREE.Mesh(bandGeo(0, 0.14), mat(PALETTE.cream, { roughness: 0.62 }));
  cream.position.y = 0.098;
  group.add(cream);
  const line = new THREE.Mesh(bandGeo(0.155, 0.18), mat(PALETTE.navy, { roughness: 0.65 }));
  line.position.y = 0.0995;
  group.add(line);
  return group;
}

function finGeometry(sign, pts, depth = 0.07) {
  const g = new THREE.ExtrudeGeometry(shapeFromPoints(pts, sign), { depth, bevelEnabled: false });
  g.rotateX(-Math.PI / 2);
  g.computeVertexNormals();
  return g;
}

/* --------------------------------------------------------------- dựng tàu */
export function buildShip({ scale = 1 } = {}) {
  const root = new THREE.Group();
  root.name = 'ship';

  const body = new THREE.Group();
  root.add(body);

  const M = hullMats();

  /* ---- thân ---- */
  const hull = new THREE.Mesh(buildHull(), M);
  hull.name = 'hull';
  body.add(hull);

  // sống lưng kem + đường kẻ navy
  const spine = dorsalStrip(0.095, 0.008, -2.28, 1.26, PALETTE.cream);
  spine.name = 'spine';
  body.add(spine);
  const pinstripe = dorsalStrip(0.02, 0.016, -1.55, 1.16, PALETTE.navy);
  body.add(pinstripe);

  /* ---- mũi ---- */

  const sensor = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.02, 0.16), glow(PALETTE.glass, 0.9));
  sensor.position.set(0, 0.2, -1.78);
  body.add(sensor);

  /* ---- buồng lái ---- */
  const well = new THREE.Mesh(new THREE.SphereGeometry(0.3, 20, 14), mat(PALETTE.glassDark, { roughness: 0.4, metalness: 0.4 }));
  well.scale.set(0.8, 0.38, 1.3);
  well.position.set(0, 0.30, -0.74);
  body.add(well);

  const cockpitFloor = new THREE.Mesh(new THREE.CircleGeometry(0.33, 24), mat(0x072436, { roughness: 0.8 }));
  cockpitFloor.rotation.x = -Math.PI / 2;
  cockpitFloor.scale.set(0.72, 1.3, 1);
  cockpitFloor.position.set(0, 0.245, -0.74);
  body.add(cockpitFloor);
  const pilot = new THREE.Mesh(new THREE.SphereGeometry(0.1, 14, 10), mat(PALETTE.navy, { roughness: 0.6 }));
  pilot.scale.set(1, 1.1, 1.05);
  pilot.position.set(0, 0.35, -0.7);
  body.add(pilot);
  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.045, 0.05), glow(PALETTE.trim, 1.0));
  visor.position.set(0, 0.38, -0.78);
  body.add(visor);

  const canopy = new THREE.Mesh(
    new THREE.SphereGeometry(0.3, 24, 18),
    glow(0x16b6e8, 0.42, { roughness: 0.1, metalness: 0.05, transparent: true, opacity: 0.96, depthWrite: false }),
  );
  canopy.scale.set(0.74, 0.56, 1.26);
  canopy.position.set(0, 0.32, -0.74);
  canopy.renderOrder = 2;
  body.add(canopy);

  const canopyRim = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.016, 6, 36), mat(PALETTE.cream));
  canopyRim.rotation.x = Math.PI / 2;
  canopyRim.scale.set(0.76, 1.31, 1);
  canopyRim.position.set(0, 0.33, -0.74);
  body.add(canopyRim);

  // gân khung trên nắp kính
  const canopyRib = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.012, 0.026), mat(PALETTE.cream));
  canopyRib.position.set(0, 0.415, -0.74);
  body.add(canopyRib);
  const canopySpine = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.012, 0.62), mat(PALETTE.creamShade));
  canopySpine.position.set(0, 0.41, -0.74);
  body.add(canopySpine);

  /* ---- hai cánh (tách riêng để vỗ) ---- */
  const wings = [];
  for (const sign of [1, -1]) {
    const pivot = new THREE.Group();
    pivot.position.set(sign * 0.3, -0.03, 0.03);
    pivot.rotation.z = sign * -0.035; // hơi vểnh lên ở đầu cánh

    const wing = new THREE.Mesh(wingGeometry(sign), [mat(PALETTE.orange), mat(PALETTE.creamShade, { roughness: 0.6 })]);
    pivot.add(wing);

    const band = leadingBand(sign);
    pivot.add(band);

    // vạch kem ngang thân cánh
    const tick = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.012, 0.045), mat(PALETTE.cream));
    tick.position.set(sign * 0.9, 0.12, 0.26);
    tick.rotation.y = sign * -0.5;
    pivot.add(tick);

    // gân tối chạy dọc cánh
    for (const [rx, rz, rl, rr] of [[0.52, 0.02, 0.5, -0.62], [1.02, -0.1, 0.42, -0.5]]) {
      const rib = new THREE.Mesh(new THREE.BoxGeometry(0.016, 0.01, rl), mat(PALETTE.orangeDark));
      rib.position.set(sign * rx, 0.128, rz);
      rib.rotation.y = sign * rr;
      pivot.add(rib);
    }

    // cánh tà sau (rung nhẹ khi bay)
    // cánh tà sau: bản lề thật, mỗi nhịp lại hạ xuống một chút
    const flapGroup = new THREE.Group();
    const hingeMid = new THREE.Vector2(0.75, -0.71);
    flapGroup.position.set(sign * hingeMid.x, 0.092, -hingeMid.y);
    const flapPts = [
      [1.36, -0.56], [0.83, -0.82], [0.33, -1.0], [0.14, -1.1],
      [0.14, -0.9], [0.33, -0.8], [0.83, -0.62], [1.36, -0.36],
    ].map(([x, y]) => [x - hingeMid.x, y - hingeMid.y]);
    const flapGeo = new THREE.ExtrudeGeometry(shapeFromPoints(flapPts, sign), {
      depth: 0.035, bevelEnabled: false,
    });
    flapGeo.rotateX(-Math.PI / 2);
    const flapMesh = new THREE.Mesh(flapGeo, mat(PALETTE.creamShade, { roughness: 0.62 }));
    flapGroup.add(flapMesh);
    const hingeLine = new THREE.Mesh(new THREE.BoxGeometry(1.24, 0.016, 0.03), mat(PALETTE.navy));
    hingeLine.position.set(0, 0.032, 0.02);
    hingeLine.rotation.y = sign * 0.42;
    flapGroup.add(hingeLine);
    const hingeAxis = new THREE.Vector3(-1.22 * sign, 0, 0.54).normalize();
    pivot.add(flapGroup);

    // đèn trang trí nháy theo nhịp
    const wingLights = [];
    for (let li = 0; li < 3; li++) {
      const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), glow(PALETTE.glass, 1.3));
      lamp.position.set(sign * (0.72 + li * 0.26), 0.13, -0.02 - li * 0.2);
      pivot.add(lamp);
      wingLights.push(lamp);
    }

    // cụm đầu cánh + đèn
    const pod = new THREE.Mesh(new THREE.CapsuleGeometry(0.072, 0.34, 6, 12), mat(PALETTE.cream));
    pod.rotation.x = Math.PI / 2;
    pod.position.set(sign * 1.6, 0.11, 0.06);
    pivot.add(pod);

    const podTip = new THREE.Mesh(new THREE.SphereGeometry(0.055, 12, 10), glow(PALETTE.glass, 0.9));
    podTip.position.set(sign * 1.6, 0.12, -0.16);
    pivot.add(podTip);

    // cánh nhỏ ở đầu mút — rung lên khi bay
    const winglet = new THREE.Mesh(finGeometry(sign, [[0, 0.14], [sign * 0.22, -0.02], [sign * 0.18, -0.14], [0, -0.16]], 0.035), mat(PALETTE.orange));
    winglet.position.set(sign * 1.62, 0.1, 0.26);
    pivot.add(winglet);

    // đèn định vị đỏ / xanh
    const nav = new THREE.Mesh(
      new THREE.SphereGeometry(0.05, 10, 8),
      glow(sign > 0 ? PALETTE.green : PALETTE.red, 1.4),
    );
    nav.position.set(sign * 1.7, 0.13, 0.2);
    pivot.add(nav);

    body.add(pivot);
    wings.push({ pivot, sign, pod, podTip, winglet, nav, band, wing, flapGroup, hingeAxis, wingLights });
  }

  /* ---- cánh mũi ---- */
  // râu cảm biến ở mũi — rung qua lại, thấy rõ từ trên
  const feelers = [];
  for (const sign of [1, -1]) {
    const feelerPivot = new THREE.Group();
    feelerPivot.position.set(sign * 0.13, 0.2, -1.86);
    body.add(feelerPivot);
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.014, 0.46, 6), mat(PALETTE.navy));
    rod.rotation.z = Math.PI / 2;
    rod.rotation.y = sign * 0.5;
    rod.position.set(sign * 0.19, 0, -0.06);
    feelerPivot.add(rod);
    const tip = new THREE.Mesh(new THREE.SphereGeometry(0.028, 8, 6), glow(PALETTE.trim, 1.2));
    tip.position.set(sign * 0.37, 0.005, -0.16);
    feelerPivot.add(tip);
    feelers.push({ pivot: feelerPivot, tip, sign });
  }

  /* ---- đuôi ---- */
  // vây đứng giữa: từ trên xuống chỉ là một sống mảnh, nhưng ở góc nghiêng thấy rõ
  const dorsalFinShape = new THREE.Shape();
  dorsalFinShape.moveTo(-0.05, 0);
  dorsalFinShape.lineTo(0.42, 0);
  dorsalFinShape.lineTo(0.62, 0.4);
  dorsalFinShape.lineTo(0.28, 0.46);
  dorsalFinShape.lineTo(-0.05, 0.12);
  dorsalFinShape.closePath();
  const dorsalFin = new THREE.Mesh(
    new THREE.ExtrudeGeometry(dorsalFinShape, { depth: 0.05, bevelEnabled: false }),
    mat(PALETTE.orange),
  );
  dorsalFin.rotation.y = -Math.PI / 2;
  dorsalFin.position.set(0.025, 0.26, 1.02);
  body.add(dorsalFin);
  // dải kem mảnh ở mép trên vây đứng
  const dorsalFinCap = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.018, 0.36), mat(PALETTE.cream));
  dorsalFinCap.position.set(0, 0.665, 1.27);
  dorsalFinCap.rotation.x = -0.42;
  body.add(dorsalFinCap);

  // chóp đuôi giữa hai động cơ
  const tailCone = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.46, 14), mat(PALETTE.cream));
  tailCone.rotation.x = Math.PI / 2;
  tailCone.position.set(0, 0, 1.46);
  body.add(tailCone);
  const tailLamp = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), glow(PALETTE.red, 1.3));
  tailLamp.position.set(0, 0.03, 1.7);
  body.add(tailLamp);

  /* ---- hai cụm động cơ ---- */
  const engines = [];
  for (const sign of [1, -1]) {
    const gx = sign * 0.36;

    const nacelle = new THREE.Mesh(new THREE.CapsuleGeometry(0.19, 0.64, 8, 16), mat(0x35496b, { roughness: 0.42, metalness: 0.55 }));
    nacelle.rotation.x = Math.PI / 2;
    nacelle.position.set(gx, -0.02, 1.28);
    body.add(nacelle);

    const intake = new THREE.Mesh(new THREE.CylinderGeometry(0.198, 0.196, 0.07, 18), mat(PALETTE.creamShade));
    intake.rotation.x = Math.PI / 2;
    intake.position.set(gx, -0.02, 1.0);
    body.add(intake);

    const intakeLip = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.025, 18), mat(PALETTE.navy));
    intakeLip.rotation.x = Math.PI / 2;
    intakeLip.position.set(gx, -0.02, 0.965);
    body.add(intakeLip);

    const band = new THREE.Mesh(new THREE.CylinderGeometry(0.207, 0.207, 0.09, 18), mat(PALETTE.orange));
    band.rotation.x = Math.PI / 2;
    band.position.set(gx, -0.02, 1.64);
    body.add(band);

    const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.145, 0.2, 0.2, 18), mat(PALETTE.metal, { metalness: 0.7, roughness: 0.3 }));
    nozzle.rotation.x = Math.PI / 2;
    nozzle.position.set(gx, -0.02, 1.9);
    body.add(nozzle);

    const vent = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.018, 0.26), mat(PALETTE.cream, { roughness: 0.6 }));
    vent.position.set(gx, 0.2, 1.3);
    body.add(vent);
    const vent2 = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.01, 0.026), mat(PALETTE.creamShade));
    vent2.position.set(gx, 0.195, 1.44);
    body.add(vent2);

    const nozzleGlow = new THREE.Mesh(new THREE.CylinderGeometry(0.125, 0.125, 0.03, 18), glow(PALETTE.flameCore, 2.2));
    nozzleGlow.rotation.x = Math.PI / 2;
    nozzleGlow.position.set(gx, -0.02, 1.99);
    body.add(nozzleGlow);

    // lửa phản lực: đáy ở miệng ống, đỉnh vuốt về phía sau
    const flame = new THREE.Mesh(
      new THREE.ConeGeometry(0.155, 1, 16, 1, true),
      new THREE.MeshBasicMaterial({ color: 0xff7a1e, transparent: true, opacity: 0.62, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }),
    );
    flame.rotation.x = Math.PI / 2;
    flame.position.set(gx, -0.02, 2.0);
    body.add(flame);

    const core = new THREE.Mesh(
      new THREE.ConeGeometry(0.068, 1, 12, 1, true),
      new THREE.MeshBasicMaterial({ color: 0xffe6a0, transparent: true, opacity: 0.72, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }),
    );
    core.rotation.x = Math.PI / 2;
    core.position.set(gx, -0.02, 2.0);
    body.add(core);

    // quầng sáng quanh miệng ống (nhìn từ trên là vòng sáng)
    const halo = new THREE.Mesh(
      new THREE.CircleGeometry(0.2, 20),
      new THREE.MeshBasicMaterial({ color: 0xff8a2a, transparent: true, opacity: 0.16, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }),
    );
    halo.rotation.x = -Math.PI / 2;
    halo.position.set(gx, -0.03, 2.0);
    body.add(halo);

    // hai "viên kim cương" sáng trong luồng phụt
    const diamonds = [0, 1].map((i) => {
      const d = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 6), glow(PALETTE.flameCore, 2));
      d.position.set(gx, -0.02, 2.16 + i * 0.14);
      body.add(d);
      return d;
    });

    engines.push({ nacelle, intake, band, nozzle, nozzleGlow, flame, core, halo, diamonds, sign, gx });
  }

  /* ---- hai khẩu pháo ở gốc cánh — đạn bay ra đúng đầu nòng ---- */
  const guns = [];
  for (const sign of [1, -1]) {
    const gx = sign * 0.68;

    const mount = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.12, 0.42), mat(PALETTE.orangeDark, { roughness: 0.5 }));
    mount.position.set(gx, 0.045, -0.6);
    body.add(mount);

    const mountTop = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.035, 0.3), mat(PALETTE.cream));
    mountTop.position.set(gx, 0.115, -0.62);
    body.add(mountTop);

    const strut = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.05, 0.14), mat(PALETTE.creamShade));
    strut.position.set(sign * 0.58, 0.02, -1.02);
    strut.rotation.z = sign * 0.16;
    body.add(strut);

    // vỏ ốp thuôn nối cụm súng vào mép cánh
    const fairing = new THREE.Mesh(
      finGeometry(sign, [[0, 0.34], [sign * 0.15, 0.03], [sign * 0.13, -0.2], [0, -0.28]], 0.07),
      mat(PALETTE.creamShade, { roughness: 0.55 }),
    );
    fairing.position.set(sign * 0.5, 0.02, -0.62);
    body.add(fairing);

    const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.058, 0.072, 0.8, 14), mat(PALETTE.metal, { metalness: 0.65, roughness: 0.3 }));
    barrel.rotation.x = Math.PI / 2;
    barrel.position.set(gx, 0.045, -1.12);
    body.add(barrel);

    for (const [bz, bw, bh] of [[-1.02, 0.15, 0.05], [-1.24, 0.135, 0.04]]) {
      const ring = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, 0.09), mat(PALETTE.orangeDark));
      ring.position.set(gx, 0.09, bz);
      body.add(ring);
    }

    const brake = new THREE.Mesh(new THREE.CylinderGeometry(0.082, 0.082, 0.16, 14), mat(PALETTE.metal, { metalness: 0.7, roughness: 0.28 }));
    brake.rotation.x = Math.PI / 2;
    brake.position.set(gx, 0.045, -1.6);
    body.add(brake);

    const muzzleRing = new THREE.Mesh(new THREE.TorusGeometry(0.068, 0.016, 6, 16), glow(PALETTE.trim, 0.85));
    muzzleRing.position.set(gx, 0.045, -1.69);
    body.add(muzzleRing);

    // chớp đầu nòng hình ngôi sao 4 cánh (nằm ngang, thấy rõ từ trên)
    const star = new THREE.Shape();
    const spikes = 4;
    for (let i = 0; i < spikes * 2; i++) {
      const a = (i / (spikes * 2)) * Math.PI * 2;
      const r = i % 2 === 0 ? 0.135 : 0.038;
      const px = Math.cos(a) * r;
      const py = Math.sin(a) * r;
      if (i === 0) star.moveTo(px, py); else star.lineTo(px, py);
    }
    star.closePath();
    const flashGeo = new THREE.ShapeGeometry(star);
    flashGeo.rotateX(-Math.PI / 2);
    const flash = new THREE.Mesh(flashGeo, new THREE.MeshBasicMaterial({ color: 0xffd166, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
    flash.position.set(gx, 0.06, -1.76);
    body.add(flash);

    const muzzle = new THREE.Vector3(gx, 0.045, -1.78);
    const muzzleAnchor = new THREE.Object3D();
    muzzleAnchor.position.copy(muzzle);
    body.add(muzzleAnchor);

    guns.push({ sign, gx, mount, barrel, brake, muzzleRing, flash, muzzleAnchor, muzzle, baseZ: barrel.position.z });
  }

  /* ---- ăng-ten rung ---- */
  const antennaPivot = new THREE.Group();
  antennaPivot.position.set(0, 0.26, 1.05);
  body.add(antennaPivot);
  const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.016, 0.44, 6), mat(PALETTE.navy));
  antenna.position.set(0, 0.22, 0);
  antennaPivot.add(antenna);
  const antennaTip = new THREE.Mesh(new THREE.SphereGeometry(0.032, 8, 6), glow(PALETTE.trim, 1.3));
  antennaTip.position.set(0, 0.45, 0);
  antennaPivot.add(antennaTip);

  root.scale.setScalar(scale);
  root.updateMatrixWorld(true);

  const state = { flap: 1, throttle: 0.7, firing: false, bank: 0, recoil: 0, time: 0 };
  const muzzles = [new THREE.Vector3(), new THREE.Vector3()];

  /**
   * Cập nhật diễn hoạt.
   * @param {number} dt giây
   * @param {number} time tổng thời gian
   * @param {object} next { flap, throttle, firing, bank }
   */
  function update(dt, time, next = {}) {
    Object.assign(state, next);
    state.time = time;

    // ---- cánh vỗ nhẹ + vặn theo nhịp thở
    const flapAmp = 0.3 * state.flap;
    const flapPhase = Math.sin(time * 5.2);
    for (const w of wings) {
      w.pivot.rotation.z = w.sign * (flapAmp * flapPhase + Math.sin(time * 1.7 + w.sign) * 0.012 * state.flap);
      w.pivot.rotation.y = w.sign * (Math.sin(time * 5.2 + 0.55 + w.sign * 0.06) * 0.07 * state.flap + Math.sin(time * 2.4 + w.sign * 0.7) * 0.018 * state.flap);
      w.pivot.rotation.x = Math.sin(time * 5.2 + 0.9) * 0.05 * state.flap;
      const buzz = Math.sin(time * 37 + w.sign) * 0.0045 * (0.35 + state.throttle);
      w.pod.position.y = 0.11 + buzz;
      w.podTip.position.y = 0.12 + buzz * 0.6;
      w.winglet.rotation.x = Math.sin(time * 9.5 + w.sign * 1.3) * 0.28 * state.flap;
      const droop = 0.12 + Math.sin(time * 5.2 + 0.9) * 0.16 * state.flap + state.throttle * 0.06;
      w.flapGroup.quaternion.setFromAxisAngle(w.hingeAxis, droop);
      const navPulse = 0.45 + Math.abs(Math.sin(time * 2.6 + (w.sign > 0 ? 0 : Math.PI))) * 1.3;
      w.nav.material.emissiveIntensity = navPulse;
      w.podTip.material.emissiveIntensity = 0.5 + Math.abs(Math.sin(time * 3.1 + w.sign)) * 0.8;
      w.wingLights.forEach((lamp, li) => {
        const beat = Math.max(0, Math.sin(time * 4.2 - li * 0.9 - (w.sign > 0 ? 0 : 0.45)));
        lamp.material.emissiveIntensity = 0.25 + beat * 1.6;
        lamp.scale.setScalar(0.8 + beat * 0.5);
      });
    }

    // ---- lửa đuôi phụt mạnh / yếu theo ga
    const thrust = 0.45 + state.throttle * 0.8;
    for (const e of engines) {
      const flick = 0.9 + Math.sin(time * 43 + e.sign * 2.1) * 0.06 + Math.sin(time * 19.7 + e.sign) * 0.05;
      const len = (0.42 + thrust * 0.66) * flick;
      const widen = 0.9 + flick * 0.12;
      e.flame.scale.set(widen, len, widen);
      e.flame.position.z = 2.0 + len * 0.5;
      e.flame.material.opacity = 0.45 + Math.min(0.25, state.throttle * 0.26);
      e.core.scale.set(0.85 + flick * 0.1, len * 0.62, 0.85 + flick * 0.1);
      e.core.position.z = 2.0 + len * 0.31;
      e.halo.scale.setScalar(0.7 + flick * 0.2 + state.throttle * 0.22);
      e.halo.material.opacity = 0.16 + state.throttle * 0.16;
      e.nozzleGlow.material.emissiveIntensity = 1.2 + state.throttle * 1.4 + Math.sin(time * 33 + e.sign) * 0.18;
      e.nacelle.position.z = 1.28 + Math.sin(time * 29 + e.sign) * 0.0035;
      e.nacelle.position.y = -0.02 + Math.sin(time * 41 + e.sign) * 0.0022;
      e.diamonds.forEach((d, i) => {
        const s = (0.55 + state.throttle * 0.8) * (0.85 + Math.sin(time * 26 + i * 2 + e.sign) * 0.15);
        d.scale.setScalar(s);
        d.visible = state.throttle > 0.08;
        d.position.z = 2.08 + i * 0.15 * (0.5 + state.throttle);
      });
    }

    // ---- giật nòng khi bắn, nòng rung khi chờ
    state.recoil = Math.max(0, state.recoil - dt * 7);
    if (state.firing) state.recoil = 1;
    for (const g of guns) {
      const idleBuzz = Math.sin(time * 31 + g.sign) * 0.0018 * (0.3 + state.throttle);
      g.barrel.position.z = g.baseZ + state.recoil * 0.1;
      g.barrel.position.x = g.gx + idleBuzz;
      const strobe = 0.45 + Math.abs(Math.sin(time * 26 + g.sign * 1.6)) * 0.55;
      const target = state.firing ? strobe : 0;
      g.flash.material.opacity += (target - g.flash.material.opacity) * Math.min(1, dt * 22);
      const fs = (0.72 + g.flash.material.opacity * 0.7 + state.recoil * 0.15);
      g.flash.scale.set(fs, 1, fs);
      g.flash.rotation.y = Math.sin(time * 3 + g.sign) * 0.3;
      g.flash.position.z = -1.76 + state.recoil * 0.1;
      g.muzzleAnchor.position.z = -1.78 + state.recoil * 0.1;
      g.muzzleRing.position.z = -1.69 + state.recoil * 0.1;
    }

    // ---- buồng lái "thở", ăng-ten rung, thân hơi lắc
    canopy.material.emissiveIntensity = 0.55 + Math.abs(Math.sin(time * 2.2)) * 0.42;
    antennaPivot.rotation.z = Math.sin(time * 47) * 0.07 * (0.35 + state.throttle) + Math.sin(time * 13.7) * 0.025;
    antennaPivot.rotation.x = Math.sin(time * 39 + 1.2) * 0.05 * (0.4 + state.throttle);
    for (const f of feelers) {
      f.pivot.rotation.y = f.sign * (Math.sin(time * 3.4 + f.sign * 1.1) * 0.16 + Math.sin(time * 8.7) * 0.05);
      f.pivot.rotation.z = Math.sin(time * 5.1 + f.sign) * 0.1;
      f.tip.material.emissiveIntensity = 0.8 + Math.abs(Math.sin(time * 6.4 + f.sign)) * 0.9;
    }
    antennaTip.material.emissiveIntensity = 0.8 + Math.abs(Math.sin(time * 5.3)) * 0.9;

    body.rotation.z = state.bank * 0.16 + Math.sin(time * 1.35) * 0.008;
    body.rotation.y = Math.sin(time * 0.8) * 0.009;
    body.position.y = Math.sin(time * 1.6) * 0.008;

    root.updateMatrixWorld(true);
    guns.forEach((g, i) => muzzles[i].copy(g.muzzleAnchor.position).applyMatrix4(body.matrixWorld));
    return { muzzles };
  }

  function getMuzzles() {
    root.updateMatrixWorld(true);
    guns.forEach((g, i) => muzzles[i].copy(g.muzzleAnchor.position).applyMatrix4(body.matrixWorld));
    return muzzles;
  }

  return {
    root, body, parts: { wings, engines, guns, canopy, antenna: antennaPivot, feelers },
    update, getMuzzles, state,
  };
}
