import * as THREE from 'three';

/**
 * Bàn phím (WASD / mũi tên) + kéo chuột/chạm trực tiếp trên mặt phẳng y = 0.
 * Kiểu điều khiển "chạm & kéo bất kỳ đâu" giống WindWings: tàu đi theo đúng độ dời ngón tay.
 */
export class Input {
  constructor(canvas, camera) {
    this.canvas = canvas;
    this.camera = camera;
    this.keys = new Set();
    this.enabled = false;
    this.dragging = false;
    this.drag = new THREE.Vector3();
    this.raycaster = new THREE.Raycaster();
    this.plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    this.lastPoint = new THREE.Vector3();
    this.ndc = new THREE.Vector2();
    /** 'joystick' = kéo tương đối (cần cần điều khiển), 'drag' = dời 1:1 theo ngón tay. */
    this.scheme = 'joystick';
    this.origin = new THREE.Vector3();
    this.stick = new THREE.Vector3();
    this.stickRadius = 4.2;
    this.onFirstDrag = null;
    this.hasDragged = false;

    window.addEventListener('keydown', (e) => {
      const k = e.key.toLowerCase();
      if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(k)) e.preventDefault();
      this.keys.add(k);
    });
    window.addEventListener('keyup', (e) => this.keys.delete(e.key.toLowerCase()));
    window.addEventListener('blur', () => this.keys.clear());

    canvas.addEventListener('pointerdown', (e) => this._down(e));
    canvas.addEventListener('pointermove', (e) => this._move(e));
    canvas.addEventListener('pointerup', (e) => this._up(e));
    canvas.addEventListener('pointercancel', (e) => this._up(e));
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  _point(e) {
    const r = this.canvas.getBoundingClientRect();
    this.ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    this.raycaster.setFromCamera(this.ndc, this.camera);
    const hit = new THREE.Vector3();
    return this.raycaster.ray.intersectPlane(this.plane, hit) ? hit : null;
  }

  _down(e) {
    if (!this.enabled) return;
    e.preventDefault();
    const p = this._point(e);
    if (!p) return;
    this.dragging = true;
    this.lastPoint.copy(p);
    this.origin.copy(p);
    this.stick.set(0, 0, 0);
    try { this.canvas.setPointerCapture(e.pointerId); } catch (_) { /* ignore */ }
  }

  _move(e) {
    if (!this.dragging || !this.enabled) return;
    const p = this._point(e);
    if (!p) return;
    const dx = p.x - this.lastPoint.x;
    const dz = p.z - this.lastPoint.z;
    if (this.scheme === 'joystick') {
      this.stick.set(p.x - this.origin.x, 0, p.z - this.origin.z);
      if (this.stick.length() > this.stickRadius) this.stick.setLength(this.stickRadius);
    } else {
      this.drag.x += dx;
      this.drag.z += dz;
    }
    this.lastPoint.copy(p);
    if ((Math.abs(dx) > 0.0005 || Math.abs(dz) > 0.0005) && !this.hasDragged) {
      this.hasDragged = true;
      if (this.onFirstDrag) this.onFirstDrag();
    }
  }

  _up() {
    this.dragging = false;
    this.stick.set(0, 0, 0);
  }

  /** Vector chỉ hướng từ bàn phím, mỗi trục trong [-1, 1]. */
  keyAxis() {
    const k = this.keys;
    const x = (k.has('d') || k.has('arrowright') ? 1 : 0) - (k.has('a') || k.has('arrowleft') ? 1 : 0);
    const z = (k.has('s') || k.has('arrowdown') ? 1 : 0) - (k.has('w') || k.has('arrowup') ? 1 : 0);
    return { x, z };
  }

  /** Lấy & xoá độ dời kéo trong frame. */
  setScheme(scheme) {
    this.scheme = scheme === 'drag' ? 'drag' : 'joystick';
    this.drag.set(0, 0, 0);
    this.stick.set(0, 0, 0);
  }

  /** Độ lớn cần điều khiển 0..1 (chỉ dùng ở scheme 'joystick'). */
  stickAmount() {
    return Math.min(1, this.stick.length() / this.stickRadius);
  }

  consumeDrag(out = new THREE.Vector3()) {
    out.copy(this.drag);
    this.drag.set(0, 0, 0);
    return out;
  }
}
