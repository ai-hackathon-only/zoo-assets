/**
 * Procedural Web Audio synthesizer for Night Shift (zero external audio files).
 * Generates footsteps, gate creak, soft animal calls, task cues, and dawn chime.
 */

export class NightAudio {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this._noiseBuffer = null;
  }

  unlock() {
    if (this.muted) return null;
    try {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return null;
        this.ctx = new AudioCtx();
      }
      if (this.ctx.state === 'suspended') {
        this.ctx.resume().catch(() => {});
      }
      return this.ctx;
    } catch {
      return null;
    }
  }

  setMuted(muted) {
    this.muted = Boolean(muted);
    if (this.ctx) {
      if (this.muted && this.ctx.state === 'running') {
        this.ctx.suspend().catch(() => {});
      } else if (!this.muted && this.ctx.state === 'suspended') {
        this.ctx.resume().catch(() => {});
      }
    }
    return this.muted;
  }

  _ready() {
    if (this.muted) return null;
    const ctx = this.unlock();
    if (!ctx || ctx.state !== 'running') return null;
    return ctx;
  }

  _getNoiseBuffer(ctx) {
    if (this._noiseBuffer && this._noiseBuffer.sampleRate === ctx.sampleRate) {
      return this._noiseBuffer;
    }
    const len = Math.floor(ctx.sampleRate * 0.25);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < len; i++) {
      data[i] = Math.random() * 2 - 1;
    }
    this._noiseBuffer = buf;
    return buf;
  }

  playFootstep(carrying = false) {
    const ctx = this._ready();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Soft gravel/path brush
    const src = ctx.createBufferSource();
    src.buffer = this._getNoiseBuffer(ctx);
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(carrying ? 480 : 620, now);
    filter.Q.setValueAtTime(1.4, now);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.exponentialRampToValueAtTime(carrying ? 0.055 : 0.04, now + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0008, now + 0.085);

    src.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    src.start(now);
    src.stop(now + 0.09);
  }

  playGateCreak() {
    const ctx = this._ready();
    if (!ctx) return;
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(190, now);
    osc.frequency.exponentialRampToValueAtTime(265, now + 0.18);
    osc.frequency.exponentialRampToValueAtTime(145, now + 0.42);

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(520, now);
    filter.Q.setValueAtTime(4.5, now);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.06, now + 0.06);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.44);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.45);
  }

  playAnimalCall(label = '') {
    const ctx = this._ready();
    if (!ctx) return;
    const now = ctx.currentTime;
    const lower = label.toLowerCase();

    if (lower.includes('penguin') || lower.includes('bird') || lower.includes('seal')) {
      // Two-note gentle chirp
      [0, 0.14].forEach((offset, idx) => {
        const osc = ctx.createOscillator();
        osc.type = 'sine';
        const f0 = idx === 0 ? 640 : 780;
        osc.frequency.setValueAtTime(f0, now + offset);
        osc.frequency.exponentialRampToValueAtTime(f0 * 1.18, now + offset + 0.09);

        const gain = ctx.createGain();
        gain.gain.setValueAtTime(0.001, now + offset);
        gain.gain.linearRampToValueAtTime(0.07, now + offset + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, now + offset + 0.11);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + offset);
        osc.stop(now + offset + 0.12);
      });
      return;
    }

    // Warm low purr / call for big mammals
    const osc = ctx.createOscillator();
    osc.type = 'triangle';
    const base = lower.includes('elephant') ? 130 : 175;
    osc.frequency.setValueAtTime(base, now);
    osc.frequency.exponentialRampToValueAtTime(base * 0.78, now + 0.36);

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(420, now);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.09, now + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.38);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.4);
  }

  playTaskCue(type, label = '') {
    if (type === 'gate') {
      this.playGateCreak();
      return;
    }
    if (type === 'feed') {
      this.playAnimalCall(label);
      return;
    }
    const ctx = this._ready();
    if (!ctx) return;
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    osc.type = 'sine';
    const freq = type === 'lamp' ? 523.25 : type === 'visitor' ? 440 : 329.63;
    osc.frequency.setValueAtTime(freq, now);
    osc.frequency.exponentialRampToValueAtTime(freq * 1.25, now + 0.16);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.06, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.23);
  }

  playDawnChime() {
    const ctx = this._ready();
    if (!ctx) return;
    const now = ctx.currentTime;
    // Gentle C-major pentatonic rising chime (C5, E5, G5, C6)
    const notes = [523.25, 659.25, 783.99, 1046.5];
    notes.forEach((freq, i) => {
      const t = now + i * 0.14;
      const osc = ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, t);

      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0.001, t);
      gain.gain.linearRampToValueAtTime(0.07, t + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0008, t + 0.75);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.78);
    });
  }
}
