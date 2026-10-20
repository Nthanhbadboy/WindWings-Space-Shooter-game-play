import * as THREE from 'three';
import { glowTexture, moteTexture, streakTexture, sparkleTexture } from './textures.js';

/**
 * NỀN KHÔNG GIAN — ẢNH THẬT, chia lớp theo độ sâu.
 * Chi tiết + ảnh tham chiếu: docs/nen-nhieu-lop.md
 *
 *   L0  VŨ TRỤ SÂU   z −320   ảnh Hubble Ultra Deep Field — **ĐỨNG YÊN TUYỆT ĐỐI**
 *                            (không xoay, không trôi, không parallax, không ăn theo speed)
 *   L1  TINH VÂN     z −292…−308  sương lớn + 3 đám Tarantula/Carina — **ảnh thật, trôi** 0,007→0,014,
 *                            cộng sáng, mép nướng vignette nên tan vào nền
 *   L2  sao xa       z −260   150 điểm, nhỏ, lạnh                 0,006 màn/s
 *   L3  sao giữa     z −170    95 điểm                           0,010
 *   L4  sao gần      z −110    48 điểm, ấm                       0,016
 *   L5  mảnh vụn     z −110…−40  thiên thạch nhỏ                  0,17 → 1,0
 *   L6  bụi          z −95…−20   4 tầng                          0,07 → 1,56
 *   L7  LỚP GẦN      z −1,7…−4,8 bụi lớn + vệt sáng **TRƯỚC tàu** 2,2 → 4,1
 *   L8  vùng giao chiến (Game vẽ)
 *
 * Không có Trái Đất, không có trạm/dầm kim loại, không có tinh vân vẽ tay:
 * lớp nào cũng là ảnh thật hoặc hạt sáng — thứ gì không làm đẹp được thì bỏ.
 *
 * Luật cuộn của lớp tĩnh: tốc độ thế giới = SCROLL / depth, nên tốc độ trên màn hình
 * tỉ lệ 1/depth² — lớp gần nhanh hơn hẳn lớp xa, đó là thứ mắt đọc thành chiều sâu.
 */
export function createBackdrop(scene, camera, textures = {}) {
  const group = new THREE.Group();
  group.name = 'backdrop';
  scene.add(group);

  const vw = () => (typeof window !== 'undefined' ? window.innerWidth : 390);
  const vh = () => (typeof window !== 'undefined' ? window.innerHeight : 844);
  const aspect = () => vw() / vh();
  const tanHalf = () => Math.tan(THREE.MathUtils.degToRad((camera.fov || 46) / 2));

  const SCROLL = 610;
  const viewH = (depth) => 2 * tanHalf() * depth;
  const viewW = (depth) => viewH(depth) * aspect();

  // ======================================================= L0 — vũ trụ sâu
  // ẢNH THẬT. Tuyệt đối đứng yên: nó là tấm nền của vũ trụ, không phải vật thể trong cảnh.
  const skyTex = textures.sky || null;
  let skyMat = null;
  let sky;
  if (skyTex) {
    skyTex.wrapS = THREE.ClampToEdgeWrapping;
    skyTex.wrapT = THREE.ClampToEdgeWrapping;
    skyTex.colorSpace = THREE.SRGBColorSpace;
    sky = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1),
      new THREE.MeshBasicMaterial({
        map: skyTex,
        depthTest: false,
        depthWrite: false,
        toneMapped: false,
        color: 0x9e9e9e, // hạ sáng 0,62 để HUD/đạn luôn nổi
      }),
    );
  } else {
    // dự phòng khi không có ảnh (test node): gradient sạch
    skyMat = new THREE.ShaderMaterial({
      uniforms: {
        uTop: { value: new THREE.Color(0x03050d) },
        uMid: { value: new THREE.Color(0x060d1c) },
        uBottom: { value: new THREE.Color(0x0a1730) },
      },
      vertexShader: /* glsl */`
        varying vec2 vUv;
        void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: /* glsl */`
        uniform vec3 uTop; uniform vec3 uMid; uniform vec3 uBottom;
        varying vec2 vUv;
        float hash(vec2 p){ return fract(sin(dot(p, vec2(41.7, 289.3))) * 43758.5453); }
        void main() {
          vec3 c = mix(uBottom, uMid, smoothstep(0.0, 0.62, vUv.y));
          c = mix(c, uTop, smoothstep(0.52, 1.0, vUv.y));
          c += (hash(vUv * 1024.0) - 0.5) * 0.012;
          gl_FragColor = vec4(max(c, 0.0), 1.0);
        }`,
      depthTest: false,
      depthWrite: false,
      toneMapped: false,
    });
    sky = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), skyMat);
  }
  sky.renderOrder = -1000;
  sky.frustumCulled = false;
  sky.position.z = -320;
  camera.add(sky);

  // ======================================================= L1 — tinh vân thật
  // Bốn lớp mây THẬT (ảnh Hubble/ESO): một tấm sương làm mờ mạnh phủ toàn khung +
  // ba đám cắt từ ảnh 4k. Mép đã nướng vignette nên cộng sáng vào nền là biến mất.
  // Chúng TRÔI chậm xuống, trôi ngang theo camera; không xoay, không vẽ tay.
  // sp = phần chiều cao màn hình trôi được trong 1 giây. Xa hơn thì chậm hơn:
  // z 308 → 0,007 · z 300 → 0,010 · z 296 → 0,012 · z 292 → 0,014
  const CLOUD_DEFS = [
    // tex,        hFrac, xFrac,  yFrac,  speed,  opacity, depth, mirror
    { key: 'nebulaHaze', h: 1.30, x: 0.00, y: 0.18, sp: 0.007, op: 0.62, z: 308, mir: 1 },
    { key: 'nebulaA', h: 0.55, x: 0.06, y: 0.52, sp: 0.010, op: 0.30, z: 300, mir: 1 },
    { key: 'nebulaB', h: 0.46, x: -0.24, y: -0.36, sp: 0.012, op: 0.22, z: 296, mir: 1 },
    { key: 'nebulaC', h: 0.40, x: 0.30, y: 0.06, sp: 0.014, op: 0.20, z: 292, mir: -1 },
  ];
  const NEB_K = 0.72; // hạ sáng ảnh để chữ/HUD và đạn luôn nổi
  const nebula = [];
  for (const def of CLOUD_DEFS) {
    const tex = textures[def.key];
    if (!tex) continue;
    tex.wrapS = THREE.ClampToEdgeWrapping;
    tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.colorSpace = THREE.SRGBColorSpace;
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1),
      new THREE.MeshBasicMaterial({
        map: tex,
        transparent: true,
        opacity: def.op,
        depthWrite: false,
        depthTest: true,
        blending: THREE.AdditiveBlending,
        toneMapped: false,
        side: THREE.DoubleSide,
        color: new THREE.Color(NEB_K, NEB_K, NEB_K),
      }),
    );
    m.renderOrder = -900;
    m.frustumCulled = false;
    m.position.z = -def.z;
    camera.add(m);
    nebula.push({
      mesh: m, tex, def,
      speed: def.sp,
      sway: Math.random() * Math.PI * 2,
      baseX: def.x,
    });
  }

  // ======================================================= L2–L4 — sao
  const makeStarLayer = (count, depth, size, speed, color, opacity) => {
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const hh = tanHalf() * depth;
    const hw = hh * aspect();
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() * 2 - 1) * hw * 1.15;
      pos[i * 3 + 1] = (Math.random() * 2 - 1) * hh * 1.15;
      pos[i * 3 + 2] = -depth;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      size,
      map: sparkleTexture() || textures.dot || null,
      color,
      transparent: true,
      opacity,
      depthWrite: false,
      depthTest: true,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: false,
    });
    const pts = new THREE.Points(geo, mat);
    pts.frustumCulled = false;
    pts.renderOrder = -35;
    camera.add(pts);
    return { pts, pos, count, hh, hw, speed, depth };
  };

  const starLayers = [
    makeStarLayer(150, 260, 4.0, 0.012, 0xffffff, 0.7),
    makeStarLayer(95, 170, 5.4, 0.02, 0xcfe4ff, 0.8),
    makeStarLayer(48, 110, 7.4, 0.032, 0xffe6c2, 0.85),
  ];

  // ======================================================= L5 — mảnh vụn
  const debrisTex = textures.enemyArt?.meteor || null;
  const debris = [];
  for (let i = 0; i < 10; i++) {
    const depth = 40 + Math.random() * 70;
    const hh = tanHalf() * depth;
    const hw = hh * aspect();
    const mat = new THREE.SpriteMaterial({
      map: debrisTex || glowTexture(),
      transparent: true,
      opacity: 0.5 + Math.random() * 0.35,
      depthWrite: false,
      depthTest: true,
      color: new THREE.Color(0x9fb0c8),
      rotation: Math.random() * Math.PI * 2,
    });
    const s = new THREE.Sprite(mat);
    const scale = 0.5 + Math.random() * 1.6;
    s.scale.set(scale, scale, 1);
    s.position.set((Math.random() * 2 - 1) * hw, (Math.random() * 2 - 1) * hh, -depth);
    s.renderOrder = -26;
    camera.add(s);
    debris.push({
      s, hh, hw, depth,
      speed: 6 + (70 / depth) * 16, // đạo cụ: đẩy nhanh hơn luật cho có nhịp
      spin: (Math.random() - 0.5) * 0.9,
      sway: Math.random() * Math.PI * 2,
    });
  }

  // ======================================================= L6 — bụi
  const dustLayers = [];
  const makeDust = (count, depth, size, speed, opacity, useStreak) => {
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const hh = tanHalf() * depth * 1.15;
    const hw = hh * aspect() * 1.1;
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() * 2 - 1) * hw;
      pos[i * 3 + 1] = (Math.random() * 2 - 1) * hh;
      pos[i * 3 + 2] = -depth - Math.random() * depth * 0.25;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      size,
      map: useStreak ? streakTexture() : moteTexture(),
      color: useStreak ? 0xcfe4ff : 0xffffff,
      transparent: true,
      opacity,
      depthWrite: false,
      depthTest: true,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
    });
    const pts = new THREE.Points(geo, mat);
    pts.frustumCulled = false;
    pts.renderOrder = -28;
    camera.add(pts);
    const layer = { pts, pos, count, hh, hw, speed, depth };
    dustLayers.push(layer);
    return layer;
  };

  makeDust(95, 95, 0.30, SCROLL / 95, 0.26, false);
  makeDust(70, 55, 0.22, SCROLL / 55, 0.34, false);
  makeDust(60, 30, 0.52, SCROLL / 30, 0.46, true);
  makeDust(40, 20, 0.62, SCROLL / 20, 0.52, true);

  // ======================================================= L7 — lớp gần
  // Nằm GIỮA camera và tàu → vẽ đè lên tàu/đạn. Chỉ ở rìa, mờ, để không che gameplay.
  const nearField = new THREE.Group();
  nearField.name = 'nearfield';
  camera.add(nearField);

  const edgeX = (hw) => {
    const side = Math.random() < 0.5 ? -1 : 1;
    return side * (hw * 0.58 + Math.random() * hw * 0.42);
  };

  const moteTex = moteTexture() || glowTexture();
  const nearMotes = [];
  for (let i = 0; i < 14; i++) {
    const depth = 2.4 + Math.random() * 2.4;
    const size = 0.26 + Math.random() * 0.85;
    const mat = new THREE.SpriteMaterial({
      map: moteTex,
      color: i % 6 === 0 ? 0xffdfae : 0xa9e4ff,
      transparent: true,
      opacity: 0.05 + Math.random() * 0.08,
      depthWrite: false,
      depthTest: true,
      blending: THREE.AdditiveBlending,
    });
    const s = new THREE.Sprite(mat);
    s.scale.set(size, size, 1);
    s.renderOrder = 30;
    const hh = tanHalf() * depth;
    const hw = hh * aspect() * 1.05;
    s.position.set(edgeX(hw), (Math.random() * 2 - 1) * hh, -depth);
    nearField.add(s);
    nearMotes.push({ s, depth, hh, hw, screenSpeed: 2.2 + (4.8 - depth) * 0.34 + Math.random() * 0.4 });
  }

  const nearStreaks = [];
  for (let i = 0; i < 7; i++) {
    const depth = 1.7 + Math.random() * 0.9;
    const mat = new THREE.SpriteMaterial({
      map: streakTexture() || moteTex,
      color: 0xcfe8ff,
      transparent: true,
      opacity: 0.08 + Math.random() * 0.07,
      depthWrite: false,
      depthTest: true,
      blending: THREE.AdditiveBlending,
    });
    const s = new THREE.Sprite(mat);
    s.scale.set(0.05 + Math.random() * 0.04, 0.5 + Math.random() * 0.7, 1);
    s.renderOrder = 31;
    const hh = tanHalf() * depth;
    const hw = hh * aspect() * 1.05;
    s.position.set(edgeX(hw) * 0.92, (Math.random() * 2 - 1) * hh, -depth);
    nearField.add(s);
    nearStreaks.push({ s, depth, hh, hw, screenSpeed: 3.2 + Math.random() * 0.9 });
  }

  let focusSm = 0;

  // --------------------------------------------------------------- update
  function update(dt, t = 0, opts = {}) {
    const speedMul = opts.speed ?? 1;
    const focus = THREE.MathUtils.clamp(opts.focus ?? 0, -1, 1);
    focusSm += (focus - focusSm) * Math.min(1, dt * 4.5);

    // ---- L0: KHÔNG chạm vào sky. Đứng yên tuyệt đối.

    // ---- L1: ba đám tinh vân thật trôi chậm xuống, hơi lắc ngang
    for (const c of nebula) {
      const vhC = viewH(c.def.z);
      const vwC = viewW(c.def.z);
      const step = c.speed * vhC * dt * speedMul;
      c.mesh.position.y -= step;
      const drift = Math.sin(t * 0.22 + c.sway) * 0.010 * vwC;
      c.mesh.position.x = c.baseX * vwC - focusSm * 0.014 * vwC + drift;
      if (c.mesh.position.y < -vhC * 1.35) {
        c.mesh.position.y = vhC * 1.35;
        c.baseX = (Math.random() * 2 - 1) * 0.5;
      }
    }

    // ---- sao
    for (const L of starLayers) {
      const step = L.speed * L.hh * dt * speedMul;
      for (let i = 0; i < L.count; i++) {
        L.pos[i * 3 + 1] -= step;
        if (L.pos[i * 3 + 1] < -L.hh) L.pos[i * 3 + 1] += L.hh * 2;
      }
      L.pts.geometry.attributes.position.needsUpdate = true;
      L.pts.material.opacity = 0.6 + Math.sin(t * 0.8) * 0.06;
    }

    // ---- bụi
    for (const D of dustLayers) {
      const step = D.speed * dt * speedMul;
      for (let i = 0; i < D.count; i++) {
        const yi = i * 3 + 1;
        D.pos[yi] -= step;
        D.pos[i * 3] += Math.sin(t * 0.6 + i * 0.7) * dt * 0.35;
        if (D.pos[yi] < -D.hh) {
          D.pos[yi] += D.hh * 2;
          D.pos[i * 3] = (Math.random() * 2 - 1) * D.hw;
        } else if (D.pos[i * 3] > D.hw) {
          D.pos[i * 3] -= D.hw * 2;
        } else if (D.pos[i * 3] < -D.hw) {
          D.pos[i * 3] += D.hw * 2;
        }
      }
      D.pts.geometry.attributes.position.needsUpdate = true;
    }

    // ---- mảnh vụn
    for (const d of debris) {
      d.s.position.y -= d.speed * dt * speedMul;
      d.s.position.x += Math.sin(t * 0.35 + d.sway) * dt * 0.8;
      d.s.material.rotation += d.spin * dt;
      if (d.s.position.y < -d.hh) {
        d.s.position.y += d.hh * 2;
        d.s.position.x = (Math.random() * 2 - 1) * d.hw;
      }
    }

    // ---- L7: lớp gần
    nearField.position.x = -focusSm * 0.18 * viewW(3.4);
    for (const m of nearMotes) {
      m.s.position.y -= m.screenSpeed * 2 * m.hh * dt * speedMul;
      m.s.position.x += Math.sin(t * 0.9 + m.depth * 3.1) * dt * 0.02;
      if (m.s.position.y < -m.hh * 1.1) {
        m.s.position.y = m.hh * (1.05 + Math.random() * 0.25);
        m.s.position.x = edgeX(m.hw);
      }
    }
    for (const k of nearStreaks) {
      k.s.position.y -= k.screenSpeed * 2 * k.hh * dt * speedMul;
      if (k.s.position.y < -k.hh * 1.2) {
        k.s.position.y = k.hh * (1.1 + Math.random() * 0.3);
        k.s.position.x = edgeX(k.hw) * 0.92;
      }
    }
  }

  // --------------------------------------------------------------- resize
  function resize(width, height) {
    const w = width || (typeof window !== 'undefined' ? window.innerWidth : 390);
    const h = height || (typeof window !== 'undefined' ? window.innerHeight : 844);
    const a = w / h;

    // sky: phủ kín, giữ đúng tỉ lệ ảnh (cover)
    const fh = viewH(320);
    const viewWpx = fh * a;
    if (skyTex && skyTex.image) {
      const texA = skyTex.image.width / skyTex.image.height;
      let sw = viewWpx;
      let sh = fh;
      if (texA > viewWpx / fh) sw = fh * texA;
      else sh = viewWpx / texA;
      sky.scale.set(sw * 1.02, sh * 1.02, 1);
    } else {
      sky.scale.set(viewWpx * 1.02, fh * 1.02, 1);
    }

    // tinh vân: chiều cao = hFrac * khung nhìn tại độ sâu của nó, rộng theo đúng tỉ lệ ảnh
    for (const c of nebula) {
      const vhC = viewH(c.def.z);
      const vwC = viewW(c.def.z);
      const hh2 = vhC * c.def.h;
      const imgW = c.tex.image?.width || 16;
      const imgH = c.tex.image?.height || 9;
      const ww2 = hh2 * (imgW / imgH);
      c.mesh.scale.set(ww2 * c.def.mir, hh2, 1);
      if (!Number.isFinite(c.mesh.position.y) || c.mesh.position.y === 0) {
        c.mesh.position.y = c.def.y * vhC;
      }
      c.mesh.position.x = c.baseX * vwC;
    }

    // biên cuộn của sao/bụi theo tỉ lệ mới
    for (const L of starLayers) {
      L.hw = tanHalf() * L.depth * a * 1.15;
      for (let i = 0; i < L.count; i++) {
        if (Math.abs(L.pos[i * 3]) > L.hw) L.pos[i * 3] = (Math.random() * 2 - 1) * L.hw;
      }
    }
    for (const D of dustLayers) {
      D.hw = tanHalf() * D.depth * a * 1.1;
      for (let i = 0; i < D.count; i++) {
        if (Math.abs(D.pos[i * 3]) > D.hw) D.pos[i * 3] = (Math.random() * 2 - 1) * D.hw;
      }
    }
  }

  // -------------------------------------------------------------- setTheme
  function setTheme(theme = {}) {
    const pair = Array.isArray(theme.nebula) ? theme.nebula : [0x3f6fd0, 0x1f6fa8];
    const toColor = (v) => new THREE.Color(v);
    // ảnh thật giữ nguyên; chỉ pha 8 % màu chương để ba chương không giống hệt nhau
    if (sky.material?.color) sky.material.color.set(0x9e9e9e).lerp(toColor(pair[0]), 0.08);
    for (const c of nebula) {
      // giữ ảnh thật: chỉ pha 10 % màu chương + hạ sáng
      c.mesh.material.color.setScalar(NEB_K).lerp(toColor(pair[1]), 0.10);
      c.mesh.material.opacity = c.def.op * (theme.fog ?? 0.85);
    }
    starLayers[0].pts.material.color.set(theme.starColor || 0xffffff);
  }

  resize(vw(), vh());

  return { group, update, resize, setTheme, sky, nebula, starLayers, dustLayers, debris, nearField };
}
