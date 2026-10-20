/**
 * SFX tổng hợp bằng WebAudio — không cần file âm thanh.
 * Toàn bộ âm thanh được tạo từ oscillator + noise buffer.
 */
export class Sfx {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noise = null;
    try {
      this.muted = localStorage.getItem('ww3d_muted') === '1';
      this.volume = Number(localStorage.getItem('ww3d_vol') ?? '0.55');
      this.musicOn = localStorage.getItem('ww3d_music') !== '0';
      this.musicVolume = Number(localStorage.getItem('ww3d_music_vol') ?? '0.35');
    } catch {
      this.muted = false;
      this.volume = 0.55;
      this.musicOn = true;
      this.musicVolume = 0.35;
    }
    this.musicGain = null;
    this.musicNodes = null;
  }

  init() {
    if (this.ctx) return;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.master.gain.value = this.muted ? 0 : this.volume;
    this.master.connect(this.ctx.destination);
    this.noise = this._noiseBuffer(1.2);
    this._buildMusic();
  }

  /** Nhạc nền synth-wave nhẹ: 2 oscillator + lọc quét chậm, không cần file. */
  _buildMusic() {
    if (!this.ctx || this.musicNodes) return;
    const ctx = this.ctx;
    const gain = ctx.createGain();
    gain.gain.value = 0;
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 620;
    filter.Q.value = 3.5;
    const oscA = ctx.createOscillator();
    oscA.type = 'sawtooth';
    oscA.frequency.value = 55;
    const oscB = ctx.createOscillator();
    oscB.type = 'sine';
    oscB.frequency.value = 82.5;
    const oscC = ctx.createOscillator();
    oscC.type = 'sine';
    oscC.frequency.value = 110;
    const lfo = ctx.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.value = 0.06;
    const lfoGain = ctx.createGain();
    lfoGain.gain.value = 260;
    lfo.connect(lfoGain).connect(filter.frequency);
    const gB = ctx.createGain();
    gB.gain.value = 0.5;
    oscA.connect(filter);
    oscB.connect(gB).connect(filter);
    oscC.connect(filter);
    filter.connect(gain).connect(this.master);
    oscA.start();
    oscB.start();
    oscC.start();
    lfo.start();
    this.musicGain = gain;
    this.musicNodes = { oscA, oscB, oscC, lfo };
    this._applyMusicGain();
  }

  _applyMusicGain() {
    if (!this.musicGain || !this.ctx) return;
    const target = this.musicOn ? this.musicVolume * 0.22 : 0;
    this.musicGain.gain.setTargetAtTime(target, this.ctx.currentTime, 0.4);
  }

  setVolume(v) {
    this.volume = Math.max(0, Math.min(1, Number(v) || 0));
    try { localStorage.setItem('ww3d_vol', String(this.volume)); } catch { /* bỏ qua */ }
    if (this.master) this.master.gain.value = this.muted ? 0 : this.volume;
  }

  setMusic(on) {
    this.musicOn = !!on;
    try { localStorage.setItem('ww3d_music', this.musicOn ? '1' : '0'); } catch { /* bỏ qua */ }
    this._applyMusicGain();
  }

  setMusicVolume(v) {
    this.musicVolume = Math.max(0, Math.min(1, Number(v) || 0));
    try { localStorage.setItem('ww3d_music_vol', String(this.musicVolume)); } catch { /* bỏ qua */ }
    this._applyMusicGain();
  }

  resume() {
    this.init();
    if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
    this._applyMusicGain();
  }

  setMuted(muted) {
    this.muted = muted;
    try { localStorage.setItem('ww3d_muted', muted ? '1' : '0'); } catch { /* bỏ qua */ }
    if (this.master) this.master.gain.value = muted ? 0 : this.volume;
  }

  _noiseBuffer(seconds) {
    const rate = this.ctx.sampleRate;
    const len = Math.floor(rate * seconds);
    const buf = this.ctx.createBuffer(1, len, rate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
    return buf;
  }

  _tone({ type = 'square', f0 = 600, f1 = 200, dur = 0.1, vol = 0.15, delay = 0 }) {
    if (!this.ctx || this.muted) return;
    const t0 = this.ctx.currentTime + delay;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(f0, t0);
    osc.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t0 + dur);
    gain.gain.setValueAtTime(vol, t0);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    osc.connect(gain).connect(this.master);
    osc.start(t0);
    osc.stop(t0 + dur + 0.02);
  }

  _noiseBurst({ dur = 0.3, vol = 0.3, freq = 900, q = 0.8, delay = 0, type = 'lowpass' }) {
    if (!this.ctx || this.muted || !this.noise) return;
    const t0 = this.ctx.currentTime + delay;
    const src = this.ctx.createBufferSource();
    src.buffer = this.noise;
    const filter = this.ctx.createBiquadFilter();
    filter.type = type;
    filter.frequency.setValueAtTime(freq, t0);
    filter.frequency.exponentialRampToValueAtTime(Math.max(80, freq * 0.25), t0 + dur);
    filter.Q.value = q;
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(vol, t0);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    src.connect(filter).connect(gain).connect(this.master);
    src.start(t0);
    src.stop(t0 + dur + 0.02);
  }

  shoot() {
    this._tone({ type: 'sawtooth', f0: 1250, f1: 380, dur: 0.07, vol: 0.06 });
    this._tone({ type: 'square', f0: 2100, f1: 900, dur: 0.045, vol: 0.025 });
  }

  enemyShoot() {
    this._tone({ type: 'square', f0: 520, f1: 180, dur: 0.11, vol: 0.05 });
  }

  hit() {
    this._noiseBurst({ dur: 0.06, vol: 0.08, freq: 2400, type: 'bandpass', q: 2 });
  }

  explode(big = false) {
    this._noiseBurst({ dur: big ? 0.75 : 0.38, vol: big ? 0.42 : 0.26, freq: big ? 700 : 1100 });
    this._tone({ type: 'sine', f0: big ? 130 : 220, f1: 40, dur: big ? 0.6 : 0.32, vol: big ? 0.35 : 0.18 });
  }

  damage() {
    this._tone({ type: 'sawtooth', f0: 260, f1: 70, dur: 0.3, vol: 0.22 });
    this._noiseBurst({ dur: 0.25, vol: 0.2, freq: 500 });
  }

  pickup() {
    this._tone({ type: 'triangle', f0: 620, f1: 900, dur: 0.09, vol: 0.12 });
    this._tone({ type: 'triangle', f0: 900, f1: 1320, dur: 0.12, vol: 0.1, delay: 0.07 });
  }

  wave() {
    this._tone({ type: 'sine', f0: 320, f1: 480, dur: 0.22, vol: 0.1 });
  }

  boss() {
    this._tone({ type: 'sawtooth', f0: 90, f1: 55, dur: 0.9, vol: 0.28 });
    this._noiseBurst({ dur: 1.1, vol: 0.16, freq: 260 });
  }

  gameOver() {
    this._tone({ type: 'sawtooth', f0: 320, f1: 60, dur: 1.2, vol: 0.22 });
  }
}
