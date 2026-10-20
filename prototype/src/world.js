import * as THREE from 'three';

/**
 * Ánh sáng cho cảnh chơi.
 *
 * Trước đây file này dựng cả "bầu trời" (sao, hành tinh, tinh vân). Từ bản
 * 3 lớp, phần nền do `backdrop.js` lo (Trái Đất 3D + bụi cuộn xuống), nên ở
 * đây chỉ còn đèn — giữ nguyên API `update / layout / setTheme` để main.js
 * không phải sửa nhiều.
 */
export function createWorld(scene) {
  const hemi = new THREE.HemisphereLight(0x9fd0ff, 0x241a3a, 1.15);
  scene.add(hemi);

  const key = new THREE.DirectionalLight(0xfff2e0, 2.3);
  key.position.set(7, 16, 9);
  scene.add(key);

  const rim = new THREE.DirectionalLight(0x38e8ff, 1.9);
  rim.position.set(-12, 7, -16);
  scene.add(rim);

  const fill = new THREE.DirectionalLight(0xff9f6a, 0.7);
  fill.position.set(4, 5, -18);
  scene.add(fill);

  scene.add(new THREE.AmbientLight(0x223355, 0.55));

  const noop = () => {};

  return {
    update: noop,
    layout: noop,
    setTheme: noop,
    stars: null,
    planets: [],
    nebulas: [],
    lights: { hemi, key, rim, fill },
  };
}
